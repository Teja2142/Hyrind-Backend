import uuid
from django.db import models
from django.conf import settings
from candidates.models import Candidate


class SubscriptionPlan(models.Model):
    """
    Admin-defined plan templates.
    Apply to a single candidate or broadcast to all active candidates at once.
    """
    BILLING_CYCLE_CHOICES = [
        ('monthly',   'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual',    'Annual'),
        ('one_time',  'One Time'),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_name     = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    currency      = models.CharField(max_length=10, default='USD')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    is_active     = models.BooleanField(default=True)
    created_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='subscription_plans_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.plan_name} — {self.amount} {self.currency}/{self.billing_cycle}'


class Subscription(models.Model):
    """
    Per-candidate recurring subscription record.
    Admin or billing webhook updates status.
    """
    STATUS_CHOICES = [
        ('trialing',    'Trialing'),
        ('active',      'Active'),
        ('past_due',    'Past Due'),
        ('canceled',    'Canceled'),
        ('unpaid',      'Unpaid'),
        ('grace_period','Grace Period'),
        ('paused',      'Paused'),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate     = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='subscription')
    plan_name     = models.CharField(max_length=100, default='Standard Marketing Plan')
    amount        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency      = models.CharField(max_length=10, default='USD')
    billing_cycle = models.CharField(max_length=20, default='monthly')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date    = models.DateField(blank=True, null=True)
    next_billing_at    = models.DateField(blank=True, null=True)
    last_payment_at    = models.DateTimeField(blank=True, null=True)
    grace_days         = models.IntegerField(default=5)
    grace_period_ends_at = models.DateTimeField(blank=True, null=True)
    failed_attempts    = models.IntegerField(default=0)
    # Masked billing method — NEVER store raw card numbers
    billing_method_brand     = models.CharField(max_length=30, blank=True, null=True)
    billing_method_last4     = models.CharField(max_length=4,  blank=True, null=True)
    billing_method_exp_month = models.CharField(max_length=2,  blank=True, null=True)
    billing_method_exp_year  = models.CharField(max_length=4,  blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'

    def __str__(self):
        return f'Sub({self.candidate.user.email}) — {self.status}'


class PaymentLineItem(models.Model):
    """
    Admin-controlled payment obligations visible on the Payments tab.
    Covers monthly fee, mock practice, interview support, etc.
    """
    CHARGE_TYPE_CHOICES = [
        ('monthly_service_fee',     'Monthly Service Fee'),
        ('mock_practice_fee',       'Mock Practice Fee'),
        ('interview_support_fee',   'Interview Support Fee'),
        ('operations_support_fee',  'Operations Support Fee'),
        ('other',                   'Other'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending',         'Pending'),
        ('paid',            'Paid'),
        ('overdue',         'Overdue'),
        ('waived',          'Waived'),
        ('partially_paid',  'Partially Paid'),
        ('cancelled',       'Cancelled'),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate     = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='payment_line_items')
    charge_name   = models.CharField(max_length=255)
    charge_type   = models.CharField(max_length=40, choices=CHARGE_TYPE_CHOICES)
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    currency      = models.CharField(max_length=10, default='USD')
    due_date      = models.DateField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_notes  = models.TextField(blank=True, null=True)
    is_internal_note = models.BooleanField(default=False)  # hide note from candidate

    # Due date change tracking
    previous_due_date       = models.DateField(blank=True, null=True)
    due_date_changed_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='due_date_changes',
    )
    due_date_change_reason  = models.TextField(blank=True, null=True)
    due_date_changed_at     = models.DateTimeField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='payment_items_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_line_items'
        ordering = ['due_date']

    def __str__(self):
        return f'{self.charge_name} — {self.candidate.user.email} — {self.payment_status}'


class Payment(models.Model):
    """Individual payment transaction record."""
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate     = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='payments')
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    currency      = models.CharField(max_length=10, default='USD')
    payment_type  = models.CharField(max_length=50, default='subscription')
    status        = models.CharField(max_length=20, default='completed')
    payment_date  = models.DateField(blank=True, null=True)
    transaction_ref = models.CharField(max_length=255, blank=True, null=True)
    notes         = models.TextField(blank=True, null=True)
    # Optional links for richer context
    invoice       = models.ForeignKey(
        'Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_records'
    )
    line_item     = models.ForeignKey(
        PaymentLineItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments'
    )
    recorded_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment({self.candidate.user.email}) — {self.amount} {self.currency}'


class Invoice(models.Model):
    """Invoice generated per billing period, with auto-numbered ID and PDF storage."""
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number  = models.CharField(max_length=50, unique=True, blank=True, null=True,
                                       help_text='Human-readable invoice number, e.g. INV-2026-000001')
    subscription    = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    candidate       = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='invoices')
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    currency        = models.CharField(max_length=10, default='USD')
    period_start    = models.DateField()
    period_end      = models.DateField()
    status          = models.CharField(max_length=20, default='pending')
    attempted_at    = models.DateTimeField(blank=True, null=True)
    paid_at         = models.DateTimeField(blank=True, null=True)
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
    failure_reason  = models.TextField(blank=True, null=True)
    # PDF stored under MEDIA_ROOT/invoices/<invoice_number>.pdf
    pdf_path        = models.CharField(max_length=500, blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-period_start']

    def __str__(self):
        return f'{self.invoice_number or "INV-?"} — {self.candidate.user.email}'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = self.created_at.year if self.created_at else __import__('datetime').date.today().year
            count = Invoice.objects.filter(invoice_number__startswith=f'INV-{year}-').count() + 1
            self.invoice_number = f'INV-{year}-{count:06d}'
        super().save(*args, **kwargs)
