from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


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
from .models import Profile
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    InterestSubmissionSerializer,
    ContactSerializer,
    UserPublicSerializer,
    AdminRegistrationSerializer,
)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [IsAdminUser]

class ProfileList(generics.ListCreateAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]
    
    # Override to prevent Swagger from trying to generate form params from nested serializer
    def get_serializer_class(self):
        # For Swagger introspection, use the base serializer
        # For actual operations, DRF will use ProfileSerializer
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
        return Response({
            'message': 'User registered successfully',
            'profile_id': str(profile.id)  # Profile.id is the UUID primary key
        }, status=status.HTTP_201_CREATED)


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
            
            operations_email = getattr(settings, 'OPERATIONS_EMAIL', 'hyrind.operations@gmail.com')
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
            
            operations_email = getattr(settings, 'OPERATIONS_EMAIL', 'hyrind.operations@gmail.com')
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
        
        # Log the password change
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='admin_password_changed',
                target=f'User:{request.user.id}',
                metadata={'user_id': request.user.id, 'email': request.user.email}
            )
        except Exception:
            pass
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )


class CandidateActivateView(generics.GenericAPIView):
    """
    Admin endpoint to activate a candidate profile.
    Sets the candidate profile as active.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Activate a candidate profile by UUID (admin only)",
        operation_summary="Activate Candidate",
        responses={
            200: ProfileSerializer,
            404: "Profile not found",
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Activate a candidate"""
        try:
            profile = Profile.objects.get(id=id)
        # Prefer toggling the underlying Django User.is_active flag
            try:
                user = profile.user
                user.is_active = True
                user.save(update_fields=['is_active'])
                # mirror on profile for clarity in admin UI
                profile.active = True
                profile.save(update_fields=['active'])
            except Exception:
                # If no linked User, continue and respond
                pass
            
            # Log the activation
            try:
                from audit.utils import log_action
                log_action(
                    actor=request.user,
                    action='candidate_activated',
                    target=f'Profile:{profile.id}',
                    metadata={'email': profile.email, 'name': f'{profile.first_name} {profile.last_name}'}
                )
            except Exception:
                pass
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate activated successfully',
                'data': {
                    'profile': serializer.data,
                    'status': 'active',
                    'is_active': profile.active,  # Use actual DB value
                    'activated_at': profile.user.last_login  # Track when last active
                }
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminRegisterView(generics.CreateAPIView):
    """Create a new admin/staff user. Only existing admin users can call this endpoint.

    Only superusers are allowed to create other superusers; staff users can create staff but not superusers.
    """
    permission_classes = [IsAdminUser]
    serializer_class = None  # Will be set in post()

    @swagger_auto_schema(
        operation_description="Create a new admin/staff user (admin-only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Admin email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Admin password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm password'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name (optional)'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name (optional)'),
                'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Staff status (default: true)'),
                'is_superuser': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Superuser status (default: false)'),
            }
        ),
        responses={201: openapi.Response('Created'), 400: 'Validation error', 403: 'Forbidden'},
        tags=['Admin']
    )
    def post(self, request, *args, **kwargs):
        from .serializers import AdminRegistrationSerializer
        
        # Prevent non-superusers from creating superusers
        is_super = bool(request.data.get('is_superuser'))
        if is_super and not request.user.is_superuser:
            return Response({'detail': 'Only superusers may create superuser accounts.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AdminRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        out = {
            'id': user.id,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        return Response(out, status=status.HTTP_201_CREATED)


class CandidateDeactivateView(generics.GenericAPIView):
    """
    Admin endpoint to deactivate a candidate profile.
    """
    permission_classes = [IsAdminUser]
    queryset = Profile.objects.all()
    lookup_field = 'id'
    serializer_class = ProfileSerializer
    
    @swagger_auto_schema(
        operation_description="Deactivate a candidate profile by UUID (admin only)",
        operation_summary="Deactivate Candidate",
        responses={
            200: ProfileSerializer,
            404: "Profile not found",
            403: "Forbidden - Admin access required"
        },
        tags=['Admin']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Deactivate a candidate"""
        try:
            profile = Profile.objects.get(id=id)
            
            # Toggle underlying Django User.is_active to prevent login
                # Toggle underlying Django User.is_active to prevent login
            try:
                user = profile.user
                user.is_active = False
                user.save(update_fields=['is_active'])
            except Exception:
                pass
            # Mirror on profile
            try:
                profile.active = False
                profile.save(update_fields=['active'])
            except Exception:
                pass
                
                # Log the deactivation
                try:
                    from audit.utils import log_action
                    log_action(
                        actor=request.user,
                        action='candidate_deactivated',
                        target=f'Profile:{profile.id}',
                        metadata={'email': profile.email, 'name': f'{profile.first_name} {profile.last_name}'}
                    )
                except Exception:
                    pass
            
            serializer = self.get_serializer(profile)
            return Response({
                'success': True,
                'message': 'Candidate deactivated successfully',
                'data': {
                    'profile': serializer.data,
                    'status': 'inactive',
                    'is_active': profile.active,  # Use actual DB value
                    'deactivated_at': profile.user.last_login
                }
            }, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
