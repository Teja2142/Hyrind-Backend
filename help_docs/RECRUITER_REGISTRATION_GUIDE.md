# Recruiter Registration System - Complete Guide

## Overview
A comprehensive, industry-standard recruiter onboarding system with support for detailed personal, family, address, document, education, and bank information. All file uploads are optional and stored in MinIO S3-compatible storage.

---

## 📊 System Architecture

### Models

#### 1. **RecruiterRegistration Model** (`recruiters/models.py`)
Primary model for comprehensive recruiter onboarding with the following sections:

**Basic Details:**
- `full_name` - Full legal name (string)
- `email` - Unique email address

**Contact Details:**
- `phone_number` - Primary phone (10-12 digits)
- `whatsapp_number` - WhatsApp number (optional)
- `date_of_joining` - Employment start date
- `date_of_birth` - Date of birth
- `gender` - Choices: Male, Female, Other, Prefer not to say

**Personal & Family Details:**
- `marital_status` - Choices: Single, Married, Divorced, Widowed, Prefer not to say
- `father_name` - Father's full name
- `mother_name` - Mother's full name
- `spouse_name` - Spouse's name (if married)
- `blood_group` - Choices: A+, A-, B+, B-, O+, O-, AB+, AB-, Unknown
- `emergency_contact_number` - Emergency contact (10-12 digits)

**Address Details:**
- `permanent_address` - Full permanent address
- `correspondence_address` - Mailing address (optional)
- `same_as_permanent_address` - Boolean flag

**ID Proofs (All Optional):**
- `aadhaar_number` - Unique 12-digit Aadhaar
- `aadhaar_card_file` - Aadhaar card scan (PDF/JPG/PNG, max 5MB)
- `pan_number` - Unique PAN (AAAAA9999A format)
- `pan_card_file` - PAN card scan (optional)
- `passport_number` - Passport number (optional)
- `passport_copy_file` - Passport copy (optional)
- `address_proof_file` - Address proof document (optional)

**Education Details:**
- `highest_education` - Qualification name
- `year_of_graduation` - Graduation year (1960-current year)
- `course` - Course/Major name
- `degree_certificate_file` - Degree certificate (optional)

**Bank Details:**
- `bank_name` - Bank name
- `account_holder_name` - Account holder name as per bank
- `bank_account_number` - Bank account number
- `ifsc_code` - IFSC code (AAAA0AAAAAA format)
- `branch_name` - Bank branch name

**Metadata:**
- `id` - UUID primary key
- `created_at` - Timestamp when created
- `updated_at` - Timestamp when updated
- `is_verified` - Admin verification status (default: False)

---

## 🔧 Validation Rules

### Phone Number Validation
- Format: 10-12 digits only
- Special characters are stripped automatically
- Applied to: `phone_number`, `whatsapp_number`, `emergency_contact_number`

### Date Validation
- `date_of_birth` must be at least 18 years old
- `date_of_birth` must be before `date_of_joining`
- `year_of_graduation` must be between 1960 and current year

### ID Number Validation
- **Aadhaar:** Exactly 12 digits
- **PAN:** Format must be AAAAA9999A (5 letters, 4 digits, 1 letter)
- **Passport:** 6-20 alphanumeric characters (optional)
- **IFSC:** Format must be AAAA0AAAAAA (4 letters, 0, 6 alphanumeric)

### File Validation
- **Allowed formats:** PDF, JPG, JPEG, PNG
- **Maximum size:** 5MB per file
- **Optional:** All file uploads are optional
- **MinIO Integration:** Files stored in S3-compatible MinIO bucket

### Cross-Field Validation
- Bank account numbers must match confirmation field
- Correspondence address required if different from permanent
- Spouse name required for married status
- All required fields must be non-empty

---

## 📡 API Endpoints

### Public Endpoints (AllowAny)

