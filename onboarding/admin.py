from django.contrib import admin
from .models import Onboarding

@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    list_display = ('profile', 'current_step', 'completed', 'started_at', 'completed_at')
    list_filter = ('completed', 'current_step')
    search_fields = ('profile__first_name', 'profile__last_name', 'profile__email')
    actions = ['mark_complete', 'export_selected']

    def mark_complete(self, request, queryset):
        updated = 0
        for o in queryset:
            o.steps_completed = ['profile','documents','agreements','questions','review']
            o.completed = True
            from django.utils import timezone
            o.completed_at = timezone.now()
            o.save()
            updated += 1
        self.message_user(request, f"Marked {updated} onboardings as complete")
    mark_complete.short_description = 'Mark selected onboardings complete'

    def export_selected(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=onboarding.csv'
        writer = csv.writer(response)
        writer.writerow(['id', 'profile', 'current_step', 'completed', 'steps_completed'])
        for o in queryset:
            profile_name = f"{o.profile.first_name} {o.profile.last_name}" if o.profile else ''
            writer.writerow([o.id, profile_name, o.current_step, o.completed, '|'.join(o.steps_completed)])
        return response
    export_selected.short_description = 'Export selected onboardings to CSV'
