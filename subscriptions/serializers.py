from rest_framework import serializers
from .models import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'profile', 'stripe_subscription_id', 'plan', 'status', 'started_at', 'ended_at']