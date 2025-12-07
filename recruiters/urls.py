from django.urls import path
from . import views

urlpatterns = [
    # Recruiter Authentication Endpoints
    path('login/', views.RecruiterLoginView.as_view(), name='recruiter-login'),
    path('register/', views.RecruiterRegistrationView.as_view(), name='recruiter-register'),
    path('me/', views.RecruiterMeView.as_view(), name='recruiter-me'),
    
    # Recruiter Management Endpoints (Admin Only)
    path('', views.RecruiterListView.as_view(), name='recruiter-list'),
    path('<uuid:id>/', views.RecruiterDetailView.as_view(), name='recruiter-detail'),
    path('<uuid:id>/activate/', views.RecruiterActivateView.as_view(), name='recruiter-activate'),
    path('<uuid:id>/deactivate/', views.RecruiterDeactivateView.as_view(), name='recruiter-deactivate'),
    
    # Recruiter Registration Form Endpoints (Comprehensive Onboarding)
    path('registration-form/', views.RecruiterRegistrationFormCreateView.as_view(), name='registration-form-create'),
    path('registration-forms/', views.RecruiterRegistrationFormListView.as_view(), name='registration-form-list'),
    path('registration-forms/<uuid:id>/', views.RecruiterRegistrationFormDetailView.as_view(), name='registration-form-detail'),
    path('registration-forms/<uuid:id>/verify/', views.RecruiterRegistrationFormVerifyView.as_view(), name='registration-form-verify'),
    
    # Assignment Operations
    path('assign/', views.AssignmentCreateView.as_view(), name='assignment-create'),
]
