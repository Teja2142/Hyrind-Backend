from django.contrib import admin
from .models import Recruiter, Assignment

@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'email')
    actions = ['activate_recruiters', 'deactivate_recruiters', 'export_selected']

    def activate_recruiters(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f"Activated {updated} recruiters")
    activate_recruiters.short_description = 'Activate selected recruiters'

    def deactivate_recruiters(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f"Deactivated {updated} recruiters")
    deactivate_recruiters.short_description = 'Deactivate selected recruiters'

    def export_selected(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=recruiters.csv'
        writer = csv.writer(response)
        writer.writerow(['id', 'name', 'email', 'phone', 'active'])
        for r in queryset:
            writer.writerow([r.id, r.name, r.email, r.phone, r.active])
        return response
    export_selected.short_description = 'Export selected recruiters to CSV'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'recruiter', 'assigned_at')
    search_fields = ('profile__first_name', 'profile__last_name', 'profile__email', 'recruiter__name')
