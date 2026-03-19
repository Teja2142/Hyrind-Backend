from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to admin users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsApproved(BasePermission):
    """Allow access only to fully approved portal users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.approval_status == 'approved'
            and request.user.portal_access
        )


class IsAdminOrTeamLead(BasePermission):
    """Admin, team_lead, or team_manager."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('admin', 'team_lead', 'team_manager')
        )


class IsRecruiter(BasePermission):
    """Recruiter or any internal team role."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('recruiter', 'team_lead', 'team_manager', 'admin')
        )


class IsCandidate(BasePermission):
    """Candidate role only."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'candidate'
        )


class IsSelfOrAdmin(BasePermission):
    """Object-level: user can access their own record; admin can access any."""
    def has_object_permission(self, request, view, obj):
        user_id = getattr(obj, 'user_id', None) or getattr(obj, 'id', None)
        return request.user.role == 'admin' or str(request.user.id) == str(user_id)