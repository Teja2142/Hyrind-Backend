from django.contrib import admin
from .models import AuditLog
from django.utils.html import format_html

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'target', 'metadata')
    list_filter = ('action', 'timestamp')
    search_fields = ('actor__username', 'action', 'target')
    readonly_fields = ('timestamp',)
