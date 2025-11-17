from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from users.models import Profile


def get_profile_by_public_id(public_id):
    """Return a Profile instance for the given public_id or raise NotFound.

    This centralizes the lookup logic so callers don't repeat imports or
    exception handling.
    """
    try:
        return get_object_or_404(Profile, public_id=public_id)
    except Exception:
        raise NotFound(detail='Profile not found')


class ProfileResolveMixin:
    """Mixin for views that need to resolve a Profile from request data.

    Exposes a helper method get_profile() which reads the 'profile' key from
    request.data (or kwargs) and returns a Profile or raises NotFound.
    """
    def get_profile(self):
        public_id = None
        # allow profile in either json body or form data
        if hasattr(self, 'request') and self.request is not None:
            public_id = self.request.data.get('profile') or self.request.data.get('profile_public_id')
        if not public_id:
            public_id = self.kwargs.get('public_id') if hasattr(self, 'kwargs') else None
        if not public_id:
            raise NotFound(detail='Profile identifier not provided')
        return get_profile_by_public_id(public_id)
