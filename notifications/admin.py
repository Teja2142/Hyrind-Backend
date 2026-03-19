from django.contrib import admin
from .models import Notification, EmailLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'is_read', 'created_at')
    list_filter   = ('is_read',)
    search_fields = ('user__email', 'title', 'message')
    ordering      = ('-created_at',)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display  = ('email_type', 'recipient_email', 'status', 'created_at')
    list_filter   = ('status', 'email_type')
    search_fields = ('recipient_email', 'email_type')
    ordering      = ('-created_at',)
    readonly_fields = ('recipient_email', 'email_type', 'status', 'error_message', 'created_at')
