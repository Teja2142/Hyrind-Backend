#!/usr/bin/env python
"""
Hyrind Backend Test Data Creation Script
Creates test users for development and testing purposes.

This script creates three test accounts:
1. Admin user (superuser with full access)
2. Candidate user (job seeker)
3. Recruiter user (internal staff member)

Usage: python create_test_data.py
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrind.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from users.models import Profile
from recruiters.models import Recruiter, Assignment
from subscriptions.models import SubscriptionPlan, UserSubscription
from decimal import Decimal

def create_admin_user():
    """Create admin superuser account"""
    print("Creating admin user...")

    # Create Django user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@hyrind.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
        }
    )

    if created:
        user.set_password('admin123')
        user.save()
        print("✅ Admin user created: admin@hyrind.com / admin123")
    else:
        # Always refresh password to ensure it is correct on every run
        user.set_password('admin123')
        user.is_active = True
        user.save(update_fields=['password', 'is_active'])
        print("⚠️  Admin user already exists (password refreshed)")

    return user

def create_candidate_user():
    """Create candidate test account"""
    print("Creating candidate user...")

    # Create Django user
    user, created = User.objects.get_or_create(
        username='candidate',
        defaults={
            'email': 'candidate@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }
    )

    if created:
        user.set_password('test123')
        user.save()

        # Create profile
        profile = Profile.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            email='candidate@test.com',
            phone='1234567890',
            active=True,
            registration_status='approved',
            university='Test University',
            degree="Bachelor's in Computer Science",
            major='Computer Science',
            visa_status='F1-OPT',
            graduation_date=date(2024, 5, 15),
            opt_end_date=date(2026, 5, 15),
            consent_to_terms=True,
            referral_source='Google',
            linkedin_url='https://linkedin.com/in/johndoe',
            github_url='https://github.com/johndoe',
            additional_notes='Passionate software developer with 2 years experience. Skilled in Python, Django, React, and cloud technologies.'
        )

        # Create a sample resume file
        sample_resume_content = """
John Doe
Software Engineer

Contact Information:
Email: candidate@test.com
Phone: 123-456-7890
LinkedIn: https://linkedin.com/in/johndoe
GitHub: https://github.com/johndoe

Education:
Bachelor of Science in Computer Science
Test University, 2024
GPA: 3.8/4.0

Experience:
Software Engineer Intern
Tech Startup, 2023-Present
- Developed web applications using Django and React
- Implemented REST APIs and database models
- Collaborated with cross-functional teams

