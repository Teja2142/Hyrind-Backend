from django.urls import path
from . import views

# API endpoints for recruiters (JSON REST API)
urlpatterns = [
    # ============================================================================
    # AUTHENTICATION & PROFILE - For recruiters
    # ============================================================================
    path('register/', views.RecruiterRegistrationView.as_view(), name='recruiter-api-register'),
    path('login/', views.RecruiterLoginView.as_view(), name='recruiter-api-login'),
    path('me/', views.RecruiterMeView.as_view(), name='recruiter-me'),
    path('dashboard/', views.RecruiterDashboardView.as_view(), name='recruiter-api-dashboard'),

    # ============================================================================
    # ADMIN MANAGEMENT - Admin only endpoints
    # ============================================================================
    path('', views.RecruiterListView.as_view(), name='recruiter-list'),
    path('<uuid:id>/', views.RecruiterDetailView.as_view(), name='recruiter-detail'),
    path('<uuid:id>/activate/', views.RecruiterActivateView.as_view(), name='recruiter-activate'),
    path('<uuid:id>/deactivate/', views.RecruiterDeactivateView.as_view(), name='recruiter-deactivate'),
    # availability_status is updated via PATCH /api/recruiters/<id>/ (RecruiterAdminUpdateSerializer)

    # ============================================================================
    # ASSIGNMENT ENDPOINTS
    # ============================================================================
    # Create a new assignment (admin assigns a client to a recruiter)
    path('assign/', views.AssignmentCreateView.as_view(), name='assignment-create'),

    # List all assignments with filters
    path('assignments/', views.AssignmentListView.as_view(), name='assignment-list'),

    # Reassign a client from one recruiter to another (when recruiter is absent)
    path('assignments/<uuid:id>/reassign/', views.ReassignClientView.as_view(), name='assignment-reassign'),
]
