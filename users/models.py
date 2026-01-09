from django.db import models
import uuid
from django.contrib.auth.models import User


class Profile(models.Model):
    # Registration Status Choices
    STATUS_CHOICES = [
        ('open', 'Open - Awaiting Admin Review'),
        ('approved', 'Approved - Ready for Payment'),
        ('ready_to_assign', 'Ready to Assign - Payment Completed'),
        ('assigned', 'Assigned - Recruiter Assigned'),
        ('waiting_payment', 'Waiting for Payment - Payment Expired'),
        ('closed', 'Closed - Candidate Placed'),
        ('rejected', 'Rejected - Admin Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    active = models.BooleanField(default=False, help_text='Whether this profile is active and allowed to log in')
    
    # Registration Status
    registration_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        help_text='Current status in the registration and assignment workflow'
    )
    status_updated_at = models.DateTimeField(auto_now=True, help_text='Last status update timestamp')
    status_notes = models.TextField(blank=True, help_text='Admin notes about status changes')
    
    # Existing fields
    university = models.CharField(max_length=100, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    major = models.CharField(max_length=100, blank=True)
    visa_status = models.CharField(max_length=50, blank=True)
    graduation_date = models.DateField(null=True, blank=True)
    opt_end_date = models.DateField(null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    consent_to_terms = models.BooleanField(default=False)
    REFERRAL_CHOICES = [
        ("Google", "Google"),
        ("LinkedIn", "LinkedIn"),
        ("Friend", "Friend"),
        ("University", "University"),
        ("Other", "Other"),
    ]
    referral_source = models.CharField(max_length=20, choices=REFERRAL_CHOICES, null=True, blank=True)
    linkedin_url = models.URLField(max_length=255, null=True, blank=True)
    github_url = models.URLField(max_length=255, null=True, blank=True)
    additional_notes = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
            return f"{self.first_name} {self.last_name}".strip()
    
    def update_status(self, new_status, notes=''):
        """Update registration status with timestamp and notes, auto-manage active field"""
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")
        
        self.registration_status = new_status
        if notes:
            self.status_notes = notes
        
        # Auto-sync active field and User.is_active based on status
        # Active statuses: approved, ready_to_assign, assigned
        # Inactive statuses: open, rejected, closed, waiting_payment
        if new_status in ['approved', 'ready_to_assign', 'assigned']:
            self.active = True
            if hasattr(self, 'user') and self.user:
                self.user.is_active = True
                self.user.save(update_fields=['is_active'])
        else:
            self.active = False
            if hasattr(self, 'user') and self.user:
                self.user.is_active = False
                self.user.save(update_fields=['is_active'])
        
        self.save(update_fields=['registration_status', 'status_notes', 'status_updated_at', 'active'])


class InterestSubmission(models.Model):
    DEGREE_CHOICES = [
        ("Bachelor's", "Bachelor's"),
        ("Master's", "Master's"),
        ("PhD", "PhD"),
    ]

    VISA_CHOICES = [
        ("F1-OPT", "F1-OPT"),
        ("F1-CPT", "F1-CPT"),
        ("H1B", "H1B"),
        ("Green Card", "Green Card"),
        ("Citizen", "Citizen"),
        ("Other", "Other"),
    ]

    REFERRAL_CHOICES = [
        ("Google", "Google"),
        ("LinkedIn", "LinkedIn"),
        ("Friend", "Friend"),
        ("University", "University"),
        ("Other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    university = models.CharField(max_length=100)
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    major = models.CharField(max_length=100)
    visa_status = models.CharField(max_length=20, choices=VISA_CHOICES)
    graduation_date = models.DateField(null=True, blank=True)
    opt_end_date = models.DateField(null=True, blank=True)
    resume_file = models.FileField(upload_to='interest_resumes/', null=True, blank=True)
    referral_source = models.CharField(max_length=20, choices=REFERRAL_CHOICES, null=True, blank=True)
    consent_to_terms = models.BooleanField()
    linkedin_url = models.URLField(max_length=255, null=True, blank=True)
    github_url = models.URLField(max_length=255, null=True, blank=True)
    additional_notes = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return f"InterestSubmission({self.email})"


class Contact(models.Model):
    """Model for storing contact form submissions"""
    full_name = models.CharField(max_length=100, help_text="Full name of the person contacting")
    email = models.EmailField(help_text="Email address for response")
    phone = models.CharField(max_length=20, help_text="Contact phone number")
    message = models.TextField(max_length=2000, help_text="Message content")
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False, help_text="Has this contact been responded to?")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
    
    def __str__(self):
        return f"Contact from {self.full_name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d')}"
