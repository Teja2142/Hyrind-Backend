# 🚀 Hyrind Backend Setup Guide

> **Industry Standard Setup for Django REST API with MySQL**

This guide provides a comprehensive, step-by-step setup process for the Hyrind Backend application - a Django REST API for US IT recruitment operations.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Python**: 3.10 or higher ([Download](https://www.python.org/downloads/))
- **Git**: Version control system ([Download](https://git-scm.com/downloads))
- **MySQL Server**: 8.0 or higher ([Download](https://dev.mysql.com/downloads/mysql/))
- **pip**: Python package manager (comes with Python 3.4+)

### Optional Tools
- **Virtual Environment**: `venv` (built-in with Python 3.3+)
- **Git Bash** or **PowerShell**: For Windows command line
- **Postman** or **Insomnia**: For API testing

## 🛠️ Installation Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Teja2142/Hyrind-Backend.git
cd Hyrind-Backend
```

### 2. Set Up Python Virtual Environment

```bash
# Windows
python -m venv hire_venv
hire_venv\Scripts\activate

# Linux/macOS
python3 -m venv hire_venv
source hire_venv/bin/activate
```

**Expected Output**: You should see `(hire_venv)` at the beginning of your command prompt.

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**Key Dependencies**:
- **Django 5.2.8**: Web framework
- **Django REST Framework**: API framework
- **MySQL Client**: Database connectivity
- **JWT Authentication**: Token-based auth
- **Swagger/OpenAPI**: API documentation
- **Razorpay**: Payment processing
- **Stripe**: Payment processing
- **CORS Headers**: Cross-origin requests

### 4. Environment Configuration

#### Create Environment File

```bash
# Copy the example environment file
cp .env.example .env
```

#### Configure Environment Variables

Edit the `.env` file with your specific values:

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

# ===========================================
# JWT CONFIGURATION (Optional - has defaults)
# ===========================================
JWT_ACCESS_TOKEN_LIFETIME=30  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)
```

#### Generate Django Secret Key

For production, generate a secure secret key:

```python
# Run in Python shell
import secrets
print(secrets.token_urlsafe(50))
```

### 5. MySQL Database Setup

#### Start MySQL Service

```bash
# Windows (if using MySQL Installer)
net start mysql

# Linux
sudo systemctl start mysql

# macOS
brew services start mysql
```

#### Create Database

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE hyrind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant permissions (optional, if using different user)
GRANT ALL PRIVILEGES ON hyrind.* TO 'your_user'@'localhost' IDENTIFIED BY 'your_password';
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

#### Alternative: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your local MySQL server
3. Create new schema named `hyrind`
4. Set charset to `utf8mb4` and collation to `utf8mb4_unicode_ci`

### 6. Database Migration

```bash
# Apply database migrations
python manage.py migrate
```

**Expected Output**: You should see successful migration messages for all apps:
- users
- jobs
- payments
- onboarding
- subscriptions
- recruiters
- audit

### 8. Verify Setup

Run the setup verification script to ensure everything is working:

```bash
# Verify your setup
python verify_setup.py
```

This script will check:
- Python version
- Virtual environment
- Required packages
- Environment variables
- Database connection
- Applied migrations

### 9. Create Test Data (Optional)

Create sample users for testing and development:

```bash
# Create test users (admin, candidate, recruiter)
python create_test_data.py
```

**Test Accounts Created:**
- **Admin**: admin@hyrind.com / admin123
- **Candidate**: candidate@test.com / test123  
- **Recruiter**: recruiter@test.com / test123

## 🚀 Running the Application

### Development Server

```bash
# Start Django development server
python manage.py runserver
```

**Access Points**:
- **Homepage**: http://127.0.0.1:8000/
- **API Documentation (Swagger)**: http://127.0.0.1:8000/swagger/
- **API Documentation (ReDoc)**: http://127.0.0.1:8000/redoc/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### Production Deployment

For production deployment, see the [Deployment Guide](DEPLOYMENT.md).

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test jobs
```

### API Testing

Use the interactive Swagger documentation at `/swagger/` or tools like Postman.

## 🔧 Troubleshooting

### Common Issues

#### 1. MySQL Connection Error
```
django.db.utils.OperationalError: (2002, "Can't connect to server on 'localhost' (10061)")
```

**Solution**:
- Ensure MySQL service is running
- Check DB_HOST, DB_USER, DB_PASSWORD in `.env`
- Verify database exists: `SHOW DATABASES;`

#### 2. Import Error: mysqlclient
```
ModuleNotFoundError: No module named 'MySQLdb'
```

**Solution**:
```bash
# Windows
pip install mysqlclient

# Linux
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient

# macOS
brew install mysql-client
pip install mysqlclient
```

#### 3. Email Not Sending
- Use Gmail App Password (not regular password)
- Enable "Less secure app access" or use App Passwords
- For development, use console backend

#### 4. Permission Denied on Virtual Environment
```bash
# Windows PowerShell (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Environment Variables Not Loading

Ensure `python-dotenv` is installed and `.env` file exists in project root.

## 📁 Project Structure

```
Hyrind-Backend/
├── hyrind/                 # Main Django project
│   ├── settings.py        # Django settings
│   ├── urls.py           # URL configuration
│   └── wsgi.py           # WSGI application
├── users/                 # User management app
├── jobs/                  # Job postings app
├── payments/             # Payment processing
├── onboarding/           # Candidate onboarding
├── subscriptions/        # Subscription management
├── recruiters/           # Recruiter management
├── audit/                # Audit logging
├── templates/            # HTML templates
├── media/                # Uploaded files
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── manage.py            # Django management script
└── README.md            # Project documentation
```

## 🔒 Security Notes

### Development vs Production

- **DEBUG**: Set to `False` in production
- **SECRET_KEY**: Use environment variable, never commit to version control
- **ALLOWED_HOSTS**: Specify exact domains in production
- **Database Credentials**: Use strong passwords, separate user accounts

### Environment Variables

Never commit sensitive data to version control:
- Database passwords
- API keys
- Secret keys
- Email credentials

## 📞 Support

For issues or questions:
1. Check this setup guide
2. Review [README.md](README.md) for detailed documentation
3. Check [help_docs/](help_docs/) for API guides
4. Create an issue on GitHub

## ✅ Verification Checklist

- [ ] Repository cloned
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] MySQL server running
- [ ] Database created
- [ ] Migrations applied
- [ ] Server starts without errors
- [ ] Admin panel accessible
- [ ] API documentation loads

---

**🎉 Setup Complete!** Your Hyrind Backend is now ready for development.</content>
<parameter name="filePath">c:\Users\creddy\gk_project\Hyrind-Backend\setup.md