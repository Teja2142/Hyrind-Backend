import razorpay
from django.conf import settings
from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription, SubscriptionPlan, UserSubscription, BillingHistory
from .serializers import (
    SubscriptionSerializer, 
    SubscriptionPlanSerializer, 
    UserSubscriptionSerializer,
    UserSubscriptionCreateSerializer,
    BillingHistorySerializer,
    UserSubscriptionSummarySerializer,
    AdminUserSubscriptionUpdateSerializer
)
from utils.profile_utils import ProfileResolveMixin

# Initialize Razorpay client
def get_razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
    if not key_id or not key_secret:
        return None
    return razorpay.Client(auth=(key_id, key_secret))


# ==================== NEW SUBSCRIPTION SYSTEM ====================

class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API to list available subscription plans
    GET /api/subscriptions/plans/ - List all active plans
    GET /api/subscriptions/plans/{id}/ - Get plan details
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Filter plans by type if specified"""
        queryset = super().get_queryset()
        plan_type = self.request.query_params.get('type', None)
        if plan_type in ['base', 'addon']:
            queryset = queryset.filter(plan_type=plan_type)
        return queryset.order_by('plan_type', 'base_price')
    
    @action(detail=False, methods=['get'])
    def base_plan(self, request):
        """Get the mandatory base subscription plan"""
        try:
            base_plan = SubscriptionPlan.objects.get(plan_type='base', is_mandatory=True, is_active=True)
            serializer = self.get_serializer(base_plan)
            return Response(serializer.data)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Base subscription plan not configured'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def addons(self, request):
        """Get all available add-on plans"""
        addons = SubscriptionPlan.objects.filter(plan_type='addon', is_active=True)
        serializer = self.get_serializer(addons, many=True)
        return Response(serializer.data)



class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    User subscription management
    GET /api/subscriptions/my-subscriptions/ - List user's subscriptions
    POST /api/subscriptions/my-subscriptions/ - Create new subscription (after payment)
    GET /api/subscriptions/my-subscriptions/{id}/ - Get subscription details
    PATCH /api/subscriptions/my-subscriptions/{id}/ - Update subscription
    DELETE /api/subscriptions/my-subscriptions/{id}/ - Cancel subscription
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return subscriptions for current user only"""
        if hasattr(self.request.user, 'profile'):
            return UserSubscription.objects.filter(profile=self.request.user.profile)
        return UserSubscription.objects.none()
    
    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return UserSubscriptionCreateSerializer
        elif self.action == 'update_price':
            return AdminUserSubscriptionUpdateSerializer
        return UserSubscriptionSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create new subscription after payment confirmation
        Expected data: {plan: uuid, price: decimal, razorpay_payment_id: string}
        """
        # Get user's profile
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add profile to request data
        data = request.data.copy()
        data['profile'] = request.user.profile.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        
        # Log action
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='subscription_created',
                target=f'UserSubscription:{subscription.id}',
                metadata={'plan': str(subscription.plan.id), 'price': str(subscription.price)}
            )
        except Exception:
            pass
        
        return Response(
            UserSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate subscription after payment confirmation
        POST /api/subscriptions/my-subscriptions/{id}/activate/
        Body: {razorpay_payment_id: string, razorpay_order_id: string, amount: decimal}
        """
        subscription = self.get_object()
        
        if subscription.status == 'active':
            return Response(
                {'message': 'Subscription is already active'},
                status=status.HTTP_200_OK
            )
        
        # Get payment details from Razorpay
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        amount = request.data.get('amount', subscription.price)
        
        # Update subscription
        subscription.razorpay_subscription_id = razorpay_payment_id
        subscription.activate()
        
        # Log action
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='subscription_activated',
                target=f'UserSubscription:{subscription.id}',
                metadata={'plan': subscription.plan.name, 'amount': str(amount)}
            )
        except Exception:
            pass

        # Send activation email to user
        try:
            from utils.email_service import EmailService, SubscriptionEmailTemplate
            subject, text_content, html_content = SubscriptionEmailTemplate.get_activation_email(subscription)
            EmailService.send_email(subject, text_content, html_content, to_emails=[subscription.profile.email])
        except Exception:
            pass
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel subscription
        POST /api/subscriptions/my-subscriptions/{id}/cancel/
        """
        subscription = self.get_object()
        
        if subscription.status in ['cancelled', 'expired']:
            return Response(
                {'message': 'Subscription is already cancelled'},
                status=status.HTTP_200_OK
            )
        
        subscription.cancel()
        
        # Log action
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='subscription_cancelled',
                target=f'UserSubscription:{subscription.id}',
                metadata={'plan': subscription.plan.name}
            )
        except Exception:
            pass

        # Send cancellation email to user
        try:
            from utils.email_service import EmailService, SubscriptionEmailTemplate
            subject, text_content, html_content = SubscriptionEmailTemplate.get_cancellation_email(subscription)
            EmailService.send_email(subject, text_content, html_content, to_emails=[subscription.profile.email])
        except Exception:
            pass
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get user's subscription summary
        GET /api/subscriptions/my-subscriptions/summary/
        """
        if not hasattr(request.user, 'profile'):
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile = request.user.profile
        subscriptions = UserSubscription.objects.filter(profile=profile, status='active')
        
        # Get base subscription
        base_subscription = subscriptions.filter(plan__plan_type='base').first()
        
        # Get add-ons
        addons = subscriptions.filter(plan__plan_type='addon')
        
        # Calculate monthly cost
        monthly_cost = subscriptions.aggregate(total=Sum('price'))['total'] or 0
        
        # Get next billing date
        next_billing_dates = subscriptions.exclude(next_billing_date__isnull=True).values_list('next_billing_date', flat=True)
        next_billing_date = min(next_billing_dates) if next_billing_dates else None
        
        data = {
            'total_subscriptions': subscriptions.count(),
            'active_subscriptions': subscriptions.count(),
            'monthly_cost': monthly_cost,
            'base_subscription': UserSubscriptionSerializer(base_subscription).data if base_subscription else None,
            'addons': UserSubscriptionSerializer(addons, many=True).data,
            'next_billing_date': next_billing_date,
        }
        
        return Response(data)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_price(self, request, pk=None):
        """
        Admin endpoint to update the price and other details of a user's subscription.
        PATCH /api/subscriptions/my-subscriptions/{id}/update_price/
        Body: {"price": 123.45, "status": "active", "billing_cycle": "monthly", "admin_notes": "Custom pricing"}
        """
        subscription = self.get_object()
        serializer = AdminUserSubscriptionUpdateSerializer(
            subscription, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log action
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='subscription_price_updated',
                target=f'UserSubscription:{subscription.id}',
                metadata={
                    'profile': str(subscription.profile.id),
                    'plan': subscription.plan.name,
                    'new_price': str(subscription.price)
                }
            )
        except Exception:
            pass
        
        return Response(
            UserSubscriptionSerializer(subscription).data,
            status=status.HTTP_200_OK
        )


class BillingHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Billing history for current user
    GET /api/subscriptions/billing-history/ - List all billing records
    GET /api/subscriptions/billing-history/{id}/ - Get specific billing record
    """
    serializer_class = BillingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return billing history for current user only"""
        if hasattr(self.request.user, 'profile'):
            return BillingHistory.objects.filter(
                user_subscription__profile=self.request.user.profile
            )
        return BillingHistory.objects.none()


class AdminUserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    Admin endpoint for managing all client subscriptions
    GET /api/subscriptions/admin/subscriptions/ - List all client subscriptions
    GET /api/subscriptions/admin/subscriptions/{id}/ - Get subscription details
    POST /api/subscriptions/admin/subscriptions/ - Create subscription for a client
    PATCH /api/subscriptions/admin/subscriptions/{id}/ - Update subscription (including price)
    DELETE /api/subscriptions/admin/subscriptions/{id}/ - Delete subscription
    """
    queryset = UserSubscription.objects.all().select_related('profile', 'plan')
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        """Use AdminUserSubscriptionUpdateSerializer for updates"""
        if self.action in ['update', 'partial_update']:
            return AdminUserSubscriptionUpdateSerializer
        return UserSubscriptionSerializer
    
    def get_queryset(self):
        """Return all subscriptions with optional filtering"""
        queryset = super().get_queryset()
        
        # Filter by profile/client
        profile_id = self.request.query_params.get('profile_id')
        if profile_id:
            queryset = queryset.filter(profile__id=profile_id)
        
        # Filter by status
        sub_status = self.request.query_params.get('status')
        if sub_status:
            queryset = queryset.filter(status=sub_status)
        
        # Filter by plan type
        plan_type = self.request.query_params.get('plan_type')
        if plan_type in ['base', 'addon']:
            queryset = queryset.filter(plan__plan_type=plan_type)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Log subscription creation by admin"""
        subscription = serializer.save()
        try:
            from audit.utils import log_action
            log_action(
                actor=self.request.user,
                action='admin_subscription_created',
                target=f'UserSubscription:{subscription.id}',
                metadata={
                    'profile': str(subscription.profile.id),
                    'plan': subscription.plan.name,
                    'price': str(subscription.price)
                }
            )
        except Exception:
            pass
    
    def perform_update(self, serializer):
        """Log subscription update by admin"""
        subscription = serializer.save()
        try:
            from audit.utils import log_action
            log_action(
                actor=self.request.user,
                action='admin_subscription_updated',
                target=f'UserSubscription:{subscription.id}',
                metadata={
                    'profile': str(subscription.profile.id),
                    'plan': subscription.plan.name,
                    'price': str(subscription.price)
                }
            )
        except Exception:
            pass


