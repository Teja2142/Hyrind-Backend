import stripe
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Subscription
from .serializers import SubscriptionSerializer
from utils.profile_utils import ProfileResolveMixin

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_placeholder')


class SubscriptionListCreateView(ProfileResolveMixin, generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plan = request.data.get('plan')
        profile = self.get_profile()
        # Create Stripe subscription (mocked for now)
        stripe_sub_id = 'sub_mocked_id'
        subscription = Subscription.objects.create(
            profile=profile,
            plan=plan,
            stripe_subscription_id=stripe_sub_id,
            status='active'
        )
        # Audit log
        try:
            from audit.utils import log_action
            # use public_id for external references
            log_action(actor=request.user if request.user.is_authenticated else None, action='subscription_created', target=f'Subscription:{subscription.id}', metadata={'plan': plan, 'profile_public_id': str(profile.public_id)})
        except Exception:
            pass
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
