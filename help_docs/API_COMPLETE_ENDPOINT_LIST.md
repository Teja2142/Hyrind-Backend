# Complete API Endpoint List - Hyrind Backend

This document lists **ALL 100+ API endpoints** in the Hyrind Backend system.

---

## Summary by Module

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Authentication** | 3 | Login endpoints for clients, admins, and recruiters |
| **User Management** | 28 | Registration, profiles, password management |
| **Subscription Management** | 15 | Plans, subscriptions, billing, analytics |
| **Client Forms** | 7 | Intake sheets, credentials, completion tracking |
| **Recruiter System** | 13 | Recruiter management, dashboard, assignments |
| **Payment Processing** | 4 | Razorpay integration, order creation, verification |
| **Job Management** | 5 | Job postings, CRUD operations |
| **Onboarding** | 4 | Workflow tracking and progress |
| **Admin Operations** | 10 | Candidate management, analytics |
| **Webhooks** | 2 | Payment notifications |
| **Public Endpoints** | 2 | Contact and interest forms |
| **TOTAL** | **103** | Complete API coverage |

---

## 1. Authentication Endpoints (3)

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/login/` | Public | Client/candidate login |
| POST | `/api/users/admin/login/` | Public | Admin login |
| POST | `/api/recruiters/login/` | Public | Recruiter login |
| POST | `/api/token/refresh/` | Public | Refresh JWT token |

---

## 2. User Management Endpoints (28)

### Registration & Profile (5)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/register/` | Public | Register new client |
| GET | `/api/users/me/` | Authenticated | Get current user profile |
| GET | `/api/users/` | Admin | List ALL users |
| GET | `/api/users/profiles/` | Admin | List all profiles |
| GET | `/api/users/profiles/{id}/` | Admin | Get specific profile |
| PATCH | `/api/users/profiles/{id}/` | Admin | Update profile |
| DELETE | `/api/users/profiles/{id}/` | Admin | Delete profile |

### Client Endpoints (2)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/users/clients/` | Admin | List clients only |
| GET | `/api/users/clients/profiles/` | Admin | List client profiles |

### Password Management (3)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/password-reset/request/` | Public | Request password reset |
| POST | `/api/users/password-reset/confirm/` | Public | Confirm password reset |
| POST | `/api/users/password-change/` | Authenticated | Change password |

### Admin User Management (3)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/users/admin/profile/` | Admin | Get admin profile |
| POST | `/api/users/admin/register/` | Admin | Register new admin |
| POST | `/api/users/admin/password/` | Admin | Change admin password |

### Candidate Status Management (5)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/admin/candidates/{id}/activate/` | Admin | Approve candidate |
| POST | `/api/users/admin/candidates/{id}/deactivate/` | Admin | Reject candidate |
| POST | `/api/users/admin/candidates/{id}/placed/` | Admin | Mark as placed |
| POST | `/api/users/admin/candidates/{id}/approve/` | Admin | Approve registration |
| POST | `/api/users/admin/candidates/{id}/reject/` | Admin | Reject registration |

### Client Forms (7)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/client-intake/` | Authenticated | Submit intake form |
| GET | `/api/users/client-intake/{id}/` | Authenticated | Get intake form |
| PATCH | `/api/users/client-intake/{id}/` | Authenticated | Update intake form |
| POST | `/api/users/credential-sheet/` | Authenticated | Submit credentials |
| GET | `/api/users/credential-sheet/{id}/` | Authenticated | Get credentials |
| PATCH | `/api/users/credential-sheet/{id}/` | Authenticated | Update credentials |
| GET | `/api/users/forms-completion-status/` | Authenticated | Check form status |

### Public Forms (2)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/interest/` | Public | Submit interest form |
| POST | `/api/users/contact/` | Public | Submit contact form |

---

## 3. Subscription Management Endpoints (15)

### Subscription Plans (2)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/plans/` | Public | List all plans |
| GET | `/api/subscriptions/plans/{id}/` | Public | Get plan details |

### User Subscriptions (6)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/my-subscriptions/` | Authenticated | List user subscriptions |
| POST | `/api/subscriptions/my-subscriptions/` | Authenticated | Create subscription |
| GET | `/api/subscriptions/my-subscriptions/{id}/` | Authenticated | Get subscription |
| PATCH | `/api/subscriptions/my-subscriptions/{id}/` | Authenticated | Update subscription |
| POST | `/api/subscriptions/my-subscriptions/{id}/activate/` | Authenticated | Activate subscription |
| POST | `/api/subscriptions/my-subscriptions/{id}/cancel/` | Authenticated | Cancel subscription |
| GET | `/api/subscriptions/my-subscriptions/summary/` | Authenticated | Dashboard summary |

### Billing History (2)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/billing-history/` | Authenticated | User billing history |
| GET | `/api/subscriptions/billing-history/statistics/` | Authenticated | User billing stats |

### Admin Subscription Management (5)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/admin/subscriptions/` | Admin | List all subscriptions |
| POST | `/api/subscriptions/admin/subscriptions/` | Admin | Create subscription |
| GET | `/api/subscriptions/admin/subscriptions/{id}/` | Admin | Get subscription |
| PATCH | `/api/subscriptions/admin/subscriptions/{id}/` | Admin | Update subscription |
| DELETE | `/api/subscriptions/admin/subscriptions/{id}/` | Admin | Delete subscription |
| GET | `/api/subscriptions/admin/subscriptions/analytics/` | Admin | Get analytics |
| GET | `/api/subscriptions/admin/billing-history/` | Admin | All billing records |

