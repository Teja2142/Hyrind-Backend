from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('profile', 'plan', 'status', 'started_at', 'ended_at')
    list_filter = ('status', 'plan')
    search_fields = ('profile__first_name', 'profile__last_name', 'profile__email')
    actions = ['mark_inactive', 'export_selected']

    def mark_inactive(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f"Marked {updated} subscriptions as inactive")
    mark_inactive.short_description = 'Mark selected subscriptions inactive'

    def export_selected(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=subscriptions.csv'
        writer = csv.writer(response)
        writer.writerow(['id', 'profile', 'plan', 'status', 'started_at', 'ended_at'])
        for s in queryset:
            profile_name = f"{s.profile.first_name} {s.profile.last_name}".strip() if s.profile else ''
            writer.writerow([s.id, profile_name, s.plan, s.status, s.started_at, s.ended_at])
        return response
    export_selected.short_description = 'Export selected subscriptions to CSV'
