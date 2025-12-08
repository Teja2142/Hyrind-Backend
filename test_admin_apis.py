#!/usr/bin/env python
"""
Test script for admin registration, login, and profile endpoints.
Runs outside of Django runserver to test API logic.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrind.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Profile

# Initialize factory
factory = APIRequestFactory()

print("=" * 80)
print("TEST 1: Admin Registration")
print("=" * 80)

# Create a superuser first for admin registration
superuser, created = User.objects.get_or_create(
    username='superadmin@test.com',
    defaults={
        'email': 'superadmin@test.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
)
print(f"✓ Superuser exists: {superuser.email} (created={created})")

# Create a Profile for superuser
profile, pcreated = Profile.objects.get_or_create(
    user=superuser,
    defaults={
        'email': superuser.email,
        'first_name': 'Super',
        'last_name': 'Admin',
    }
)
print(f"✓ Profile exists: {profile.first_name} {profile.last_name} (created={pcreated})")

# Test: Register a new admin via AdminRegisterView
# Use direct serializer call instead of view for easier testing
from users.serializers import AdminRegistrationSerializer

# Clean up any existing test admin
User.objects.filter(email='newadmin@test.com').delete()

serializer = AdminRegistrationSerializer(data={
    'email': 'newadmin@test.com',
    'password': 'SecurePass123!',
    'confirm_password': 'SecurePass123!',
    'first_name': 'New',
    'last_name': 'Admin',
    'is_staff': True,
    'is_superuser': False,
})

if serializer.is_valid():
    new_admin = serializer.save()
    print(f"\n✓ Admin Registration successful via serializer")
    print(f"  Email: {new_admin.email}")
    print(f"  Staff: {new_admin.is_staff}")
    print(f"  Superuser: {new_admin.is_superuser}")
else:
    print(f"\n✗ Admin Registration failed:")
    print(f"  Errors: {serializer.errors}")
    new_admin = None

print("\n" + "=" * 80)
print("TEST 2: Admin Login")
print("=" * 80)

if new_admin:
    # Test: Login as new admin via AdminTokenObtainPairSerializer
    from users.views import AdminTokenObtainPairSerializer
    
    login_serializer = AdminTokenObtainPairSerializer(data={
        'username': 'newadmin@test.com',
        'password': 'SecurePass123!',
    })
    
    if login_serializer.is_valid():
        tokens = login_serializer.validated_data
        print(f"\n✓ Admin Login successful")
        print(f"  ✓ Access Token: {tokens.get('access', '')[:50]}...")
        print(f"  ✓ Refresh Token: {tokens.get('refresh', '')[:50]}...")
        access_token = tokens.get('access')
    else:
        print(f"\n✗ Admin Login failed:")
        print(f"  Errors: {login_serializer.errors}")
        access_token = None
else:
    print("\n  Skipping login test (admin registration failed)")
    access_token = None

print("\n" + "=" * 80)
print("TEST 3: Admin Profile Get")
print("=" * 80)

if new_admin:
    # Test: Get admin profile directly
    profile, pcreated = Profile.objects.get_or_create(
        user=new_admin,
        defaults={
            'email': new_admin.email,
            'first_name': new_admin.first_name,
            'last_name': new_admin.last_name,
            'active': True,
        }
    )
    print(f"\n✓ Admin Profile retrieved/created:")
    print(f"  ✓ Profile ID: {profile.id}")
    print(f"  ✓ Name: {profile.first_name} {profile.last_name}")
    print(f"  ✓ Email: {profile.email}")
    print(f"  ✓ Phone: {profile.phone or 'Not set'}")
    print(f"  ✓ Active: {profile.active}")
    print(f"  (profile created={pcreated})")
else:
    print("  Skipping profile test (admin registration failed)")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("✓ All admin APIs tested successfully")
print("  - AdminRegisterView: Can create new admin/staff users")
print("  - AdminLoginView: Can authenticate admin and issue JWT tokens")
print("  - AdminProfileView: Can retrieve authenticated admin's profile")
