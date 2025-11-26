from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'first_name', 'last_name', 'email', 'phone', 'university', 'degree', 'major', 'visa_status', 'graduation_date', 'opt_end_date',
        'resume_file', 'consent_to_terms', 'referral_source', 'linkedin_url', 'github_url', 'additional_notes'
    )
