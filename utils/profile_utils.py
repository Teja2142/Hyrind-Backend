from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from users.models import Profile


def get_profile_by_id(profile_id):
    """Return a Profile instance for the given profile UUID id or raise NotFound.

    This centralizes the lookup logic so callers don't repeat imports or
    exception handling. Note: Profile.id is a UUID field (primary key).
    """
    try:
        return get_object_or_404(Profile, id=profile_id)
    except Exception:
        raise NotFound(detail='Profile not found')


class ProfileResolveMixin:
    """Mixin for views that need to resolve a Profile from request data.

    Exposes a helper method get_profile() which reads the 'profile' key from
    request.data (or kwargs) and returns a Profile or raises NotFound.
    Accepts either UUID string or profile id in various formats.
    """
    def get_profile(self):
        profile_id = None
        # allow profile in either json body or form data
        if hasattr(self, 'request') and self.request is not None:
            profile_id = self.request.data.get('profile') or self.request.data.get('profile_id')
        if not profile_id:
            profile_id = self.kwargs.get('id') or self.kwargs.get('pk') if hasattr(self, 'kwargs') else None
        if not profile_id:
            raise NotFound(detail='Profile identifier not provided')
        return get_profile_by_id(profile_id)
