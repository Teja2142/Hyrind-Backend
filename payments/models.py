from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
try:
    # Django 3.1+ has JSONField in models
    from django.db.models import JSONField
except Exception:
    from django.contrib.postgres.fields import JSONField
import uuid


class Payment(models.Model):
    PROVIDER_RAZORPAY = 'razorpay'

    STATUS_CREATED = 'created'
    STATUS_PENDING = 'pending'
    STATUS_AUTHORIZED = 'authorized'
    STATUS_CAPTURED = 'captured'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Created'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_AUTHORIZED, 'Authorized'),
        (STATUS_CAPTURED, 'Captured'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    provider = models.CharField(max_length=32, default=PROVIDER_RAZORPAY, editable=False)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_CREATED)

    # Provider-specific ids
    provider_order_id = models.CharField(max_length=256, blank=True, db_index=True)
    provider_payment_id = models.CharField(max_length=256, blank=True, db_index=True)
    provider_signature = models.CharField(max_length=512, blank=True)

    # (legacy) generic provider charge id removed — use provider_payment_id/provider_order_id

    metadata = JSONField(blank=True, null=True)
    idempotency_key = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def mark_processed(self):
        self.processed_at = timezone.now()
        self.save(update_fields=['processed_at'])

    def __str__(self):
        return f"Payment {self.id} ({self.provider}) - {self.amount} {self.currency} - {self.status}"


class WebhookEvent(models.Model):
    """Persist incoming webhook payloads for audit and debugging."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50, default='razorpay')
    event_type = models.CharField(max_length=100, blank=True)
    payload = JSONField(blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"Webhook {self.provider} {self.event_type} @ {self.received_at.isoformat()}"


class Invoice(models.Model):
    """
    Invoice model for tracking all financial transactions
    Supports both one-time payments and subscription billing
    """
    INVOICE_TYPE_CHOICES = [
        ('payment', 'One-time Payment'),
        ('subscription', 'Subscription Billing'),
        ('refund', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True, 
                                     help_text='Unique invoice number (e.g., INV-2026-00001)')
    
    # Relations
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='invoices', help_text='Related payment transaction')
    subscription = models.ForeignKey('subscriptions.UserSubscription', on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='invoices', 
                                    help_text='Related subscription')
    billing_history = models.ForeignKey('subscriptions.BillingHistory', on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='invoices',
                                       help_text='Related billing history entry')
    
    # Invoice details
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, default='payment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Billing information
    bill_to_name = models.CharField(max_length=200, help_text='Customer name')
    bill_to_email = models.EmailField(help_text='Customer email')
    bill_to_phone = models.CharField(max_length=20, blank=True)
    bill_to_address = models.TextField(blank=True, help_text='Customer billing address')
    
    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), 
                                   help_text='Tax rate in percentage')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Final amount to be paid')
    currency = models.CharField(max_length=10, default='INR')
    
    # Dates
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(help_text='Payment due date')
    paid_date = models.DateTimeField(null=True, blank=True, help_text='Date when payment was received')
    
    # Additional info
    description = models.TextField(blank=True, help_text='Invoice description or notes')
    notes = models.TextField(blank=True, help_text='Additional notes for customer')
    internal_notes = models.TextField(blank=True, help_text='Internal admin notes')
    
    # Payment tracking
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    
    # PDF generation
    pdf_file = models.FileField(upload_to='invoices/pdfs/', null=True, blank=True, 
                               help_text='Generated PDF invoice')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['invoice_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.bill_to_name} - {self.currency} {self.total_amount} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-generate invoice number if not set
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calculate totals
        self.calculate_totals()
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_invoice_number():
        """Generate unique invoice number in format: INV-YYYY-NNNNN"""
        year = timezone.now().year
        prefix = f"INV-{year}-"
        
        # Get last invoice number for current year
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            # Extract number and increment
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:05d}"
    
    def calculate_totals(self):
        """Calculate tax and total amount"""
        from decimal import Decimal
        # Calculate tax amount
        self.tax_amount = (self.subtotal * self.tax_rate) / Decimal('100')
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        # Ensure total is not negative
        if self.total_amount < 0:
            self.total_amount = Decimal('0.00')
    
    def mark_as_paid(self, payment_id=None, order_id=None):
        """Mark invoice as paid"""
        self.status = 'paid'
        self.paid_date = timezone.now()
        if payment_id:
            self.razorpay_payment_id = payment_id
        if order_id:
            self.razorpay_order_id = order_id
        self.save(update_fields=['status', 'paid_date', 'razorpay_payment_id', 'razorpay_order_id', 'updated_at'])
    
    def mark_as_failed(self):
        """Mark invoice as failed"""
        self.status = 'failed'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_refunded(self):
        """Mark invoice as refunded"""
        self.status = 'refunded'
        self.save(update_fields=['status', 'updated_at'])


class InvoiceLineItem(models.Model):
    """
    Line items for invoices - detailed breakdown of charges
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    
    description = models.CharField(max_length=500, help_text='Item description')
    quantity = models.IntegerField(default=1, help_text='Quantity')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price per unit')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Total amount (quantity * unit_price)')
    
    # Optional references
    subscription_plan = models.ForeignKey('subscriptions.SubscriptionPlan', on_delete=models.SET_NULL, 
                                         null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Invoice Line Item'
        verbose_name_plural = 'Invoice Line Items'
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"
    
    def save(self, *args, **kwargs):
        from decimal import Decimal
        # Calculate amount
        self.amount = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
        
        # Update invoice subtotal
        self.update_invoice_subtotal()
    
    def update_invoice_subtotal(self):
        """Update parent invoice subtotal"""
        if self.invoice:
            total = sum(item.amount for item in self.invoice.line_items.all())
            self.invoice.subtotal = total
            self.invoice.calculate_totals()
            self.invoice.save(update_fields=['subtotal', 'tax_amount', 'total_amount', 'updated_at'])