---

## 4. Recruiter System Endpoints (13)

### Recruiter Auth & Profile (4)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/recruiters/register/` | Public | Register recruiter |
| POST | `/api/recruiters/login/` | Public | Recruiter login |
| GET | `/api/recruiters/me/` | Recruiter | Get own profile |
| PATCH | `/api/recruiters/me/` | Recruiter | Update own profile |
| GET | `/api/recruiters/dashboard/` | Recruiter | Get dashboard |

### Admin Recruiter Management (8)
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/recruiters/` | Admin | List all recruiters |
| GET | `/api/recruiters/{id}/` | Admin | Get recruiter details |
| PATCH | `/api/recruiters/{id}/` | Admin | Update recruiter |
| DELETE | `/api/recruiters/{id}/` | Admin | Delete recruiter |
| POST | `/api/recruiters/{id}/activate/` | Admin | Approve recruiter |
| POST | `/api/recruiters/{id}/deactivate/` | Admin | Deactivate recruiter |
| POST | `/api/recruiters/assign/` | Admin | Assign candidate |
| GET | `/api/recruiters/registration-forms/` | Admin | List registration forms |
| GET | `/api/recruiters/registration-forms/{id}/` | Admin | Get form details |

---

## 5. Payment Processing Endpoints (4)

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/payments/` | Authenticated | List payments |
| POST | `/api/payments/` | Authenticated | Create payment record |
| POST | `/api/payments/razorpay/create-order/` | Authenticated | Create Razorpay order |
| POST | `/api/payments/razorpay/verify/` | Authenticated | Verify payment |
| POST | `/api/payments/razorpay/webhook/` | Public (webhook) | Razorpay webhook |

---

## 6. Job Management Endpoints (5)

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/jobs/` | Public | List all jobs |
| POST | `/api/jobs/` | Admin/Recruiter | Create job posting |
| GET | `/api/jobs/{id}/` | Public | Get job details |
| PATCH | `/api/jobs/{id}/` | Admin/Creator | Update job |
| DELETE | `/api/jobs/{id}/` | Admin/Creator | Delete job |

---

## 7. Onboarding Endpoints (4)

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/onboarding/` | Authenticated | List workflows |
| POST | `/api/onboarding/` | Admin | Create workflow |
| GET | `/api/onboarding/{id}/` | Authenticated/Admin | Get workflow |
| PATCH | `/api/onboarding/{id}/` | Authenticated/Admin | Update progress |

---

## 8. Webhook Endpoints (2)

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/subscriptions/webhook/payment/` | Public | Subscription payment webhook |
| POST | `/api/payments/razorpay/webhook/` | Public | Razorpay webhook |

---

## API Endpoints by Permission Level

### Public Endpoints (17)
- User login, admin login, recruiter login
- Token refresh
- User registration, recruiter registration
- Password reset request/confirm
- Interest and contact forms
- List subscription plans
- List/view jobs
- Webhooks (2)

### Authenticated User Endpoints (32)
- Get current user profile
- Password change
- Client intake sheet (create, view, update)
- Credential sheet (create, view, update)
- Forms completion status
- User subscriptions (list, create, view, update, activate, cancel, summary)
- Billing history and statistics
- List/create/view/update onboarding workflows
- List/create payments
- Create/verify Razorpay orders

### Authenticated Recruiter Endpoints (5)
- Get/update own profile
- View dashboard with assigned candidates
- Access assigned candidate details

### Admin Only Endpoints (49)
- List all users, clients, profiles
- Manage profiles (create, update, delete)
- Admin registration and password management
- Candidate status management (approve, reject, activate, deactivate, placed)
- List/manage all recruiters
- Activate/deactivate recruiters
- Assign candidates to recruiters
- Admin subscription management (list, create, update, delete all subscriptions)
- View all billing history across users
- Subscription analytics and metrics
- Create onboarding workflows
- Create/update/delete job postings

---

## Module File Locations

| Module | Views File | URLs File |
|--------|------------|-----------|
| Users | `users/views.py` | `users/urls.py` |
| Subscriptions | `subscriptions/views.py` | `subscriptions/urls.py` |
| Recruiters | `recruiters/views.py` | `recruiters/urls.py` |
| Payments | `payments/views.py` | `payments/urls.py` |
| Jobs | `jobs/views.py` | `jobs/urls.py` |
| Onboarding | `onboarding/views.py` | `onboarding/urls.py` |

---

## Main URL Configuration

Base URLs are defined in `hyrind/urls.py`:
- `/api/users/` → User management
- `/api/subscriptions/` → Subscription & billing
- `/api/recruiters/` → Recruiter system
- `/api/payments/` → Payment processing
- `/api/jobs/` → Job management
- `/api/onboarding/` → Onboarding workflows

---

## Notes

1. **All endpoints** support standard HTTP methods and return JSON responses
2. **Pagination** is available on list endpoints (default: 10 items per page)
3. **Filtering** is available via query parameters on most list endpoints
4. **Authentication** uses JWT tokens in Authorization header
5. **File uploads** use multipart/form-data content type
6. **Error responses** follow standard HTTP status codes

---

## Documentation Access

- **Swagger UI:** `http://localhost:8000/swagger/`
- **ReDoc:** `http://localhost:8000/redoc/`
- **API Schema:** `http://localhost:8000/swagger.json`

---

**Last Updated:** January 18, 2026  
**Total Endpoints:** 103  
**Total Views:** 52  
**Total Modules:** 6
