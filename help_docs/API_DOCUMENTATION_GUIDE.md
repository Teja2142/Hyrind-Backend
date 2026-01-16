# 🌐 Hyrind API Documentation Guide

## Overview

This guide provides a comprehensive overview of all APIs available in the Hyrind platform. All APIs follow industry-standard REST conventions with clear naming, proper HTTP methods, and semantic status codes.

---

## 📋 API Architecture

### Base URL
```
http://localhost:8000/api
```

### Authentication
- **Type**: JWT (JSON Web Tokens)
- **Location**: `Authorization: Bearer <access_token>`
- **Endpoints**: `/api/users/login/` (client), `/api/users/admin/login/` (admin), `/api/recruiters/login/` (recruiter)

### Response Format
All APIs return JSON with consistent structure:

```json
{
    "success": true,
    "data": {},
    "message": "Success message",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 👥 User Management APIs

### Purpose
Manage user accounts, profiles, and authentication for candidates, recruiters, and admins.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/users/register/` | POST | Register new candidate account | No | Profile UUID + JWT tokens |
| `/users/login/` | POST | Login with email/password | No | JWT access/refresh tokens |
| `/users/me/` | GET | Get current logged-in user profile | Yes | Full profile details |
| `/users/profiles/` | GET | List all profiles (admin only) | Yes (Admin) | Array of profiles |
| `/users/profiles/<id>/` | GET/PATCH/DELETE | Manage specific profile | Yes | Profile details |
| `/users/clients/` | GET | List only client profiles | Yes (Admin) | Array of client profiles |
| `/users/clients/profiles/` | GET | List all client profiles | Yes (Admin) | Array of client profiles |

### What Each API Does

#### POST `/users/register/`
**Purpose**: Create a new candidate user account and profile  
**When to use**: First step for new candidates joining platform  
**Request**:
```json
{
    "email": "john@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-1234"
}
```
**Response** (201 Created):
```json
{
    "success": true,
    "profile_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "tokens": {
        "access": "eyJ...",
        "refresh": "eyJ..."
    }
}
```

#### POST `/users/login/`
**Purpose**: Authenticate user and obtain JWT tokens  
**When to use**: Every time user needs to access protected resources  
**Request**:
```json
{
    "email": "john@example.com",
    "password": "secure_password"
}
```
**Response** (200 OK):
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```
**Why**: Tokens provide stateless authentication for every request

#### GET `/users/me/`
**Purpose**: Get current authenticated user's profile  
**When to use**: Frontend needs to load user dashboard or verify login  
**Response** (200 OK):
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-1234",
    "status": "approved",
    "active": true
}
```
**Why**: Single source of truth for current user data

---

## 🔐 Client Forms APIs

### Purpose
Collect comprehensive candidate information through structured onboarding forms with built-in validation and email notifications.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/users/client-intake/` | POST | Submit client intake sheet | Yes | Form ID + confirmation |
| `/users/client-intake/<id>/` | GET/PATCH | View/update intake form | Yes | Form data |
| `/users/credential-sheet/` | POST | Submit credential sheet | Yes | Form ID + confirmation |
| `/users/credential-sheet/<id>/` | GET/PATCH | View/update credentials | Yes | Form data (passwords masked) |
| `/users/forms-completion-status/` | GET | Check form completion | Yes | Status of both forms |

### What Each API Does

#### POST `/users/client-intake/`
**Purpose**: Submit comprehensive candidate intake form  
**When to use**: Candidate's first onboarding step after registration  
**What it collects**:
- Personal info (name, DOB, contact, address)
- Visa/immigration status
- Technical & non-technical skills
- Work experience (up to 3 jobs)
- Education & certifications
- Document uploads (passport, resume, visa, etc.)
- Job preferences

**Why this matters**: Intake form provides complete candidate profile for recruiter matching  
**Automation**: Auto-sends confirmation email with submitted data

#### GET `/users/forms-completion-status/`
**Purpose**: Check if candidate has completed required onboarding  
**When to use**: Frontend gates job matching features behind form completion  
**Response** (200 OK):
```json
{
    "client_intake_completed": true,
    "credential_sheet_completed": false,
    "all_forms_completed": false,
    "profile_id": "550e8400-e29b-41d4-a716-446655440000",
    "forms": {
        "client_intake": {
            "completed": true,
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "submitted_at": "2024-01-15T10:30:00Z",
            "editable": true
        },
        "credential_sheet": {
            "completed": false
        }
    }
}
```
**Why**: Single endpoint to determine onboarding progress

---

## 🏢 Recruiter APIs

### Purpose
Manage recruiter accounts, assignments, and dashboard operations.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/recruiters/register/` | POST | Register recruiter account | No | Employee ID + tokens |
| `/recruiters/login/` | POST | Login recruiter | No | JWT tokens |
| `/recruiters/me/` | GET | Get recruiter profile | Yes | Recruiter details |
| `/recruiters/dashboard/` | GET | Get recruiter dashboard data | Yes | Stats, assignments, clients |
| `/recruiters/` | GET | List all recruiters (admin) | Yes (Admin) | Array of recruiters |
| `/recruiters/<id>/` | GET/PATCH | Manage recruiter | Yes (Admin) | Recruiter details |
| `/recruiters/<id>/activate/` | PATCH | Activate recruiter | Yes (Admin) | Updated recruiter |
| `/recruiters/<id>/deactivate/` | PATCH | Deactivate recruiter | Yes (Admin) | Updated recruiter |
| `/recruiters/assign/` | POST | Assign client to recruiter | Yes (Admin) | Assignment confirmation |

