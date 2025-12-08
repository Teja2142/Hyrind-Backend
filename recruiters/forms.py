"""
Industry-standard recruiter registration system with two-phase onboarding:
1. Registration Phase: Minimal fields (auto-generated employee ID)
2. Profile Completion Phase: Comprehensive fields after login

Forms:
- RecruiterMinimalRegistrationForm: Quick registration (email, password, name, phone, department, specialization)
- RecruiterProfileUpdateForm: Complete profile (70+ fields from RecruiterRegistration model)
- RecruiterBasicUpdateForm: Basic info updates
"""
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re
import random

from .models import RecruiterRegistration, Recruiter
from users.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_employee_id():
    """Generate unique employee ID with format: H + 5 random digits (e.g., H12345)"""
    while True:
        # Generate H + 5 random digits
        employee_id = f"H{random.randint(10000, 99999)}"
        # Check if it's unique
        if not Recruiter.objects.filter(employee_id=employee_id).exists():
            return employee_id


class RecruiterMinimalRegistrationForm(forms.Form):
    """
    Industry-standard minimal registration form for new recruiters.
    Employee ID is auto-generated. Additional details collected after login.
    """
    # Account credentials
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Email (e.g., john.doe@hyrind.com)'
        }),
        help_text='Your company email address'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password (min 8 characters)'
        }),
        help_text='Minimum 8 characters with letters and numbers'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )
    
    # Personal information
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone (10-12 digits)',
            'inputmode': 'numeric'
        }),
        help_text='10-12 digits only'
    )
    
    # Employment information
    department = forms.ChoiceField(
        choices=Recruiter.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Your assigned department'
    )
    specialization = forms.ChoiceField(
        choices=Recruiter.SPECIALIZATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Your primary area of expertise'
    )
    date_of_joining = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Your employment start date'
    )
    
    # Optional fields
    linkedin_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/yourprofile'
        }),
        help_text='Your LinkedIn profile (optional)'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        if Recruiter.objects.filter(email=email).exists():
            raise ValidationError('A recruiter with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits):
            raise ValidationError('Phone must contain 10-12 digits only')
        return digits

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', 'Passwords do not match.')
        if pw:
            try:
                validate_password(pw)
            except ValidationError as e:
                self.add_error('password', e.messages)
        return cleaned

    def save(self):
        """Create User, Profile, and Recruiter with auto-generated employee ID"""
        data = self.cleaned_data
        
        # Generate unique employee ID
        employee_id = generate_employee_id()
        
        # Create User
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        # New recruiter accounts require admin approval; keep underlying User inactive
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        # Create Profile
        profile = Profile.objects.create(
            user=user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            linkedin_url=data.get('linkedin_url', '')
        )
        # reflect inactive state on profile
        profile.active = False
        profile.save(update_fields=['active'])
        
        # Create Recruiter with auto-generated employee ID
        recruiter_name = f"{data['first_name']} {data['last_name']}"
        recruiter = Recruiter.objects.create(
            user=profile,
            employee_id=employee_id,  # AUTO-GENERATED
            name=recruiter_name,
            email=data['email'],
            phone=data['phone'],
            department=data['department'],
            specialization=data['specialization'],
            date_of_joining=data['date_of_joining'],
            max_clients=3,  # Default
            status='pending',  # Requires admin approval
            active=False,
            company_name='Hyrind Recruitment Services'
        )
        
        return recruiter


class RecruiterProfileUpdateForm(forms.ModelForm):
    """
    Comprehensive profile update form using RecruiterRegistration model.
    Collects all personal, address, ID proof, education, and bank details.
    """
    confirm_bank_account_number = forms.CharField(
        max_length=50,
        required=False,
        label='Confirm Bank Account Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your bank account number',
            'inputmode': 'numeric'
        })
    )
    
    # Link to recruiter
    recruiter_id = forms.UUIDField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RecruiterRegistration
        exclude = ['created_at', 'updated_at', 'is_verified']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full legal name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-12 digits', 'inputmode': 'numeric'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp (optional)', 'inputmode': 'numeric'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': 'readonly'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric'}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'correspondence_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'same_as_permanent_address': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12 digits', 'inputmode': 'numeric'}),
            'aadhaar_card_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AAAAA9999A'}),
            'pan_card_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_copy_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'address_proof_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'highest_education': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_graduation': forms.NumberInput(attrs={'class': 'form-control', 'min': '1960', 'max': '2099'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'degree_certificate_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AAAA0AAAAAA'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.recruiter = kwargs.pop('recruiter', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill from recruiter if available
        if self.recruiter and not self.instance.pk:
            self.initial['full_name'] = self.recruiter.name
            self.initial['email'] = self.recruiter.email
            self.initial['phone_number'] = self.recruiter.phone
            self.initial['date_of_joining'] = self.recruiter.date_of_joining

    def clean(self):
        cleaned = super().clean()
        
        # Bank account confirmation
        account = cleaned.get('bank_account_number')
        confirm = cleaned.get('confirm_bank_account_number')
        if account and confirm and account != confirm:
            self.add_error('confirm_bank_account_number', 'Bank account numbers do not match.')
        
        # Address validation
        if not cleaned.get('same_as_permanent_address') and not cleaned.get('correspondence_address'):
            self.add_error('correspondence_address', 'Correspondence address required if different from permanent.')
        
        # Marital status validation
        if cleaned.get('marital_status') == 'married' and not cleaned.get('spouse_name'):
            self.add_error('spouse_name', 'Spouse name is required for married status.')
        
        return cleaned


class RecruiterBasicUpdateForm(forms.ModelForm):
    """Form for updating basic recruiter information"""
    class Meta:
        model = Recruiter
        fields = ['name', 'phone', 'department', 'specialization', 'max_clients', 'company_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'max_clients': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits):
            raise ValidationError('Phone must contain 10-12 digits only')
        return digits
