from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.db import models as django_models
from django.conf import settings

# Constants
DEFAULT_OPERATIONS_EMAIL = 'hyrind.operations@gmail.com'


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Obtain JWT token using email and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email address'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password')
            }
        ),
        responses={200: openapi.Response('Token pair with access and refresh tokens')}
    )
    def post(self, request, *args, **kwargs):
        # Allow login with email by converting email to username
        email = request.data.get('email')
        if email and not request.data.get('username'):
            # Create a mutable copy of request.data
            data = request.data.copy()
            data['username'] = email  # Use email as username for authentication
            request._full_data = data
        return super().post(request, *args, **kwargs)


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend TokenObtainPairSerializer to restrict token issuance to admin users only."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if not (user.is_staff or user.is_superuser):
            raise serializers.ValidationError({
                'detail': 'Admin credentials required.'
            })
        return data


class AdminLoginView(TokenObtainPairView):
    """API endpoint to obtain JWT for admin users only."""
    permission_classes = [AllowAny]
    serializer_class = AdminTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Obtain admin JWT token using email/username and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Admin username or email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
            }
        ),
        responses={200: openapi.Response('Token pair with access and refresh tokens')},
        tags=['Admin']
    )
    def post(self, request, *args, **kwargs):
        # Support email in `username` field similar to LoginView
        email = request.data.get('email')
        if email and not request.data.get('username'):
            data = request.data.copy()
            data['username'] = email
            request._full_data = data
        return super().post(request, *args, **kwargs)
from django.contrib.auth.models import User
from .models import Profile, ClientIntakeSheet, CredentialSheet
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    InterestSubmissionSerializer,
    ContactSerializer,
    UserPublicSerializer,
    AdminRegistrationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    ClientIntakeSheetSerializer,
    CredentialSheetSerializer,
)

class UserList(generics.ListAPIView):
    """
    GET /api/users/ - List ALL users in the system
    
    Returns ALL users including clients, recruiters, and admins.
    No filtering by user type - this shows everyone in the system.
    
    Query Parameters:
        - active: Filter by active status (true/false)
        - status: Filter by registration status (open/approved/ready_to_assign/assigned/waiting_payment/closed/rejected)
        - search: Search by email
    
    Permission: Admin only
    
    Example:
        GET /api/users/
        GET /api/users/?active=true
        GET /api/users/?status=approved
        GET /api/users/?search=john@example.com
    """
    serializer_class = UserPublicSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Get all users in the system without filtering"""
        queryset = User.objects.select_related('profile').order_by('-id')
        
        # Filter by active status
        active = self.request.query_params.get('active', None)
        if active is not None:
            active_bool = active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(profile__active=active_bool)
        
        # Filter by registration status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(profile__registration_status=status)
        
        # Search by email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                django_models.Q(email__icontains=search) |
                django_models.Q(profile__email__icontains=search)
            )
        
        return queryset


class ClientListView(generics.ListAPIView):
    """
    GET /api/clients/ - List CLIENTS ONLY (candidates seeking jobs)
    
    Excludes recruiters and admin users. Returns client users with their 
    profile information, assignment status, and assigned recruiter details.
    
    Query Parameters:
        - active: Filter by active status (true/false)
        - status: Filter by registration status (open/approved/ready_to_assign/assigned/waiting_payment/closed/rejected)
        - has_recruiter: Filter by whether client has assigned recruiter (true/false)
        - search: Search by name or email
    
    Permission: Admin only
    
    Example:
        GET /api/clients/
        GET /api/clients/?active=true
        GET /api/clients/?status=approved
        GET /api/clients/?has_recruiter=false
    """
    serializer_class = UserPublicSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter to show only clients (users without recruiter_profile)"""
        queryset = User.objects.select_related('profile').exclude(
            profile__recruiter_profile__isnull=False
        ).order_by('-id')
        
        # Filter by active status
        active = self.request.query_params.get('active', None)
        if active is not None:
            active_bool = active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(profile__active=active_bool)
        
        # Filter by registration status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(profile__registration_status=status)
        
        # Filter by whether user has assigned recruiter
        has_recruiter = self.request.query_params.get('has_recruiter', None)
        if has_recruiter is not None:
            if has_recruiter.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(profile__assignment__recruiter__isnull=False)
            else:
                queryset = queryset.filter(profile__assignment__recruiter__isnull=True)
        
        # Search by name or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                django_models.Q(profile__first_name__icontains=search) |
                django_models.Q(profile__last_name__icontains=search) |
                django_models.Q(profile__email__icontains=search)
            )
        
        return queryset

