from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Recruiter, Assignment, RecruiterRegistration
from .serializers import (
    RecruiterSerializer,
    RecruiterDashboardSerializer,
    RecruiterLoginSerializer,
    RecruiterRegistrationSerializer,
    RecruiterUpdateSerializer,
    RecruiterListSerializer,
    RecruiterAdminUpdateSerializer,
    AssignmentSerializer,
    RecruiterRegistrationFormSerializer,
    RecruiterRegistrationFormListSerializer
)
from users.models import Profile
from onboarding.models import Onboarding
from utils.profile_utils import ProfileResolveMixin


# ============================================================================
# RECRUITER AUTHENTICATION & PROFILE ENDPOINTS
# ============================================================================

class RecruiterLoginView(generics.GenericAPIView):
    """
    Recruiter login endpoint.
    Authenticates recruiter and returns JWT tokens and recruiter details.
    """
    serializer_class = RecruiterLoginSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Authenticate recruiter and get JWT tokens",
        operation_summary="Recruiter Login",
        request_body=RecruiterLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'recruiter_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'company_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: "Unauthorized - Invalid credentials"
        },
        tags=['Recruiters - Auth']
    )
    def post(self, request, *args, **kwargs):
        """Authenticate recruiter and return tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Authenticate user
        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(username=user.username, password=password)
            
            if not user_auth:
                return Response(
                    {'detail': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get recruiter
            profile = Profile.objects.get(user=user)
            recruiter = Recruiter.objects.get(user=profile)
            
            # Check if recruiter is active (approved by admin)
            if not recruiter.active:
                return Response(
                    {'detail': 'Your recruiter account is not yet approved. Please contact an administrator.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update last login
            recruiter.last_login = timezone.now()
            recruiter.save(update_fields=['last_login'])
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(recruiter.id),
                    'employee_id': recruiter.employee_id,
                    'name': recruiter.name,
                    'email': recruiter.email,
                    'department': recruiter.get_department_display(),
                    'specialization': recruiter.get_specialization_display(),
                    'status': recruiter.status
                }
            }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RecruiterRegistrationView(generics.CreateAPIView):
    """
    Public endpoint for recruiter registration.
    Creates User, Profile, and Recruiter instances.
    Recruiter account starts as inactive and requires admin approval.
    """
    serializer_class = RecruiterRegistrationSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Register a new internal recruiter account (requires admin approval before activation)",
        operation_summary="Recruiter Registration",
        request_body=RecruiterRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Recruiter account created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'employee_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'department': openapi.Schema(type=openapi.TYPE_STRING),
                        'specialization': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Bad Request - Validation errors"
        },
        tags=['Recruiters - Auth']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recruiter = serializer.save()
        
        # Send welcome email to recruiter
        self._send_welcome_email_to_recruiter(recruiter)
        
        # Send notification email to admin
        self._send_notification_to_admin(recruiter)
        
        return Response({
            'id': str(recruiter.id),
            'employee_id': recruiter.employee_id,
            'name': recruiter.name,
            'email': recruiter.email,
            'department': recruiter.get_department_display(),
            'specialization': recruiter.get_specialization_display(),
            'status': recruiter.status,
            'message': 'Registration successful. Please check your email for further instructions.'
        }, status=status.HTTP_201_CREATED)
    
    def _send_welcome_email_to_recruiter(self, recruiter):
        """Send welcome email to newly registered recruiter"""
        try:
            from utils.email_service import EmailService, RecruiterRegistrationEmailTemplate
            
            recruiter_data = {
                'id': str(recruiter.id),
                'employee_id': recruiter.employee_id,
                'name': recruiter.name,
                'email': recruiter.email,
                'phone': recruiter.phone,
                'department_display': recruiter.get_department_display(),
                'specialization_display': recruiter.get_specialization_display(),
                'date_of_joining': recruiter.date_of_joining,
                'max_clients': recruiter.max_clients,
                'status': recruiter.get_status_display(),
                'created_at': recruiter.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            subject, text_content, html_content = RecruiterRegistrationEmailTemplate.get_welcome_email_to_recruiter(recruiter_data)
            EmailService.send_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_emails=[recruiter.email]
            )
            
        except Exception as e:
            print(f"✗ Failed to send welcome email to recruiter: {str(e)}")
    
    def _send_notification_to_admin(self, recruiter):
        """Send notification email to operations team about new recruiter registration"""
        try:
            from utils.email_service import EmailService, RecruiterRegistrationEmailTemplate
            from django.conf import settings
            
            recruiter_data = {
                'id': str(recruiter.id),
                'employee_id': recruiter.employee_id,
                'name': recruiter.name,
                'email': recruiter.email,
                'phone': recruiter.phone,
                'department_display': recruiter.get_department_display(),
                'specialization_display': recruiter.get_specialization_display(),
                'date_of_joining': recruiter.date_of_joining,
                'max_clients': recruiter.max_clients,
                'status': recruiter.get_status_display(),
                'created_at': recruiter.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            subject, text_content, html_content = RecruiterRegistrationEmailTemplate.get_admin_notification_email(recruiter_data)
            operations_email = getattr(settings, 'OPERATIONS_EMAIL', 'hyrind.operations@gmail.com')
            
            EmailService.send_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                to_emails=[operations_email]
            )
            
        except Exception as e:
            print(f"✗ Failed to send notification email to admin: {str(e)}")


class RecruiterMeView(generics.RetrieveUpdateAPIView):
    """
    Authenticated recruiter profile endpoint.
    GET: Retrieve own recruiter profile
    PATCH/PUT: Update own recruiter information
    """
    serializer_class = RecruiterSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get authenticated recruiter's profile",
        operation_summary="Get Recruiter Profile",
        responses={
            200: RecruiterSerializer,
            404: "Recruiter not found for authenticated user"
        },
        tags=['Recruiters - Profile']
    )
    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
            recruiter = Recruiter.objects.get(user=profile)
            serializer = self.get_serializer(recruiter)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Profile.DoesNotExist, Recruiter.DoesNotExist):
            return Response(
                {'detail': 'Recruiter profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Update authenticated recruiter's profile",
        operation_summary="Update Recruiter Profile",
        request_body=RecruiterUpdateSerializer,
        responses={
            200: RecruiterSerializer,
            400: "Bad Request",
            404: "Recruiter not found"
        },
        tags=['Recruiters - Profile']
    )
    def patch(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
            recruiter = Recruiter.objects.get(user=profile)
            serializer = RecruiterUpdateSerializer(recruiter, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Log the update
            try:
                from audit.utils import log_action
                log_action(
                    actor=request.user,
                    action='recruiter_profile_updated',
                    target=f'Recruiter:{recruiter.id}',
                    metadata={'recruiter_id': str(recruiter.id)}
                )
            except Exception:
                pass
            
            return Response(RecruiterSerializer(recruiter).data, status=status.HTTP_200_OK)
        except (Profile.DoesNotExist, Recruiter.DoesNotExist):
            return Response(
                {'detail': 'Recruiter profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, request, *args, **kwargs):
        """Full update - same as PATCH for recruiter profile"""
        return self.patch(request, *args, **kwargs)


class RecruiterDashboardView(generics.RetrieveAPIView):
    """
    Recruiter dashboard endpoint with stats and assigned clients.
    Returns comprehensive dashboard data for authenticated recruiter.
    """
    serializer_class = RecruiterDashboardSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get recruiter dashboard with stats and assigned clients",
        operation_summary="Recruiter Dashboard",
        responses={
            200: RecruiterDashboardSerializer,
            404: "Recruiter not found"
        },
        tags=['Recruiters - Dashboard']
    )
    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
            recruiter = Recruiter.objects.get(user=profile)
            serializer = self.get_serializer(recruiter)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Profile.DoesNotExist, Recruiter.DoesNotExist):
            return Response(
                {'detail': 'Recruiter profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# RECRUITER MANAGEMENT ENDPOINTS (ADMIN ONLY)
# ============================================================================

class RecruiterListView(generics.ListAPIView):
    """
    List all recruiters.
    Admin only - returns all recruiters with admin filters.
    """
    serializer_class = RecruiterListSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="List all recruiters (admin only)",
        operation_summary="List All Recruiters",
        manual_parameters=[
            openapi.Parameter(
                'active',
                openapi.IN_QUERY,
                description='Filter by active status (true/false)',
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'company_name',
                openapi.IN_QUERY,
                description='Filter by company name (partial match)',
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: RecruiterListSerializer(many=True),
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiters - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter based on query parameters"""
        queryset = Recruiter.objects.all().order_by('-created_at')
        
        # Filter by active status
        active = self.request.query_params.get('active', None)
        if active is not None:
            active = active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(active=active)
        
        # Filter by company name
        company_name = self.request.query_params.get('company_name', None)
        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)
        
        return queryset


class RecruiterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a recruiter (admin endpoints).
    - GET: Retrieve recruiter details
    - PUT/PATCH: Update recruiter information (including active status)
    - DELETE: Soft delete (set active=False)
    
    Lookup by recruiter UUID id.
    """
    queryset = Recruiter.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Get recruiter details by UUID (admin only)",
        operation_summary="Retrieve Recruiter",
        responses={
            200: RecruiterSerializer,
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiters - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update recruiter information by UUID (admin only)",
        operation_summary="Update Recruiter",
        request_body=RecruiterAdminUpdateSerializer,
        responses={
            200: RecruiterSerializer,
            400: "Bad Request",
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiters - Admin']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update recruiter information by UUID (admin only)",
        operation_summary="Partial Update Recruiter",
        request_body=RecruiterAdminUpdateSerializer,
        responses={
            200: RecruiterSerializer,
            400: "Bad Request",
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiters - Admin']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete recruiter by UUID (soft delete - sets active=False) (admin only)",
        operation_summary="Delete Recruiter",
        responses={
            204: "No Content - Recruiter deactivated",
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiters - Admin']
    )
    def delete(self, request, *args, **kwargs):
        recruiter = self.get_object()
        recruiter.active = False
        recruiter.save()
        
        # Log the deactivation
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='recruiter_deactivated',
                target=f'Recruiter:{recruiter.id}',
                metadata={'email': recruiter.email, 'name': recruiter.name}
            )
        except Exception:
            pass
        
        return Response(
            {'message': 'Recruiter deactivated successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    def get_serializer_class(self):
        """Use different serializers for different methods"""
        if self.request.method in ['PUT', 'PATCH']:
            return RecruiterAdminUpdateSerializer
        return RecruiterSerializer


class RecruiterActivateView(generics.GenericAPIView):
    """
    Admin endpoint to activate/approve a recruiter account and send activation email.
    """
    queryset = Recruiter.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAdminUser]
    serializer_class = RecruiterSerializer
    
    @swagger_auto_schema(
        operation_description="Activate (approve) a recruiter account by UUID (admin only)",
        operation_summary="Activate Recruiter",
        responses={
            200: RecruiterSerializer,
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiters - Admin']
    )
    def patch(self, request, *args, **kwargs):
        """Activate a recruiter"""
        recruiter = self.get_object()
        recruiter.active = True
        # Also enable the underlying Django user and profile so they can log in
        try:
            profile = recruiter.user
            django_user = profile.user
            django_user.is_active = True
            django_user.save(update_fields=['is_active'])
            # mirror on profile
            profile.active = True
            profile.save(update_fields=['active'])
        except Exception:
            # If associated User/Profile can't be found, continue and rely on recruiter.active
            pass

        # mark status appropriately
        recruiter.status = 'active'
        recruiter.active = True
        recruiter.save(update_fields=['active', 'status'])
        
        # Send activation email to the recruiter
        self._send_activation_email_to_recruiter(recruiter)
        
        # Log the activation
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='recruiter_activated',
                target=f'Recruiter:{recruiter.id}',
                metadata={'email': recruiter.email, 'name': recruiter.name}
            )
        except Exception:
            pass
        
        serializer = RecruiterSerializer(recruiter)
        return Response({
            'success': True,
            'message': 'Recruiter activated successfully',
            'data': {
                'recruiter': serializer.data,
                'status': 'active',
                'is_active': recruiter.active,  # Use actual DB value
                'activated_at': recruiter.updated_at if hasattr(recruiter, 'updated_at') else None
            }
        }, status=status.HTTP_200_OK)
    
    def _send_activation_email_to_recruiter(self, recruiter):
        """
        Send activation notification email to the recruiter
        
        Args:
            recruiter: Recruiter instance of the activated recruiter
        """
        try:
            from utils.email_service import EmailService, RecruiterActivationEmailTemplate
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Prepare recruiter data for email template
            recruiter_data = {
                'employee_id': recruiter.employee_id,
                'name': recruiter.name,
                'email': recruiter.email,
                'department_display': recruiter.get_department_display() if recruiter.department else 'N/A',
                'specialization_display': recruiter.get_specialization_display() if recruiter.specialization else 'N/A',
                'max_clients': recruiter.max_clients,
                'login_url': 'https://hyrind.com/recruiter/login',  # Update with your actual frontend URL
                'dashboard_url': 'https://hyrind.com/recruiter/dashboard',  # Update with your actual frontend URL
            }
            
            # Get email content from template
            subject, text_content, html_content = RecruiterActivationEmailTemplate.get_activation_email(recruiter_data)
            
            # Send email using central EmailService
            try:
                EmailService.send_email(
                    subject,
                    text_content,
                    html_content,
                    to_emails=[recruiter.email]
                )
                logger.info(f"Activation email sent successfully to recruiter {recruiter.email}")
            except Exception:
                logger.warning(f"Failed to send activation email to recruiter {recruiter.email}")
                
        except Exception as e:
            # Log the error but don't fail the activation process
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending activation email to recruiter {recruiter.email}: {str(e)}")



class RecruiterDeactivateView(generics.GenericAPIView):
    """
    Admin endpoint to deactivate a recruiter account.
    """
    queryset = Recruiter.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAdminUser]
    serializer_class = RecruiterSerializer
    
    @swagger_auto_schema(
        operation_description="Deactivate a recruiter account by UUID (admin only)",
        operation_summary="Deactivate Recruiter",
        responses={
            200: RecruiterSerializer,
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiters - Admin']
    )
    def patch(self, request, *args, **kwargs):
        """Deactivate a recruiter"""
        recruiter = self.get_object()
        recruiter.active = False
        # Also disable the underlying Django user and profile to prevent login
        try:
            profile = recruiter.user
            django_user = profile.user
            django_user.is_active = False
            django_user.save(update_fields=['is_active'])
            profile.active = False
            profile.save(update_fields=['active'])
        except Exception:
            pass

        recruiter.status = 'inactive'
        recruiter.active = False
        recruiter.save(update_fields=['active', 'status'])
        
        # Log the deactivation
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user,
                action='recruiter_deactivated',
                target=f'Recruiter:{recruiter.id}',
                metadata={'email': recruiter.email, 'name': recruiter.name}
            )
        except Exception:
            pass
        
        serializer = RecruiterSerializer(recruiter)
        return Response({
            'success': True,
            'message': 'Recruiter deactivated successfully',
            'data': {
                'recruiter': serializer.data,
                'status': 'inactive',
                'is_active': recruiter.active,  # Use actual DB value
                'deactivated_at': recruiter.updated_at if hasattr(recruiter, 'updated_at') else None
            }
        }, status=status.HTTP_200_OK)


# ============================================================================
# ASSIGNMENT ENDPOINTS
# ============================================================================

class AssignmentCreateView(ProfileResolveMixin, generics.CreateAPIView):
    """Create an assignment between a profile and recruiter"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create assignment between a candidate profile and recruiter (admin only)",
        operation_summary="Create Assignment",
        request_body=AssignmentSerializer,
        responses={
            201: AssignmentSerializer,
            400: "Bad Request"
        },
        tags=['Assignments']
    )
    def post(self, request, *args, **kwargs):
        recruiter_id = request.data.get('recruiter_id')
        profile = self.get_profile()
        onboarding = Onboarding.objects.get(profile=profile)
        if not onboarding.completed:
            return Response(
                {'detail': 'Onboarding not completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment, _ = Assignment.objects.get_or_create(profile=profile)
        assignment.recruiter_id = recruiter_id
        assignment.save()
        
        # Audit log
        try:
            from audit.utils import log_action
            log_action(
                actor=request.user if request.user.is_authenticated else None,
                action='recruiter_assigned',
                target=f'Profile:{str(profile.id)}',
                metadata={'recruiter_id': recruiter_id}
            )
        except Exception:
            pass
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ============================================================================
# RECRUITER REGISTRATION FORM ENDPOINTS (COMPREHENSIVE ONBOARDING)
# ============================================================================

class RecruiterRegistrationFormCreateView(generics.CreateAPIView):
    """
    Public endpoint for comprehensive recruiter registration form submission.
    Accepts multipart form data with optional file uploads to MinIO storage.
    """
    queryset = RecruiterRegistration.objects.all()
    serializer_class = RecruiterRegistrationFormSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="Submit comprehensive recruiter registration form (public endpoint)",
        operation_summary="Create Recruiter Registration Form",
        request_body=RecruiterRegistrationFormSerializer,
        responses={
            201: openapi.Response(
                description="Recruiter registration created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Bad Request - Validation errors"
        },
        tags=['Recruiter Registration Form']
    )
    def post(self, request, *args, **kwargs):
        """Create recruiter registration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Log the registration
        try:
            from audit.utils import log_action
            log_action(
                actor=None,
                action='recruiter_registration_form_submitted',
                target=f'RecruiterRegistration:{instance.id}',
                metadata={'email': instance.email, 'name': instance.full_name}
            )
        except Exception:
            pass
        
        return Response({
            'message': 'Recruiter registration form submitted successfully',
            'id': str(instance.id),
            'email': instance.email,
            'status': 'pending_verification'
        }, status=status.HTTP_201_CREATED)


class RecruiterRegistrationFormListView(generics.ListAPIView):
    """
    Admin endpoint to list all recruiter registrations.
    Admin only - returns all registrations with filtering options.
    """
    queryset = RecruiterRegistration.objects.all()
    serializer_class = RecruiterRegistrationFormListSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Get list of recruiter registrations (admin only)",
        operation_summary="List Recruiter Registrations",
        manual_parameters=[
            openapi.Parameter(
                'verified',
                openapi.IN_QUERY,
                description='Filter by verification status (true/false)',
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                description='Filter by email (partial match)',
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: RecruiterRegistrationFormListSerializer(many=True),
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiter Registration Form']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter based on query parameters"""
        queryset = RecruiterRegistration.objects.all().order_by('-created_at')
        
        # Filter by verification status
        verified = self.request.query_params.get('verified', None)
        if verified is not None:
            is_verified = verified.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_verified=is_verified)
        
        # Filter by email
        email = self.request.query_params.get('email', None)
        if email:
            queryset = queryset.filter(email__icontains=email)
        
        return queryset


class RecruiterRegistrationFormDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin endpoint to retrieve and update recruiter registration details.
    Supports file uploads for missing documents.
    """
    queryset = RecruiterRegistration.objects.all()
    serializer_class = RecruiterRegistrationFormSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="Get recruiter registration details by UUID (admin only)",
        operation_summary="Retrieve Recruiter Registration",
        responses={
            200: RecruiterRegistrationFormSerializer,
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiter Registration Form']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update recruiter registration details by UUID (admin only, supports file uploads)",
        operation_summary="Update Recruiter Registration",
        request_body=RecruiterRegistrationFormSerializer,
        responses={
            200: RecruiterRegistrationFormSerializer,
            400: "Bad Request",
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiter Registration Form']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        """Full update"""
        return super().put(request, *args, **kwargs)


class RecruiterRegistrationFormVerifyView(generics.GenericAPIView):
    """
    Admin endpoint to verify/approve recruiter registration.
    """
    queryset = RecruiterRegistration.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAdminUser]
    serializer_class = RecruiterRegistrationFormSerializer
    
    @swagger_auto_schema(
        operation_description="Verify recruiter registration by UUID (admin only)",
        operation_summary="Verify Recruiter Registration",
        responses={
            200: RecruiterRegistrationFormSerializer,
            404: "Not Found",
            403: "Forbidden - Admin access required"
        },
        tags=['Recruiter Registration Form']
    )
    def patch(self, request, id=None, *args, **kwargs):
        """Verify a recruiter registration"""
        try:
            registration = RecruiterRegistration.objects.get(id=id)
            registration.is_verified = True
            registration.save()

            # Auto-create User, Profile, and Recruiter if not existing
            try:
                from django.contrib.auth.models import User
                from django.contrib.auth import get_user_model
                from users.models import Profile

                UserModel = get_user_model()
                # Check if a user with this email exists
                user = None
                if UserModel.objects.filter(email=registration.email).exists():
                    user = UserModel.objects.filter(email=registration.email).first()
                else:
                    # Create a user with a random password and keep inactive until admin activates
                    random_password = UserModel.objects.make_random_password()
                    user = UserModel.objects.create_user(
                        username=registration.email,
                        email=registration.email,
                        password=random_password,
                        first_name=(registration.full_name.split(' ')[0] if registration.full_name else ''),
                        last_name=(' '.join(registration.full_name.split(' ')[1:]) if registration.full_name and len(registration.full_name.split(' '))>1 else '')
                    )
                    user.is_active = False
                    user.save(update_fields=['is_active'])

                # Create or get Profile
                profile, _ = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': (registration.full_name.split(' ')[0] if registration.full_name else ''),
                        'last_name': (' '.join(registration.full_name.split(' ')[1:]) if registration.full_name and len(registration.full_name.split(' '))>1 else ''),
                        'email': registration.email,
                        'phone': registration.phone_number,
                    }
                )

                # Create Recruiter if not exists
                from .models import Recruiter
                if not Recruiter.objects.filter(email=registration.email).exists():
                    recruiter = Recruiter.objects.create(
                        user=profile,
                        name=registration.full_name,
                        email=registration.email,
                        phone=registration.phone_number,
                        company_name='',
                        active=False,
                    )
                else:
                    recruiter = Recruiter.objects.filter(email=registration.email).first()

                # Try sending an informational email to the recruiter (fail silently)
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    send_mail(
                        'Your recruiter account has been created',
                        f'Hello {registration.full_name},\n\nYour reviewer account has been verified by admin. You can log in using your email: {registration.email}. If you did not set a password, please use the password reset link to set your password.',
                        settings.DEFAULT_FROM_EMAIL,
                        [registration.email],
                        fail_silently=True
                    )
                except Exception:
                    pass

            except Exception:
                # If any of the auto-create steps fail, continue but log via audit
                try:
                    from audit.utils import log_action
                    log_action(
                        actor=request.user,
                        action='recruiter_verification_auto_create_failed',
                        target=f'RecruiterRegistration:{registration.id}',
                        metadata={'email': registration.email}
                    )
                except Exception:
                    pass
            
            # Log the verification
            try:
                from audit.utils import log_action
                log_action(
                    actor=request.user,
                    action='recruiter_registration_verified',
                    target=f'RecruiterRegistration:{registration.id}',
                    metadata={'email': registration.email, 'name': registration.full_name}
                )
            except Exception:
                pass
            
            serializer = RecruiterRegistrationFormSerializer(registration)
            return Response({
                'message': 'Recruiter registration verified successfully',
                'registration': serializer.data
            }, status=status.HTTP_200_OK)
        
        except RecruiterRegistration.DoesNotExist:
            return Response(
                {'detail': 'Recruiter registration not found'},
                status=status.HTTP_404_NOT_FOUND
            )
