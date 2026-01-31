#!/usr/bin/env python
"""
Hyrind Backend Setup Verification Script
Run this script to verify your setup is working correctly.
"""

import os
import sys
import django
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.10+")
        return False

def check_virtual_env():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual Environment - Active")
        return True
    else:
        print("⚠️  Virtual Environment - Not detected (recommended for development)")
        return True  # Not critical

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        ('django', 'django'),
        ('djangorestframework', 'rest_framework'),
        ('djangorestframework_simplejwt', 'rest_framework_simplejwt'),
        ('drf_yasg', 'drf_yasg'),
        ('mysqlclient', 'MySQLdb'),
        ('python-dotenv', 'dotenv'),
        ('razorpay', 'razorpay'),
        ('stripe', 'stripe'),
        ('django-cors-headers', 'corsheaders'),
    ]

    missing = []
    for pip_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {pip_name} - Installed")
        except ImportError:
            missing.append(pip_name)
            print(f"❌ {pip_name} - Missing")

    return len(missing) == 0

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file - Missing (copy from .env.example)")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Environment variables - Missing: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Environment variables - OK")
        return True

def check_database_connection():
    """Check database connection"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrind.settings')
        django.setup()

        from django.db import connection
        cursor = connection.cursor()
        print("✅ Database connection - OK")
        return True
    except Exception as e:
        print(f"❌ Database connection - Failed: {str(e)}")
        return False

def check_migrations():
    """Check if migrations are applied"""
    try:
        from django.core.management import execute_from_command_line
        from io import StringIO
        import sys

        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            execute_from_command_line(['manage.py', 'showmigrations', '--list'])
            output = sys.stdout.getvalue()
            if '[X]' in output:
                print("✅ Database migrations - Applied")
                return True
            else:
                print("⚠️  Database migrations - Not all applied")
                return False
        finally:
            sys.stdout = old_stdout
    except Exception as e:
        print(f"❌ Database migrations - Check failed: {str(e)}")
        return False

def main():
    """Run all checks"""
    print("🔍 Hyrind Backend Setup Verification")
    print("=" * 40)

    checks = [
        check_python_version,
        check_virtual_env,
        check_dependencies,
        check_env_file,
        check_database_connection,
        check_migrations,
    ]

    passed = 0
    total = len(checks)

    for check in checks:
        if check():
            passed += 1
        print()

    print("=" * 40)
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 Setup verification complete! Your environment is ready.")
        print("\n🚀 You can now run: python manage.py runserver")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("📖 Check setup.md for detailed setup instructions.")

    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)