# MinIO Configuration for Recruiter File Uploads

This guide explains how to set up MinIO for storing recruiter registration documents.

## 📦 Installation

### Step 1: Install boto3 and django-storages

```bash
pip install boto3 django-storages
```

### Step 2: Update requirements.txt

Add these lines to your `requirements.txt`:
```
boto3>=1.26.0
django-storages>=1.13.0
```

## ⚙️ Configuration

### Step 3: Update Django Settings (`settings.py`)

```python
# =================== FILE STORAGE ===================

# Add 'storages' to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps ...
    'storages',
    'recruiters',
]

# =================== MinIO/S3 Configuration ===================

# Use S3 storage for all file uploads
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# AWS credentials (Replace with your MinIO credentials)
AWS_ACCESS_KEY_ID = 'minioadmin'  # Default MinIO access key
AWS_SECRET_ACCESS_KEY = 'minioadmin'  # Default MinIO secret key

# MinIO bucket name
AWS_STORAGE_BUCKET_NAME = 'hyrind-recruiter-docs'

# MinIO S3-compatible endpoint
# For localhost: http://localhost:9000
# For production: https://minio.yourdomain.com
AWS_S3_ENDPOINT_URL = 'http://localhost:9000'

# AWS region (MinIO default)
AWS_S3_REGION_NAME = 'us-east-1'

# S3 configuration
AWS_S3_USE_SSL = False  # Set to True for HTTPS (production)
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_S3_CUSTOM_DOMAIN = None  # Set to your domain for custom URLs
AWS_DEFAULT_ACL = 'public-read'  # Change to 'private' if files should be private

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB in bytes
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB in bytes

# =================== Static Files (Optional) ===================

# If you want to serve static files from S3 as well:
# STATIC_LOCATION = 'static'
# STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{STATIC_LOCATION}/'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# =================== Media Files ===================

# Media files go to S3 by default when using storages backend
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
```

## 🚀 Running MinIO Locally

### Option 1: Docker (Recommended)

```bash
# Pull and run MinIO image
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /minio --console-address ":9001"
```

**Access MinIO:**
- API: http://localhost:9000
- Console: http://localhost:9001
- Username: minioadmin
- Password: minioadmin

### Option 2: Binary Installation

```bash
# Download MinIO binary
wget https://dl.min.io/server/minio/release/linux-x86_64/minio

# Make executable
chmod +x minio

# Run MinIO
./minio server /data
```

## 🪣 Create MinIO Bucket

### Using MinIO Console

1. Go to http://localhost:9001
2. Login with credentials (default: minioadmin/minioadmin)
3. Click "Create Bucket"
4. Name: `hyrind-recruiter-docs`
5. Click Create

### Using AWS CLI

```bash
# Configure AWS CLI for MinIO
aws configure --profile minio

# AWS Access Key ID: minioadmin
# AWS Secret Access Key: minioadmin
# Default region: us-east-1
# Default output format: json

# Create bucket
aws s3 mb s3://hyrind-recruiter-docs \
  --endpoint-url http://localhost:9000 \
  --profile minio
```

### Using boto3

```python
import boto3

# Create S3 client
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)

# Create bucket
s3_client.create_bucket(Bucket='hyrind-recruiter-docs')
```

## 📋 Verify Configuration

### Django Shell Test

```python
python manage.py shell

# Test file upload
from django.core.files.base import ContentFile
from recruiters.models import RecruiterRegistration

# Create a test registration
registration = RecruiterRegistration(
    full_name="Test User",
    email="test@example.com",
    phone_number="9876543210",
    # ... other required fields ...
)

# Create a test file
test_file = ContentFile(b"Test content")
test_file.name = "test.pdf"

# Upload file
registration.aadhaar_card_file = test_file
registration.save()

# Verify file URL
print(registration.aadhaar_card_file.url)
```

## 🔒 Production Setup

### Configuration for Production

```python
# Use HTTPS
AWS_S3_USE_SSL = True

# Custom domain
AWS_S3_ENDPOINT_URL = 'https://minio.yourdomain.com'
AWS_S3_CUSTOM_DOMAIN = 'minio.yourdomain.com'

# Private files by default
AWS_DEFAULT_ACL = 'private'

# CORS configuration
# Configure in MinIO console or via AWS CLI
aws s3api put-bucket-cors \
  --bucket hyrind-recruiter-docs \
  --cors-configuration file://cors.json \
  --endpoint-url https://minio.yourdomain.com
```

### CORS Configuration (cors.json)

```json
{
  "CORSRules": [
    {
      "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
      "AllowedOrigins": ["https://yourdomain.com"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

### SSL Certificate

Use a reverse proxy (Nginx) to handle HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name minio.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/key.key;

    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring & Maintenance

### Monitor Storage Usage

```python
import boto3

s3_client = boto3.client('s3', endpoint_url='http://localhost:9000')
response = s3_client.list_objects_v2(Bucket='hyrind-recruiter-docs')

total_size = sum(obj['Size'] for obj in response.get('Contents', []))
print(f"Total storage used: {total_size / (1024*1024):.2f} MB")
```

### Cleanup Old Files

```python
from django.utils import timezone
from datetime import timedelta
from recruiters.models import RecruiterRegistration

# Delete files not verified after 30 days
thirty_days_ago = timezone.now() - timedelta(days=30)
old_registrations = RecruiterRegistration.objects.filter(
    created_at__lt=thirty_days_ago,
    is_verified=False
)

for reg in old_registrations:
    # Delete files from S3
    if reg.aadhaar_card_file:
        reg.aadhaar_card_file.delete()
    # ... delete other files ...
    reg.delete()
```

## 🐛 Troubleshooting

### Connection Error

```
Error: Could not connect to MinIO server
Solution: Check MinIO is running and endpoint URL is correct
```

### Access Denied

```
Error: User: minioadmin is not allowed on this operation
Solution: Check AWS credentials and MinIO permissions
```

### File Not Found

```
Error: The S3 bucket does not exist
Solution: Create the bucket using MinIO console or AWS CLI
```

### Size Limit Error

```
Error: File size exceeds maximum allowed
Solution: Check FILE_UPLOAD_MAX_MEMORY_SIZE in settings.py (set to 5MB)
```

## 📚 Additional Resources

- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [django-storages Documentation](https://django-storages.readthedocs.io/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html)

---

## 🎯 Quick Start

```bash
# 1. Install dependencies
pip install boto3 django-storages

# 2. Run MinIO locally
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /minio --console-address ":9001"

# 3. Create bucket in MinIO console
# http://localhost:9001
# Bucket name: hyrind-recruiter-docs

# 4. Update Django settings (see configuration above)

# 5. Test upload
python manage.py shell
# Run test code from "Verify Configuration" section

# 6. You're ready to use the recruiter registration form!
```
