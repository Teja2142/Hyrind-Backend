"""
Views and API endpoints for role suggestions
Ultra-simple API where admins type role titles directly
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from .models import UserRoleSuggestion
from .recommendation_serializers import (
    RoleSuggestionSerializer, RoleSuggestionUpdateSerializer,
    BulkRoleSuggestionUpdateSerializer, BulkCreateRoleSuggestionsSerializer
)


class RoleSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for role suggestions
    Users can view their suggestions and select/deselect them
    
    Endpoints:
    - GET /api/jobs/suggestions/ - List role suggestions for authenticated user
    - GET /api/jobs/suggestions/{id}/ - Get suggestion detail
    - PATCH /api/jobs/suggestions/{id}/toggle/ - Toggle selection status
    - POST /api/jobs/suggestions/submit/ - Submit selected suggestions
    - POST /api/jobs/suggestions/bulk_select/ - Bulk select multiple suggestions
    - POST /api/jobs/suggestions/bulk_create/ - Bulk create suggestions (Admin only)
    - GET /api/jobs/suggestions/by_category/ - Get suggestions grouped by category
    - GET /api/jobs/suggestions/categories/ - Get list of all categories
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSuggestionSerializer
    
    def get_queryset(self):
        """Return suggestions for authenticated user"""
        # Avoid querying during Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return UserRoleSuggestion.objects.none()
        
        return UserRoleSuggestion.objects.filter(
            user=self.request.user
        ).select_related('added_by')
    
    def list(self, request, *args, **kwargs):
        """List suggestions with summary stats"""
        queryset = self.get_queryset()
        
        # Filter by selection status
        status_filter = request.query_params.get('status')
        if status_filter == 'selected':
            queryset = queryset.filter(is_selected=True)
        elif status_filter == 'unselected':
            queryset = queryset.filter(is_selected=False)
        elif status_filter == 'submitted':
            queryset = queryset.filter(submitted_at__isnull=False)
        elif status_filter == 'pending':
            queryset = queryset.filter(submitted_at__isnull=True)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(role_category__iexact=category)
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Summary stats
        total_count = queryset.count()
        selected_count = queryset.filter(is_selected=True).count()
        submitted_count = queryset.filter(submitted_at__isnull=False).count()
        
        # Group by category
        categories = {}
        for suggestion in queryset:
            cat = suggestion.role_category or 'Uncategorized'
            if cat not in categories:
                categories[cat] = {
                    'total': 0,
                    'selected': 0,
                    'submitted': 0,
                    'roles': []
                }
            categories[cat]['total'] += 1
            if suggestion.is_selected:
                categories[cat]['selected'] += 1
            if suggestion.submitted_at:
                categories[cat]['submitted'] += 1
            categories[cat]['roles'].append(RoleSuggestionSerializer(suggestion).data)
        
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username
            },
            'summary': {
                'total': total_count,
                'selected': selected_count,
                'unselected': total_count - selected_count,
                'submitted': submitted_count,
                'pending': total_count - submitted_count
            },
            'suggestions': serializer.data,
            'grouped_by_category': categories
        })
    
    @action(detail=True, methods=['patch'])
    def toggle(self, request, pk=None):
        """
        Toggle selection status for a role suggestion
        
        PATCH /api/jobs/suggestions/{id}/toggle/
        Body:
        {
            "is_selected": true/false
        }
        """
        suggestion = self.get_object()
        
        serializer = RoleSuggestionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        is_selected = serializer.validated_data['is_selected']
        
        if is_selected:
            suggestion.select()
            message = 'Role selected successfully'
        else:
            suggestion.deselect()
            message = 'Role deselected successfully'
        
        return Response({
            'message': message,
            'suggestion': RoleSuggestionSerializer(suggestion).data
        })
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """
        Submit selected roles (marks them as finalized)
        
        POST /api/jobs/suggestions/submit/
        """
        selected_suggestions = self.get_queryset().filter(is_selected=True)
        
        if not selected_suggestions.exists():
            return Response({
                'message': 'No roles selected',
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark all as submitted
        submitted_at = timezone.now()
        for suggestion in selected_suggestions:
            suggestion.submit()
        
        return Response({
            'message': f'Successfully submitted {selected_suggestions.count()} role(s)',
            'count': selected_suggestions.count(),
            'submitted_at': submitted_at.isoformat(),
            'selections': RoleSuggestionSerializer(selected_suggestions, many=True).data
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def bulk_create(self, request):
        """
        Bulk create role suggestions for a user (Admin only)
        
        POST /api/jobs/suggestions/bulk_create/
        Body:
        {
            "user_id": 123,
            "role_titles": ["Software Engineer", "Data Analyst", "Backend Developer"],
            "role_category": "Engineering",  // optional
            "admin_notes": "Based on your profile"  // optional
        }
        
        Response:
        {
            "message": "Successfully created 3 role suggestions",
            "created_count": 3,
            "skipped_count": 0,
            "suggestions": [...]
        }
        """
        serializer = BulkCreateRoleSuggestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(id=serializer.validated_data['user_id'])
        role_titles = serializer.validated_data['role_titles']
        role_category = serializer.validated_data.get('role_category', '')
        admin_notes = serializer.validated_data.get('admin_notes', '')
        
        created_suggestions = []
        skipped_count = 0
        
        for role_title in role_titles:
            # Check if suggestion already exists
            existing = UserRoleSuggestion.objects.filter(
                user=user,
                role_title=role_title
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Create new suggestion
            suggestion = UserRoleSuggestion.objects.create(
                user=user,
                role_title=role_title,
                role_category=role_category,
                admin_notes=admin_notes,
                added_by=request.user
            )
            created_suggestions.append(suggestion)
        
        created_count = len(created_suggestions)
        
        # Better structured response
        return Response({
            'message': f'Successfully created {created_count} role suggestion(s) for {user.username}',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'summary': {
                'total_submitted': len(role_titles),
                'created': created_count,
                'skipped': skipped_count,
                'category': role_category or 'Uncategorized'
            },
            'suggestions': {
                'created': RoleSuggestionSerializer(created_suggestions, many=True).data,
                'skipped': [title for title in role_titles if UserRoleSuggestion.objects.filter(
                    user=user, role_title=title
                ).exists() and title not in [s.role_title for s in created_suggestions]]
            }
        }, status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def bulk_select(self, request):
        """
        Bulk select multiple suggestions at once
        
        POST /api/jobs/suggestions/bulk_select/
        Body:
        {
            "suggestion_ids": ["uuid1", "uuid2", ...]
        }
        """
        serializer = BulkRoleSuggestionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        suggestion_ids = serializer.validated_data['suggestion_ids']
        
        # Update suggestions belonging to the current user
        updated_count = UserRoleSuggestion.objects.filter(
            id__in=suggestion_ids,
            user=request.user
        ).update(is_selected=True)
        
        return Response({
            'message': f'Successfully selected {updated_count} suggestions',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get suggestions grouped by category
        
        GET /api/jobs/suggestions/by_category/
        """
        queryset = self.get_queryset()
        categories = queryset.exclude(role_category='').values_list('role_category', flat=True).distinct()
        
        result = {}
        for category in categories:
            suggestions = queryset.filter(role_category=category)
            result[category] = RoleSuggestionSerializer(suggestions, many=True).data
        
        # Add uncategorized if any
        uncategorized = queryset.filter(role_category='')
        if uncategorized.exists():
            result['Uncategorized'] = RoleSuggestionSerializer(uncategorized, many=True).data
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Get list of all unique categories from user's suggestions
        
        GET /api/jobs/suggestions/categories/
        """
        categories = self.get_queryset().exclude(
            role_category=''
        ).values_list('role_category', flat=True).distinct()
        
        return Response({
            'categories': sorted(categories)
        })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_role_suggestions(request, profile_id):
    """
    GET /api/users/profiles/{profile_id}/role-suggestions/ - Get role suggestions for specific profile (Admin)
    
    Admin endpoint to fetch all role suggestions for any user by their profile UUID.
    
    Parameters:
        profile_id (UUID): Profile UUID of the user
    
    Returns:
        - user: User details (id, username, email, profile_id)
        - summary: Statistics (total, selected, unselected, submitted, pending)
        - suggestions: List of all role suggestions for this user
    
    Access: Admin only
    """
    try:
        from users.models import Profile
        profile = Profile.objects.select_related('user').get(id=profile_id)
        user = profile.user
    except Profile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    suggestions = UserRoleSuggestion.objects.filter(user=user).select_related('added_by')
    serializer = RoleSuggestionSerializer(suggestions, many=True)
    
    # Summary stats
    total_count = suggestions.count()
    selected_count = suggestions.filter(is_selected=True).count()
    submitted_count = suggestions.filter(submitted_at__isnull=False).count()
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'profile_id': str(profile.id)
        },
        'summary': {
            'total': total_count,
            'selected': selected_count,
            'unselected': total_count - selected_count,
            'submitted': submitted_count,
            'pending': total_count - submitted_count
        },
        'suggestions': serializer.data
    }, status=status.HTTP_200_OK)
