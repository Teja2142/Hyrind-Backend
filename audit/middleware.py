from django.utils.deprecation import MiddlewareMixin
from .utils import log_action
from django.conf import settings

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            if not getattr(settings, 'AUDIT_LOG_REQUESTS', True):
                return None
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            path = request.path
            method = request.method
            log_action(actor=user, action='http_request', target=path, metadata={'method': method})
        except Exception:
            pass
        return None
