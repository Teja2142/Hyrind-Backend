from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Onboarding
from .serializers import OnboardingSerializer


class OnboardingListCreateView(generics.ListCreateAPIView):
    """List onboarding workflows or create a new one"""
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List onboarding workflows",
        operation_description="Retrieve all onboarding workflows for the authenticated user. Shows progress for each workflow including completed and pending steps.",
        responses={200: OnboardingSerializer(many=True)},
        tags=['Onboarding']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create new onboarding workflow",
        operation_description="Initialize a new onboarding workflow for a user. This creates a structured multi-step process to guide users through platform setup and profile completion.",
        request_body=OnboardingSerializer,
        responses={
            201: openapi.Response('Workflow created', OnboardingSerializer),
            400: 'Invalid data',
            401: 'Authentication required'
        },
        tags=['Onboarding']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OnboardingRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a specific onboarding workflow"""
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Get onboarding workflow details",
        operation_description="Retrieve detailed information about a specific onboarding workflow, including all steps, completed status, and progress percentage.",
        responses={
            200: OnboardingSerializer,
            404: 'Workflow not found'
        },
        tags=['Onboarding']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Mark onboarding step as complete",
        operation_description="Mark a specific step in the onboarding workflow as complete. This advances the user's progress through the onboarding process.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'step': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the step to mark as complete')
            }
        ),
        responses={
            200: openapi.Response('Step marked complete', OnboardingSerializer),
            400: 'Step already completed',
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
