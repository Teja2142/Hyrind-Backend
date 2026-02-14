"""
Serializers for role recommendation API
"""
from rest_framework import serializers
from .models import (
    JobRole, UserRoleRecommendation, UserSkillProfile, RecommendationFeedback
)


class JobRoleSerializer(serializers.ModelSerializer):
    """Serializer for job roles"""
    
    class Meta:
        model = JobRole
        fields = [
            'id', 'title', 'category', 'description', 'required_skills',
            'preferred_skills', 'min_years_experience', 'max_years_experience',
            'required_degrees', 'alternative_titles', 'avg_salary_min',
            'avg_salary_max', 'is_active', 'popularity_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class JobRoleSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for job role listing"""
    
    class Meta:
        model = JobRole
        fields = [
            'id', 'title', 'category', 'min_years_experience',
            'max_years_experience', 'popularity_score'
        ]


class UserRoleRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for user role recommendations"""
    role = JobRoleSerializer(read_only=True)
    
    class Meta:
        model = UserRoleRecommendation
        fields = [
            'id', 'role', 'match_score', 'skill_match_score',
            'experience_match_score', 'education_match_score', 'matched_skills',
            'missing_skills', 'recommendation_reason', 'is_interested',
            'is_dismissed', 'viewed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'match_score', 'skill_match_score', 'experience_match_score',
            'education_match_score', 'matched_skills', 'missing_skills',
            'recommendation_reason', 'viewed_at', 'created_at'
        ]


class UserRoleRecommendationSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for recommendation listing"""
    role = JobRoleSummarySerializer(read_only=True)
    
    class Meta:
        model = UserRoleRecommendation
        fields = [
            'id', 'role', 'match_score', 'recommendation_reason',
            'is_interested', 'is_dismissed', 'created_at'
        ]


class UserSkillProfileSerializer(serializers.ModelSerializer):
    """Serializer for user skill profiles"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSkillProfile
        fields = [
            'id', 'user', 'user_email', 'user_name', 'primary_skills',
            'secondary_skills', 'learning_skills', 'total_years_experience',
            'industries', 'highest_degree', 'field_of_study', 'desired_roles',
            'preferred_locations', 'job_type_preference', 'profile_completeness',
            'last_updated_from_intake', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'profile_completeness', 'last_updated_from_intake',
            'created_at', 'updated_at'
        ]
    
    def get_user_name(self, obj):
        """Get user's full name"""
        if hasattr(obj.user, 'profile'):
            profile = obj.user.profile
            return f"{profile.first_name} {profile.last_name}".strip() or obj.user.username
        return obj.user.username


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for recommendation feedback"""
    
    class Meta:
        model = RecommendationFeedback
        fields = [
            'id', 'recommendation', 'feedback_type', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecommendationActionSerializer(serializers.Serializer):
    """Serializer for recommendation actions (interest, dismiss)"""
    action = serializers.ChoiceField(choices=['interested', 'dismiss', 'view'])
    
    def validate_action(self, value):
        """Validate action"""
        if value not in ['interested', 'dismiss', 'view']:
            raise serializers.ValidationError("Invalid action. Must be 'interested', 'dismiss', or 'view'")
        return value


class GenerateRecommendationsSerializer(serializers.Serializer):
    """Serializer for generating recommendations"""
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50)
    force_refresh = serializers.BooleanField(default=False)
    category = serializers.CharField(required=False, allow_blank=True)
