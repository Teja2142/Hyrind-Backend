from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Recruiter, Assignment, RecruiterRegistration
from users.models import Profile
import re


class RecruiterSerializer(serializers.ModelSerializer):
    """Serializer for Recruiter model - read operations"""
    user_email = serializers.EmailField(source='user.user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'name', 'email', 'phone', 'company_name', 'user_email', 'user_name', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get full name from associated profile"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class RecruiterLoginSerializer(serializers.Serializer):
    """Serializer for recruiter login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class RecruiterRegistrationSerializer(serializers.Serializer):
    """Serializer for recruiter registration - creates User, Profile, and Recruiter"""
    # User credentials
    email = serializers.EmailField(help_text='Email address (will be used for login)')
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, help_text='Password must be at least 8 characters')
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, help_text='Confirm password')
    
    # Personal information
    first_name = serializers.CharField(max_length=50, help_text='First name')
    last_name = serializers.CharField(max_length=50, help_text='Last name')
    
    # Recruiter-specific information
    company_name = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text='Company or agency name')
    phone = serializers.CharField(max_length=20, help_text='Phone number (10-12 digits)')
    
    # Optional fields
    linkedin_url = serializers.URLField(required=False, allow_blank=True, help_text='LinkedIn profile URL')
    
    def validate_email(self, value):
        """Check if email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        if Recruiter.objects.filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value
    
    def validate_phone(self, value):
        """Validate phone number format (10-12 digits only)"""
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError('Phone must contain 10-12 digits only')
        return value
    
    def validate(self, data):
        """Validate password match and strength"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        
        try:
            validate_password(data['password'])
        except Exception as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return data
    
    def create(self, validated_data):
        """Create User, Profile, and Recruiter instances"""
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        phone = validated_data['phone']
        company_name = validated_data.get('company_name', '')
        linkedin_url = validated_data.get('linkedin_url', '')
        
        # Create User (email as username)
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
        
        # Create Recruiter (inactive by default, requires admin approval)
        recruiter_name = f"{first_name} {last_name}"
        if company_name:
            recruiter_name += f" - {company_name}"
        
        recruiter = Recruiter.objects.create(
            user=profile,
            name=recruiter_name,
            email=email,
            phone=phone,
            company_name=company_name,
            active=False  # Recruiter must be approved by admin
        )
        
        # Audit log
        try:
            from audit.utils import log_action
            log_action(actor=user, action='recruiter_registered', target=f'Recruiter:{recruiter.id}', metadata={'email': email})
        except Exception:
            pass
        
        return recruiter


class RecruiterUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating recruiter information (recruiters update their own profile)"""
    phone = serializers.CharField(max_length=20)
    
    class Meta:
        model = Recruiter
        fields = ['name', 'phone', 'company_name']
    
    def validate_phone(self, value):
        """Validate phone number format (10-12 digits only)"""
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError('Phone must contain 10-12 digits only')
        return value


class RecruiterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing recruiters"""
    total_assignments = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'name', 'email', 'phone', 'company_name', 'user_name', 'active', 'total_assignments', 'created_at']
    
    def get_total_assignments(self, obj):
        """Get count of assignments for this recruiter"""
        return obj.assignment_set.count()
    
    def get_user_name(self, obj):
        """Get full name from associated profile"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class RecruiterAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update recruiter (can change active status)"""
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'phone', 'company_name', 'active']
    
    def validate_email(self, value):
        """Check if email is unique (excluding current recruiter)"""
        recruiter = self.instance
        if Recruiter.objects.exclude(id=recruiter.id).filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value


class AssignmentSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSerializer(read_only=True)
    recruiter_id = serializers.PrimaryKeyRelatedField(queryset=Recruiter.objects.all(), source='recruiter', write_only=True)
    profile_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='profile', write_only=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'profile', 'profile_id', 'recruiter', 'recruiter_id', 'assigned_at', 'updated_at']
        read_only_fields = ['id', 'assigned_at', 'updated_at']


