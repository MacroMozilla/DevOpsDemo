from django.db import models
from django.utils import timezone


class APICallLog(models.Model):
    """
    Model to track API calls made through the DevOpsDemo API.
    Useful for monitoring, analytics, and demonstrating database operations in CI/CD.
    """

    ENDPOINT_CHOICES = [
        ('docker_repos', 'Docker Repositories'),
        ('docker_tags', 'Docker Tags'),
        ('ai_chat', 'AI Chat'),
        ('health', 'Health Check'),
    ]

    endpoint = models.CharField(
        max_length=50,
        choices=ENDPOINT_CHOICES,
        help_text="API endpoint that was called"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the API call was made"
    )
    response_time_ms = models.FloatField(
        null=True,
        blank=True,
        help_text="Response time in milliseconds"
    )
    status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="HTTP status code returned"
    )
    error_message = models.TextField(
        blank=True,
        default='',
        help_text="Error message if the call failed"
    )
    request_params = models.JSONField(
        null=True,
        blank=True,
        help_text="Request parameters (for analysis)"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'API Call Log'
        verbose_name_plural = 'API Call Logs'
        indexes = [
            models.Index(fields=['-timestamp', 'endpoint']),
        ]

    def __str__(self):
        return f"{self.endpoint} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def was_successful(self):
        """Check if the API call was successful (2xx status code)"""
        return self.status_code and 200 <= self.status_code < 300
