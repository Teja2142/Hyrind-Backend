"""
Role recommendation engine
Uses multiple factors to match users with suitable job roles
"""
from django.db.models import Q
from decimal import Decimal
from .models import JobRole, UserRoleRecommendation, UserSkillProfile
from users.models import ClientIntakeSheet, Profile
import re


class RoleRecommendationEngine:
    """
    Intelligent role recommendation engine
    Matches users with suitable job roles based on:
    - Skills (primary factor)
    - Experience level
    - Education background
    - User preferences
    - Industry trends
    """
    
    # Weights for different factors (total = 100)
    SKILL_WEIGHT = 50
    EXPERIENCE_WEIGHT = 25
    EDUCATION_WEIGHT = 15
    PREFERENCE_WEIGHT = 10
    
    @staticmethod
    def normalize_skill(skill):
        """Normalize skill string for matching"""
        return skill.lower().strip()
    
    @staticmethod
    def extract_skills_from_text(text):
        """Extract individual skills from comma/semicolon separated text"""
        if not text:
            return []
        
        # Split by common separators
        skills = re.split(r'[,;/\n]+', text)
        
        # Clean and normalize
        return [
            RoleRecommendationEngine.normalize_skill(s) 
            for s in skills 
            if s.strip()
        ]
    
    @staticmethod
    def sync_skill_profile_from_intake(user):
        """
        Sync or create UserSkillProfile from ClientIntakeSheet
        
        Args:
            user: User object
        
        Returns:
            UserSkillProfile object
        """
        try:
            intake = ClientIntakeSheet.objects.get(profile__user=user)
        except ClientIntakeSheet.DoesNotExist:
            # Create minimal profile if no intake sheet
            skill_profile, created = UserSkillProfile.objects.get_or_create(user=user)
            return skill_profile
        
        # Get or create skill profile
        skill_profile, created = UserSkillProfile.objects.get_or_create(user=user)
        
        # Extract skills from intake sheet
        primary_skills = RoleRecommendationEngine.extract_skills_from_text(intake.skilled_in)
        primary_skills += RoleRecommendationEngine.extract_skills_from_text(intake.experienced_with)
        
        learning_skills = RoleRecommendationEngine.extract_skills_from_text(intake.currently_learning)
        learning_skills += RoleRecommendationEngine.extract_skills_from_text(intake.learning_tools)
        
        secondary_skills = RoleRecommendationEngine.extract_skills_from_text(intake.non_technical_skills)
        
        # Calculate experience
        total_experience = 0
        if intake.job_1_start_date and intake.job_1_end_date:
            total_experience += (intake.job_1_end_date - intake.job_1_start_date).days / 365
        if intake.job_2_start_date and intake.job_2_end_date:
            total_experience += (intake.job_2_end_date - intake.job_2_start_date).days / 365
        if intake.job_3_start_date and intake.job_3_end_date:
            total_experience += (intake.job_3_end_date - intake.job_3_start_date).days / 365
        
        # Use US years if no jobs listed
        if total_experience == 0 and intake.total_years_in_us:
            total_experience = intake.total_years_in_us
        
        # Extract desired roles
        desired_roles = RoleRecommendationEngine.extract_skills_from_text(intake.desired_job_role)
        
        # Update skill profile
        skill_profile.primary_skills = list(set(primary_skills))  # Remove duplicates
        skill_profile.secondary_skills = list(set(secondary_skills))
        skill_profile.learning_skills = list(set(learning_skills))
        skill_profile.total_years_experience = Decimal(str(round(total_experience, 1)))
        skill_profile.highest_degree = intake.highest_degree or intake.bachelors_degree or ''
        skill_profile.field_of_study = intake.highest_field_of_study or intake.bachelors_field_of_study or ''
        skill_profile.desired_roles = desired_roles
        
        from django.utils import timezone
        skill_profile.last_updated_from_intake = timezone.now()
        skill_profile.calculate_completeness()
        skill_profile.save()
        
        return skill_profile
    
    @classmethod
    def calculate_skill_match(cls, user_skills, role):
        """
        Calculate skill match score (0-100)
        
        Args:
            user_skills: List of user's skills (normalized)
            role: JobRole object
        
        Returns:
            tuple: (score, matched_skills, missing_skills)
        """
        user_skills_set = set(cls.normalize_skill(s) for s in user_skills)
        
        required_skills = [cls.normalize_skill(s) for s in role.required_skills]
        preferred_skills = [cls.normalize_skill(s) for s in role.preferred_skills]
        
        # Calculate matches
        matched_required = [s for s in required_skills if s in user_skills_set]
        matched_preferred = [s for s in preferred_skills if s in user_skills_set]
        missing_required = [s for s in required_skills if s not in user_skills_set]
        
        # Score calculation
        if required_skills:
            required_score = (len(matched_required) / len(required_skills)) * 100
        else:
            required_score = 100  # No requirements = perfect match
        
        if preferred_skills:
            preferred_score = (len(matched_preferred) / len(preferred_skills)) * 100
        else:
            preferred_score = 100
        
        # Weight: 80% required, 20% preferred
        final_score = (required_score * 0.8) + (preferred_score * 0.2)
        
        return (
            round(final_score, 2),
            matched_required + matched_preferred,
            missing_required
        )
    
    @classmethod
    def calculate_experience_match(cls, user_experience, role):
        """
        Calculate experience match score (0-100)
        
        Args:
            user_experience: User's years of experience (Decimal)
            role: JobRole object
        
        Returns:
            float: Match score
        """
        user_years = float(user_experience)
        min_years = role.min_years_experience
        max_years = role.max_years_experience if role.max_years_experience else 100
        
        # Perfect match if within range
        if min_years <= user_years <= max_years:
            return 100.0
        
        # Penalize if below minimum
        if user_years < min_years:
            gap = min_years - user_years
            penalty = min(gap * 20, 80)  # Max 80 point penalty
            return max(100 - penalty, 0)
        
        # Mild penalty if above maximum (overqualified)
        if user_years > max_years:
            gap = user_years - max_years
            penalty = min(gap * 10, 50)  # Max 50 point penalty
            return max(100 - penalty, 0)
        
        return 0
    
    @classmethod
    def calculate_education_match(cls, user_degree, role):
        """
        Calculate education match score (0-100)
        
        Args:
            user_degree: User's highest degree
            role: JobRole object
        
        Returns:
            float: Match score
        """
        if not role.required_degrees:
            return 100.0  # No requirements
        
        if not user_degree:
            return 0.0  # User has no degree but role requires one
        
        # Normalize degree names
        degree_hierarchy = {
            'phd': 4,
            "master's": 3,
            'masters': 3,
            "bachelor's": 2,
            'bachelors': 2,
            'diploma': 1,
        }
        
        user_level = degree_hierarchy.get(user_degree.lower(), 0)
        
        # Check if user meets any required degree
        required_levels = [
            degree_hierarchy.get(d.lower(), 0) 
            for d in role.required_degrees
        ]
        
        if not required_levels:
            return 100.0
        
        min_required = min(required_levels)
        
        # Perfect match if meets or exceeds requirement
        if user_level >= min_required:
            return 100.0
        
        # Partial match if close
        if user_level == min_required - 1:
            return 50.0
        
        return 0.0
    
    @classmethod
    def calculate_preference_match(cls, user_profile, role):
        """
        Calculate preference match score (0-100)
        
        Args:
            user_profile: UserSkillProfile object
            role: JobRole object
        
        Returns:
            float: Match score
        """
        score = 0
        
        # Check if role matches desired roles
        if user_profile.desired_roles:
            normalized_desired = [cls.normalize_skill(r) for r in user_profile.desired_roles]
            normalized_role = cls.normalize_skill(role.title)
            normalized_alt_titles = [cls.normalize_skill(t) for t in role.alternative_titles]
            
            # Check for exact or partial matches
            for desired in normalized_desired:
                if desired in normalized_role or normalized_role in desired:
                    score += 50
                    break
                
                for alt_title in normalized_alt_titles:
                    if desired in alt_title or alt_title in desired:
                        score += 50
                        break
        
        # Bonus for popular roles
        if role.popularity_score > 0:
            popularity_bonus = min(role.popularity_score / 10, 50)
            score += popularity_bonus
        
        return min(score, 100.0)
    
    @classmethod
    def generate_recommendations(cls, user, limit=10, force_refresh=False):
        """
        Generate role recommendations for a user
        
        Args:
            user: User object
            limit: Maximum number of recommendations
            force_refresh: If True, delete existing recommendations and regenerate
        
        Returns:
            QuerySet of UserRoleRecommendation objects
        """
        # Sync skill profile from intake sheet
        skill_profile = cls.sync_skill_profile_from_intake(user)
        
        # Delete existing recommendations if force refresh
        if force_refresh:
            UserRoleRecommendation.objects.filter(user=user).delete()
        
        # Check if recommendations already exist
        existing_count = UserRoleRecommendation.objects.filter(user=user).count()
        if existing_count >= limit and not force_refresh:
            return UserRoleRecommendation.objects.filter(user=user)[:limit]
        
        # Get all active job roles
        active_roles = JobRole.objects.filter(is_active=True)
        
        # Combine all user skills
        all_user_skills = (
            skill_profile.primary_skills + 
            skill_profile.secondary_skills + 
            skill_profile.learning_skills
        )
        
        recommendations = []
        
        for role in active_roles:
            # Calculate individual scores
            skill_score, matched_skills, missing_skills = cls.calculate_skill_match(all_user_skills, role)
            experience_score = cls.calculate_experience_match(skill_profile.total_years_experience, role)
            education_score = cls.calculate_education_match(skill_profile.highest_degree, role)
            preference_score = cls.calculate_preference_match(skill_profile, role)
            
            # Calculate weighted total score
            total_score = (
                (skill_score * cls.SKILL_WEIGHT / 100) +
                (experience_score * cls.EXPERIENCE_WEIGHT / 100) +
                (education_score * cls.EDUCATION_WEIGHT / 100) +
                (preference_score * cls.PREFERENCE_WEIGHT / 100)
            )
            
            # Generate recommendation reason
            reason_parts = []
            if skill_score >= 70:
                reason_parts.append(f"Strong skill match ({len(matched_skills)} matching skills)")
            elif skill_score >= 50:
                reason_parts.append(f"Good skill match ({len(matched_skills)} matching skills)")
            
            if experience_score >= 90:
                reason_parts.append("Experience level is a perfect fit")
            elif experience_score >= 70:
                reason_parts.append("Experience level aligns well")
            
            if education_score >= 90:
                reason_parts.append("Education requirements met")
            
            if preference_score >= 50:
                reason_parts.append("Matches your career preferences")
            
            if missing_skills:
                reason_parts.append(f"Consider learning: {', '.join(missing_skills[:3])}")
            
            recommendation_reason = ". ".join(reason_parts) + "." if reason_parts else "This role may be a good fit for you."
            
            # Create or update recommendation
            recommendation, created = UserRoleRecommendation.objects.update_or_create(
                user=user,
                role=role,
                defaults={
                    'match_score': Decimal(str(round(total_score, 2))),
                    'skill_match_score': Decimal(str(round(skill_score, 2))),
                    'experience_match_score': Decimal(str(round(experience_score, 2))),
                    'education_match_score': Decimal(str(round(education_score, 2))),
                    'matched_skills': matched_skills,
                    'missing_skills': missing_skills,
                    'recommendation_reason': recommendation_reason,
                }
            )
            
            recommendations.append(recommendation)
        
        # Return top recommendations sorted by score
        return UserRoleRecommendation.objects.filter(user=user).order_by('-match_score')[:limit]
    
    @classmethod
    def get_recommendations_by_category(cls, user, limit_per_category=5):
        """
        Get role recommendations grouped by category
        
        Args:
            user: User object
            limit_per_category: Max recommendations per category
        
        Returns:
            dict: Category -> list of recommendations
        """
        recommendations = cls.generate_recommendations(user, limit=50)
        
        # Group by category
        by_category = {}
        for rec in recommendations:
            category = rec.role.category
            if category not in by_category:
                by_category[category] = []
            if len(by_category[category]) < limit_per_category:
                by_category[category].append(rec)
        
        return by_category
