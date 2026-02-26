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

### 📚 Complete API Documentation

**NEW!** Comprehensive API documentation with all endpoints organized by role and purpose:

📖 **[Complete API Endpoint Reference](./API_ENDPOINTS_COMPLETE.md)** - Full documentation with:
- All 70+ endpoints organized by role (Public, Client, Recruiter, Admin)
- Request/response examples for every endpoint
- Authentication requirements clearly marked
- ID parameter reference (UUID vs integer)
- Quick start examples for common workflows
- Response status codes and error handling

**Quick Links:**
- [📖 Full API Documentation](./API_DOCUMENTATION.md) - In-depth guide with examples
- [⚡ Quick Reference](./API_QUICK_REFERENCE.md) - Quick lookup table
- [🔄 Status Workflow](./CANDIDATE_STATUS_WORKFLOW.md) - Candidate lifecycle
- [🔐 Authentication Guide](./help_docs/EMAIL_SETUP.md) - Setup and configuration

**Interactive Documentation:**
- **Swagger UI**: http://localhost:8000/swagger/ (Try endpoints live)
- **ReDoc**: http://localhost:8000/redoc/ (Clean, readable docs)
- **Admin Panel**: http://localhost:8000/admin/ (Backend management)

**API Coverage by Module:**
- ✅ **Authentication** (4 endpoints) - Client, Admin, Recruiter login
- ✅ **Users & Profiles** (15 endpoints) - Registration, profile management
- ✅ **Client Forms** (8 endpoints) - Intake sheets, credentials
- ✅ **Admin Management** (10 endpoints) - Candidate approvals, status changes
- ✅ **Recruiters** (12 endpoints) - Recruiter management & dashboard
- ✅ **Jobs** (5 endpoints) - Job postings & CRUD
- ✅ **Role Suggestions** (8 endpoints) - AI-powered role matching
- ✅ **Payments** (6 endpoints) - Razorpay integration
- ✅ **Invoices** (5 endpoints) - Invoice management
- ✅ **Subscriptions** (12 endpoints) - Plans & billing
- ✅ **Onboarding** (4 endpoints) - Workflow tracking
- ✅ **Public** (3 endpoints) - Contact, interest forms

**Total: 92 API Endpoints** across all modules

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
- **MySQL Server**: 8.0 or higher
- **Git**: Version control
- **Virtual Environment**: Recommended for isolation

### 🔥 Fast Setup (Recommended)

```powershell
# Windows PowerShell - Complete setup in 5 minutes

# 1. Clone repository
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend

# 2. Create virtual environment
python -m venv hire_venv
.\hire_venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
copy .env.example .env
# Edit .env with your MySQL and email settings

# 5. Setup MySQL database
# - Start MySQL service: net start mysql
# - Create database: CREATE DATABASE hyrind;

# 6. Initialize database with migrations
python manage.py migrate

# 7. Create superuser (optional)
python manage.py createsuperuser

# 8. Start server
python manage.py runserver
```

**✅ Done! Access:**
- **Homepage**: http://127.0.0.1:8000/
- **API Docs**: http://127.0.0.1:8000/swagger/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

### 🐧 Linux/macOS Setup

```bash
# 1. Clone repository
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend

# 2. Create virtual environment
python3 -m venv hire_venv
source hire_venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your MySQL and email settings

# 5. Setup MySQL database
# Start MySQL: sudo systemctl start mysql (Linux) or brew services start mysql (macOS)
# Create database: mysql -u root -p -e "CREATE DATABASE hyrind;"

# 6. Initialize database
python manage.py migrate

# 7. Create superuser (optional)
python manage.py createsuperuser

# 8. Start server
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

---

**Environment Configuration**

- **Supported filenames:** `properties-dev.env`, `properties-qa.env`, `properties-stag.env`, `properties-prod.env`.
- **Which env var selects the file:** Set `HYRIND_ENV`, `DJANGO_ENV`, or `ENV` to one of `dev`, `qa`, `stag`, or `prod`. The loader in `hyrind/settings.py` will prefer `properties-<env>.env` and fall back to a legacy `.env` when present.
- **Do NOT store secrets in the repo:** `SECRET_KEY`, database passwords, email passwords, and third-party API keys have been removed from the repository templates. Inject them at deploy-time from environment variables or a secrets manager.

Example systemd service snippet (set environment from a secure file):

```ini
[Service]
EnvironmentFile=/etc/hyrind/properties-prod.env
Environment=HYRIND_ENV=prod
ExecStart=/path/to/hire_venv/bin/gunicorn hyrind.wsgi:application
``` 

Example `docker-compose.yml` fragment using an external env file or secrets:

```yaml
services:
  hyrind:
    image: hyrind-backend:latest
    env_file:
      - ./properties-prod.env   # keep this out of the image; mount at deploy time
    environment:
      - HYRIND_ENV=prod
    secrets:
      - db_password

