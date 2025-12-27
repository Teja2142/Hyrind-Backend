from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, InterestSubmission, Contact
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import os
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')  # Removed username since we use email for auth


class UserPublicSerializer(serializers.ModelSerializer):
    profile_id = serializers.UUIDField(source='profile.id', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'profile_id', 'email')  # Removed username

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # nested user is read-only for responses
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user', required=False)
    assignment_status = serializers.SerializerMethodField()
    recruiter_info = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'phone', 'university',
            'degree', 'major', 'visa_status', 'graduation_date', 'opt_end_date', 'resume_file', 'consent_to_terms',
            'referral_source', 'linkedin_url', 'github_url', 'additional_notes', 'user_id', 'active',
            'assignment_status', 'recruiter_info'
        ]

    def get_assignment_status(self, obj):
        """Get client's assignment status to a recruiter"""
        try:
            assignment = obj.assignment
            return {
                'status': assignment.status,
                'priority': assignment.priority,
                'assigned_at': assignment.assigned_at,
                'last_activity': assignment.last_activity
            }
        except Exception:
            return None

    def get_recruiter_info(self, obj):
        """Get assigned recruiter information"""
        try:
            assignment = obj.assignment
            if assignment.recruiter:
                return {
                    'id': str(assignment.recruiter.id),
                    'name': assignment.recruiter.name,
                    'email': assignment.recruiter.email,
                    'employee_id': assignment.recruiter.employee_id
                }
        except Exception:
            pass
        return None

    def validate(self, data):
        import re
        # phone format: 10-12 digits only
        phone = data.get('phone')
        if phone:
            # Remove any non-digit characters for validation
            digits_only = re.sub(r'\D', '', phone)
            if not re.match(r'^\d{10,12}$', digits_only):
                raise serializers.ValidationError({'phone': 'Phone must contain 10-12 digits only'})

        # graduation_date: if provided but blank -> normalize to None; if provided as MM/YYYY string -> parse
        gd = data.get('graduation_date')
        if gd == '' or gd is None:
            # allow clearing the date on update
            data['graduation_date'] = None
        elif isinstance(gd, str):
            try:
                data['graduation_date'] = datetime.strptime(gd.strip(), '%m/%Y').date()
            except Exception:
                raise serializers.ValidationError({'graduation_date': 'Graduation date must be MM/YYYY'})

        # opt_end_date: normalize blanks to None; require when F1-OPT
        opt = data.get('opt_end_date')
        if opt == '' or opt is None:
            data['opt_end_date'] = None
        if data.get('visa_status') == 'F1-OPT':
            if not data.get('opt_end_date'):
                raise serializers.ValidationError({'opt_end_date': 'opt_end_date is required when visa_status is F1-OPT'})
            if isinstance(data['opt_end_date'], str):
                try:
                    data['opt_end_date'] = datetime.strptime(data['opt_end_date'].strip(), '%m/%Y').date()
                except Exception:
                    raise serializers.ValidationError({'opt_end_date': 'opt_end_date must be MM/YYYY'})

        # resume_file validation
        resume_file = data.get('resume_file')
        if resume_file:
            name = resume_file.name.lower()
            if not (name.endswith('.pdf') or name.endswith('.docx')):
                raise serializers.ValidationError({'resume_file': 'Resume must be a PDF or DOCX file.'})
            if resume_file.size > 5 * 1024 * 1024:
                raise serializers.ValidationError({'resume_file': 'Resume must be 5MB or smaller.'})

        # URLs
        url_validator = URLValidator()
        for field in ('linkedin_url', 'github_url'):
            val = data.get(field)
            if val:
                try:
                    url_validator(val)
                except ValidationError:
                    raise serializers.ValidationError({field: 'Invalid URL'})

        # consent
        consent = data.get('consent_to_terms')
        if consent is not None and not consent:
            raise serializers.ValidationError({'consent_to_terms': 'Consent to terms is required.'})

        return data

