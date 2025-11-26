from django.urls import path
from . import views

urlpatterns = [
    # Recruiter CRUD operations
    path('register/', views.RecruiterRegistrationView.as_view(), name='recruiter-register'),
    path('', views.RecruiterListView.as_view(), name='recruiter-list'),
    path('<int:id>/', views.RecruiterDetailView.as_view(), name='recruiter-detail'),
    
    # Assignment operations
    path('assign/', views.AssignmentCreateView.as_view(), name='assignment-create'),
]
