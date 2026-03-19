from django.contrib import admin
from .models import (
    Candidate, ClientIntake, RoleSuggestion,
    CredentialVersion, Referral, InterviewLog, PlacementClosure,
)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display  = ('user', 'status', 'placement_ready', 'created_at')
    list_filter   = ('status', 'placement_ready')
    search_fields = ('user__email',)
    ordering      = ('-created_at',)
    raw_id_fields = ('user',)


@admin.register(ClientIntake)
class ClientIntakeAdmin(admin.ModelAdmin):
    list_display  = ('candidate', 'is_locked', 'submitted_at', 'created_at')
    list_filter   = ('is_locked',)
    search_fields = ('candidate__user__email',)
    raw_id_fields = ('candidate', 'reopened_by')


@admin.register(RoleSuggestion)
class RoleSuggestionAdmin(admin.ModelAdmin):
    list_display  = ('role_title', 'candidate', 'is_published', 'candidate_response', 'created_at')
    list_filter   = ('is_published', 'candidate_response')
    search_fields = ('role_title', 'candidate__user__email')
    raw_id_fields = ('candidate', 'suggested_by')


@admin.register(CredentialVersion)
class CredentialVersionAdmin(admin.ModelAdmin):
    list_display  = ('candidate', 'version_number', 'source_role', 'updated_by', 'created_at')
    list_filter   = ('source_role',)
    search_fields = ('candidate__user__email',)
    raw_id_fields = ('candidate', 'updated_by')


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display  = ('friend_name', 'friend_email', 'referrer', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('friend_email', 'referrer__user__email')


@admin.register(InterviewLog)
class InterviewLogAdmin(admin.ModelAdmin):
    list_display  = ('company_name', 'candidate', 'interview_type', 'interview_date', 'outcome')
    list_filter   = ('interview_type', 'outcome')
    search_fields = ('company_name', 'candidate__user__email')


@admin.register(PlacementClosure)
class PlacementClosureAdmin(admin.ModelAdmin):
    list_display  = ('candidate', 'employer_name', 'role_placed_into', 'start_date', 'salary')
    search_fields = ('employer_name', 'candidate__user__email')
    raw_id_fields = ('candidate', 'closed_by')
