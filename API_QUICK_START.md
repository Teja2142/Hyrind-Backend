# 🚀 Hyrind Backend API - Quick Start Guide

## Overview
Hyrind is a comprehensive Django REST API for client onboarding, job matching, payment processing, and recruiter management. All APIs are documented with Swagger/OpenAPI.

---

## 📚 Documentation Structure

### Start Here 👇

**For API Reference:**
- **[API_DOCUMENTATION_GUIDE.md](help_docs/API_DOCUMENTATION_GUIDE.md)** ⭐ 
  - Complete reference for all 49 APIs
  - What each API does and why
  - Real-world examples (cURL, JSON)
  - Status codes and error handling

**For Architecture:**
- **[API_STANDARDS_AND_PRACTICES.md](help_docs/API_STANDARDS_AND_PRACTICES.md)**
  - Industry standards and best practices applied
  - REST conventions used
  - Authentication patterns
  - Error handling strategies

**For Navigation:**
- **[DOCUMENTATION_MAP.md](help_docs/DOCUMENTATION_MAP.md)**
  - Navigate by user role (Client, Admin, Recruiter)
  - API grouping by feature
  - Quick lookup by endpoint

**For Configuration:**
- **[EMAIL_SETUP.md](help_docs/EMAIL_SETUP.md)** - Email service configuration
- **[MINIO_SETUP.md](help_docs/MINIO_SETUP.md)** - S3-compatible file storage
- **[CLIENT_FORMS_API_FIELD_VALIDATIONS.md](help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md)** - Form field rules

---

## 🚀 Getting Started

### 1. Start the Server
```bash
python manage.py runserver
```

### 2. Access Swagger UI
Visit: **http://localhost:8000/swagger/**

This interactive interface lets you:
- 📖 Browse all endpoints
- 🧪 Test APIs directly
- 📋 View request/response schemas
- 🔐 Authenticate with JWT tokens

### 3. Authenticate
All APIs (except login/register) require JWT authentication:

1. Call `POST /api/users/login/` with email/password
2. Get access token from response
3. Include in headers: `Authorization: Bearer <access_token>`

---

## 🏗️ Project Structure

```
Hyrind-Backend/
├── help_docs/              # 📚 Comprehensive documentation
├── hyrind/                 # 🎛️ Project settings & routing
├── users/                  # 👤 Authentication & profiles
├── jobs/                   # 💼 Job postings
├── recruiters/             # 🎯 Recruiter management
├── payments/               # 💳 Payment processing
├── subscriptions/          # 📅 Subscription management
├── onboarding/             # 📋 Client onboarding workflow
├── audit/                  # 📝 Activity logging
├── utils/                  # 🛠️ Helper functions
├── tests/                  # ✅ Integration tests
└── manage.py               # Django management
```

---

## 🔑 Core API Endpoints

### Authentication
- `POST /api/users/login/` - Client login
- `POST /api/users/register/` - Client registration
- `POST /api/token/refresh/` - Refresh JWT token

### User Management
- `GET /api/users/profile/` - Get user profile
- `PUT/PATCH /api/users/profile/` - Update profile

### Client Forms
- `POST /api/users/client-intake/` - Create intake sheet
- `POST /api/users/credential-sheet/` - Create credential sheet
- `GET /api/users/forms-completion-status/` - Check form status

### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create job (admin only)
- `GET/PUT/PATCH/DELETE /api/jobs/{id}/` - Job CRUD

### Recruiters
- `GET /api/recruiters/` - List recruiters
- `POST /api/recruiters/assign/` - Assign recruiter to client

### Payments & Subscriptions
- `POST /api/payments/` - Create payment
- `GET /api/subscriptions/` - List subscriptions
- `POST /api/subscriptions/` - Create subscription

---

## ✅ Key Features

✅ **JWT Authentication** - Secure token-based auth  
✅ **File Uploads** - Resume, ID, visa documents  
✅ **Email Notifications** - Automated email on form submission  
✅ **Swagger/OpenAPI** - Interactive API documentation  
✅ **Comprehensive Logging** - Audit trail of all actions  
✅ **Role-Based Access** - Client, Admin, Recruiter roles  
✅ **Form Validation** - Field-level validation rules  
✅ **Payment Integration** - Stripe payment processing  
✅ **Subscription Workflow** - Automated subscription management  
✅ **Onboarding Flow** - Multi-step client onboarding  

---

## 📞 Support Resources

- 🐍 **Django Documentation**: https://docs.djangoproject.com/
- 🔄 **DRF Docs**: https://www.django-rest-framework.org/
- 📖 **Swagger/OpenAPI**: https://swagger.io/
- 🔐 **JWT Auth**: https://github.com/jpadilla/pyjwt

---

## 🧪 Testing with cURL

### Login
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

### Get Profile (requires token)
```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List Jobs
```bash
curl -X GET http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔧 Configuration Files

- `.env` - Environment variables (create from `.env.example`)
- `hyrind/settings.py` - Django settings
- `requirements.txt` - Python dependencies
- `manage.py` - Django management script

---

## 📊 Database

The project uses **SQLite** (development) or PostgreSQL (production).

Migrations:
```bash
python manage.py makemigrations   # Create migrations
python manage.py migrate          # Apply migrations
python manage.py createsuperuser  # Create admin user
```

---

## 🎯 Next Steps

1. **Read** [API_DOCUMENTATION_GUIDE.md](help_docs/API_DOCUMENTATION_GUIDE.md) for complete API reference
2. **Visit** http://localhost:8000/swagger/ to test APIs interactively
3. **Check** [DOCUMENTATION_MAP.md](help_docs/DOCUMENTATION_MAP.md) for role-specific guidance
4. **Setup** Email and S3 storage using help_docs guides

---

**Status:** ✅ Production-Ready  
**Last Updated:** January 16, 2026  
**API Version:** v1  
**Django:** 5.2.8