#### Create Recruiter Registration Form
```
POST /api/recruiters/registration-form/
Content-Type: multipart/form-data

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone_number": "9876543210",
  "whatsapp_number": "9876543210",
  "date_of_joining": "2025-01-15",
  "date_of_birth": "1990-05-20",
  "gender": "male",
  "marital_status": "married",
  "father_name": "James Doe",
  "mother_name": "Mary Doe",
  "spouse_name": "Jane Doe",
  "blood_group": "O+",
  "emergency_contact_number": "9876543211",
  "permanent_address": "123 Main Street, City, State 12345",
  "correspondence_address": "123 Main Street, City, State 12345",
  "same_as_permanent_address": true,
  "aadhaar_number": "123456789012",
  "aadhaar_card_file": <file>,
  "pan_number": "ABCDE1234F",
  "pan_card_file": <file>,
  "passport_number": "A12345678",
  "passport_copy_file": <file>,
  "address_proof_file": <file>,
  "highest_education": "Bachelor of Science",
  "year_of_graduation": 2012,
  "course": "Computer Science",
  "degree_certificate_file": <file>,
  "bank_name": "State Bank of India",
  "account_holder_name": "John Doe",
  "bank_account_number": "12345678901234567890",
  "confirm_bank_account_number": "12345678901234567890",
  "ifsc_code": "SBIN0001234",
  "branch_name": "Downtown Branch"
}

Response: 201 Created
{
  "message": "Recruiter registration form submitted successfully",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "status": "pending_verification"
}
```

### Admin Only Endpoints (IsAdminUser)

#### List All Registrations
```
GET /api/recruiters/registration-forms/?verified=false&email=john

Response: 200 OK
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "9876543210",
    "date_of_joining": "2025-01-15",
    "aadhaar_number": "123456789012",
    "pan_number": "ABCDE1234F",
    "is_verified": false,
    "created_at": "2025-12-06T10:30:00Z"
  }
]
```

#### Get Registration Details
```
GET /api/recruiters/registration-forms/{id}/

Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "John Doe",
  "email": "john@example.com",
  ...all fields...
  "is_verified": false,
  "created_at": "2025-12-06T10:30:00Z"
}
```

#### Update Registration (with file uploads)
```
PATCH /api/recruiters/registration-forms/{id}/
Content-Type: multipart/form-data

{
  "aadhaar_card_file": <new_file>,
  "pan_card_file": <new_file>,
  ...updated fields...
}

Response: 200 OK
{...updated registration...}
```

#### Verify/Approve Registration
```
PATCH /api/recruiters/registration-forms/{id}/verify/

Response: 200 OK
{
  "message": "Recruiter registration verified successfully",
  "registration": {...full registration data...}
}
```

---

## 🎯 Django Form Integration

### RecruiterRegistrationFormModel Form
ModelForm with comprehensive validation and Bootstrap CSS integration.

```python
from recruiters.forms import RecruiterRegistrationFormModel

form = RecruiterRegistrationFormModel()

# Render in template
{% load widget_tweaks %}

<form method="post" enctype="multipart/form-data">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Features:
- ✅ Bootstrap CSS classes on all form fields
- ✅ Required field indicators (red asterisk)
- ✅ Proper help text for complex fields
- ✅ Custom validation with clear error messages
- ✅ File input with accept filters
- ✅ Date inputs with HTML5 date picker
- ✅ Select dropdowns for choice fields

---

## 💾 File Storage - MinIO Integration

### Configuration (settings.py)

```python
# MinIO Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = 'your-minio-access-key'
AWS_SECRET_ACCESS_KEY = 'your-minio-secret-key'
AWS_STORAGE_BUCKET_NAME = 'hyrind-recruiter-docs'

# MinIO S3-compatible endpoint
AWS_S3_ENDPOINT_URL = 'http://localhost:9000'  # or your MinIO server URL
AWS_S3_REGION_NAME = 'us-east-1'