class RegistrationSerializer(serializers.Serializer):
    # Removed username - we'll use email as username for Django User model
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=20)
    university = serializers.CharField(max_length=100)
    degree = serializers.ChoiceField(choices=[("Bachelor's", "Bachelor's"), ("Master's", "Master's"), ("PhD", "PhD")])
    major = serializers.CharField(max_length=100)
    visa_status = serializers.ChoiceField(choices=['F1-OPT', 'F1-CPT', 'H1B', 'Green Card', 'Citizen', 'Other'])
    graduation_date = serializers.CharField(help_text='MM/YYYY')
    opt_end_date = serializers.CharField(required=False, allow_blank=True, help_text='MM/YYYY (if applicable)')
    resume_file = serializers.FileField()
    referral_source = serializers.ChoiceField(choices=['Google', 'LinkedIn', 'Friend', 'University', 'Other'],required=False, allow_blank=True)
    consent_to_terms = serializers.BooleanField()
    linkedin_url = serializers.CharField(required=False, allow_blank=True)
    github_url = serializers.CharField(required=False, allow_blank=True)
    additional_notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, data):
        # passwords
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')

        # consent
        if not data.get('consent_to_terms'):
            raise serializers.ValidationError('Consent to terms is required.')

        # unique email check
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'A user with that email already exists.'})

        # phone format: 10-12 digits only
        import re
        phone = data.get('phone', '')
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError({'phone': 'Phone must contain 10-12 digits only'})

        # parse graduation_date (MM/YYYY) - must be present and non-empty
        gd_raw = data.get('graduation_date')
        if not gd_raw or (isinstance(gd_raw, str) and gd_raw.strip() == ''):
            raise serializers.ValidationError({'graduation_date': 'Graduation date is required and must be MM/YYYY'})
        try:
            datetime_obj = datetime.strptime(gd_raw.strip(), '%m/%Y')
            data['graduation_date'] = datetime_obj.date()
        except Exception:
            raise serializers.ValidationError({'graduation_date': 'Graduation date must be MM/YYYY'})

        # opt_end_date required if F1-OPT. Convert empty to None when not required.
        opt_raw = data.get('opt_end_date')
        if data.get('visa_status') == 'F1-OPT':
            if not opt_raw or (isinstance(opt_raw, str) and opt_raw.strip() == ''):
                raise serializers.ValidationError({'opt_end_date': 'opt_end_date is required when visa_status is F1-OPT'})
            try:
                dt_opt = datetime.strptime(opt_raw.strip(), '%m/%Y')
                data['opt_end_date'] = dt_opt.date()
            except Exception:
                raise serializers.ValidationError({'opt_end_date': 'opt_end_date must be MM/YYYY'})
        else:
            # not required - normalize empty values to None
            if opt_raw == '' or opt_raw is None:
                data['opt_end_date'] = None

        # resume file type/size
        resume_file = data.get('resume_file')
        if resume_file:
            name = resume_file.name.lower()
            if not (name.endswith('.pdf') or name.endswith('.docx')):
                raise serializers.ValidationError({'resume_file': 'Resume must be a PDF or DOCX file.'})
            if resume_file.size > 5 * 1024 * 1024:
                raise serializers.ValidationError({'resume_file': 'Resume must be 5MB or smaller.'})

        # urls validation
        url_validator = URLValidator()
        for field in ('linkedin_url', 'github_url'):
            val = data.get(field)
            if val:
                try:
                    url_validator(val)
                except ValidationError:
                    raise serializers.ValidationError({field: 'Invalid URL'})

        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        # Use email as username for Django User model authentication
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Newly registered users should be inactive until approved by admin
        user.is_active = False
        user.save(update_fields=['is_active'])
        profile = Profile.objects.create(
            user=user,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=email,
            phone=validated_data['phone'],
            university=validated_data.get('university', ''),
            degree=validated_data.get('degree', ''),
            major=validated_data.get('major', ''),
            visa_status=validated_data.get('visa_status', ''),
            # ensure empty strings are not written to DateFields
            graduation_date=validated_data.get('graduation_date', None) or None,
            resume_file=validated_data.get('resume_file', None),
            opt_end_date=validated_data.get('opt_end_date', None),
            consent_to_terms=validated_data['consent_to_terms'],
            referral_source=validated_data.get('referral_source', None),
            linkedin_url=validated_data.get('linkedin_url', None),
            github_url=validated_data.get('github_url', None),
            additional_notes=validated_data.get('additional_notes', None),
            active=False,
        )
        try:
            from audit.utils import log_action
            log_action(actor=user, action='user_registered', target=f'Profile:{str(profile.id)}', metadata={'email': email})
        except Exception:
            pass

        return profile


