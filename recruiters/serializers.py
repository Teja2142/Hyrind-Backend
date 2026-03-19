from rest_framework import serializers
from .models import RecruiterProfile, RecruiterBankDetail, RecruiterAssignment, DailySubmissionLog, JobLinkEntry


class RecruiterProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    role  = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model  = RecruiterProfile
        fields = [
            'id', 'email', 'role', 'first_name', 'last_name',
            'phone', 'city', 'state', 'country',
            'linkedin_url', 'documents_url', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at', 'updated_at']


class RecruiterBankDetailSerializer(serializers.ModelSerializer):
    masked_account = serializers.CharField(read_only=True)

    class Meta:
        model  = RecruiterBankDetail
        fields = ['id', 'bank_name', 'account_holder_name', 'account_number',
                  'routing_number', 'account_type', 'masked_account', 'updated_at']
        read_only_fields = ['id', 'masked_account', 'updated_at']
        extra_kwargs = {'account_number': {'write_only': True}}


class RecruiterAssignmentSerializer(serializers.ModelSerializer):
    recruiter_email   = serializers.EmailField(source='recruiter.email', read_only=True)
    candidate_email   = serializers.SerializerMethodField()

    class Meta:
        model  = RecruiterAssignment
        fields = '__all__'
        read_only_fields = ['id', 'assigned_at']

    def get_candidate_email(self, obj):
        return obj.candidate.user.email


class AssignRecruiterSerializer(serializers.Serializer):
    candidate_id  = serializers.UUIDField()
    recruiter_id  = serializers.UUIDField()
    role_type     = serializers.CharField(max_length=50, required=False, allow_blank=True)


class JobLinkEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model  = JobLinkEntry
        fields = '__all__'
        read_only_fields = ['id', 'submission_log', 'candidate', 'submitted_by',
                            'submitted_at', 'fetch_status', 'updated_at']


class DailySubmissionLogSerializer(serializers.ModelSerializer):
    job_entries = JobLinkEntrySerializer(many=True, read_only=True)

    class Meta:
        model  = DailySubmissionLog
        fields = '__all__'
        read_only_fields = ['id', 'recruiter', 'created_at', 'updated_at']
