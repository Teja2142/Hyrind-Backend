from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
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


class JobRole(models.Model):
    """
    Master job roles database for recommendations
    Admin-managed list of common job titles/roles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True, help_text='Job role title (e.g., Software Engineer, Data Analyst)')
    category = models.CharField(max_length=100, help_text='Category (e.g., Engineering, Data Science, Marketing)')
    description = models.TextField(blank=True, help_text='Role description')
    
    # Required skills/keywords for matching
    required_skills = models.JSONField(default=list, help_text='List of required skills (e.g., ["Python", "Django", "REST API"])')
    preferred_skills = models.JSONField(default=list, help_text='List of preferred/nice-to-have skills')
    
    # Experience requirements
    min_years_experience = models.IntegerField(default=0, help_text='Minimum years of experience')
    max_years_experience = models.IntegerField(null=True, blank=True, help_text='Maximum years of experience')
    
    # Education requirements
    required_degrees = models.JSONField(default=list, help_text='Required degrees (e.g., ["Bachelor\'s", "Master\'s"])')
    
    # Common alternative titles
    alternative_titles = models.JSONField(default=list, help_text='Alternative job titles (e.g., ["SWE", "Software Dev"])')
    
    # Metadata
    avg_salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Average minimum salary')
    avg_salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Average maximum salary')
    
    is_active = models.BooleanField(default=True, help_text='Whether this role is active for recommendations')
    popularity_score = models.IntegerField(default=0, help_text='Popularity score (higher = more common)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity_score', 'title']
        verbose_name = 'Job Role'
        verbose_name_plural = 'Job Roles'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active', '-popularity_score']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.category})"


class UserRoleRecommendation(models.Model):
    """
    Tracks role recommendations for users
    Stores recommendation scores and reasons
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_recommendations')
    role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='recommendations')
    
    # Recommendation scoring
    match_score = models.DecimalField(max_digits=5, decimal_places=2, help_text='Match score (0-100)')
    skill_match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Skills match score')
    experience_match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Experience match score')
    education_match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Education match score')
    
    # Matching details
    matched_skills = models.JSONField(default=list, help_text='List of matched skills')
    missing_skills = models.JSONField(default=list, help_text='List of missing required skills')
    recommendation_reason = models.TextField(blank=True, help_text='Explanation for why this role is recommended')
    
    # User interaction
    is_interested = models.BooleanField(default=False, help_text='User indicated interest')
    is_dismissed = models.BooleanField(default=False, help_text='User dismissed this recommendation')
    viewed_at = models.DateTimeField(null=True, blank=True, help_text='When user viewed this recommendation')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-match_score', '-created_at']
        unique_together = ['user', 'role']
        verbose_name = 'User Role Recommendation'
        verbose_name_plural = 'User Role Recommendations'
        indexes = [
            models.Index(fields=['user', '-match_score']),
            models.Index(fields=['is_interested']),
        ]
    
    def __str__(self):
        return f"{self.user.username} -> {self.role.title} (Score: {self.match_score})"
    
    def mark_as_viewed(self):
        """Mark recommendation as viewed"""
        if not self.viewed_at:
            self.viewed_at = timezone.now()
            self.save(update_fields=['viewed_at'])
    
    def mark_interested(self):
        """Mark user as interested in this role"""
        self.is_interested = True
        self.is_dismissed = False
        self.save(update_fields=['is_interested', 'is_dismissed'])
    
    def dismiss(self):
        """Dismiss this recommendation"""
        self.is_dismissed = True
        self.is_interested = False
        self.save(update_fields=['is_dismissed', 'is_interested'])


class UserSkillProfile(models.Model):
    """
    User's skill profile for better role matching
    Automatically populated from ClientIntakeSheet and can be updated
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='skill_profile')
    
    # Skills (parsed from intake sheet and user updates)
    primary_skills = models.JSONField(default=list, help_text='Primary/expert skills')
    secondary_skills = models.JSONField(default=list, help_text='Secondary/intermediate skills')
    learning_skills = models.JSONField(default=list, help_text='Currently learning')
    
    # Experience
    total_years_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0, help_text='Total years of professional experience')
    industries = models.JSONField(default=list, help_text='Industries worked in')
    
    # Education
    highest_degree = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    
    # Preferences
    desired_roles = models.JSONField(default=list, help_text='User-specified desired roles')
    preferred_locations = models.JSONField(default=list, help_text='Preferred work locations')
    job_type_preference = models.CharField(max_length=50, blank=True, help_text='Full-time, Part-time, Internship, etc.')
    
    # Metadata
    profile_completeness = models.IntegerField(default=0, help_text='Profile completeness percentage (0-100)')
    last_updated_from_intake = models.DateTimeField(null=True, blank=True, help_text='Last sync from intake sheet')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Skill Profile'
        verbose_name_plural = 'User Skill Profiles'
    
    def __str__(self):
        return f"Skill Profile - {self.user.username}"
    
    def calculate_completeness(self):
        """Calculate profile completeness percentage"""
        fields = [
            bool(self.primary_skills),
            bool(self.secondary_skills),
            self.total_years_experience > 0,
            bool(self.highest_degree),
            bool(self.field_of_study),
            bool(self.desired_roles),
            bool(self.preferred_locations),
        ]
        self.profile_completeness = int((sum(fields) / len(fields)) * 100)
        self.save(update_fields=['profile_completeness'])


class RecommendationFeedback(models.Model):
    """
    User feedback on recommendations for improving the algorithm
    """
    FEEDBACK_TYPES = [
        ('helpful', 'Helpful'),
        ('not_relevant', 'Not Relevant'),
        ('too_senior', 'Too Senior'),
        ('too_junior', 'Too Junior'),
        ('wrong_skills', 'Wrong Skills'),
        ('wrong_location', 'Wrong Location'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation = models.ForeignKey(UserRoleRecommendation, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True, help_text='Optional user comment')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Recommendation Feedback'
        verbose_name_plural = 'Recommendation Feedback'
    
    def __str__(self):
        return f"Feedback: {self.feedback_type} for {self.recommendation.role.title}"
