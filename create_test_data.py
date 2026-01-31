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
from recruiters.models import Recruiter

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
        print("⚠️  Admin user already exists")

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
        print("⚠️  Candidate user already exists")

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
        print("⚠️  Recruiter user already exists")

    return user

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

        print("=" * 50)
        print("✅ Test data creation completed successfully!")
        print()
        print("📋 Test Accounts Created:")
        print("1. Admin:     admin@hyrind.com     / admin123")
        print("2. Candidate: candidate@test.com   / test123")
        print("3. Recruiter: recruiter@test.com   / test123")
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