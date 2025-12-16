from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
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
