from rest_framework import serializers
from .models import Recruiter, Assignment

class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ['id', 'name', 'email', 'phone', 'active']

class AssignmentSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSerializer(read_only=True)
    recruiter_id = serializers.PrimaryKeyRelatedField(queryset=Recruiter.objects.all(), source='recruiter', write_only=True)
    class Meta:
        model = Assignment
        fields = ['id', 'profile', 'recruiter', 'recruiter_id', 'assigned_at']