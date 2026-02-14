from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .recommendation_views import JobRoleViewSet, RoleRecommendationViewSet, UserSkillProfileViewSet

# Router for ViewSets
router = DefaultRouter()
router.register(r'roles', JobRoleViewSet, basename='job-role')
router.register(r'recommendations', RoleRecommendationViewSet, basename='recommendation')
router.register(r'skill-profile', UserSkillProfileViewSet, basename='skill-profile')

urlpatterns = [
    path('', views.JobListCreate.as_view(), name='job-list-create'),
    path('<int:pk>/', views.JobDetail.as_view(), name='job-detail'),
    
    # Include router URLs for recommendations
    path('', include(router.urls)),
]
