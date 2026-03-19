import uuid
from django.db import models
from django.conf import settings


# ---------------------------------------------------------------------------
# Master Status Pipeline  (v4 spec Section 4)
# ---------------------------------------------------------------------------

class Candidate(models.Model):
    STATUS_CHOICES = [
        ('pending_approval',          'Pending Approval'),
        ('approved',                  'Approved'),
        ('intake_pending',            'Intake Pending'),
        ('intake_submitted',          'Intake Submitted'),
        ('roles_published',           'Roles Published'),
        ('roles_candidate_responded', 'Roles Candidate Responded'),
        ('payment_pending',           'Payment Pending'),
        ('payment_completed',         'Payment Completed'),
        ('credentials_submitted',     'Credentials Submitted'),
        ('active_marketing',          'Active Marketing'),
        ('paused',                    'Paused'),
        ('on_hold',                   'On Hold'),
        ('past_due',                  'Past Due'),
        ('cancelled',                 'Cancelled'),
        ('placed_closed',             'Placed Closed'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate'
    )
    status          = models.CharField(max_length=40, choices=STATUS_CHOICES, default='pending_approval')
    placement_ready = models.BooleanField(default=False)
    notes           = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates'

    def __str__(self):
        return f'Candidate({self.user.email}) — {self.status}'


# ---------------------------------------------------------------------------
# Client Intake  (v4 spec Section 5.3, Sections A–F)
# ---------------------------------------------------------------------------

class ClientIntake(models.Model):
    DEGREE_CHOICES = [
        ("Bachelor's", "Bachelor's"), ("Master's", "Master's"), ('PhD', 'PhD'),
        ('Associate', 'Associate'), ('Other', 'Other'),
    ]
    VISA_TYPE_CHOICES = [
        ('H1B', 'H1B'), ('OPT', 'OPT'), ('CPT', 'CPT'),
        ('Green Card', 'Green Card'), ('US Citizen', 'US Citizen'),
        ('EAD', 'EAD'), ('TN', 'TN'), ('Other', 'Other'),
    ]
    WORK_AUTH_CHOICES = [
        ('Authorized', 'Authorized'),
        ('Requires Sponsorship', 'Requires Sponsorship'),
        ('Pending', 'Pending'),
    ]
    REMOTE_PREF_CHOICES = [
        ('Remote', 'Remote'), ('Hybrid', 'Hybrid'), ('On-site', 'On-site'), ('Any', 'Any'),
    ]
    EMP_TYPE_CHOICES = [
        ('Full-time', 'Full-time'), ('Part-time', 'Part-time'),
        ('Contract', 'Contract'), ('C2C', 'C2C'),
    ]
    JOB_SEARCH_CHOICES = [
        ('Active', 'Active'), ('Passive', 'Passive'), ('Not looking', 'Not looking'),
    ]

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='intake')

    # Section A — Personal Details
    first_name          = models.CharField(max_length=60, blank=True, null=True)
    last_name           = models.CharField(max_length=60, blank=True, null=True)
    date_of_birth       = models.DateField(blank=True, null=True)
    phone_number        = models.CharField(max_length=30, blank=True, null=True)
    alternate_phone     = models.CharField(max_length=30, blank=True, null=True)
    current_address     = models.CharField(max_length=200, blank=True, null=True)
    city                = models.CharField(max_length=80, blank=True, null=True)
    state               = models.CharField(max_length=80, blank=True, null=True)
    country             = models.CharField(max_length=80, blank=True, null=True)
    zip_code            = models.CharField(max_length=20, blank=True, null=True)

    # Section B — Education
    degree_level                = models.CharField(max_length=30, choices=DEGREE_CHOICES, blank=True, null=True)
    university_name             = models.CharField(max_length=120, blank=True, null=True)
    major                       = models.CharField(max_length=120, blank=True, null=True)
    graduation_date             = models.DateField(blank=True, null=True)
    additional_certifications   = models.TextField(max_length=500, blank=True, null=True)
    academic_projects           = models.TextField(max_length=1000, blank=True, null=True)

    # Section C — Work Authorization
    visa_type                       = models.CharField(max_length=30, choices=VISA_TYPE_CHOICES, blank=True, null=True)
    visa_expiry_date                = models.DateField(blank=True, null=True)
    work_authorization_status       = models.CharField(max_length=30, choices=WORK_AUTH_CHOICES, blank=True, null=True)
    sponsorship_required            = models.BooleanField(null=True)
    country_of_work_authorization   = models.CharField(max_length=100, blank=True, null=True)

    # Section D — Job Preferences
    target_roles            = models.JSONField(default=list)
    preferred_locations     = models.JSONField(default=list)
    remote_preference       = models.CharField(max_length=20, choices=REMOTE_PREF_CHOICES, blank=True, null=True)
    salary_expectation      = models.IntegerField(blank=True, null=True)
    relocation_preference   = models.BooleanField(null=True)
    industry_preference     = models.JSONField(default=list)
    shift_preference        = models.CharField(max_length=20, blank=True, null=True)

    # Section E — Professional Background
    years_of_experience     = models.IntegerField(blank=True, null=True)
    recent_employer         = models.CharField(max_length=120, blank=True, null=True)
    current_job_title       = models.CharField(max_length=120, blank=True, null=True)
    technologies_or_skills  = models.TextField(max_length=2000, blank=True, null=True)
    linkedin_url            = models.URLField(blank=True, null=True)
    github_url              = models.URLField(blank=True, null=True)
    portfolio_url           = models.URLField(blank=True, null=True)
    resume_upload_url       = models.URLField(blank=True, null=True)

    # Section F — Marketing Inputs
    ready_to_start_date         = models.DateField(blank=True, null=True)
    preferred_employment_type   = models.CharField(max_length=20, choices=EMP_TYPE_CHOICES, blank=True, null=True)
    job_search_priority         = models.CharField(max_length=20, choices=JOB_SEARCH_CHOICES, blank=True, null=True)
    additional_notes            = models.TextField(max_length=1000, blank=True, null=True)

    # Lock / reopen tracking
    is_locked       = models.BooleanField(default=False)
    submitted_at    = models.DateTimeField(blank=True, null=True)
    reopened_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reopened_intakes',
    )
    reopened_at     = models.DateTimeField(blank=True, null=True)
    reopen_reason   = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'client_intake'

    def __str__(self):
        return f'Intake({self.candidate.user.email})'


