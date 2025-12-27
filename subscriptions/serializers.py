from rest_framework import serializers
from django.db import models
from .models import Subscription, SubscriptionPlan, UserSubscription, BillingHistory


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans (Base + Add-ons)"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'description', 'base_price', 
            'is_mandatory', 'is_active', 'billing_cycle', 'features',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    profile_name = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'profile', 'profile_name', 'plan', 'plan_details',
            'price', 'status', 'razorpay_subscription_id', 'billing_cycle',
            'next_billing_date', 'started_at', 'ended_at', 
            'admin_notes', 'total_paid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'started_at', 'ended_at']
    
    def get_profile_name(self, obj):
        """Get user's full name"""
        return f"{obj.profile.first_name} {obj.profile.last_name}".strip() or obj.profile.email
    
    def get_total_paid(self, obj):
        """Get total amount paid for this subscription"""
        total = obj.billing_history.filter(status='success').aggregate(
            total=models.Sum('amount')
        )['total']
        return float(total) if total else 0.0


class UserSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user subscriptions (used by frontend after payment)"""
    
    class Meta:
        model = UserSubscription
        fields = ['profile', 'plan', 'price', 'billing_cycle']
    
    def validate(self, attrs):
        """Validate subscription creation"""
        profile = attrs.get('profile')
        plan = attrs.get('plan')
        
        # Check if plan is active
        if not plan.is_active:
            raise serializers.ValidationError("This subscription plan is not currently available.")
        
        # Check if user already has an active subscription for this plan
        existing = UserSubscription.objects.filter(
            profile=profile,
            plan=plan,
            status='active'
        ).exists()
        
        if existing:
            raise serializers.ValidationError(f"User already has an active subscription for {plan.name}")
        
        # Set price from plan if not provided
        if 'price' not in attrs or attrs['price'] is None:
            attrs['price'] = plan.base_price
        
        # Set billing cycle from plan if not provided
        if 'billing_cycle' not in attrs:
            attrs['billing_cycle'] = plan.billing_cycle
        
        return attrs
    
    def create(self, validated_data):
        """Create subscription in pending status (will be activated after payment)"""
        subscription = UserSubscription.objects.create(
            status='pending',
            **validated_data
        )
        return subscription


class BillingHistorySerializer(serializers.ModelSerializer):
    """Serializer for billing history"""
    subscription_name = serializers.CharField(source='user_subscription.plan.name', read_only=True)
    profile_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BillingHistory
        fields = [
            'id', 'user_subscription', 'subscription_name', 'profile_name',
            'amount', 'status', 'razorpay_payment_id', 'razorpay_order_id', 'description', 
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_profile_name(self, obj):
        """Get user's full name"""
        profile = obj.user_subscription.profile
        return f"{profile.first_name} {profile.last_name}".strip() or profile.email


class UserSubscriptionSummarySerializer(serializers.Serializer):
    """Summary of user's subscriptions for dashboard"""
    total_subscriptions = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    monthly_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    base_subscription = UserSubscriptionSerializer()
    addons = UserSubscriptionSerializer(many=True)
    next_billing_date = serializers.DateField()


class AdminUserSubscriptionUpdateSerializer(serializers.ModelSerializer):
    """Admin serializer for updating client subscription pricing"""
    
    class Meta:
        model = UserSubscription
        fields = ['price', 'status', 'billing_cycle', 'admin_notes']
    
    def validate_price(self, value):
        """Ensure price is positive"""
        if value < 0:
            raise serializers.ValidationError('Price must be a positive value.')
        return value


# Legacy serializer - kept for backward compatibility
class SubscriptionSerializer(serializers.ModelSerializer):
    """
    DEPRECATED: Use UserSubscriptionSerializer instead
    Kept for backward compatibility
    """
    class Meta:
        model = Subscription
        fields = ['id', 'profile', 'razorpay_subscription_id', 'plan', 'status', 'started_at', 'ended_at']