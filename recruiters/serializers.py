from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Recruiter, Assignment
from users.models import Profile
import re


class RecruiterSerializer(serializers.ModelSerializer):
    """Serializer for Recruiter model - read operations"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'user', 'user_email', 'user_name', 'name', 'email', 'phone', 'active']
        read_only_fields = ['id', 'user']
    
    def get_user_name(self, obj):
        """Get full name from associated profile"""
        return f"{obj.user.first_name} {obj.user.last_name}"


class RecruiterRegistrationSerializer(serializers.Serializer):
    """Serializer for recruiter registration - creates User, Profile, and Recruiter"""
    # User credentials
    email = serializers.EmailField(
        help_text='Email address (will be used for login)'
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Password must be at least 8 characters'
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirm password'
    )
    
    # Personal information
    first_name = serializers.CharField(
        max_length=50,
        help_text='First name'
    )
    last_name = serializers.CharField(
        max_length=50,
        help_text='Last name'
    )
    
    # Recruiter-specific information
    company_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text='Company or agency name'
    )
    phone = serializers.CharField(
        max_length=20,
        help_text='Phone number (10-12 digits)'
    )
    
    # Optional fields
    linkedin_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text='LinkedIn profile URL'
    )
    
    def validate_email(self, value):
        """Check if email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
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
        
        # Validate password strength
        try:
            validate_password(data['password'])
        except Exception as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return data
    
    def create(self, validated_data):
        """Create User, Profile, and Recruiter instances"""
        # Extract data
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        phone = validated_data['phone']
        company_name = validated_data.get('company_name', '')
        linkedin_url = validated_data.get('linkedin_url', '')
        
        # Create User
        user = User.objects.create_user(
            username=email,  # Use email as username
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


class RecruiterUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating recruiter information"""
    phone = serializers.CharField(max_length=20)
    
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'phone', 'active']
    
    def validate_phone(self, value):
        """Validate phone number format (10-12 digits only)"""
        digits_only = re.sub(r'\D', '', value)
        if not re.match(r'^\d{10,12}$', digits_only):
            raise serializers.ValidationError('Phone must contain 10-12 digits only')
        return value
    
    def validate_email(self, value):
        """Check if email is unique (excluding current recruiter)"""
        recruiter = self.instance
        if Recruiter.objects.exclude(id=recruiter.id).filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value


class RecruiterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing recruiters"""
    total_assignments = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'name', 'email', 'phone', 'active', 'total_assignments']
    
    def get_total_assignments(self, obj):
        """Get count of assignments for this recruiter"""
        return obj.assignment_set.count()


class AssignmentSerializer(serializers.ModelSerializer):
    recruiter = RecruiterSerializer(read_only=True)
    recruiter_id = serializers.PrimaryKeyRelatedField(queryset=Recruiter.objects.all(), source='recruiter', write_only=True)
    class Meta:
        model = Assignment
        fields = ['id', 'profile', 'recruiter', 'recruiter_id', 'assigned_at']