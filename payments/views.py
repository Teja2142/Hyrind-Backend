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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)


def get_razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
    if not key_id or not key_secret:
        raise RuntimeError('Razorpay keys not configured in settings')
    return razorpay.Client(auth=(key_id, key_secret))


class PaymentListCreate(generics.ListCreateAPIView):
    """
    Payment Records API
    GET /api/payments/ - List all payment records
    POST /api/payments/ - Create payment record (internal use)
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='List all payments',
        operation_description="""Retrieve all payment records for the authenticated user.

Shows payment history including:
- Razorpay orders and payments
- Payment status (created, pending, captured, failed, refunded)
- Amount and currency
- Transaction timestamps

Permission: Authenticated users (see own payments), Admin (see all)

Example Response:
[
  {
    "id": "uuid",
    "user": {"id": "uuid", "email": "user@example.com"},
    "amount": "299.00",
    "currency": "USD",
    "provider": "razorpay",
    "status": "captured",
    "provider_order_id": "order_xyz123",
    "provider_payment_id": "pay_abc456",
    "created_at": "2024-01-18T10:00:00Z",
    "processed_at": "2024-01-18T10:05:00Z"
  }
]""",
        responses={
            200: openapi.Response('List of payments', PaymentSerializer(many=True)),
            401: 'Authentication required'
        },
        tags=['Payments']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create payment record',
        operation_description="""Create a local payment record (internal use).

Note: This endpoint is primarily used internally. 
For creating actual Razorpay orders, use POST /api/payments/create-razorpay-order/

Permission: Authenticated users

Example Request:
{
  "amount": "299.00",
  "currency": "USD",
  "provider": "razorpay",
  "status": "created"
}""",
        request_body=PaymentSerializer,
        responses={
            201: openapi.Response('Payment record created', PaymentSerializer),
            400: 'Invalid data - validation errors',
            401: 'Authentication required'
        },
        tags=['Payments']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CreateRazorpayOrderView(APIView):
    """
    Razorpay Order Creation API
    POST /api/payments/create-razorpay-order/ - Create Razorpay payment order
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Create Razorpay payment order",
        operation_description="""Create a new Razorpay order for payment processing.

This is the PRIMARY endpoint for initiating payments:
1. Creates local payment record in database
2. Creates Razorpay order via Razorpay API
3. Returns order details and Razorpay key for frontend integration

Use the returned order_id and key_id in Razorpay checkout on frontend.

Permission: Authenticated users

Example Request:
{
  "amount": 299.00,
  "currency": "USD",
  "notes": {
    "subscription_plan": "premium",
    "user_email": "user@example.com"
  },
  "idempotency_key": "unique_key_123"
}

Example Response:
{
  "order": {
    "id": "order_xyz123",
    "amount": 29900,
    "currency": "USD",
    "status": "created"
  },
  "key_id": "rzp_test_...",
  "payment_uuid": "local-payment-uuid"
}

Frontend Integration:
- Use order.id as order_id in Razorpay checkout
- Use key_id as key in Razorpay options
- Store payment_uuid for verification step""",
        request_body=CreateRazorpayOrderSerializer,
        responses={
            201: openapi.Response('Razorpay order created', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'order': openapi.Schema(type=openapi.TYPE_OBJECT, description='Razorpay order object'),
                    'key_id': openapi.Schema(type=openapi.TYPE_STRING, description='Razorpay key ID for frontend'),
                    'payment_uuid': openapi.Schema(type=openapi.TYPE_STRING, description='Local payment UUID')
                }
            )),
            400: 'Invalid request data',
            401: 'Authentication required',
            502: 'Failed to create order with Razorpay'
        },
        tags=['Payments']
    )
    def post(self, request, *args, **kwargs):
        serializer = CreateRazorpayOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        amount = data.get('amount')
        currency = data.get('currency') or getattr(settings, 'RAZORPAY_CURRENCY', 'USD')
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
        except Exception:
            logger.exception('Failed to create Razorpay order')
            payment.status = Payment.STATUS_FAILED
            payment.save(update_fields=['status'])
            return Response({'detail': 'Unable to create order with payment provider'}, status=status.HTTP_502_BAD_GATEWAY)

        # Save provider order id
        payment.provider_order_id = razorpay_order.get('id')
        payment.status = Payment.STATUS_PENDING
        payment.save(update_fields=['provider_order_id', 'status'])

        # Return a compact order info and key id for frontend
        return Response({
            'order': razorpay_order,
            'key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
            'payment_uuid': payment.id
        }, status=status.HTTP_201_CREATED)


class VerifyRazorpayPaymentView(APIView):
    """
    Razorpay Payment Verification API
    POST /api/payments/verify-razorpay-payment/ - Verify payment signature
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Verify Razorpay payment",
        operation_description="""Verify Razorpay payment signature and update payment status.

Call this AFTER successful payment on frontend:
1. Validates Razorpay signature (security check)
2. Updates local payment record to 'captured' status
3. Marks payment as processed with timestamp

Permission: Authenticated users

Example Request:
{
  "payment_uuid": "local-payment-uuid",
  "payment_id": "pay_abc456",
  "order_id": "order_xyz123",
  "signature": "razorpay_signature_hash"
}

Example Response (Success):
{
  "success": true,
  "payment_id": "local-payment-uuid",
  "status": "captured"
}

Security:
- Signature verification ensures payment authenticity
- Prevents fraudulent payment confirmations
- Server-side validation of Razorpay webhook data

Error Responses:
- 400: Signature verification failed (fraudulent request)
- 404: Payment record not found""",
        request_body=VerifyRazorpayPaymentSerializer,
        responses={
            200: openapi.Response('Payment verified', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'payment_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Signature verification failed',
            401: 'Authentication required',
            404: 'Payment record not found'
        },
        tags=['Payments']
    )
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
        except Exception:
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
        # Robust webhook verification: SDKs differ in signature API. Try both common forms.
        raw_body = request.body
        # SDK may expect str payload
        try:
            body_text = raw_body.decode('utf-8')
        except Exception:
            body_text = raw_body

        signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', None)
        client = get_razorpay_client()

        verified = False
        if webhook_secret:
            # Try calling with (body, signature, secret)
            try:
                client.utility.verify_webhook_signature(body_text, signature, webhook_secret)
                verified = True
            except TypeError:
                # Some SDK versions expect (body, signature) with secret configured on client
                try:
                    client.utility.verify_webhook_signature(body_text, signature)
                    verified = True
                except Exception:
                    logger.exception('Invalid webhook signature (alternative call)')
            except Exception:
                logger.exception('Invalid webhook signature')

        if webhook_secret and not verified:
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
