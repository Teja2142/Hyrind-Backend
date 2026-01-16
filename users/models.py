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


class ClientIntakeSheet(models.Model):
    """
    Client Intake Sheet form based on Excel file
    Captures detailed information about skills, experience, education, and certifications
    """
    
    VISA_STATUS_CHOICES = [
        ('F1-OPT', 'F1-OPT'),
        ('H1B', 'H1B'),
        ('H4 EAD', 'H4 EAD'),
        ('Green Card', 'Green Card'),
        ('US Citizen', 'US Citizen'),
        ('Other', 'Other'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
    ]
    
    DEGREE_CHOICES = [
        ("Bachelor's", "Bachelor's"),
        ("Master's", "Master's"),
        ("PhD", "PhD"),
        ("Diploma", "Diploma"),
        ("Other", "Other"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='client_intake_sheet')
    
    # Personal Information
    first_name = models.CharField(max_length=100, help_text='First Name')
    last_name = models.CharField(max_length=100, help_text='Last Name')
    date_of_birth = models.DateField(help_text='Date of Birth (DD/MM/YYYY)')
    phone_number = models.CharField(max_length=20, help_text='Phone Number with country code')
    email = models.EmailField(help_text='Email Address')
    alternate_email = models.EmailField(blank=True, null=True, help_text='Alternate Email Address')
    marketing_contact_number = models.CharField(max_length=20, blank=True, null=True, help_text='Contact number for Marketing')
    marketing_email = models.EmailField(blank=True, null=True, help_text='Email for Marketing')
    current_address = models.TextField(help_text='Current Address')
    mailing_address = models.TextField(help_text='Mailing Address')
    
    # Visa and Entry Information
    visa_status = models.CharField(max_length=50, choices=VISA_STATUS_CHOICES, help_text='Current Visa Status')
    first_entry_us = models.DateField(help_text='First Entry into the U.S. (DD/MM/YYYY)')
    total_years_in_us = models.IntegerField(help_text='Total Years in the U.S.')
    
    # Skills
    skilled_in = models.TextField(help_text='Skilled In (e.g., Python, Java, C++, JavaScript, React, Node.js, etc.)')
    currently_learning = models.TextField(blank=True, null=True, help_text='Currently Learning / Recently Learned')
    experienced_with = models.TextField(help_text='Experienced With (e.g., AWS, SQL, Docker, Git, Selenium, etc.)')
    learning_tools = models.TextField(blank=True, null=True, help_text='Learning Now / Self-Taught Tools')
    non_technical_skills = models.TextField(blank=True, null=True, help_text='Other Non Technical Skills / Courses (e.g., Business Analysis, Digital Marketing, etc.)')
    
    # Work Experience - Job 1
    job_1_title = models.CharField(max_length=100, blank=True, null=True, help_text='Job Title')
    job_1_company = models.CharField(max_length=100, blank=True, null=True, help_text='Company Name')
    job_1_address = models.TextField(blank=True, null=True, help_text='Company Address')
    job_1_start_date = models.DateField(blank=True, null=True, help_text='Start Date (DD/MM/YYYY)')
    job_1_end_date = models.DateField(blank=True, null=True, help_text='End Date (DD/MM/YYYY)')
    job_1_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True, null=True, help_text='Job Type')
    job_1_responsibilities = models.TextField(blank=True, null=True, help_text='Key Responsibilities / Projects')
    
    # Work Experience - Job 2
    job_2_title = models.CharField(max_length=100, blank=True, null=True, help_text='Job Title')
    job_2_company = models.CharField(max_length=100, blank=True, null=True, help_text='Company Name')
    job_2_address = models.TextField(blank=True, null=True, help_text='Company Address')
    job_2_start_date = models.DateField(blank=True, null=True, help_text='Start Date (DD/MM/YYYY)')
    job_2_end_date = models.DateField(blank=True, null=True, help_text='End Date (DD/MM/YYYY)')
    job_2_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True, null=True, help_text='Job Type')
    job_2_responsibilities = models.TextField(blank=True, null=True, help_text='Key Responsibilities / Projects')
    
    # Work Experience - Job 3
    job_3_title = models.CharField(max_length=100, blank=True, null=True, help_text='Job Title')
    job_3_company = models.CharField(max_length=100, blank=True, null=True, help_text='Company Name')
    job_3_address = models.TextField(blank=True, null=True, help_text='Company Address')
    job_3_start_date = models.DateField(blank=True, null=True, help_text='Start Date (DD/MM/YYYY)')
    job_3_end_date = models.DateField(blank=True, null=True, help_text='End Date (DD/MM/YYYY)')
    job_3_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True, null=True, help_text='Job Type')
    job_3_responsibilities = models.TextField(blank=True, null=True, help_text='Key Responsibilities / Projects')
    
    # Education - Highest Degree
    highest_degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, blank=True, null=True, help_text='Highest Degree')
    highest_field_of_study = models.CharField(max_length=100, blank=True, null=True, help_text='Field of Study')
    highest_university = models.CharField(max_length=100, blank=True, null=True, help_text='University/Institution Name')
    highest_country = models.CharField(max_length=100, blank=True, null=True, help_text='Country')
    highest_graduation_date = models.DateField(blank=True, null=True, help_text='Graduation Date')
    
    # Education - Bachelors Degree
    bachelors_degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, blank=True, null=True, help_text="Bachelor's Degree")
    bachelors_field_of_study = models.CharField(max_length=100, blank=True, null=True, help_text='Field of Study')
    bachelors_university = models.CharField(max_length=100, blank=True, null=True, help_text='University/Institution Name')
    bachelors_country = models.CharField(max_length=100, blank=True, null=True, help_text='Country')
    bachelors_graduation_date = models.DateField(blank=True, null=True, help_text='Graduation Date')
    
    # Certifications
    certification_name = models.CharField(max_length=100, blank=True, null=True, help_text='Certification Name')
    issuing_organization = models.CharField(max_length=100, blank=True, null=True, help_text='Issuing Organization')
    issued_date = models.DateField(blank=True, null=True, help_text='Issued Date')
    
    # Documents
    passport_file = models.FileField(upload_to='users/documents/passports/', blank=True, null=True, help_text='Passport')
    government_id_file = models.FileField(upload_to='users/documents/ids/', blank=True, null=True, help_text='Government ID (DL / State ID)')
    visa_file = models.FileField(upload_to='users/documents/visas/', blank=True, null=True, help_text='Visa')
    work_authorization_file = models.FileField(upload_to='users/documents/work_authorization/', blank=True, null=True, help_text='Work Authorization Proof (OPT Card, EAD, etc.)')
    resume_file = models.FileField(upload_to='users/documents/resumes/', blank=True, null=True, help_text='Original Resume')
    
    # Job Preferences
    desired_job_role = models.CharField(max_length=100, blank=True, null=True, help_text='Desired Job Role / Roles')
    desired_years_experience = models.CharField(max_length=100, blank=True, null=True, help_text='Desired years of experience')
    
    # Timestamps
    submission_timestamp = models.DateTimeField(blank=True, null=True, help_text='Form submission timestamp')
    is_editable = models.BooleanField(default=True, help_text='Whether form can be edited after submission')
    form_submitted_date = models.DateTimeField(blank=True, null=True, help_text='Date when form was first submitted')
    
    class Meta:
        ordering = ['-submission_timestamp']
        verbose_name = 'Client Intake Sheet'
        verbose_name_plural = 'Client Intake Sheets'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['submission_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - Client Intake ({self.submission_timestamp.strftime('%Y-%m-%d') if self.submission_timestamp else 'Draft'})"


class CredentialSheet(models.Model):
    """
    Credential Sheet form based on Excel file
    Stores job platform login information and job search preferences
    """
    
    OPT_STATUS_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='credential_sheet')
    
    # Personal Information
    full_name = models.CharField(max_length=100, help_text='Full Name')
    personal_email = models.EmailField(help_text='Personal Email Address')
    phone_number = models.CharField(max_length=20, help_text='Phone Number')
    location = models.CharField(max_length=100, help_text='Location (City, State)')
    
    # Job Search Status
    bachelor_graduation_date = models.DateField(help_text='Bachelors Graduation Date')
    first_entry_us = models.DateField(help_text='First Entry into the U.S. (DD/MM/YYYY)')
    masters_graduation_date = models.DateField(blank=True, null=True, help_text='Masters Graduation Date')
    opt_start_date = models.DateField(blank=True, null=True, help_text='OPT Start date')
    opt_offer_letter_submitted = models.CharField(max_length=10, choices=OPT_STATUS_CHOICES, blank=True, null=True, help_text='OPT offer letter submitted')
    opt_offer_letter_file = models.FileField(upload_to='users/credentials/opt_letters/', blank=True, null=True, help_text='Upload Offer letter')
    
    # Job Preferences
    preferred_job_roles = models.TextField(help_text='Preferred Job Roles for marketing')
    preferred_locations = models.TextField(help_text='Preferred Location(s)')
    
    # LinkedIn Credentials
    linkedin_username = models.CharField(max_length=100, blank=True, null=True, help_text='LinkedIn Login ID')
    linkedin_password = models.CharField(max_length=255, blank=True, null=True, help_text='LinkedIn Password')
    
    # Indeed Credentials
    indeed_username = models.CharField(max_length=100, blank=True, null=True, help_text='Indeed Login ID')
    indeed_password = models.CharField(max_length=255, blank=True, null=True, help_text='Indeed Password')
    
    # Dice Credentials
    dice_username = models.CharField(max_length=100, blank=True, null=True, help_text='Dice Login ID')
    dice_password = models.CharField(max_length=255, blank=True, null=True, help_text='Dice Password')
    
    # Monster Credentials
    monster_username = models.CharField(max_length=100, blank=True, null=True, help_text='Monster Login ID')
    monster_password = models.CharField(max_length=255, blank=True, null=True, help_text='Monster Password')
    
    # ZipRecruiter Credentials
    ziprecruiter_username = models.CharField(max_length=100, blank=True, null=True, help_text='ZipRecruiter Login ID')
    ziprecruiter_password = models.CharField(max_length=255, blank=True, null=True, help_text='ZipRecruiter Password')
    
    # Glassdoor Credentials
    glassdoor_username = models.CharField(max_length=100, blank=True, null=True, help_text='Glassdoor Login ID')
    glassdoor_password = models.CharField(max_length=255, blank=True, null=True, help_text='Glassdoor Password')
    
    # BuildIn Credentials
    buildin_username = models.CharField(max_length=100, blank=True, null=True, help_text='BuildIn Login ID')
    buildin_password = models.CharField(max_length=255, blank=True, null=True, help_text='BuildIn Password')
    
    # Jobvite Credentials
    jobvite_username = models.CharField(max_length=100, blank=True, null=True, help_text='Jobvite Login ID')
    jobvite_password = models.CharField(max_length=255, blank=True, null=True, help_text='Jobvite Password')
    
    # CareerBuilder Credentials
    careerbuilder_username = models.CharField(max_length=100, blank=True, null=True, help_text='CareerBuilder Login ID')
    careerbuilder_password = models.CharField(max_length=255, blank=True, null=True, help_text='CareerBuilder Password')
    
    # GitHub Credentials
    github_username = models.CharField(max_length=100, blank=True, null=True, help_text='GitHub Login ID')
    github_password = models.CharField(max_length=255, blank=True, null=True, help_text='GitHub Password')
    
    # Other Platforms
    other_job_platform_accounts = models.TextField(blank=True, null=True, help_text='Mention all other Job Platform accounts you have (or N/A)')
    
    # Timestamps
    submission_timestamp = models.DateTimeField(blank=True, null=True, help_text='Form submission timestamp')
    is_editable = models.BooleanField(default=True, help_text='Whether form can be edited after submission')
    form_submitted_date = models.DateTimeField(blank=True, null=True, help_text='Date when form was first submitted')
    
    class Meta:
        ordering = ['-submission_timestamp']
        verbose_name = 'Credential Sheet'
        verbose_name_plural = 'Credential Sheets'
        indexes = [
            models.Index(fields=['personal_email']),
            models.Index(fields=['submission_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - Credentials ({self.submission_timestamp.strftime('%Y-%m-%d') if self.submission_timestamp else 'Draft'})"
