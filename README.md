# 🚀 Hyrind Backend - Recruitment Platform API

[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

A comprehensive Django REST API backend for Hyrind, a modern recruitment platform connecting candidates with opportunities. Features include user registration, interest submissions, recruiter management, job postings, payments, and automated email notifications.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Environment Setup](#-environment-setup)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Key Endpoints](#-key-endpoints)
- [Email Configuration](#-email-configuration)
- [Testing](#-testing)
- [Deployment Notes](#-deployment-notes)

---

## ✨ Features

### 🎯 Core Features
- **User Management**: Registration, authentication (JWT), profile management
- **Interest Submission**: Public form for candidates to express interest (no account needed)
- **Contact Us**: Public contact form with email notifications
- **Recruiter Management**: Full CRUD operations with role-based access
- **Job Postings**: Create, list, update, and delete job opportunities
- **Payment Integration**: Stripe integration for subscription payments
- **Email Notifications**: HTML email templates with attachments

### 🔐 Security & Auth
- JWT (JSON Web Token) authentication
- Role-based permissions (User, Admin, Recruiter)
- Secure password handling
- CSRF protection

### 📚 Documentation
- Swagger/OpenAPI documentation at `/swagger/`
- ReDoc documentation at `/redoc/`
- Beautiful homepage with navigation at `/`

### 📧 Email System
- HTML email templates with inline CSS
- Resume attachment support
- Gmail SMTP integration
- Automated notifications for interest submissions and contact forms

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
├── hyrind/                 # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py            # URL routing
│   └── admin.py           # Custom admin configuration
├── users/                  # User management app
│   ├── models.py          # Profile, InterestSubmission, Contact
│   ├── serializers.py     # API serializers with validation
│   ├── views.py           # API views
│   └── urls.py            # User endpoints
├── recruiters/            # Recruiter management app
│   ├── models.py          # Recruiter model
│   ├── serializers.py     # 4 specialized serializers
│   ├── views.py           # CRUD operations
│   ├── forms.py           # Django forms
│   └── urls.py            # Recruiter endpoints
├── jobs/                  # Job posting app
│   ├── models.py          # Job model
│   ├── serializers.py     # Job serializer
│   └── views.py           # Job CRUD operations
├── payments/              # Payment processing
│   ├── models.py          # Payment records
│   └── views.py           # Stripe integration
├── subscriptions/         # Subscription management
├── onboarding/           # User onboarding flow
├── audit/                # Audit logging utility
├── templates/            # HTML templates
│   └── home.html         # Beautiful homepage
├── media/                # User uploads (resumes, etc.)
├── tests/                # Test suite
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation (Windows PowerShell)

```powershell
# 1. Clone the repository
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend

# 2. Create and activate virtual environment
python -m venv hy_env
.\hy_env\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env with your configuration (email, database, etc.)

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (admin)
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

### Installation (macOS/Linux)

```bash
# 1. Clone the repository
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend

# 2. Create and activate virtual environment
python3 -m venv hy_env
source hy_env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

### Access the Application

- **Homepage**: http://127.0.0.1:8000/
- **Swagger API Docs**: http://127.0.0.1:8000/swagger/
- **ReDoc API Docs**: http://127.0.0.1:8000/redoc/
- **Admin Panel**: http://127.0.0.1:8000/admin/

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

## 🌐 Key Endpoints

### Public Endpoints (No Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Homepage with navigation |
| `POST` | `/api/users/register/` | Register new user account |
| `POST` | `/api/users/login/` | Login and get JWT tokens |
| `POST` | `/api/users/interest/` | Submit interest form (no account needed) |
| `POST` | `/api/users/contact/` | Submit contact form |
| `POST` | `/api/recruiters/register/` | Register new recruiter |
| `GET` | `/swagger/` | API documentation (Swagger UI) |
| `GET` | `/redoc/` | API documentation (ReDoc) |

### Protected Endpoints (Require Authentication)

#### User Management
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/users/` | List all users | Authenticated |
| `GET` | `/api/users/profiles/` | List profiles | Authenticated |
| `GET` | `/api/users/profiles/{id}/` | Get profile by ID | Authenticated |
| `PUT` | `/api/users/profiles/{id}/` | Update profile | Owner/Admin |
| `DELETE` | `/api/users/profiles/{id}/` | Delete profile | Owner/Admin |

#### Recruiter Management
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/recruiters/` | List recruiters | Admin/Self |
| `GET` | `/api/recruiters/{id}/` | Get recruiter details | Admin/Self |
| `PUT` | `/api/recruiters/{id}/` | Update recruiter | Admin |
| `DELETE` | `/api/recruiters/{id}/` | Delete recruiter | Admin |
| `POST` | `/api/recruiters/assign/` | Assign recruiter to candidate | Admin |

#### Job Management
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/jobs/` | List all jobs | Authenticated |
| `POST` | `/api/jobs/` | Create new job | Recruiter/Admin |
| `GET` | `/api/jobs/{id}/` | Get job details | Authenticated |
| `PUT` | `/api/jobs/{id}/` | Update job | Recruiter/Admin |
| `DELETE` | `/api/jobs/{id}/` | Delete job | Admin |

#### Payments & Subscriptions
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| `GET` | `/api/payments/` | List payments | Authenticated |
| `POST` | `/api/payments/` | Create payment | Authenticated |
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

### Run Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test users
python manage.py test recruiters

# Run with coverage (install coverage first)
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual API Testing

#### Using cURL
```bash
# Register user
curl -X POST http://127.0.0.1:8000/api/users/register/ \
  -F "email=test@example.com" \
  -F "password=SecurePass123" \
  -F "confirm_password=SecurePass123" \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "phone=1234567890" \
  -F "university=Test University" \
  -F "degree=Bachelor's" \
  -F "major=Computer Science" \
  -F "visa_status=F1-OPT" \
  -F "graduation_date=05/2025" \
  -F "opt_end_date=05/2026" \
  -F "consent_to_terms=true" \
  -F "resume_file=@/path/to/resume.pdf"
```

#### Using Swagger UI
1. Go to http://127.0.0.1:8000/swagger/
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

---

## 🚀 Deployment Notes

### Production Checklist

- [ ] Set `DEBUG=False` in settings
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Configure production-ready email backend
- [ ] Set strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure CORS headers
- [ ] Set up media file storage (AWS S3, etc.)
- [ ] Configure Stripe production keys
- [ ] Set up proper logging
- [ ] Enable CSRF protection
- [ ] Use environment variables for all secrets

### Database Migration (SQLite → PostgreSQL)

```bash
# Install psycopg2
pip install psycopg2-binary

# Update settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hyrind_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Run migrations
python manage.py migrate
```

### Recommended Hosting Platforms
- **Heroku** (easiest for beginners)
- **AWS Elastic Beanstalk**
- **DigitalOcean App Platform**
- **Railway**
- **Render**

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