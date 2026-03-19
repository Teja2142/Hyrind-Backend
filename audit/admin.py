from django.contrib import admin
from .models import AuditLog
from django.utils.html import format_html

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display    = ('created_at', 'actor', 'action', 'target_type', 'target_id', 'details')
    list_filter     = ('action', 'created_at')
    search_fields   = ('actor__email', 'action', 'target_type', 'target_id')
    readonly_fields = ('created_at',)
    ordering        = ('-created_at',)
