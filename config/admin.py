from django.contrib import admin
from .models import AdminConfig


@admin.register(AdminConfig)
class AdminConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'review_timeline_text', 'grace_period_days', 'updated_at')
    fieldsets = (
        ('Cal.com Scheduling Links', {'fields': (
            'cal_training_url', 'cal_mock_practice_url',
            'cal_interview_training_url', 'cal_interview_support_url',
            'cal_operations_call_url',
        )}),
        ('UI Text', {'fields': (
            'review_timeline_text', 'roles_locked_message',
            'credentials_locked_message', 'help_desk_url',
        )}),
        ('Billing', {'fields': ('grace_period_days',)}),
    )

    def has_add_permission(self, request):
        return not AdminConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
