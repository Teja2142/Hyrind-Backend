"""
Clean, consolidated recruiter forms with modern widget attributes.
Provides:
- RecruiterRegistrationFormModel: full onboarding ModelForm
- RecruiterSimpleRegistrationForm: lightweight account creation
- RecruiterUpdateForm: recruiter profile updates

Widgets include Bootstrap classes, placeholders, inputmode/pattern where appropriate.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re

from .models import RecruiterRegistration, Recruiter
from users.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()


class RecruiterRegistrationFormModel(forms.ModelForm):
    confirm_bank_account_number = forms.CharField(
        max_length=50,
        required=True,
        label='Confirm Bank Account Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your bank account number',
            'inputmode': 'numeric'
        }),
        help_text='Confirm your bank account number'
    )

    class Meta:
        model = RecruiterRegistration
        fields = [
            'full_name', 'email',
            'phone_number', 'whatsapp_number', 'date_of_joining', 'date_of_birth', 'gender',
            'marital_status', 'father_name', 'mother_name', 'spouse_name', 'blood_group', 'emergency_contact_number',
            'permanent_address', 'correspondence_address', 'same_as_permanent_address',
            'aadhaar_number', 'aadhaar_card_file', 'pan_number', 'pan_card_file', 'passport_number', 'passport_copy_file', 'address_proof_file',
            'highest_education', 'year_of_graduation', 'course', 'degree_certificate_file',
            'bank_name', 'account_holder_name', 'bank_account_number', 'ifsc_code', 'branch_name',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full legal name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address for communication'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary phone number (10-12 digits)', 'inputmode': 'numeric'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp number (optional)', 'inputmode': 'numeric'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's full name"}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's full name"}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Spouse's name (if married)"}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact number', 'inputmode': 'numeric'}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Full permanent address', 'rows': 3}),
            'correspondence_address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mailing address (leave blank if same as permanent)', 'rows': 3}),
            'same_as_permanent_address': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aadhaar number (12 digits)', 'inputmode': 'numeric'}),
            'aadhaar_card_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN number (AAAAA9999A)'}),
            'pan_card_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Passport number (optional)'}),
            'passport_copy_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'address_proof_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'highest_education': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Bachelor of Science'}),
            'year_of_graduation': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year (YYYY)', 'min': '1960', 'max': '2099'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course/Major name'}),
            'degree_certificate_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank name'}),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account holder name (as per bank records)'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank account number', 'inputmode': 'numeric'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IFSC code (AAAA0AAAAAA)'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank branch name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # mark required fields with asterisk in label
        for name, field in self.fields.items():
            if field.required:
                field.label = forms.utils.format_lazy("{} <span class=\"text-danger\">*</span>", field.label or name.replace('_', ' ').title())

    def clean_phone_number(self):
        value = self.cleaned_data.get('phone_number', '')
        digits = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits):
            raise ValidationError('Phone number must contain 10-12 digits.')
        return digits

    def clean_whatsapp_number(self):
        value = self.cleaned_data.get('whatsapp_number', '')
        if value:
            digits = re.sub(r'\D', '', value)
            if not re.match(r'^\d{10,12}$', digits):
                raise ValidationError('WhatsApp number must contain 10-12 digits.')
            return digits
        return value

    def clean_aadhaar_number(self):
        value = (self.cleaned_data.get('aadhaar_number') or '').strip()
        if value and not re.match(r'^\d{12}$', value):
            raise ValidationError('Aadhaar number must be exactly 12 digits.')
        return value

    def clean_pan_number(self):
        value = (self.cleaned_data.get('pan_number') or '').strip().upper()
        if value and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', value):
            raise ValidationError('PAN number format invalid. Expected: AAAAA9999A')
        return value

    def clean_ifsc_code(self):
        value = (self.cleaned_data.get('ifsc_code') or '').strip().upper()
        if value and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', value):
            raise ValidationError('IFSC code format invalid. Expected: AAAA0AAAAAA')
        return value

    def clean(self):
        cleaned = super().clean()
        # cross checks
        if cleaned.get('date_of_birth') and cleaned.get('date_of_joining'):
            if cleaned['date_of_birth'] >= cleaned['date_of_joining']:
                self.add_error('date_of_birth', 'Date of birth must be before joining date.')

        if cleaned.get('bank_account_number') and cleaned.get('confirm_bank_account_number'):
            if cleaned['bank_account_number'] != cleaned['confirm_bank_account_number']:
                self.add_error('confirm_bank_account_number', 'Bank account numbers do not match.')

        if not cleaned.get('same_as_permanent_address') and not cleaned.get('correspondence_address'):
            self.add_error('correspondence_address', 'Correspondence address required if different from permanent.')

        if cleaned.get('marital_status') == 'married' and not cleaned.get('spouse_name'):
            self.add_error('spouse_name', 'Spouse name is required for married status.')

        # file checks handled by model/form earlier if present
        return cleaned


class RecruiterSimpleRegistrationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    company_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company or agency name (optional)'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (10-12 digits)', 'inputmode': 'numeric'}))
    linkedin_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
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
        data = self.cleaned_data
        user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'], first_name=data.get('first_name', ''), last_name=data.get('last_name', ''))
        profile = Profile.objects.create(user=user, first_name=data.get('first_name',''), last_name=data.get('last_name',''), email=data['email'], phone=data.get('phone',''), linkedin_url=data.get('linkedin_url',''))
        recruiter_name = f"{data.get('first_name','')} {data.get('last_name','')}".strip()
        if data.get('company_name'):
            recruiter_name += f" - {data.get('company_name')}"
        recruiter = Recruiter.objects.create(user=profile, name=recruiter_name, email=data['email'], phone=data.get('phone',''), company_name=data.get('company_name',''), active=False)
        return recruiter


class RecruiterUpdateForm(forms.ModelForm):
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'phone', 'active', 'company_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits):
            raise ValidationError('Phone must contain 10-12 digits only')
        return digits
"""
Consolidated forms for recruiters: comprehensive ModelForm, simple account registration form, and update form.
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

