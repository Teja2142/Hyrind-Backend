# 🔐 Authentication & API Usage Guide

## Table of Contents
1. [Serializers Review](#serializers-review)
2. [JWT Authentication](#jwt-authentication)
3. [Using Authentication in Routes](#using-authentication-in-routes)
4. [Swagger/API Documentation](#swagger-api-documentation)
5. [Testing with Postman/cURL](#testing-with-postmancurl)

---

## ✅ Serializers Review

### **Overall Assessment: EXCELLENT** ✨

Your serializers are well-structured with proper validation. Here's the breakdown:

### 1. **UserSerializer** - ✅ Good
```python
- Simple and clean
- Returns only id and email (no username, as intended)
- Used for nested user objects in responses
```

### 2. **ProfileSerializer** - ✅ Good
```python
✅ Properly handles nested user object
✅ Phone validation: 10-12 digits with flexible input
✅ Date parsing: MM/YYYY format for graduation/OPT dates
✅ File validation: PDF/DOCX only, max 5MB
✅ URL validation for LinkedIn/GitHub
✅ Handles blank dates properly (normalizes to None)
```

### 3. **RegistrationSerializer** - ✅ Excellent
```python
✅ Password confirmation check
✅ Email uniqueness validation
✅ Phone validation (10-12 digits)
✅ Required field validation
✅ Creates both User and Profile atomically
✅ Uses email as username for authentication
✅ Audit logging included
```

### 4. **InterestSubmissionSerializer** - ✅ Good
```python
✅ Allows duplicate emails (by design for interest form)
✅ Phone validation consistent with other serializers
✅ Date parsing and validation
✅ Resume file validation
✅ URL validation
✅ Consent requirement enforced
```

### 5. **ContactSerializer** - ✅ Excellent
```python
✅ Full name validation (min 2 characters)
✅ Email validation
✅ Phone validation (10-12 digits)
✅ Message validation (10-2000 characters)
✅ Read-only fields properly marked
✅ Clear error messages
```

### 🎯 Minor Suggestions (Optional):
1. **Code Duplication**: Phone validation regex pattern appears 4 times
   - Consider creating a constant: `PHONE_REGEX = r'^\d{10,12}$'`
   
2. **Consistent Error Messages**: All phone errors say the same thing (good for consistency)

---

## 🔑 JWT Authentication

### How JWT Works in Your Project

1. **Login (Get Token)**
   - User sends email + password
   - Server validates credentials
   - Server returns access token + refresh token

2. **Use Token**
   - Include token in Authorization header
   - Format: `Authorization: Bearer <access_token>`

3. **Refresh Token**
   - When access token expires, use refresh token to get new access token

### Authentication Endpoints

```
POST /api/users/login/          - Get JWT tokens (email + password)
POST /api/token/                - Alternative login endpoint
POST /api/token/refresh/        - Refresh access token
```

---

## 🛡️ Using Authentication in Routes

### Permission Classes

Django REST Framework provides several permission classes:

```python
from rest_framework import permissions

# 1. AllowAny - No authentication required (public endpoints)
permission_classes = [permissions.AllowAny]

# 2. IsAuthenticated - Requires valid JWT token
permission_classes = [permissions.IsAuthenticated]

# 3. IsAdminUser - Requires admin/staff user
permission_classes = [permissions.IsAdminUser]

# 4. IsAuthenticatedOrReadOnly - Read: anyone, Write: authenticated
permission_classes = [permissions.IsAuthenticatedOrReadOnly]
```

### Examples in Your Code

#### Public Endpoint (No Auth Required)
```python
class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can register
    
    def post(self, request, *args, **kwargs):
        # ... registration logic
```

#### Protected Endpoint (Auth Required)
```python
class ProfileList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # 🔒 Requires JWT token
    
    def get_queryset(self):
        # Optionally filter by authenticated user
        return Profile.objects.filter(user=self.request.user)
```

#### Admin-Only Endpoint
```python
class RecruiterListView(generics.ListAPIView):
    serializer_class = RecruiterListSerializer
    permission_classes = [permissions.IsAdminUser]  # 🔒 Admins only
    
    def get_queryset(self):
        # Admin sees all recruiters
        return Recruiter.objects.filter(active=True)
```

#### Mixed Permissions (Custom Logic)
```python
class RecruiterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecruiterSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]  # Anyone logged in can view
        else:
            return [permissions.IsAdminUser()]  # Only admins can edit/delete
```

### Getting the Current User in Views
```python
def get_queryset(self):
    # Access authenticated user
    user = self.request.user
    
    # Check if authenticated
    if user.is_authenticated:
        return Profile.objects.filter(user=user)
    return Profile.objects.none()

def perform_create(self, serializer):
    # Save with current user
    serializer.save(user=self.request.user)
```

---

## 📚 Swagger/API Documentation

### Current Setup ✅

Your Swagger is configured with JWT Bearer authentication:

```python
# hyrind/settings.py
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}
```

### How to Use Authentication in Swagger

#### Step 1: Access Swagger UI
```
http://127.0.0.1:8000/swagger/
```

#### Step 2: Get JWT Token
1. Scroll to **POST /api/users/login/**
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "email": "user@example.com",
     "password": "yourpassword"
   }
   ```
4. Click "Execute"
5. Copy the `access` token from response:
   ```json
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }
   ```

#### Step 3: Authorize in Swagger
1. Click the **🔓 Authorize** button (top right)
2. Enter: `Bearer <your_access_token>`
   ```
   Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```
3. Click "Authorize"
4. Click "Close"

#### Step 4: Use Protected Endpoints
Now all your API calls will include the JWT token automatically! 🎉

### Adding Swagger Documentation to Views

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class MyProtectedView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get list of items (requires authentication)",
        operation_summary="List Items",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search query",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response('Success', MySerializer(many=True)),
            401: 'Unauthorized - Invalid or missing token',
            403: 'Forbidden - Insufficient permissions'
        },
        security=[{'Bearer': []}],  # Shows lock icon in Swagger
        tags=['My API Section']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
```

---

## 🧪 Testing with Postman/cURL

### 1. Get JWT Token

**cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Use Token in Requests

**cURL with Token:**
```bash
curl -X GET http://127.0.0.1:8000/api/users/profiles/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Postman:**
1. Create new request
2. Go to "Authorization" tab
3. Type: "Bearer Token"
4. Token: Paste your access token
5. Send request

### 3. Refresh Token (When Expired)

**cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Response:**
```json
{
  "access": "new_access_token_here..."
}
```

---

## 🎯 Quick Reference: Your Current Endpoints

### Public Endpoints (No Auth)
```
POST /api/users/register/          - Register new user
POST /api/users/login/             - Login (get JWT tokens)
POST /api/users/interest/          - Submit interest form
POST /api/users/contact/           - Contact form
POST /api/recruiters/register/     - Register recruiter
```

### Protected Endpoints (Require Auth)
```
GET    /api/users/                 - List users
GET    /api/users/profiles/        - List profiles
GET    /api/users/profiles/{id}/   - Get profile details
PUT    /api/users/profiles/{id}/   - Update profile
DELETE /api/users/profiles/{id}/   - Delete profile
```

### Admin-Only Endpoints
```
GET    /api/recruiters/            - List recruiters (admin sees all)
GET    /api/recruiters/{id}/       - Recruiter details
PUT    /api/recruiters/{id}/       - Update recruiter
DELETE /api/recruiters/{id}/       - Delete recruiter
```

---

## 💡 Best Practices

1. **Token Expiration**: Access tokens expire quickly (default: 5 minutes)
   - Store refresh token securely
   - Auto-refresh when access token expires

2. **Security**:
   - Never commit tokens to git
   - Use HTTPS in production
   - Rotate refresh tokens periodically

3. **Error Handling**:
   - 401 Unauthorized: Token missing/invalid
   - 403 Forbidden: Token valid but insufficient permissions

4. **Frontend Integration**:
   ```javascript
   // Store tokens
   localStorage.setItem('access_token', response.data.access);
   localStorage.setItem('refresh_token', response.data.refresh);
   
   // Use in requests
   axios.get('/api/users/profiles/', {
     headers: {
       'Authorization': `Bearer ${localStorage.getItem('access_token')}`
     }
   });
   ```

---

## 📝 Summary

✅ **Your serializers are excellent** - well-validated, consistent, and follow best practices

✅ **JWT is properly configured** - using djangorestframework-simplejwt

✅ **Swagger has auth support** - Bearer token configuration in place

✅ **Permission classes** - Use `IsAuthenticated`, `IsAdminUser`, or `AllowAny` as needed

🎯 **To protect a route**: Just add `permission_classes = [permissions.IsAuthenticated]`

🔐 **To use in Swagger**: Get token from login → Click Authorize → Enter "Bearer <token>"

---

Need help with anything specific? 🚀
