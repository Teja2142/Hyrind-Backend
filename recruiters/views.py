from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Recruiter, Assignment
from .serializers import (
    RecruiterSerializer, 
    RecruiterRegistrationSerializer,
    RecruiterUpdateSerializer,
    RecruiterListSerializer,
    AssignmentSerializer
)
from onboarding.models import Onboarding
from utils.profile_utils import ProfileResolveMixin


class RecruiterRegistrationView(generics.CreateAPIView):
    """
    Public endpoint for recruiter registration.
    Creates User, Profile, and Recruiter instances.
    """
    serializer_class = RecruiterRegistrationSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Register a new recruiter account",
        operation_summary="Recruiter Registration",
        request_body=RecruiterRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Recruiter created successfully",
                schema=RecruiterSerializer
            ),
            400: "Bad Request - Validation errors"
        },
        tags=['Recruiters']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recruiter = serializer.save()
        
        # Log the registration
        try:
            from audit.utils import log_action
            log_action(
                actor=recruiter.user.user,
                action='recruiter_registered',
                target=f'Recruiter:{recruiter.id}',
                metadata={'email': recruiter.email, 'name': recruiter.name}
            )
        except Exception:
            pass
        
        return Response({
            'message': 'Recruiter registered successfully',
            'recruiter_id': recruiter.id,
            'email': recruiter.email,
            'name': recruiter.name
        }, status=status.HTTP_201_CREATED)


class RecruiterListView(generics.ListAPIView):
    """
    List all recruiters. 
    Admin only - returns all recruiters.
    Authenticated users - returns only active recruiters.
    """
    serializer_class = RecruiterListSerializer
    
    @swagger_auto_schema(
        operation_description="Get list of recruiters",
        operation_summary="List Recruiters",
        responses={200: RecruiterListSerializer(many=True)},
        tags=['Recruiters']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter based on user permissions"""
        if self.request.user.is_staff:
            # Admins see all recruiters
            return Recruiter.objects.all().order_by('-id')
        else:
            # Regular users see only active recruiters
            return Recruiter.objects.filter(active=True).order_by('-id')
    
    def get_permissions(self):
        """Require authentication"""
        return [IsAuthenticated()]


class RecruiterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a recruiter.
    - GET: Retrieve recruiter details
    - PUT/PATCH: Update recruiter information
    - DELETE: Soft delete (set active=False)
    """
    queryset = Recruiter.objects.all()
    lookup_field = 'id'
    
    @swagger_auto_schema(
        operation_description="Get recruiter details by ID",
        operation_summary="Retrieve Recruiter",
        responses={
            200: RecruiterSerializer,
            404: "Not Found"
        },
        tags=['Recruiters']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update recruiter information",
        operation_summary="Update Recruiter",
        request_body=RecruiterUpdateSerializer,
        responses={
            200: RecruiterSerializer,
            400: "Bad Request",
            404: "Not Found"
        },
        tags=['Recruiters']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update recruiter information",
        operation_summary="Partial Update Recruiter",
        request_body=RecruiterUpdateSerializer,
        responses={
            200: RecruiterSerializer,
            400: "Bad Request",
            404: "Not Found"
        },
        tags=['Recruiters']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete recruiter (soft delete - sets active=False)",
        operation_summary="Delete Recruiter",
        responses={
            204: "No Content - Recruiter deactivated",
            404: "Not Found"
        },
        tags=['Recruiters']
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
        
        return Response({'message': 'Recruiter deactivated successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    def get_serializer_class(self):
        """Use different serializers for different methods"""
        if self.request.method in ['PUT', 'PATCH']:
            return RecruiterUpdateSerializer
        return RecruiterSerializer
    
    def get_permissions(self):
        """Admin required for update/delete, authenticated for read"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class AssignmentCreateView(ProfileResolveMixin, generics.CreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        recruiter_id = request.data.get('recruiter_id')
        profile = self.get_profile()
        onboarding = Onboarding.objects.get(profile=profile)
        if not onboarding.completed:
            return Response({'detail': 'Onboarding not completed.'}, status=status.HTTP_400_BAD_REQUEST)
        assignment, _ = Assignment.objects.get_or_create(profile=profile)
        assignment.recruiter_id = recruiter_id
        assignment.save()
        # Audit log
        try:
            from audit.utils import log_action
            log_action(actor=request.user if request.user.is_authenticated else None, action='recruiter_assigned', target=f'Profile:{str(profile.id)}', metadata={'recruiter_id': recruiter_id})
        except Exception:
            pass
        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
