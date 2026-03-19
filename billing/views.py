"""
billing/views.py
"""
import hashlib
import hmac
import json
import logging
import os
from datetime import date

import razorpay
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from users.permissions import IsAdmin, IsApproved
from audit.utils import log_action
from notifications.utils import send_email, create_notification
from candidates.models import Candidate

from .models import SubscriptionPlan, Subscription, PaymentLineItem, Payment, Invoice
from .serializers import (
    SubscriptionPlanSerializer, ApplyPlanSerializer,
    SubscriptionSerializer, CreateSubscriptionSerializer,
    PaymentLineItemSerializer,
    PaymentSerializer, PaymentHistorySerializer, RecordPaymentSerializer,
    InvoiceSerializer,
    CreateRazorpayOrderSerializer, RazorpayOrderResponseSerializer,
    VerifyRazorpayPaymentSerializer,
)
from .utils import save_receipt_pdf, send_payment_receipt_email

logger = logging.getLogger(__name__)


# ── Razorpay helper ───────────────────────────────────────────────────────────

def _get_razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if not key_id or not key_secret:
        raise RuntimeError('Razorpay credentials are not configured in settings.')
    return razorpay.Client(auth=(key_id, key_secret))


# Subscription Plans -----------------------------------------------------------

@extend_schema(
    summary='List subscription plans',
    description='Returns all active subscription plan templates.',
    responses={200: SubscriptionPlanSerializer(many=True)},
    tags=['Billing - Plans'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def subscription_plan_list(request):
    qs = SubscriptionPlan.objects.filter(is_active=True)
    return Response(SubscriptionPlanSerializer(qs, many=True).data)


@extend_schema(
    summary='Create a subscription plan (Admin)',
    description='Admin creates a reusable plan template. Can later be applied to one or all candidates.',
    request=SubscriptionPlanSerializer,
    responses={201: SubscriptionPlanSerializer},
    tags=['Billing - Plans'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_subscription_plan(request):
    ser = SubscriptionPlanSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    plan = ser.save(created_by=request.user)
    log_action(request.user, 'subscription_plan_created', str(plan.id), 'subscription_plan',
               {'plan_name': plan.plan_name, 'amount': str(plan.amount)})
    return Response(SubscriptionPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Update a subscription plan (Admin)',
    request=SubscriptionPlanSerializer,
    responses={200: SubscriptionPlanSerializer},
    tags=['Billing - Plans'],
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_subscription_plan(request, plan_id):
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


@extend_schema(
    summary='Apply a plan to a candidate or all candidates (Admin)',
    description=(
        'Set apply_to_all=true to push this plan to every active candidate, '
        'or provide candidate_id to target just one. '
        'Existing subscriptions are updated in-place; new ones are created if none exist. '
        'Affected candidates receive an email notification.'
    ),
    request=ApplyPlanSerializer,
    responses={
        200: OpenApiResponse(description='Plan applied. Returns count or updated subscription.'),
        404: OpenApiResponse(description='Plan or candidate not found'),
    },
    tags=['Billing - Plans'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def apply_subscription_plan(request, plan_id):
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

    ser = ApplyPlanSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data
    apply_to_all = d.get('apply_to_all', False)
    candidate_id = d.get('candidate_id')

    plan_defaults = dict(
        plan_name=plan.plan_name,
        amount=plan.amount,
        currency=plan.currency,
        billing_cycle=plan.billing_cycle,
        status='active',
    )

    if apply_to_all:
        candidates = Candidate.objects.select_related('user').all()
        updated = 0
        for c in candidates:
            Subscription.objects.update_or_create(candidate=c, defaults=plan_defaults)
            send_email(
                to=c.user.email,
                subject='Your Hyrind Subscription Has Been Updated',
                html=(
                    f'<p>Hi, your subscription has been updated to the <strong>{plan.plan_name}</strong> plan '
                    f'({plan.currency} {plan.amount}/{plan.billing_cycle}).</p>'
                ),
                email_type='subscription_updated',
            )
            create_notification(c.user, 'Subscription Updated', f'Your plan has been updated to {plan.plan_name}.')
            updated += 1
        log_action(request.user, 'subscription_plan_applied_all', str(plan.id), 'subscription_plan',
                   {'plan_name': plan.plan_name, 'affected': updated})
        return Response({'message': f'Plan applied to all {updated} candidates.'})

    if not candidate_id:
        return Response({'error': 'Provide candidate_id or set apply_to_all=true'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    sub, _ = Subscription.objects.update_or_create(candidate=candidate, defaults=plan_defaults)
    send_email(
        to=candidate.user.email,
        subject='Your Hyrind Subscription Has Been Updated',
        html=(
            f'<p>Hi, your subscription has been updated to the <strong>{plan.plan_name}</strong> plan '
            f'({plan.currency} {plan.amount}/{plan.billing_cycle}).</p>'
        ),
        email_type='subscription_updated',
    )
    create_notification(candidate.user, 'Subscription Updated', f'Your plan has been updated to {plan.plan_name}.')
    log_action(request.user, 'subscription_plan_applied', str(candidate.id), 'candidate',
               {'plan_id': str(plan.id), 'plan_name': plan.plan_name})
    return Response({
        'message': f'Plan applied to candidate {candidate.user.email}.',
        'subscription': SubscriptionSerializer(sub).data,
    })


# Subscriptions ----------------------------------------------------------------

@extend_schema(
    summary="Get candidate's subscription",
    responses={200: SubscriptionSerializer, 404: OpenApiResponse(description='No subscription found')},
    tags=['Billing - Subscriptions'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def get_subscription(request, candidate_id):
    try:
        sub = Subscription.objects.get(candidate_id=candidate_id)
    except Subscription.DoesNotExist:
        return Response({'error': 'No subscription found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(SubscriptionSerializer(sub).data)


@extend_schema(
    summary='Create a subscription for a candidate (Admin)',
    description='Admin manually creates a subscription for this candidate without a plan template.',
    request=CreateSubscriptionSerializer,
    responses={
        201: SubscriptionSerializer,
        400: OpenApiResponse(description='Subscription already exists - use update endpoint'),
    },
    tags=['Billing - Subscriptions'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_subscription(request, candidate_id):
    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    if Subscription.objects.filter(candidate=candidate).exists():
        return Response(
            {'error': 'Subscription already exists. Use the update endpoint.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ser = CreateSubscriptionSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data
    sub = Subscription.objects.create(
        candidate=candidate,
        plan_name=d['plan_name'],
        amount=d['amount'],
        currency=d.get('currency', 'USD'),
        billing_cycle=d.get('billing_cycle', 'monthly'),
        status=d.get('status', 'active'),
        start_date=d.get('start_date'),
        next_billing_at=d.get('next_billing_at'),
        grace_days=d.get('grace_days', 5),
    )
    send_email(
        to=candidate.user.email,
        subject='Welcome to Your Hyrind Subscription',
        html=f'<p>Your <strong>{sub.plan_name}</strong> subscription is now active. Amount: {sub.currency} {sub.amount}/{sub.billing_cycle}.</p>',
        email_type='subscription_created',
    )
    create_notification(candidate.user, 'Subscription Created', f'Your {sub.plan_name} subscription is now active.')
    log_action(request.user, 'subscription_created', str(candidate.id), 'candidate',
               {'plan_name': sub.plan_name, 'amount': str(sub.amount)})
    return Response(SubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Update subscription (Admin)',
    request=SubscriptionSerializer,
    responses={200: SubscriptionSerializer},
    tags=['Billing - Subscriptions'],
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_subscription(request, candidate_id):
    try:
        sub = Subscription.objects.get(candidate_id=candidate_id)
    except Subscription.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    old = sub.status
    for field in ['status', 'plan_name', 'amount', 'next_billing_at', 'grace_days',
                  'billing_method_brand', 'billing_method_last4',
                  'billing_method_exp_month', 'billing_method_exp_year']:
        if field in request.data:
            setattr(sub, field, request.data[field])
    sub.save()
    log_action(request.user, 'billing_status_changed', str(sub.candidate_id), 'subscription',
               {'old_status': old, 'new_status': sub.status})
    return Response(SubscriptionSerializer(sub).data)


# Payment Line Items -----------------------------------------------------------

@extend_schema(
    summary='List payment line items for a candidate',
    responses={200: PaymentLineItemSerializer(many=True)},
    tags=['Billing - Line Items'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def payment_items(request, candidate_id):
    items = PaymentLineItem.objects.filter(candidate_id=candidate_id)
    return Response(PaymentLineItemSerializer(items, many=True).data)


@extend_schema(
    summary='Create a payment line item (Admin)',
    request=PaymentLineItemSerializer,
    responses={201: PaymentLineItemSerializer},
    tags=['Billing - Line Items'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_payment_item(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = PaymentLineItemSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    item = ser.save(candidate=c, created_by=request.user)
    create_notification(c.user, 'New Payment Due',
                        f'A new charge "{item.charge_name}" of {item.amount} {item.currency} is due on {item.due_date}.')
    return Response(PaymentLineItemSerializer(item).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Update a payment line item (Admin)',
    description='Update fields on an existing line item. Due date changes are tracked and the candidate is notified.',
    request=PaymentLineItemSerializer,
    responses={200: PaymentLineItemSerializer},
    tags=['Billing - Line Items'],
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_payment_item(request, candidate_id, item_id):
    try:
        item = PaymentLineItem.objects.get(id=item_id, candidate_id=candidate_id)
    except PaymentLineItem.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if 'due_date' in request.data and str(item.due_date) != str(request.data['due_date']):
        item.previous_due_date      = item.due_date
        item.due_date_changed_by    = request.user
        item.due_date_change_reason = request.data.get('change_reason', '')
        item.due_date_changed_at    = timezone.now()
        log_action(request.user, 'payment_due_date_changed', str(item.id), 'payment_line_item', {
            'old_date': str(item.due_date), 'new_date': str(request.data['due_date']),
        })
        candidate = item.candidate
        create_notification(candidate.user, 'Payment Due Date Changed',
                            f'Due date for "{item.charge_name}" has been updated.')
        send_email(
            to=candidate.user.email,
            subject='Payment Due Date Updated - Hyrind',
            html=f'<p>The due date for <strong>{item.charge_name}</strong> has been updated to {request.data["due_date"]}.</p>',
            email_type='payment_due_date_changed',
        )

    ser = PaymentLineItemSerializer(item, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


# Payments (record, history, PDF receipt) --------------------------------------

@extend_schema(
    summary='Record a payment (Admin)',
    description=(
        'Record an incoming payment for a candidate. '
        'When generate_invoice=true (default), an Invoice record is created, a PDF receipt is generated, '
        'saved to disk, and emailed to the candidate with the PDF attached.'
    ),
    request=RecordPaymentSerializer,
    responses={
        201: PaymentHistorySerializer,
        404: OpenApiResponse(description='Candidate or line item not found'),
    },
    tags=['Billing - Payments'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def record_payment(request):
    ser = RecordPaymentSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    try:
        c = Candidate.objects.get(id=d['candidate_id'])
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    line_item = None
    if d.get('line_item_id'):
        try:
            line_item = PaymentLineItem.objects.get(id=d['line_item_id'], candidate=c)
        except PaymentLineItem.DoesNotExist:
            return Response({'error': 'Line item not found for this candidate'}, status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.create(
        candidate=c,
        amount=d['amount'],
        currency=d.get('currency', 'USD'),
        payment_type=d.get('payment_type', 'subscription'),
        payment_date=d.get('payment_date'),
        notes=d.get('notes', ''),
        transaction_ref=d.get('transaction_ref', ''),
        status='completed',
        recorded_by=request.user,
        line_item=line_item,
    )

    if line_item:
        line_item.payment_status = 'paid'
        line_item.save(update_fields=['payment_status'])

    if c.status == 'payment_pending':
        c.status = 'payment_completed'
        c.save(update_fields=['status'])

    # Generate invoice + PDF + email
    invoice = None
    if d.get('generate_invoice', True):
        period_start = d.get('period_start') or date.today()
        period_end   = d.get('period_end')   or date.today()
        try:
            sub = c.subscription
        except Subscription.DoesNotExist:
            sub = None

        if sub:
            invoice = Invoice.objects.create(
                subscription=sub,
                candidate=c,
                amount=payment.amount,
                currency=payment.currency,
                period_start=period_start,
                period_end=period_end,
                status='paid',
                paid_at=timezone.now(),
                payment_reference=payment.transaction_ref,
            )
            pdf_rel_path = save_receipt_pdf(payment, invoice)
            if pdf_rel_path:
                invoice.pdf_path = pdf_rel_path
                invoice.save(update_fields=['pdf_path'])

            payment.invoice = invoice
            payment.save(update_fields=['invoice'])

        send_payment_receipt_email(payment, invoice)

    log_action(request.user, 'payment_recorded', str(c.id), 'candidate',
               {'amount': str(d['amount']), 'payment_id': str(payment.id)})
    return Response(
        PaymentHistorySerializer(payment, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    summary='Candidate payment history dashboard',
    description='Returns full payment history for a candidate including invoice numbers and PDF receipt links.',
    parameters=[
        OpenApiParameter('payment_type', description='Filter by type (subscription, one_time ...)', required=False),
        OpenApiParameter('status',       description='Filter by status (completed, pending, failed)',  required=False),
    ],
    responses={200: PaymentHistorySerializer(many=True)},
    tags=['Billing - Payments'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def payment_history(request, candidate_id):
    qs = (
        Payment.objects
        .filter(candidate_id=candidate_id)
        .select_related('invoice', 'line_item', 'recorded_by')
        .order_by('-created_at')
    )
    if pt := request.query_params.get('payment_type'):
        qs = qs.filter(payment_type=pt)
    if st := request.query_params.get('status'):
        qs = qs.filter(status=st)
    return Response(PaymentHistorySerializer(qs, many=True, context={'request': request}).data)


@extend_schema(
    summary='Download payment PDF receipt',
    description='Returns the PDF receipt for a specific payment as a downloadable file.',
    responses={
        200: OpenApiResponse(description='PDF file download'),
        404: OpenApiResponse(description='Payment or PDF not found'),
    },
    tags=['Billing - Payments'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def payment_receipt_download(request, candidate_id, payment_id):
    try:
        payment = Payment.objects.select_related('invoice').get(
            id=payment_id, candidate_id=candidate_id,
        )
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

    if payment.invoice and payment.invoice.pdf_path:
        abs_path = os.path.join(settings.MEDIA_ROOT, payment.invoice.pdf_path)
        if os.path.exists(abs_path):
            filename = os.path.basename(abs_path)
            return FileResponse(open(abs_path, 'rb'), content_type='application/pdf',
                                as_attachment=True, filename=filename)

    # On-the-fly generation
    from .utils import generate_receipt_pdf
    pdf_bytes = generate_receipt_pdf(payment, getattr(payment, 'invoice', None))
    if not pdf_bytes:
        return Response({'error': 'PDF generation unavailable'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    filename = f'receipt-{str(payment.id)[:8]}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# Invoices ---------------------------------------------------------------------

@extend_schema(
    summary='List invoices for a candidate',
    responses={200: InvoiceSerializer(many=True)},
    tags=['Billing - Invoices'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def invoice_list(request, candidate_id):
    invoices = Invoice.objects.filter(candidate_id=candidate_id).order_by('-created_at')
    return Response(InvoiceSerializer(invoices, many=True, context={'request': request}).data)


@extend_schema(
    summary='Record a payment for a candidate (Admin, candidate-scoped URL)',
    description=(
        'Same as POST /api/billing/record/ but with candidate_id in the URL path — '
        'matches the frontend: POST /api/billing/{candidate_id}/payments/record/. '
        'The candidate_id from the URL is automatically used; you do not need to include it in the body.'
    ),
    request=RecordPaymentSerializer,
    responses={
        201: PaymentHistorySerializer,
        404: OpenApiResponse(description='Candidate not found'),
    },
    tags=['Billing - Payments'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def record_payment_scoped(request, candidate_id):
    """Injects candidate_id from URL into request data, then runs the record_payment logic inline."""
    ser = RecordPaymentSerializer(data={**request.data, 'candidate_id': str(candidate_id)})
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    try:
        c = Candidate.objects.get(id=d['candidate_id'])
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    line_item = None
    if d.get('line_item_id'):
        try:
            line_item = PaymentLineItem.objects.get(id=d['line_item_id'], candidate=c)
        except PaymentLineItem.DoesNotExist:
            return Response({'error': 'Line item not found'}, status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.create(
        candidate=c, amount=d['amount'], currency=d.get('currency', 'USD'),
        payment_type=d.get('payment_type', 'subscription'),
        payment_date=d.get('payment_date'), notes=d.get('notes', ''),
        transaction_ref=d.get('transaction_ref', ''), status='completed',
        recorded_by=request.user, line_item=line_item,
    )
    if line_item:
        line_item.payment_status = 'paid'
        line_item.save(update_fields=['payment_status'])
    if c.status == 'payment_pending':
        c.status = 'payment_completed'
        c.save(update_fields=['status'])

    invoice = None
    if d.get('generate_invoice', True):
        period_start = d.get('period_start') or date.today()
        period_end   = d.get('period_end')   or date.today()
        try:
            sub = c.subscription
            invoice = Invoice.objects.create(
                subscription=sub, candidate=c, amount=payment.amount,
                currency=payment.currency, period_start=period_start,
                period_end=period_end, status='paid', paid_at=timezone.now(),
                payment_reference=payment.transaction_ref,
            )
            pdf_rel = save_receipt_pdf(payment, invoice)
            if pdf_rel:
                invoice.pdf_path = pdf_rel
                invoice.save(update_fields=['pdf_path'])
            payment.invoice = invoice
            payment.save(update_fields=['invoice'])
        except Subscription.DoesNotExist:
            pass
        send_payment_receipt_email(payment, invoice)

    log_action(request.user, 'payment_recorded', str(c.id), 'candidate',
               {'amount': str(d['amount']), 'payment_id': str(payment.id)})
    return Response(
        PaymentHistorySerializer(payment, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )


# ── Razorpay — Create Order ───────────────────────────────────────────────────

@extend_schema(
    summary='Create a Razorpay payment order',
    description=(
        'Creates a Razorpay order and a local pending Payment record. '
        'The `razorpay_key_id` and `order_id` returned here must be passed '
        'to the Razorpay checkout widget on the frontend.'
    ),
    request=CreateRazorpayOrderSerializer,
    responses={
        201: RazorpayOrderResponseSerializer,
        400: OpenApiResponse(description='Validation error'),
        502: OpenApiResponse(description='Razorpay gateway error'),
    },
    tags=['Billing - Razorpay'],
)
@api_view(['POST'])
@permission_classes([IsApproved])
def create_razorpay_order(request, candidate_id):
    serializer = CreateRazorpayOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Razorpay expects amount in smallest currency unit (paise for INR)
    amount_paise = int(data['amount'] * 100)
    currency = data.get('currency') or getattr(settings, 'RAZORPAY_CURRENCY', 'INR')

    try:
        client = _get_razorpay_client()
        rz_order = client.order.create({
            'amount': amount_paise,
            'currency': currency,
            'receipt': f'candidate_{candidate_id}',
            'payment_capture': 1,
        })
    except Exception as exc:
        logger.error('Razorpay order creation failed: %s', exc)
        return Response({'error': 'Payment gateway error. Please try again.'},
                        status=status.HTTP_502_BAD_GATEWAY)

    payment = Payment.objects.create(
        candidate_id=candidate_id,
        amount=data['amount'],
        currency=currency,
        payment_type=data.get('payment_type', 'subscription'),
        status='pending',
        notes=rz_order['id'],   # store Razorpay order ID for cross-reference
        recorded_by=request.user,
    )
    log_action(request.user, 'razorpay_order_created', str(candidate_id), 'payment',
               {'razorpay_order_id': rz_order['id'], 'amount': str(data['amount'])})

    return Response({
        'razorpay_key_id':  settings.RAZORPAY_KEY_ID,
        'order_id':         rz_order['id'],
        'amount':           amount_paise,
        'currency':         currency,
        'local_payment_id': str(payment.id),
    }, status=status.HTTP_201_CREATED)


# ── Razorpay — Verify Payment ─────────────────────────────────────────────────

@extend_schema(
    summary='Verify and capture a Razorpay payment',
    description=(
        'After the user completes checkout the frontend receives `razorpay_order_id`, '
        '`razorpay_payment_id`, and `razorpay_signature`. Send them here to verify the '
        'HMAC-SHA256 signature and mark the local payment as completed.'
    ),
    request=VerifyRazorpayPaymentSerializer,
    responses={
        200: OpenApiResponse(description='Payment verified and captured'),
        400: OpenApiResponse(description='Invalid or tampered signature'),
    },
    tags=['Billing - Razorpay'],
)
@api_view(['POST'])
@permission_classes([IsApproved])
def verify_razorpay_payment(request, candidate_id):
    serializer = VerifyRazorpayPaymentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Verify HMAC-SHA256 signature
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
        f"{data['razorpay_order_id']}|{data['razorpay_payment_id']}".encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, data['razorpay_signature']):
        logger.warning('Razorpay signature mismatch for candidate %s', candidate_id)
        return Response({'error': 'Payment signature verification failed.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Update the matching pending payment to completed
    Payment.objects.filter(
        candidate_id=candidate_id,
        status='pending',
        notes=data['razorpay_order_id'],
    ).update(status='completed', notes=data['razorpay_payment_id'])

    log_action(request.user, 'razorpay_payment_verified', str(candidate_id), 'payment', {
        'razorpay_order_id':   data['razorpay_order_id'],
        'razorpay_payment_id': data['razorpay_payment_id'],
    })
    return Response({'message': 'Payment verified and recorded successfully.'})


# ── Razorpay — Webhook ────────────────────────────────────────────────────────

@extend_schema(exclude=True)   # Webhooks are not part of the public API docs
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):
    """
    Razorpay sends server-to-server webhook events here.
    Configure this URL in the Razorpay dashboard.
    Always verifies X-Razorpay-Signature before acting on any event.
    """
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
    if not webhook_secret:
        logger.error('RAZORPAY_WEBHOOK_SECRET is not configured.')
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    signature = request.headers.get('X-Razorpay-Signature', '')
    body = request.body

    expected = hmac.new(
        webhook_secret.encode('utf-8'),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        logger.warning('Razorpay webhook: invalid signature')
        return Response({'error': 'Invalid signature.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        payload = json.loads(body)
        event = payload.get('event', '')
        entity = payload.get('payload', {}).get('payment', {}).get('entity', {})

        if event == 'payment.captured':
            razorpay_payment_id = entity.get('id', '')
            razorpay_order_id   = entity.get('order_id', '')
            updated = Payment.objects.filter(
                status='pending', notes=razorpay_order_id
            ).update(status='completed', notes=razorpay_payment_id)
            logger.info('Webhook payment.captured: order=%s updated=%d', razorpay_order_id, updated)

        elif event == 'payment.failed':
            razorpay_order_id = entity.get('order_id', '')
            Payment.objects.filter(
                status='pending', notes=razorpay_order_id
            ).update(status='failed')
            logger.warning('Webhook payment.failed: order=%s', razorpay_order_id)

    except Exception as exc:
        logger.exception('Razorpay webhook processing error: %s', exc)
        # Always return 200 to stop Razorpay retrying on parse errors
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_200_OK)
