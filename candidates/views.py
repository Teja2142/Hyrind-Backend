from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from users.permissions import IsAdmin, IsApproved, IsRecruiter, IsCandidate
from audit.utils import log_action
from notifications.utils import send_email, create_notification
from django.conf import settings

from .models import (
    Candidate, ClientIntake, RoleSuggestion, CredentialVersion,
    Referral, InterviewLog, PlacementClosure,
)
from .serializers import (
    CandidateSerializer, CandidateListSerializer, ClientIntakeSerializer,
    RoleSuggestionSerializer, CredentialVersionSerializer,
    ReferralSerializer, InterviewLogSerializer, PlacementClosureSerializer,
)


# ── Candidate ─────────────────────────────────────────────────────────────────

@extend_schema(
    summary='List candidates (role-filtered)',
    parameters=[OpenApiParameter('status', description='Filter by pipeline status', required=False)],
    responses={200: CandidateListSerializer(many=True)},
    tags=['Candidates'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def candidate_list(request):
    if request.user.role in ('admin', 'team_lead', 'team_manager'):
        qs = Candidate.objects.select_related('user__profile').all()
    elif request.user.role == 'recruiter':
        ids = request.user.recruiter_assignments.filter(
            is_active=True
        ).values_list('candidate_id', flat=True)
        qs = Candidate.objects.filter(id__in=ids).select_related('user__profile')
    else:
        qs = Candidate.objects.filter(user=request.user).select_related('user__profile')

    s = request.query_params.get('status')
    if s:
        qs = qs.filter(status=s)
    return Response(CandidateListSerializer(qs.order_by('-created_at'), many=True).data)


@extend_schema(
    summary='Get candidate detail',
    responses={200: CandidateSerializer, 404: OpenApiResponse(description='Not found')},
    tags=['Candidates'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def candidate_detail(request, candidate_id):
    try:
        c = Candidate.objects.select_related('user__profile').get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(CandidateSerializer(c).data)


@extend_schema(
    summary='Update candidate pipeline status (Admin)',
    request={'application/json': {'type': 'object', 'properties': {
        'status': {'type': 'string'},
    }, 'required': ['status']}},
    responses={200: OpenApiResponse(description='Status updated')},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def update_candidate_status(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    old_status = c.status
    c.status = new_status
    c.save()
    log_action(request.user, 'status_changed', str(c.id), 'candidate',
               {'old_status': old_status, 'new_status': new_status})
    return Response({'message': f'Status updated to {new_status}'})


# ── Client Intake ─────────────────────────────────────────────────────────────

@extend_schema(
    summary='Get or submit intake form',
    responses={200: ClientIntakeSerializer, 201: ClientIntakeSerializer},
    tags=['Candidates'],
)
@api_view(['GET', 'POST'])
@permission_classes([IsApproved])
def intake(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        try:
            return Response(ClientIntakeSerializer(c.intake).data)
        except ClientIntake.DoesNotExist:
            return Response({})

    # Check lock
    if hasattr(c, 'intake') and c.intake.is_locked:
        return Response({'error': 'Intake is locked. Contact admin to reopen.'}, status=status.HTTP_403_FORBIDDEN)

    intake_obj, _ = ClientIntake.objects.update_or_create(
        candidate=c,
        defaults={**request.data, 'submitted_at': timezone.now(), 'is_locked': True},
    )
    if c.status in ('approved', 'intake_pending'):
        c.status = 'intake_submitted'
        c.save()
    log_action(request.user, 'intake_submitted', str(c.id), 'candidate')
    # Notify admin
    send_email(
        to=settings.ADMIN_NOTIFICATION_EMAIL,
        subject='New Intake Submitted – Action Required',
        html=f'<p>Candidate <strong>{c.user.email}</strong> has submitted their intake form.</p>',
        email_type='intake_submitted_admin',
    )
    return Response(ClientIntakeSerializer(intake_obj).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Admin: reopen intake form',
    request={'application/json': {'type': 'object', 'properties': {'reason': {'type': 'string'}}}},
    responses={200: OpenApiResponse(description='Intake reopened')},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def reopen_intake(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
        c.intake.is_locked   = False
        c.intake.reopened_by = request.user
        c.intake.reopened_at = timezone.now()
        c.intake.reopen_reason = request.data.get('reason', '')
        c.intake.save()
    except (Candidate.DoesNotExist, ClientIntake.DoesNotExist):
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    log_action(request.user, 'intake_reopened', str(c.id), 'candidate',
               {'reason': request.data.get('reason', '')})
    create_notification(c.user, 'Intake Reopened',
                        'Your intake form has been reopened by admin for updates.')
    send_email(
        to=c.user.email, subject='Your Intake Form Has Been Reopened',
        html='<p>Your intake form has been reopened. Please log in and update it.</p>',
        email_type='intake_reopened',
    )
    return Response({'message': 'Intake reopened'})


# ── Role Suggestions ──────────────────────────────────────────────────────────

@extend_schema(
    summary='List role suggestions for a candidate',
    responses={200: RoleSuggestionSerializer(many=True)},
    tags=['Candidates'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def role_list(request, candidate_id):
    roles = RoleSuggestion.objects.filter(candidate_id=candidate_id)
    return Response(RoleSuggestionSerializer(roles, many=True).data)


@extend_schema(
    summary='Add a role suggestion (Admin)',
    request=RoleSuggestionSerializer,
    responses={201: RoleSuggestionSerializer},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def add_role(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = RoleSuggestionSerializer(data={**request.data, 'candidate': str(candidate_id)})
    ser.is_valid(raise_exception=True)
    role = ser.save(candidate=c, suggested_by=request.user)
    return Response(RoleSuggestionSerializer(role).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Publish all role suggestions for a candidate (Admin)',
    responses={200: OpenApiResponse(description='Roles published')},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def publish_roles(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    count = RoleSuggestion.objects.filter(candidate=c, is_published=False).update(
        is_published=True, published_at=now
    )
    c.status = 'roles_published'
    c.save()
    log_action(request.user, 'roles_published', str(c.id), 'candidate', {'roles_count': count})
    create_notification(c.user, 'Role Suggestions Ready',
                        'Your role suggestions are ready for review.')
    send_email(
        to=c.user.email, subject='Your Role Suggestions Are Ready for Review',
        html='<p>Please log in to review and respond to your suggested roles.</p>',
        email_type='roles_published',
    )
    return Response({'message': f'{count} roles published'})


@extend_schema(
    summary='Candidate responds to role suggestions',
    request={'application/json': {'type': 'object', 'properties': {
        'responses': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'role_id': {'type': 'string'},
                    'response': {'type': 'string', 'enum': ['accepted', 'declined', 'change_requested']},
                    'change_request_note': {'type': 'string'},
                },
            },
        },
    }}},
    responses={200: OpenApiResponse(description='Responses saved')},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsCandidate])
def respond_roles(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id, user=request.user)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found or forbidden'}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    for r in request.data.get('responses', []):
        RoleSuggestion.objects.filter(id=r['role_id'], candidate=c).update(
            candidate_response=r.get('response', 'accepted'),
            change_request_note=r.get('change_request_note', ''),
            responded_at=now,
        )
    c.status = 'roles_candidate_responded'
    c.save()
    log_action(request.user, 'roles_responded', str(c.id), 'candidate')
    return Response({'message': 'Responses saved'})


# ── Credentials ───────────────────────────────────────────────────────────────

@extend_schema(
    summary='List credential versions',
    responses={200: CredentialVersionSerializer(many=True)},
    tags=['Candidates'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def credential_list(request, candidate_id):
    versions = CredentialVersion.objects.filter(candidate_id=candidate_id)
    return Response(CredentialVersionSerializer(versions, many=True).data)


@extend_schema(
    summary='Save a new credential version',
    responses={201: CredentialVersionSerializer},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsApproved])
def save_credential(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    # Compute version number (auto-increment per candidate)
    last = CredentialVersion.objects.filter(candidate=c).order_by('-version_number').first()
    next_version = (last.version_number + 1) if last else 1

    # Compute diff against last version
    sensitive = CredentialVersion.SENSITIVE_FIELDS
    data = request.data.copy()
    diff  = {}
    if last:
        for field in data:
            old_val = getattr(last, field, None)
            new_val = data[field]
            if str(old_val) != str(new_val):
                if field in sensitive:
                    diff[field] = {'before': '[REDACTED]', 'after': '[REDACTED]'}
                else:
                    diff[field] = {'before': old_val, 'after': new_val}

    changed = list(diff.keys())
    snap = {f: getattr(last, f, None) for f in data} if last else {}
    snap.update(data)

    cv = CredentialVersion.objects.create(
        candidate=c, version_number=next_version,
        updated_by=request.user,
        source_role=request.user.role,
        changed_fields=changed,
        diff_summary=diff,
        full_snapshot=snap,
        **{k: v for k, v in data.items() if hasattr(CredentialVersion, k)},
    )
    if c.status == 'payment_completed':
        c.status = 'credentials_submitted'
        c.save()
    log_action(request.user, 'credential_updated', str(c.id), 'candidate',
               {'version': next_version, 'changed_fields': changed})
    return Response(CredentialVersionSerializer(cv).data, status=status.HTTP_201_CREATED)


# ── Referrals ─────────────────────────────────────────────────────────────────

@extend_schema(
    summary='Submit a referral',
    request=ReferralSerializer,
    responses={201: ReferralSerializer},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsCandidate])
def submit_referral(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id, user=request.user)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = ReferralSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    ref = ser.save(referrer=c)
    log_action(request.user, 'referral_submitted', str(ref.id), 'referral')
    return Response(ReferralSerializer(ref).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='List referrals for a candidate',
    responses={200: ReferralSerializer(many=True)},
    tags=['Candidates'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def referral_list(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    refs = c.referrals.all()
    return Response(ReferralSerializer(refs, many=True).data)


# ── Interview Logs ────────────────────────────────────────────────────────────

@extend_schema(
    summary='List interview logs for a candidate',
    responses={200: InterviewLogSerializer(many=True)},
    tags=['Candidates'],
)
@api_view(['GET'])
@permission_classes([IsApproved])
def interview_list(request, candidate_id):
    logs = InterviewLog.objects.filter(candidate_id=candidate_id)
    return Response(InterviewLogSerializer(logs, many=True).data)


@extend_schema(
    summary='Log an interview',
    request=InterviewLogSerializer,
    responses={201: InterviewLogSerializer},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsApproved])
def log_interview(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = InterviewLogSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    interview = ser.save(candidate=c, created_by=request.user, updated_by=request.user)
    return Response(InterviewLogSerializer(interview).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Update an interview log entry',
    request=InterviewLogSerializer,
    responses={200: InterviewLogSerializer},
    tags=['Candidates'],
)
@api_view(['PATCH'])
@permission_classes([IsApproved])
def update_interview(request, candidate_id, interview_id):
    try:
        interview = InterviewLog.objects.get(id=interview_id, candidate_id=candidate_id)
    except InterviewLog.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = InterviewLogSerializer(interview, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save(updated_by=request.user)
    return Response(ser.data)


# ── Placement Closure ─────────────────────────────────────────────────────────

@extend_schema(
    summary='Close placement (Admin)',
    request=PlacementClosureSerializer,
    responses={201: PlacementClosureSerializer},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def close_placement(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ser = PlacementClosureSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    placement = ser.save(candidate=c, closed_by=request.user)
    c.status = 'placed_closed'
    c.save()
    log_action(request.user, 'placement_closed', str(c.id), 'candidate', {
        'employer': placement.employer_name,
        'role': placement.role_placed_into,
        'salary': str(placement.salary),
    })
    create_notification(c.user, 'Congratulations!',
                        'Your placement has been confirmed. Case closed successfully.')
    send_email(
        to=c.user.email,
        subject='Congratulations – Your Placement Has Been Confirmed',
        html=(
            f'<p>Congratulations! Your placement at <strong>{placement.employer_name}</strong> '
            f'as <strong>{placement.role_placed_into}</strong> has been confirmed.</p>'
            f'<p>Start date: {placement.start_date}. Well done!</p>'
        ),
        email_type='placement_closed',
    )
    return Response(PlacementClosureSerializer(placement).data, status=status.HTTP_201_CREATED)


# ── Aliases / unified endpoints matching frontend api.ts paths ────────────────

@extend_schema(
    summary='Candidate confirms or rejects suggested roles (frontend: /roles/confirm/)',
    description='Pass decisions: {"<role_uuid>": true|false}. Advances status to roles_confirmed. '
                'Also accepts the detailed responses format for backwards compatibility.',
    request={'application/json': {'type': 'object', 'properties': {
        'decisions': {'type': 'object', 'description': '{"<role_id>": true|false}'},
    }}},
    responses={200: OpenApiResponse(description='Roles confirmed')},
    tags=['Candidates'],
)
@api_view(['POST'])
@permission_classes([IsCandidate])
def confirm_roles(request, candidate_id):
    """
    Alias for respond_roles. Accepts both:
      1. {decisions: {"<uuid>": true/false}}   ← frontend format
      2. {responses: [{role_id, response, ...}]} ← legacy format
    """
    try:
        c = Candidate.objects.get(id=candidate_id, user=request.user)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    decisions = request.data.get('decisions', {})
    if decisions:
        for role_id, confirmed in decisions.items():
            response_val = 'accepted' if confirmed else 'declined'
            RoleSuggestion.objects.filter(id=role_id, candidate=c).update(
                candidate_response=response_val, responded_at=now,
            )
    else:
        for r in request.data.get('responses', []):
            RoleSuggestion.objects.filter(id=r['role_id'], candidate=c).update(
                candidate_response=r.get('response', 'accepted'),
                change_request_note=r.get('change_request_note', ''),
                responded_at=now,
            )

    c.status = 'roles_candidate_responded'
    c.save()
    log_action(request.user, 'roles_confirmed', str(c.id), 'candidate')
    return Response({'message': 'Roles confirmed'})


@extend_schema(
    summary='List or submit referrals (frontend: GET+POST /referrals/)',
    responses={200: ReferralSerializer(many=True), 201: ReferralSerializer},
    tags=['Candidates'],
)
@api_view(['GET', 'POST'])
@permission_classes([IsApproved])
def referrals(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(ReferralSerializer(c.referrals.all(), many=True).data)

    # POST
    if request.user.role == 'candidate' and c.user != request.user:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    ser = ReferralSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    ref = ser.save(referrer=c)
    log_action(request.user, 'referral_submitted', str(ref.id), 'referral')
    return Response(ReferralSerializer(ref).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='List or log interviews (frontend: GET+POST /interviews/)',
    responses={200: InterviewLogSerializer(many=True), 201: InterviewLogSerializer},
    tags=['Candidates'],
)
@api_view(['GET', 'POST'])
@permission_classes([IsApproved])
def interviews(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(InterviewLogSerializer(
            InterviewLog.objects.filter(candidate=c), many=True
        ).data)

    ser = InterviewLogSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    interview = ser.save(candidate=c, created_by=request.user, updated_by=request.user)
    return Response(InterviewLogSerializer(interview).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary='Get or close placement (frontend: GET+POST /placement/)',
    description='GET returns current placement details. POST closes the placement (Admin).',
    responses={200: PlacementClosureSerializer, 201: PlacementClosureSerializer},
    tags=['Candidates'],
)
@api_view(['GET', 'POST'])
@permission_classes([IsApproved])
def placement(request, candidate_id):
    try:
        c = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        try:
            return Response(PlacementClosureSerializer(c.placement_closure).data)
        except PlacementClosure.DoesNotExist:
            return Response({})

    # POST — admin closes placement
    if request.user.role not in ('admin', 'team_lead', 'team_manager'):
        return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
    ser = PlacementClosureSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    p = ser.save(candidate=c, closed_by=request.user)
    c.status = 'placed_closed'
    c.save()
    log_action(request.user, 'placement_closed', str(c.id), 'candidate',
               {'employer': p.employer_name, 'role': p.role_placed_into})
    create_notification(c.user, 'Congratulations!',
                        'Your placement has been confirmed. Case closed successfully.')
    send_email(
        to=c.user.email,
        subject='Congratulations – Your Placement Has Been Confirmed',
        html=(
            f'<p>Your placement at <strong>{p.employer_name}</strong> '
            f'as <strong>{p.role_placed_into}</strong> has been confirmed. Start: {p.start_date}.</p>'
        ),
        email_type='placement_closed',
    )
    return Response(PlacementClosureSerializer(p).data, status=status.HTTP_201_CREATED)
