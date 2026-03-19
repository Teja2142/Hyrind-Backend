import uuid
from django.db import models
from django.conf import settings
from candidates.models import Candidate


class RecruiterProfile(models.Model):
    """Extended profile for recruiters  per v4 spec Section 7.4."""
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter_profile'
    )
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name  = models.CharField(max_length=60, blank=True, null=True)
    phone      = models.CharField(max_length=30, blank=True, null=True)
    city       = models.CharField(max_length=100, blank=True, null=True)
    state      = models.CharField(max_length=100, blank=True, null=True)
    country    = models.CharField(max_length=100, blank=True, null=True)
    linkedin_url  = models.URLField(blank=True, null=True)
    documents_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recruiter_profiles'

    def __str__(self):
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return name or self.user.email


class RecruiterBankDetail(models.Model):
    """Isolated sensitive bank info  only recruiter (own) + admin can access."""
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruiter = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bank_details',
        limit_choices_to={'role': 'recruiter'},
    )
    bank_name            = models.CharField(max_length=255)
    account_holder_name  = models.CharField(max_length=255)
    account_number       = models.CharField(max_length=255)  # store encrypted in prod
    routing_number       = models.CharField(max_length=50, blank=True, null=True)
    account_type         = models.CharField(max_length=30, blank=True, null=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recruiter_bank_details'

    @property
    def masked_account(self):
        return f"****{self.account_number[-4:]}" if self.account_number else ''

    def __str__(self):
        return f"BankDetails({self.recruiter.email})"


class RecruiterAssignment(models.Model):
    """Max 4 active recruiter assignments per candidate  enforced in save()."""
    MAX_PER_CANDIDATE = 4

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate   = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='assignments')
    recruiter   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recruiter_assignments'
    )
    role_type   = models.CharField(max_length=50, blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )
    assigned_at   = models.DateTimeField(auto_now_add=True)
    unassigned_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'recruiter_assignments'
        unique_together = [('candidate', 'recruiter')]

    def save(self, *args, **kwargs):
        if self.is_active and not self.pk:
            active_count = RecruiterAssignment.objects.filter(
                candidate=self.candidate, is_active=True
            ).count()
            if active_count >= self.MAX_PER_CANDIDATE:
                raise ValueError(f"Max {self.MAX_PER_CANDIDATE} recruiters per candidate.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.recruiter.email} -> {self.candidate.user.email}"


class DailySubmissionLog(models.Model):
    """Daily recruiter submission log header  one per recruiter per candidate per day."""
    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate          = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='daily_logs')
    recruiter          = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submission_logs'
    )
    log_date           = models.DateField()
    applications_count = models.IntegerField(default=0)
    notes              = models.TextField(blank=True, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_submission_logs'
        unique_together = [('candidate', 'recruiter', 'log_date')]

    def __str__(self):
        return f"Log({self.recruiter.email}, {self.candidate.user.email}, {self.log_date})"


class JobLinkEntry(models.Model):
    """Individual job application entry within a daily log."""
    APPLICATION_STATUS_CHOICES = [
        ('applied',    'Applied'),
        ('screening',  'Screening'),
        ('interview',  'Interview'),
        ('rejected',   'Rejected'),
        ('offer',      'Offer'),
    ]
    FETCH_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed',  'Failed'),
    ]

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_log = models.ForeignKey(DailySubmissionLog, on_delete=models.CASCADE, related_name='job_entries')
    candidate      = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='job_postings')
    company_name   = models.CharField(max_length=120)
    role_title     = models.CharField(max_length=120)
    job_url        = models.URLField()
    job_description = models.TextField(blank=True, null=True)
    fetch_status   = models.CharField(max_length=10, choices=FETCH_STATUS_CHOICES, default='pending')
    resume_used    = models.CharField(max_length=255, blank=True, null=True)
    application_status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='applied')
    notes          = models.TextField(blank=True, null=True)
    submitted_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='job_entries_submitted'
    )
    submitted_at   = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_link_entries'

    def __str__(self):
        return f"{self.company_name}  {self.role_title} ({self.application_status})"
