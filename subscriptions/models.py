from django.db import models
from users.models import Profile
import uuid

class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    plan = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='inactive')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Subscription for {self.profile.first_name} {self.profile.last_name} - {self.plan} ({self.status})"