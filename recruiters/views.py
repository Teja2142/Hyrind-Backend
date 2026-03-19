from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse

from users.models import User
from users.permissions import IsAdmin, IsApproved, IsRecruiter
from audit.utils import log_action
from notifications.utils import send_email, create_notification
from candidates.models import Candidate

from .models import RecruiterProfile, RecruiterBankDetail, RecruiterAssignment, DailySubmissionLog, JobLinkEntry
from .serializers import (
    RecruiterProfileSerializer, RecruiterBankDetailSerializer,
    RecruiterAssignmentSerializer, AssignRecruiterSerializer,
    DailySubmissionLogSerializer, JobLinkEntrySerializer,
)


# -- Recruiter Profile --------------------------------------------------------

@extend_schema(summary='Get my recruiter profile', tags=['Recruiters'])
@api_view(['GET'])
@permission_classes([IsRecruiter])
def recruiter_me(request):
    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Recruiter profile not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(RecruiterProfileSerializer(profile).data)


@extend_schema(summary='Update my recruiter profile', tags=['Recruiters'])
@api_view(['PATCH'])
@permission_classes([IsRecruiter])
def update_recruiter_me(request):
    try:
        profile = request.user.recruiter_profile
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Recruiter profile not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = RecruiterProfileSerializer(profile, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


@extend_schema(summary='List all recruiters (Admin)', tags=['Recruiters'])
@api_view(['GET'])
@permission_classes([IsAdmin])
def recruiter_list(request):
    profiles = RecruiterProfile.objects.select_related('user').all().order_by('-created_at')
    return Response(RecruiterProfileSerializer(profiles, many=True).data)


@extend_schema(summary='Get a recruiter by ID (Admin)', tags=['Recruiters'])
@api_view(['GET'])
@permission_classes([IsAdmin])
def recruiter_detail(request, recruiter_id):
    try:
        profile = RecruiterProfile.objects.select_related('user').get(id=recruiter_id)
    except RecruiterProfile.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(RecruiterProfileSerializer(profile).data)


# -- Bank Details -------------------------------------------------------------

@extend_schema(summary='Get/set my bank details (Recruiter)', tags=['Recruiters'])
@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsRecruiter])
def bank_details(request):
    if request.method == 'GET':
        try:
            bd = request.user.bank_details
            return Response(RecruiterBankDetailSerializer(bd).data)
        except RecruiterBankDetail.DoesNotExist:
            return Response({})

    ser = RecruiterBankDetailSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    bd, _ = RecruiterBankDetail.objects.update_or_create(
        recruiter=request.user,
        defaults=ser.validated_data,
    )
    log_action(request.user, 'bank_details_updated', str(request.user.id), 'user')
    send_email(
        to='hyrind.operations@gmail.com',
        subject='Recruiter Bank Details Updated',
        html=f'<p>Recruiter <strong>{request.user.email}</strong> has updated their bank details.</p>',
        email_type='bank_details_updated',
    )
    return Response(RecruiterBankDetailSerializer(bd).data)


@extend_schema(summary='View recruiter bank details (Admin only)', tags=['Recruiters'])
@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_bank_details(request, recruiter_id):
    try:
        profile = RecruiterProfile.objects.get(id=recruiter_id)
        bd = profile.user.bank_details
        return Response(RecruiterBankDetailSerializer(bd).data)
    except (RecruiterProfile.DoesNotExist, RecruiterBankDetail.DoesNotExist):
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# -- Recruiter Assignments ----------------------------------------------------

