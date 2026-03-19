from rest_framework import serializers
from django.conf import settings
from .models import SubscriptionPlan, Subscription, PaymentLineItem, Payment, Invoice


# ── Subscription Plans ────────────────────────────────────────────────────────

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SubscriptionPlan
        fields = [
            'id', 'plan_name', 'description', 'amount', 'currency',
            'billing_cycle', 'is_active', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ApplyPlanSerializer(serializers.Serializer):
    """
    Used by: POST /api/billing/plans/{plan_id}/apply/

    Either supply a candidate_id to apply to a single candidate,
    or set apply_to_all=true to push the plan to every active candidate
    (existing subscriptions are updated in-place).
    """
    candidate_id  = serializers.UUIDField(required=False, allow_null=True,
                                          help_text='Apply to this specific candidate only.')
    apply_to_all  = serializers.BooleanField(default=False,
                                              help_text='If true, overrides candidate_id and applies to every active candidate.')


# ── Subscriptions ─────────────────────────────────────────────────────────────

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Subscription
        fields = '__all__'
        read_only_fields = ['id', 'candidate', 'created_at', 'updated_at']


class CreateSubscriptionSerializer(serializers.Serializer):
    """Admin creates a subscription from scratch for a specific candidate."""
    plan_name            = serializers.CharField(max_length=100)
    description          = serializers.CharField(required=False, allow_blank=True)
    amount               = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency             = serializers.CharField(max_length=10, default='USD')
    billing_cycle        = serializers.ChoiceField(
        choices=['monthly', 'quarterly', 'annual', 'one_time'], default='monthly'
    )
    status               = serializers.ChoiceField(
        choices=['trialing', 'active', 'past_due', 'canceled', 'unpaid', 'grace_period', 'paused'],
        default='active',
    )
    start_date           = serializers.DateField(required=False, allow_null=True)
    next_billing_at      = serializers.DateField(required=False, allow_null=True)
    grace_days           = serializers.IntegerField(default=5)


# ── Payment Line Items ────────────────────────────────────────────────────────

class PaymentLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PaymentLineItem
        fields = '__all__'
        read_only_fields = [
            'id', 'candidate', 'previous_due_date',
            'due_date_changed_by', 'due_date_changed_at', 'created_by', 'created_at', 'updated_at',
        ]


# ── Payments ─────────────────────────────────────────────────────────────────

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Payment
        fields = '__all__'
        read_only_fields = ['id', 'candidate', 'recorded_by', 'created_at']


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Extended serializer for the candidate payment history dashboard view."""
    invoice_number    = serializers.SerializerMethodField()
    invoice_pdf_url   = serializers.SerializerMethodField()
    line_item_name    = serializers.SerializerMethodField()
    recorded_by_email = serializers.SerializerMethodField()

    class Meta:
        model  = Payment
        fields = [
            'id', 'amount', 'currency', 'payment_type', 'status',
            'payment_date', 'transaction_ref', 'notes',
            'invoice_number', 'invoice_pdf_url',
            'line_item_name', 'recorded_by_email', 'created_at',
        ]

    def get_invoice_number(self, obj):
        return obj.invoice.invoice_number if obj.invoice else None

    def get_invoice_pdf_url(self, obj):
        if obj.invoice and obj.invoice.pdf_path:
            request = self.context.get('request')
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            path = f'{media_url}{obj.invoice.pdf_path}'
            return request.build_absolute_uri(path) if request else path
        return None

    def get_line_item_name(self, obj):
        return obj.line_item.charge_name if obj.line_item else None

    def get_recorded_by_email(self, obj):
        return obj.recorded_by.email if obj.recorded_by else None


class RecordPaymentSerializer(serializers.Serializer):
    candidate_id    = serializers.UUIDField()
    amount          = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency        = serializers.CharField(max_length=10, default='USD')
    payment_type    = serializers.CharField(max_length=50, default='subscription')
    payment_date    = serializers.DateField()
    transaction_ref = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes           = serializers.CharField(required=False, allow_blank=True)
    line_item_id    = serializers.UUIDField(required=False, allow_null=True,
                                             help_text='Optionally link this payment to a specific line item.')
    # Invoice generation fields
    generate_invoice  = serializers.BooleanField(default=True,
                                                  help_text='Generate & email a PDF receipt automatically.')
    period_start      = serializers.DateField(required=False, allow_null=True)
    period_end        = serializers.DateField(required=False, allow_null=True)


# ── Razorpay ─────────────────────────────────────────────────────────────────

class CreateRazorpayOrderSerializer(serializers.Serializer):
    """Input for creating a Razorpay checkout order."""
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Amount in the major currency unit (e.g. 299.00 INR).',
    )
    currency = serializers.CharField(
        max_length=10, required=False, default='INR',
        help_text='ISO 4217 currency code. Defaults to RAZORPAY_CURRENCY from settings.',
    )
    payment_type = serializers.CharField(
        max_length=50, required=False, default='subscription',
        help_text='Internal label: subscription | one_time | addon.',
    )


class RazorpayOrderResponseSerializer(serializers.Serializer):
    """Response returned after a Razorpay order is created successfully."""
    razorpay_key_id  = serializers.CharField(help_text='Public key to initialise the Razorpay checkout modal.')
    order_id         = serializers.CharField(help_text='Razorpay order ID.')
    amount           = serializers.IntegerField(help_text='Amount in smallest currency unit (paise for INR).')
    currency         = serializers.CharField()
    local_payment_id = serializers.UUIDField(help_text='UUID of the locally created Payment record.')


class VerifyRazorpayPaymentSerializer(serializers.Serializer):
    """Input from the frontend after the user completes Razorpay checkout."""
    razorpay_order_id   = serializers.CharField(help_text='order_id returned by Razorpay on checkout success.')
    razorpay_payment_id = serializers.CharField(help_text='payment_id returned by Razorpay on checkout success.')
    razorpay_signature  = serializers.CharField(help_text='HMAC-SHA256 signature returned by Razorpay on checkout success.')


# ── Invoices ─────────────────────────────────────────────────────────────────

class InvoiceSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model  = Invoice
        fields = [
            'id', 'invoice_number', 'subscription', 'candidate',
            'amount', 'currency', 'period_start', 'period_end',
            'status', 'attempted_at', 'paid_at', 'payment_reference',
            'failure_reason', 'pdf_url', 'created_at',
        ]
        read_only_fields = ['id', 'invoice_number', 'pdf_url', 'created_at']

    def get_pdf_url(self, obj):
        if not obj.pdf_path:
            return None
        request  = self.context.get('request')
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        path = f'{media_url}{obj.pdf_path}'
        return request.build_absolute_uri(path) if request else path