secrets:
  db_password:
    external: true
```

Quick checklist when deploying:
- Ensure `properties-<env>.env` is present on the host (or inject variables via CI/CD).
- Populate `SECRET_KEY`, `DB_PASSWORD`, `EMAIL_HOST_PASSWORD`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, etc., from your secret store.
- Set `HYRIND_ENV` (or `DJANGO_ENV`/`ENV`) to the matching environment token.

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
# ===========================================
# DJANGO CORE SETTINGS
# ===========================================
SECRET_KEY=your-super-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ===========================================
# DATABASE CONFIGURATION (MySQL)
# ===========================================
DB_NAME=hyrind
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# ===========================================
# EMAIL CONFIGURATION
# ===========================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
OPERATIONS_EMAIL=hyrind.operations@gmail.com

# For development (no emails sent):
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# ===========================================
# PAYMENT GATEWAYS
# ===========================================

# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret_key
RAZORPAY_WEBHOOK_SECRET=whsec_your_webhook_secret
RAZORPAY_CURRENCY=USD

# Stripe Configuration (Optional)
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret

# ===========================================
# JWT CONFIGURATION (Optional - has defaults)
# ===========================================
JWT_ACCESS_TOKEN_LIFETIME=30  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)
```

**Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833). See `EMAIL_SETUP.md` for detailed instructions.

---

## 📚 API Documentation

The API is fully documented using Swagger/OpenAPI 3.0 with comprehensive descriptions for every endpoint explaining what each API does, when to use it, and why it's needed.

### Documentation Resources

1. **Comprehensive API Guide**: [API_DOCUMENTATION_GUIDE.md](help_docs/API_DOCUMENTATION_GUIDE.md)
   - Detailed explanation of every API endpoint
   - What each API does and when to use it
   - Request/response examples for all major endpoints
   - Common workflows and integration patterns
   - Status codes and error handling

2. **Client Forms API**: [CLIENT_FORMS_API.md](help_docs/CLIENT_FORMS_API.md)
   - Client Intake Sheet API details
   - Credential Sheet API details
   - Field validations and constraints
   - Email notifications

3. **Field Validations**: [CLIENT_FORMS_API_FIELD_VALIDATIONS.md](help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md)
   - Complete field validation rules
   - Choice/enum values for all fields
   - Security practices and password handling
   - Data constraints and business rules

### Access Interactive API Documentation
- **Swagger UI**: http://127.0.0.1:8000/swagger/ (interactive - test APIs directly)
- **ReDoc**: http://127.0.0.1:8000/redoc/ (read-only - clean documentation view)
- **JSON Schema**: http://127.0.0.1:8000/swagger.json (for code generation)

### Understanding API Endpoints

Each Swagger endpoint includes:
- **Operation Summary**: What the API does in 1 sentence
- **Operation Description**: When/why to use it and what it accomplishes
- **Request Body**: Example input with field descriptions
- **Response**: Example output with status codes
- **Permissions**: Who can access (public, authenticated, admin, etc.)

**Example**: The `/api/users/client-intake/` endpoint shows:
```
Summary: Create client intake sheet
Description: Create a new client intake sheet for the authenticated user. 
Only one form per user. If form exists, returns 409 with update URL.
Purpose: Collect comprehensive candidate information for recruiter matching.
```

### Using Swagger UI

#### 1. **Test Public Endpoints** (No Authentication)
```
GET /api/users/register/         → Register new account
GET /api/users/login/             → Login with email/password
GET /api/users/interest/          → Submit interest form
GET /api/users/contact/           → Submit contact form
```
- No "Authorize" needed for these endpoints
- Click endpoint → "Try it out" → "Execute"

#### 2. **Test Protected Endpoints** (Authentication Required)
1. Navigate to http://127.0.0.1:8000/swagger/
2. Find and click **POST `/api/users/login/`**
3. Click "Try it out"
4. Enter email and password
5. Click "Execute"
6. Copy the `access` token from response
7. Click **🔓 Authorize** button (top right)
8. Paste token as: `Bearer <your_access_token>`
9. Click "Authorize" → "Close"
10. Now test any protected endpoint