### What Each API Does

#### GET `/recruiters/dashboard/`
**Purpose**: Get recruiter's personal dashboard with stats  
**When to use**: Recruiter logs in and views dashboard  
**Response** (200 OK):
```json
{
    "recruiter": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Jane Smith",
        "department": "US-IT-HIRING"
    },
    "stats": {
        "total_assigned": 15,
        "completed": 8,
        "in_progress": 7
    },
    "assigned_clients": [
        {
            "id": "client_uuid",
            "name": "John Doe",
            "status": "assigned",
            "assigned_date": "2024-01-10T15:30:00Z"
        }
    ]
}
```
**Why**: Dashboard provides quick overview of recruiter's workload

---

## 💼 Job Posting APIs

### Purpose
Create, manage, and list job opportunities available to candidates.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/jobs/` | GET | List all job postings | Yes | Array of jobs |
| `/jobs/` | POST | Create job posting | Yes (Recruiter/Admin) | Job ID + details |
| `/jobs/<id>/` | GET | Get job details | Yes | Complete job info |
| `/jobs/<id>/` | PATCH | Update job posting | Yes (Owner/Admin) | Updated job |
| `/jobs/<id>/` | DELETE | Delete job posting | Yes (Admin) | Confirmation |

### What Each API Does

#### GET `/jobs/`
**Purpose**: Browse available job opportunities  
**When to use**: Candidate searching for jobs or recruiter viewing postings  
**Query Parameters**:
- `search`: Search by job title or company
- `page`: Pagination (10 per page by default)

**Response** (200 OK):
```json
{
    "count": 45,
    "next": "http://api/jobs/?page=2",
    "results": [
        {
            "id": 1,
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "description": "...",
            "salary_min": 100000,
            "salary_max": 150000,
            "location": "San Francisco, CA",
            "posted_date": "2024-01-15T10:30:00Z"
        }
    ]
}
```
**Why**: Enables job discovery without authentication for public listings

#### POST `/jobs/`
**Purpose**: Post new job opening  
**When to use**: Recruiter publishes new position  
**What it collects**:
- Job title & description
- Required skills & experience
- Salary range
- Location
- Application deadline

**Automation**: Job becomes searchable immediately, notifications sent to matching candidates

---

## 💳 Payment APIs

### Purpose
Handle payment processing and subscription management.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/payments/` | GET | List payment history | Yes | Array of payments |
| `/payments/` | POST | Create payment | Yes | Payment ID |
| `/payments/razorpay/create-order/` | POST | Create Razorpay order | Yes | Order details |
| `/payments/razorpay/verify/` | POST | Verify payment | Yes | Verification result |
| `/payments/razorpay/webhook/` | POST | Payment webhook | No | Confirmation |

### What Each API Does

