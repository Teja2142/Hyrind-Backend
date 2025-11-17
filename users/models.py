from django.db import models
import uuid
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    university = models.CharField(max_length=100, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    major = models.CharField(max_length=100, blank=True)
    visa_status = models.CharField(max_length=50, blank=True)
    graduation_date = models.DateField(null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    terms_accepted = models.BooleanField(default=False)
    # public_id is exposed externally; we ensure uniqueness via a data migration
    # migrations in this repo will populate existing rows before enforcing uniqueness
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.full_name or self.user.username
