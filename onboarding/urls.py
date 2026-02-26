from django.urls import path
from . import views

urlpatterns = [
    path('', views.OnboardingListCreateView.as_view(), name='onboarding-list-create'),
    path('<uuid:pk>/', views.OnboardingRetrieveUpdateView.as_view(), name='onboarding-detail'),
]