@extend_schema(summary='Assign a recruiter to a candidate (Admin)', tags=['Recruiters'])
@api_view(['POST'])
@permission_classes([IsAdmin])
def assign_recruiter(request):
    ser = AssignRecruiterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    try:
        candidate = Candidate.objects.get(id=d['candidate_id'])
        recruiter = User.objects.get(id=d['recruiter_id'], role='recruiter')
    except (Candidate.DoesNotExist, User.DoesNotExist):
        return Response({'error': 'Candidate or recruiter not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        assignment = RecruiterAssignment.objects.create(
            candidate=candidate,
            recruiter=recruiter,
            role_type=d.get('role_type', ''),
            assigned_by=request.user,
        )
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    log_action(request.user, 'recruiter_assigned', str(candidate.id), 'candidate', {
        'recruiter_id': str(recruiter.id),
    })
    create_notification(candidate.user, 'Recruiter Assigned',
                        f'A recruiter has been assigned to your profile.')
    create_notification(recruiter, 'New Candidate Assigned',
                        f'You have been assigned to a new candidate.')
    return Response(RecruiterAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)


@extend_schema(summary='Unassign a recruiter from a candidate (Admin)', tags=['Recruiters'])
@api_view(['POST'])
@permission_classes([IsAdmin])
def unassign_recruiter(request, assignment_id):
    try:
        assignment = RecruiterAssignment.objects.get(id=assignment_id)
    except RecruiterAssignment.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    assignment.is_active    = False
    assignment.unassigned_at = timezone.now()
    assignment.save()
    log_action(request.user, 'recruiter_unassigned', str(assignment.candidate_id), 'candidate', {
        'recruiter_id': str(assignment.recruiter_id),
    })
    return Response({'message': 'Recruiter unassigned'})


@extend_schema(summary='List all active assignments (Admin)', tags=['Recruiters'])
@api_view(['GET'])
@permission_classes([IsAdmin])
def assignment_list(request):
    assignments = RecruiterAssignment.objects.select_related('candidate__user', 'recruiter').filter(is_active=True)
    return Response(RecruiterAssignmentSerializer(assignments, many=True).data)


# -- Daily Submission Logs ----------------------------------------------------

@extend_schema(summary='List daily logs for a candidate', tags=['Recruiters'])
@api_view(['GET'])
@permission_classes([IsApproved])
def daily_log_list(request, candidate_id):
    logs = DailySubmissionLog.objects.filter(candidate_id=candidate_id).prefetch_related('job_entries')
    return Response(DailySubmissionLogSerializer(logs, many=True).data)


@extend_schema(summary='Create a daily submission log', tags=['Recruiters'])
@api_view(['POST'])
@permission_classes([IsRecruiter])
def create_daily_log(request, candidate_id):
    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = DailySubmissionLogSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    log = ser.save(candidate=candidate, recruiter=request.user)
    return Response(DailySubmissionLogSerializer(log).data, status=status.HTTP_201_CREATED)


@extend_schema(summary='Add a job entry to a daily log', tags=['Recruiters'])
@api_view(['POST'])
@permission_classes([IsRecruiter])
def add_job_entry(request, log_id):
    try:
        log = DailySubmissionLog.objects.get(id=log_id)
    except DailySubmissionLog.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = JobLinkEntrySerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    entry = ser.save(
        submission_log=log, candidate=log.candidate,
        submitted_by=request.user, fetch_status='pending',
    )
    return Response(JobLinkEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


@extend_schema(summary='Update a job entry', tags=['Recruiters'])
@api_view(['PATCH'])
@permission_classes([IsRecruiter])
def update_job_entry(request, entry_id):
    try:
        entry = JobLinkEntry.objects.get(id=entry_id)
    except JobLinkEntry.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = JobLinkEntrySerializer(entry, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)


# ── Additional views matching frontend api.ts paths ───────────────────────────

@extend_schema(
    summary='List candidates assigned to the current recruiter',
    responses={200: OpenApiResponse(description='List of assigned candidates')},
    tags=['Recruiters'],
)
@api_view(['GET'])
@permission_classes([IsRecruiter])
def my_candidates(request):
    assigned_ids = RecruiterAssignment.objects.filter(
        recruiter=request.user, is_active=True
    ).values_list('candidate_id', flat=True)
    from candidates.models import Candidate
    from candidates.serializers import CandidateListSerializer
    candidates = Candidate.objects.filter(id__in=assigned_ids).select_related('user__profile')
    return Response(CandidateListSerializer(candidates, many=True).data)


@extend_schema(
    summary='Recruiter dashboard — assigned candidates + stats',
    responses={200: OpenApiResponse(description='Dashboard payload with candidates and stats')},
    tags=['Recruiters'],
)
@api_view(['GET'])
@permission_classes([IsRecruiter])
def recruiter_dashboard(request):
    from candidates.models import Candidate
    from candidates.serializers import CandidateListSerializer

    active_assignments = RecruiterAssignment.objects.filter(
        recruiter=request.user, is_active=True
    ).select_related('candidate__user__profile')
    active_ids = active_assignments.values_list('candidate_id', flat=True)
    candidates = Candidate.objects.filter(id__in=active_ids).select_related('user__profile')

    all_ids = RecruiterAssignment.objects.filter(
        recruiter=request.user
    ).values_list('candidate_id', flat=True)
    placed_count = Candidate.objects.filter(id__in=all_ids, status='placed_closed').count()

    return Response({
        'stats': {
            'total_assigned': len(active_ids),
            'active':         candidates.count(),
            'placed':         placed_count,
        },
        'candidates': CandidateListSerializer(candidates, many=True).data,
    })


@extend_schema(
    summary='List assignments for a specific candidate',
    responses={200: RecruiterAssignmentSerializer(many=True)},
    tags=['Recruiters'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def candidate_assignment_list(request, candidate_id):
    assignments = RecruiterAssignment.objects.filter(
        candidate_id=candidate_id
    ).select_related('recruiter')
    return Response(RecruiterAssignmentSerializer(assignments, many=True).data)


@extend_schema(
    summary='Get or create daily submission logs for a candidate (GET+POST)',
    description='GET returns all logs for this candidate. POST creates a new daily log with optional job_links array.',
    responses={200: DailySubmissionLogSerializer(many=True), 201: DailySubmissionLogSerializer},
    tags=['Recruiters'],
)
@api_view(['GET', 'POST'])
@permission_classes([IsRecruiter])
def daily_logs(request, candidate_id):
    if request.method == 'GET':
        logs = DailySubmissionLog.objects.filter(
            candidate_id=candidate_id
        ).prefetch_related('job_entries').order_by('-log_date')
        return Response(DailySubmissionLogSerializer(logs, many=True).data)

    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    log = DailySubmissionLog.objects.create(
        candidate=candidate,
        recruiter=request.user,
        applications_count=request.data.get('applications_count', 0),
        notes=request.data.get('notes', ''),
    )
    for jl in request.data.get('job_links', []):
        JobLinkEntry.objects.create(
            submission_log=log,
            candidate=candidate,
            company_name=jl.get('company_name', ''),
            role_title=jl.get('role_title', ''),
            job_url=jl.get('job_url', ''),
            application_status=jl.get('status', 'applied'),
            submitted_by=request.user,
        )
    return Response(DailySubmissionLogSerializer(log).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Update job link / application status',
    description='Candidate or recruiter updates the status of a tracked job application.',
    request={'application/json': {'type': 'object', 'properties': {
        'status': {'type': 'string', 'description': 'applied | callback | rejected | offer | other'},
    }}},
    responses={200: JobLinkEntrySerializer},
    tags=['Recruiters'],
)
@api_view(['POST'])
@permission_classes([IsApproved])
def update_job_status(request, job_id):
    try:
        job = JobLinkEntry.objects.get(id=job_id)
    except JobLinkEntry.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    new_status = request.data.get('status')
    if new_status:
        job.application_status = new_status
        job.save(update_fields=['application_status'])
    return Response(JobLinkEntrySerializer(job).data)
