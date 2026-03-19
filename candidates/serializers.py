from rest_framework import serializers
from .models import (
    Candidate, ClientIntake, RoleSuggestion, CredentialVersion,
    Referral, InterviewLog, PlacementClosure,
)


class CandidateListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email     = serializers.SerializerMethodField()

    class Meta:
        model  = Candidate
        fields = ['id', 'status', 'full_name', 'email', 'placement_ready', 'created_at']

    def get_full_name(self, obj):
        p = getattr(obj.user, 'profile', None)
        return p.full_name if p else ''

    def get_email(self, obj):
        return obj.user.email


class CandidateSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email     = serializers.SerializerMethodField()
    role      = serializers.SerializerMethodField()

    class Meta:
        model  = Candidate
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        p = getattr(obj.user, 'profile', None)
        return p.full_name if p else ''

    def get_email(self, obj):
        return obj.user.email

    def get_role(self, obj):
        return obj.user.role


class ClientIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ClientIntake
        fields = '__all__'
        read_only_fields = ['id', 'candidate', 'is_locked', 'submitted_at', 'created_at', 'updated_at']


class RoleSuggestionSerializer(serializers.ModelSerializer):
    suggested_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = RoleSuggestion
        fields = '__all__'
        read_only_fields = ['id', 'suggested_by', 'is_published', 'published_at', 'created_at', 'updated_at']

    def get_suggested_by_name(self, obj):
        if obj.suggested_by and hasattr(obj.suggested_by, 'profile'):
            return obj.suggested_by.profile.full_name
        return ''


class CredentialVersionSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = CredentialVersion
        fields = '__all__'
        read_only_fields = [
            'id', 'candidate', 'version_number', 'updated_by',
            'changed_fields', 'diff_summary', 'full_snapshot', 'created_at',
        ]

    def get_updated_by_name(self, obj):
        if obj.updated_by and hasattr(obj.updated_by, 'profile'):
            return obj.updated_by.profile.full_name
        return ''


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Referral
        fields = '__all__'
        read_only_fields = ['id', 'referrer', 'status', 'admin_notes', 'created_at', 'updated_at']


class InterviewLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = InterviewLog
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']


class PlacementClosureSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PlacementClosure
        fields = '__all__'
        read_only_fields = ['id', 'closed_by', 'created_at']
