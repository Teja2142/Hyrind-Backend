"""
Admin-configurable platform settings per v4 spec Section 15.3.
Single-row table — no code change needed to update UI text or Cal.com links.
"""
import uuid
from django.db import models


class AdminConfig(models.Model):
    """Singleton config table. Admin edits via Django admin without redeploy."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Cal.com scheduling links (spec Section 5.2 Component E)
    cal_training_url           = models.URLField(blank=True, null=True, help_text='Schedule Training Practice URL')
    cal_mock_practice_url      = models.URLField(blank=True, null=True, help_text='Schedule Mock Practice Call URL')
    cal_interview_training_url = models.URLField(blank=True, null=True, help_text='Schedule Interview Training URL')
    cal_interview_support_url  = models.URLField(blank=True, null=True, help_text='Schedule Interview Support URL')
    cal_operations_call_url    = models.URLField(blank=True, null=True, help_text='Schedule Operations Call URL')

    # Configurable UI text
    review_timeline_text      = models.CharField(
        max_length=100, default='24–48 hours',
        help_text="Review timeline shown to candidates (e.g. '24–48 hours')",
    )
    roles_locked_message      = models.TextField(
        blank=True, null=True,
        help_text='Message on Roles tab before roles are published',
    )
    credentials_locked_message = models.TextField(
        blank=True, null=True,
        help_text='Message on Credentials tab when locked',
    )
    help_desk_url             = models.URLField(blank=True, null=True, help_text='Support / Help Desk URL')
    grace_period_days         = models.IntegerField(default=5, help_text='Grace period in days before billing suspension')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table       = 'admin_config'
        verbose_name   = 'Admin Configuration'
        verbose_name_plural = 'Admin Configuration'

    def save(self, *args, **kwargs):
        if not self.pk and AdminConfig.objects.exists():
            raise ValueError('Only one AdminConfig record is allowed. Edit the existing row.')
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        """Return the singleton config, creating with defaults if absent."""
        obj, _ = cls.objects.get_or_create(
            pk=cls.objects.values_list('id', flat=True).first() or uuid.uuid4()
        )
        return obj

    def __str__(self):
        return 'Platform Admin Config'
