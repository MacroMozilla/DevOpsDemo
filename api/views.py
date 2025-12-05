import logging
from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import APICallLog
from .serializers import (
    APICallLogSerializer,
    DockerRepoSerializer,
    DockerTagSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    HealthCheckSerializer,
)
from utility.watch import Watch
from src.LF_dockerhubmanger.docker_tools import DockerHubManager
from src.fctn_tools.deepseek_tools import call_deepseek

logger = logging.getLogger(__name__)


class APICallLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing API call logs.

    Provides read-only access to API call history for monitoring and analytics.
    """
    queryset = APICallLog.objects.all()
    serializer_class = APICallLogSerializer

    @extend_schema(
        summary="Get API call statistics",
        description="Returns aggregated statistics about API calls"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about API calls"""
        total_calls = APICallLog.objects.count()
        successful_calls = APICallLog.objects.filter(status_code__gte=200, status_code__lt=300).count()
        avg_response_time = APICallLog.objects.filter(
            response_time_ms__isnull=False
        ).aggregate(avg=models.Avg('response_time_ms'))['avg'] or 0

        return Response({
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 0,
            'average_response_time_ms': round(avg_response_time, 2),
        })


@extend_schema(
    summary="Get Docker Hub repositories",
    description="Fetches list of repositories from Docker Hub for the configured user",
    parameters=[
        OpenApiParameter(
            name='page_size',
            description='Number of repositories to return per page',
            required=False,
            type=int,
            default=10
        )
    ],
    responses={
        200: OpenApiResponse(
            response=DockerRepoSerializer(many=True),
            description="List of Docker repositories"
        ),
        500: OpenApiResponse(description="Docker Hub API error")
    },
    tags=['Docker']
)
@api_view(['GET'])
def docker_repos(request):
    """
    Get list of Docker Hub repositories.

    Requires DOCKERHUB_USERNAME and DOCKERHUB_TOKEN to be configured.
    """
    watch = Watch()
    log_entry = APICallLog(endpoint='docker_repos')

    try:
        if not settings.DOCKERHUB_USERNAME or not settings.DOCKERHUB_TOKEN:
            log_entry.status_code = 500
            log_entry.error_message = "Docker Hub credentials not configured"
            log_entry.save()
            return Response(
                {'error': 'Docker Hub credentials not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        page_size = int(request.GET.get('page_size', 10))
        manager = DockerHubManager()
        repos = manager.get_repos(page_size=page_size)

        log_entry.response_time_ms = watch.see_seconds() * 1000
        log_entry.status_code = 200
        log_entry.request_params = {'page_size': page_size}
        log_entry.save()

        serializer = DockerRepoSerializer(repos, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.exception("Error fetching Docker repos")
        log_entry.response_time_ms = watch.see_seconds() * 1000
        log_entry.status_code = 500
        log_entry.error_message = str(e)
        log_entry.save()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Get Docker image tags",
    description="Fetches list of tags for a specific Docker repository",
    parameters=[
        OpenApiParameter(
            name='repo_name',
            description='Name of the repository',
            required=True,
            type=str,
            location=OpenApiParameter.PATH
        )
    ],
    responses={
        200: OpenApiResponse(
            response=DockerTagSerializer(many=True),
            description="List of Docker image tags"
        ),
        500: OpenApiResponse(description="Docker Hub API error")
    },
    tags=['Docker']
)
@api_view(['GET'])
def docker_tags(request, repo_name):
    """
    Get list of tags for a specific Docker repository.

    Args:
        repo_name: Name of the Docker repository
    """
    watch = Watch()
    log_entry = APICallLog(endpoint='docker_tags')

    try:
        if not settings.DOCKERHUB_USERNAME or not settings.DOCKERHUB_TOKEN:
            log_entry.status_code = 500
            log_entry.error_message = "Docker Hub credentials not configured"
            log_entry.save()
            return Response(
                {'error': 'Docker Hub credentials not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        manager = DockerHubManager()
        tags = manager.get_tags_by_repo(repo_name)

        log_entry.response_time_ms = watch.see_seconds() * 1000
        log_entry.status_code = 200
        log_entry.request_params = {'repo_name': repo_name}
        log_entry.save()

        serializer = DockerTagSerializer(tags, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.exception(f"Error fetching tags for repo {repo_name}")
        log_entry.response_time_ms = watch.see_seconds() * 1000
        log_entry.status_code = 500
        log_entry.error_message = str(e)
        log_entry.save()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Chat with DeepSeek AI",
    description="Send a message to DeepSeek AI and get a response",
    request=ChatRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=ChatResponseSerializer,
            description="AI response"
        ),
        500: OpenApiResponse(description="DeepSeek API error")
    },
    tags=['AI']
)
@api_view(['POST'])
def ai_chat(request):
    """
    Chat with DeepSeek AI.

    Requires DEEPSEEK_API_KEY to be configured.
    """
    watch = Watch()
    log_entry = APICallLog(endpoint='ai_chat')

    try:
        if not settings.DEEPSEEK_API_KEY:
            log_entry.status_code = 500
            log_entry.error_message = "DeepSeek API key not configured"
            log_entry.save()
            return Response(
                {'error': 'DeepSeek API key not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        request_serializer = ChatRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            log_entry.status_code = 400
            log_entry.error_message = str(request_serializer.errors)
            log_entry.save()
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = request_serializer.validated_data['message']
        model = request_serializer.validated_data.get('model', 'deepseek-chat')
        stream = request_serializer.validated_data.get('stream', False)

        # Create message format for DeepSeek API
        messages = [{"role": "user", "content": message}]

        # Call DeepSeek API
        response_content = call_deepseek(messages, model=model, stream=stream)

        response_time_ms = watch.see_seconds() * 1000

        log_entry.response_time_ms = response_time_ms
        log_entry.status_code = 200
        log_entry.request_params = {
            'message_length': len(message),
            'model': model,
            'stream': stream
        }
        log_entry.save()

        response_data = {
            'response': response_content,
            'model': model,
            'response_time_ms': round(response_time_ms, 2)
        }

        response_serializer = ChatResponseSerializer(response_data)
        return Response(response_serializer.data)

    except Exception as e:
        logger.exception("Error in AI chat")
        log_entry.response_time_ms = watch.see_seconds() * 1000
        log_entry.status_code = 500
        log_entry.error_message = str(e)
        log_entry.save()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Health check",
    description="Check API health and configuration status",
    responses={
        200: OpenApiResponse(
            response=HealthCheckSerializer,
            description="Health status"
        )
    },
    tags=['System']
)
@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint.

    Returns system status and configuration information.
    """
    watch = Watch()
    log_entry = APICallLog(endpoint='health')

    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    response_data = {
        'status': 'healthy',
        'timestamp': timezone.now(),
        'version': '1.0.0',
        'database': db_status,
        'deepseek_configured': bool(settings.DEEPSEEK_API_KEY),
        'dockerhub_configured': bool(settings.DOCKERHUB_USERNAME and settings.DOCKERHUB_TOKEN),
    }

    log_entry.response_time_ms = watch.see_seconds() * 1000
    log_entry.status_code = 200
    log_entry.save()

    serializer = HealthCheckSerializer(response_data)
    return Response(serializer.data)
