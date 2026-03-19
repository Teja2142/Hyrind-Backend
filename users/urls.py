from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from . import views

# Give the built-in TokenRefreshView a clean Swagger schema
TokenRefreshView = extend_schema(
    summary='Refresh access token',
    tags=['Auth'],
    responses={
        200: {'type': 'object', 'properties': {
            'access': {'type': 'string', 'description': 'New short-lived access token'},
        }},
    },
)(TokenRefreshView)

urlpatterns = [
    # ── Public auth ──────────────────────────────────────────────────────
    path('register/',      views.register,              name='auth-register'),
    path('login/',         views.login,                  name='auth-login'),
    path('refresh/',       TokenRefreshView.as_view(),   name='token-refresh'),

    # ── Authenticated user ─────────────────────────────────
    path('logout/',          views.logout,          name='auth-logout'),
    path('me/',              views.me,               name='auth-me'),
    path('profile/',         views.update_profile,  name='auth-update-profile'),
    path('password-change/', views.change_password, name='auth-change-password'),

    # ── Password reset (public) ─────────────────────────────────
    path('password-reset/',         views.password_reset_request, name='auth-password-reset'),
    path('password-reset/confirm/', views.password_reset_confirm, name='auth-password-reset-confirm'),

    # ── Admin ───────────────────────────────────────────
    path('pending-approvals/',  views.pending_approvals, name='auth-pending'),
    path('approve-user/',       views.approve_user,      name='auth-approve'),
    path('users/',              views.user_list,         name='auth-user-list'),
]
