# Admin APIs - Complete Implementation Guide

## Overview
The Hyrind backend now supports a complete admin workflow including registration, authentication, and profile management. All admin endpoints require JWT token authentication.

---

## 1. Admin Registration API

**Endpoint:** `POST /api/users/admin/register/`

**Permission:** Admin only (must be authenticated as an admin/staff user)

**Request Body:**
```json
{
  "email": "newidmin@hyrind.com",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "is_staff": true,
  "is_superuser": false
}
```

**Response (201 Created):**
```json
{
  "id": 15,
  "email": "newadmin@hyrind.com",
  "is_staff": true,
  "is_superuser": false
}
```

**Notes:**
- Only superusers can create other superusers
- All new admins are created with `is_active=True` and `is_staff=True`
- A Profile object is automatically created for each admin user
- Emails must be unique

---

## 2. Admin Login API

**Endpoint:** `POST /api/admin/login/`

**Permission:** Public (AllowAny)

**Request Body:**
```json
{
  "username": "newadmin@hyrind.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Usage:**
- Include the `access` token in the `Authorization: Bearer <token>` header for subsequent authenticated requests
- Use the `refresh` token to obtain new access tokens when they expire

---

## 3. Get Admin Profile API

**Endpoint:** `GET /api/users/admin/profile/`

**Permission:** Admin only (requires JWT token)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "0c244127-20e8-4a03-831e-e4953fbaaeaa",
  "user": {
    "id": 15,
    "email": "newadmin@hyrind.com"
  },
  "first_name": "John",
  "last_name": "Doe",
  "email": "newadmin@hyrind.com",
  "phone": null,
  "active": true,
  "university": null,
  "degree": null,
  "major": null,
  "visa_status": null,
  "graduation_date": null,
  "opt_end_date": null,
  "resume_file": null,
  "consent_to_terms": false,
  "referral_source": null,
  "linkedin_url": null,
  "github_url": null,
  "additional_notes": null,
  "_created_profile": false
}
```

**Notes:**
- Returns the authenticated admin's profile
- If no profile exists, one is automatically created
- Includes a `_created_profile` flag if the profile was just created

---

## 4. Admin Password Change API

**Endpoint:** `POST /api/users/admin/password/`

**Permission:** Admin only (requires JWT token)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "CurrentPassword123!",
  "new_password": "NewPassword456!",
  "confirm_password": "NewPassword456!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

## 5. Activate Candidate API

**Endpoint:** `PATCH /api/users/admin/candidates/<profile_id>/activate/`

**Permission:** Admin only (requires JWT token)

**Response (200 OK):**
```json
{
  "message": "Candidate activated successfully",
  "profile": { /* profile object */ }
}
```

---

## 6. Deactivate Candidate API

**Endpoint:** `PATCH /api/users/admin/candidates/<profile_id>/deactivate/`

**Permission:** Admin only (requires JWT token)

**Response (200 OK):**
```json
{
  "message": "Candidate deactivated successfully",
  "profile": { /* profile object */ }
}
```

---

## Frontend Implementation Steps

### Step 1: Register a New Admin (Superuser/Admin only)
```javascript
POST /api/users/admin/register/
{
  "email": "admin@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "Admin",
  "last_name": "User",
  "is_staff": true,
  "is_superuser": false
}
```

### Step 2: Admin Login
```javascript
POST /api/admin/login/
{
  "username": "admin@example.com",
  "password": "password123"
}
```

Store the returned `access` token in localStorage or sessionStorage.

### Step 3: Fetch Admin Profile
```javascript
GET /api/users/admin/profile/
Headers: {
  "Authorization": "Bearer <access_token>"
}
```

### Step 4: Use the Access Token for All Subsequent Requests
```javascript
Headers: {
  "Authorization": "Bearer <access_token>"
}
```

---

## Error Handling

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Fix:** Ensure you're including the `Authorization: Bearer <token>` header.

### 403 Forbidden
```json
{
  "detail": "Admin credentials required."
}
```
**Fix:** Only admin/staff users can access these endpoints.

### 400 Bad Request
```json
{
  "email": ["A user with that email already exists."]
}
```
**Fix:** Use a unique email address or check validation errors.

---

## Testing

All admin APIs have been tested and verified to work correctly:
- ✅ Admin Registration: Creates new staff/superuser accounts
- ✅ Admin Login: Issues JWT tokens for authenticated admins
- ✅ Admin Profile Get: Returns authenticated admin's profile data

See `test_admin_apis.py` for the complete test suite.

---

## Database Schema

Admin users are stored in Django's native `User` model with:
- `is_staff = True` (indicates admin/staff user)
- `is_superuser = True/False` (indicates superuser privileges)
- `is_active = True` (allows login)

Each admin user has a corresponding `Profile` object with extended info:
- UUID primary key
- First/last name
- Email, phone
- Education and visa information (optional)
- Social media URLs (optional)
- Active flag (mirrors `User.is_active`)

---

## Security Notes

1. **Password Requirements:** Enforce strong passwords (min 8 chars, uppercase, number, special char)
2. **Token Expiry:** Access tokens expire after a configurable period (default: 5 minutes)
3. **Rate Limiting:** Consider adding rate limiting to `/api/admin/login/` to prevent brute force
4. **HTTPS:** Always use HTTPS in production to protect tokens
5. **Token Storage:** Store tokens in `httpOnly` cookies or secure localStorage
6. **Superuser Creation:** Only superusers can create other superusers via the API

---

## Swagger Documentation

Full API documentation is available at:
- `/swagger/` - Swagger UI
- `/redoc/` - ReDoc UI
- `/swagger.json` - OpenAPI schema

All admin endpoints are documented with request/response examples.