# Additional S3 settings
AWS_S3_USE_SSL = False  # Change to True for production
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = 'virtual'
```

### File Upload Paths
Files are automatically organized by type in MinIO:
- `recruiters/aadhaar/` - Aadhaar cards
- `recruiters/pan/` - PAN cards
- `recruiters/passport/` - Passport copies
- `recruiters/address_proof/` - Address proof documents
- `recruiters/degree_certificates/` - Degree certificates

### File Validation
- **Size limit:** 5MB per file
- **Allowed types:** PDF, JPG, JPEG, PNG
- **Optional:** All file uploads are optional
- **Error handling:** Validation occurs before model save

---

## 🔐 Security & Validation

### Input Sanitization
- Phone numbers: Digits only (10-12)
- ID numbers: Uppercased and stripped
- Names: Alphanumeric with limited special characters
- All string fields trimmed and normalized

### Database Constraints
- `email` - Unique constraint
- `aadhaar_number` - Unique constraint
- `pan_number` - Unique constraint
- Database indexes on frequently queried fields

### CSRF Protection
- All forms protected with Django CSRF tokens
- API endpoints use proper authentication/permission classes

### File Security
- MIME type validation
- Size validation (5MB max)
- Extension whitelist (PDF, JPG, JPEG, PNG only)
- Files stored outside web root (MinIO)

---

## 🎨 Template Integration - Home Page

### Update home.html to include registration link:

```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
  <h1>Welcome to Hyrind</h1>
  
  <!-- Recruiter Registration Section -->
  <div class="row mt-4">
    <div class="col-md-6">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Recruiter Registration</h5>
          <p class="card-text">Complete your detailed onboarding form with personal, address, and bank details.</p>
          <a href="{% url 'registration-form' %}" class="btn btn-primary">
            Start Registration Form
          </a>
        </div>
      </div>
    </div>
    
    <div class="col-md-6">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Quick Registration</h5>
          <p class="card-text">Quick registration for immediate access. Complete detailed form later.</p>
          <a href="{% url 'recruiter-register' %}" class="btn btn-secondary">
            Quick Register
          </a>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### Create registration form template (templates/recruiter_registration_form.html):

