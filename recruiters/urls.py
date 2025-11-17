from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.RecruiterListView.as_view(), name='recruiter-list'),
    path('assign/', views.AssignmentCreateView.as_view(), name='assignment-create'),
]
