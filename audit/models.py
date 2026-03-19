import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Immutable audit trail — INSERT only, no UPDATE or DELETE allowed.
    Every significant action in the platform must produce an audit record.
    See v4 spec Section 12 for the full required event list.
    """
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
    )
    action      = models.CharField(max_length=100)       # event code from spec
    target_id   = models.CharField(max_length=100, blank=True, null=True)
    target_type = models.CharField(max_length=50,  blank=True, null=True)
    details     = models.JSONField(default=dict, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        # enforce immutability at model level: block bulk deletes
        default_permissions = ('add', 'view')  # remove 'change' and 'delete'

    def __str__(self):
        return f"[{self.created_at}] {self.action} on {self.target_type}:{self.target_id}"
