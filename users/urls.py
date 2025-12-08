from django.urls import path
from . import views
from .views import LoginView

urlpatterns = [
    # User & Profile Endpoints
    path('', views.UserList.as_view(), name='user-list'),
    path('profiles/', views.ProfileList.as_view(), name='profile-list'),
    path('profiles/<uuid:id>/', views.ProfileRetrieveUpdateDestroy.as_view(), name='profile-detail'),
    
    # Public Registration & Submission Endpoints
    path('register/', views.RegistrationView.as_view(), name='user-register'),
    path('interest/', views.InterestSubmissionCreateView.as_view(), name='interest-submit'),
    path('contact/', views.ContactCreateView.as_view(), name='contact-submit'),
    
    # Authentication
    path('login/', LoginView.as_view(), name='user-login'),
    
    # Admin Endpoints
    path('admin/profile/', views.AdminProfileView.as_view(), name='admin-profile'),
    path('admin/password/', views.AdminPasswordChangeView.as_view(), name='admin-password-change'),
    path('admin/candidates/<uuid:id>/activate/', views.CandidateActivateView.as_view(), name='candidate-activate'),
    path('admin/candidates/<uuid:id>/deactivate/', views.CandidateDeactivateView.as_view(), name='candidate-deactivate'),
]
