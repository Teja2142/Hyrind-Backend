# Hyrind Backend API Documentation

## Table of Contents
- [Authentication](#authentication)
- [User Management APIs](#user-management-apis)
- [Subscription Management APIs](#subscription-management-apis)
- [Client Forms APIs](#client-forms-apis)
- [Admin APIs](#admin-apis)
## Recruiter APIs](#recruiter-apis)
- [Payment APIs](#payment-apis)
- [Job Management APIs](#job-management-apis)
- [Onboarding APIs](#onboarding-apis)

---

## Authentication

All authenticated endpoints require a JWT Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Get Access Token
**Endpoint:** `POST /api/users/login/`  
**Permission:** Public  
**Description:** Client/candidate login to get JWT tokens

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Token Expiry:**
- Access Token: 60 minutes
- Refresh Token: Use `/api/token/refresh/` to get new access token

---

### Admin Login
**Endpoint:** `POST /api/users/admin/login/`  
**Permission:** Public (validates admin credentials)  
**Description:** Admin user login (staff/superuser only)

**Request Body:**
```json
{
  "username": "admin@example.com",
  "password": "adminPassword123"
}
```

**Response:** Same as client login

---

## User Management APIs

### 1. User Registration
**Endpoint:** `POST /api/users/register/`  
**Permission:** Public  
**Content-Type:** multipart/form-data  
**Description:** Register new client (job seeker) account

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1-234-567-8900",
  "password": "securePassword123",
  "password2": "securePassword123",
  "university": "Stanford University",
  "degree": "Master of Science",
  "major": "Computer Science",
  "graduation_date": "2024-05-15",
  "visa_status": "F1-OPT",
  "years_of_experience": 2,
  "linkedin_profile": "https://linkedin.com/in/johndoe",
  "resume": "<file>",
  "profile_picture": "<file>"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully. Please check your email for further instructions.",
  "profile_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Workflow:**
1. User registers → Status: `open`
2. Admin reviews application
3. Admin approves → Status: `approved`
4. User completes payment → Status: `ready_to_assign`
5. Admin assigns recruiter → Status: `assigned`

---

### 2. Get Current User Profile
**Endpoint:** `GET /api/users/me/`  
**Permission:** Authenticated  
**Description:** Get logged-in user's profile details

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user": {
    "id": 1,
    "username": "john@example.com",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-234-567-8900",
  "university": "Stanford University",
  "degree": "Master of Science",
  "major": "Computer Science",
  "registration_status": "approved",
  "active": true,
  "created_at": "2024-01-10T10:30:00Z"
}
```

---

### 3. List All Users (Admin)
**Endpoint:** `GET /api/users/`  
**Permission:** Admin only  
**Description:** List ALL users (clients, recruiters, admins)

**Query Parameters:**
- `active`: Filter by active status (true/false)
- `status`: Filter by registration status (open/approved/ready_to_assign/assigned/waiting_payment/closed/rejected)
- `search`: Search by email

**Example:**
```
GET /api/users/?active=true&status=approved
```

---

### 4. List Clients Only (Admin)
**Endpoint:** `GET /api/clients/`  
**Permission:** Admin only  
**Description:** List ONLY clients (excludes recruiters and admins)

**Query Parameters:**
- `active`: Filter by active status
- `status`: Filter by registration status
- `has_recruiter`: Filter by assigned recruiter (true/false)
- `search`: Search by name or email

**Example:**
```
GET /api/clients/?status=assigned&has_recruiter=true
```

---

### 5. Password Reset (Forgot Password)
**Step 1: Request Reset**  
**Endpoint:** `POST /api/users/password-reset/request/`  
**Permission:** Public

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "If an account exists with this email, you will receive password reset instructions."
}
```

**Step 2: Confirm Reset**  
**Endpoint:** `POST /api/users/password-reset/confirm/`  
**Permission:** Public

**Request Body:**
```json
{
  "uid": "MQ",
  "token": "abc123...",
  "new_password": "newPassword123",
  "confirm_password": "newPassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password has been reset successfully. You can now log in with your new password."
}
```

---

### 6. Change Password (Dashboard)
**Endpoint:** `POST /api/users/password-change/`  
**Permission:** Authenticated  
**Description:** Change password from user dashboard

**Request Body:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newPassword456",
  "confirm_password": "newPassword456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## Subscription Management APIs

### 1. List Subscription Plans
**Endpoint:** `GET /api/subscriptions/plans/`  
**Permission:** Public  
**Description:** Get all available subscription plans

**Query Parameters:**
- `plan_type`: Filter by type (base/addon)
- `is_active`: Filter active plans (true/false)

**Response (200 OK):**
```json
[
  {
    "id": "plan-uuid",
    "name": "Premium Plan",
    "description": "Full service package with dedicated recruiter",
    "price": 499.00,
    "billing_cycle": "monthly",
    "plan_type": "base",
    "features": {
      "recruiter_support": true,
      "resume_review": true,
      "interview_prep": true
    },
    "is_active": true
  }
]
```

---

### 2. List User Subscriptions
**Endpoint:** `GET /api/subscriptions/my-subscriptions/`  
**Permission:** Authenticated  
**Description:** Get logged-in user's subscriptions

**Query Parameters:**
- `status`: Filter by status (pending/active/cancelled/expired)
- `plan_type`: Filter by type (base/addon)

**Response (200 OK):**
```json
[
  {
    "id": "sub-uuid",
    "profile": {
      "id": "profile-uuid",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    },
    "plan": {
      "id": "plan-uuid",
      "name": "Premium Plan",
      "price": 499.00
    },
    "price": 499.00,
    "status": "active",
    "start_date": "2024-01-15T00:00:00Z",
    "next_billing_date": "2024-02-15T00:00:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### 3. Create Subscription
**Endpoint:** `POST /api/subscriptions/my-subscriptions/`  
**Permission:** Authenticated  
**Description:** Create new subscription for logged-in user

**Request Body:**
```json
{
  "plan": "plan-uuid"
}
```

**Response (201 Created):**
```json
{
  "id": "sub-uuid",
  "plan": { /* plan details */ },
  "price": 499.00,
  "status": "pending",
  "razorpay_order_id": "order_123abc",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Next Step:** Use `razorpay_order_id` to complete payment via Razorpay

---

### 4. Activate Subscription (After Payment)
**Endpoint:** `POST /api/subscriptions/my-subscriptions/{id}/activate/`  
**Permission:** Authenticated  
**Description:** Activate subscription after successful payment

**Request Body:**
```json
{
  "razorpay_payment_id": "pay_123abc",
  "razorpay_order_id": "order_123abc",
  "amount": 499.00
}
```

**Response (200 OK):**
```json
{
  "id": "sub-uuid",
  "status": "active",
  "start_date": "2024-01-15T10:30:00Z",
  "next_billing_date": "2024-02-15T00:00:00Z"
}
```

---

### 5. Cancel Subscription
**Endpoint:** `POST /api/subscriptions/my-subscriptions/{id}/cancel/`  
**Permission:** Authenticated  
**Description:** Cancel active subscription

**Response (200 OK):**
```json
{
  "message": "Subscription cancelled successfully",
  "id": "sub-uuid",
  "status": "cancelled"
}
```

---

### 6. Subscription Summary (Dashboard)
**Endpoint:** `GET /api/subscriptions/my-subscriptions/summary/`  
**Permission:** Authenticated  
**Description:** Get subscription summary for dashboard

**Response (200 OK):**
```json
{
  "total_subscriptions": 2,
  "active_subscriptions": 2,
  "monthly_cost": 599.00,
  "base_subscription": { /* base subscription details */ },
  "addons": [ /* addon subscriptions */ ],
  "next_billing_date": "2024-02-15T00:00:00Z",
  "next_billing_amount": 599.00,
  "total_spent_lifetime": 2396.00,
  "recent_transactions": [ /* last 5 transactions */ ]
}
```

---

### 7. Billing History
**Endpoint:** `GET /api/subscriptions/billing-history/`  
**Permission:** Authenticated  
**Description:** Get billing history for logged-in user

**Query Parameters:**
- `status`: Filter by status (pending/success/failed/refunded)
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

**Example:**
```
GET /api/subscriptions/billing-history/?status=success&start_date=2024-01-01
```

**Response (200 OK):**
```json
[
  {
    "id": "billing-uuid",
    "user_subscription": {
      "id": "sub-uuid",
      "plan": { "name": "Premium Plan" }
    },
    "amount": 499.00,
    "status": "success",
    "razorpay_payment_id": "pay_123abc",
    "description": "Payment for Premium Plan",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### 8. Billing Statistics
**Endpoint:** `GET /api/subscriptions/billing-history/statistics/`  
**Permission:** Authenticated  
**Description:** Get billing statistics for logged-in user

**Response (200 OK):**
```json
{
  "total_spent": {
    "lifetime": 2396.00,
    "this_year": 1496.00,
    "this_month": 599.00
  },
  "transactions": {
    "total_count": 8,
    "success_count": 7,
    "success_rate_percentage": 87.5,
    "average_amount": 299.50,
    "by_status": [
      {"status": "success", "count": 7, "total_amount": 2096.00},
      {"status": "failed", "count": 1, "total_amount": 300.00}
    ]
  }
}
```

---

## Client Forms APIs

### 1. Submit Client Intake Sheet
**Endpoint:** `POST /api/users/client-intake/`  
**Permission:** Authenticated  
**Content-Type:** multipart/form-data  
**Description:** Submit comprehensive client information form (one per user)

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15",
  "phone_number": "+1-555-1234",
  "email": "john@example.com",
  "alternate_email": "john.alt@example.com",
  "current_address": "123 Main St, New York, NY 10001",
  "mailing_address": "456 Oak Ave, Los Angeles, CA 90001",
  "visa_status": "F1-OPT",
  "first_entry_us": "2020-01-15",
  "total_years_in_us": 4,
  "skilled_in": "Python, Java, SQL, JavaScript",
  "experienced_with": "AWS, Docker, Git, Linux",
  "education_history": [ /* array of education entries */ ],
  "work_history": [ /* array of work entries */ ],
  "certifications": "AWS Solutions Architect, PMP"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Client intake sheet submitted successfully!",
  "data": {
    "id": "intake-uuid",
    "profile": "profile-uuid",
    "first_name": "John",
    "last_name": "Doe",
    "is_editable": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error (409 Conflict):**
```json
{
  "error": "Client intake sheet already exists for this profile",
  "existing_form_id": "intake-uuid"
}
```

---

### 2. Get/Update Client Intake Sheet
**Endpoint:** `GET /api/users/client-intake/{id}/`  
**Endpoint:** `PATCH /api/users/client-intake/{id}/`  
**Permission:** Authenticated (owner or admin)  
**Description:** Retrieve or update existing intake sheet

---

### 3. Submit Credential Sheet
**Endpoint:** `POST /api/users/credential-sheet/`  
**Permission:** Authenticated  
**Description:** Submit job platform credentials (one per user)

**Request Body:**
```json
{
  "dice_username": "john_doe",
  "dice_password": "password123",
  "monster_username": "johndoe@example.com",
  "monster_password": "password456",
  "indeed_username": "john.doe",
  "indeed_password": "password789",
  "linkedin_username": "johndoe",
  "linkedin_password": "password012",
  "other_platforms": "GitHub: johndoe, Stack Overflow: john_doe"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Credential sheet submitted successfully!",
  "data": {
    "id": "credential-uuid",
    "profile": "profile-uuid",
    "is_editable": true,
    "created_at": "2024-01-15T11:00:00Z"
  }
}
```

---

### 4. Check Forms Completion Status
**Endpoint:** `GET /api/users/forms-completion-status/`  
**Permission:** Authenticated  
**Description:** Check if user has completed both required forms

**Response (200 OK):**
```json
{
  "client_intake_completed": true,
  "credential_sheet_completed": false,
  "all_forms_completed": false,
  "profile_id": "profile-uuid",
  "forms": {
    "client_intake": {
      "completed": true,
      "id": "intake-uuid",
      "submitted_at": "2024-01-15T10:30:00Z",
      "editable": true
    },
    "credential_sheet": {
      "completed": false
    }
  },
  "message": "Please complete the Credential Sheet form to proceed."
}
```

---

## Admin APIs

### 1. Admin Subscription Management
**Endpoint:** `GET /api/subscriptions/admin/subscriptions/`  
**Permission:** Admin only  
**Description:** List all client subscriptions

**Query Parameters:**
- `profile_id`: Filter by user (UUID)
- `status`: Filter by status
- `plan_type`: Filter by plan type (base/addon)

**Example:**
```
GET /api/subscriptions/admin/subscriptions/?status=active&plan_type=base
```

---

### 2. Admin Billing History
**Endpoint:** `GET /api/subscriptions/admin/billing-history/`  
**Permission:** Admin only  
**Description:** View ALL billing records across all users

**Query Parameters:**
- `profile_id`: Filter by user
- `status`: Filter by status
- `start_date`: Filter from date
- `end_date`: Filter to date
- `min_amount`: Minimum amount
- `max_amount`: Maximum amount
- `search`: Search by user name/email

**Example:**
```
GET /api/subscriptions/admin/billing-history/?status=failed&start_date=2024-01-01
```

---

### 3. Subscription Analytics
**Endpoint:** `GET /api/subscriptions/admin/subscriptions/analytics/`  
**Permission:** Admin only  
**Description:** Get comprehensive subscription metrics

**Query Parameters:**
- `period`: today/week/month/year/all (default: month)

**Response (200 OK):**
```json
{
  "period": "month",
  "date_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "subscriptions": {
    "total_active": 150,
    "total_customers": 145,
    "by_plan": [
      {"plan__name": "Premium Plan", "count": 100, "total_revenue": 49900.00},
      {"plan__name": "Basic Plan", "count": 50, "total_revenue": 9950.00}
    ]
  },
  "revenue": {
    "mrr": 59850.00,
    "period_total": 75000.00,
    "previous_period": 68000.00,
    "growth_percentage": 10.29,
    "average_per_user": 517.24
  },
  "payments": {
    "failed_count": 8,
    "recent_failures": [ /* last 10 failed payments */ ]
  }
}
```

---

### 4. Approve Candidate
**Endpoint:** `POST /api/users/admin/candidates/{id}/activate/`  
**Permission:** Admin only  
**Description:** Approve candidate registration (open → approved)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Candidate approved successfully!",
  "data": {
    "id": "profile-uuid",
    "registration_status": "approved",
    "active": true
  }
}
```

---

### 5. Reject Candidate
**Endpoint:** `POST /api/users/admin/candidates/{id}/deactivate/`  
**Permission:** Admin only  
**Description:** Reject candidate registration

**Request Body:**
```json
{
  "reason": "Insufficient qualifications"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Candidate rejected",
  "data": {
    "id": "profile-uuid",
    "registration_status": "rejected",
    "active": false
  }
}
```

---

### 6. Mark Candidate as Placed
**Endpoint:** `POST /api/users/admin/candidates/{id}/placed/`  
**Permission:** Admin only  
**Description:** Mark candidate as successfully placed (assigned → closed)

**Request Body:**
```json
{
  "company_name": "Google Inc.",
  "position": "Senior Software Engineer",
  "notes": "Placed through direct referral"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Candidate marked as successfully placed!",
  "data": {
    "id": "profile-uuid",
    "registration_status": "closed"
  }
}
```

---

## Candidate Status Workflow

```
open (Initial registration)
  ↓ [Admin approves]
approved (Can login, needs payment)
  ↓ [User completes payment]
ready_to_assign (Paid, waiting for recruiter)
  ↓ [Admin assigns recruiter]
assigned (Working with recruiter)
  ↓ [Gets job offer]
closed (Successfully placed)

Alternative paths:
any → rejected (Admin rejects)
any → deactivated (Admin deactivates)
```

---

## Error Responses

All endpoints follow standard HTTP status codes:

- **200 OK:** Success
- **201 Created:** Resource created successfully
- **400 Bad Request:** Validation error
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **409 Conflict:** Resource already exists
- **500 Internal Server Error:** Server error

**Error Response Format:**
```json
{
  "error": "Detailed error message",
  "detail": "Additional context",
  "field_name": ["Field-specific validation errors"]
}
```

---

## Rate Limiting

- **Public endpoints:** 100 requests per hour per IP
- **Authenticated endpoints:** 1000 requests per hour per user
- **Admin endpoints:** Unlimited

---

## Pagination

List endpoints return paginated results:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

**Response Format:**
```json
{
  "count": 150,
  "next": "/api/users/clients/?page=2",
  "previous": null,
  "results": [ /* array of objects */ ]
}
```

---

## File Uploads

Endpoints accepting files use `multipart/form-data`:

**Accepted File Types:**
- **Resume:** PDF, DOC, DOCX (max 5MB)
- **Profile Picture:** JPG, PNG (max 2MB)

---

## Webhook Endpoints

### Payment Webhook
**Endpoint:** `POST /api/subscriptions/webhook/payment/`  
**Permission:** Public (no auth)  
**Description:** Called by frontend after Razorpay payment

**Request Body:**
```json
{
  "subscription_id": "sub-uuid",
  "razorpay_payment_id": "pay_123abc",
  "razorpay_order_id": "order_123abc",
  "amount": 499.00,
  "status": "success"
}
```

---

## Recruiter APIs

### 1. Recruiter Registration
**Endpoint:** `POST /api/recruiters/register/`  
**Permission:** Public  
**Content-Type:** multipart/form-data  
**Description:** Register new recruiter account (requires admin approval)

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@company.com",
  "phone": "+1-555-9876",
  "password": "securePassword123",
  "password2": "securePassword123",
  "company_name": "Tech Recruiters Inc.",
  "company_website": "https://techrecruiters.com",
  "specialization": "Software Engineering, Data Science",
  "years_of_experience": 5,
  "linkedin_profile": "https://linkedin.com/in/janesmith",
  "resume": "<file>",
  "certification": "AIRS Certified, LinkedIn Certified"
}
```

**Response (201 Created):**
```json
{
  "message": "Recruiter registration successful. Please wait for admin approval.",
  "recruiter_id": "recruiter-uuid",
  "email": "jane.smith@company.com"
}
```

---

### 2. Recruiter Login
**Endpoint:** `POST /api/recruiters/login/`  
**Permission:** Public  
**Description:** Authenticate recruiter and get JWT tokens

**Request Body:**
```json
{
  "email": "jane.smith@company.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "recruiter_id": "recruiter-uuid",
  "name": "Jane Smith",
  "email": "jane.smith@company.com",
  "company_name": "Tech Recruiters Inc.",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 3. Get Recruiter Profile
**Endpoint:** `GET /api/recruiters/me/`  
**Permission:** Authenticated Recruiter  
**Description:** Get logged-in recruiter's profile

---

### 4. Recruiter Dashboard
**Endpoint:** `GET /api/recruiters/dashboard/`  
**Permission:** Authenticated Recruiter  
**Description:** Get dashboard with assigned candidates and statistics

**Response (200 OK):**
```json
{
  "recruiter": {
    "id": "recruiter-uuid",
    "name": "Jane Smith",
    "company_name": "Tech Recruiters Inc."
  },
  "assigned_candidates": [
    {
      "id": "profile-uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "assignment_status": "active",
      "registration_status": "assigned"
    }
  ],
  "statistics": {
    "total_assigned": 3,
    "active_candidates": 2,
    "placed_candidates": 5
  }
}
```

---

### 5. List Recruiters (Admin)
**Endpoint:** `GET /api/recruiters/`  
**Permission:** Admin only

**Query Parameters:**
- `active`: Filter by active status
- `search`: Search by name, email, or company

---

### 6. Activate/Deactivate Recruiter (Admin)
**Endpoint:** `POST /api/recruiters/{id}/activate/`  
**Endpoint:** `POST /api/recruiters/{id}/deactivate/`  
**Permission:** Admin only

---

### 7. Assign Candidate to Recruiter (Admin)
**Endpoint:** `POST /api/recruiters/assign/`  
**Permission:** Admin only  
**Description:** Assign candidate to recruiter

**Request Body:**
```json
{
  "profile": "candidate-profile-uuid",
  "recruiter": "recruiter-uuid",
  "notes": "High-priority candidate"
}
```

---

## Payment APIs

### 1. Create Razorpay Order
**Endpoint:** `POST /api/payments/razorpay/create-order/`  
**Permission:** Authenticated  
**Description:** Create Razorpay order for payment

**Request Body:**
```json
{
  "amount": 499.00,
  "currency": "USD",
  "notes": {
    "subscription_id": "sub-uuid"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "payment-uuid",
  "amount": 499.00,
  "provider_order_id": "order_MNxyz123abc",
  "razorpay_key": "rzp_live_abc123",
  "status": "pending"
}
```

---

### 2. Verify Razorpay Payment
**Endpoint:** `POST /api/payments/razorpay/verify/`  
**Permission:** Authenticated  
**Description:** Verify payment signature

**Request Body:**
```json
{
  "razorpay_order_id": "order_MNxyz123abc",
  "razorpay_payment_id": "pay_ABC123xyz",
  "razorpay_signature": "signature_hash"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Payment verified successfully",
  "payment": {
    "id": "payment-uuid",
    "status": "completed"
  }
}
```

---

### 3. List Payments
**Endpoint:** `GET /api/payments/`  
**Permission:** Authenticated  
**Description:** List user's payment records

---

### 4. Razorpay Webhook
**Endpoint:** `POST /api/payments/razorpay/webhook/`  
**Permission:** Public (webhook validation)  
**Description:** Webhook for Razorpay notifications

---

## Job Management APIs

### 1. List Job Postings
**Endpoint:** `GET /api/jobs/`  
**Permission:** Public  
**Description:** List all active job postings

**Query Parameters:**
- `page`: Page number
- `search`: Search by title or company

**Response (200 OK):**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "job_type": "Full-time",
      "salary_range": "$120,000 - $180,000",
      "description": "...",
      "application_deadline": "2024-02-28"
    }
  ]
}
```

---

### 2. Get Job Details
**Endpoint:** `GET /api/jobs/{id}/`  
**Permission:** Public  
**Description:** Get detailed job information

---

### 3. Create Job Posting
**Endpoint:** `POST /api/jobs/`  
**Permission:** Admin or Recruiter  
**Description:** Create new job posting

**Request Body:**
```json
{
  "title": "Senior Software Engineer",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "job_type": "Full-time",
  "salary_range": "$120,000 - $180,000",
  "description": "...",
  "requirements": "5+ years Python, AWS",
  "application_deadline": "2024-02-28"
}
```

---

### 4. Update/Delete Job
**Endpoint:** `PATCH /api/jobs/{id}/`  
**Endpoint:** `DELETE /api/jobs/{id}/`  
**Permission:** Admin or Job Creator

---

## Onboarding APIs

### 1. List Onboarding Workflows
**Endpoint:** `GET /api/onboarding/`  
**Permission:** Authenticated  
**Description:** List onboarding workflows for user

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": {
      "id": "profile-uuid",
      "name": "John Doe"
    },
    "workflow_type": "candidate",
    "current_step": 3,
    "total_steps": 5,
    "progress_percentage": 60,
    "steps": [
      {"step": 1, "title": "Create Account", "completed": true},
      {"step": 2, "title": "Complete Profile", "completed": true},
      {"step": 3, "title": "Submit Forms", "completed": true},
      {"step": 4, "title": "Payment", "completed": false},
      {"step": 5, "title": "Assignment", "completed": false}
    ],
    "completed": false
  }
]
```

---

### 2. Get Onboarding Details
**Endpoint:** `GET /api/onboarding/{id}/`  
**Permission:** Authenticated (owner) or Admin

---

### 3. Create Onboarding Workflow
**Endpoint:** `POST /api/onboarding/`  
**Permission:** Admin  
**Description:** Initialize onboarding for user

---

### 4. Update Onboarding Progress
**Endpoint:** `PATCH /api/onboarding/{id}/`  
**Permission:** Authenticated (owner) or Admin  
**Description:** Update progress and mark steps completed

---

## API Base URL

- **Development:** `http://localhost:8000/api/`
- **Production:** `https://api.hyrind.com/api/`

---

## Additional Resources

- **Swagger Documentation:** `/swagger/`
- **ReDoc Documentation:** `/redoc/`
- **API Schema:** `/swagger.json`

---

## Support

For API issues or questions:
- **Email:** hyrind.operations@gmail.com
- **Documentation:** https://docs.hyrind.com
