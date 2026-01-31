from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('HYRIND_SECRET_KEY', 'dev-secret-key')

DEBUG = True

# Define URL constants to avoid duplication
API_DOMAIN = 'https://api.hyrind.com'
API_STAGING_DOMAIN = 'https://api-staging.hyrind.com'
STAGING_DOMAIN = 'https://staging.hyrind.com'
PRODUCTION_DOMAIN = 'https://hyrind.com'

# Normalize ALLOWED_HOSTS: list hostnames only (no scheme or port).
# Keep '*' if you still want to allow all hosts during development, but
# in production prefer a specific list or use an env var.
ALLOWED_HOSTS = [
    '*',
    API_DOMAIN,
    'http://82.29.164.112',
    API_STAGING_DOMAIN,
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    STAGING_DOMAIN,
    PRODUCTION_DOMAIN,
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'corsheaders',
    'users',
    'jobs',
    'payments',
    'onboarding',
    'subscriptions',
    'recruiters',
    'audit',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# SimpleJWT settings (optional, can be customized)
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'audit.middleware.RequestLoggingMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    API_DOMAIN,
    PRODUCTION_DOMAIN,
    API_STAGING_DOMAIN,
    'http://localhost:5173',
    STAGING_DOMAIN
]

# Trusted origins for Django's CSRF Origin check. Add production API/domain origins here.
# Include the scheme (https://) as required by Django.
CSRF_TRUSTED_ORIGINS = [
    API_DOMAIN,
    PRODUCTION_DOMAIN,
    API_STAGING_DOMAIN,
    STAGING_DOMAIN,
    
]

# If the service is behind a reverse proxy / load balancer that terminates
# TLS and sets X-Forwarded-Proto, enable this so Django recognizes secure
# requests and CSRF/redirects behave correctly.
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# For production, ensure cookies are only sent over HTTPS. Controlled by
# environment in case you need to run locally without TLS.
# CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True') == 'True'
# SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'

# Optionally redirect all HTTP to HTTPS in production. Set the environment
# variable `SECURE_SSL_REDIRECT=True` when enabling in production.
# SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
]

# Ensure common headers are allowed in CORS preflight and explicitly allow HTTP methods
# including PATCH which some browsers require to be present in Access-Control-Allow-Methods
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-requested-with',
    'x-csrftoken',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

ROOT_URLCONF = 'hyrind.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hyrind.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'hyrind'),
        'USER': os.environ.get('DB_USER', 'gktech'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '82.29.164.112'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# Media files (for uploaded resumes etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Basic logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Toggle request-level audit logging (set to False to disable request logging)
AUDIT_LOG_REQUESTS = True

# Swagger settings to enable Bearer auth in the UI
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
OPERATIONS_EMAIL = os.environ.get('OPERATIONS_EMAIL', 'hyrind.operations@gmail.com')

# ------------------------ Razorpay Settings ------------------------
# Configure these via environment variables in production. Example .env keys:
# RAZORPAY_KEY_ID=rzp_test_XXXXX
# RAZORPAY_KEY_SECRET=yyyyyy
# RAZORPAY_WEBHOOK_SECRET=whsec_zzzz
# RAZORPAY_CURRENCY=USD (or INR)
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', '')
RAZORPAY_CURRENCY = os.environ.get('RAZORPAY_CURRENCY', 'USD')


# ------------------------ MinIO / S3 Storage ------------------------
# To enable MinIO-backed storage set USE_MINIO=True in your environment
USE_MINIO = os.environ.get('USE_MINIO', 'False') == 'True'
if USE_MINIO:
    # django-storages + boto3 settings for S3-compatible backend (MinIO)
    INSTALLED_APPS.append('storages')

    AWS_ACCESS_KEY_ID = os.environ.get('MINIO_ACCESS_KEY', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('MINIO_SECRET_KEY', '')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('MINIO_BUCKET_NAME', 'hyrind-recruiter-docs')
    AWS_S3_ENDPOINT_URL = os.environ.get('MINIO_ENDPOINT', 'http://127.0.0.1:9000')
    AWS_S3_REGION_NAME = os.environ.get('MINIO_REGION', '')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # Useful object parameters
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    # When using MinIO without TLS
    if AWS_S3_ENDPOINT_URL.startswith('http://'):
        AWS_S3_USE_SSL = False
    else:
        AWS_S3_USE_SSL = True
# --------------------------------------------------------------------
