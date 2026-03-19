from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema

from .models import User
from .serializers import (
    RegisterSerializer, UserSerializer, UserListSerializer,
    ApproveUserSerializer, ChangePasswordSerializer,
)
from .permissions import IsAdmin
from audit.utils import log_action
from notifications.utils import send_email


@extend_schema(
    summary='Register a new candidate or recruiter',
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(description='Registration successful. Awaiting admin approval.'),
        400: OpenApiResponse(description='Validation error'),
    },
    tags=['Auth'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    log_action(actor=None, action='registration_created', target_id=str(user.id), target_type='user',
               details={'role': user.role, 'email': user.email})

    # Notify admin
    send_email(
        to=settings.ADMIN_NOTIFICATION_EMAIL,
        subject=f'New {user.role} registration \u2013 {user.profile.full_name}',
        html=(
            f'<p><strong>{user.profile.full_name}</strong> ({user.email}) registered as <em>{user.role}</em>.</p>'
            f'<p><a href="{settings.SITE_URL}/admin-dashboard/approvals">Review in Admin Dashboard</a></p>'
        ),
        email_type='registration_notify_admin',
    )

    return Response({'message': 'Registration successful. Awaiting admin approval.'}, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Login and obtain JWT tokens',
    request={'application/json': {'type': 'object', 'properties': {
        'email': {'type': 'string', 'format': 'email'},
        'password': {'type': 'string'},
    }, 'required': ['email', 'password']}},
    responses={
        200: OpenApiResponse(description='JWT access and refresh tokens plus user details'),
        401: OpenApiResponse(description='Invalid credentials'),
        403: OpenApiResponse(description='Account pending approval'),
    },
    tags=['Auth'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email    = request.data.get('email', '').lower().strip()
    password = request.data.get('password', '')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Non-admin users must be approved to log in
    if user.approval_status != 'approved' and user.role != 'admin':
        return Response({
            'error': 'Account not yet approved',
            'approval_status': user.approval_status,
        }, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user':    UserSerializer(user).data,
    })


@extend_schema(
    summary='Logout \u2014 blacklist refresh token',
    request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}},
    responses={200: OpenApiResponse(description='Logged out successfully')},
    tags=['Auth'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except Exception:
        pass
    return Response({'message': 'Logged out'})


@extend_schema(
    summary='Get current authenticated user',
    responses={200: UserSerializer},
    tags=['Auth'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@extend_schema(
    summary='Update own profile fields',
    request={'application/json': {'type': 'object', 'properties': {
        'first_name': {'type': 'string'},
        'last_name':  {'type': 'string'},
        'phone':      {'type': 'string'},
        'avatar_url': {'type': 'string', 'format': 'uri'},
    }}},
    responses={200: UserSerializer},
    tags=['Auth'],
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    profile = request.user.profile
    for field in ['first_name', 'last_name', 'phone', 'avatar_url']:
        if field in request.data:
            setattr(profile, field, request.data[field])
    profile.save()
    return Response(UserSerializer(request.user).data)


@extend_schema(
    summary='Change own password',
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description='Password changed successfully'),
        400: OpenApiResponse(description='Validation error'),
    },
    tags=['Auth'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not request.user.check_password(serializer.validated_data['current_password']):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save()
    log_action(actor=request.user, action='password_updated', target_id=str(request.user.id), target_type='user')
    return Response({'message': 'Password changed successfully'})


# --- Admin endpoints ----------------------------------------------------------

@extend_schema(
    summary='List users pending admin approval',
    responses={200: UserListSerializer(many=True)},
    tags=['Auth - Admin'],
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def pending_approvals(request):
    users = (
        User.objects
        .filter(approval_status='pending_approval')
        .select_related('profile')
        .order_by('-created_at')
    )
    return Response(UserListSerializer(users, many=True).data)


@extend_schema(
    summary='List all users (Admin)',
    responses={200: UserListSerializer(many=True)},
    tags=['Auth - Admin'],
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def user_list(request):
    role_filter   = request.query_params.get('role')
    status_filter = request.query_params.get('approval_status')
    qs = User.objects.select_related('profile').order_by('-created_at')
    if role_filter:
        qs = qs.filter(role=role_filter)
    if status_filter:
        qs = qs.filter(approval_status=status_filter)
    return Response(UserListSerializer(qs, many=True).data)


@extend_schema(
    summary='Approve or reject a user (Admin)',
    request=ApproveUserSerializer,
    responses={
        200: OpenApiResponse(description='User approved/rejected'),
        404: OpenApiResponse(description='User not found'),
    },
    tags=['Auth - Admin'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def approve_user(request):
    serializer = ApproveUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(id=serializer.validated_data['user_id'])
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    action      = serializer.validated_data['action']
    old_status  = user.approval_status
    user.approval_status = action
    if action == 'approved':
        user.portal_access = True
    user.save()

    log_action(
        actor=request.user,
        action=f'registration_{action}',
        target_id=str(user.id),
        target_type='user',
        details={'old_status': old_status, 'new_status': action},
    )

    name = user.profile.full_name if hasattr(user, 'profile') else user.email
    if action == 'approved':
        send_email(
            to=user.email,
            subject='Your HYRIND account is approved',
            html=(
                f'<p>Hi {name},</p>'
                f'<p>Your account has been approved. You can now log in to the portal.</p>'
                f'<p><a href="{settings.SITE_URL}/{user.role}-login">Login here</a></p>'
            ),
            email_type='registration_approved',
        )
    else:
        send_email(
            to=user.email,
            subject='Update on Your Hyrind Registration',
            html=(
                f'<p>Hi {name},</p>'
                f'<p>Your registration has been reviewed and was not approved at this time.</p>'
                f'<p>If you have questions, please contact support.</p>'
            ),
            email_type='registration_rejected',
        )

    return Response({'message': f'User {action}'})


# ── Password Reset ────────────────────────────────────────────────────────────

@extend_schema(
    summary='Request a password reset email (public)',
    request={'application/json': {'type': 'object', 'properties': {
        'email': {'type': 'string', 'format': 'email'},
    }, 'required': ['email']}},
    responses={200: OpenApiResponse(description='Reset email sent if account exists')},
    tags=['Auth'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get('email', '').lower().strip()
    # Always return 200 to prevent email enumeration
    try:
        user = User.objects.get(email=email)
        import secrets
        token = secrets.token_urlsafe(32)
        # Store token in cache/db — using a simple approach with a timestamp in the token
        # In production use django.contrib.auth.tokens.PasswordResetTokenGenerator
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f'{settings.SITE_URL}/reset-password?uid={uid}&token={token}'
        send_email(
            to=user.email,
            subject='Reset Your Hyrind Password',
            html=(
                f'<p>Hi,</p>'
                f'<p>Click the link below to reset your password (valid for 24 hours):</p>'
                f'<p><a href="{reset_url}">{reset_url}</a></p>'
                f'<p>If you did not request this, ignore this email.</p>'
            ),
            email_type='password_reset',
        )
    except User.DoesNotExist:
        pass
    return Response({'message': 'If an account with that email exists, a reset link has been sent.'})


@extend_schema(
    summary='Confirm password reset with uid + token (public)',
    request={'application/json': {'type': 'object', 'properties': {
        'uid':          {'type': 'string'},
        'token':        {'type': 'string'},
        'new_password': {'type': 'string'},
    }, 'required': ['uid', 'token', 'new_password']}},
    responses={
        200: OpenApiResponse(description='Password reset successfully'),
        400: OpenApiResponse(description='Invalid or expired token'),
    },
    tags=['Auth'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str

    uid_encoded   = request.data.get('uid', '')
    token         = request.data.get('token', '')
    new_password  = request.data.get('new_password', '')

    if not all([uid_encoded, token, new_password]):
        return Response({'error': 'uid, token, and new_password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid  = force_str(urlsafe_base64_decode(uid_encoded))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, Exception):
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Reset link has expired or is invalid'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    log_action(actor=None, action='password_reset', target_id=str(user.id), target_type='user')
    return Response({'message': 'Password reset successfully. You can now log in.'})