class ProfileList(generics.ListCreateAPIView):
    """
    GET /api/users/profiles/ - List ALL user profiles in the system
    POST /api/users/profiles/ - Create a new user profile
    
    Returns ALL profiles including clients, recruiters, and admins.
    No filtering by user type - this shows all profile details for everyone.
    
    Query Parameters:
        - active: Filter by active status (true/false)
        - visa_status: Filter by visa status (F1-OPT, H1B, etc.)
        - university: Filter by university name (partial match)
        - major: Filter by major (partial match)
        - search: Search by name or email
    
    Permission: Admin only
    
    Example:
        GET /api/users/profiles/
        GET /api/users/profiles/?active=true
        GET /api/users/profiles/?visa_status=F1-OPT&university=MIT
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Get all profiles in the system without filtering by user type"""
        queryset = Profile.objects.select_related('user').order_by('-id')
        
        # Filter by active status
        active = self.request.query_params.get('active', None)
        if active is not None:
            active_bool = active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(active=active_bool)
        
        # Filter by visa status
        visa_status = self.request.query_params.get('visa_status', None)
        if visa_status:
            queryset = queryset.filter(visa_status__icontains=visa_status)
        
        # Filter by university
        university = self.request.query_params.get('university', None)
        if university:
            queryset = queryset.filter(university__icontains=university)
        
        # Filter by major
        major = self.request.query_params.get('major', None)
        if major:
            queryset = queryset.filter(major__icontains=major)
        
        # Search by name or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                django_models.Q(first_name__icontains=search) |
                django_models.Q(last_name__icontains=search) |
                django_models.Q(email__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        return ProfileSerializer


class ClientProfileList(generics.ListCreateAPIView):
    """
    GET /api/clients/profiles/ - List CLIENT profiles with detailed information
    POST /api/clients/profiles/ - Create a new client profile
    
    Returns detailed profile information for CLIENTS ONLY (excludes recruiters).
    Includes personal details, education, visa status, assignment status, and recruiter info.
    
    Query Parameters:
        - active: Filter by active status (true/false)
        - has_recruiter: Filter by whether client has assigned recruiter (true/false)
        - visa_status: Filter by visa status (F1-OPT, H1B, etc.)
        - university: Filter by university name (partial match)
        - major: Filter by major (partial match)
        - search: Search by name or email
    
    Permission: Admin only
    
    Example:
        GET /api/clients/profiles/
        GET /api/clients/profiles/?active=true&visa_status=F1-OPT
        GET /api/clients/profiles/?has_recruiter=false
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter to show only client profiles (exclude recruiter profiles)"""
        queryset = Profile.objects.select_related('user').exclude(
            recruiter_profile__isnull=False
        ).order_by('-id')
        
        # Filter by active status
        active = self.request.query_params.get('active', None)
        if active is not None:
            active_bool = active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(active=active_bool)
        
        # Filter by whether profile has assigned recruiter
        has_recruiter = self.request.query_params.get('has_recruiter', None)
        if has_recruiter is not None:
            if has_recruiter.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(assignment__recruiter__isnull=False)
            else:
                queryset = queryset.filter(assignment__recruiter__isnull=True)
        
        # Filter by visa status
        visa_status = self.request.query_params.get('visa_status', None)
        if visa_status:
            queryset = queryset.filter(visa_status__icontains=visa_status)
        
        # Filter by university
        university = self.request.query_params.get('university', None)
        if university:
            queryset = queryset.filter(university__icontains=university)
        
        # Filter by major
        major = self.request.query_params.get('major', None)
        if major:
            queryset = queryset.filter(major__icontains=major)
        
        # Search by name or email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                django_models.Q(first_name__icontains=search) |
                django_models.Q(last_name__icontains=search) |
                django_models.Q(email__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        return ProfileSerializer

class ProfileRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    lookup_field = 'id'  # Profile.id is the UUID primary key
    parser_classes = [MultiPartParser, FormParser]

class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=RegistrationSerializer,
        responses={201: openapi.Response('Created')}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        
        # Send welcome email to user
        self._send_welcome_email_to_user(profile)
        
        # Send notification email to admin
        self._send_notification_to_admin(profile)
        
        return Response({
            'message': 'User registered successfully. Please check your email for further instructions.',
            'profile_id': str(profile.id)  # Profile.id is the UUID primary key
        }, status=status.HTTP_201_CREATED)
    
    def _send_welcome_email_to_user(self, profile):
        """Send welcome email to newly registered user"""
        try:
            from utils.email_service import EmailService, UserRegistrationEmailTemplate
            
            user_data = {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'email': profile.email,
                'phone': profile.phone,
                'university': profile.university,
                'degree': profile.degree,
                'major': profile.major,
                'graduation_date': profile.graduation_date,
                'visa_status': profile.visa_status,
                'opt_end_date': profile.opt_end_date,
                'profile_id': str(profile.id),
                'created_at': profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if hasattr(profile.user, 'date_joined') else 'N/A'
            }
            
            subject, text_content, html_content = UserRegistrationEmailTemplate.get_welcome_email_to_user(user_data)
            EmailService.send_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_emails=[profile.email]
            )
            
        except Exception as e:
            print(f"✗ Failed to send welcome email to user: {str(e)}")
    
    def _send_notification_to_admin(self, profile):
        """Send notification email to operations team about new user registration"""
        try:
            from utils.email_service import EmailService, UserRegistrationEmailTemplate
            from django.conf import settings
            
            user_data = {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'email': profile.email,
                'phone': profile.phone,
                'university': profile.university,
                'degree': profile.degree,
                'major': profile.major,
                'graduation_date': profile.graduation_date,
                'visa_status': profile.visa_status,
                'opt_end_date': profile.opt_end_date,
                'profile_id': str(profile.id),
                'created_at': profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if hasattr(profile.user, 'date_joined') else 'N/A'
            }
            
            subject, text_content, html_content = UserRegistrationEmailTemplate.get_admin_notification_email(user_data)
            operations_email = getattr(settings, 'OPERATIONS_EMAIL', DEFAULT_OPERATIONS_EMAIL)
            
            EmailService.send_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_emails=[operations_email]
            )
            
        except Exception as e:
            print(f"✗ Failed to send notification email to admin: {str(e)}")


class InterestSubmissionCreateView(generics.CreateAPIView):
    """Public interest form endpoint: accepts candidate interest submissions without creating a user account."""
    serializer_class = InterestSubmissionSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Submit candidate interest form",
        request_body=InterestSubmissionSerializer,
        responses={201: openapi.Response('Created')}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Save the interest submission and send email notification to operations team."""
        instance = serializer.save()
        self._send_notification_email(instance)

    def _send_notification_email(self, instance):
        """Send email notification to operations team about new interest submission."""
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            subject = f'🎯 New Interest Submission - {instance.first_name} {instance.last_name}'
            text_content = self._generate_text_email(instance)
            html_content = self._generate_html_email(instance)
            
            operations_email = getattr(settings, 'OPERATIONS_EMAIL', DEFAULT_OPERATIONS_EMAIL)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hyrind.com')
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[operations_email]
            )
            
            email.attach_alternative(html_content, "text/html")
            self._attach_resume_if_present(email, instance)
            
            email.send(fail_silently=True)
            print(f"✓ Sent  email notification to {operations_email}")
            
        except Exception as e:
            print(f"✗ Failed to send email notification: {str(e)}")

    def _generate_text_email(self, instance):
        """Generate plain text email content."""
        return f"""
New Interest Form Submission Received

Candidate Information:
Name: {instance.first_name} {instance.last_name}
Email: {instance.email}
Phone: {instance.phone}

Education:
University: {instance.university}
Degree: {instance.degree}
Major: {instance.major}
Graduation Date: {instance.graduation_date}

Visa & Employment:
Visa Status: {instance.visa_status}
OPT End Date: {instance.opt_end_date or 'N/A'}

Additional Information:
Referral Source: {instance.referral_source or 'N/A'}
LinkedIn: {instance.linkedin_url or 'N/A'}
GitHub: {instance.github_url or 'N/A'}
Additional Notes: {instance.additional_notes or 'N/A'}

