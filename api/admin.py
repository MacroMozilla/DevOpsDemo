from django.contrib import admin
from .models import APICallLog


@admin.register(APICallLog)
class APICallLogAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'timestamp', 'response_time_ms', 'status_code', 'was_successful']
    list_filter = ['endpoint', 'status_code', 'timestamp']
    search_fields = ['endpoint', 'error_message']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def was_successful(self, obj):
        return obj.was_successful
    was_successful.boolean = True
    was_successful.short_description = 'Success'
