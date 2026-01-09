from django.urls import path
from . import views
from .views import LoginView

urlpatterns = [
    # ============================================================================
    # USER ENDPOINTS (Industry Standard RESTful API)
    # ============================================================================
    # List ALL users in system (clients, recruiters, admins)
    path('', views.UserList.as_view(), name='user-list'),
    # List ALL user profiles with detailed information
    path('profiles/', views.ProfileList.as_view(), name='profile-list'),
    # Get/Update/Delete specific user profile
    path('profiles/<uuid:id>/', views.ProfileRetrieveUpdateDestroy.as_view(), name='profile-detail'),
    
    # ============================================================================
    # CLIENT ENDPOINTS (Client-Specific Filtered Views)
    # ============================================================================
    # List ONLY clients (candidates seeking jobs) - excludes recruiters
    path('clients/', views.ClientListView.as_view(), name='client-list'),
    # List ONLY client profiles with detailed information - excludes recruiters
    path('clients/profiles/', views.ClientProfileList.as_view(), name='client-profile-list'),
    # Get/Update/Delete specific client profile (same as users/profiles/<id>/)
    path('clients/profiles/<uuid:id>/', views.ProfileRetrieveUpdateDestroy.as_view(), name='client-profile-detail'),
    
    # ============================================================================
    # PUBLIC ENDPOINTS (No Authentication Required)
    # ============================================================================
    # Client registration
    path('register/', views.RegistrationView.as_view(), name='user-register'),
    # Interest submission form
    path('interest/', views.InterestSubmissionCreateView.as_view(), name='interest-submit'),
    # Contact form submission
    path('contact/', views.ContactCreateView.as_view(), name='contact-submit'),
    
    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================
    # Client login
    path('login/', LoginView.as_view(), name='user-login'),
    # Get current logged-in user profile
    path('me/', views.CurrentUserProfileView.as_view(), name='current-user-profile'),
    
    # ============================================================================
    # PASSWORD MANAGEMENT ENDPOINTS
    # ============================================================================
    # Request password reset (Forgot Password on login page)
    path('password-reset/request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    # Confirm password reset with token from email
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # Change password (Dashboard settings - requires authentication)
    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # ============================================================================
    # ADMIN ENDPOINTS
    # ============================================================================
    # Admin profile management
    path('admin/profile/', views.AdminProfileView.as_view(), name='admin-profile'),
    # Admin registration
    path('admin/register/', views.AdminRegisterView.as_view(), name='admin-register'),
    # Admin password change
    path('admin/password/', views.AdminPasswordChangeView.as_view(), name='admin-password-change'),
    
    # ============================================================================
    # ADMIN CANDIDATE MANAGEMENT (Status Workflow)
    # ============================================================================
    # Approve candidate registration (open → approved) - grants login access
    path('admin/candidates/<uuid:id>/activate/', views.CandidateActivateView.as_view(), name='candidate-activate'),
    # Reject candidate registration (any → rejected) - revokes login access
    path('admin/candidates/<uuid:id>/deactivate/', views.CandidateDeactivateView.as_view(), name='candidate-deactivate'),
    # Mark candidate as placed (assigned → closed) - indicates successful placement
    path('admin/candidates/<uuid:id>/placed/', views.CandidateMarkPlacedView.as_view(), name='candidate-placed'),
]
