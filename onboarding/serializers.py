from rest_framework import serializers
from .models import Onboarding

class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Onboarding
        fields = ['id', 'profile', 'current_step', 'steps_completed', 'completed', 'started_at', 'completed_at']