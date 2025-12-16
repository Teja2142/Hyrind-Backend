# 🚀 Hyrind Backend - US IT Recruitment Platform API

<div align="center">

[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![JWT](https://img.shields.io/badge/JWT-Auth-orange.svg)](https://jwt.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Enterprise-grade recruitment platform connecting US IT professionals with opportunities**

[Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-documentation) • [Testing](#-testing) • [Deployment](#-deployment)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Test Credentials](#-test-credentials)
- [Environment Setup](#-environment-setup)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Key Endpoints](#-key-endpoints)
- [Recruiter System](#-recruiter-system)
- [Admin APIs](#-admin-apis)
- [Email Configuration](#-email-configuration)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)

---

## 🎯 Overview

**Hyrind Backend** is a comprehensive Django REST API designed for internal US IT recruitment operations. The platform manages the complete recruitment lifecycle from candidate registration to placement tracking, with specialized tools for internal recruiters (employees) to manage multiple client candidates.

### 🏢 Business Model
- **Target**: US IT Recruitment Agency (Internal Use)
- **Users**: Internal recruiters (employees), candidates, admin
- **Capacity**: Each recruiter manages 1-3 client candidates
- **Focus**: Software development, cloud, DevOps, data science roles

---

---

## ✨ Features

### 🎯 Core Features
- ✅ **User Management**: Complete registration, JWT authentication, profile management with UUID primary keys
- ✅ **Two-Phase Onboarding**: Minimal registration → Comprehensive profile completion after approval
- ✅ **Interest Submission**: Public form for candidates to express interest (no account needed)
- ✅ **Contact Us**: Public contact form with automated email notifications
- ✅ **Recruiter Management**: Full CRUD with auto-generated Employee IDs (H#####)
- ✅ **Job Postings**: Create, list, update, delete with full CRUD operations
- ✅ **Client Assignment**: Admin assigns clients to recruiters (1-3 per recruiter)
- ✅ **Dashboard System**: Enhanced recruiter dashboard with stats, clients, placements
- ✅ **Payment Integration**: Stripe integration for subscription payments
- ✅ **Email Notifications**: HTML email templates with resume attachments

### 🔐 Security & Authentication
- ✅ JWT (JSON Web Token) authentication with access & refresh tokens
- ✅ Role-based permissions (User, Admin, Recruiter, Staff)
- ✅ Secure password hashing with Django's authentication system
- ✅ CSRF protection enabled
- ✅ Admin-only endpoints for sensitive operations
- ✅ Profile activation system for candidate approval
- ✅ Audit logging for admin actions

### 👥 Recruiter System (Internal Staff)
- ✅ **Auto-Generated Employee IDs**: H + 5 random digits (e.g., H12345)
- ✅ **Two-Phase Registration**: 
  - Phase 1: Minimal info (8 fields) + auto-generated Employee ID
  - Phase 2: Comprehensive profile (70+ fields) after admin approval
- ✅ **Dashboard Features**:
  - Profile completion tracking with visual alerts
  - Assigned clients list with full details
  - Performance metrics (placements, applications, slots)
  - Recent placements timeline
- ✅ **Client Management**: Track 1-3 clients per recruiter
- ✅ **Status Tracking**: Pending → Active → Placements
- ✅ **Department & Specialization**: IT Staffing, Healthcare, Finance, etc.

### 📚 Documentation & API
- ✅ Interactive Swagger UI documentation at `/swagger/`
- ✅ ReDoc documentation at `/redoc/`
- ✅ Beautiful homepage with navigation at `/`
- ✅ Comprehensive API guides included

### 📧 Email System
- ✅ HTML email templates with professional design
- ✅ Resume attachment support (PDF/DOCX)
- ✅ Gmail SMTP integration
- ✅ Automated notifications for interest submissions and contact forms

### 🗄️ Database
- ✅ UUID primary keys for all user-related models
- ✅ SQLite for development (easy PostgreSQL migration)
- ✅ Fresh migration system (December 2025)
- ✅ Indexed fields for performance

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Django** | 5.2.8 | Web framework |
| **Django REST Framework** | 3.16.1 | REST API |
| **djangorestframework-simplejwt** | 5.5.1 | JWT authentication |
| **drf-yasg** | 1.21.11 | API documentation (Swagger/OpenAPI) |
| **Stripe** | 13.2.0 | Payment processing |
| **python-dotenv** | 1.0.0 | Environment configuration |
| **SQLite** | 3.x | Database (development) |

---

## 📁 Project Structure

```
Hyrind-Backend/
├── 📁 Core Django Apps
│   ├── users/              # User & Profile management
│   │   ├── models.py       # Profile, InterestSubmission, Contact (UUID PKs)
│   │   ├── serializers.py  # 5 specialized serializers with validation
│   │   ├── views.py        # Registration, login, admin APIs
│   │   └── urls.py         # User & admin endpoints
│   │
│   ├── recruiters/         # Internal recruiter system
│   │   ├── models.py       # Recruiter, Assignment, RecruiterRegistration (UUID PKs)
│   │   ├── serializers.py  # 8 specialized serializers
│   │   ├── views.py        # CRUD, activation, dashboard APIs
│   │   ├── forms.py        # 3 Django forms (minimal, comprehensive, basic)
│   │   ├── urls.py         # API endpoints (REST)
│   │   ├── web_urls.py     # Web endpoints (HTML templates)
│   │   └── web_views.py    # Dashboard, profile, registration views
│   │
│   ├── jobs/               # Job posting management
│   │   ├── models.py       # Job model with full details
│   │   ├── serializers.py  # Job serializer
│   │   └── views.py        # Job CRUD operations
│   │
│   ├── payments/           # Stripe payment processing
│   │   ├── models.py       # Payment records
│   │   └── views.py        # Stripe integration
│   │
│   ├── subscriptions/      # Subscription management
│   ├── onboarding/         # User onboarding flow
│   └── audit/              # Audit logging utility
│
├── 📁 Configuration
│   ├── hyrind/             # Main project settings
│   │   ├── settings.py     # Django configuration
│   │   ├── urls.py         # Master URL routing
│   │   └── admin.py        # Custom admin site
│   │
│   └── templates/          # HTML templates (Bootstrap 5)
│       ├── home.html                       # Landing page
│       ├── recruiter_dashboard.html        # Enhanced dashboard
│       ├── recruiter_complete_profile.html # 70+ field form
│       ├── recruiter_registration_form.html# Minimal registration
│       ├── recruiter_profile.html          # Basic profile update
│       └── recruiter_login.html            # Login page
│
├── 📁 Documentation
│   ├── README.md                    # This file (main guide)
│   ├── API_STATUS_CHECKLIST.md     # Complete API reference
│   ├── REQUIREMENTS_CHECKLIST.md   # Quick requirements checklist
│   ├── TESTING_FLOW.md             # Testing guide for onboarding
│   ├── RECRUITER_API_GUIDE.md      # Recruiter API documentation
│   └── RECRUITER_SYSTEM_IMPLEMENTATION.md # Implementation details
│
├── 📁 Resources
│   ├── media/              # User uploads (resumes, ID proofs)
│   ├── tests/              # Test suite
│   └── utils/              # Helper utilities
│
├── 📄 Configuration Files
│   ├── .env.example        # Environment template
│   ├── requirements.txt    # Python dependencies
│   ├── manage.py           # Django management script
│   └── db.sqlite3          # SQLite database (dev)
│
└── 📄 Setup Scripts
    ├── create_test_data.py # Creates test accounts
    ├── fix_database.ps1    # Database fix script (PowerShell)
    └── setup_email.ps1     # Email setup helper
```

---

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.10 or higher
- **pip**: Python package manager
- **Git**: Version control
- **Virtual Environment**: Recommended for isolation

### 🔥 Fast Setup (Recommended)

```powershell
# Windows PowerShell - Complete setup in 3 minutes
# Clone repository
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend

# Create virtual environment
python -m venv hy_env
.\hy_env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your email settings (optional for basic testing)

# Initialize database with fresh migrations
python manage.py migrate

# Create test data (includes admin, candidate, recruiter)
python create_test_data.py

# Start server
python manage.py runserver
```

**✅ Done! Access:**
- **Homepage**: http://127.0.0.1:8000/
- **API Docs**: http://127.0.0.1:8000/swagger/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

### 🐧 Linux/macOS Setup

```bash
# Clone repository
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend

# Create virtual environment
python3 -m venv hy_env
source hy_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env as needed

# Initialize database
python manage.py migrate

# Create test data
python create_test_data.py

# Start server
python manage.py runserver
```

---

### 🗄️ Database Setup (Fresh Migrations)

If you encounter migration issues or need a fresh start:

```powershell
# Run the automated fix script (Windows)
.\fix_database.ps1

# OR manually:
# 1. Backup database (if exists)
Copy-Item db.sqlite3 db.sqlite3.backup

# 2. Delete old migrations (except __init__.py)
Get-ChildItem -Path users\migrations, recruiters\migrations, jobs\migrations -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item

# 3. Delete database
Remove-Item db.sqlite3

# 4. Create fresh migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create test data
python create_test_data.py
```

---

---

## 🔑 Test Credentials

After running `create_test_data.py`, you'll have three ready-to-use accounts:

### 👨‍💼 Admin Account
```
Email:    admin@hyrind.com
Password: admin123
Role:     Superuser (full access)
Access:   http://127.0.0.1:8000/admin/
```
**Capabilities:**
- ✅ Activate/deactivate candidates
- ✅ Activate/deactivate recruiters
- ✅ Assign clients to recruiters
- ✅ Manage all data via Django admin
- ✅ View audit logs

---

### 👤 Candidate Account
```
Email:    candidate@test.com
Password: test123
Role:     Candidate (job seeker)
Status:   Active (approved)
```
**Profile Details:**
- Name: John Doe
- Phone: 1234567890
- University: Test University
- Degree: Bachelor's in Computer Science
- Visa Status: F1-OPT

**API Access:**
```bash
# Login to get JWT token
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"candidate@test.com","password":"test123"}'
```

---

### 💼 Recruiter Account
```
Email:       recruiter@test.com
Password:    test123
Employee ID: H12345
Role:        Internal Recruiter (staff)
Status:      Active (approved)
Dashboard:   http://127.0.0.1:8000/recruiter-registration/dashboard/
```
**Profile Details:**
- Name: Jane Smith
- Phone: 9876543210
- Department: IT Staffing
- Specialization: Software Development
- Max Clients: 3
- Current Clients: 0
- Joining Date: Today

**Web Access:**
1. **Login**: http://127.0.0.1:8000/recruiter-registration/login/
2. **Dashboard**: View assigned clients, stats, placements
3. **Complete Profile**: 70+ field comprehensive form

**API Access:**
```bash
# Login to get JWT token + recruiter details
curl -X POST http://127.0.0.1:8000/api/recruiters/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"recruiter@test.com","password":"test123"}'
```

---

### 🔐 Security Notes

⚠️ **These are test credentials for development only!**

**For Production:**
- Change all default passwords immediately
- Use strong passwords (min 12 characters, mixed case, numbers, symbols)
- Enable 2FA for admin accounts
- Rotate secrets regularly
- Never commit credentials to version control

**Create New Admin:**
```bash
python manage.py createsuperuser
```

---

## ⚙️ Environment Setup

Create a `.env` file in the root directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
OPERATIONS_EMAIL=hyrind.operations@gmail.com

# Stripe Payment (optional)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# JWT Settings (optional - has defaults)
JWT_ACCESS_TOKEN_LIFETIME=5  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)
```

**Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833). See `EMAIL_SETUP.md` for detailed instructions.

---

## 📚 API Documentation

The API is fully documented using Swagger/OpenAPI 3.0.

### Access Documentation
- **Swagger UI**: http://127.0.0.1:8000/swagger/ (interactive)
- **ReDoc**: http://127.0.0.1:8000/redoc/ (read-only)
- **JSON Schema**: http://127.0.0.1:8000/swagger.json

### Using Swagger UI

1. Navigate to http://127.0.0.1:8000/swagger/
2. Click on any endpoint to see details
3. For protected endpoints:
   - Login via `/api/users/login/` to get JWT token
   - Click **🔓 Authorize** button
   - Enter: `Bearer <your_access_token>`
   - Click **Authorize**

---

## 🔐 Authentication

### JWT Token-Based Authentication

This project uses JWT (JSON Web Tokens) for authentication.

#### Getting Tokens

**Endpoint**: `POST /api/users/login/`

```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
  }'
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Using Tokens

Include the **access token** in the Authorization header:

```bash
curl -X GET http://127.0.0.1:8000/api/users/profiles/ \
  -H "Authorization: Bearer <access_token>"
```

#### Token Types

| Token Type | Purpose | Lifespan |
|------------|---------|----------|
| **Access Token** | API requests | 5-60 minutes |
| **Refresh Token** | Get new access token | 24 hours - 7 days |

#### Refreshing Tokens

When access token expires:

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

**See `AUTHENTICATION_GUIDE.md` for detailed authentication documentation.**

---

## 👥 Recruiter System

### Overview
Internal IT recruitment staff management system with two-phase onboarding and client assignment tracking.

### Key Features

#### 🆔 Auto-Generated Employee IDs
- **Format**: H + 5 random digits (e.g., H12345, H98765)
- **Automatic**: Generated on registration (no user input)
- **Unique**: Checked for duplicates
- **Persistent**: Never changes after assignment

#### 📝 Two-Phase Onboarding

**Phase 1: Minimal Registration** (8 fields)
```
- Email, Password
- First Name, Last Name
- Phone Number
- Department (IT Staffing, Healthcare, Finance, etc.)
- Specialization (Software Dev, Cloud, DevOps, etc.)
- Date of Joining
- LinkedIn URL (optional)
```
**Result**: Account created with `status='pending'`, auto-generated Employee ID shown

**Phase 2: Comprehensive Profile** (70+ fields)
After admin approval, recruiter completes:
```
- Personal Details (DOB, gender, marital status, blood group)
- Family Details (father, mother, spouse, emergency contact)
- Contact Details (WhatsApp, alternate phone)
- Address Details (permanent, correspondence)
- ID Proofs (Aadhaar, PAN, Passport with uploads)
- Education Details (degree, year, course, certificates)
- Bank Details (account, IFSC, branch)
```
**Result**: `is_verified=True`, full access to system

#### 📊 Enhanced Dashboard

**Profile Completion Alert**
- Red banner displayed when profile incomplete
- "Complete Now" button links to comprehensive form
- Banner disappears after profile completion

**Stats Cards**
- Assigned Clients (current count)
- Total Placements (lifetime)
- Active Applications (in progress)
- Available Slots (remaining capacity)

**Assigned Clients Section**
- Full client details (name, email, phone)
- Assignment date and status
- Priority indicators (high/medium/low)
- Notes and special instructions

**Recent Placements**
- Last 5 successful placements
- Placement dates
- Client names

**Account Info Panel**
- Status (pending/active/inactive)
- Max clients allowed
- Date of joining
- Profile completion status

### Recruiter Workflow

```
1. REGISTRATION
   ↓
   Register at /recruiter-registration/
   Fill 8 basic fields
   ↓
   Employee ID auto-generated (H#####)
   Status: Pending
   ↓

2. ADMIN APPROVAL
   ↓
   Admin logs into /admin/
   Reviews recruiter profile
   Sets status='active', active=True
   ↓

3. FIRST LOGIN
   ↓
   Recruiter logs in
   Redirected to Dashboard
   Sees RED BANNER: "Profile Incomplete"
   ↓

4. PROFILE COMPLETION
   ↓
   Clicks "Complete Now"
   Fills 70+ fields
   Uploads documents
   Submits
   ↓
   Returns to dashboard
   Banner disappears ✓
   ↓

5. DAILY USAGE
   ↓
   View assigned clients
   Track placements
   Update applications
   Manage client relationships
```

### API Endpoints

#### Authentication
```bash
# Register (Public)
POST /api/recruiters/register/
# Returns: Employee ID, status='pending'

# Login (Public)
POST /api/recruiters/login/
# Returns: JWT tokens + recruiter details

# Get Own Profile (Authenticated)
GET /api/recruiters/me/
# Returns: Full recruiter profile

# Update Own Profile (Authenticated)
PATCH /api/recruiters/me/
# Update: phone, department, specialization, etc.
```

#### Admin Operations
```bash
# List All Recruiters (Admin Only)
GET /api/recruiters/

# Get Recruiter Details (Admin Only)
GET /api/recruiters/<uuid>/

# Activate Recruiter (Admin Only)
PATCH /api/recruiters/<uuid>/activate/

# Deactivate Recruiter (Admin Only)
PATCH /api/recruiters/<uuid>/deactivate/

# Assign Client (Admin Only)
POST /api/recruiters/assign/
```

### Web Interface (HTML Templates)

```
/recruiter-registration/           → Registration form
/recruiter-registration/login/     → Login page
/recruiter-registration/dashboard/ → Main dashboard
/recruiter-registration/profile/   → Basic profile update
/recruiter-registration/complete-profile/ → Comprehensive form
/recruiter-registration/logout/    → Logout
```

---

## 🔐 Admin APIs

### Candidate Management

#### Activate Candidate
```bash
PATCH /api/users/admin/candidates/<uuid>/activate/
Authorization: Bearer <admin_token>

# Response
{
  "message": "Candidate activated successfully",
  "profile": { profile_data }
}
```

#### Deactivate Candidate
```bash
PATCH /api/users/admin/candidates/<uuid>/deactivate/
Authorization: Bearer <admin_token>

# Response
{
  "message": "Candidate deactivated successfully",
  "profile": { profile_data }
}
```

### Recruiter Management

#### Activate Recruiter
```bash
PATCH /api/recruiters/<uuid>/activate/
Authorization: Bearer <admin_token>

# Response
{
  "message": "Recruiter activated successfully",
  "recruiter": {
    "id": "uuid",
    "employee_id": "H12345",
    "name": "Jane Smith",
    "status": "active",
    "active": true
  }
}
```

#### Deactivate Recruiter
```bash
PATCH /api/recruiters/<uuid>/deactivate/
Authorization: Bearer <admin_token>

# Response
{
  "message": "Recruiter deactivated successfully",
  "recruiter": { recruiter_data }
}
```

### Admin Profile & Settings

#### Get Admin Profile
```bash
GET /api/users/admin/profile/
Authorization: Bearer <admin_token>

# Response
{
  "id": "uuid",
  "first_name": "Admin",
  "last_name": "User",
  "email": "admin@hyrind.com",
  "phone": "1234567890"
}
```

#### Change Admin Password
```bash
POST /api/users/admin/password/
Authorization: Bearer <admin_token>

# Request Body
{
  "old_password": "current_password",
  "new_password": "new_secure_password",
  "new_password_confirm": "new_secure_password"
}

# Response
{
  "message": "Password changed successfully"
}
```

### Admin Login
```bash
POST /api/users/login/
Content-Type: application/json

# Request Body
{
  "email": "admin@hyrind.com",
  "password": "admin123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Permission Requirements

| Endpoint | Permission | Notes |
|----------|-----------|-------|
| Candidate Activate/Deactivate | `IsAdminUser` | Admin/staff only |
| Recruiter Activate/Deactivate | `IsAdminUser` | Admin/staff only |
| Admin Profile | `IsAdminUser` | Own profile only |
| Admin Password Change | `IsAdminUser` | Requires old password |
| List All Recruiters | `IsAdminUser` | Full list access |
| Assign Client | `IsAdminUser` | Assignment management |

---

## 🌐 Key Endpoints

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description | Returns |
|--------|----------|-------------|---------|
| `GET` | `/` | Homepage with navigation | HTML |
| `POST` | `/api/users/register/` | Register candidate account | Profile ID (UUID) |
| `POST` | `/api/users/login/` | Login (all user types) | JWT tokens |
| `POST` | `/api/users/interest/` | Submit interest form | Submission ID |
| `POST` | `/api/users/contact/` | Submit contact form | Confirmation |
| `POST` | `/api/recruiters/register/` | Register recruiter | Employee ID (H#####) |
| `POST` | `/api/recruiters/login/` | Recruiter login | JWT + recruiter details |
| `GET` | `/swagger/` | Interactive API docs | Swagger UI |
| `GET` | `/redoc/` | API documentation | ReDoc UI |
| `GET` | `/recruiter-registration/` | Recruiter registration page | HTML |
| `GET` | `/recruiter-registration/login/` | Recruiter login page | HTML |

### Protected Endpoints (Authentication Required)

#### User & Profile Management
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/users/` | List all users | Admin |
| `GET` | `/api/users/profiles/` | List all profiles | Admin |
| `GET` | `/api/users/profiles/<uuid>/` | Get profile by UUID | Owner/Admin |
| `PATCH` | `/api/users/profiles/<uuid>/` | Update profile | Owner/Admin |
| `DELETE` | `/api/users/profiles/<uuid>/` | Delete profile | Admin |

#### Recruiter Management
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/recruiters/` | List all recruiters | Admin |
| `GET` | `/api/recruiters/me/` | Get own profile | Recruiter |
| `PATCH` | `/api/recruiters/me/` | Update own profile | Recruiter |
| `GET` | `/api/recruiters/<uuid>/` | Get recruiter by UUID | Admin |
| `PATCH` | `/api/recruiters/<uuid>/` | Update recruiter | Admin |
| `DELETE` | `/api/recruiters/<uuid>/` | Soft delete recruiter | Admin |
| `PATCH` | `/api/recruiters/<uuid>/activate/` | Activate recruiter | Admin |
| `PATCH` | `/api/recruiters/<uuid>/deactivate/` | Deactivate recruiter | Admin |
| `POST` | `/api/recruiters/assign/` | Assign client to recruiter | Admin |
| `GET` | `/api/recruiters/dashboard/` | Get dashboard data | Recruiter |

#### Web Interface (HTML)
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/recruiter-registration/dashboard/` | Recruiter dashboard | Recruiter |
| `GET` | `/recruiter-registration/profile/` | Basic profile update | Recruiter |
| `GET` | `/recruiter-registration/complete-profile/` | Comprehensive form | Recruiter |
| `POST` | `/recruiter-registration/complete-profile/` | Submit profile | Recruiter |
| `GET` | `/recruiter-registration/logout/` | Logout | Recruiter |

#### Admin Operations
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/users/admin/profile/` | Get admin profile | Admin |
| `POST` | `/api/users/admin/password/` | Change password | Admin |
| `PATCH` | `/api/users/admin/candidates/<uuid>/activate/` | Activate candidate | Admin |
| `PATCH` | `/api/users/admin/candidates/<uuid>/deactivate/` | Deactivate candidate | Admin |

#### Job Management
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/jobs/` | List all jobs | Authenticated |
| `POST` | `/api/jobs/` | Create job posting | Recruiter/Admin |
| `GET` | `/api/jobs/<id>/` | Get job details | Authenticated |
| `PATCH` | `/api/jobs/<id>/` | Update job | Recruiter/Admin |
| `DELETE` | `/api/jobs/<id>/` | Delete job | Admin |

#### Payments & Subscriptions
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/payments/` | List payments | Authenticated |
| `POST` | `/api/payments/` | Process payment | Authenticated |
| `GET` | `/api/subscriptions/` | List subscriptions | Authenticated |
| `POST` | `/api/subscriptions/` | Create subscription | Authenticated |

---

## 📧 Email Configuration

### Gmail Setup (Recommended for Development)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Copy the generated 16-character password
3. **Update `.env` file**:
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   OPERATIONS_EMAIL=hyrind.operations@gmail.com
   ```

### Email Features

- ✅ HTML email templates with beautiful gradient design
- ✅ Inline CSS for cross-client compatibility
- ✅ Resume file attachments (PDF/DOCX)
- ✅ Clickable links and formatted tables
- ✅ Automated notifications for:
  - Interest form submissions
  - Contact form messages
  - Recruiter assignments

### Testing Email

Run the test script:
```powershell
python test_email.py
```

Or use the setup script (Windows):
```powershell
.\setup_email.ps1
```

**See `EMAIL_SETUP.md` for detailed email configuration guide.**

---

## 🧪 Testing

### Automated Test Data Setup

The quickest way to get started:

```bash
# Activate virtual environment first
.\hy_env\Scripts\Activate.ps1  # Windows
source hy_env/bin/activate      # Linux/Mac

# Run test data creation script
python create_test_data.py
```

**This creates:**
- ✅ Admin account (admin@hyrind.com / admin123)
- ✅ Active candidate (candidate@test.com / test123)
- ✅ Active recruiter (recruiter@test.com / test123, ID: H12345)

### Manual Testing

#### 1. Test User Registration
```bash
curl -X POST http://127.0.0.1:8000/api/users/register/ \
  -F "email=newuser@test.com" \
  -F "password=Test123!" \
  -F "confirm_password=Test123!" \
  -F "first_name=Test" \
  -F "last_name=User" \
  -F "phone=1234567890" \
  -F "university=Test University" \
  -F "degree=Bachelor's" \
  -F "major=Computer Science" \
  -F "visa_status=F1-OPT" \
  -F "graduation_date=05/2025" \
  -F "consent_to_terms=true"
```

#### 2. Test Login
```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"candidate@test.com","password":"test123"}'
```

#### 3. Test Recruiter Dashboard
```bash
# Login first to get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/recruiters/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"recruiter@test.com","password":"test123"}' \
  | jq -r '.access')

# Access dashboard API
curl -X GET http://127.0.0.1:8000/api/recruiters/dashboard/ \
  -H "Authorization: Bearer $TOKEN"
```

### Using Swagger UI (Recommended)

1. **Start server**: `python manage.py runserver`
2. **Open Swagger**: http://127.0.0.1:8000/swagger/
3. **Login to get token**:
   - Expand `POST /api/users/login/`
   - Click "Try it out"
   - Enter: `{"email":"admin@hyrind.com","password":"admin123"}`
   - Click "Execute"
   - Copy the `access` token
4. **Authorize**:
   - Click **🔓 Authorize** button (top right)
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"
5. **Test any endpoint** - Click "Try it out" on any endpoint

### Run Django Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test recruiters
python manage.py test jobs

# Run with verbosity
python manage.py test --verbosity=2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML report in htmlcov/
```

### Test Recruiter Onboarding Flow

Follow the complete workflow:

```bash
# 1. Register recruiter
curl -X POST http://127.0.0.1:8000/api/recruiters/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testrecruiter@test.com",
    "password": "Test123!",
    "password_confirm": "Test123!",
    "first_name": "Test",
    "last_name": "Recruiter",
    "phone": "9999999999",
    "employee_id": "H99999",
    "department": "it_staffing",
    "specialization": "software_dev",
    "date_of_joining": "2025-12-09"
  }'

# 2. Get UUID from response
# 3. Login as admin and activate
# 4. Test recruiter login
# 5. Access dashboard
# 6. Complete profile
```

See `TESTING_FLOW.md` for detailed step-by-step testing guide.

---

## ⚠️ Troubleshooting

### Common Issues & Solutions

#### ❌ Issue: `no such column: users_profile.active`

**Cause**: Database schema is outdated (migrations not applied)

**Solution**:
```bash
# Quick fix (Windows)
.\fix_database.ps1

# OR Manual fix:
python manage.py migrate
# If that fails, use fresh migrations (see Database Setup section)
```

---

#### ❌ Issue: `ModuleNotFoundError: No module named 'django'`

**Cause**: Virtual environment not activated

**Solution**:
```bash
# Windows
.\hy_env\Scripts\Activate.ps1

# Linux/Mac
source hy_env/bin/activate

# Verify
python -c "import django; print(django.get_version())"
# Should output: 5.2.8
```

---

#### ❌ Issue: Recruiter login redirects to wrong page

**Cause**: Fixed in recent update

**Solution**: Already resolved - login now redirects to dashboard automatically. If still seeing issues:
```bash
# Pull latest changes
git pull origin main
python manage.py runserver
```

---

#### ❌ Issue: "Profile Incomplete" banner doesn't disappear

**Cause**: RecruiterRegistration not created or `is_verified=False`

**Solution**:
1. Login to recruiter dashboard
2. Click "Complete Now" button
3. Fill comprehensive form
4. Submit form
5. Check that `is_verified=True` in database

**Verify via Admin**:
```
/admin/recruiters/recruiterregistration/
Find your email → Check 'Is verified' → Save
```

---

#### ❌ Issue: Employee ID not auto-generating

**Cause**: Old form code or manual input

**Solution**: Employee IDs are auto-generated - do NOT include `employee_id` field in registration form. The backend generates it automatically in format H##### (e.g., H12345).

**Check**: Registration form should NOT have an employee_id input field.

---

#### ❌ Issue: Migration conflicts

**Cause**: Multiple migration files or database/code mismatch

**Solution**: Use fresh migrations approach:
```powershell
# Windows PowerShell
.\fix_database.ps1

# OR manually:
# 1. Backup database
Copy-Item db.sqlite3 db.sqlite3.backup

# 2. Delete migrations (except __init__.py)
Get-ChildItem -Recurse -Filter "0*.py" | Where-Object {$_.DirectoryName -like "*migrations*"} | Remove-Item

# 3. Delete database
Remove-Item db.sqlite3

# 4. Fresh migrations
python manage.py makemigrations
python manage.py migrate
python create_test_data.py
```

---

#### ❌ Issue: Static files not loading

**Cause**: Static files not collected

**Solution**:
```bash
python manage.py collectstatic --noinput
```

---

#### ❌ Issue: Email not sending

**Cause**: Gmail App Password not configured

**Solution**:
1. Enable 2FA on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Update `.env`:
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   ```
4. Test: `python test_email.py`

See `EMAIL_SETUP.md` for detailed guide.

---

#### ❌ Issue: JWT token expired

**Cause**: Access token lifespan expired (default 30 minutes)

**Solution**: Use refresh token to get new access token:
```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

---

#### ❌ Issue: CORS errors from frontend

**Cause**: Frontend domain not in CORS whitelist

**Solution**: Update `hyrind/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite default
    'http://localhost:3000',  # React default
    'https://yourdomain.com',  # Production
]
```

---

### Getting Help

If you encounter issues not listed above:

1. **Check Logs**: Look at terminal output for error details
2. **Check Django Admin**: http://127.0.0.1:8000/admin/ - verify data
3. **Check Database**: Use SQLite browser or Django shell
4. **Read Docs**: Check documentation files in project root
5. **GitHub Issues**: https://github.com/Teja2142/Hyrind-Backend/issues

---

## 🚀 Deployment

### Pre-Deployment Checklist

Before deploying to production:

- [ ] **Security Settings**
  ```python
  # hyrind/settings.py - Production settings
  DEBUG = False
  ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
  SECRET_KEY = os.getenv('SECRET_KEY')  # Generate new one!
  ```

- [ ] **Database Migration**
  ```bash
  # Switch to PostgreSQL or MySQL (not SQLite)
  # Update settings.py:
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'hyrind_db',
          'USER': 'db_user',
          'PASSWORD': os.getenv('DB_PASSWORD'),
          'HOST': 'db.host.com',
          'PORT': '5432',
      }
  }
  ```

- [ ] **Static Files**
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] **CORS Configuration**
  ```python
  CORS_ALLOWED_ORIGINS = [
      'https://yourdomain.com',
      'https://www.yourdomain.com',
  ]
  ```

- [ ] **Environment Variables**
  ```env
  SECRET_KEY=your-secure-secret-key-50-chars-long
  DEBUG=False
  DATABASE_URL=postgresql://user:password@host:port/database
  EMAIL_HOST_USER=your-production-email@gmail.com
  EMAIL_HOST_PASSWORD=your-app-password
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```

---

### Deployment Platforms

#### ☁️ Heroku (Recommended for beginners)

1. **Create Heroku app**:
   ```bash
   heroku create hyrind-backend
   ```

2. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set EMAIL_HOST_USER=email@gmail.com
   heroku config:set EMAIL_HOST_PASSWORD=app-password
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python create_test_data.py
   ```

5. **Open app**: `heroku open`

---

#### 🐋 Docker (Recommended for production)

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   RUN python manage.py collectstatic --noinput
   
   EXPOSE 8000
   
   CMD ["gunicorn", "hyrind.wsgi:application", "--bind", "0.0.0.0:8000"]
   ```

2. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'
   
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: hyrind_db
         POSTGRES_USER: hyrind_user
         POSTGRES_PASSWORD: ${DB_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     web:
       build: .
       command: gunicorn hyrind.wsgi:application --bind 0.0.0.0:8000
       volumes:
         - .:/app
       ports:
         - "8000:8000"
       depends_on:
         - db
       environment:
         DATABASE_URL: postgresql://hyrind_user:${DB_PASSWORD}@db:5432/hyrind_db
         SECRET_KEY: ${SECRET_KEY}
         DEBUG: False
   
   volumes:
     postgres_data:
   ```

3. **Deploy**:
   ```bash
   docker-compose up -d
   docker-compose exec web python manage.py migrate
   docker-compose exec web python create_test_data.py
   ```

---

#### 🌐 AWS EC2 (Full control)

1. **Launch Ubuntu EC2 instance**
2. **SSH into server**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```

4. **Clone and setup**:
   ```bash
   git clone https://github.com/Teja2142/Hyrind-Backend.git
   cd Hyrind-Backend
   python3 -m venv hy_env
   source hy_env/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn hyrind.wsgi:application --bind 0.0.0.0:8000 --daemon
   ```

6. **Configure Nginx**:
   ```nginx
   # /etc/nginx/sites-available/hyrind
   server {
       listen 80;
       server_name yourdomain.com;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   
       location /static/ {
           alias /home/ubuntu/Hyrind-Backend/staticfiles/;
       }
   }
   ```

7. **Enable site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/hyrind /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

### Production Database Setup

#### PostgreSQL Setup (Recommended)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE hyrind_db;
CREATE USER hyrind_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE hyrind_db TO hyrind_user;
\q

# Update settings.py
pip install psycopg2-binary
```

---

### SSL/HTTPS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

---

### Monitoring & Maintenance

#### Setup System Service (Ubuntu)

Create `/etc/systemd/system/hyrind.service`:

```ini
[Unit]
Description=Hyrind Django Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Hyrind-Backend
Environment="PATH=/home/ubuntu/Hyrind-Backend/hy_env/bin"
ExecStart=/home/ubuntu/Hyrind-Backend/hy_env/bin/gunicorn hyrind.wsgi:application --bind 0.0.0.0:8000 --workers 3

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hyrind
sudo systemctl start hyrind
sudo systemctl status hyrind
```

#### Setup Logging

```python
# settings.py - Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/hyrind/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

---

### Backup Strategy

```bash
# Backup database (PostgreSQL)
pg_dump -U hyrind_user hyrind_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U hyrind_user hyrind_db < backup_20251209.sql

# Automated backups (cron)
0 2 * * * /home/ubuntu/backup_db.sh  # Daily at 2 AM
```

---

### Performance Optimization

1. **Enable Django Caching**:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

2. **Database Indexing**: Already optimized with UUID indexes

3. **Gunicorn Workers**: `workers = (CPU cores × 2) + 1`

4. **CDN for Static Files**: Use AWS CloudFront or Cloudflare

---

### Security Checklist

- ✅ DEBUG=False
- ✅ Secure SECRET_KEY (50+ characters)
- ✅ HTTPS/SSL enabled
- ✅ Database password strong (16+ characters)
- ✅ CORS properly configured
- ✅ Email credentials secure (app passwords)
- ✅ File upload limits set
- ✅ Rate limiting enabled
- ✅ Security headers configured:
  ```python
  SECURE_BROWSER_XSS_FILTER = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  X_FRAME_OPTIONS = 'DENY'
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  ```

---

## 📖 Additional Documentation

- **`AUTHENTICATION_GUIDE.md`** - Complete JWT authentication guide
- **`EMAIL_SETUP.md`** - Email configuration instructions
- **`RECRUITER_API_GUIDE.md`** - Recruiter management API details
- **`TESTING_GUIDE.md`** - Step-by-step testing instructions
- **`EMAIL_PREVIEW.md`** - Email template preview

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 📞 Support

For questions or issues:
- **GitHub Issues**: https://github.com/Teja2142/Hyrind-Backend/issues
- **Email**: hyrind.operations@gmail.com

---

## 🎯 Project Status

✅ **Completed Features**:
- User registration & authentication (JWT)
- Profile management with file uploads
- Interest submission form (public)
- Contact form (public)
- Recruiter CRUD operations
- Job posting management
- Email notifications (HTML templates)
- API documentation (Swagger/ReDoc)
- Beautiful homepage UI

🚧 **In Progress**:
- Payment processing (Stripe integration)
- Advanced job search & filtering
- Candidate-recruiter matching algorithm

📋 **Planned Features**:
- Real-time notifications
- Video interview scheduling
- Document verification
- Advanced analytics dashboard
- Mobile app API support

---

**Built with ❤️ by the Hyrind Team**