# ============================================================================
# RECRUITER REGISTRATION FORM SERIALIZERS
# ============================================================================

class RecruiterRegistrationFormSerializer(serializers.ModelSerializer):
    """Serializer for comprehensive recruiter onboarding form"""
    confirm_bank_account_number = serializers.CharField(
        max_length=50,
        write_only=True,
        help_text='Confirm bank account number'
    )
    
    class Meta:
        model = RecruiterRegistration
        fields = [
            'id',
            # Basic Details
            'full_name', 'email',
            # Contact Details
            'phone_number', 'whatsapp_number', 'date_of_joining', 'date_of_birth', 'gender',
            # Personal & Family Details
            'marital_status', 'father_name', 'mother_name', 'spouse_name',
            'blood_group', 'emergency_contact_number',
            # Address Details
            'permanent_address', 'correspondence_address', 'same_as_permanent_address',
            # ID Proofs
            'aadhaar_number', 'aadhaar_card_file',
            'pan_number', 'pan_card_file',
            'passport_number', 'passport_copy_file',
            'address_proof_file',
            # Education Details
            'highest_education', 'year_of_graduation', 'course', 'degree_certificate_file',
            # Bank Details
            'bank_name', 'account_holder_name', 'bank_account_number', 'confirm_bank_account_number',
            'ifsc_code', 'branch_name',
            # Metadata
            'created_at', 'is_verified',
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']
    
    def validate_email(self, value):
        """Check if email is unique"""
        if RecruiterRegistration.objects.filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError('Phone number must contain 10-12 digits.')
        return value
    
    def validate_whatsapp_number(self, value):
        """Validate WhatsApp number if provided"""
        if value:
            digits_only = re.sub(r'\D', '', value)
            if not re.match(r'^\d{10,12}$', digits_only):
                raise serializers.ValidationError('WhatsApp number must contain 10-12 digits.')
        return value
    
    def validate_aadhaar_number(self, value):
        """Validate Aadhaar number (12 digits)"""
        if not re.match(r'^\d{12}$', value.strip()):
            raise serializers.ValidationError('Aadhaar number must be exactly 12 digits.')
        return value
    
    def validate_pan_number(self, value):
        """Validate PAN number format (5 letters, 4 digits, 1 letter)"""
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', value.strip()):
            raise serializers.ValidationError('PAN number format invalid. Expected: AAAAA9999A')
        return value
    
    def validate_ifsc_code(self, value):
        """Validate IFSC code (11 characters)"""
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', value.strip()):
            raise serializers.ValidationError('IFSC code format invalid. Expected: AAAA0AAAAAA')
        return value
    
    def validate(self, data):
        """Validate bank account confirmation and correspondence address"""
        # Validate bank account numbers match
        confirm_bank_account = data.pop('confirm_bank_account_number', None)
        if data.get('bank_account_number') != confirm_bank_account:
            raise serializers.ValidationError({
                'confirm_bank_account_number': 'Bank account numbers do not match.'
            })
        
        # Validate correspondence address if not same as permanent
        if not data.get('same_as_permanent_address') and not data.get('correspondence_address'):
            raise serializers.ValidationError({
                'correspondence_address': 'Correspondence address is required if different from permanent.'
            })
        
        # Validate date_of_birth < date_of_joining
        if data.get('date_of_birth') and data.get('date_of_joining'):
            if data['date_of_birth'] >= data['date_of_joining']:
                raise serializers.ValidationError({
                    'date_of_birth': 'Date of birth must be before joining date.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create RecruiterRegistration instance with file handling"""
        instance = RecruiterRegistration.objects.create(**validated_data)
        return instance
    
    def update(self, instance, validated_data):
        """Update RecruiterRegistration instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecruiterRegistrationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing recruiter registrations"""
    
    class Meta:
        model = RecruiterRegistration
        fields = [
            'id', 'full_name', 'email', 'phone_number',
            'date_of_joining', 'aadhaar_number', 'pan_number',
            'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecruiterSerializer(serializers.ModelSerializer):
    """Serializer for Recruiter model - read operations"""
    user_email = serializers.EmailField(source='user.user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'name', 'email', 'phone', 'company_name', 'user_email', 'user_name', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get full name from associated profile"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class RecruiterLoginSerializer(serializers.Serializer):
    """Serializer for recruiter login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class RecruiterRegistrationSerializer(serializers.Serializer):
    """Serializer for recruiter registration - creates User, Profile, and Recruiter"""
    # User credentials
    email = serializers.EmailField(help_text='Email address (will be used for login)')
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, help_text='Password must be at least 8 characters')
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, help_text='Confirm password')
    
    # Personal information
    first_name = serializers.CharField(max_length=50, help_text='First name')
    last_name = serializers.CharField(max_length=50, help_text='Last name')
    
    # Recruiter-specific information
    company_name = serializers.CharField(max_length=100, required=False, allow_blank=True, help_text='Company or agency name')
    phone = serializers.CharField(max_length=20, help_text='Phone number (10-12 digits)')
    
    # Optional fields
    linkedin_url = serializers.URLField(required=False, allow_blank=True, help_text='LinkedIn profile URL')
    
    def validate_email(self, value):
        """Check if email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        if Recruiter.objects.filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value
    
    def validate_phone(self, value):
        """Validate phone number format (10-12 digits only)"""
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError('Phone must contain 10-12 digits only')
        return value
    
    def validate(self, data):
        """Validate password match and strength"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        
        try:
            validate_password(data['password'])
        except Exception as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return data
    
    def create(self, validated_data):
        """Create User, Profile, and Recruiter instances"""
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        phone = validated_data['phone']
        company_name = validated_data.get('company_name', '')
        linkedin_url = validated_data.get('linkedin_url', '')
        
        # Create User (email as username)
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
        
        # Create Recruiter (inactive by default, requires admin approval)
        recruiter_name = f"{first_name} {last_name}"
        if company_name:
            recruiter_name += f" - {company_name}"
        
        recruiter = Recruiter.objects.create(
            user=profile,
            name=recruiter_name,
            email=email,
            phone=phone,
            company_name=company_name,
            active=False  # Recruiter must be approved by admin
        )
        
        # Audit log
        try:
            from audit.utils import log_action
            log_action(actor=user, action='recruiter_registered', target=f'Recruiter:{recruiter.id}', metadata={'email': email})
        except Exception:
            pass
        
        return recruiter


class RecruiterUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating recruiter information (recruiters update their own profile)"""
    phone = serializers.CharField(max_length=20)
    
    class Meta:
        model = Recruiter
        fields = ['name', 'phone', 'company_name']
    
    def validate_phone(self, value):
        """Validate phone number format (10-12 digits only)"""
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError('Phone must contain 10-12 digits only')
        return value


class RecruiterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing recruiters"""
    total_assignments = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'name', 'email', 'phone', 'company_name', 'user_name', 'active', 'total_assignments', 'created_at']
    
    def get_total_assignments(self, obj):
        """Get count of assignments for this recruiter"""
        return obj.assignment_set.count()
    
    def get_user_name(self, obj):
        """Get full name from associated profile"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class RecruiterAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update recruiter (can change active status)"""
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'phone', 'company_name', 'active']
    
    def validate_email(self, value):
        """Check if email is unique (excluding current recruiter)"""
        recruiter = self.instance
        if Recruiter.objects.exclude(id=recruiter.id).filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value


class AssignmentSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSerializer(read_only=True)
    recruiter_id = serializers.PrimaryKeyRelatedField(queryset=Recruiter.objects.all(), source='recruiter', write_only=True)
    profile_id = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), source='profile', write_only=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'profile', 'profile_id', 'recruiter', 'recruiter_id', 'assigned_at', 'updated_at']
        read_only_fields = ['id', 'assigned_at', 'updated_at']