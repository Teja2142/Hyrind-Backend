from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Recruiter, Assignment
from .serializers import RecruiterSerializer, AssignmentSerializer
from onboarding.models import Onboarding
from utils.profile_utils import ProfileResolveMixin


class RecruiterListView(generics.ListAPIView):
    queryset = Recruiter.objects.filter(active=True)
    serializer_class = RecruiterSerializer
    permission_classes = [permissions.IsAdminUser]


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
