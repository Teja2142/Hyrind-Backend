from django.db import models
from users.models import Profile
import uuid
import re


class Recruiter(models.Model):
    """Existing Recruiter model for basic recruiter info"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=False)  # Inactive by default until admin approves
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Assignment(models.Model):
    """Assignment of candidate profiles to recruiters"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name} assigned to {self.recruiter.name if self.recruiter else 'None'}"


class RecruiterRegistration(models.Model):
    """
    Comprehensive recruiter onboarding form with personal, address, and document details.
    Documents are stored in MinIO S3-compatible storage.
    """
    # ===== Gender Choices =====
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    # ===== Marital Status Choices =====
    MARITAL_STATUS_CHOICES = [
        ("single", "Single"),
        ("married", "Married"),
        ("divorced", "Divorced"),
        ("widowed", "Widowed"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    # ===== Blood Group Choices =====
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("O+", "O+"), ("O-", "O-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("unknown", "Unknown / Not provided"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ===== Basic Details =====
    full_name = models.CharField(max_length=100, help_text="Full legal name")
    email = models.EmailField(unique=True, help_text="Email address for communication")
    
    # ===== Contact Details =====
    phone_number = models.CharField(
        max_length=20,
        help_text="Primary phone number (10-12 digits)"
    )
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="WhatsApp number (optional)"
    )
    date_of_joining = models.DateField(help_text="Employment start date")
    date_of_birth = models.DateField(help_text="Date of birth (DD/MM/YYYY)")
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        help_text="Gender"
    )

    # ===== Personal & Family Details =====
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        help_text="Marital status"
    )
    father_name = models.CharField(
        max_length=100,
        help_text="Father's full name"
    )
    mother_name = models.CharField(
        max_length=100,
        help_text="Mother's full name"
    )
    spouse_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Spouse's name (if married)"
    )
    blood_group = models.CharField(
        max_length=20,
        choices=BLOOD_GROUP_CHOICES,
        help_text="Blood group"
    )
    emergency_contact_number = models.CharField(
        max_length=20,
        help_text="Emergency contact number"
    )

    # ===== Address Details =====
    permanent_address = models.TextField(help_text="Full permanent address")
    correspondence_address = models.TextField(
        blank=True,
        null=True,
        help_text="Mailing address (leave blank if same as permanent)"
    )
    same_as_permanent_address = models.BooleanField(
        default=True,
        help_text="Is correspondence address same as permanent?"
    )

    # ===== ID Proofs (MinIO Storage) =====
    aadhaar_number = models.CharField(
        max_length=14,
        unique=True,
        help_text="Aadhaar number (12 digits)"
    )
    aadhaar_card_file = models.FileField(
        upload_to="recruiters/aadhaar/",
        blank=True,
        null=True,
        help_text="Aadhaar card scan (PDF, JPG, PNG - optional)"
    )

    pan_number = models.CharField(
        max_length=10,
        unique=True,
        help_text="PAN number (10 alphanumeric)"
    )
    pan_card_file = models.FileField(
        upload_to="recruiters/pan/",
        blank=True,
        null=True,
        help_text="PAN card scan (PDF, JPG, PNG - optional)"
    )

    passport_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Passport number (optional)"
    )
    passport_copy_file = models.FileField(
        upload_to="recruiters/passport/",
        blank=True,
        null=True,
        help_text="Passport copy (PDF, JPG, PNG - optional)"
    )

    address_proof_file = models.FileField(
        upload_to="recruiters/address_proof/",
        blank=True,
        null=True,
        help_text="Address proof document (PDF, JPG, PNG - optional)"
    )

    # ===== Education Details =====
    highest_education = models.CharField(
        max_length=100,
        help_text="Highest qualification (e.g., Bachelor of Science)"
    )
    year_of_graduation = models.PositiveIntegerField(
        help_text="Year of graduation (YYYY)"
    )
    course = models.CharField(
        max_length=100,
        help_text="Course/Major name"
    )
    degree_certificate_file = models.FileField(
        upload_to="recruiters/degree_certificates/",
        blank=True,
        null=True,
        help_text="Degree certificate (PDF, JPG, PNG - optional)"
    )

    # ===== Bank Details =====
    bank_name = models.CharField(max_length=100, help_text="Bank name")
    account_holder_name = models.CharField(
        max_length=100,
        help_text="Account holder name (as per bank records)"
    )
    bank_account_number = models.CharField(
        max_length=50,
        help_text="Bank account number"
    )
    ifsc_code = models.CharField(
        max_length=20,
        help_text="IFSC code (11 characters)"
    )
    branch_name = models.CharField(max_length=100, help_text="Bank branch name")

    # ===== Metadata =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Has admin verified this registration?"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['aadhaar_number']),
            models.Index(fields=['pan_number']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def clean(self):
        """Validate model fields"""
        from django.core.exceptions import ValidationError
        import re

        errors = {}

        # Validate phone numbers (10-12 digits)
        phone_pattern = re.compile(r'^\d{10,12}$')
        digits_only = re.sub(r'\D', '', self.phone_number)
        if not phone_pattern.match(digits_only):
            errors['phone_number'] = 'Phone number must contain 10-12 digits.'

        if self.whatsapp_number:
            digits_only = re.sub(r'\D', '', self.whatsapp_number)
            if not phone_pattern.match(digits_only):
                errors['whatsapp_number'] = 'WhatsApp number must contain 10-12 digits.'

        # Validate Aadhaar (12 digits)
        aadhaar_val = (self.aadhaar_number or '').strip()
        if aadhaar_val and not re.match(r'^\d{12}$', aadhaar_val):
            errors['aadhaar_number'] = 'Aadhaar number must be exactly 12 digits.'

        # Validate PAN (10 alphanumeric: 5 letters, 4 digits, 1 letter)
        pan_val = (self.pan_number or '').strip().upper()
        if pan_val and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_val):
            errors['pan_number'] = 'PAN number format invalid. Expected: AAAAA9999A'

        # Validate IFSC (11 characters)
        ifsc_val = (self.ifsc_code or '').strip().upper()
        if ifsc_val and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_val):
            errors['ifsc_code'] = 'IFSC code format invalid. Expected: AAAA0AAAAAA'

        # Validate dates
        from datetime import datetime
        if self.date_of_birth and self.date_of_joining:
            if self.date_of_birth >= self.date_of_joining:
                errors['date_of_birth'] = 'Date of birth must be before joining date.'

        # Validate year of graduation
        current_year = datetime.now().year
        if self.year_of_graduation is not None:
            if self.year_of_graduation < 1960 or self.year_of_graduation > current_year:
                errors['year_of_graduation'] = f'Year of graduation must be between 1960 and {current_year}.'

        # Correspondence address logic
        if not self.same_as_permanent_address and not self.correspondence_address:
            errors['correspondence_address'] = 'Correspondence address required if different from permanent.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Normalize data before saving"""
        # Normalize phone numbers
        self.phone_number = re.sub(r'\D', '', self.phone_number)
        if self.whatsapp_number:
            self.whatsapp_number = re.sub(r'\D', '', self.whatsapp_number)

        # Normalize ID numbers
        if self.aadhaar_number is not None:
            self.aadhaar_number = (self.aadhaar_number or '').strip().upper()
        if self.pan_number is not None:
            self.pan_number = (self.pan_number or '').strip().upper()
        if self.ifsc_code is not None:
            self.ifsc_code = (self.ifsc_code or '').strip().upper()

        # Set correspondence address if same as permanent
        if self.same_as_permanent_address:
            self.correspondence_address = self.permanent_address

        self.full_clean()
        super().save(*args, **kwargs)