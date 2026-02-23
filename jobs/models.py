from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class UserRoleSuggestion(models.Model):
    """
    Simple role suggestions: Admin suggests → User selects → User submits
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_suggestions')
    
    # Role details (admin types directly)
    role_title = models.CharField(max_length=200, db_index=True)
    role_category = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Admin who suggested this
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_role_suggestions')
    admin_notes = models.TextField(blank=True)
    
    # User actions
    is_selected = models.BooleanField(default=False, db_index=True)
    selected_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Role Suggestion'
        verbose_name_plural = 'Role Suggestions'
        # Optimized indexes for common queries
        indexes = [
            models.Index(fields=['user', 'is_selected']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['submitted_at']),
        ]
        # Prevent duplicate role suggestions for same user
        unique_together = [['user', 'role_title']]
    
    def __str__(self):
        status = "✓" if self.is_selected else "○"
        return f"{self.user.username} -> {self.role_title} ({status})"
    
    def select(self):
        """User selects this role"""
        self.is_selected = True
        self.selected_at = timezone.now()
        self.save(update_fields=['is_selected', 'selected_at'])
    
    def deselect(self):
        """User deselects this role"""
        self.is_selected = False
        self.selected_at = None
        self.save(update_fields=['is_selected', 'selected_at'])
    
    def submit(self):
        """Mark as submitted (called when user submits final selection)"""
        if self.is_selected:
            self.submitted_at = timezone.now()
            self.save(update_fields=['submitted_at'])

# Backward compatibility alias
UserRoleRecommendation = UserRoleSuggestion
