from django.db import models
from users.models import Profile

from django.db import models

from users.models import Profile
from django.db.models import JSONField
from django.utils import timezone
import uuid

ONBOARDING_STEPS = [
    'profile',
    'documents',
    'agreements',
    'questions',
    'review',
]

class Onboarding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    current_step = models.CharField(max_length=50, default='profile')
    steps_completed = JSONField(default=list, blank=True)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Onboarding for {self.profile.full_name} - Step: {self.current_step}"

    def mark_step_complete(self, step):
        if step not in self.steps_completed:
            self.steps_completed.append(step)
            self.save()
        if set(self.steps_completed) == set(ONBOARDING_STEPS):
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            # Audit log
            try:
                from audit.utils import log_action
                log_action(actor=None, action='onboarding_completed', target=f'Profile:{str(self.profile.id)}', metadata={'steps': self.steps_completed})
            except Exception:
                pass