class SubscriptionPaymentWebhookView(APIView):
    """
    Webhook endpoint for payment confirmations
    POST /api/subscriptions/webhook/payment/
    
    This endpoint should be called by frontend after successful Razorpay payment
    Body: {
        subscription_id: uuid,
        razorpay_payment_id: string,
        razorpay_order_id: string,
        amount: decimal,
        status: 'success' | 'failed'
    }
    """
    permission_classes = [permissions.AllowAny]  # Webhook doesn't need auth
    
    def post(self, request):
        """Process payment webhook"""
        subscription_id = request.data.get('subscription_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        amount = request.data.get('amount')
        payment_status = request.data.get('status', 'success')
        
        if not all([subscription_id, razorpay_payment_id, amount]):
            return Response(
                {'error': 'Missing required fields: subscription_id, razorpay_payment_id, amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = UserSubscription.objects.get(id=subscription_id)
        except UserSubscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create billing record
        billing = BillingHistory.objects.create(
            user_subscription=subscription,
            amount=amount,
            status=payment_status,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            description=f"Payment for {subscription.plan.name}"
        )
        
        # Activate subscription if payment successful
        if payment_status == 'success' and subscription.status == 'pending':
            subscription.razorpay_subscription_id = razorpay_payment_id
            subscription.activate()
        
        return Response({
            'message': 'Payment processed successfully',
            'subscription': UserSubscriptionSerializer(subscription).data,
            'billing': BillingHistorySerializer(billing).data
        })


# ==================== LEGACY SUBSCRIPTION VIEWS ====================

class SubscriptionListCreateView(ProfileResolveMixin, generics.ListCreateAPIView):
    """
    DEPRECATED: Use UserSubscriptionViewSet instead
    Kept for backward compatibility
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plan = request.data.get('plan')
        profile = self.get_profile()
        # Create Razorpay subscription (mocked for now)
        razorpay_sub_id = 'sub_mocked_id'
        subscription = Subscription.objects.create(
            profile=profile,
            plan=plan,
            razorpay_subscription_id=razorpay_sub_id,
            status='active'
        )
        # Audit log
        try:
            from audit.utils import log_action
            # use profile.id (UUID) for external references
            log_action(actor=request.user if request.user.is_authenticated else None, action='subscription_created', target=f'Subscription:{subscription.id}', metadata={'plan': plan, 'profile_id': str(profile.id)})
        except Exception:
            pass
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    DEPRECATED: Use UserSubscriptionViewSet instead
    Kept for backward compatibility
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