#### POST `/payments/razorpay/create-order/`
**Purpose**: Initiate payment for candidate registration fee  
**When to use**: Candidate clicks "Pay Now" after approval  
**Request**:
```json
{
    "amount": 4900,
    "currency": "INR",
    "description": "Hyrind Registration Fee"
}
```
**Response** (201 Created):
```json
{
    "order_id": "order_1234567890",
    "amount": 4900,
    "currency": "INR",
    "created_at": "2024-01-15T10:30:00Z"
}
```
**Why**: Razorpay integration enables secure payment processing

#### POST `/payments/razorpay/verify/`
**Purpose**: Verify successful payment  
**When to use**: After candidate completes payment in Razorpay gateway  
**Request**:
```json
{
    "razorpay_order_id": "order_1234567890",
    "razorpay_payment_id": "pay_1234567890",
    "razorpay_signature": "signature_string"
}
```
**Response** (200 OK):
```json
{
    "success": true,
    "message": "Payment verified",
    "profile_status": "ready_to_assign"
}
```
**Why**: Confirms payment and advances candidate to recruiter assignment stage

---

## 📚 Subscription APIs

### Purpose
Manage subscription plans and billing for candidates and recruiters.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/subscriptions/plans/` | GET | List subscription plans | Yes | Array of plans |
| `/subscriptions/my-subscriptions/` | GET | List user subscriptions | Yes | User's subscriptions |
| `/subscriptions/billing-history/` | GET | View billing history | Yes | Array of invoices |
| `/subscriptions/admin/subscriptions/` | GET | List all subscriptions (admin) | Yes (Admin) | All subscriptions |

### What Each API Does

#### GET `/subscriptions/plans/`
**Purpose**: View available subscription tiers  
**When to use**: User decides which plan to purchase  
**Response** (200 OK):
```json
{
    "results": [
        {
            "id": "plan_basic_001",
            "name": "Basic",
            "description": "Access to job listings",
            "price": 0,
            "billing_cycle": "monthly",
            "features": ["Job search", "Apply to jobs", "1 active profile"]
        },
        {
            "id": "plan_pro_001",
            "name": "Pro",
            "description": "Enhanced job matching",
            "price": 99,
            "billing_cycle": "monthly",
            "features": ["Advanced filtering", "Profile boosting", "Recruiter messages"]
        }
    ]
}
```
**Why**: Transparency in pricing and features

---

## 🎯 Onboarding APIs

### Purpose
Guide users through multi-step onboarding workflows.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/onboarding/` | GET | List onboarding workflows | Yes | Array of workflows |
| `/onboarding/` | POST | Create onboarding workflow | Yes | Workflow ID |
| `/onboarding/<id>/` | GET | Get workflow details | Yes | Workflow data |
| `/onboarding/<id>/` | PATCH | Mark step complete | Yes | Updated workflow |

### What Each API Does

#### POST `/onboarding/`
**Purpose**: Initialize structured onboarding process  
**When to use**: New candidate signs up  
**What it creates**:
- Multi-step workflow
- Progress tracking
- Automatic reminders
- Completion status

**Workflow steps**:
1. Complete profile
2. Submit intake form
3. Submit credential sheet
4. Payment
5. Assignment to recruiter

#### PATCH `/onboarding/<id>/`
**Purpose**: Mark onboarding step as complete  
**When to use**: Candidate completes step (form submission, payment, etc.)  
**Request**:
```json
{
    "step": "submit_intake_form"
}
```
**Response** (200 OK):
```json
{
    "id": "workflow_uuid",
    "steps_completed": ["complete_profile", "submit_intake_form"],
    "progress_percentage": 40,
    "current_step": "submit_credential_sheet"
}
```
**Why**: Tracks onboarding progress and sends reminders for incomplete steps

---

## 🔒 Admin APIs