from .models import RecruiterRegistration, Recruiter
from users.models import Profile
from django.contrib.auth.models import User


class RecruiterRegistrationFormModel(forms.ModelForm):
    """Comprehensive ModelForm mapped to RecruiterRegistration."""
    confirm_bank_account_number = forms.CharField(max_length=50, required=False)

    class Meta:
        model = RecruiterRegistration
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        # Basic cross-field validation (bank confirmation, addresses, spouse)
        account = cleaned.get('bank_account_number')
        confirm = cleaned.get('confirm_bank_account_number')
        if account and confirm and account != confirm:
            self.add_error('confirm_bank_account_number', 'Bank account numbers do not match.')

        if not cleaned.get('same_as_permanent_address') and not cleaned.get('correspondence_address'):
            self.add_error('correspondence_address', 'Correspondence address is required if different from permanent.')

        if cleaned.get('marital_status') == 'married' and not cleaned.get('spouse_name'):
            self.add_error('spouse_name', 'Spouse name is required for married status.')

        # File size/type checks
        file_fields = ['aadhaar_card_file', 'pan_card_file', 'passport_copy_file', 'address_proof_file', 'degree_certificate_file']
        allowed = ('.pdf', '.jpg', '.jpeg', '.png')
        for f in file_fields:
            file_obj = cleaned.get(f)
            if file_obj:
                if file_obj.size > 5 * 1024 * 1024:
                    self.add_error(f, 'File size must not exceed 5MB.')
                if not any(file_obj.name.lower().endswith(ext) for ext in allowed):
                    self.add_error(f, 'Only PDF, JPG, JPEG, and PNG files are allowed.')

        return cleaned