Resume: {'Attached' if instance.resume_file else 'Not provided'}
Submitted At: {instance.created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _generate_html_email(self, instance):
        """Generate HTML email content."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                    margin: -30px -30px 30px -30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .header p {{
                    margin: 5px 0 0 0;
                    opacity: 0.9;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #667eea;
                    margin-bottom: 15px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #667eea;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    background-color: #fff;
                }}
                td {{
                    padding: 12px;
                    border: 1px solid #e0e0e0;
                }}
                td:first-child {{
                    font-weight: 600;
                    background-color: #f8f9fa;
                    width: 35%;
                    color: #495057;
                }}
                td:last-child {{
                    background-color: #ffffff;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 2px 6px;
                    border-radius: 3px;
                }}
                .link {{
                    color: #667eea;
                    text-decoration: none;
                }}
                .link:hover {{
                    text-decoration: underline;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    font-size: 12px;
                    color: #6c757d;
                    text-align: center;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                .badge-success {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                .badge-warning {{
                    background-color: #fff3cd;
                    color: #856404;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🎯 New Interest Form Submission</h1>
                    <p>Submission received on {instance.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>

                <div class="section">
                    <div class="section-title">👤 Candidate Information</div>
                    <table>
                        <tr>
                            <td>Full Name</td>
                            <td><strong>{instance.first_name} {instance.last_name}</strong></td>
                        </tr>
                        <tr>
                            <td>Email Address</td>
                            <td><a href="mailto:{instance.email}" class="link">{instance.email}</a></td>
                        </tr>
                        <tr>
                            <td>Phone Number</td>
                            <td><a href="tel:{instance.phone}" class="link">{instance.phone}</a></td>
                        </tr>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">🎓 Education Details</div>
                    <table>
                        <tr>
                            <td>University</td>
                            <td>{instance.university}</td>
                        </tr>
                        <tr>
                            <td>Degree</td>
                            <td>{instance.degree}</td>
                        </tr>
                        <tr>
                            <td>Major</td>
                            <td>{instance.major}</td>
                        </tr>
                        <tr>
                            <td>Graduation Date</td>
                            <td>{instance.graduation_date}</td>
                        </tr>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">🌍 Visa & Employment Status</div>
                    <table>
                        <tr>
                            <td>Visa Status</td>
                            <td><span class="badge badge-warning">{instance.visa_status}</span></td>
                        </tr>
                        <tr>
                            <td>OPT End Date</td>
                            <td>{instance.opt_end_date if instance.opt_end_date else '<span style="color: #6c757d;">N/A</span>'}</td>
                        </tr>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">📋 Additional Information</div>
                    <table>
                        <tr>
                            <td>Referral Source</td>
                            <td>{instance.referral_source if instance.referral_source else '<span style="color: #6c757d;">Not provided</span>'}</td>
                        </tr>
                        <tr>
                            <td>LinkedIn Profile</td>
                            <td>
                                {f'<a href="{instance.linkedin_url}" class="link" target="_blank">{instance.linkedin_url}</a>' if instance.linkedin_url else '<span style="color: #6c757d;">Not provided</span>'}
                            </td>
                        </tr>
                        <tr>
                            <td>GitHub Profile</td>
                            <td>
                                {f'<a href="{instance.github_url}" class="link" target="_blank">{instance.github_url}</a>' if instance.github_url else '<span style="color: #6c757d;">Not provided</span>'}
                            </td>
                        </tr>
                        <tr>
                            <td>Resume</td>
                            <td>
                                {'<span class="badge badge-success">✓ Attached to this email</span>' if instance.resume_file else '<span style="color: #6c757d;">Not provided</span>'}
                            </td>
                        </tr>
                        <tr>
                            <td>Additional Notes</td>
                            <td>{instance.additional_notes if instance.additional_notes else '<span style="color: #6c757d;">None</span>'}</td>
                        </tr>
                    </table>
                </div>

                <div class="footer">
                    <p>This is an automated notification from the Hyrind Interest Form System</p>
                    <p>Submission ID: {instance.id}</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _attach_resume_if_present(self, email, instance):
        """Attach resume file to email if present."""
        if instance.resume_file:
            try:
                email.attach_file(instance.resume_file.path)
                print(f"Attached resume file: {instance.resume_file.name}")
            except Exception as e:
                print(f"Could not attach resume file: {str(e)}")


class ContactCreateView(generics.CreateAPIView):
    """
    Public contact form endpoint: accepts contact messages without authentication.
    Sends email notification to operations team and stores in database.
    """
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Submit contact form message",
        operation_summary="Contact Us Form",
        request_body=ContactSerializer,
        responses={
            201: openapi.Response('Contact message submitted successfully', ContactSerializer),
            400: openapi.Response('Validation error')
        },
        tags=['Contact']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Save the contact message and send email notification to operations team."""
        instance = serializer.save()
        self._send_notification_email(instance)

    def _send_notification_email(self, instance):
        """Send email notification to operations team about new contact message."""
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            subject = f'📧 New Contact Message - {instance.full_name}'
            text_content = self._generate_text_email(instance)
            html_content = self._generate_html_email(instance)
            
            operations_email = getattr(settings, 'OPERATIONS_EMAIL', DEFAULT_OPERATIONS_EMAIL)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hyrind.com')
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[operations_email],
                reply_to=[instance.email]  # Allow easy reply to the contact
            )
            
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=True)
            print(f"✓ Sent contact email notification to {operations_email}")
            
        except Exception as e:
            print(f"✗ Failed to send contact email notification: {str(e)}")

    def _generate_text_email(self, instance):
        """Generate plain text email content."""
        return f"""
New Contact Form Message Received

Contact Information:
Name: {instance.full_name}
Email: {instance.email}
Phone: {instance.phone}

Message:
{instance.message}

---
Submitted At: {instance.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Contact ID: {instance.id}

Reply to this message directly or contact {instance.email}
"""

    def _generate_html_email(self, instance):
        """Generate HTML email content."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                    margin: -30px -30px 30px -30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .header p {{
                    margin: 5px 0 0 0;
                    opacity: 0.9;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #667eea;
                    margin-bottom: 15px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #667eea;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    background-color: #fff;
                }}
                td {{
                    padding: 12px;
                    border: 1px solid #e0e0e0;
                }}
                td:first-child {{
                    font-weight: 600;
                    background-color: #f8f9fa;
                    width: 35%;
                    color: #495057;
                }}
                td:last-child {{
                    background-color: #ffffff;
                }}
                .message-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 4px;
                    font-size: 14px;
                    line-height: 1.8;
                    color: #333;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                .link {{
                    color: #667eea;
                    text-decoration: none;
                }}
                .link:hover {{
                    text-decoration: underline;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    font-size: 12px;
                    color: #6c757d;
                    text-align: center;
                }}
                .reply-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .reply-button:hover {{
                    opacity: 0.9;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>📧 New Contact Message</h1>
                    <p>Message received on {instance.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>

                <div class="section">
                    <div class="section-title">👤 Contact Information</div>
                    <table>
                        <tr>
                            <td>Full Name</td>
                            <td><strong>{instance.full_name}</strong></td>
                        </tr>
                        <tr>
                            <td>Email Address</td>
                            <td><a href="mailto:{instance.email}" class="link">{instance.email}</a></td>
                        </tr>
                        <tr>
                            <td>Phone Number</td>
                            <td><a href="tel:{instance.phone}" class="link">{instance.phone}</a></td>
                        </tr>
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">💬 Message</div>
                    <div class="message-box">{instance.message}</div>
                </div>

                <div style="text-align: center;">
                    <a href="mailto:{instance.email}?subject=Re: Your Contact Message" class="reply-button">
                        Reply to {instance.full_name}
                    </a>
                </div>

                <div class="footer">
                    <p>This is an automated notification from the Hyrind Contact Form System</p>
                    <p>Contact ID: {instance.id} | We usually reply within 24 hours</p>
                </div>
            </div>
        </body>
        </html>
        """


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