### Purpose
Administrative functions for managing candidates, recruiters, and platform settings.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/users/admin/profile/` | GET | Get admin profile | Yes (Admin) | Admin details |
| `/users/admin/register/` | POST | Register new admin | Yes (Admin) | Admin ID + tokens |
| `/users/admin/password/` | POST | Change admin password | Yes (Admin) | Confirmation |
| `/users/admin/candidates/<id>/activate/` | PATCH | Activate candidate | Yes (Admin) | Updated profile |
| `/users/admin/candidates/<id>/deactivate/` | PATCH | Deactivate candidate | Yes (Admin) | Updated profile |
| `/users/admin/candidates/<id>/placed/` | PATCH | Mark candidate placed | Yes (Admin) | Updated profile |

### What Each API Does

#### PATCH `/users/admin/candidates/<id>/activate/`
**Purpose**: Approve candidate registration  
**When to use**: Admin reviews submitted application and approves  
**Effect**:
- Status changes: `open` → `approved`
- User can now login
- Email sent to candidate
- Candidate can proceed to payment

**Request**: (usually empty body, or with notes)
```json
{
    "status_notes": "All documents verified"
}
```

#### PATCH `/users/admin/candidates/<id>/placed/`
**Purpose**: Mark candidate as successfully placed  
**When to use**: Job successfully completed and candidate hired  
**Effect**:
- Status changes: `assigned` → `closed`
- Recruiter assignment ends
- Confirmation email sent
- Candidate profile marked as inactive

---

## 🔑 Password Management APIs

### Purpose
Handle password reset and change requests securely.

| Endpoint | Method | Purpose | Auth | Returns |
|----------|--------|---------|------|---------|
| `/users/password-reset/request/` | POST | Request password reset | No | Confirmation |
| `/users/password-reset/confirm/` | POST | Reset with token | No | Confirmation |
| `/users/password-change/` | POST | Change password | Yes | Confirmation |
| `/users/admin/password/` | POST | Admin password change | Yes (Admin) | Confirmation |

### What Each API Does

#### POST `/users/password-reset/request/`
**Purpose**: Initiate password reset process  
**When to use**: User clicks "Forgot Password"  
**Request**:
```json
{
    "email": "john@example.com"
}
```
**Response** (200 OK):
```json
{
    "success": true,
    "message": "Password reset link sent to email"
}
```
**Why**: Secure way to regain access without emergency support

#### POST `/users/password-reset/confirm/`
**Purpose**: Complete password reset with token from email  
**When to use**: User receives email and clicks reset link  
**Request**:
```json
{
    "token": "reset_token_from_email",
    "new_password": "new_secure_password"
}
```
**Response** (200 OK):
```json
{
    "success": true,
    "message": "Password reset successfully"
}
```
**Why**: Token-based reset prevents unauthorized password changes

---

## 📊 Status Codes Guide

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PATCH request |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (e.g., intake form) |
| 500 | Server Error | Internal server error |

---

## 🔄 Common Workflows

### Candidate Registration to Job Placement

```
1. POST /api/users/register/
   → User account created, JWT obtained
   
2. POST /api/users/client-intake/
   → Intake form submitted, email confirmation sent
   
3. POST /api/users/credential-sheet/
   → Credentials submitted, email confirmation sent
   
4. GET /api/users/forms-completion-status/
   → Verify both forms complete
   
5. POST /api/payments/razorpay/create-order/
   → Payment initiated
   
6. POST /api/payments/razorpay/verify/
   → Payment verified, status → ready_to_assign
   
7. [ADMIN] PATCH /api/users/admin/candidates/<id>/activate/
   → Candidate activated by admin
   
8. [RECRUITER] PATCH /api/recruiters/assign/
   → Candidate assigned to recruiter
   
9. GET /api/jobs/
   → Candidate browses job opportunities
   
10. [RECRUITER] PATCH /api/users/admin/candidates/<id>/placed/
    → Candidate marked as placed
```

---

## 🛠️ Testing APIs

### Using Swagger UI
1. Navigate to `http://localhost:8000/swagger/`
2. Click "Authorize" button
3. Login via `/api/users/login/`
4. Copy access token and paste in authorization
5. Test any endpoint interactively

### Using cURL
```bash
# Login and get token
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'

# Use token for protected request
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Using Postman
1. Create POST request to `/api/users/login/`
2. Copy `access` token from response
3. Add header: `Authorization: Bearer <token>`
4. Make protected requests

---

## 📞 Support & Questions

For API issues or questions:
- Check help_docs/ folder for specific API guides
- Review models.py for field validations
- Check serializers.py for request/response formats
- View example requests in help_docs/CLIENT_FORMS_API.md

---

Last Updated: January 16, 2026
