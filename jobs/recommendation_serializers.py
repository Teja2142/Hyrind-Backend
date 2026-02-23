"""
Serializers for role suggestions API
Ultra-simple serializers for admin-managed role suggestions
"""
from rest_framework import serializers
from .models import UserRoleSuggestion


class RoleSuggestionSerializer(serializers.ModelSerializer):
    """Simple serializer for role suggestions"""
    added_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRoleSuggestion
        fields = [
            'id', 'role_title', 'role_category', 'admin_notes',
            'is_selected', 'selected_at', 'submitted_at',
            'added_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'added_by_name', 'selected_at', 'submitted_at', 'created_at']
    
    def get_added_by_name(self, obj):
        """Get the name of admin who added this suggestion"""
        if obj.added_by:
            if hasattr(obj.added_by, 'profile'):
                profile = obj.added_by.profile
                return f"{profile.first_name} {profile.last_name}".strip() or obj.added_by.username
            return obj.added_by.username
        return "System"


class BulkCreateRoleSuggestionsSerializer(serializers.Serializer):
    """
    Serializer for bulk creating role suggestions (Admin API)
    Accepts multiple role titles at once
    """
    user_id = serializers.IntegerField(
        help_text="User ID to receive role suggestions",
        required=True
    )
    role_titles = serializers.ListField(
        child=serializers.CharField(max_length=200),
        help_text="List of role titles (1-10 roles)",
        min_length=1,
        max_length=10
    )
    role_category = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional category for all roles (e.g., Engineering)"
    )
    admin_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes applied to all suggestions"
    )
    
    def validate_role_titles(self, value):
        """Validate role titles"""
        # Remove duplicates while preserving order
        unique_titles = []
        seen = set()
        for title in value:
            title_clean = title.strip()
            if title_clean and title_clean not in seen:
                unique_titles.append(title_clean)
                seen.add(title_clean)
        
        if not unique_titles:
            raise serializers.ValidationError("At least one valid role title is required.")
        
        return unique_titles
    
    def validate_user_id(self, value):
        """Validate user exists"""
        from django.contrib.auth.models import User
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("User not found or inactive.")
        return value


class RoleSuggestionUpdateSerializer(serializers.Serializer):
    """Serializer for updating role selection status"""
    is_selected = serializers.BooleanField(required=True)


class BulkRoleSuggestionUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating role selections"""
    suggestion_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of role suggestion IDs to mark as selected"
    )
