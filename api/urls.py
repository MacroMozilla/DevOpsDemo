from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'logs', views.APICallLogViewSet, basename='api-log')

app_name = 'api'

urlpatterns = [
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),

    # Health check
    path('health/', views.health_check, name='health'),

    # Docker endpoints
    path('docker/repos/', views.docker_repos, name='docker-repos'),
    path('docker/tags/<str:repo_name>/', views.docker_tags, name='docker-tags'),

    # AI endpoints
    path('ai/chat/', views.ai_chat, name='ai-chat'),

    # Include router URLs
    path('', include(router.urls)),
]
