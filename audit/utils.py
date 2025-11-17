from .models import AuditLog

def log_action(actor=None, action='', target='', metadata=None):
    AuditLog.objects.create(actor=actor, action=action, target=target, metadata=metadata or {})
