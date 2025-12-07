from django.urls import path
from . import web_views

urlpatterns = [
    path('', web_views.recruiter_registration_form_view, name='recruiter-web-register-root'),
    path('register/', web_views.recruiter_register_simple_view, name='recruiter-register'),
    path('login/', web_views.recruiter_login_view, name='recruiter-login'),
    path('profile/', web_views.recruiter_profile_view, name='recruiter-profile'),
    path('dashboard/', web_views.recruiter_dashboard_view, name='recruiter-dashboard'),
    path('logout/', web_views.recruiter_logout_view, name='recruiter-logout'),
]
