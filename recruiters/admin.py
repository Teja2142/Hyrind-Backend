from django.contrib import admin
from .models import RecruiterProfile, RecruiterBankDetail, RecruiterAssignment, DailySubmissionLog, JobLinkEntry


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'first_name', 'last_name', 'phone', 'city', 'country', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name')
    raw_id_fields = ('user',)
    ordering      = ('-created_at',)


@admin.register(RecruiterBankDetail)
class RecruiterBankDetailAdmin(admin.ModelAdmin):
    list_display  = ('recruiter', 'bank_name', 'account_holder_name', 'masked_account', 'updated_at')
    search_fields = ('recruiter__email', 'bank_name', 'account_holder_name')
    raw_id_fields = ('recruiter',)
    readonly_fields = ('masked_account', 'updated_at')


@admin.register(RecruiterAssignment)
class RecruiterAssignmentAdmin(admin.ModelAdmin):
    list_display  = ('recruiter', 'candidate', 'role_type', 'is_active', 'assigned_at')
    list_filter   = ('is_active',)
    search_fields = ('recruiter__email', 'candidate__user__email')
    raw_id_fields = ('recruiter', 'candidate', 'assigned_by')
    ordering      = ('-assigned_at',)


@admin.register(DailySubmissionLog)
class DailySubmissionLogAdmin(admin.ModelAdmin):
    list_display  = ('recruiter', 'candidate', 'log_date', 'applications_count', 'created_at')
    search_fields = ('recruiter__email', 'candidate__user__email')
    raw_id_fields = ('recruiter', 'candidate')
    ordering      = ('-log_date',)


@admin.register(JobLinkEntry)
class JobLinkEntryAdmin(admin.ModelAdmin):
    list_display  = ('company_name', 'role_title', 'candidate', 'application_status', 'submitted_at')
    list_filter   = ('application_status', 'fetch_status')
    search_fields = ('company_name', 'role_title', 'candidate__user__email')
    raw_id_fields = ('submission_log', 'candidate', 'submitted_by')
