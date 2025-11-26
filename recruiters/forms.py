from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Recruiter
from users.models import Profile
import re


class RecruiterRegistrationForm(forms.Form):
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
