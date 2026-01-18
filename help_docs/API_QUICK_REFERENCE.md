# Hyrind API Quick Reference

## Authentication Endpoints
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/login/` | Public | Client login |
| POST | `/api/users/admin/login/` | Public | Admin login |
| POST | `/api/token/refresh/` | Public | Refresh access token |

## User Management
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/register/` | Public | Register new client |
| GET | `/api/users/me/` | Authenticated | Get current user profile |
| GET | `/api/users/` | Admin | List ALL users |
| GET | `/api/clients/` | Admin | List clients only |
| GET | `/api/users/profiles/` | Admin | List all profiles |
| GET | `/api/users/profiles/{id}/` | Admin | Get specific profile |
| PATCH | `/api/users/profiles/{id}/` | Admin | Update profile |

## Password Management
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/password-reset/request/` | Public | Request password reset |
| POST | `/api/users/password-reset/confirm/` | Public | Confirm password reset |
| POST | `/api/users/password-change/` | Authenticated | Change password |

## Subscription Plans
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/plans/` | Public | List all plans |
| GET | `/api/subscriptions/plans/{id}/` | Public | Get plan details |

## User Subscriptions
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/my-subscriptions/` | Authenticated | List user's subscriptions |
| POST | `/api/subscriptions/my-subscriptions/` | Authenticated | Create subscription |
| GET | `/api/subscriptions/my-subscriptions/{id}/` | Authenticated | Get subscription details |
| POST | `/api/subscriptions/my-subscriptions/{id}/activate/` | Authenticated | Activate after payment |
| POST | `/api/subscriptions/my-subscriptions/{id}/cancel/` | Authenticated | Cancel subscription |
| GET | `/api/subscriptions/my-subscriptions/summary/` | Authenticated | Dashboard summary |

## Billing
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/billing-history/` | Authenticated | User's billing history |
| GET | `/api/subscriptions/billing-history/statistics/` | Authenticated | User's billing stats |

## Client Forms
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/client-intake/` | Authenticated | Submit intake form |
| GET | `/api/users/client-intake/{id}/` | Authenticated | Get intake form |
| PATCH | `/api/users/client-intake/{id}/` | Authenticated | Update intake form |
| POST | `/api/users/credential-sheet/` | Authenticated | Submit credentials |
| GET | `/api/users/credential-sheet/{id}/` | Authenticated | Get credentials |
| PATCH | `/api/users/credential-sheet/{id}/` | Authenticated | Update credentials |
| GET | `/api/users/forms-completion-status/` | Authenticated | Check form status |

## Admin - Candidate Management
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/admin/candidates/{id}/activate/` | Admin | Approve candidate |
| POST | `/api/users/admin/candidates/{id}/deactivate/` | Admin | Reject candidate |
| POST | `/api/users/admin/candidates/{id}/placed/` | Admin | Mark as placed |

## Admin - Subscriptions
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/admin/subscriptions/` | Admin | List all subscriptions |
| POST | `/api/subscriptions/admin/subscriptions/` | Admin | Create subscription |
| GET | `/api/subscriptions/admin/subscriptions/{id}/` | Admin | Get subscription |
| PATCH | `/api/subscriptions/admin/subscriptions/{id}/` | Admin | Update subscription |
| DELETE | `/api/subscriptions/admin/subscriptions/{id}/` | Admin | Delete subscription |
| GET | `/api/subscriptions/admin/subscriptions/analytics/` | Admin | Get analytics |

## Admin - Billing
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/subscriptions/admin/billing-history/` | Admin | All billing records |
| GET | `/api/subscriptions/admin/billing-history/{id}/` | Admin | Get billing record |

## Public Endpoints
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/users/interest/` | Public | Submit interest form |
| POST | `/api/users/contact/` | Public | Submit contact form |

## Recruiter Endpoints
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/recruiters/register/` | Public | Register new recruiter |
| POST | `/api/recruiters/login/` | Public | Recruiter login |
| GET | `/api/recruiters/me/` | Recruiter | Get own profile |
| PATCH | `/api/recruiters/me/` | Recruiter | Update own profile |
| GET | `/api/recruiters/dashboard/` | Recruiter | Get dashboard with stats |
| GET | `/api/recruiters/` | Admin | List all recruiters |
| GET | `/api/recruiters/{id}/` | Admin | Get recruiter details |
| PATCH | `/api/recruiters/{id}/` | Admin | Update recruiter |
| DELETE | `/api/recruiters/{id}/` | Admin | Delete recruiter |
| POST | `/api/recruiters/{id}/activate/` | Admin | Approve recruiter |
| POST | `/api/recruiters/{id}/deactivate/` | Admin | Deactivate recruiter |
| POST | `/api/recruiters/assign/` | Admin | Assign candidate to recruiter |

## Payment Endpoints
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/payments/` | Authenticated | List user's payments |
| POST | `/api/payments/razorpay/create-order/` | Authenticated | Create Razorpay order |
| POST | `/api/payments/razorpay/verify/` | Authenticated | Verify payment |
| POST | `/api/payments/razorpay/webhook/` | Public (webhook) | Razorpay webhook |

## Job Management Endpoints
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/jobs/` | Public | List all jobs |
| POST | `/api/jobs/` | Admin/Recruiter | Create job posting |
| GET | `/api/jobs/{id}/` | Public | Get job details |
| PATCH | `/api/jobs/{id}/` | Admin/Creator | Update job |
| DELETE | `/api/jobs/{id}/` | Admin/Creator | Delete job |

## Onboarding Endpoints
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/onboarding/` | Authenticated | List workflows |
| POST | `/api/onboarding/` | Admin | Create workflow |
| GET | `/api/onboarding/{id}/` | Authenticated/Admin | Get workflow details |
| PATCH | `/api/onboarding/{id}/` | Authenticated/Admin | Update progress |

## Webhook
| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/subscriptions/webhook/payment/` | Public | Payment confirmation |
| POST | `/api/payments/razorpay/webhook/` | Public | Razorpay webhook |

---

## Common Query Parameters

### Filtering
- `status`: Filter by status
- `active`: Filter by active status (true/false)
- `plan_type`: Filter by plan type (base/addon)
- `search`: Search by name/email

### Pagination
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

### Date Range
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

---

## Status Values

### Registration Status
- `open`: Initial registration
- `approved`: Admin approved, needs payment
- `ready_to_assign`: Paid, waiting for recruiter
- `assigned`: Working with recruiter
- `waiting_payment`: Additional payment needed
- `closed`: Successfully placed
- `rejected`: Rejected by admin

### Subscription Status
- `pending`: Created, awaiting payment
- `active`: Active subscription
- `cancelled`: User cancelled
- `expired`: Subscription expired

### Billing Status
- `pending`: Payment pending
- `success`: Payment successful
- `failed`: Payment failed
- `refunded`: Payment refunded

---

## Response Codes

- **200:** Success
- **201:** Created
- **400:** Bad request (validation error)
- **401:** Unauthorized (auth required)
- **403:** Forbidden (insufficient permissions)
- **404:** Not found
- **409:** Conflict (resource exists)
- **500:** Server error

---

## Authorization Header

All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```

---

## API Base URL

- **Development:** `http://localhost:8000/api/`
- **Production:** `https://api.hyrind.com/api/`

---

## Documentation URLs

- **Swagger UI:** `/swagger/`
- **ReDoc:** `/redoc/`
- **API Schema:** `/swagger.json`
