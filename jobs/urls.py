from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .recommendation_views import RoleSuggestionViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r'suggestions', RoleSuggestionViewSet, basename='role-suggestion')

urlpatterns = [
    path('', views.JobListCreate.as_view(), name='job-list-create'),
    path('<uuid:pk>/', views.JobDetail.as_view(), name='job-detail'),
    
    # Include router URLs for role suggestions
    path('', include(router.urls)),
]