class AdminProfileView(generics.RetrieveAPIView):
    """
    Admin endpoint to get authenticated admin's profile.
    Requires admin/staff user.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Get authenticated admin's profile information (admin only)",
        operation_summary="Get Admin Profile",
        responses={
            200: ProfileSerializer,
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def get(self, request, *args, **kwargs):
        """Get authenticated admin's profile"""
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            # Create a profile for admin user if it doesn't exist
            profile = Profile.objects.create(
                user=request.user,
                first_name=request.user.first_name or '',
                last_name=request.user.last_name or '',
                email=request.user.email,
                phone='',
                active=True  # Admin profiles are active by default
            )

        # Ensure serializer is assigned for both existing and newly-created profiles
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrentUserProfileView(generics.RetrieveAPIView):
    """
    Endpoint for authenticated users to retrieve their own profile.
    Accessible to any logged-in user (both regular users and admins).
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get the authenticated user's own profile information",
        operation_summary="Get Current User Profile",
        responses={
            200: ProfileSerializer,
            401: "Unauthorized - Authentication required",
            404: "Profile not found for authenticated user"
        },
        tags=['User']
    )
    def get(self, request, *args, **kwargs):
        """Get authenticated user's profile"""
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            # For regular users, create a profile if it doesn't exist
            profile = Profile.objects.create(
                user=request.user,
                first_name=request.user.first_name or '',
                last_name=request.user.last_name or '',
                email=request.user.email,
                phone='',
                active=True  # Regular user profiles are active by default
            )
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPasswordChangeView(generics.GenericAPIView):
    """
    Admin endpoint to change password.
    Authenticated admin user only.
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Change admin password (admin only)",
        operation_summary="Admin Change Password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['old_password', 'new_password', 'confirm_password'],
            properties={
                'old_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Current password'
                ),
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New password (must be different and meet complexity requirements)'
                ),
                'confirm_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Confirm new password'
                )
            }
        ),
        responses={
            200: openapi.Response('Password changed successfully'),
            400: "Bad Request - Invalid passwords or mismatch",
            401: "Unauthorized - Wrong current password",
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def post(self, request, *args, **kwargs):
        """Change admin password"""
        from django.contrib.auth.password_validation import validate_password
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validate inputs
        if not all([old_password, new_password, confirm_password]):
            return Response(
                {'detail': 'Please provide old_password, new_password, and confirm_password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check old password
        if not request.user.check_password(old_password):
            return Response(
                {'detail': 'Old password is incorrect'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check password match
        if new_password != confirm_password:
            return Response(
                {'detail': 'New passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check password strength
        try:
            validate_password(new_password, user=request.user)
        except Exception as e:
            return Response(
                {'detail': list(e.messages) if hasattr(e, 'messages') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check that new password is different from old
        if old_password == new_password:
            return Response(
                {'detail': 'New password must be different from old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )


class AdminRegisterView(generics.GenericAPIView):
    """
    Admin registration endpoint - create new admin users
    Only accessible by existing admin users
    """
    permission_classes = [IsAdminUser]
    serializer_class = AdminRegistrationSerializer
    
    @swagger_auto_schema(
        operation_description="Register a new admin user (admin only)",
        operation_summary="Admin Registration",
        request_body=AdminRegistrationSerializer,
        responses={
            201: openapi.Response(
                'Admin user created successfully',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'is_superuser': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request - Validation errors",
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def post(self, request, *args, **kwargs):
        """Create a new admin user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        out = {
            'id': user.id,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        return Response(out, status=status.HTTP_201_CREATED)


class CandidateActivateView(generics.GenericAPIView):
    """
    Admin endpoint to APPROVE a candidate registration.
    Changes status from 'open' to 'approved' and grants login access.
    This replaces the old 'activate' concept with proper status workflow.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Approve candidate registration - changes status to 'approved' and grants login access (admin only)",
        operation_summary="Approve Candidate Registration",
        responses={
            200: ProfileSerializer,
            404: "Profile not found",
            403: "Forbidden - Admin access required",
            400: "Invalid status transition"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Approve candidate registration"""
        try:
            profile = Profile.objects.get(id=id)
            
            # Validate status transition
            if profile.registration_status == 'rejected':
                return Response(
                    {'error': 'Cannot approve a rejected candidate. Status is already rejected.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if profile.registration_status == 'closed':
                return Response(
                    {'error': 'Cannot approve a closed candidate. Candidate is already placed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status to 'approved' (this auto-activates login via update_status method)
            profile.update_status('approved', notes=f'Approved by admin: {request.user.email}')
            
            # Send approval/activation email
            try:
                self._send_activation_email_to_user(profile)
            except Exception:
                pass
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate registration approved successfully. Candidate can now login.',
                'data': {
                    'profile': serializer.data,
                    'registration_status': profile.registration_status,
                    'can_login': profile.active,
                    'approved_at': profile.status_updated_at.isoformat() if profile.status_updated_at else None,
                    'approved_by': request.user.email
                }
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _send_activation_email_to_user(self, profile):
        """
        Send activation notification email to the candidate
        
        Args:
            profile: Profile instance of the activated candidate
        """
        try:
            from utils.email_service import EmailService, UserActivationEmailTemplate
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Prepare user data for email template
            user_data = {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'email': profile.email,
                'login_url': 'https://hyrind.com/login',  # Update with your actual frontend URL
            }
            
            # Get email content from template
            subject, text_content, html_content = UserActivationEmailTemplate.get_activation_email(user_data)
            
            # Send email using central EmailService
            success = EmailService.send_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_emails=[profile.email]
            )
            
            if success:
                logger.info(f"Activation email sent successfully to {profile.email}")
            else:
                logger.warning(f"Failed to send activation email to {profile.email}")
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending activation email: {str(e)}")


class CandidateDeactivateView(generics.GenericAPIView):
    """
    Admin endpoint to REJECT a candidate registration.
    Changes status to 'rejected' and revokes login access.
    This replaces the old 'deactivate' concept with proper status workflow.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Reject candidate registration - changes status to 'rejected' and revokes login access (admin only)",
        operation_summary="Reject Candidate Registration",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Optional rejection reason')
            }
        ),
        responses={
            200: ProfileSerializer,
            404: "Profile not found",
            403: "Forbidden - Admin access required",
            400: "Invalid status transition"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Reject candidate registration"""
        try:
            profile = Profile.objects.get(id=id)
            rejection_reason = request.data.get('reason', 'No reason provided')
            
            # Validate status transition
            if profile.registration_status == 'closed':
                return Response(
                    {'error': 'Cannot reject a closed candidate. Candidate is already placed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status to 'rejected' (this auto-deactivates login via update_status method)
            profile.update_status('rejected', notes=f'Rejected by {request.user.email}: {rejection_reason}')
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate registration rejected successfully. Login access revoked.',
                'data': {
                    'profile': serializer.data,
                    'registration_status': profile.registration_status,
                    'can_login': profile.active,
                    'rejected_at': profile.status_updated_at.isoformat() if profile.status_updated_at else None,
                    'rejected_by': request.user.email,
                    'rejection_reason': rejection_reason
                }
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CandidateMarkPlacedView(generics.GenericAPIView):
    """
    Admin endpoint to mark a candidate as PLACED (Closed status).
    This indicates the candidate has been successfully placed in a job.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Mark candidate as placed/closed - indicates successful job placement (admin only)",
        operation_summary="Mark Candidate as Placed",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'placement_details': openapi.Schema(type=openapi.TYPE_STRING, description='Optional placement details (company, position, etc.)')
            }
        ),
        responses={
            200: ProfileSerializer,
            404: "Profile not found",
            403: "Forbidden - Admin access required",
            400: "Invalid status transition"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Mark candidate as placed"""
        try:
            profile = Profile.objects.get(id=id)
            placement_details = request.data.get('placement_details', 'Successfully placed')
            
            # Validate status transition - can only mark as placed if candidate is assigned
            if profile.registration_status not in ['assigned', 'ready_to_assign']:
                return Response(
                    {'error': f'Cannot mark candidate as placed. Current status: {profile.registration_status}. Only assigned candidates can be marked as placed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status to 'closed' (successfully placed)
            profile.update_status('closed', notes=f'Placed by {request.user.email}: {placement_details}')
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate marked as placed successfully. Status set to closed.',
                'data': {
                    'profile': serializer.data,
                    'registration_status': profile.registration_status,
                    'can_login': profile.active,
                    'placed_at': profile.status_updated_at.isoformat() if profile.status_updated_at else None,
                    'placed_by': request.user.email,
                    'placement_details': placement_details
                }
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# PASSWORD RESET VIEWS
# ============================================================================


class CandidateApproveView(generics.GenericAPIView):
    """
    Admin endpoint to approve a candidate registration.
    Changes status from 'open' to 'approved' - candidate can now proceed to payment.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Approve candidate registration (admin only)",
        operation_summary="Approve Candidate",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Admin approval notes (optional)')
            }
        ),
        responses={
            200: ProfileSerializer,
            400: "Invalid status transition",
            404: "Profile not found",
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Approve a candidate registration"""
        try:
            profile = Profile.objects.get(id=id)
            notes = request.data.get('notes', '')
            
            # Validate status transition
            if profile.registration_status not in ['open', 'rejected']:
                return Response({
                    'success': False,
                    'message': f'Cannot approve candidate with status: {profile.get_registration_status_display()}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update status to approved
            profile.update_status('approved', notes=notes or 'Registration approved by admin')
            
            # Send approval email to candidate
            try:
                self._send_approval_email(profile)
            except Exception:
                pass
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate approved successfully. They can now proceed to payment.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _send_approval_email(self, profile):
        """Send approval notification email to candidate"""
        from utils.email_service import EmailService
        
        subject = f"✅ Application Approved - Next Steps"
        text_content = f"""
Dear {profile.first_name},

Your registration has been approved! 

Next Steps:
1. Complete payment to activate your account
2. Once payment is confirmed, you'll be assigned to a recruiter
3. Your recruiter will guide you through the job placement process

Please log in to your dashboard to proceed with payment.

Best regards,
Hyrind Team
        """
        
        html_content = f"""
<h2>Application Approved!</h2>
<p>Dear {profile.first_name},</p>
<p>Great news! Your registration has been approved.</p>
<h3>Next Steps:</h3>
<ol>
    <li>Complete payment to activate your account</li>
    <li>Once payment is confirmed, you'll be assigned to a recruiter</li>
    <li>Your recruiter will guide you through the job placement process</li>
</ol>
<p>Please log in to your dashboard to proceed with payment.</p>
<p>Best regards,<br>Hyrind Team</p>
        """
        
        EmailService.send_email(
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            to_emails=[profile.email]
        )


class CandidateRejectView(generics.GenericAPIView):
    """
    Admin endpoint to reject a candidate registration.
    Changes status to 'rejected' - candidate will be notified.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Reject candidate registration (admin only)",
        operation_summary="Reject Candidate",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['reason'],
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Reason for rejection')
            }
        ),
        responses={
            200: ProfileSerializer,
            400: "Bad Request - Reason required",
            404: "Profile not found",
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Reject a candidate registration"""
        try:
            profile = Profile.objects.get(id=id)
            reason = request.data.get('reason', '').strip()
            
            if not reason:
                return Response({
                    'success': False,
                    'message': 'Rejection reason is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update status to rejected
            profile.update_status('rejected', notes=f'Rejected: {reason}')
            
            # Deactivate user account
            try:
                profile.user.is_active = False
                profile.user.save(update_fields=['is_active'])
                profile.active = False
                profile.save(update_fields=['active'])
            except Exception:
                pass
            
            # Send rejection email to candidate
            try:
                self._send_rejection_email(profile, reason)
            except Exception:
                pass
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate rejected.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _send_rejection_email(self, profile, reason):
        """Send rejection notification email to candidate"""
        from utils.email_service import EmailService
        
        subject = f"Application Status Update"
        text_content = f"""
Dear {profile.first_name},

Thank you for your interest in Hyrind's services.

After careful review, we regret to inform you that we cannot proceed with your application at this time.

Reason: {reason}

If you have any questions or would like to discuss this further, please don't hesitate to contact us.

Best regards,
Hyrind Team
        """
        
        html_content = f"""
<h2>Application Status Update</h2>
<p>Dear {profile.first_name},</p>
<p>Thank you for your interest in Hyrind's services.</p>
<p>After careful review, we regret to inform you that we cannot proceed with your application at this time.</p>
<p><strong>Reason:</strong> {reason}</p>
<p>If you have any questions or would like to discuss this further, please don't hesitate to contact us.</p>
<p>Best regards,<br>Hyrind Team</p>
        """
        
        EmailService.send_email(
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            to_emails=[profile.email]
        )


class CandidatePlacedView(generics.GenericAPIView):
    """
    Admin/Recruiter endpoint to mark a candidate as placed (job found).
    Changes status to 'closed' - successful placement completion.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Mark candidate as successfully placed (admin/recruiter only)",
        operation_summary="Mark Candidate Placed",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='Company where placed'),
                'position': openapi.Schema(type=openapi.TYPE_STRING, description='Job position/title'),
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Additional placement notes')
            }
        ),
        responses={
            200: ProfileSerializer,
            400: "Invalid status transition",
            404: "Profile not found",
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Mark candidate as placed"""
        try:
            profile = Profile.objects.get(id=id)
            company_name = request.data.get('company_name', '').strip()
            position = request.data.get('position', '').strip()
            notes = request.data.get('notes', '').strip()
            
            # Build placement notes
            placement_info = []
            if company_name:
                placement_info.append(f'Company: {company_name}')
            if position:
                placement_info.append(f'Position: {position}')
            if notes:
                placement_info.append(f'Notes: {notes}')
            
            placement_notes = 'Successfully placed. ' + ' | '.join(placement_info) if placement_info else 'Successfully placed'
            
            # Update status to closed
            profile.update_status('closed', notes=placement_notes)
            
            # Update assignment status if exists
            try:
                assignment = profile.assignment
                assignment.status = 'placed'
                assignment.save(update_fields=['status'])
            except Exception:
                pass
            
            # Send congratulations email to candidate
            try:
                self._send_placement_email(profile, company_name, position)
            except Exception:
                pass
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate marked as successfully placed!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _send_placement_email(self, profile, company_name='', position=''):
        """Send congratulations email to placed candidate"""
        from utils.email_service import EmailService
        
        subject = f"🎉 Congratulations on Your Placement!"
        
        placement_details = ''
        if company_name and position:
            placement_details = f"\n\nCompany: {company_name}\nPosition: {position}"
        elif company_name:
            placement_details = f"\n\nCompany: {company_name}"
        elif position:
            placement_details = f"\n\nPosition: {position}"
        
        text_content = f"""
Dear {profile.first_name},

Congratulations! We're thrilled to inform you that you've been successfully placed!{placement_details}

This is a significant milestone in your career journey, and we're proud to have been part of your success story.

We wish you all the best in your new role!

Best regards,
Hyrind Team
        """
        
        html_content = f"""
<h2>🎉 Congratulations on Your Placement!</h2>
<p>Dear {profile.first_name},</p>
<p>Congratulations! We're thrilled to inform you that you've been successfully placed!</p>
{f'<p><strong>Company:</strong> {company_name}<br>' if company_name else ''}
{f'<strong>Position:</strong> {position}</p>' if position else ''}
<p>This is a significant milestone in your career journey, and we're proud to have been part of your success story.</p>
<p>We wish you all the best in your new role!</p>
<p>Best regards,<br>Hyrind Team</p>
        """
        
        EmailService.send_email(
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            to_emails=[profile.email]
        )


# ============================================================================
# PASSWORD RESET VIEWS
# ============================================================================

class PasswordResetRequestView(generics.GenericAPIView):
    """
    POST /api/users/password-reset/request/ - Request password reset (Forgot Password)
    
    Send password reset email to user. This is used on the login page when user
    clicks "Forgot Password". Anyone can request a reset by providing an email.
    
    Request Body:
        {
            "email": "user@example.com"
        }
    
    Response:
        {
            "success": true,
            "message": "If an account exists with this email, you will receive password reset instructions."
        }
    
    Note: For security, we always return success even if email doesn't exist.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    @swagger_auto_schema(
        operation_description="Request password reset link via email (Forgot Password flow)",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                'Reset link sent',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            from .password_reset import generate_reset_token, send_password_reset_email
            uid, token = generate_reset_token(user)
            
            # Construct reset link (frontend URL)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"
            
            # Send email
            send_password_reset_email(user, reset_link)
        
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            pass
        
        # Always return success message
        return Response({
            'success': True,
            'message': 'If an account exists with this email, you will receive password reset instructions.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    POST /api/users/password-reset/confirm/ - Confirm password reset with token
    
    Reset password using the token sent via email. This is called after user
    clicks the reset link in their email and submits new password.
    
    Request Body:
        {
            "uid": "MQ",
            "token": "abc123...",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
    
    Response:
        {
            "success": true,
            "message": "Password has been reset successfully. You can now log in with your new password."
        }
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    @swagger_auto_schema(
        operation_description="Confirm password reset with token from email",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                'Password reset successful',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: 'Invalid or expired token'
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Verify token and get user
        from .password_reset import verify_reset_token
        user = verify_reset_token(uid, token)
        
        if user is None:
            return Response({
                'success': False,
                'message': 'Invalid or expired reset link. Please request a new password reset.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password has been reset successfully. You can now log in with your new password.'
        }, status=status.HTTP_200_OK)


class PasswordChangeView(generics.GenericAPIView):
    """
    POST /api/users/password-change/ - Change password (User Dashboard)
    
    Change password for authenticated user from dashboard settings.
    User must provide current password for verification.
    
    Request Body:
        {
            "current_password": "oldpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
    
    Response:
        {
            "success": true,
            "message": "Password changed successfully"
        }
    
    Permission: Authenticated users only
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    
    @swagger_auto_schema(
        operation_description="Change password for authenticated user (Dashboard flow)",
        request_body=PasswordChangeSerializer,
        responses={
            200: openapi.Response(
                'Password changed successfully',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: 'Validation error'
        }
    )
    def post(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Set new password
        user = request.user
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

# ============================================================================
# CLIENT INTAKE SHEET AND CREDENTIAL SHEET VIEWS
# ============================================================================

@swagger_auto_schema(
    operation_description='Submit a new Client Intake Sheet form. This form collects comprehensive personal, professional, and educational information. Only one intake sheet per user is allowed. Returns 409 if form already exists.',
    operation_summary='Create Client Intake Sheet',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['first_name', 'last_name', 'date_of_birth', 'phone_number', 'email', 'current_address', 'mailing_address', 'visa_status', 'first_entry_us', 'total_years_in_us', 'skilled_in', 'experienced_with'],
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, example='John', description='Candidate first name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, example='Doe', description='Candidate last name'),
            'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, format='date', example='1990-05-15', description='Date of birth in YYYY-MM-DD format'),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, example='+1-555-1234', description='Phone number with country code'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='john@example.com', description='Primary email address'),
            'alternate_email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example='john.alt@example.com', description='Alternate email (optional)'),
            'current_address': openapi.Schema(type=openapi.TYPE_STRING, example='123 Main St, New York, NY 10001', description='Current residential address'),
            'mailing_address': openapi.Schema(type=openapi.TYPE_STRING, example='456 Oak Ave, Los Angeles, CA 90001', description='Mailing address'),
            'visa_status': openapi.Schema(type=openapi.TYPE_STRING, enum=['F1-OPT', 'H1B', 'H4 EAD', 'Green Card', 'US Citizen', 'Other'], example='F1-OPT', description='Current visa/immigration status'),
            'first_entry_us': openapi.Schema(type=openapi.TYPE_STRING, format='date', example='2020-01-15', description='First entry date to USA'),
            'total_years_in_us': openapi.Schema(type=openapi.TYPE_INTEGER, example=4, description='Total years spent in USA'),
            'skilled_in': openapi.Schema(type=openapi.TYPE_STRING, example='Python, Java, SQL, JavaScript', description='Technical skills'),
            'experienced_with': openapi.Schema(type=openapi.TYPE_STRING, example='AWS, Docker, Git, Linux', description='Tools/platforms with experience'),
            'desired_job_role': openapi.Schema(type=openapi.TYPE_STRING, example='Software Engineer, Senior Developer', description='Desired job position(s)'),
            'resume_file': openapi.Schema(type=openapi.TYPE_STRING, format='binary', description='Resume file upload (PDF, DOC, DOCX)'),
        }
    ),
    responses={
        201: openapi.Response(
            'Form submitted successfully',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example='Client intake sheet submitted successfully'),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', example='550e8400-e29b-41d4-a716-446655440000'),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'submission_timestamp': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', example='2024-01-15T10:30:00Z'),
                            'is_editable': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        }
                    )
                }
            )
        ),
        400: openapi.Response('Validation error or profile not found'),
        401: openapi.Response('Authentication required'),
        409: openapi.Response('Form already exists for this user. Use PATCH to update existing form.'),
    },
    tags=['Client Forms']
)
class ClientIntakeSheetCreateView(generics.CreateAPIView):
    """
    POST /api/users/client-intake/ - Create or get client intake sheet
    
    Create a new client intake sheet submission. Only authenticated users can submit.
    If user already has a submitted form, they can update it via the detail endpoint.
    
    Permission: Authenticated users only
    
    Example Request:
        POST /api/users/client-intake/
        {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-05-15",
            "phone_number": "+1-555-1234",
            "email": "john@example.com",
            "alternate_email": "alternate@example.com",
            "current_address": "123 Main St, New York, NY 10001",
            "mailing_address": "456 Oak Ave, Los Angeles, CA 90001",
            "visa_status": "F1-OPT",
            "first_entry_us": "2020-01-15",
            "total_years_in_us": 4,
            ...
        }
    """
    queryset = ClientIntakeSheet.objects.all()
    serializer_class = ClientIntakeSheetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """Create or update client intake sheet"""
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found. Please complete your registration first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already has an intake sheet
        try:
            intake_sheet = ClientIntakeSheet.objects.get(profile=profile)
            # If exists, use detail view update instead
            return Response({
                'message': 'Client intake sheet already exists. Use PATCH to update.',
                'intake_sheet_id': str(intake_sheet.id),
                'url': f'/api/users/client-intake/{intake_sheet.id}/'
            }, status=status.HTTP_409_CONFLICT)
        except ClientIntakeSheet.DoesNotExist:
            pass
        
        # Create new intake sheet
        request.data._mutable = True
        request.data['profile'] = str(profile.id)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Send confirmation email
        self._send_submission_email(serializer.instance, request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Client intake sheet submitted successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def _send_submission_email(self, intake_sheet, user):
        """Send confirmation email to user after submission"""
        try:
            from utils.email_service import EmailService
            
            subject = '✅ Client Intake Form - Submission Confirmed'
            text_content = f"""
Dear {intake_sheet.profile.first_name},

Thank you for submitting your client intake form!

We have received your submission and will review your information shortly.
You can view or edit your submission anytime by logging into your dashboard.

Form Details:
- First Name: {intake_sheet.first_name}
- Last Name: {intake_sheet.last_name}
- Visa Status: {intake_sheet.visa_status}
- Submission Date: {intake_sheet.submission_timestamp.strftime('%Y-%m-%d %H:%M:%S') if intake_sheet.submission_timestamp else 'N/A'}
- Form Status: {'Editable' if intake_sheet.is_editable else 'Locked'}

If you need to make any changes, you can edit your form from your dashboard.

Best regards,
Hyrind Team
            """
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
        .footer {{ text-align: center; font-size: 12px; color: #6c757d; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        td {{ padding: 8px; border: 1px solid #dee2e6; }}
        td:first-child {{ font-weight: 600; background-color: #e9ecef; width: 40%; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Intake Form Submitted</h1>
            <p>Your information has been received</p>
        </div>
        <div class="content">
            <p>Dear {intake_sheet.profile.first_name},</p>
            <p>Thank you for submitting your client intake form!</p>
            <p>We have received your submission and will review your information shortly.</p>
            
            <h3>Your Submission Summary:</h3>
            <table>
                <tr><td>First Name</td><td>{intake_sheet.first_name}</td></tr>
                <tr><td>Last Name</td><td>{intake_sheet.last_name}</td></tr>
                <tr><td>Visa Status</td><td>{intake_sheet.visa_status}</td></tr>
                <tr><td>Submission Date</td><td>{intake_sheet.submission_timestamp.strftime('%B %d, %Y') if intake_sheet.submission_timestamp else 'N/A'}</td></tr>
                <tr><td>Editable</td><td>{'Yes' if intake_sheet.is_editable else 'No'}</td></tr>
            </table>
            
            <p>You can view or edit your submission anytime by logging into your dashboard.</p>
            <a href="https://hyrind.com/dashboard" class="button">View Your Dashboard</a>
        </div>
        <div class="footer">
            <p>© 2024 Hyrind. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            EmailService.send_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_emails=[user.email]
            )
        except Exception as e:
            print(f"Failed to send intake form confirmation email: {str(e)}")


@swagger_auto_schema(
    operation_summary="Retrieve or update client intake sheet",
    operation_description="Retrieve, update, or partially update a client intake sheet. Only the owner or admin can access/modify.",
    responses={
        200: openapi.Response('Success', ClientIntakeSheetSerializer),
        400: 'Bad request',
        401: 'Authentication required',
        403: 'Forbidden',
        404: 'Not found'
    },
    tags=["Client Forms"]
)
class ClientIntakeSheetRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET /api/users/client-intake/{id}/ - Get client intake sheet
    PUT /api/users/client-intake/{id}/ - Full update client intake sheet
    PATCH /api/users/client-intake/{id}/ - Partial update client intake sheet
    
    Retrieve, update, or partially update a client intake sheet.
    Only the user who created the form or admin can access/modify it.
    
    Permission: Authenticated users only (owner or admin)
    """
    queryset = ClientIntakeSheet.objects.all()
    serializer_class = ClientIntakeSheetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'
    
    def get_object(self):
        """Get the client intake sheet, ensuring user permission"""
        obj = super().get_object()
        
        # Check if user is the owner or admin
        if obj.profile.user != self.request.user and not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message='You do not have permission to access this form.'
            )
        
        return obj
    
    def update(self, request, *args, **kwargs):
        """Update intake sheet and send notification"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check if form is editable
        if not instance.is_editable and not request.user.is_staff:
            return Response(
                {'error': 'This form is locked and cannot be edited.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Client intake form updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    operation_summary="Create credential sheet",
    operation_description="Create a new credential sheet for the authenticated user. If a form already exists, returns a 409 with the form URL.",
    request_body=CredentialSheetSerializer,
    responses={
        201: openapi.Response('Created', CredentialSheetSerializer),
        400: 'Bad request',
        401: 'Authentication required',
        409: 'Form already exists for this user.'
    },
    tags=["Client Forms"]
)
class CredentialSheetCreateView(generics.CreateAPIView):
    """
    POST /api/users/credential-sheet/ - Create credential sheet
    
    Create a new credential sheet with job platform login information.
    Only authenticated users can submit.
    
    Permission: Authenticated users only
    
    Example Request:
        POST /api/users/credential-sheet/
        {
            "full_name": "John Doe",
            "personal_email": "john.personal@example.com",
            "phone_number": "+1-555-1234",
            "location": "New York, NY",
            "bachelor_graduation_date": "2020-05-15",
            "masters_graduation_date": "2022-05-15",
            "opt_start_date": "2022-06-01",
            "opt_offer_letter_submitted": "Yes",
            "opt_offer_letter_file": <file>,
            "preferred_job_roles": "Software Engineer, Data Scientist",
            "preferred_locations": "New York, San Francisco, Remote",
            "linkedin_username": "johndoe",
            "linkedin_password": "encrypted_password",
            ...
        }
    """
    queryset = CredentialSheet.objects.all()
    serializer_class = CredentialSheetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """Create credential sheet"""
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found. Please complete your registration first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already has a credential sheet
        try:
            credential_sheet = CredentialSheet.objects.get(profile=profile)
            # If exists, use detail view update instead
            return Response({
                'message': 'Credential sheet already exists. Use PATCH to update.',
                'credential_sheet_id': str(credential_sheet.id),
                'url': f'/api/users/credential-sheet/{credential_sheet.id}/'
            }, status=status.HTTP_409_CONFLICT)
        except CredentialSheet.DoesNotExist:
            pass
        
        # Validate and create credential sheet
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save with profile relationship
        credential_sheet = serializer.save(profile=profile)
        
        # Send confirmation email (without passwords)
        self._send_submission_email(credential_sheet, request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Credential sheet submitted successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    def _send_submission_email(self, credential_sheet, user):
        """Send confirmation email to user after credential submission"""
        try:
            from utils.email_service import EmailService
            
            subject = '✅ Credential Sheet - Submission Confirmed'
            text_content = f"""
Dear {credential_sheet.profile.first_name},

Thank you for submitting your credential sheet!

We have securely received your platform credentials and job preferences.
Your login information is encrypted and will only be used to assist with your job search.

Submission Details:
- Full Name: {credential_sheet.full_name}
- Email: {credential_sheet.personal_email}
- Location: {credential_sheet.location}
- Preferred Roles: {credential_sheet.preferred_job_roles}
- Submission Date: {credential_sheet.submission_timestamp.strftime('%Y-%m-%d %H:%M:%S') if credential_sheet.submission_timestamp else 'N/A'}

Your credentials are encrypted and secure. You can update them anytime from your dashboard.

Best regards,
Hyrind Team
            """
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; }}
        .footer {{ text-align: center; font-size: 12px; color: #6c757d; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        td {{ padding: 8px; border: 1px solid #dee2e6; }}
        td:first-child {{ font-weight: 600; background-color: #e9ecef; width: 40%; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 15px; }}
        .security-notice {{ background: #e7f5ff; border: 1px solid #a5d8ff; padding: 12px; border-radius: 4px; margin: 15px 0; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Credential Sheet Submitted</h1>
            <p>Your credentials have been securely received</p>
        </div>
        <div class="content">
            <p>Dear {credential_sheet.profile.first_name},</p>
            <p>Thank you for submitting your credential sheet!</p>
            
            <div class="security-notice">
                🔒 <strong>Security Notice:</strong> Your login credentials are encrypted with industry-standard security protocols and will only be used to assist with your job search.
            </div>
            
            <h3>Your Submission Summary:</h3>
            <table>
                <tr><td>Full Name</td><td>{credential_sheet.full_name}</td></tr>
                <tr><td>Email</td><td>{credential_sheet.personal_email}</td></tr>
                <tr><td>Location</td><td>{credential_sheet.location}</td></tr>
                <tr><td>Preferred Roles</td><td>{credential_sheet.preferred_job_roles}</td></tr>
                <tr><td>Submission Date</td><td>{credential_sheet.submission_timestamp.strftime('%B %d, %Y') if credential_sheet.submission_timestamp else 'N/A'}</td></tr>
            </table>
            
            <p>You can update your credentials anytime from your dashboard.</p>
            <a href="https://hyrind.com/dashboard" class="button">View Your Dashboard</a>
        </div>
        <div class="footer">
            <p>© 2024 Hyrind. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            EmailService.send_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_emails=[user.email]
            )
        except Exception as e:
            print(f"Failed to send credential sheet confirmation email: {str(e)}")


@swagger_auto_schema(
    operation_summary="Retrieve or update credential sheet",
    operation_description="Retrieve, update, or partially update a credential sheet. Only the owner or admin can access/modify.",
    responses={
        200: openapi.Response('Success', CredentialSheetSerializer),
        400: 'Bad request',
        401: 'Authentication required',
        403: 'Forbidden',
        404: 'Not found'
    },
    tags=["Client Forms"]
)
class CredentialSheetRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET /api/users/credential-sheet/{id}/ - Get credential sheet
    PUT /api/users/credential-sheet/{id}/ - Full update credential sheet
    PATCH /api/users/credential-sheet/{id}/ - Partial update credential sheet
    
    Retrieve, update, or partially update a credential sheet.
    Only the user who created the form or admin can access/modify it.
    
    Permission: Authenticated users only (owner or admin)
    """
    queryset = CredentialSheet.objects.all()
    serializer_class = CredentialSheetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'
    
    def get_object(self):
        """Get the credential sheet, ensuring user permission"""
        obj = super().get_object()
        
        # Check if user is the owner or admin
        if obj.profile.user != self.request.user and not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message='You do not have permission to access this form.'
            )
        
        return obj
    
    def update(self, request, *args, **kwargs):
        """Update credential sheet"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check if form is editable
        if not instance.is_editable and not request.user.is_staff:
            return Response(
                {'error': 'This form is locked and cannot be edited.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Credential sheet updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    operation_summary="Get forms completion status",
    operation_description="Check if the authenticated user has completed both required forms (Client Intake Sheet and Credential Sheet). Returns completion status and form details.",
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'client_intake_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'credential_sheet_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'all_forms_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'profile_id': openapi.Schema(type=openapi.TYPE_STRING),
                'forms': openapi.Schema(type=openapi.TYPE_OBJECT)
            }
        )),
        401: 'Authentication required',
        404: 'Profile not found'
    },
    tags=["Client Forms"]
)
class FormsCompletionStatusView(generics.GenericAPIView):
    """
    GET /api/users/forms-completion-status/ - Get form completion status
    
    Check if authenticated user has completed both required forms:
    - Client Intake Sheet
    - Credential Sheet
    
    Returns completion status and links to forms.
    
    Permission: Authenticated users only
    
    Response:
        {
            "client_intake_completed": true/false,
            "credential_sheet_completed": true/false,
            "all_forms_completed": true/false,
            "profile_id": "uuid",
            "forms": {
                "client_intake": {
                    "completed": true/false,
                    "id": "uuid (if exists)",
                    "submitted_at": "2024-01-15T10:30:00Z (if exists)",
                    "editable": true/false (if exists)
                },
                "credential_sheet": {
                    "completed": true/false,
                    "id": "uuid (if exists)",
                    "submitted_at": "2024-01-15T10:30:00Z (if exists)",
                    "editable": true/false (if exists)
                }
            }
        }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return a dummy serializer for Swagger schema generation"""
        # This view doesn't actually use a serializer, but we need to provide one for schema generation
        from rest_framework import serializers
        
        class FormsStatusSerializer(serializers.Serializer):
            client_intake_completed = serializers.BooleanField()
            credential_sheet_completed = serializers.BooleanField()
            all_forms_completed = serializers.BooleanField()
            profile_id = serializers.CharField()
            
        return FormsStatusSerializer
    
    def get(self, request):
        """Get form completion status"""
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check intake sheet
        intake_exists = ClientIntakeSheet.objects.filter(profile=profile).exists()
        intake_data = None
        if intake_exists:
            intake = ClientIntakeSheet.objects.get(profile=profile)
            intake_data = {
                'id': str(intake.id),
                'submitted_at': intake.submission_timestamp.isoformat() if intake.submission_timestamp else None,
                'editable': intake.is_editable
            }
        
        # Check credential sheet
        credential_exists = CredentialSheet.objects.filter(profile=profile).exists()
        credential_data = None
        if credential_exists:
            credential = CredentialSheet.objects.get(profile=profile)
            credential_data = {
                'id': str(credential.id),
                'submitted_at': credential.submission_timestamp.isoformat() if credential.submission_timestamp else None,
                'editable': credential.is_editable
            }
        
        return Response({
            'client_intake_completed': intake_exists,
            'credential_sheet_completed': credential_exists,
            'all_forms_completed': intake_exists and credential_exists,
            'profile_id': str(profile.id),
            'forms': {
                'client_intake': {
                    'completed': intake_exists,
                    **(intake_data or {})
                },
                'credential_sheet': {
                    'completed': credential_exists,
                    **(credential_data or {})
                }
            }
        }, status=status.HTTP_200_OK)