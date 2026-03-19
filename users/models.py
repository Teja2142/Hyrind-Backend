import uuid
import re
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ---------------------------------------------------------------------------
# Custom User Manager
# ---------------------------------------------------------------------------

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('approval_status', 'approved')
        extra_fields.setdefault('portal_access', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# ---------------------------------------------------------------------------
# User  single auth model for all roles
# ---------------------------------------------------------------------------

class User(AbstractBaseUser, PermissionsMixin):
    """
    Central auth model for all roles per v4 spec Section 2.
    Roles: candidate, recruiter, team_lead, team_manager, admin, finance_admin.
    Approval flow: pending_approval  approved (admin-controlled).
    portal_access=True only after admin approval.
    """
    ROLE_CHOICES = [
        ('candidate',     'Candidate'),
        ('recruiter',     'Recruiter'),
        ('team_lead',     'Team Lead'),
        ('team_manager',  'Team Manager'),
        ('admin',         'Admin'),
        ('finance_admin', 'Finance Admin'),
    ]
    APPROVAL_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('approved',         'Approved'),
        ('rejected',         'Rejected'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email           = models.EmailField(unique=True)
    role            = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='pending_approval')
    # portal_access: set True only after admin approval
    portal_access   = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


# ---------------------------------------------------------------------------
# Profile  extended registration fields per v4 spec Section 3
# ---------------------------------------------------------------------------

class Profile(models.Model):
    """
    Extended profile attached 1-to-1 with User.
    Stores all registration-time fields (identity, academic, source, links, visa).
    Intake and credential data lives in the candidates app.
    """
    VISA_STATUS_CHOICES = [
        ('H1B',        'H1B'),
        ('OPT',        'OPT'),
        ('CPT',        'CPT'),
        ('Green Card', 'Green Card'),
        ('US Citizen', 'US Citizen'),
        ('EAD',        'EAD'),
        ('TN',         'TN'),
        ('Other',      'Other'),
    ]
    HEAR_ABOUT_US_CHOICES = [
        ('LinkedIn',     'LinkedIn'),
        ('Google',       'Google'),
        ('University',   'University'),
        ('Friend',       'Friend'),
        ('Social Media', 'Social Media'),
        ('Other',        'Other'),
    ]

    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Identity
    first_name = models.CharField(max_length=60, blank=True, default='')
    last_name  = models.CharField(max_length=60, blank=True, default='')
    phone      = models.CharField(max_length=30, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    # Location (optional at registration; full address captured in intake)
    current_location  = models.CharField(max_length=255, blank=True, null=True)

    # Academic (pre-filled from registration; full details captured in intake)
    university_name = models.CharField(max_length=120, blank=True, null=True)
    major_degree    = models.CharField(max_length=120, blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)

    # Source / discovery
    how_did_you_hear_about_us = models.CharField(
        max_length=30, choices=HEAR_ABOUT_US_CHOICES, blank=True, null=True
    )
    # friend_name required when source == 'Friend'
    friend_name = models.CharField(max_length=120, blank=True, null=True)

    # Profile links
    linkedin_url  = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)

    # Visa (optional at registration; verified in intake)
    visa_status = models.CharField(max_length=30, choices=VISA_STATUS_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.user.email

    def __str__(self):
        return self.full_name