# ---------------------------------------------------------------------------
# Role Suggestions  (v4 spec Section 5.4)
# ---------------------------------------------------------------------------

class RoleSuggestion(models.Model):
    RESPONSE_CHOICES = [
        ('pending',          'Pending'),
        ('accepted',         'Accepted'),
        ('declined',         'Declined'),
        ('change_requested', 'Change Requested'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate   = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='role_suggestions')
    role_title  = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    admin_note  = models.TextField(blank=True, null=True)
    suggested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='suggestions_made',
    )
    is_published    = models.BooleanField(default=False)
    published_at    = models.DateTimeField(blank=True, null=True)

    # Candidate response
    candidate_response  = models.CharField(max_length=20, choices=RESPONSE_CHOICES, default='pending')
    change_request_note = models.TextField(blank=True, null=True)
    responded_at        = models.DateTimeField(blank=True, null=True)

    # Optional custom role proposed by candidate
    custom_role_title   = models.CharField(max_length=120, blank=True, null=True)
    custom_reason       = models.TextField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_suggestions'

    def __str__(self):
        return f'{self.role_title} — {self.candidate.user.email}'


# ---------------------------------------------------------------------------
# Credential Versions  (v4 spec Section 5.5)
# ---------------------------------------------------------------------------

class CredentialVersion(models.Model):
    SOURCE_ROLE_CHOICES = [
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter'),
        ('admin',     'Admin'),
    ]
    SENSITIVE_FIELDS = {'visa_details', 'references_if_needed'}

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='credentials')

    # Editable credential fields
    full_name_as_resume     = models.CharField(max_length=255, blank=True, null=True)
    primary_resume_url      = models.URLField(blank=True, null=True)
    alternate_resume_urls   = models.JSONField(default=list)
    linkedin_url            = models.URLField(blank=True, null=True)
    github_url              = models.URLField(blank=True, null=True)
    portfolio_url           = models.URLField(blank=True, null=True)
    work_history_summary    = models.TextField(blank=True, null=True)
    skills_summary          = models.TextField(blank=True, null=True)
    tools_and_technologies  = models.TextField(blank=True, null=True)
    certifications          = models.TextField(blank=True, null=True)
    visa_details            = models.TextField(blank=True, null=True)   # sensitive — redacted in diffs
    relocation_preference   = models.CharField(max_length=20, blank=True, null=True)
    references_if_needed    = models.TextField(blank=True, null=True)   # sensitive
    recruiter_notes         = models.TextField(blank=True, null=True)
    formatting_notes        = models.TextField(blank=True, null=True)

    # Version metadata
    version_number  = models.IntegerField(default=1)
    updated_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='credential_edits',
    )
    source_role     = models.CharField(max_length=20, choices=SOURCE_ROLE_CHOICES, blank=True, null=True)
    changed_fields  = models.JSONField(default=list)    # list of field names changed
    diff_summary    = models.JSONField(default=dict)    # {field: {before, after}} — sensitive fields omitted
    full_snapshot   = models.JSONField(default=dict)    # full state at save time

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'credential_versions'
        ordering = ['-version_number']

    def __str__(self):
        return f'CredentialV{self.version_number}({self.candidate.user.email})'


