from rest_framework import serializers
from .models import APICallLog


class APICallLogSerializer(serializers.ModelSerializer):
    """Serializer for API call logs"""

    was_successful = serializers.ReadOnlyField()

    class Meta:
        model = APICallLog
        fields = [
            'id',
            'endpoint',
            'timestamp',
            'response_time_ms',
            'status_code',
            'was_successful',
            'error_message',
            'request_params',
        ]
        read_only_fields = ['timestamp']


class DockerRepoSerializer(serializers.Serializer):
    """Serializer for Docker Hub repository information"""

    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    is_private = serializers.BooleanField()
    star_count = serializers.IntegerField(required=False, default=0)
    pull_count = serializers.IntegerField(required=False, default=0)
    last_updated = serializers.DateTimeField(required=False, allow_null=True)


class DockerTagSerializer(serializers.Serializer):
    """Serializer for Docker image tags"""

    name = serializers.CharField()
    full_size = serializers.IntegerField(required=False, allow_null=True)
    last_updated = serializers.DateTimeField(required=False, allow_null=True)
    last_updater_username = serializers.CharField(required=False, allow_null=True)


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for chat messages"""

    role = serializers.ChoiceField(choices=['user', 'assistant', 'system'])
    content = serializers.CharField()


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for AI chat requests"""

    message = serializers.CharField(max_length=2000, help_text="Your message to the AI")
    model = serializers.CharField(
        default='deepseek-chat',
        required=False,
        help_text="AI model to use"
    )
    stream = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Enable streaming responses"
    )


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for AI chat responses"""

    response = serializers.CharField()
    model = serializers.CharField()
    response_time_ms = serializers.FloatField()


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response"""

    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()
    database = serializers.CharField()
    deepseek_configured = serializers.BooleanField()
    dockerhub_configured = serializers.BooleanField()
