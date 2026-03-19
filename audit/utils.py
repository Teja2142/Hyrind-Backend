from .models import AuditLog


def log_action(actor=None, action='', target_id='', target_type='', details=None):
    """
    Create an immutable audit log entry.

    Args:
        actor:       User instance or None for system actions
        action:      Audit event code (e.g. 'registration_created')
        target_id:   UUID/PK string of the affected record
        target_type: Model name (e.g. 'user', 'candidate')
        details:     Extra JSON-serialisable context dict
    """
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target_id=str(target_id) if target_id else '',
        target_type=target_type,
        details=details or {},
    )