#### 3. **Test Admin Endpoints**
- Login with admin account via **POST `/api/users/admin/login/`**
- Use admin token in Authorization
- Access admin-only endpoints like:
  - PATCH `/api/users/admin/candidates/<id>/activate/`
  - PATCH `/api/users/admin/candidates/<id>/deactivate/`

#### 4. **Test File Uploads**
- Endpoints like POST `/api/users/client-intake/` accept file uploads
- In Swagger, click "Choose File" for FileField parameters
- Select resume.pdf, passport.jpg, etc.
- Submit with other form fields

### Example API Calls

#### Register a New User
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-1234"
  }'
```

#### Login and Get Token
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

#### Submit Client Intake Form
```bash
curl -X POST http://localhost:8000/api/users/client-intake/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-05-15",
    "phone_number": "+1-555-1234",
    "email": "john@example.com",
    "current_address": "123 Main St, New York, NY",
    "mailing_address": "123 Main St, New York, NY",
    "visa_status": "F1-OPT",
    "first_entry_us": "2020-01-15",
    "total_years_in_us": 4,
    "skilled_in": "Python, Java, SQL",
    "experienced_with": "AWS, Docker, Git"
  }'
```

#### Check Form Completion Status
```bash
curl -X GET http://localhost:8000/api/users/forms-completion-status/ \
  -H "Authorization: Bearer <access_token>"
```

### API Endpoint Summary
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

## � Complete API Endpoints by Role

> **📖 For full documentation with examples, see [API_ENDPOINTS_COMPLETE.md](./API_ENDPOINTS_COMPLETE.md)**

### 🌍 Public Endpoints (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/users/register/` | Register new candidate |
| `POST` | `/api/users/login/` | Client/Candidate login |
| `POST` | `/api/users/interest/` | Submit interest form |
| `POST` | `/api/users/contact/` | Contact form submission |
| `POST` | `/api/users/password-reset/request/` | Request password reset |
| `POST` | `/api/users/password-reset/confirm/` | Confirm password reset |
| `GET` | `/api/jobs/` | List all job postings |
| `GET` | `/api/jobs/{id}/` | Get job details |

### 👤 Client/Candidate Endpoints (Auth Required)

| Method | Endpoint | Description | ID Type |
|--------|----------|-------------|---------|
| `GET` | `/api/users/me/` | Get my profile | - |
| `GET/PATCH/DELETE` | `/api/users/profiles/{id}/` | Manage profile | UUID |
| `GET/POST` | `/api/users/me/client-intake/` | My client intake form | - |
| `GET/POST` | `/api/users/me/credential-sheet/` | My credential sheet | - |
| `GET` | `/api/users/forms-completion-status/` | Check form completion | - |
| `POST` | `/api/users/password-change/` | Change password | - |
| `GET` | `/api/jobs/suggestions/` | My role suggestions | - |
| `PATCH` | `/api/jobs/suggestions/{id}/toggle/` | Toggle suggestion selection | Integer |
| `POST` | `/api/jobs/suggestions/submit/` | Submit selected suggestions | - |
| `GET` | `/api/payments/` | My payment history | - |
| `POST` | `/api/payments/razorpay/create-order/` | Create payment order | - |
| `POST` | `/api/payments/razorpay/verify/` | Verify payment | - |
| `GET` | `/api/subscriptions/my-subscriptions/` | My subscriptions | - |
| `GET` | `/api/subscriptions/billing-history/` | My billing history | - |
| `GET` | `/api/onboarding/` | My onboarding workflow | - |
| `PATCH` | `/api/onboarding/{id}/` | Update workflow step | Integer |

### 💼 Recruiter Endpoints (Recruiter Auth Required)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/api/recruiters/register/` | Register as recruiter | Public |
| `POST` | `/api/recruiters/login/` | Recruiter login | Public |
| `GET` | `/api/recruiters/me/` | Get my recruiter profile | Recruiter |
| `PATCH` | `/api/recruiters/me/` | Update my profile | Recruiter |
| `GET` | `/api/recruiters/dashboard/` | Recruiter dashboard with stats | Recruiter |
| `POST` | `/api/jobs/` | Create job posting | Recruiter |
| `PATCH` | `/api/jobs/{id}/` | Update job posting | Recruiter |
| `DELETE` | `/api/jobs/{id}/` | Delete job posting | Recruiter |

