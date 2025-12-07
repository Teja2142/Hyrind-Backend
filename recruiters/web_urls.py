from django.urls import path
from . import web_views

# Web-based recruiter portal URLs (HTML forms)
urlpatterns = [
    # Registration - SINGLE unified endpoint
    path('', web_views.recruiter_registration_view, name='recruiter-web-register'),
    path('register/', web_views.recruiter_registration_view, name='recruiter-register-alt'),  # Redirect alias
    
    # Authentication
    path('login/', web_views.recruiter_login_view, name='recruiter-login'),
    path('logout/', web_views.recruiter_logout_view, name='recruiter-logout'),
    
    # Authenticated pages
    path('dashboard/', web_views.recruiter_dashboard_view, name='recruiter-dashboard'),
    path('profile/', web_views.recruiter_profile_view, name='recruiter-profile'),
    path('complete-profile/', web_views.recruiter_complete_profile_view, name='recruiter-complete-profile'),
]
