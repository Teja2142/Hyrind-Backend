from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from users.permissions import IsAdmin
from .models import AuditLog


@extend_schema(
    summary='List audit logs (Admin)',
    parameters=[
        OpenApiParameter('action',      description='Filter by action code', required=False),
        OpenApiParameter('target_type', description='Filter by target type', required=False),
        OpenApiParameter('target_id',   description='Filter by target ID',   required=False),
    ],
    tags=['Audit'],
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def audit_log_list(request):
    qs = AuditLog.objects.select_related('actor').order_by('-created_at')
    if action := request.query_params.get('action'):
        qs = qs.filter(action=action)
    if ttype := request.query_params.get('target_type'):
        qs = qs.filter(target_type=ttype)
    if tid := request.query_params.get('target_id'):
        qs = qs.filter(target_id=tid)
    qs = qs[:200]
    data = [
        {
            'id':          str(log.id),
            'actor':       log.actor.email if log.actor else None,
            'action':      log.action,
            'target_id':   log.target_id,
            'target_type': log.target_type,
            'details':     log.details,
            'created_at':  log.created_at,
        }
        for log in qs
    ]
    return Response(data)


@extend_schema(
    summary='List audit logs for a specific candidate (Admin)',
    parameters=[
        OpenApiParameter('action', description='Filter by action code', required=False),
    ],
    tags=['Audit'],
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def audit_candidate_logs(request, candidate_id):
    qs = AuditLog.objects.select_related('actor').filter(
        target_type='candidate', target_id=str(candidate_id)
    ).order_by('-created_at')
    if action := request.query_params.get('action'):
        qs = qs.filter(action=action)
    qs = qs[:200]
    data = [
        {
            'id':          str(log.id),
            'actor':       log.actor.email if log.actor else None,
            'action':      log.action,
            'target_id':   log.target_id,
            'target_type': log.target_type,
            'details':     log.details,
            'created_at':  log.created_at,
        }
        for log in qs
    ]
    return Response(data)
