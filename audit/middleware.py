from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Lightweight request logging middleware.
    Only logs authenticated API calls; skips static, media, schema, and admin.
    """
    SKIP_PREFIXES = ('/static/', '/media/', '/api/schema/', '/admin/')

    def process_request(self, request):
        try:
            if not getattr(settings, 'AUDIT_LOG_REQUESTS', False):
                return None
            if any(request.path.startswith(p) for p in self.SKIP_PREFIXES):
                return None
            if not request.path.startswith('/api/'):
                return None

            user = (
                request.user
                if hasattr(request, 'user') and request.user.is_authenticated
                else None
            )

            from .utils import log_action
            log_action(
                actor=user,
                action='http_request',
                target_id=request.path,
                target_type='http',
                details={'method': request.method},
            )
        except Exception:
            pass
        return None