Skills:
- Programming: Python, JavaScript, SQL
- Frameworks: Django, React, Node.js
- Tools: Git, Docker, AWS
- Soft Skills: Teamwork, Problem Solving, Communication
"""
        profile.resume_file.save('sample_resume.txt', ContentFile(sample_resume_content))

        print("✅ Candidate user created: candidate@test.com / test123")
    else:
        user.set_password('test123')
        user.is_active = True
        user.save(update_fields=['password', 'is_active'])
        print("⚠️  Candidate user already exists (password refreshed)")

    return user

def create_recruiter_user():
    """Create recruiter test account"""
    print("Creating recruiter user...")

    # Create Django user
    user, created = User.objects.get_or_create(
        username='recruiter',
        defaults={
            'email': 'recruiter@test.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
        }
    )

    if created:
        user.set_password('test123')
        user.save()

        # Create profile
        profile = Profile.objects.create(
            user=user,
            first_name='Jane',
            last_name='Smith',
            email='recruiter@test.com',
            phone='9876543210',
            active=True,
            registration_status='approved',
        )

        # Create recruiter profile
        recruiter = Recruiter.objects.create(
            user=profile,
            employee_id='H12345',
            name='Jane Smith',
            email='recruiter@test.com',
            phone='9876543210',
            department='it_staffing',
            specialization='software_dev',
            date_of_joining=date.today(),
            max_clients=3,
            current_clients_count=0,
            status='active',
            active=True,
            verified=True,
            company_name='Hyrind Recruitment Services',
            notes='Excellent performer, specializes in software development roles. 5 years experience in IT recruitment.'
        )

        print("✅ Recruiter user created: recruiter@test.com / test123")
    else:
        user.set_password('test123')
        user.is_active = True
        user.save(update_fields=['password', 'is_active'])
        print("⚠️  Recruiter user already exists (password refreshed)")

    return user

def create_team_lead_user():
    """Create team lead recruiter test account"""
    print("Creating team lead recruiter user...")

    user, created = User.objects.get_or_create(
        username='teamlead',
        defaults={
            'email': 'teamlead@test.com',
            'first_name': 'Taylor',
            'last_name': 'Lead',
        }
    )

    if created:
        user.set_password('test123')
        user.save()

        profile = Profile.objects.create(
            user=user,
            first_name='Taylor',
            last_name='Lead',
            email='teamlead@test.com',
            phone='5551234567',
            active=True,
            registration_status='approved',
        )

        Recruiter.objects.create(
            user=profile,
            employee_id='TL1001',
            name='Taylor Lead',
            email='teamlead@test.com',
            phone='5551234567',
            department='it_staffing',
            specialization='project_management',
            date_of_joining=date.today(),
            max_clients=5,
            current_clients_count=0,
            status='active',
            active=True,
            verified=True,
            company_name='Hyrind Recruitment Services',
            notes='Team lead recruiter for testing multi-assignment workflow.'
        )

        print("✅ Team lead user created: teamlead@test.com / test123")
    else:
        user.set_password('test123')
        user.is_active = True
        user.save(update_fields=['password', 'is_active'])
        print("⚠️  Team lead user already exists (password refreshed)")

    return user

def create_subscription_plans():
    """Create base and add-on subscription plans (including private add-on)"""
    print("Creating subscription plans...")

    base_plan, _ = SubscriptionPlan.objects.get_or_create(
        name='Profile Marketing Services Fee',
        plan_type='base',
        defaults={
            'description': 'Mandatory base subscription for all users.',
            'base_price': Decimal('400.00'),
            'is_mandatory': True,
            'is_active': True,
            'billing_cycle': 'monthly',
            'features': ['Profile visibility', 'Marketing support']
        }
    )

    addon_plan, _ = SubscriptionPlan.objects.get_or_create(
        name='Skill Development Training',
        plan_type='addon',
        defaults={
            'description': 'Optional training add-on',
            'base_price': Decimal('150.00'),
            'is_mandatory': False,
            'is_active': True,
            'billing_cycle': 'monthly',
            'features': ['Training sessions', 'Mock interviews']
        }
    )

    private_addon, _ = SubscriptionPlan.objects.get_or_create(
        name='Client-Specific Premium Addon',
        plan_type='addon',
        defaults={
            'description': 'Private add-on for specific client only',
            'base_price': Decimal('250.00'),
            'is_mandatory': False,
            'is_active': True,
            'billing_cycle': 'monthly',
            'features': ['Dedicated support', 'Priority matching'],
            'is_private': True
        }
    )

    print("✅ Subscription plans created/verified")
    return base_plan, addon_plan, private_addon

def create_user_subscriptions(profile, base_plan, addon_plan, private_addon):
    """Assign subscriptions for a profile and allow private add-on visibility"""
    print("Creating user subscriptions...")

    private_addon.allowed_profiles.add(profile)

    UserSubscription.objects.get_or_create(
        profile=profile,
        plan=base_plan,
        defaults={
            'price': base_plan.base_price,
            'status': 'active',
            'billing_cycle': base_plan.billing_cycle
        }
    )

    UserSubscription.objects.get_or_create(
        profile=profile,
        plan=addon_plan,
        defaults={
            'price': addon_plan.base_price,
            'status': 'active',
            'billing_cycle': addon_plan.billing_cycle
        }
    )

    UserSubscription.objects.get_or_create(
        profile=profile,
        plan=private_addon,
        defaults={
            'price': Decimal('199.00'),
            'status': 'active',
            'billing_cycle': private_addon.billing_cycle,
            'admin_notes': 'Client-specific discounted private add-on'
        }
    )

    print("✅ User subscriptions created/verified")

def create_assignments(profile, recruiter, team_lead):
    """Assign a client to multiple recruiters"""
    print("Creating recruiter assignments...")

    Assignment.objects.get_or_create(
        profile=profile,
        recruiter=recruiter,
        defaults={
            'status': 'active',
            'priority': 'high'
        }
    )

    Assignment.objects.get_or_create(
        profile=profile,
        recruiter=team_lead,
        defaults={
            'status': 'active',
            'priority': 'medium'
        }
    )

    print("✅ Assignments created/verified")

def main():
    """Main function to create all test data"""
    print("🚀 Hyrind Backend Test Data Creation")
    print("=" * 50)

    try:
        # Create test users
        admin_user = create_admin_user()
        print()

        candidate_user = create_candidate_user()
        print()

        recruiter_user = create_recruiter_user()
        print()

        team_lead_user = create_team_lead_user()
        print()

        base_plan, addon_plan, private_addon = create_subscription_plans()
        print()

        candidate_profile = Profile.objects.get(user=candidate_user)
        create_user_subscriptions(candidate_profile, base_plan, addon_plan, private_addon)
        print()

        recruiter_profile = Profile.objects.get(user=recruiter_user)
        team_lead_profile = Profile.objects.get(user=team_lead_user)

        recruiter = Recruiter.objects.get(user=recruiter_profile)
        team_lead = Recruiter.objects.get(user=team_lead_profile)

        create_assignments(candidate_profile, recruiter, team_lead)
        print()

        print("=" * 50)
        print("✅ Test data creation completed successfully!")
        print()
        print("📋 Test Accounts Created:")
        print("1. Admin:     admin@hyrind.com     / admin123")
        print("2. Candidate: candidate@test.com   / test123")
        print("3. Recruiter: recruiter@test.com   / test123")
        print("4. Team Lead: teamlead@test.com    / test123")
        print()
        print("🌐 Access URLs:")
        print("- Admin Panel: http://127.0.0.1:8000/admin/")
        print("- API Docs:    http://127.0.0.1:8000/swagger/")
        print("- Recruiter:   http://127.0.0.1:8000/recruiter-registration/login/")
        print()
        print("🔒 Security Note: These are development test credentials only!")

    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()