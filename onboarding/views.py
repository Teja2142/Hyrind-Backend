from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Onboarding
from .serializers import OnboardingSerializer


class OnboardingListCreateView(generics.ListCreateAPIView):
    """
    Onboarding Workflows API
    GET /api/onboarding/ - List workflows for authenticated user
    POST /api/onboarding/ - Create new workflow (Admin only)
    """
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List onboarding workflows",
        operation_description="""Retrieve all onboarding workflows for authenticated user.

Shows workflow progress including:
- Current step and total steps
- Progress percentage
- List of all steps with completion status
- Workflow type (candidate, recruiter, admin)

Example Response:
[
  {
    "id": 1,
    "user": {"id": "uuid", "name": "John Doe"},
    "workflow_type": "candidate",
    "current_step": 3,
    "total_steps": 5,
    "progress_percentage": 60,
    "steps": [
      {"step": 1, "title": "Create Account", "completed": true},
      {"step": 2, "title": "Complete Profile", "completed": true},
      {"step": 3, "title": "Submit Forms", "completed": true},
      {"step": 4, "title": "Payment", "completed": false},
      {"step": 5, "title": "Assignment", "completed": false}
    ],
    "completed": false
  }
]""",
        responses={
            200: openapi.Response('List of workflows', OnboardingSerializer(many=True)),
            401: 'Authentication required'
        },
        tags=['Onboarding']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create new onboarding workflow",
        operation_description="""Initialize a new onboarding workflow for a user.

Permission: Admin only

Creates structured multi-step process for platform setup and profile completion.

Workflow types:
- candidate: For job seekers (5 steps)
- recruiter: For recruiter onboarding (4 steps)  
- admin: For admin setup (3 steps)

Example Request:
{
  "user": "profile-uuid",
  "workflow_type": "candidate",
  "total_steps": 5
}""",
        request_body=OnboardingSerializer,
        responses={
            201: openapi.Response('Workflow created', OnboardingSerializer),
            400: 'Invalid data - validation errors',
            401: 'Authentication required',
            403: 'Permission denied - admin only'
        },
        tags=['Onboarding']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OnboardingRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Onboarding Workflow Detail API
    GET /api/onboarding/{id}/ - Get specific workflow details
    PATCH /api/onboarding/{id}/ - Mark step as complete
    """
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get workflow details",
        operation_description="""Retrieve specific onboarding workflow by ID.

Shows complete workflow state:
- All steps with completion status
- Current progress percentage
- Workflow type and metadata

Example Response:
{
  "id": 1,
  "user": {"id": "uuid", "name": "John Doe"},
  "workflow_type": "candidate",
  "current_step": 3,
  "total_steps": 5,
  "progress_percentage": 60,
  "steps_completed": ["profile_setup", "form_submission", "payment"],
  "completed": false,
  "created_at": "2024-01-18T09:00:00Z",
  "updated_at": "2024-01-18T12:00:00Z"
}""",
        responses={
            200: openapi.Response('Workflow details', OnboardingSerializer),
            401: 'Authentication required',
            403: 'Not your workflow',
            404: 'Workflow not found'
        },
        tags=['Onboarding']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Mark onboarding step as complete",
        operation_description="""Mark a specific step in the onboarding workflow as complete.

This advances the user's progress through the onboarding process.

Common steps:
- profile_setup: Complete user profile
- form_submission: Submit required forms
- payment: Process payment
- document_upload: Upload documents
- assignment: Complete assignment

Example Request:
{
  "step": "payment"
}

Example Response:
{
  "id": 1,
  "user": {"id": "uuid", "name": "John Doe"},
  "workflow_type": "candidate",
  "current_step": 4,
  "total_steps": 5,
  "progress_percentage": 80,
  "steps_completed": ["profile_setup", "form_submission", "payment"],
  "completed": false
}""",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'step': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Name of the step to mark as complete',
                    example='payment'
                )
            },
            required=['step']
        ),
        responses={
            200: openapi.Response('Step marked complete', OnboardingSerializer),
            400: 'Step already completed or invalid step name',
            401: 'Authentication required',
            403: 'Not your workflow',
            404: 'Workflow not found'
        },
        tags=['Onboarding']
    )
    def patch(self, request, *args, **kwargs):
        onboarding = self.get_object()
        step = request.data.get('step')
        if step and step in onboarding.steps_completed:
            return Response({'detail': 'Step already completed.'}, status=status.HTTP_400_BAD_REQUEST)
        if step:
            onboarding.mark_step_complete(step)
        serializer = self.get_serializer(onboarding)
        return Response(serializer.data)