# ---------------------------------------------------------------------------
# Referral  (v4 spec Section 5.10)
# ---------------------------------------------------------------------------

class Referral(models.Model):
    STATUS_CHOICES = [
        ('sent',       'Sent'),
        ('contacted',  'Contacted'),
        ('onboarded',  'Onboarded'),
        ('closed',     'Closed'),
        ('rejected',   'Rejected'),
    ]

    id                      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referrer                = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='referrals')
    friend_name             = models.CharField(max_length=120)
    friend_email            = models.EmailField()
    friend_phone            = models.CharField(max_length=30, blank=True, null=True)
    referred_for            = models.CharField(max_length=100, blank=True, null=True)
    note_from_candidate     = models.TextField(max_length=500, blank=True, null=True)
    status                  = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    admin_notes             = models.TextField(blank=True, null=True)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'referrals'

    def __str__(self):
        return f'Referral({self.friend_email}) by {self.referrer.user.email}'


# ---------------------------------------------------------------------------
# Interview Log  (v4 spec Section 5.9)
# ---------------------------------------------------------------------------

class InterviewLog(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ('screening_call',   'Screening Call'),
        ('technical',        'Technical Interview'),
        ('hr',               'HR Interview'),
        ('client_round',     'Client Round'),
        ('final_round',      'Final Round'),
        ('mock',             'Mock Interview'),
        ('support_call',     'Support Call'),
    ]
    INTERVIEW_MODE_CHOICES = [
        ('video',     'Video'),
        ('phone',     'Phone'),
        ('in_person', 'In Person'),
    ]
    OUTCOME_CHOICES = [
        ('scheduled',       'Scheduled'),
        ('completed',       'Completed'),
        ('selected',        'Selected / Passed'),
        ('rejected',        'Rejected'),
        ('follow_up_needed','Follow-up Needed'),
        ('rescheduled',     'Rescheduled'),
        ('no_show',         'No Show'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate       = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interview_logs')
    interview_type  = models.CharField(max_length=30, choices=INTERVIEW_TYPE_CHOICES)
    stage_round     = models.CharField(max_length=100)
    company_name    = models.CharField(max_length=255)
    role_title      = models.CharField(max_length=255)
    interview_date  = models.DateField()
    interview_time  = models.TimeField(blank=True, null=True)
    time_zone       = models.CharField(max_length=60, blank=True, null=True)
    interviewer_name = models.CharField(max_length=255, blank=True, null=True)
    interview_mode  = models.CharField(max_length=20, choices=INTERVIEW_MODE_CHOICES, blank=True, null=True)
    meeting_link    = models.URLField(blank=True, null=True)
    outcome         = models.CharField(max_length=30, choices=OUTCOME_CHOICES, default='scheduled')
    difficult_questions = models.TextField(blank=True, null=True)
    feedback_notes      = models.TextField(blank=True, null=True)
    support_needed      = models.TextField(blank=True, null=True)
    next_round_date     = models.DateField(blank=True, null=True)
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='interviews_created',
    )
    updated_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='interviews_updated',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interview_logs'
        ordering = ['-interview_date', '-created_at']

    def __str__(self):
        return f'{self.company_name} — {self.get_interview_type_display()} — {self.candidate.user.email}'


# ---------------------------------------------------------------------------
# Placement Closure  (v4 spec Section 8.3)
# ---------------------------------------------------------------------------

class PlacementClosure(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD'), ('INR', 'INR'), ('GBP', 'GBP'), ('EUR', 'EUR'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate       = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='placement')
    employer_name   = models.CharField(max_length=255)
    role_placed_into = models.CharField(max_length=255)
    start_date      = models.DateField()
    salary          = models.DecimalField(max_digits=12, decimal_places=2)
    currency        = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='USD')
    offer_letter_url = models.URLField(blank=True, null=True)
    hr_contact_email = models.EmailField()
    placement_notes  = models.TextField(blank=True, null=True)
    closed_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='placements_closed',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'placement_closures'

    def __str__(self):
        return f'Placement({self.candidate.user.email}) — {self.employer_name}'
