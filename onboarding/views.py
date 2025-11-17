from rest_framework import generics, permissions
from .models import Onboarding
from .serializers import OnboardingSerializer

class OnboardingListCreateView(generics.ListCreateAPIView):
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    permission_classes = [permissions.IsAuthenticated]

from rest_framework import status
from rest_framework.response import Response

class OnboardingRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        onboarding = self.get_object()
        step = request.data.get('step')
        if step and step in onboarding.steps_completed:
            return Response({'detail': 'Step already completed.'}, status=status.HTTP_400_BAD_REQUEST)
        if step:
            onboarding.mark_step_complete(step)
        serializer = self.get_serializer(onboarding)
        return Response(serializer.data)
