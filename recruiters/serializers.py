from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Recruiter, Assignment, RecruiterRegistration
from users.models import Profile
import re


class RecruiterSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for internal IT Recruiter staff"""
    user_email = serializers.EmailField(source='user.user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    available_slots = serializers.SerializerMethodField()
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Recruiter
        fields = [
            'id', 'employee_id', 'name', 'email', 'phone',
            'department', 'department_display', 'specialization', 'specialization_display',
            'date_of_joining', 'max_clients', 'current_clients_count', 'available_slots',
            'total_placements', 'active_applications',
            'status', 'status_display', 'active', 'verified', 'company_name',
            'user_email', 'user_name', 'notes',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'employee_id', 'current_clients_count', 'total_placements', 
                          'active_applications', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get full name from associated profile"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    
    def get_available_slots(self, obj):
        """Get available client slots"""
        return obj.get_available_slots()


class RecruiterDashboardSerializer(serializers.ModelSerializer):
    """Dashboard serializer with stats and assigned clients"""
    user_name = serializers.SerializerMethodField()
    available_slots = serializers.SerializerMethodField()
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    assigned_clients = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = [
            'id', 'employee_id', 'name', 'email', 'user_name',
            'department', 'department_display', 'specialization', 'specialization_display',
            'max_clients', 'current_clients_count', 'available_slots',
            'total_placements', 'active_applications',
            'status', 'assigned_clients'
        ]
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    
    def get_available_slots(self, obj):
        return obj.get_available_slots()
    
    def get_assigned_clients(self, obj):
        """Get list of assigned clients with details"""
        # Use the related_name 'assignments' defined on Assignment.recruiter
        assignments = obj.assignments.filter(status='active').select_related('profile')
        return [{
            'id': str(assignment.profile.id),
            'name': f"{assignment.profile.first_name} {assignment.profile.last_name}",
            'email': assignment.profile.email,
            'phone': assignment.profile.phone,
            'status': assignment.status,
            'priority': assignment.priority,
            'assigned_at': assignment.assigned_at,
            'last_activity': assignment.last_activity
        } for assignment in assignments]


class RecruiterLoginSerializer(serializers.Serializer):
    """Serializer for recruiter login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class RecruiterRegistrationSerializer(serializers.Serializer):
    """Serializer for internal recruiter/staff registration"""
    # User credentials
    email = serializers.EmailField(help_text='Company email address (will be used for login)')
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, help_text='Password must be at least 8 characters')
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, help_text='Confirm password')
    
    # Personal information
    first_name = serializers.CharField(max_length=50, help_text='First name')
    last_name = serializers.CharField(max_length=50, help_text='Last name')
    phone = serializers.CharField(max_length=20, help_text='Phone number (10-12 digits)')
    
    # Employment information
    employee_id = serializers.CharField(max_length=20, help_text='Employee ID (e.g., REC001)')
    department = serializers.ChoiceField(
        choices=Recruiter.DEPARTMENT_CHOICES,
        default='it_staffing',
        help_text='Department'
    )
    specialization = serializers.ChoiceField(
        choices=Recruiter.SPECIALIZATION_CHOICES,
        default='general_it',
        help_text='Primary specialization area'
    )
    date_of_joining = serializers.DateField(help_text='Employment start date (YYYY-MM-DD)')
    
    # Optional fields
    max_clients = serializers.IntegerField(default=3, min_value=1, max_value=5, help_text='Maximum clients (1-5, default 3)')
    linkedin_url = serializers.URLField(required=False, allow_blank=True, help_text='LinkedIn profile URL')
    
    def validate_email(self, value):
        """Check if email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        if Recruiter.objects.filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value
    
    def validate_employee_id(self, value):
        """Check if employee_id is unique"""
        if Recruiter.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError('A recruiter with this employee ID already exists.')
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
        """Create User, Profile, and Recruiter instances atomically"""
        from django.db import transaction
        
        # Extract and remove non-model fields
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        linkedin_url = validated_data.pop('linkedin_url', '')
        
        with transaction.atomic():
            # Create User
            user = User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=password,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name']
            )
            # Keep account inactive until admin activation
            user.is_active = False
            user.save(update_fields=['is_active'])
            
            # Create Profile
            profile = Profile.objects.create(
                user=user,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                linkedin_url=linkedin_url
            )
            
            # Create Recruiter
            recruiter = Recruiter.objects.create(
                user=profile,
                employee_id=validated_data['employee_id'],
                name=f"{validated_data['first_name']} {validated_data['last_name']}",
                email=validated_data['email'],
                phone=validated_data['phone'],
                department=validated_data['department'],
                specialization=validated_data['specialization'],
                date_of_joining=validated_data['date_of_joining'],
                max_clients=validated_data.get('max_clients', 3),
                status='pending',
                active=False
            )
            
            return recruiter


class RecruiterUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating recruiter information (recruiters update their own profile)"""
    phone = serializers.CharField(max_length=20)
    
    class Meta:
        model = Recruiter
        fields = ['name', 'phone', 'specialization', 'notes']
    
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
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    specialization_display = serializers.CharField(source='get_specialization_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    available_slots = serializers.SerializerMethodField()
    assigned_clients = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = [
            'id', 'employee_id', 'name', 'email', 'phone', 'user_name',
            'department', 'department_display', 'specialization', 'specialization_display',
            'current_clients_count', 'available_slots', 'total_placements', 'active_applications',
            'status', 'status_display', 'active', 'total_assignments', 'assigned_clients', 'created_at'
        ]
    
    def get_available_slots(self, obj):
        return obj.get_available_slots()
    
    def get_total_assignments(self, obj):
        """Get count of assignments for this recruiter"""
        # Use the related_name 'assignments' defined on Assignment.recruiter
        return obj.assignments.count()
    
    def get_user_name(self, obj):
        """Get full name from associated profile"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    
    def get_assigned_clients(self, obj):
        """Get list of assigned clients with basic info"""
        try:
            assignments = obj.assignments.select_related('profile').all()
            return [{
                'id': str(assignment.profile.id),
                'name': f"{assignment.profile.first_name} {assignment.profile.last_name}",
                'email': assignment.profile.email,
                'phone': assignment.profile.phone,
                'status': assignment.status,
                'priority': assignment.priority,
                'assigned_at': assignment.assigned_at,
                'last_activity': assignment.last_activity
            } for assignment in assignments]
        except Exception:
            return []


class RecruiterAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update recruiter (can change active status)"""
    class Meta:
        model = Recruiter
        fields = [
            'name', 'email', 'phone', 'department', 'specialization',
            'max_clients', 'status', 'active', 'verified', 'notes'
        ]
    
    def validate_email(self, value):
        """Check if email is unique (excluding current recruiter)"""
        recruiter = self.instance
        if Recruiter.objects.exclude(id=recruiter.id).filter(email=value).exists():
            raise serializers.ValidationError('A recruiter with this email already exists.')
        return value


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for client-recruiter assignments"""
    recruiter = RecruiterListSerializer(read_only=True)
    recruiter_id = serializers.PrimaryKeyRelatedField(
        queryset=Recruiter.objects.all(),
        source='recruiter',
        write_only=True
    )
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        source='profile',
        write_only=True
    )
    profile_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'profile', 'profile_id', 'profile_name',
            'recruiter', 'recruiter_id',
            'status', 'status_display', 'priority', 'priority_display',
            'assigned_at', 'assigned_by', 'last_activity',
            'placement_date', 'notes', 'internal_comments',
            'updated_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'updated_at']
    
    def get_profile_name(self, obj):
        return f"{obj.profile.first_name} {obj.profile.last_name}".strip()


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
            # Personal Information
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'social_security_number', 'profile_picture',
            
            # Address
            'street_address', 'city', 'state', 'zip_code', 'country',
            
            # Professional Information
            'current_job_title', 'years_of_experience', 'specialization',
            'linkedin_profile', 'professional_summary',
            
            # Education
            'highest_degree', 'field_of_study', 'university_name',
            'graduation_year',
            
            # Certifications & Skills
            'certifications', 'technical_skills', 'languages_spoken',
            
            # Employment History
            'previous_employer_1', 'previous_job_title_1', 'employment_duration_1',
            'previous_employer_2', 'previous_job_title_2', 'employment_duration_2',
            'previous_employer_3', 'previous_job_title_3', 'employment_duration_3',
            
            # References
            'reference_1_name', 'reference_1_phone', 'reference_1_email', 'reference_1_relationship',
            'reference_2_name', 'reference_2_phone', 'reference_2_email', 'reference_2_relationship',
            
            # Availability & Preferences
            'preferred_work_location', 'work_authorization', 'available_start_date',
            'preferred_industries', 'willing_to_relocate', 'travel_willingness',
            
            # Banking & Tax
            'bank_name', 'bank_account_number', 'routing_number',
            'confirm_bank_account_number', 'tax_id_number',
            
            # Emergency Contact
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship',
            
            # Legal & Compliance
            'background_check_consent', 'terms_and_conditions',
            'data_privacy_consent', 'signature',
            
            # Documents
            'resume', 'cover_letter', 'certifications_document', 'id_proof',
            
            # Additional
            'why_join_us', 'additional_comments'
        ]
        extra_kwargs = {
            'social_security_number': {'write_only': True},
            'bank_account_number': {'write_only': True},
            'routing_number': {'write_only': True},
            'tax_id_number': {'write_only': True},
        }
    
    def validate(self, data):
        """Validate bank account number confirmation"""
        if data.get('bank_account_number') != data.get('confirm_bank_account_number'):
            raise serializers.ValidationError({
                'confirm_bank_account_number': 'Bank account numbers do not match.'
            })
        return data
    
    def create(self, validated_data):
        """Create recruiter registration (remove confirm field before saving)"""
        validated_data.pop('confirm_bank_account_number', None)
        return super().create(validated_data)


class RecruiterRegistrationFormListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing registration forms (admin view)"""
    class Meta:
        model = RecruiterRegistration
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'current_job_title', 'years_of_experience',
            'specialization', 'status', 'submitted_at', 'reviewed_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'reviewed_at']


class RecruiterRegistrationFormUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update registration form status"""
    class Meta:
        model = RecruiterRegistration
        fields = ['status', 'admin_notes']