```html
{% extends "base.html" %}
{% load widget_tweaks %}

{% block title %}Recruiter Registration Form{% endblock %}

{% block content %}
<div class="container mt-5">
  <div class="row">
    <div class="col-lg-8">
      <h1 class="mb-4">Recruiter Registration Form</h1>
      
      {% if messages %}
        {% for message in messages %}
          <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        {% endfor %}
      {% endif %}
      
      <form method="post" enctype="multipart/form-data" class="needs-validation">
        {% csrf_token %}
        
        <!-- Basic Details -->
        <fieldset class="mb-4">
          <legend class="fs-5 fw-bold mb-3">Basic Details</legend>
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.full_name|add_class:"form-control" }}
              {% if form.full_name.errors %}
                <div class="invalid-feedback d-block">{{ form.full_name.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.email|add_class:"form-control" }}
              {% if form.email.errors %}
                <div class="invalid-feedback d-block">{{ form.email.errors }}</div>
              {% endif %}
            </div>
          </div>
        </fieldset>
        
        <!-- Contact Details -->
        <fieldset class="mb-4">
          <legend class="fs-5 fw-bold mb-3">Contact Details</legend>
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.phone_number|add_class:"form-control" }}
              {% if form.phone_number.errors %}
                <div class="invalid-feedback d-block">{{ form.phone_number.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.whatsapp_number|add_class:"form-control" }}
              {% if form.whatsapp_number.errors %}
                <div class="invalid-feedback d-block">{{ form.whatsapp_number.errors }}</div>
              {% endif %}
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Date of Joining *</label>
              {{ form.date_of_joining|add_class:"form-control" }}
              {% if form.date_of_joining.errors %}
                <div class="invalid-feedback d-block">{{ form.date_of_joining.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Date of Birth *</label>
              {{ form.date_of_birth|add_class:"form-control" }}
              {% if form.date_of_birth.errors %}
                <div class="invalid-feedback d-block">{{ form.date_of_birth.errors }}</div>
              {% endif %}
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.gender|add_class:"form-control" }}
              {% if form.gender.errors %}
                <div class="invalid-feedback d-block">{{ form.gender.errors }}</div>
              {% endif %}
            </div>
          </div>
        </fieldset>
        
        <!-- Personal & Family Details -->
        <fieldset class="mb-4">
          <legend class="fs-5 fw-bold mb-3">Personal & Family Details</legend>
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.marital_status|add_class:"form-control" }}
              {% if form.marital_status.errors %}
                <div class="invalid-feedback d-block">{{ form.marital_status.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.blood_group|add_class:"form-control" }}
              {% if form.blood_group.errors %}
                <div class="invalid-feedback d-block">{{ form.blood_group.errors }}</div>
              {% endif %}
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.father_name|add_class:"form-control" }}
              {% if form.father_name.errors %}
                <div class="invalid-feedback d-block">{{ form.father_name.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.mother_name|add_class:"form-control" }}
              {% if form.mother_name.errors %}
                <div class="invalid-feedback d-block">{{ form.mother_name.errors }}</div>
              {% endif %}
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.spouse_name|add_class:"form-control" }}
              {% if form.spouse_name.errors %}
                <div class="invalid-feedback d-block">{{ form.spouse_name.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.emergency_contact_number|add_class:"form-control" }}
              {% if form.emergency_contact_number.errors %}
                <div class="invalid-feedback d-block">{{ form.emergency_contact_number.errors }}</div>
              {% endif %}
            </div>
          </div>
        </fieldset>
        
        <!-- Address Details -->
        <fieldset class="mb-4">
          <legend class="fs-5 fw-bold mb-3">Address Details</legend>
          <div class="mb-3">
            {{ form.permanent_address|add_class:"form-control" }}
            {% if form.permanent_address.errors %}
              <div class="invalid-feedback d-block">{{ form.permanent_address.errors }}</div>
            {% endif %}
          </div>
          
          <div class="form-check mb-3">
            {{ form.same_as_permanent_address }}
            <label class="form-check-label" for="{{ form.same_as_permanent_address.id_for_label }}">
              Same as permanent address
            </label>
          </div>
          
          <div class="mb-3" id="correspondence_address_section">
            {{ form.correspondence_address|add_class:"form-control" }}
            {% if form.correspondence_address.errors %}
              <div class="invalid-feedback d-block">{{ form.correspondence_address.errors }}</div>
            {% endif %}
          </div>
        </fieldset>
        
        <!-- ID Proofs -->
        <fieldset class="mb-4">
          <legend class="fs-5 fw-bold mb-3">ID Proofs (Optional)</legend>
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.aadhaar_number|add_class:"form-control" }}
              {% if form.aadhaar_number.errors %}
                <div class="invalid-feedback d-block">{{ form.aadhaar_number.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Aadhaar Card</label>
              {{ form.aadhaar_card_file|add_class:"form-control" }}
              <small class="form-text text-muted">Max 5MB, PDF/JPG/PNG</small>
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.pan_number|add_class:"form-control" }}
              {% if form.pan_number.errors %}
                <div class="invalid-feedback d-block">{{ form.pan_number.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">PAN Card</label>
              {{ form.pan_card_file|add_class:"form-control" }}
              <small class="form-text text-muted">Max 5MB, PDF/JPG/PNG</small>
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.passport_number|add_class:"form-control" }}
              {% if form.passport_number.errors %}
                <div class="invalid-feedback d-block">{{ form.passport_number.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Passport Copy</label>
              {{ form.passport_copy_file|add_class:"form-control" }}
              <small class="form-text text-muted">Max 5MB, PDF/JPG/PNG</small>
            </div>
          </div>
          
          <div class="mb-3">
            <label class="form-label">Address Proof</label>
            {{ form.address_proof_file|add_class:"form-control" }}
            <small class="form-text text-muted">Max 5MB, PDF/JPG/PNG</small>
          </div>
        </fieldset>
        
        <!-- Education Details -->
        <fieldset class="mb-4">
          <legend class="fs-5 fw-bold mb-3">Education Details</legend>
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.highest_education|add_class:"form-control" }}
              {% if form.highest_education.errors %}
                <div class="invalid-feedback d-block">{{ form.highest_education.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.year_of_graduation|add_class:"form-control" }}
              {% if form.year_of_graduation.errors %}
                <div class="invalid-feedback d-block">{{ form.year_of_graduation.errors }}</div>
              {% endif %}
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.course|add_class:"form-control" }}
              {% if form.course.errors %}
                <div class="invalid-feedback d-block">{{ form.course.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Degree Certificate</label>
              {{ form.degree_certificate_file|add_class:"form-control" }}
              <small class="form-text text-muted">Max 5MB, PDF/JPG/PNG</small>
            </div>
          </div>
        </fieldset>
        
        <!-- Bank Details -->
        <fieldset class="mb-4">
          <legend class="fs-5 fw-bold mb-3">Bank Details</legend>
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.bank_name|add_class:"form-control" }}
              {% if form.bank_name.errors %}
                <div class="invalid-feedback d-block">{{ form.bank_name.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.branch_name|add_class:"form-control" }}
              {% if form.branch_name.errors %}
                <div class="invalid-feedback d-block">{{ form.branch_name.errors }}</div>
              {% endif %}
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              {{ form.account_holder_name|add_class:"form-control" }}
              {% if form.account_holder_name.errors %}
                <div class="invalid-feedback d-block">{{ form.account_holder_name.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              {{ form.ifsc_code|add_class:"form-control" }}
              {% if form.ifsc_code.errors %}
                <div class="invalid-feedback d-block">{{ form.ifsc_code.errors }}</div>
              {% endif %}
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Bank Account Number *</label>
              {{ form.bank_account_number|add_class:"form-control" }}
              {% if form.bank_account_number.errors %}
                <div class="invalid-feedback d-block">{{ form.bank_account_number.errors }}</div>
              {% endif %}
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Confirm Bank Account Number *</label>
              {{ form.confirm_bank_account_number|add_class:"form-control" }}
              {% if form.confirm_bank_account_number.errors %}
                <div class="invalid-feedback d-block">{{ form.confirm_bank_account_number.errors }}</div>
              {% endif %}
            </div>
          </div>
        </fieldset>
        
        <div class="d-grid gap-2">
          <button type="submit" class="btn btn-primary btn-lg">Submit Registration</button>
          <a href="{% url 'home' %}" class="btn btn-secondary">Cancel</a>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Show/hide correspondence address based on checkbox
  document.getElementById('{{ form.same_as_permanent_address.id_for_label }}').addEventListener('change', function() {
    document.getElementById('correspondence_address_section').style.display = 
      this.checked ? 'none' : 'block';
  });
</script>
{% endblock %}
```