**Recruiter Web Portal (HTML):**
- `GET/POST` `/recruiter-registration/` - Registration form
- `GET/POST` `/recruiter-registration/login/` - Login page
- `GET` `/recruiter-registration/dashboard/` - Dashboard
- `GET/POST` `/recruiter-registration/profile/` - Profile management
- `GET/POST` `/recruiter-registration/complete-profile/` - Complete profile

### 🔧 Admin Endpoints (Admin Auth Required)

#### User Management
| Method | Endpoint | Description | ID Type |
|--------|----------|-------------|---------|
| `GET` | `/api/users/` | List all users | - |
| `GET` | `/api/users/clients/` | List only clients | - |
| `GET` | `/api/users/profiles/` | List all profiles | - |
| `GET` | `/api/users/clients/profiles/` | List client profiles | - |
| `GET` | `/api/users/profiles/{profile_id}/client-intake/` | Get intake by profile | UUID |
| `GET` | `/api/users/profiles/{profile_id}/credential-sheet/` | Get credentials by profile | UUID |
| `GET` | `/api/users/profiles/{profile_id}/role-suggestions/` | Get role suggestions | UUID |

#### Candidate Status Management
| Method | Endpoint | Description | Status Change |
|--------|----------|-------------|---------------|
| `POST` | `/api/users/admin/candidates/{id}/activate/` | Activate candidate | open → approved |
| `POST` | `/api/users/admin/candidates/{id}/deactivate/` | Deactivate candidate | any → rejected |
| `POST` | `/api/users/admin/candidates/{id}/placed/` | Mark as placed | assigned → closed |

#### Recruiter Management
| Method | Endpoint | Description | ID Type |
|--------|----------|-------------|---------|
| `GET` | `/api/recruiters/` | List all recruiters | - |
| `GET` | `/api/recruiters/{id}/` | Get recruiter details | UUID |
| `PATCH` | `/api/recruiters/{id}/` | Update recruiter | UUID |
| `POST` | `/api/recruiters/{id}/activate/` | Activate recruiter | UUID |
| `POST` | `/api/recruiters/{id}/deactivate/` | Deactivate recruiter | UUID |
| `POST` | `/api/recruiters/assign/` | Assign candidate to recruiter | - |

#### Admin Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/admin/profile/` | Get admin profile |
| `POST` | `/api/users/admin/register/` | Register new admin |
| `POST` | `/api/users/admin/password/` | Change admin password |

#### Subscription & Payment Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/subscriptions/admin/subscriptions/` | All subscriptions |
| `GET` | `/api/subscriptions/admin/billing-history/` | All billing records |
| `POST` | `/api/subscriptions/plans/` | Create subscription plan |
| `GET` | `/api/payments/invoices/` | All invoices |
| `POST` | `/api/payments/invoices/` | Create invoice |

#### Role Suggestions Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/jobs/suggestions/bulk_create/` | Bulk create suggestions for user |

### 📊 Summary by Module

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Authentication** | 4 | Login for clients, admins, recruiters + token refresh |
| **Users & Profiles** | 15 | Registration, profile CRUD, password management |
| **Client Forms** | 8 | Intake sheets, credentials, completion status |
| **Admin Management** | 10 | Candidate approvals, status changes, analytics |
| **Recruiters** | 12 | Registration, dashboard, assignments, portal |
| **Jobs** | 5 | Job postings CRUD, public listings |
| **Role Suggestions** | 8 | AI-powered role matching for candidates |
| **Payments** | 6 | Razorpay integration, orders, verification |
| **Invoices** | 5 | Invoice management and tracking |
| **Subscriptions** | 12 | Plans, user subscriptions, billing history |
| **Onboarding** | 4 | Workflow tracking, progress updates |
| **Public** | 3 | Contact and interest forms |
| **Total** | **92** | Complete API coverage |

### 🔑 ID Parameter Reference

| Parameter | Type | Usage | Example |
|-----------|------|-------|---------|
| `id` | UUID | Profile ID (users, candidates, recruiters) | `550e8400-e29b-41d4-a716-446655440000` |
| `profile_id` | UUID | Explicitly profile-scoped operations | `550e8400-e29b-41d4-a716-446655440000` |
| `pk` | Integer | Auto-increment IDs (jobs, onboarding) | `123` |

**Note:** All user/candidate operations consistently use UUID-based profile IDs for security.

---

## �👥 Recruiter System

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

## 📋 Client Forms APIs (Onboarding Forms)

