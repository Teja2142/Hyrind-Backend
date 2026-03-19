import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """In-app notification record per v4 spec Section 5.2 Component F."""
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title   = models.CharField(max_length=255)
    message = models.TextField()
    link    = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.user.email}] {self.title}'


class EmailLog(models.Model):
    """
    Track every outbound email per v4 spec Section 9.
    All transactional emails are logged here with send status.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_email = models.EmailField()
    email_type      = models.CharField(max_length=100)   # event code, e.g. 'registration_approved'
    status          = models.CharField(max_length=20, default='sent')   # sent | failed
    error_message   = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email_type} → {self.recipient_email} ({self.status})'
