from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import Profile
import uuid
from decimal import Decimal


class SubscriptionPlan(models.Model):
    """
    Master subscription plans (Base + Add-ons)
    Managed by Admin only
    """
    PLAN_TYPES = [
        ('base', 'Base Subscription'),
        ('addon', 'Add-on Service'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True, help_text="e.g., Profile Marketing Services Fee, Skill Development Training")
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES, default='addon')
    description = models.TextField(blank=True, help_text="Detailed description of what this plan includes")
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Base price in USD. For add-ons, this is the default price (can be customized per user)"
    )
    is_mandatory = models.BooleanField(default=False, help_text="If true, all users must have this plan")
    is_active = models.BooleanField(default=True, help_text="Only active plans can be assigned to users")
    billing_cycle = models.CharField(
        max_length=20, 
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annual', 'Annual'),
            ('one_time', 'One-Time')
        ],
        default='monthly'
    )
    features = models.JSONField(default=list, blank=True, help_text="List of features included in this plan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['plan_type', 'name']
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
    
    def __str__(self):
        plan_type_label = 'BASE' if self.plan_type == 'base' else 'ADD-ON'
        return f"[{plan_type_label}] {self.name} - ${self.base_price}"
    
    def save(self, *args, **kwargs):
        # Ensure only one base plan exists
        if self.plan_type == 'base' and self.is_mandatory:
            SubscriptionPlan.objects.filter(plan_type='base', is_mandatory=True).exclude(id=self.id).update(is_mandatory=False)
        super().save(*args, **kwargs)


class UserSubscription(models.Model):
    """
    Tracks user's active subscriptions (Base + Add-ons)
    Each user can have one base subscription + multiple add-ons
    """
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('pending', 'Pending Payment'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='user_subscriptions')
    
    # Pricing (can be customized per user by admin)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Actual price for this user (may differ from base price for add-ons)"
    )
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    # Billing info
    razorpay_subscription_id = models.CharField(max_length=100, blank=True, null=True, help_text="Razorpay subscription ID")
    billing_cycle = models.CharField(max_length=20, default='monthly')
    next_billing_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True, help_text="When subscription became active")
    ended_at = models.DateTimeField(null=True, blank=True, help_text="When subscription was cancelled/expired")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin reference")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
        # Prevent duplicate active subscriptions for same plan
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'plan'],
                condition=models.Q(status='active'),
                name='unique_active_subscription_per_plan'
            )
        ]
    
    def __str__(self):
        profile_name = f"{self.profile.first_name} {self.profile.last_name}".strip() or self.profile.email
        return f"{profile_name} - {self.plan.name} ({self.status})"
    
    def activate(self):
        """Activate this subscription"""
        if self.status != 'active':
            self.status = 'active'
            self.started_at = timezone.now()
            if not self.next_billing_date:
                self.next_billing_date = self._calculate_next_billing_date()
            self.save()
            
            # Log billing history
            BillingHistory.objects.create(
                user_subscription=self,
                amount=self.price,
                status='success',
                description=f"Subscription activated: {self.plan.name}"
            )
    
    def cancel(self):
        """Cancel this subscription"""
        self.status = 'cancelled'
        self.ended_at = timezone.now()
        self.save()
    
    def _calculate_next_billing_date(self):
        """Calculate next billing date based on billing cycle"""
        from dateutil.relativedelta import relativedelta
        today = timezone.now().date()
        
        if self.billing_cycle == 'monthly':
            return today + relativedelta(months=1)
        elif self.billing_cycle == 'quarterly':
            return today + relativedelta(months=3)
        elif self.billing_cycle == 'annual':
            return today + relativedelta(years=1)
        else:  # one_time
            return None


class BillingHistory(models.Model):
    """
    Tracks all billing transactions for transparency
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='billing_history')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, help_text="Razorpay payment ID")
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, help_text="Razorpay order ID")
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional payment metadata")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Billing History'
        verbose_name_plural = 'Billing History'
    
    def __str__(self):
        profile_name = f"{self.user_subscription.profile.first_name} {self.user_subscription.profile.last_name}".strip()
        return f"{profile_name} - ${self.amount} ({self.status}) - {self.created_at.strftime('%Y-%m-%d')}"


# Legacy model - kept for backward compatibility
class Subscription(models.Model):
    """
    DEPRECATED: Use UserSubscription instead
    Kept for backward compatibility with existing code
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    razorpay_subscription_id = models.CharField(max_length=100, blank=True)
    plan = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='inactive')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Subscription (Legacy)'
        verbose_name_plural = 'Subscriptions (Legacy)'

    def __str__(self):
        return f"[LEGACY] Subscription for {self.profile.first_name} {self.profile.last_name} - {self.plan} ({self.status})"