class RecruiterSimpleRegistrationForm(forms.Form):
    """Simple account-create form: creates User, Profile, Recruiter."""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    company_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20)
    linkedin_url = forms.URLField(required=False)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits):
            raise ValidationError('Phone must contain 10-12 digits only')
        return phone

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            raise ValidationError({'confirm_password': 'Passwords do not match.'})
        if pw:
            try:
                validate_password(pw)
            except ValidationError as e:
                raise ValidationError({'password': e.messages})
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )

        profile = Profile.objects.create(
            user=user,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data['email'],
            phone=data.get('phone', ''),
            linkedin_url=data.get('linkedin_url', '')
        )

        recruiter_name = f"{data.get('first_name','')} {data.get('last_name','')}".strip()
        if data.get('company_name'):
            recruiter_name += f" - {data.get('company_name')}"

        recruiter = Recruiter.objects.create(
            user=profile,
            name=recruiter_name,
            email=data['email'],
            phone=data.get('phone',''),
            company_name=data.get('company_name',''),
            active=False,
        )

        return recruiter


class RecruiterUpdateForm(forms.ModelForm):
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'phone', 'active', 'company_name']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits):
            raise ValidationError('Phone must contain 10-12 digits only')
        return phone
"""
Recruiter Registration Form with comprehensive validation and file handling.
Industry-standard form with proper error handling and user feedback.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.html import format_html
import re
from .models import Recruiter, RecruiterRegistration
from users.models import Profile


class RecruiterRegistrationFormModel(forms.ModelForm):
    """
    Comprehensive recruiter onboarding form - MODEL FORM.
    All file fields are optional. Validates phone numbers, ID numbers, dates, etc.
    Integrates with RecruiterRegistration model.
    """
    
    # Confirmation field for bank account
    confirm_bank_account_number = forms.CharField(
        max_length=50,
        required=True,
        help_text='Confirm your bank account number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm account number'
        })
    )

    class Meta:
        model = RecruiterRegistration
        fields = [
            # Basic Details
            'full_name', 'email',
            # Contact Details
            'phone_number', 'whatsapp_number',
            'date_of_joining', 'date_of_birth', 'gender',
            # Personal & Family Details
            'marital_status', 'father_name', 'mother_name',
            'spouse_name', 'blood_group', 'emergency_contact_number',
            # Address Details
            'permanent_address', 'correspondence_address',
            'same_as_permanent_address',
            # ID Proofs (Optional)
            'aadhaar_number', 'aadhaar_card_file',
            'pan_number', 'pan_card_file',
            'passport_number', 'passport_copy_file',
            'address_proof_file',
            # Education Details
            'highest_education', 'year_of_graduation', 'course',
            'degree_certificate_file',
            # Bank Details
            'bank_name', 'account_holder_name',
            'bank_account_number', 'ifsc_code', 'branch_name',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full legal name',
                'maxlength': '100'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (10-12 digits)',
                'maxlength': '20'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WhatsApp number (optional)',
                'maxlength': '20'
            }),
            'date_of_joining': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'father_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Father's full name",
                'maxlength': '100'
            }),
            'mother_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Mother's full name",
                'maxlength': '100'
            }),
            'spouse_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Spouse's name (if married)",
                'maxlength': '100'
            }),
            'blood_group': forms.Select(attrs={
                'class': 'form-control'
            }),
            'emergency_contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact number',
                'maxlength': '20'
            }),
            'permanent_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Full permanent address',
                'rows': 3
            }),
            'correspondence_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mailing address (optional)',
                'rows': 3
            }),
            'same_as_permanent_address': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'aadhaar_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Aadhaar number (12 digits)',
                'maxlength': '14'
            }),
            'aadhaar_card_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'pan_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PAN number (AAAAA9999A)',
                'maxlength': '10'
            }),
            'pan_card_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Passport number (optional)',
                'maxlength': '20'
            }),
            'passport_copy_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'address_proof_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'highest_education': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor of Science, Master of Business Administration',
                'maxlength': '100'
            }),
            'year_of_graduation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Year (YYYY)',
                'min': '1960',
                'max': '2099'
            }),
            'course': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course/Major name',
                'maxlength': '100'
            }),
            'degree_certificate_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank name',
                'maxlength': '100'
            }),
            'account_holder_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account holder name (as per bank)',
                'maxlength': '100'
            }),
            'bank_account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank account number',
                'maxlength': '50'
            }),
            'ifsc_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IFSC code (AAAA0AAAAAA)',
                'maxlength': '20'
            }),
            'branch_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank branch name',
                'maxlength': '100'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add 'required' asterisk to required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.label = format_html('{}{}', field.label or field_name.replace('_', ' ').title(), ' <span class="text-danger">*</span>')

    def clean_full_name(self):
        """Validate full name"""
        value = (self.cleaned_data.get('full_name') or '').strip()
        if not value:
            raise ValidationError('Full name is required.')
        if len(value) < 3:
            raise ValidationError('Full name must be at least 3 characters.')
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", value):
            raise ValidationError('Full name can only contain letters, spaces, hyphens, apostrophes, and periods.')
        return value

    def clean_email(self):
        """Validate email uniqueness"""
        value = self.cleaned_data.get('email', '').lower()
        if RecruiterRegistration.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise ValidationError('A recruiter with this email already exists.')
        return value

    def clean_phone_number(self):
        """Validate phone number (10-12 digits)"""
        value = self.cleaned_data.get('phone_number', '')
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise ValidationError('Phone number must contain 10-12 digits.')
        return value

    def clean_whatsapp_number(self):
        """Validate WhatsApp number if provided"""
        value = self.cleaned_data.get('whatsapp_number', '')
        if value:
            digits_only = re.sub(r'\D', '', value)
            if not re.match(r'^\d{10,12}$', digits_only):
                raise ValidationError('WhatsApp number must contain 10-12 digits.')
        return value

    def clean_emergency_contact_number(self):
        """Validate emergency contact number"""
        value = self.cleaned_data.get('emergency_contact_number', '')
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise ValidationError('Emergency contact number must contain 10-12 digits.')
        return value

    def clean_date_of_birth(self):
        """Validate date of birth"""
        from datetime import datetime
        value = self.cleaned_data.get('date_of_birth')
        if not value:
            raise ValidationError('Date of birth is required.')
        if value >= datetime.now().date():
            raise ValidationError('Date of birth must be in the past.')
        age = (datetime.now().date() - value).days // 365
        if age < 18:
            raise ValidationError('You must be at least 18 years old.')
        return value

    def clean_date_of_joining(self):
        """Validate date of joining"""
        value = self.cleaned_data.get('date_of_joining')
        if not value:
            raise ValidationError('Date of joining is required.')
        return value

    def clean_aadhaar_number(self):
        """Validate Aadhaar number (12 digits)"""
        value = (self.cleaned_data.get('aadhaar_number') or '').strip()
        if value and not re.match(r'^\d{12}$', value):
            raise ValidationError('Aadhaar number must be exactly 12 digits.')
        return value

    def clean_pan_number(self):
        """Validate PAN number format"""
        value = (self.cleaned_data.get('pan_number') or '').strip().upper()
        if value and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', value):
            raise ValidationError('PAN number format invalid. Expected: AAAAA9999A')
        return value

    def clean_ifsc_code(self):
        """Validate IFSC code"""
        value = (self.cleaned_data.get('ifsc_code') or '').strip().upper()
        if value and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', value):
            raise ValidationError('IFSC code format invalid. Expected: AAAA0AAAAAA')
        return value

    def clean_passport_number(self):
        """Validate passport number if provided"""
        value = (self.cleaned_data.get('passport_number') or '').strip()
        if value and not re.match(r'^[A-Z0-9]{6,20}$', value):
            raise ValidationError('Passport number format invalid.')
        return value

    def clean_bank_account_number(self):
        """Validate bank account number"""
        value = self.cleaned_data.get('bank_account_number', '')
        if not value:
            raise ValidationError('Bank account number is required.')
        if len(value) < 5:
            raise ValidationError('Bank account number too short.')
        if len(value) > 50:
            raise ValidationError('Bank account number too long.')
        return value

    def clean_year_of_graduation(self):
        """Validate year of graduation"""
        from datetime import datetime
        value = self.cleaned_data.get('year_of_graduation')
        if not value:
            raise ValidationError('Year of graduation is required.')
        current_year = datetime.now().year
        if value < 1960 or value > current_year:
            raise ValidationError(f'Year of graduation must be between 1960 and {current_year}.')
        return value

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()

        # Validate dates
        dob = cleaned_data.get('date_of_birth')
        doj = cleaned_data.get('date_of_joining')
        if dob and doj and dob >= doj:
            self.add_error('date_of_birth', 'Date of birth must be before joining date.')

        # Validate bank account confirmation
        account = cleaned_data.get('bank_account_number', '')
        confirm_account = cleaned_data.get('confirm_bank_account_number', '')
        if account and confirm_account and account != confirm_account:
            self.add_error('confirm_bank_account_number', 'Bank account numbers do not match.')

        # Validate correspondence address if different
        same_as_permanent = cleaned_data.get('same_as_permanent_address', True)
        correspondence = (cleaned_data.get('correspondence_address') or '').strip()
        if not same_as_permanent and not correspondence:
            self.add_error('correspondence_address', 'Correspondence address is required if different from permanent.')

        # Validate spouse name for married
        marital_status = cleaned_data.get('marital_status')
        spouse = (cleaned_data.get('spouse_name') or '').strip()
        if marital_status == 'married' and not spouse:
            self.add_error('spouse_name', 'Spouse name is required for married status.')

        # Validate file sizes (max 5MB per file)
        file_fields = [
            'aadhaar_card_file', 'pan_card_file', 'passport_copy_file',
            'address_proof_file', 'degree_certificate_file'
        ]
        for field_name in file_fields:
            file_obj = cleaned_data.get(field_name)
            if file_obj and file_obj.size > 5 * 1024 * 1024:  # 5MB
                self.add_error(field_name, 'File size must not exceed 5MB.')

        # Validate file types
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        for field_name in file_fields:
            file_obj = cleaned_data.get(field_name)
            if file_obj:
                file_ext = file_obj.name.lower()
                if not any(file_ext.endswith(ext) for ext in allowed_extensions):
                    self.add_error(field_name, 'Only PDF, JPG, JPEG, and PNG files are allowed.')

        return cleaned_data


class RecruiterRegistrationForm(forms.Form):
    """Django form for simple recruiter registration with proper widgets"""
    
    # User credentials
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True
        }),
        help_text='This will be your login username'
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': True
        }),
        help_text='At least 8 characters'
    )
    
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        })
    )
    
    # Personal information
    first_name = forms.CharField(
        label='First Name',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'required': True
        })
    )
    
    last_name = forms.CharField(
        label='Last Name',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'required': True
        })
    )
    
    # Recruiter-specific information
    company_name = forms.CharField(
        label='Company Name',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company or agency name (optional)'
        }),
        help_text='Optional'
    )
    
    phone = forms.CharField(
        label='Phone Number',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234567890',
            'required': True
        }),
        help_text='10-12 digits only'
    )
    
    linkedin_url = forms.URLField(
        label='LinkedIn Profile',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/yourprofile'
        }),
        help_text='Optional'
    )
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        digits_only = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise ValidationError('Phone must contain 10-12 digits only')
        return phone
    
    def clean(self):
        """Validate password match and strength"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError({'confirm_password': 'Passwords do not match.'})
            
            # Validate password strength
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError({'password': e.messages})
        
        return cleaned_data
    
    def save(self):
        """Create User, Profile, and Recruiter instances"""
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        phone = self.cleaned_data['phone']
        company_name = self.cleaned_data.get('company_name', '')
        linkedin_url = self.cleaned_data.get('linkedin_url', '')
        
        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create Profile
        profile = Profile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            linkedin_url=linkedin_url
        )
        
        # Create Recruiter
        recruiter_name = f"{first_name} {last_name}"
        if company_name:
            recruiter_name += f" - {company_name}"
        
        recruiter = Recruiter.objects.create(
            user=profile,
            name=recruiter_name,
            email=email,
            phone=phone,
            active=False  # Require admin approval
        )
        
        return recruiter