---

## 🚀 Usage Example - Django View

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from recruiters.forms import RecruiterRegistrationFormModel

def recruiter_registration_form_view(request):
    if request.method == 'POST':
        form = RecruiterRegistrationFormModel(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save()
            messages.success(request, 'Registration submitted successfully! We will verify and contact you soon.')
            return redirect('home')
        else:
            # Form has errors, they will be displayed in template
            pass
    else:
        form = RecruiterRegistrationFormModel()
    
    return render(request, 'recruiter_registration_form.html', {'form': form})
```

---

## 🔍 Admin Interface

### Admin Panel Features
- View all recruiter registrations
- Filter by verification status
- Search by email
- Upload missing documents
- Mark as verified/approved
- Audit logging of all actions

---

## 📋 Audit Logging

All actions are logged:
- `recruiter_registration_form_submitted` - Form submission
- `recruiter_registration_verified` - Admin verification
- `recruiter_registration_form_updated` - Form updates

---

## ✅ Checklist for Production

- [ ] Configure MinIO credentials in settings.py
- [ ] Set up MinIO bucket: `hyrind-recruiter-docs`
- [ ] Configure file upload path permissions
- [ ] Test file uploads to MinIO
- [ ] Set up SSL for MinIO (if not using localhost)
- [ ] Configure CORS for file access
- [ ] Add email notifications for admin (optional)
- [ ] Create recruiter registration admin page
- [ ] Set up backup strategy for MinIO files
- [ ] Configure retention policies for documents
- [ ] Add recruiter registration link to home page
- [ ] Test form validation with various inputs
- [ ] Performance test with large file uploads
- [ ] Set up monitoring for file storage

---

## 📞 Support

For issues or questions about the recruiter registration system:
1. Check validation error messages
2. Review model constraints in `recruiters/models.py`
3. Check form validation in `recruiters/forms.py`
4. Verify MinIO configuration in settings.py
5. Review audit logs for action history
