from django.contrib import admin
from .models import Job, JobRole, UserRoleRecommendation, UserSkillProfile, RecommendationFeedback

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'price', 'is_open')


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    """Admin for JobRole model"""
    list_display = [
        'title', 'category', 'min_years_experience', 'max_years_experience',
        'is_active', 'popularity_score', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'min_years_experience']
    search_fields = ['title', 'category', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'category', 'description', 'alternative_titles')
        }),
        ('Requirements', {
            'fields': (
                'required_skills', 'preferred_skills', 'required_degrees',
                'min_years_experience', 'max_years_experience'
            )
        }),
        ('Metadata', {
            'fields': ('avg_salary_min', 'avg_salary_max', 'popularity_score', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserRoleRecommendation)
class UserRoleRecommendationAdmin(admin.ModelAdmin):
    """Admin for UserRoleRecommendation model"""
    list_display = [
        'user', 'role', 'match_score', 'is_interested', 'is_dismissed',
        'viewed_at', 'created_at'
    ]
    list_filter = ['is_interested', 'is_dismissed', 'created_at']
    search_fields = ['user__username', 'role__title']
    readonly_fields = [
        'id', 'match_score', 'skill_match_score', 'experience_match_score',
        'education_match_score', 'matched_skills', 'missing_skills',
        'recommendation_reason', 'viewed_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'role')
        }),
        ('Match Scores', {
            'fields': (
                'match_score', 'skill_match_score', 'experience_match_score',
                'education_match_score'
            )
        }),
        ('Matching Details', {
            'fields': ('matched_skills', 'missing_skills', 'recommendation_reason')
        }),
        ('User Interaction', {
            'fields': ('is_interested', 'is_dismissed', 'viewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserSkillProfile)
class UserSkillProfileAdmin(admin.ModelAdmin):
    """Admin for UserSkillProfile model"""
    list_display = [
        'user', 'highest_degree', 'total_years_experience',
        'profile_completeness', 'last_updated_from_intake', 'created_at'
    ]
    list_filter = ['highest_degree', 'profile_completeness', 'created_at']
    search_fields = ['user__username', 'highest_degree', 'field_of_study']
    readonly_fields = [
        'id', 'profile_completeness', 'last_updated_from_intake',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user')
        }),
        ('Skills', {
            'fields': ('primary_skills', 'secondary_skills', 'learning_skills')
        }),
        ('Experience', {
            'fields': ('total_years_experience', 'industries')
        }),
        ('Education', {
            'fields': ('highest_degree', 'field_of_study')
        }),
        ('Preferences', {
            'fields': ('desired_roles', 'preferred_locations', 'job_type_preference')
        }),
        ('Metadata', {
            'fields': ('profile_completeness', 'last_updated_from_intake')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    """Admin for RecommendationFeedback model"""
    list_display = ['recommendation', 'feedback_type', 'created_at']
    list_filter = ['feedback_type', 'created_at']
    search_fields = ['recommendation__user__username', 'recommendation__role__title', 'comment']
    readonly_fields = ['id', 'created_at']
