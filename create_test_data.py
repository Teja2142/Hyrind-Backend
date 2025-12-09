#!/usr/bin/env python
"""
Quick setup script to create test data after fresh migrations
Run: python create_test_data.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrind.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Profile
from recruiters.models import Recruiter
from datetime import date

def create_test_data():
    print("\n=== CREATING TEST DATA ===\n")
    
    # 1. Create Admin User
    print("1. Creating admin user...")
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@hyrind.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("   ✓ Admin created: admin / admin123")
    else:
        print("   ✓ Admin already exists")
    
    # 2. Create Test Candidate
    print("\n2. Creating test candidate...")
    if not User.objects.filter(email='candidate@test.com').exists():
        user = User.objects.create_user(
            username='candidate@test.com',
            email='candidate@test.com',
            password='test123',
            first_name='John',
            last_name='Doe'
        )
        
        profile = Profile.objects.create(
            user=user,
            first_name='John',
            last_name='Doe',
            email='candidate@test.com',
            phone='1234567890',
            active=True,  # Activated
            university='Test University',
            degree="Bachelor's",
            major='Computer Science',
            visa_status='F1-OPT',
            consent_to_terms=True
        )
        print("   ✓ Candidate created: candidate@test.com / test123")
        print("   ✓ Profile active: True")
    else:
        print("   ✓ Candidate already exists")
    
    # 3. Create Test Recruiter
    print("\n3. Creating test recruiter...")
    if not User.objects.filter(email='recruiter@test.com').exists():
        user = User.objects.create_user(
            username='recruiter@test.com',
            email='recruiter@test.com',
            password='test123',
            first_name='Jane',
            last_name='Smith'
        )
        
        profile = Profile.objects.create(
            user=user,
            first_name='Jane',
            last_name='Smith',
            email='recruiter@test.com',
            phone='9876543210',
            active=True,
            consent_to_terms=True
        )
        
        recruiter = Recruiter.objects.create(
            user=profile,
            employee_id='H12345',
            name='Jane Smith',
            email='recruiter@test.com',
            phone='9876543210',
            department='it_staffing',
            specialization='software_dev',
            date_of_joining=date.today(),
            status='active',
            active=True,  # Activated
            max_clients=3
        )
        print("   ✓ Recruiter created: recruiter@test.com / test123")
        print(f"   ✓ Employee ID: {recruiter.employee_id}")
        print("   ✓ Status: active")
    else:
        print("   ✓ Recruiter already exists")
    
    print("\n=== TEST DATA CREATED SUCCESSFULLY ===\n")
    print("Login Credentials:")
    print("-" * 50)
    print("Admin:      admin@hyrind.com / admin123")
    print("Candidate:  candidate@test.com / test123")
    print("Recruiter:  recruiter@test.com / test123")
    print("-" * 50)
    print("\nAdmin Panel:   http://127.0.0.1:8000/admin/")
    print("Recruiter Dashboard: http://127.0.0.1:8000/recruiter-registration/dashboard/")
    print("\n")

if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