### Overview

The Client Forms system provides two comprehensive forms for user onboarding:

1. **Client Intake Sheet** - Collects personal, professional, and educational information
2. **Credential Sheet** - Stores job platform credentials and job preferences

Both forms are integrated into the `users` app and support:
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ One form per user (OneToOne relationship with Profile)
- ✅ Email notifications upon submission
- ✅ Password masking for security
- ✅ File uploads for documents and credentials
- ✅ Form locking mechanism (edit control)
- ✅ Completion status tracking

### Why These APIs?

These APIs enable:
1. **Comprehensive Candidate Data Collection** - Beyond basic registration, collect detailed skills, experience, and preferences
2. **Secure Credential Storage** - Safely store job platform credentials without exposing them
3. **Compliance & Verification** - Collect necessary documents (passport, visa, work authorization, resume)
4. **Job Matching** - Use stored preferences and skills for intelligent job matching
5. **Audit Trail** - Track submission timestamps and edit history
6. **Progress Tracking** - Know when candidates have completed all required onboarding

### Client Intake Sheet API

**Purpose**: Collect comprehensive candidate information including skills, experience, education, and documents.

#### POST /api/users/client-intake/
Create a new client intake sheet.

**Authentication**: Required (JWT token)

**Why**: Initial form submission to collect candidate details. Only one form per user. If user already has a form, returns 409 Conflict with URL to update existing form.

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15",
  "phone_number": "+1-555-1234",
  "email": "john@example.com",
  "current_address": "123 Main St, New York, NY",
  "mailing_address": "123 Main St, New York, NY",
  "visa_status": "F1-OPT",
  "first_entry_us": "2020-01-15",
  "total_years_in_us": 4,
  "skilled_in": "Python, Java, SQL, React",
  "experienced_with": "AWS, Docker, Git, CI/CD",
  "desired_job_role": "Senior Software Engineer"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Client intake sheet submitted successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "submission_timestamp": "2024-01-15T10:30:00Z",
    "is_editable": true,
    "form_submitted_date": "2024-01-15T10:30:00Z"
  }
}
```

**Success Email**: Confirmation email sent to candidate with form summary.

**Error Cases**:
- `400 Bad Request`: Missing required fields or invalid data
- `401 Unauthorized`: No authentication token provided
- `409 Conflict`: Form already exists - use PATCH to update

#### GET /api/users/client-intake/{id}/
Retrieve existing client intake sheet.

**Authentication**: Required (owner or admin)

**Why**: View previously submitted form details. Used by candidates to review their submission or by admin to verify information.

**Response** (200 OK): Complete form data with all submitted fields

**Error Cases**:
- `401 Unauthorized`: No authentication token
- `403 Forbidden`: User doesn't own the form (and not admin)
- `404 Not Found`: Form doesn't exist

#### PATCH /api/users/client-intake/{id}/
Update (partially) an existing client intake sheet.

**Authentication**: Required (owner or admin)

**Why**: Allow candidates to modify their information after submission. Useful for updating phone numbers, skills, or other details. Admin can bypass edit restrictions.

**Request Body** (example - any fields can be updated):
```json
{
  "phone_number": "+1-555-5678",
  "visa_status": "H1B",
  "skilled_in": "Python, Java, SQL, React, Go"
}
```

**Response** (200 OK): Updated form data

**Edit Restrictions**:
- Candidates can only edit if `is_editable=true`
- Admins can always edit regardless of `is_editable`
- Can be locked after HR review

#### PUT /api/users/client-intake/{id}/
Full update of client intake sheet (replace all fields).

**Authentication**: Required (owner or admin)

**Why**: Less common than PATCH but used when replacing entire form (admin operations).

---

### Credential Sheet API

**Purpose**: Store job platform login credentials and job search preferences securely.

#### POST /api/users/credential-sheet/
Create a new credential sheet with platform credentials.

**Authentication**: Required (JWT token)

**Why**: Second required form in onboarding flow. Stores credentials for 11+ job platforms. Passwords are masked in responses for security.

**Request Body**:
```json
{
  "full_name": "John Doe",
  "personal_email": "john.personal@example.com",
  "phone_number": "+1-555-1234",
  "location": "New York, NY",
  "bachelor_graduation_date": "2020-05-15",
  "first_entry_us": "2020-01-15",
  "preferred_job_roles": "Software Engineer, Senior Developer",
  "preferred_locations": "New York, San Francisco, Remote",
  "linkedin_username": "johndoe",
  "linkedin_password": "my_secure_password",
  "indeed_username": "johndoe@gmail.com",
  "indeed_password": "another_password"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Credential sheet submitted successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "full_name": "John Doe",
    "personal_email": "john.personal@example.com",
    "linkedin_username": "johndoe",
    "linkedin_password": "••••••",
    "submission_timestamp": "2024-01-15T11:00:00Z",
    "is_editable": true
  }
}
```

**Security**: Passwords masked as "••••••" in all API responses (stored securely in database)

**Success Email**: Confirmation email sent with security notice (credentials NOT included in email)

**Error Cases**:
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: No authentication token
- `409 Conflict`: Credential sheet already exists

#### GET /api/users/credential-sheet/{id}/
Retrieve existing credential sheet.

**Authentication**: Required (owner or admin)

**Why**: View stored credentials for updating or verification.

**Important**: All passwords returned as "••••••" for security

**Response** (200 OK): Form data with masked passwords

#### PATCH /api/users/credential-sheet/{id}/
Update credential sheet (partially).

**Authentication**: Required (owner or admin)

**Why**: Update job preferences, locations, or platform credentials.

**Request Body** (example):
```json
{
  "preferred_job_roles": "Senior Engineer, Tech Lead",
  "linkedin_password": "new_password"
}
```

**Response** (200 OK): Updated data with masked passwords

#### PUT /api/users/credential-sheet/{id}/
Full update of credential sheet.

**Authentication**: Required (owner or admin)

---

### Forms Completion Status API

#### GET /api/users/forms-completion-status/
Check if user has completed both required forms.

**Authentication**: Required

**Why**: Frontend can use this to:
- Show progress to users (which forms are done)
- Gate access to job matching features
- Redirect incomplete users to form pages
- Display completion percentage

**Response** (200 OK):
```json
{
  "client_intake_completed": true,
  "credential_sheet_completed": true,
  "all_forms_completed": true,
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "forms": {
    "client_intake": {
      "completed": true,
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "submitted_at": "2024-01-15T10:30:00Z",
      "editable": true
    },
    "credential_sheet": {
      "completed": true,
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "submitted_at": "2024-01-15T11:00:00Z",
      "editable": true
    }
  }
}
```

---

### Field Validations & Choices

For complete field validation rules, choices, and security considerations, see:
- **`help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md`** - Detailed field documentation
- **`help_docs/CLIENT_FORMS_API.md`** - Complete API reference with examples

### Key Choices

**Visa Status**: F1-OPT, H1B, H4 EAD, Green Card, US Citizen, Other

**Job Type**: Full-time, Part-time, Internship

**Degree**: Bachelor's, Master's, PhD, Diploma, Other

**OPT Offer Letter Submitted**: Yes, No

### Security Features

- ✅ **Password Masking**: All passwords masked in API responses
- ✅ **Authentication Required**: All endpoints require JWT token
- ✅ **Authorization**: Users can only access their own forms (admins can access all)
- ✅ **Edit Control**: Forms can be locked after HR review
- ✅ **OneToOne Relationship**: Only one form per user
- ✅ **Timestamps**: Submission and edit tracking for audit

### Email Notifications

**Client Intake Sheet Email**:
- Subject: ✅ Client Intake Form - Submission Confirmed
- Contains: Form summary, link to edit
- Sent to: Candidate's email

**Credential Sheet Email**:
- Subject: ✅ Credential Sheet - Submission Confirmed
- Contains: Form summary, security notice
- **Does NOT include**: Passwords (for security)
- Sent to: Candidate's email

### Testing Client Forms APIs

#### Using Swagger UI
1. Go to http://127.0.0.1:8000/swagger/
2. Login via `/api/users/login/` to get token
3. Authorize with token
4. Test each endpoint under "Client Forms" section

#### Using curl
```bash
# Create intake sheet
curl -X POST http://127.0.0.1:8000/api/users/client-intake/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-05-15",
    "phone_number": "+1-555-1234",
    "email": "john@example.com",
    "current_address": "123 Main St",
    "mailing_address": "123 Main St",
    "visa_status": "F1-OPT",
    "first_entry_us": "2020-01-15",
    "total_years_in_us": 4,
    "skilled_in": "Python",
    "experienced_with": "AWS"
  }'

# Check completion status
curl -X GET http://127.0.0.1:8000/api/users/forms-completion-status/ \
  -H "Authorization: Bearer <token>"
```

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