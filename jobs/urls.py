from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListCreate.as_view(), name='job-list-create'),
    path('<int:pk>/', views.JobDetail.as_view(), name='job-detail'),
]
