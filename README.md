# Hyrind Backend — US IT Recruitment Platform API

<div align="center">

[![Django](https://img.shields.io/badge/Django-5.2.8-092E20?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SimpleJWT](https://img.shields.io/badge/Auth-SimpleJWT-orange)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![Razorpay](https://img.shields.io/badge/Payments-Razorpay-0C2451)](https://razorpay.com/)
[![Tests](https://img.shields.io/badge/tests-120%20passing-brightgreen)](#-testing)

**Enterprise-grade Django REST API for internal US IT recruitment operations.**  
Manages the full candidate lifecycle — registration → onboarding → recruiter assignment → placement — with Razorpay payments, subscription billing, role suggestions, and a full audit trail.

[Quick Start](#-quick-start) · [API Docs](#-api-documentation) · [Endpoints](#-api-endpoints) · [Testing](#-testing) · [Deployment](#-deployment)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Environment Configuration](#-environment-configuration)
- [Test Accounts](#-test-accounts)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [API Endpoints](#-api-endpoints)
- [Recruiter System](#-recruiter-system)
- [Subscription & Addon System](#-subscription--addon-system)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Help Docs](#-help-docs)

---

## Overview

**Hyrind Backend** is a Django REST API built for an internal US IT recruitment agency. It manages candidates, internal recruiters, job postings, payments, and subscription plans from a single platform.

### Business Model

| Actor | Role |
|---|---|
| **Candidate / Client** | IT professional seeking placement; registers, completes forms, subscribes |
| **Internal Recruiter** | Agency employee assigned 1–3 clients; tracks applications and placements |
| **Admin** | Approves users, manages all data, creates private addons, monitors billing |

### Key Capabilities

- **Candidate lifecycle** — registration → admin approval → form completion → subscription → placement
- **Multi-recruiter assignment** — one candidate can be assigned to multiple recruiters (primary, secondary, team lead, backup); full reassignment workflow when a recruiter is absent
- **Role suggestions** — admin suggests target job roles per candidate; candidate selects and submits
- **Private addon plans** — admin creates subscription addons visible only to specific clients at custom prices
- **Razorpay billing** — one-time payments, subscription plans, invoices, webhook verification
- **Audit logging** — every API action is logged with actor, action, and target
- **Swagger / ReDoc** — fully documented interactive API at `/swagger/` and `/redoc/`

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Framework | Django | 5.2.8 |
| REST API | Django REST Framework | 3.16.1 |
| Authentication | djangorestframework-simplejwt | 5.5.1 |
| API Docs | drf-yasg (Swagger / ReDoc) | 1.21.11 |
| Payments | Razorpay | latest |
| CORS | django-cors-headers | 3.13.0 |
| Env config | python-dotenv | 1.0.0 |
| DB (dev) | SQLite | built-in |
| DB (prod) | MySQL | 8.0+ |
| File storage | Local `media/` or MinIO / S3 | optional |
| Python | 3.10+ | — |

---

## Project Structure

```
Hyrind-Backend/
├── hyrind/                      # Project config
│   ├── settings.py              # All settings (env-driven)
│   ├── urls.py                  # Root URL router
│   ├── admin.py                 # Custom admin site
│   └── wsgi.py
│
├── users/                       # Candidates & profiles
│   ├── models.py                # Profile, InterestSubmission, Contact, forms
│   ├── serializers.py           # 10+ serializers
│   ├── views.py                 # Auth, profile, admin, password, forms
│   └── urls.py
│
├── recruiters/                  # Internal recruiters
│   ├── models.py                # Recruiter, Assignment (UUID PKs)
│   ├── serializers.py           # Assignment, recruiter serializers
│   ├── views.py                 # CRUD, activate, dashboard, assign, reassign
│   ├── urls.py                  # REST API routes
│   ├── web_urls.py              # HTML template routes
│   └── web_views.py             # Dashboard, profile, registration pages
│
├── jobs/                        # Job postings & role suggestions
│   ├── models.py                # Job, UserRoleSuggestion (UUID PKs)
│   ├── views.py                 # JobListCreate, JobDetail
│   ├── recommendation_views.py  # RoleSuggestionViewSet
│   └── urls.py
│
├── subscriptions/               # Plans, billing, addons
│   ├── models.py                # SubscriptionPlan, UserSubscription, BillingHistory
│   ├── serializers.py
│   ├── views.py                 # ViewSet + DefaultRouter
│   └── urls.py
│
├── payments/                    # Razorpay integration
│   ├── models.py                # Payment, Invoice, WebhookEvent
│   ├── views.py                 # Orders, verify, webhook
│   ├── invoice_views.py         # InvoiceViewSet
│   └── urls.py
│
├── onboarding/                  # Onboarding workflow
│   ├── models.py                # Onboarding (UUID PK)
│   └── urls.py
│
├── audit/                       # Audit trail
│   ├── models.py                # AuditLog
│   ├── middleware.py            # RequestLoggingMiddleware (API paths only)
│   └── utils.py                 # log_action()
│
├── templates/                   # HTML templates (Bootstrap 5)
├── tests/                       # Test suite (120 tests)
│   ├── test_api_regression.py   # 28 regression tests
│   └── test_new_apis.py         # 92 feature tests
│
├── help_docs/                   # Extended documentation
├── properties-dev.env           # Dev environment variables
├── properties-qa.env
├── properties-stag.env
├── properties-prod.env
├── requirements.txt
├── manage.py
└── create_test_data.py          # Seeds test accounts
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Git

### Setup (Windows)

```powershell
# 1. Clone
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend

# 2. Virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Dependencies
pip install -r requirements.txt

# 4. Migrate (uses SQLite by default in dev)
python manage.py migrate

# 5. Seed test accounts
python create_test_data.py

# 6. Run
python manage.py runserver
```

### Setup (Linux / macOS)

```bash
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python create_test_data.py
python manage.py runserver
```

**Access points after startup:**

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Homepage |
| `http://127.0.0.1:8000/swagger/` | Interactive API docs |
| `http://127.0.0.1:8000/redoc/` | Readable API docs |
| `http://127.0.0.1:8000/admin/` | Django admin panel |
| `http://127.0.0.1:8000/recruiter-registration/` | Recruiter web portal |

---

## Environment Configuration

The settings loader reads `properties-<env>.env` from the project root.  
Select the environment with one of these variables before starting Django:

```
HYRIND_ENV=dev   # or: qa | stag | prod
# alternatives:  DJANGO_ENV=dev  or  ENV=dev
```

Defaults to `dev` (SQLite) when not set.

### Variables Reference

```env
# ── Django ────────────────────────────────────────────────────────────────────
HYRIND_SECRET_KEY=change-me-to-a-50-char-random-string
DEBUG=True

# ── Database (required for qa / stag / prod; dev uses SQLite) ─────────────────
DB_NAME=hyrind
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your@gmail.com
OPERATIONS_EMAIL=hyrind.operations@gmail.com

# ── Razorpay ──────────────────────────────────────────────────────────────────
RAZORPAY_KEY_ID=rzp_test_XXXXXXXX
RAZORPAY_KEY_SECRET=your_secret
RAZORPAY_WEBHOOK_SECRET=whsec_your_secret
RAZORPAY_CURRENCY=USD

# ── MinIO / S3 (optional — local media/ folder used by default) ───────────────
USE_MINIO=False
# MINIO_ACCESS_KEY=
# MINIO_SECRET_KEY=
# MINIO_ENDPOINT=http://127.0.0.1:9000
# MINIO_BUCKET_NAME=hyrind-recruiter-docs
```

> For Gmail SMTP you need an [App Password](https://support.google.com/accounts/answer/185833).  
> See [help_docs/EMAIL_SETUP.md](help_docs/EMAIL_SETUP.md) for full email setup.  
> See [help_docs/MINIO_SETUP.md](help_docs/MINIO_SETUP.md) for object storage setup.

---

## Test Accounts

Run `python create_test_data.py` to seed these accounts:

### Admin
```
Email:    admin@hyrind.com
Password: admin123
```
Full access to Django admin (`/admin/`) and all admin API endpoints.

### Candidate
```
Email:    candidate@test.com
Password: test123
Profile:  John Doe · F1-OPT · BS Computer Science
```

### Recruiter
```
Email:       recruiter@test.com
Password:    test123
Employee ID: H12345
Dashboard:   http://127.0.0.1:8000/recruiter-registration/dashboard/
```

> ⚠️ **Development only.** Change all credentials before deploying to production.

---

## API Documentation

### Interactive Docs

| URL | Tool | Description |
|---|---|---|
| `/swagger/` | Swagger UI | Test endpoints live in the browser |
| `/redoc/` | ReDoc | Clean, readable reference |
| `/swagger.json` | OpenAPI JSON | Import into Postman or code generators |

### Using Swagger UI

1. Open `http://127.0.0.1:8000/swagger/`
2. Call `POST /api/users/login/` (or the relevant login endpoint for your role)
3. Copy the `access` token from the response
4. Click **Authorize 🔓** (top right) → enter `Bearer <access_token>`
5. All subsequent calls will be authenticated automatically

### Extended Docs

| File | Contents |
|---|---|
| [help_docs/API_DOCUMENTATION.md](help_docs/API_DOCUMENTATION.md) | Full endpoint guide with examples |
| [help_docs/API_DOCUMENTATION_GUIDE.md](help_docs/API_DOCUMENTATION_GUIDE.md) | How to read and use the API docs |
| [help_docs/API_STANDARDS_AND_PRACTICES.md](help_docs/API_STANDARDS_AND_PRACTICES.md) | Design conventions and response formats |
| [help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md](help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md) | Intake sheet & credential sheet field rules |
| [help_docs/ROLE_SUGGESTIONS_SIMPLE.md](help_docs/ROLE_SUGGESTIONS_SIMPLE.md) | Role suggestion workflow |
| [help_docs/EMAIL_SETUP.md](help_docs/EMAIL_SETUP.md) | SMTP / Gmail app password setup |
| [help_docs/MINIO_SETUP.md](help_docs/MINIO_SETUP.md) | MinIO / S3 storage setup |

---

## Authentication

JWT Bearer tokens via `djangorestframework-simplejwt`.

### Login by Role

| Role | Endpoint | Response |
|---|---|---|
| Candidate | `POST /api/users/login/` | `access` + `refresh` |
| Recruiter | `POST /api/recruiters/login/` | `access` + `refresh` + recruiter profile |
| Admin | `POST /api/admin/login/` | `access` + `refresh` |
| Standard JWT | `POST /api/token/` | `access` + `refresh` (username/password) |

### Token Refresh

```bash
POST /api/token/refresh/
Content-Type: application/json

{ "refresh": "<refresh_token>" }
```

### Authenticated Request

```bash
curl -H "Authorization: Bearer <access_token>" \
     http://127.0.0.1:8000/api/users/me/
```

### Token Lifetimes

| Token | Lifetime |
|---|---|
| Access | 30 minutes |
| Refresh | 1 day |

---

## API Endpoints

All resource IDs are **UUIDs**. All endpoints are prefixed with `/api/`.

---

### Public (No Auth Required)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/users/register/` | Register new candidate |
| `POST` | `/api/users/login/` | Candidate login |
| `POST` | `/api/users/interest/` | Submit interest form (no account needed) |
| `POST` | `/api/users/contact/` | Contact form |
| `POST` | `/api/users/password-reset/request/` | Send password reset email |
| `GET/POST` | `/api/users/password-reset/confirm/` | Set new password via token |
| `POST` | `/api/recruiters/register/` | Register as recruiter |
| `POST` | `/api/recruiters/login/` | Recruiter login |
| `GET` | `/api/jobs/` | List all job postings |
| `GET` | `/api/jobs/<uuid>/` | Job posting detail |

---

### Candidate (Auth Required)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users/me/` | My profile |
| `GET/PATCH/DELETE` | `/api/users/profiles/<uuid>/` | Profile detail / update |
| `POST` | `/api/users/password-change/` | Change my password |
| `GET/POST` | `/api/users/me/client-intake/` | My intake form |
| `GET/POST` | `/api/users/me/credential-sheet/` | My credential sheet |
| `GET` | `/api/users/forms-completion-status/` | Which forms are complete |
| `GET` | `/api/jobs/suggestions/` | My role suggestions |
| `PATCH` | `/api/jobs/suggestions/<uuid>/toggle/` | Select / deselect a suggestion |
| `POST` | `/api/jobs/suggestions/submit/` | Submit final selections |
| `POST` | `/api/payments/razorpay/create-order/` | Create Razorpay payment order |
| `POST` | `/api/payments/razorpay/verify/` | Verify payment signature |
| `GET` | `/api/subscriptions/plans/` | Browse available plans (includes private addons scoped to me) |
| `GET` | `/api/subscriptions/my-subscriptions/` | My active subscriptions |
| `GET` | `/api/subscriptions/billing-history/` | My billing history |
| `GET` | `/api/onboarding/` | My onboarding workflow |
| `GET/PATCH` | `/api/onboarding/<uuid>/` | Update onboarding step |

---

### Recruiter (Recruiter Auth Required)

| Method | Endpoint | Description |
|---|---|---|
| `GET/PATCH` | `/api/recruiters/me/` | My profile (incl. `availability_status`) |
| `GET` | `/api/recruiters/dashboard/` | Stats, assigned clients, placements |
| `POST` | `/api/jobs/` | Create job posting |
| `PATCH/DELETE` | `/api/jobs/<uuid>/` | Edit or remove job posting |

**Web Portal (HTML):**

| URL | Page |
|---|---|
| `/recruiter-registration/` | Registration form |
| `/recruiter-registration/login/` | Login |
| `/recruiter-registration/dashboard/` | Dashboard |
| `/recruiter-registration/complete-profile/` | Full profile (70+ fields) |
| `/recruiter-registration/profile/` | Profile update |

---

### Admin (Admin Auth Required)

#### User & Candidate Management

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users/` | List all users |
| `GET` | `/api/users/profiles/` | All profiles |
| `GET` | `/api/users/clients/` | Candidates only |
| `GET` | `/api/users/clients/profiles/` | Candidate profiles only |
| `GET` | `/api/users/profiles/<uuid>/client-intake/` | Intake form for a profile |
| `GET` | `/api/users/profiles/<uuid>/credential-sheet/` | Credential sheet for a profile |
| `GET` | `/api/users/profiles/<uuid>/role-suggestions/` | Role suggestions for a profile |
| `GET/PATCH/DELETE` | `/api/users/client-intake/<uuid>/` | Intake form CRUD |
| `GET/PATCH/DELETE` | `/api/users/credential-sheet/<uuid>/` | Credential sheet CRUD |
| `POST` | `/api/users/admin/candidates/<uuid>/activate/` | Approve candidate (`open → approved`) |
| `POST` | `/api/users/admin/candidates/<uuid>/deactivate/` | Reject candidate (`any → rejected`) |
| `POST` | `/api/users/admin/candidates/<uuid>/placed/` | Mark placed (`assigned → closed`) |
| `GET/PATCH` | `/api/users/admin/profile/` | Admin own profile |
| `POST` | `/api/users/admin/register/` | Register new admin |
| `POST` | `/api/users/admin/password/` | Change admin password |

#### Recruiter Management

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/recruiters/` | List all recruiters |
| `GET/PATCH` | `/api/recruiters/<uuid>/` | Detail / update (incl. `availability_status`) |
| `POST` | `/api/recruiters/<uuid>/activate/` | Activate recruiter |
| `POST` | `/api/recruiters/<uuid>/deactivate/` | Deactivate recruiter |
| `POST` | `/api/recruiters/assign/` | Assign candidate to recruiter |
| `GET` | `/api/recruiters/assignments/` | All assignments (filter by status, recruiter, profile) |
| `POST` | `/api/recruiters/assignments/<uuid>/reassign/` | Reassign to another recruiter |

#### Role Suggestions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/jobs/suggestions/bulk_create/` | Create suggestions in bulk for a user |
| `GET` | `/api/jobs/suggestions/` | All suggestions (admin sees all) |
| `PATCH/DELETE` | `/api/jobs/suggestions/<uuid>/` | Edit or remove a suggestion |

#### Subscriptions & Billing

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/api/subscriptions/plans/` | List / create plans (incl. private addons) |
| `GET/PATCH/DELETE` | `/api/subscriptions/plans/<uuid>/` | Plan detail |
| `GET` | `/api/subscriptions/admin/subscriptions/` | All user subscriptions |
| `GET/PATCH` | `/api/subscriptions/admin/subscriptions/<uuid>/` | Subscription detail |
| `GET` | `/api/subscriptions/admin/billing-history/` | All billing records |
| `POST` | `/api/subscriptions/webhook/payment/` | Subscription payment webhook |

#### Payments & Invoices

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/payments/` | All payment records |
| `GET/POST` | `/api/payments/invoices/` | List / create invoices |
| `GET/PATCH` | `/api/payments/invoices/<uuid>/` | Invoice detail |
| `POST` | `/api/payments/razorpay/webhook/` | Razorpay webhook handler |

---

## Recruiter System

### Employee IDs

Auto-generated at registration in the format `H#####` (e.g. `H12345`). Unique, immutable.

### Two-Phase Registration

| Phase | Trigger | Fields |
|---|---|---|
| Phase 1 | Self-registration | Name, email, password, phone, department |
| Phase 2 | Admin activates account | 70+ fields: specialization, skills, certifications, capacity |

### Client Assignment

Admin assigns candidates to recruiters via `POST /api/recruiters/assign/`.

- Each recruiter has a configurable `max_clients` (default 3)
- Each assignment carries a **role**: `primary` · `secondary` · `team_lead` · `backup`
- Each assignment carries a **priority**: `high` · `medium` · `low`

### Reassignment Workflow

When a recruiter is unavailable:

```bash
POST /api/recruiters/assignments/<uuid>/reassign/
Authorization: Bearer <admin_token>
{
  "new_recruiter_id": "<uuid>",
  "reason": "Original recruiter on leave"
}
```

The original assignment is linked via `reassigned_from` and `reassignment_reason`, maintaining a full audit trail.

### Availability Status

Update via `PATCH /api/recruiters/<uuid>/`:

| `availability_status` | Meaning |
|---|---|
| `available` | Accepting new clients |
| `busy` | At capacity |
| `on_leave` | Temporarily absent |
| `inactive` | Not active |

---

## Subscription & Addon System

### Plan Types

| `plan_type` | Description |
|---|---|
| `base` | Mandatory base plan |
| `addon` | Optional add-on feature |

### Private Addons

Admin can create addon plans scoped to specific clients (`is_private=True`). These appear **only** in that client's `GET /api/subscriptions/plans/` response — no other candidate can see or subscribe to them.

```bash
POST /api/subscriptions/plans/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Priority Placement",
  "plan_type": "addon",
  "base_price": "199.00",
  "billing_cycle": "one_time",
  "is_private": true,
  "allowed_profiles": ["<candidate-profile-uuid>"]
}
```

---

## Testing

The test suite runs against a live local server using Python's `unittest` and `requests`.

### Run Tests

```powershell
# Terminal 1 — start the server
python manage.py runserver

# Terminal 2 — run tests
python tests/test_api_regression.py
python tests/test_new_apis.py
```

### Coverage

| File | Tests | What it covers |
|---|---|---|
| `tests/test_api_regression.py` | 28 | Core auth, profiles, forms, jobs, payments, subscriptions |
| `tests/test_new_apis.py` | 92 | Role suggestion flow · recruiter assignment & reassignment · private addon scoping |
| **Total** | **120** | **All passing ✅** |

---

## Deployment

### Environment Selection

| `HYRIND_ENV` | File loaded | Database |
|---|---|---|
| `dev` *(default)* | `properties-dev.env` | SQLite |
| `qa` | `properties-qa.env` | MySQL |
| `stag` | `properties-stag.env` | MySQL |
| `prod` | `properties-prod.env` | MySQL |

### Production Checklist

| Item | Action |
|---|---|
| `DEBUG=False` | Set in `properties-prod.env` |
| Strong `SECRET_KEY` | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `ALLOWED_HOSTS` | Hostname-only entries (already correct — no `http://` prefixes) |
| Secure cookies | Uncomment `CSRF_COOKIE_SECURE` and `SESSION_COOKIE_SECURE` in `settings.py` |
| SSL redirect | Set `SECURE_SSL_REDIRECT=True` in env |
| Collect static | `python manage.py collectstatic` |
| Migrate | `python manage.py migrate` |
| Razorpay live keys | Replace test keys with `rzp_live_...` keys |

### Gunicorn + systemd

```bash
pip install gunicorn
```

```ini
# /etc/systemd/system/hyrind.service
[Unit]
Description=Hyrind Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/srv/hyrind
EnvironmentFile=/etc/hyrind/properties-prod.env
Environment=HYRIND_ENV=prod
ExecStart=/srv/hyrind/.venv/bin/gunicorn hyrind.wsgi:application \
          --workers 4 --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hyrind
sudo systemctl start hyrind
```

### Docker (optional)

```yaml
services:
  api:
    build: .
    env_file: ./properties-prod.env
    environment:
      HYRIND_ENV: prod
    ports:
      - "8000:8000"
    command: >
      gunicorn hyrind.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

---

## Help Docs

| Document | Description |
|---|---|
| [help_docs/API_DOCUMENTATION.md](help_docs/API_DOCUMENTATION.md) | Full API reference with request/response examples |
| [help_docs/API_DOCUMENTATION_GUIDE.md](help_docs/API_DOCUMENTATION_GUIDE.md) | How to read and use the API docs |
| [help_docs/API_STANDARDS_AND_PRACTICES.md](help_docs/API_STANDARDS_AND_PRACTICES.md) | Naming conventions, response formats, error codes |
| [help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md](help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md) | Intake sheet & credential sheet field rules |
| [help_docs/ROLE_SUGGESTIONS_SIMPLE.md](help_docs/ROLE_SUGGESTIONS_SIMPLE.md) | Role suggestion workflow (admin → candidate → submit) |
| [help_docs/EMAIL_SETUP.md](help_docs/EMAIL_SETUP.md) | Gmail SMTP / app password setup |
| [help_docs/MINIO_SETUP.md](help_docs/MINIO_SETUP.md) | MinIO / S3 storage setup |

---

## Support

- **Email**: hyrind.operations@gmail.com
- **Issues**: [GitHub Issues](https://github.com/Teja2142/Hyrind-Backend/issues)

---

*Built by the Hyrind Team*
