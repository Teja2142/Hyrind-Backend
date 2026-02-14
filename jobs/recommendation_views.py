"""
Views and API endpoints for role recommendations
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import (
    JobRole, UserRoleRecommendation, UserSkillProfile, RecommendationFeedback
)
from .recommendation_serializers import (
    JobRoleSerializer, JobRoleSummarySerializer,
    UserRoleRecommendationSerializer, UserRoleRecommendationSummarySerializer,
    UserSkillProfileSerializer, RecommendationFeedbackSerializer,
    RecommendationActionSerializer, GenerateRecommendationsSerializer
)
from .recommendation_engine import RoleRecommendationEngine


class JobRoleViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for job roles (Admin only for create/update/delete)
    
    Endpoints:
    - GET /api/job-roles/ - List all job roles
    - GET /api/job-roles/{id}/ - Get job role detail
    - POST /api/job-roles/ - Create job role (Admin only)
    - PUT/PATCH /api/job-roles/{id}/ - Update job role (Admin only)
    - DELETE /api/job-roles/{id}/ - Delete job role (Admin only)
    """
    queryset = JobRole.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'list':
            return JobRoleSummarySerializer
        return JobRoleSerializer
    
    def get_permissions(self):
        """Allow read for authenticated, write for admin only"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Get list of all job categories
        
        GET /api/job-roles/categories/
        """
        categories = JobRole.objects.filter(is_active=True).values_list('category', flat=True).distinct()
        return Response({
            'categories': sorted(list(categories))
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get job roles grouped by category
        
        GET /api/job-roles/by_category/
        """
        categories = JobRole.objects.filter(is_active=True).values_list('category', flat=True).distinct()
        
        result = {}
        for category in categories:
            roles = JobRole.objects.filter(is_active=True, category=category)
            result[category] = JobRoleSummarySerializer(roles, many=True).data
        
        return Response(result)


class RoleRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for role recommendations
    
    Endpoints:
    - GET /api/recommendations/ - List recommendations for authenticated user
    - GET /api/recommendations/{id}/ - Get recommendation detail
    - POST /api/recommendations/generate/ - Generate new recommendations
    - POST /api/recommendations/{id}/action/ - Mark interested/dismissed
    - POST /api/recommendations/{id}/feedback/ - Submit feedback
    - GET /api/recommendations/by_category/ - Get recommendations by category
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return recommendations for authenticated user"""
        user = self.request.user
        
        # Admin can see all recommendations with user filter
        if user.is_staff and 'user_id' in self.request.query_params:
            user_id = self.request.query_params.get('user_id')
            return UserRoleRecommendation.objects.filter(user_id=user_id).select_related('role', 'user')
        
        # Regular users see only their recommendations
        return UserRoleRecommendation.objects.filter(user=user).select_related('role')
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'list':
            return UserRoleRecommendationSummarySerializer
        return UserRoleRecommendationSerializer
    
    def list(self, request, *args, **kwargs):
        """List recommendations with filters"""
        queryset = self.get_queryset()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter == 'interested':
            queryset = queryset.filter(is_interested=True)
        elif status_filter == 'dismissed':
            queryset = queryset.filter(is_dismissed=True)
        elif status_filter == 'new':
            queryset = queryset.filter(is_interested=False, is_dismissed=False)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(role__category=category)
        
        # Filter by minimum score
        min_score = request.query_params.get('min_score')
        if min_score:
            try:
                queryset = queryset.filter(match_score__gte=float(min_score))
            except ValueError:
                pass
        
        # Order by match score (default) or other fields
        ordering = request.query_params.get('ordering', '-match_score')
        queryset = queryset.order_by(ordering)
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Add summary stats
        total_count = queryset.count()
        interested_count = queryset.filter(is_interested=True).count()
        dismissed_count = queryset.filter(is_dismissed=True).count()
        
        return Response({
            'count': total_count,
            'interested_count': interested_count,
            'dismissed_count': dismissed_count,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate new recommendations for authenticated user
        
        POST /api/recommendations/generate/
        Body:
        {
            "limit": 10,  // Optional, default 10
            "force_refresh": false,  // Optional, default false
            "category": "Engineering"  // Optional
        }
        """
        serializer = GenerateRecommendationsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        limit = serializer.validated_data.get('limit', 10)
        force_refresh = serializer.validated_data.get('force_refresh', False)
        category = serializer.validated_data.get('category')
        
        try:
            # Generate recommendations
            recommendations = RoleRecommendationEngine.generate_recommendations(
                user=request.user,
                limit=limit,
                force_refresh=force_refresh
            )
            
            # Filter by category if specified
            if category:
                recommendations = recommendations.filter(role__category=category)
            
            response_serializer = UserRoleRecommendationSummarySerializer(recommendations, many=True)
            
            return Response({
                'message': 'Recommendations generated successfully',
                'count': recommendations.count(),
                'recommendations': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def perform_action(self, request, pk=None):
        """
        Perform action on recommendation (interested, dismiss, view)
        
        POST /api/recommendations/{id}/perform_action/
        Body:
        {
            "action": "interested" | "dismiss" | "view"
        }
        """
        recommendation = self.get_object()
        
        serializer = RecommendationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        
        if action_type == 'interested':
            recommendation.mark_interested()
            message = 'Marked as interested'
        elif action_type == 'dismiss':
            recommendation.dismiss()
            message = 'Recommendation dismissed'
        elif action_type == 'view':
            recommendation.mark_as_viewed()
            message = 'Marked as viewed'
        
        return Response({
            'message': message,
            'recommendation': UserRoleRecommendationSerializer(recommendation).data
        })
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """
        Submit feedback for a recommendation
        
        POST /api/recommendations/{id}/feedback/
        Body:
        {
            "feedback_type": "helpful" | "not_relevant" | "too_senior" | "too_junior" | "wrong_skills" | "wrong_location" | "other",
            "comment": "Optional comment"
        }
        """
        recommendation = self.get_object()
        
        serializer = RecommendationFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        feedback = RecommendationFeedback.objects.create(
            recommendation=recommendation,
            **serializer.validated_data
        )
        
        return Response({
            'message': 'Feedback submitted successfully',
            'feedback': RecommendationFeedbackSerializer(feedback).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get recommendations grouped by category
        
        GET /api/recommendations/by_category/
        """
        limit_per_category = int(request.query_params.get('limit', 5))
        
        recommendations_by_category = RoleRecommendationEngine.get_recommendations_by_category(
            user=request.user,
            limit_per_category=limit_per_category
        )
        
        # Serialize
        result = {}
        for category, recs in recommendations_by_category.items():
            result[category] = UserRoleRecommendationSummarySerializer(recs, many=True).data
        
        return Response(result)


class UserSkillProfileViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for user skill profiles
    
    Endpoints:
    - GET /api/skill-profile/ - Get authenticated user's skill profile
    - PUT/PATCH /api/skill-profile/ - Update skill profile
    - POST /api/skill-profile/sync/ - Sync from intake sheet
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSkillProfileSerializer
    
    def get_queryset(self):
        """Return skill profile for authenticated user"""
        user = self.request.user
        
        # Admin can see all profiles with user filter
        if user.is_staff and 'user_id' in self.request.query_params:
            user_id = self.request.query_params.get('user_id')
            return UserSkillProfile.objects.filter(user_id=user_id)
        
        return UserSkillProfile.objects.filter(user=user)
    
    def list(self, request, *args, **kwargs):
        """Get user's skill profile (single object)"""
        try:
            profile = UserSkillProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserSkillProfile.DoesNotExist:
            return Response({
                'message': 'Skill profile not found. Please sync from intake sheet.',
                'profile': None
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        Sync skill profile from intake sheet
        
        POST /api/skill-profile/sync/
        """
        try:
            skill_profile = RoleRecommendationEngine.sync_skill_profile_from_intake(request.user)
            
            return Response({
                'message': 'Skill profile synced successfully',
                'profile': UserSkillProfileSerializer(skill_profile).data
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
