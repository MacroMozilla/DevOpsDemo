import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import APICallLog


@pytest.fixture
def api_client():
    """Fixture for API client"""
    return APIClient()


@pytest.fixture
def api_call_log():
    """Fixture for creating API call log"""
    return APICallLog.objects.create(
        endpoint='health',
        response_time_ms=100.5,
        status_code=200
    )


@pytest.mark.django_db
class TestHealthCheckEndpoint:
    """Tests for health check endpoint"""

    def test_health_check_success(self, api_client):
        """Test health check returns successful response"""
        url = reverse('api:health')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert 'timestamp' in response.data
        assert 'version' in response.data
        assert 'database' in response.data

    def test_health_check_creates_log_entry(self, api_client):
        """Test health check creates a log entry"""
        initial_count = APICallLog.objects.count()
        url = reverse('api:health')
        api_client.get(url)

        assert APICallLog.objects.count() == initial_count + 1
        log = APICallLog.objects.latest('timestamp')
        assert log.endpoint == 'health'
        assert log.status_code == 200


@pytest.mark.django_db
class TestAPICallLogModel:
    """Tests for APICallLog model"""

    def test_create_log_entry(self):
        """Test creating a log entry"""
        log = APICallLog.objects.create(
            endpoint='docker_repos',
            response_time_ms=250.75,
            status_code=200
        )

        assert log.endpoint == 'docker_repos'
        assert log.response_time_ms == 250.75
        assert log.status_code == 200
        assert log.was_successful is True

    def test_was_successful_property_true(self):
        """Test was_successful property for successful calls"""
        log = APICallLog.objects.create(endpoint='health', status_code=200)
        assert log.was_successful is True

    def test_was_successful_property_false(self):
        """Test was_successful property for failed calls"""
        log = APICallLog.objects.create(endpoint='health', status_code=500)
        assert log.was_successful is False

    def test_str_representation(self, api_call_log):
        """Test string representation of log entry"""
        str_repr = str(api_call_log)
        assert 'health' in str_repr


@pytest.mark.django_db
class TestAPICallLogViewSet:
    """Tests for APICallLog ViewSet"""

    def test_list_logs(self, api_client, api_call_log):
        """Test listing API call logs"""
        url = reverse('api:api-log-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_stats_endpoint(self, api_client):
        """Test stats endpoint"""
        # Create some test data
        APICallLog.objects.create(endpoint='health', status_code=200, response_time_ms=100)
        APICallLog.objects.create(endpoint='health', status_code=500, response_time_ms=150)

        url = reverse('api:api-log-stats')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'total_calls' in response.data
        assert 'successful_calls' in response.data
        assert 'success_rate' in response.data
        assert 'average_response_time_ms' in response.data


@pytest.mark.django_db
class TestDockerEndpoints:
    """Tests for Docker Hub endpoints"""

    @patch('api.views.DockerHubManager')
    @patch('api.views.settings')
    def test_docker_repos_success(self, mock_settings, mock_manager_class, api_client):
        """Test successful Docker repos retrieval"""
        # Mock settings
        mock_settings.DOCKERHUB_USERNAME = 'testuser'
        mock_settings.DOCKERHUB_TOKEN = 'testtoken'

        # Mock manager
        mock_manager = MagicMock()
        mock_manager.get_repos.return_value = [
            {
                'name': 'test-repo',
                'description': 'Test repository',
                'is_private': False,
                'star_count': 10,
                'pull_count': 100,
                'last_updated': '2025-01-01T00:00:00Z'
            }
        ]
        mock_manager_class.return_value = mock_manager

        url = reverse('api:docker-repos')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'test-repo'

    @patch('api.views.settings')
    def test_docker_repos_no_credentials(self, mock_settings, api_client):
        """Test Docker repos endpoint without credentials"""
        mock_settings.DOCKERHUB_USERNAME = ''
        mock_settings.DOCKERHUB_TOKEN = ''

        url = reverse('api:docker-repos')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

    @patch('api.views.DockerHubManager')
    @patch('api.views.settings')
    def test_docker_tags_success(self, mock_settings, mock_manager_class, api_client):
        """Test successful Docker tags retrieval"""
        mock_settings.DOCKERHUB_USERNAME = 'testuser'
        mock_settings.DOCKERHUB_TOKEN = 'testtoken'

        mock_manager = MagicMock()
        mock_manager.get_tags_by_repo.return_value = [
            {
                'name': 'latest',
                'full_size': 1024000,
                'last_updated': '2025-01-01T00:00:00Z',
                'last_updater_username': 'testuser'
            }
        ]
        mock_manager_class.return_value = mock_manager

        url = reverse('api:docker-tags', kwargs={'repo_name': 'test-repo'})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'latest'


@pytest.mark.django_db
class TestAIEndpoints:
    """Tests for AI chat endpoints"""

    @patch('api.views.call_deepseek')
    @patch('api.views.settings')
    def test_ai_chat_success(self, mock_settings, mock_call_deepseek, api_client):
        """Test successful AI chat"""
        mock_settings.DEEPSEEK_API_KEY = 'test-api-key'
        mock_call_deepseek.return_value = "Hello! I'm DeepSeek AI."

        url = reverse('api:ai-chat')
        data = {
            'message': 'Hello',
            'model': 'deepseek-chat',
            'stream': False
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'response' in response.data
        assert response.data['response'] == "Hello! I'm DeepSeek AI."
        assert 'response_time_ms' in response.data

    @patch('api.views.settings')
    def test_ai_chat_no_api_key(self, mock_settings, api_client):
        """Test AI chat without API key"""
        mock_settings.DEEPSEEK_API_KEY = ''

        url = reverse('api:ai-chat')
        data = {'message': 'Hello'}
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

    @patch('api.views.settings')
    def test_ai_chat_invalid_data(self, mock_settings, api_client):
        """Test AI chat with invalid data"""
        mock_settings.DEEPSEEK_API_KEY = 'test-api-key'

        url = reverse('api:ai-chat')
        data = {}  # Missing required 'message' field
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