class AdminRegistrationSerializer(serializers.Serializer):
    """Serializer for creating admin/staff users. Only callable by authenticated admin users."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    is_staff = serializers.BooleanField(default=True)
    is_superuser = serializers.BooleanField(default=False)

    def validate(self, data):
        # password match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')

        # unique email
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'A user with that email already exists.'})

        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.is_active = True
        user.is_staff = bool(validated_data.get('is_staff', True))
        user.is_superuser = bool(validated_data.get('is_superuser', False))
        user.save()

        # create profile for admin user
        try:
            Profile.objects.get_or_create(user=user, defaults={
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'email': user.email or '',
                'active': True,
            })
        except Exception:
            pass

        return user


class InterestSubmissionSerializer(serializers.ModelSerializer):
    # Accepts graduation/opt in MM/YYYY format or Date input; conversion handled in validate()
    graduation_date = serializers.CharField(required=False, allow_blank=True, help_text='MM/YYYY')
    opt_end_date = serializers.CharField(required=False, allow_blank=True, help_text='MM/YYYY')

    class Meta:
        model = InterestSubmission
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'university', 'degree', 'major',
            'visa_status', 'graduation_date', 'opt_end_date', 'resume_file', 'referral_source',
            'consent_to_terms', 'linkedin_url', 'github_url', 'additional_notes', 'created_at'
        ]

    def validate(self, data):
        import re
        # email uniqueness for interest form: allow duplicates but ensure format
        # phone format: 10-12 digits only
        phone = data.get('phone', '')
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', phone)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError({'phone': 'Phone must contain 10-12 digits only'})

        # graduation_date: normalize empty -> None; parse MM/YYYY when provided
        gd = data.get('graduation_date')
        if gd == '' or gd is None:
            data['graduation_date'] = None
        elif isinstance(gd, str):
            try:
                data['graduation_date'] = datetime.strptime(gd.strip(), '%m/%Y').date()
            except Exception:
                raise serializers.ValidationError({'graduation_date': 'Graduation date must be MM/YYYY'})

        # opt_end_date: normalize empty -> None; require when F1-OPT
        opt = data.get('opt_end_date')
        if opt == '' or opt is None:
            data['opt_end_date'] = None
        if data.get('visa_status') == 'F1-OPT':
            if not data.get('opt_end_date'):
                raise serializers.ValidationError({'opt_end_date': 'opt_end_date is required when visa_status is F1-OPT'})
            try:
                data['opt_end_date'] = datetime.strptime(data.get('opt_end_date'), '%m/%Y').date()
            except Exception:
                raise serializers.ValidationError({'opt_end_date': 'opt_end_date must be MM/YYYY'})

        # resume validations
        resume = data.get('resume_file')
        if resume:
            name = resume.name.lower()
            if not (name.endswith('.pdf') or name.endswith('.docx')):
                raise serializers.ValidationError({'resume_file': 'Resume must be a PDF or DOCX file.'})
            if resume.size > 5 * 1024 * 1024:
                raise serializers.ValidationError({'resume_file': 'Resume must be 5MB or smaller.'})

        # urls
        url_validator = URLValidator()
        for field in ('linkedin_url', 'github_url'):
            val = data.get(field)
            if val:
                try:
                    url_validator(val)
                except ValidationError:
                    raise serializers.ValidationError({field: 'Invalid URL'})

        # ensure consent
        if not data.get('consent_to_terms'):
            raise serializers.ValidationError({'consent_to_terms': 'Consent to terms is required.'})

        return data


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model - handles contact form submissions
    """
    class Meta:
        model = Contact
        fields = ['id', 'full_name', 'email', 'phone', 'message', 'created_at', 'responded']
        read_only_fields = ['id', 'created_at', 'responded']

    def validate(self, data):
        import re
        
        # Validate full_name
        full_name = data.get('full_name', '').strip()
        if not full_name:
            raise serializers.ValidationError({'full_name': 'Full name is required.'})
        if len(full_name) < 2:
            raise serializers.ValidationError({'full_name': 'Full name must be at least 2 characters.'})
        
        # Validate email format (handled by EmailField but adding custom message)
        email = data.get('email', '')
        if not email:
            raise serializers.ValidationError({'email': 'Email is required.'})
        
        # Validate phone: 10-12 digits only
        phone = data.get('phone', '')
        if phone:
            # Remove any non-digit characters for validation
            digits_only = re.sub(r'\D', '', phone)
            if not re.match(r'^\d{10,12}$', digits_only):
                raise serializers.ValidationError({'phone': 'Phone must contain 10-12 digits only'})
        else:
            raise serializers.ValidationError({'phone': 'Phone number is required.'})
        
        # Validate message
        message = data.get('message', '').strip()
        if not message:
            raise serializers.ValidationError({'message': 'Message is required.'})
        if len(message) < 10:
            raise serializers.ValidationError({'message': 'Message must be at least 10 characters.'})
        if len(message) > 2000:
            raise serializers.ValidationError({'message': 'Message must not exceed 2000 characters.'})
        
        return data
