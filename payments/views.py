from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Payment
from .serializers import (
    PaymentSerializer, CreateRazorpayOrderSerializer, VerifyRazorpayPaymentSerializer
)
import razorpay
import logging

logger = logging.getLogger(__name__)


def get_razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
    if not key_id or not key_secret:
        raise RuntimeError('Razorpay keys not configured in settings')
    return razorpay.Client(auth=(key_id, key_secret))


class PaymentListCreate(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateRazorpayOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        amount = data.get('amount')
        currency = data.get('currency', 'INR')
        notes = data.get('notes') or {}
        idempotency_key = data.get('idempotency_key')

        # Create local payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            currency=currency,
            provider=Payment.PROVIDER_RAZORPAY,
            status=Payment.STATUS_CREATED,
            metadata={'notes': notes} if notes else {},
            idempotency_key=idempotency_key
        )

        # Create Razorpay order (amount in paise)
        client = get_razorpay_client()
        razorpay_amount = int(round(float(amount) * 100))
        order_payload = {
            'amount': razorpay_amount,
            'currency': currency,
            'receipt': str(payment.id),
            'notes': notes or {}
        }

        try:
            razorpay_order = client.order.create(data=order_payload)
        except Exception as exc:
            logger.exception('Failed to create Razorpay order')
            payment.status = Payment.STATUS_FAILED
            payment.save(update_fields=['status'])
            return Response({'detail': 'Unable to create order with payment provider'}, status=status.HTTP_502_BAD_GATEWAY)

        # Save provider order id
        payment.provider_order_id = razorpay_order.get('id')
        payment.status = Payment.STATUS_PENDING
        payment.save(update_fields=['provider_order_id', 'status'])

        return Response({
            'order': razorpay_order,
            'key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
            'payment_uuid': payment.id
        }, status=status.HTTP_201_CREATED)


class VerifyRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = VerifyRazorpayPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        payment_id = data.get('payment_uuid')
        razorpay_payment_id = data['payment_id']
        razorpay_order_id = data['order_id']
        signature = data['signature']

        client = get_razorpay_client()
        # Verify signature
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': signature
            })
        except Exception as exc:
            logger.exception('Razorpay signature verification failed')
            return Response({'detail': 'Signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        # Find local payment either by our uuid or by order id
        payment = None
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
            except Payment.DoesNotExist:
                payment = None

        if not payment:
            try:
                payment = Payment.objects.get(provider_order_id=razorpay_order_id)
            except Payment.DoesNotExist:
                return Response({'detail': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update payment record
        payment.provider_payment_id = razorpay_payment_id
        payment.provider_signature = signature
        payment.status = Payment.STATUS_CAPTURED
        payment.mark_processed()
        payment.save(update_fields=['provider_payment_id', 'provider_signature', 'status', 'processed_at'])

        return Response({'success': True, 'payment_id': payment.id, 'status': payment.status})


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    """Endpoint to receive Razorpay webhooks. Verify signature and update payments accordingly."""

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        body = request.body
        signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', None)
        client = get_razorpay_client()

        try:
            if webhook_secret:
                client.utility.verify_webhook_signature(body, signature, webhook_secret)
        except Exception:
            logger.exception('Invalid webhook signature')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        payload = request.data
        event = payload.get('event')
        payload_data = payload.get('payload', {})

        # Handle common events
        if event == 'payment.captured':
            payment_obj = payload_data.get('payment', {}).get('entity', {})
            order_id = payment_obj.get('order_id')
            payment_id = payment_obj.get('id')
            try:
                p = Payment.objects.get(provider_order_id=order_id)
                p.provider_payment_id = payment_id
                p.status = Payment.STATUS_CAPTURED
                p.mark_processed()
                p.save(update_fields=['provider_payment_id', 'status', 'processed_at'])
            except Payment.DoesNotExist:
                logger.warning('Webhook: payment for order %s not found', order_id)

        elif event == 'payment.failed':
            payment_obj = payload_data.get('payment', {}).get('entity', {})
            order_id = payment_obj.get('order_id')
            try:
                p = Payment.objects.get(provider_order_id=order_id)
                p.status = Payment.STATUS_FAILED
                p.mark_processed()
                p.save(update_fields=['status', 'processed_at'])
            except Payment.DoesNotExist:
                logger.warning('Webhook: payment failed and local record not found for order %s', order_id)

        # Respond with 200 for successful verification
        return Response({'ok': True})
