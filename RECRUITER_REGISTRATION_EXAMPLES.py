"""
Example Usage & Testing - Recruiter Registration System

This file shows practical examples of how to use the recruiter registration system.
"""

# ============================================================================
# EXAMPLE 1: Using the Django Form in a View
# ============================================================================

from django.shortcuts import render, redirect
from django.contrib import messages
from recruiters.forms import RecruiterRegistrationFormModel

def recruiter_registration_form_view(request):
    """
    Django view for recruiter registration form submission.
    Handles both GET (show form) and POST (process form).
    """
    if request.method == 'POST':
        form = RecruiterRegistrationFormModel(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the registration
            registration = form.save()
            
            # Show success message
            messages.success(
                request,
                'Registration submitted successfully! '
                'We will verify and contact you within 2-3 business days.'
            )
            
            # Send email to admin (optional)
            try:
                from django.core.mail import send_mail
                send_mail(
                    f'New Recruiter Registration - {registration.full_name}',
                    f'Email: {registration.email}\nPhone: {registration.phone_number}',
                    'noreply@hyrind.com',
                    ['admin@hyrind.com'],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            # Redirect to home
            return redirect('home')
        else:
            # Form has errors - will be displayed in template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterRegistrationFormModel()
    
    return render(request, 'recruiter_registration_form.html', {'form': form})


# ============================================================================
# EXAMPLE 2: API-based Form Submission (using Serializer)
# ============================================================================

from rest_framework.test import APIClient
from rest_framework import status

def test_api_form_submission():
    """
    Example of submitting registration form via REST API.
    """
    client = APIClient()
    
    # Prepare form data
    form_data = {
        # Basic Details
        'full_name': 'John Doe',
        'email': 'john.doe@example.com',
        
        # Contact Details
        'phone_number': '9876543210',
        'whatsapp_number': '9876543211',
        'date_of_joining': '2025-01-15',
        'date_of_birth': '1990-05-20',
        'gender': 'male',
        
        # Personal & Family
        'marital_status': 'married',
        'father_name': 'James Doe',
        'mother_name': 'Mary Doe',
        'spouse_name': 'Jane Doe',
        'blood_group': 'O+',
        'emergency_contact_number': '9876543212',
        
        # Address
        'permanent_address': '123 Main Street, New York, NY 10001',
        'correspondence_address': '123 Main Street, New York, NY 10001',
        'same_as_permanent_address': True,
        
        # ID Proofs
        'aadhaar_number': '123456789012',
        'pan_number': 'ABCDE1234F',
        
        # Education
        'highest_education': 'Bachelor of Science',
        'year_of_graduation': 2012,
        'course': 'Computer Science',
        
        # Bank Details
        'bank_name': 'State Bank of India',
        'account_holder_name': 'John Doe',
        'bank_account_number': '12345678901234567890',
        'confirm_bank_account_number': '12345678901234567890',
        'ifsc_code': 'SBIN0001234',
        'branch_name': 'Downtown Branch',
    }
    
    # Submit form
    response = client.post(
        '/api/recruiters/registration-form/',
        form_data,
        format='json'
    )
    
    # Verify response
    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data
    assert response.data['email'] == 'john.doe@example.com'
    
    print(f"✓ Registration created with ID: {response.data['id']}")
    return response.data


# ============================================================================
# EXAMPLE 3: Admin Verification Workflow
# ============================================================================

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

def test_admin_verification_workflow():
    """
    Example of admin verifying a recruiter registration.
    """
    # Create admin user
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    
    # Get auth token
    token, _ = Token.objects.get_or_create(user=admin_user)
    
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    # Get registration to verify (assuming ID from previous example)
    registration_id = '550e8400-e29b-41d4-a716-446655440000'
    
    # 1. List unverified registrations
    response = client.get('/api/recruiters/registration-forms/?verified=false')
    assert response.status_code == status.HTTP_200_OK
    print(f"✓ Found {len(response.data)} unverified registrations")
    
    # 2. Get registration details
    response = client.get(f'/api/recruiters/registration-forms/{registration_id}/')
    assert response.status_code == status.HTTP_200_OK
    registration = response.data
    print(f"✓ Retrieved registration for {registration['full_name']}")
    
    # 3. Verify registration
    response = client.patch(
        f'/api/recruiters/registration-forms/{registration_id}/verify/',
        {},
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data['registration']['is_verified'] == True
    print(f"✓ Registration verified!")
    
    return True


# ============================================================================
# EXAMPLE 4: File Upload Handling
# ============================================================================

from django.core.files.uploadedfile import SimpleUploadedFile

def test_file_upload():
    """
    Example of submitting registration with file uploads.
    """
    client = APIClient()
    
    # Create test files
    aadhaar_file = SimpleUploadedFile(
        "aadhaar.pdf",
        b"file_content",
        content_type="application/pdf"
    )
    
    pan_file = SimpleUploadedFile(
        "pan.jpg",
        b"file_content",
        content_type="image/jpeg"
    )
    
    # Prepare form data with files
    form_data = {
        'full_name': 'John Doe',
        'email': 'john.doe.files@example.com',
        'phone_number': '9876543210',
        'whatsapp_number': '9876543211',
        'date_of_joining': '2025-01-15',
        'date_of_birth': '1990-05-20',
        'gender': 'male',
        'marital_status': 'single',
        'father_name': 'James Doe',
        'mother_name': 'Mary Doe',
        'blood_group': 'O+',
        'emergency_contact_number': '9876543212',
        'permanent_address': '123 Main Street',
        'same_as_permanent_address': True,
        'aadhaar_number': '123456789012',
        'aadhaar_card_file': aadhaar_file,
        'pan_number': 'ABCDE1234F',
        'pan_card_file': pan_file,
        'highest_education': 'Bachelor of Science',
        'year_of_graduation': 2012,
        'course': 'Computer Science',
        'bank_name': 'SBI',
        'account_holder_name': 'John Doe',
        'bank_account_number': '12345678901234567890',
        'confirm_bank_account_number': '12345678901234567890',
        'ifsc_code': 'SBIN0001234',
        'branch_name': 'Downtown',
    }
    
    # Submit with files
    response = client.post(
        '/api/recruiters/registration-form/',
        form_data,
        format='multipart'
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    print(f"✓ Files uploaded successfully!")
    print(f"  Registration ID: {response.data['id']}")
    
    return response.data


# ============================================================================
# EXAMPLE 5: Validation Testing
# ============================================================================

def test_validation():
    """
    Test various validation scenarios.
    """
    client = APIClient()
    
    # Test 1: Invalid phone number
    print("\nTest 1: Invalid phone number")
    response = client.post(
        '/api/recruiters/registration-form/',
        {'phone_number': '123'},  # Only 3 digits
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    print(f"✓ Phone validation works: {response.data['phone_number']}")
    
    # Test 2: Invalid PAN format
    print("\nTest 2: Invalid PAN format")
    response = client.post(
        '/api/recruiters/registration-form/',
        {'pan_number': 'INVALID123'},  # Invalid format
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    print(f"✓ PAN validation works: {response.data['pan_number']}")
    
    # Test 3: Invalid Aadhaar
    print("\nTest 3: Invalid Aadhaar")
    response = client.post(
        '/api/recruiters/registration-form/',
        {'aadhaar_number': '12345'},  # Only 5 digits
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    print(f"✓ Aadhaar validation works: {response.data['aadhaar_number']}")
    
    # Test 4: Date validation
    print("\nTest 4: Date validation")
    response = client.post(
        '/api/recruiters/registration-form/',
        {
            'date_of_birth': '2025-01-01',  # Future date
            'date_of_joining': '2025-01-15'
        },
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    print(f"✓ Date validation works")
    
    # Test 5: Bank account confirmation
    print("\nTest 5: Bank account confirmation")
    response = client.post(
        '/api/recruiters/registration-form/',
        {
            'bank_account_number': '12345678901234567890',
            'confirm_bank_account_number': '99999999999999999999'  # Mismatch
        },
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    print(f"✓ Bank account validation works")


# ============================================================================
# EXAMPLE 6: Using in Django Shell
# ============================================================================

"""
# Enter Django shell
python manage.py shell

# Import the form and model
from recruiters.forms import RecruiterRegistrationFormModel
from recruiters.models import RecruiterRegistration

# Create an instance
form = RecruiterRegistrationFormModel()

# Get all registrations
all_registrations = RecruiterRegistration.objects.all()
print(f"Total registrations: {all_registrations.count()}")

# Get unverified registrations
unverified = RecruiterRegistration.objects.filter(is_verified=False)
print(f"Unverified registrations: {unverified.count()}")

# Get by email
registration = RecruiterRegistration.objects.get(email='john@example.com')
print(f"Found: {registration.full_name}")

# Mark as verified
registration.is_verified = True
registration.save()
print("Marked as verified!")

# Check file URL
if registration.aadhaar_card_file:
    print(f"Aadhaar file URL: {registration.aadhaar_card_file.url}")
"""


# ============================================================================
# EXAMPLE 7: Email Notification (Optional)
# ============================================================================

from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_verification_complete_email(registration):
    """
    Send email to recruiter when registration is verified.
    """
    context = {
        'recruiter_name': registration.full_name,
        'email': registration.email,
        'registration_id': registration.id,
    }
    
    html_message = render_to_string(
        'emails/registration_verified.html',
        context
    )
    
    send_mail(
        'Your Recruiter Registration Verified',
        'Your registration has been verified!',
        'noreply@hyrind.com',
        [registration.email],
        html_message=html_message,
        fail_silently=True
    )


# ============================================================================
# EXAMPLE 8: Data Export (Admin)
# ============================================================================

import csv
from django.http import HttpResponse
from recruiters.models import RecruiterRegistration

def export_registrations_csv(request):
    """
    Export all registrations to CSV (admin only).
    """
    if not request.user.is_staff:
        return HttpResponse('Unauthorized', status=403)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registrations.csv"'
    
    writer = csv.writer(response)
    
    # Header row
    writer.writerow([
        'ID', 'Full Name', 'Email', 'Phone', 'WhatsApp',
        'DOB', 'Aadhaar', 'PAN', 'Bank Account', 'Verified', 'Created'
    ])
    
    # Data rows
    for reg in RecruiterRegistration.objects.all():
        writer.writerow([
            reg.id,
            reg.full_name,
            reg.email,
            reg.phone_number,
            reg.whatsapp_number,
            reg.date_of_birth,
            reg.aadhaar_number,
            reg.pan_number,
            reg.bank_account_number,
            reg.is_verified,
            reg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


# ============================================================================
# URLS Configuration
# ============================================================================

"""
# Add to your urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Registration form view (Django template)
    path('recruiter-registration/', 
         views.recruiter_registration_form_view, 
         name='recruiter-registration'),
    
    # Admin export view
    path('admin/export-registrations/', 
         views.export_registrations_csv, 
         name='export-registrations'),
]
"""


# ============================================================================
# Template Context for Home Page
# ============================================================================

"""
# In your home view:

def home(request):
    context = {
        'show_recruiter_registration': True,
        'registration_form_url': reverse('recruiter-registration'),
        'api_registration_url': '/api/recruiters/registration-form/',
    }
    return render(request, 'home.html', context)

# In your home.html template:

{% if show_recruiter_registration %}
  <a href="{{ registration_form_url }}" class="btn btn-primary">
    Start Recruiter Registration
  </a>
{% endif %}
"""