class RecruiterUpdateForm(forms.ModelForm):
    """Django form for updating recruiter information"""
    
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'phone', 'active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'phone': '10-12 digits only',
            'active': 'Uncheck to deactivate this recruiter'
        }
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        digits_only = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise ValidationError('Phone must contain 10-12 digits only')
        return phone
    
    def clean_email(self):
        """Validate email uniqueness (excluding current recruiter)"""
        email = self.cleaned_data.get('email')
        if self.instance:
            if Recruiter.objects.exclude(id=self.instance.id).filter(email=email).exists():
                raise ValidationError('A recruiter with this email already exists.')
        return email

    """Django form for recruiter registration with proper widgets"""
    
    # User credentials
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': True
        }),
        help_text='This will be your login username'
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': True
        }),
        help_text='At least 8 characters'
    )
    
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        })
    )
    
    # Personal information
    first_name = forms.CharField(
        label='First Name',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'required': True
        })
    )
    
    last_name = forms.CharField(
        label='Last Name',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'required': True
        })
    )
    
    # Recruiter-specific information
    company_name = forms.CharField(
        label='Company Name',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company or agency name (optional)'
        }),
        help_text='Optional'
    )
    
    phone = forms.CharField(
        label='Phone Number',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234567890',
            'required': True
        }),
        help_text='10-12 digits only'
    )
    
    linkedin_url = forms.URLField(
        label='LinkedIn Profile',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/yourprofile'
        }),
        help_text='Optional'
    )
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        digits_only = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise ValidationError('Phone must contain 10-12 digits only')
        return phone
    
    def clean(self):
        """Validate password match and strength"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError({'confirm_password': 'Passwords do not match.'})
            
            # Validate password strength
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError({'password': e.messages})
        
        return cleaned_data
    
    def save(self):
        """Create User, Profile, and Recruiter instances"""
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        phone = self.cleaned_data['phone']
        company_name = self.cleaned_data.get('company_name', '')
        linkedin_url = self.cleaned_data.get('linkedin_url', '')
        
        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create Profile
        profile = Profile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            linkedin_url=linkedin_url
        )
        
        # Create Recruiter
        recruiter_name = f"{first_name} {last_name}"
        if company_name:
            recruiter_name += f" - {company_name}"
        
        recruiter = Recruiter.objects.create(
            user=profile,
            name=recruiter_name,
            email=email,
            phone=phone,
            active=True
        )
        
        return recruiter


class RecruiterUpdateForm(forms.ModelForm):
    """Django form for updating recruiter information"""
    
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'phone', 'active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'phone': '10-12 digits only',
            'active': 'Uncheck to deactivate this recruiter'
        }
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        digits_only = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise ValidationError('Phone must contain 10-12 digits only')
        return phone
    
    def clean_email(self):
        """Validate email uniqueness (excluding current recruiter)"""
        email = self.cleaned_data.get('email')
        if self.instance:
            if Recruiter.objects.exclude(id=self.instance.id).filter(email=email).exists():
                raise ValidationError('A recruiter with this email already exists.')
        return email
