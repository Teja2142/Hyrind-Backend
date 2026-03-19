from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
 
# Determine runtime environment and load corresponding properties-*.env file.
# Set `HYRIND_ENV`, `DJANGO_ENV`, or `ENV` in your deployment to one of:
# 'dev', 'qa', 'perf', 'stag', 'prod' (or synonyms like 'staging', 'production').
# Loader prefers files named `properties-<env>.env` (e.g. properties-dev.env).
ENV_NAME = (
    os.environ.get('HYRIND_ENV')
    or os.environ.get('DJANGO_ENV')
    or os.environ.get('ENV')
    or 'dev'
).lower()

# Normalize common synonyms to the short tokens used in filenames
_ENV_MAP = {
    'production': 'prod',
    'prod': 'prod',
    'staging': 'stag',
    'stage': 'stag',
    'stag': 'stag',
    'qa': 'qa',
    'performance': 'perf',
    'perf': 'perf',
    'development': 'dev',
    'dev': 'dev',
}
ENV_NAME = _ENV_MAP.get(ENV_NAME, ENV_NAME)

env_path = BASE_DIR / f'properties-{ENV_NAME}.env'
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))
else:
    # fallback to legacy `.env` if present
    default_env = BASE_DIR / '.env'
    if default_env.exists():
        load_dotenv(dotenv_path=str(default_env))

SECRET_KEY = os.environ.get('HYRIND_SECRET_KEY', 'dev-secret-key')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Define URL constants to avoid duplication
API_DOMAIN = 'https://api.hyrind.com'
API_STAGING_DOMAIN = 'https://api-staging.hyrind.com'
STAGING_DOMAIN = 'https://staging.hyrind.com'
PRODUCTION_DOMAIN = 'https://hyrind.com'

# Backend URL for password reset links - automatically set based on environment
if ENV_NAME in ['prod', 'production']:
    BACKEND_URL = os.environ.get('BACKEND_URL', API_DOMAIN)
elif ENV_NAME in ['stag', 'staging', 'stage']:
    BACKEND_URL = os.environ.get('BACKEND_URL', API_STAGING_DOMAIN)
elif ENV_NAME in ['qa']:
    BACKEND_URL = os.environ.get('BACKEND_URL', 'https://api-qa.hyrind.com')
elif ENV_NAME in ['perf', 'performance']:
    BACKEND_URL = os.environ.get('BACKEND_URL', 'https://api-perf.hyrind.com')
else:  # dev, local, or any other environment
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://127.0.0.1:8000')

# Normalize ALLOWED_HOSTS: list hostnames only (no scheme or port).
# Django matches against the Host header, so strip http(s):// and ports.
# Keep '*' only for local development; use a specific list in production.
ALLOWED_HOSTS = [
    '*',
    'api.hyrind.com',
    '82.29.164.112',
    'api-staging.hyrind.com',
    'localhost',
    '127.0.0.1',
    'staging.hyrind.com',
    'hyrind.com',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    # Local apps
    'users',
    'audit',
    'notifications',
    'candidates',
    'recruiters',
    'billing',
    'chat',
    'config',
    'files',
]
# Custom user model — must come before REST_FRAMEWORK
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Hyrind API',
    'DESCRIPTION': (
        'Backend API for the Hyrind placement management platform.\n\n'
        'Roles: candidate | recruiter | team_lead | team_manager | admin | finance_admin\n\n'
        '**Authentication**: Protected endpoints require a Bearer JWT in the Authorization header.\n'
        'Obtain a token via `POST /api/auth/login/`, then pass: `Authorization: Bearer <access_token>`'
    ),
    'VERSION': '4.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    # Global JWT security — every endpoint shows the lock icon; use @extend_schema(security=[]) to opt-out
    'SECURITY': [{'BearerAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'Obtain via POST /api/auth/login/ → copy the `access` value → click Authorize above',
            }
        }
    },
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'deepLinking': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
    },
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
    'http://localhost:8080',
    'http://127.0.0.1:8080',
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

# Database configuration - use SQLite for local development
if ENV_NAME == 'local' or ENV_NAME == 'dev':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
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

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

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
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
        'detailed': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'WARNING',
        },
    },
    'loggers': {
        # Root logger - only warnings and errors
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        # Silence Django autoreload messages
        'django.utils.autoreload': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Silence drf-yasg schema generation warnings
        'drf_yasg': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Show errors from our app
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Email service - only show actual email send confirmations
        'utils.email_service': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Toggle request-level audit logging (set to False to disable request logging)
AUDIT_LOG_REQUESTS = True

# Email Configuration
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'gktechnologies.stl@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'gktechnologies.stl@gmail.com')
OPERATIONS_EMAIL            = os.environ.get('OPERATIONS_EMAIL', 'hyrind.operations@gmail.com')
# Used in transactional emails and notification links
ADMIN_NOTIFICATION_EMAIL    = os.environ.get('ADMIN_NOTIFICATION_EMAIL', OPERATIONS_EMAIL)
SITE_URL                    = os.environ.get('SITE_URL', 'https://hyrnd.netlify.app')

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
