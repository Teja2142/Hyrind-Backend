# 🧪 Quick Testing Guide - Recruiter APIs

## Prerequisites

```bash
# 1. Run migrations
python manage.py makemigrations
python manage.py migrate

# 2. Start the server
python manage.py runserver
```

---

## Test 1: View Homepage ✅

**Browser:** Navigate to:
```
http://127.0.0.1:8000/
```

**Expected Result:**
- Beautiful blue/white homepage with Hyrind logo
- 6 navigation cards visible
- Responsive design
- All buttons clickable

---

## Test 2: Register a Recruiter ✅

**Using Swagger UI:**
1. Go to: `http://127.0.0.1:8000/swagger/`
2. Find `POST /api/recruiters/register/`
3. Click "Try it out"
4. Enter test data:

```json
{
  "email": "test.recruiter@example.com",
  "password": "TestPass123!",
  "confirm_password": "TestPass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "company_name": "Elite Recruiters",
  "phone": "1234567890",
  "linkedin_url": "https://linkedin.com/in/janesmith"
}
```

**Expected Response (201):**
```json
{
  "message": "Recruiter registered successfully",
  "recruiter_id": 1,
  "email": "test.recruiter@example.com",
  "name": "Jane Smith - Elite Recruiters"
}
```

**Using cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/recruiters/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.recruiter@example.com",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!",
    "first_name": "Jane",
    "last_name": "Smith",
    "company_name": "Elite Recruiters",
    "phone": "1234567890",
    "linkedin_url": "https://linkedin.com/in/janesmith"
  }'
```

---

## Test 3: Login as Recruiter ✅

**Using Swagger UI:**
1. Find `POST /api/users/login/`
2. Click "Try it out"
3. Enter credentials:

```json
{
  "email": "test.recruiter@example.com",
  "password": "TestPass123!"
}
```

**Expected Response (200):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJh...",
  "access": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

**📋 Copy the `access` token for next tests!**

**Using cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.recruiter@example.com",
    "password": "TestPass123!"
  }'
```

---

## Test 4: List All Recruiters ✅

**Using Swagger UI:**
1. Click the 🔓 "Authorize" button at the top
2. Enter: `Bearer <your_access_token>`
3. Click "Authorize"
4. Find `GET /api/recruiters/`
5. Click "Try it out" → "Execute"

**Expected Response (200):**
```json
[
  {
    "id": 1,
    "name": "Jane Smith - Elite Recruiters",
    "email": "test.recruiter@example.com",
    "phone": "1234567890",
    "active": true,
    "total_assignments": 0
  }
]
```

**Using cURL:**
```bash
curl -X GET http://127.0.0.1:8000/api/recruiters/ \
  -H "Authorization: Bearer <your_access_token>"
```

---

## Test 5: Get Recruiter Details ✅

**Using Swagger UI:**
1. Find `GET /api/recruiters/{id}/`
2. Enter ID: `1`
3. Click "Execute"

**Expected Response (200):**
```json
{
  "id": 1,
  "user": 2,
  "user_email": "test.recruiter@example.com",
  "user_name": "Jane Smith",
  "name": "Jane Smith - Elite Recruiters",
  "email": "test.recruiter@example.com",
  "phone": "1234567890",
  "active": true
}
```

---

## Test 6: Update Recruiter (Admin Required) ✅

**First, create admin user:**
```bash
python manage.py createsuperuser
# Username: admin@example.com (use email as username)
# Email: admin@example.com
# Password: AdminPass123!
```

**Login as admin:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123!"
  }'
```

**Update recruiter:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/recruiters/1/ \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9876543210",
    "name": "Jane Smith - Updated Company"
  }'
```

**Expected Response (200):**
```json
{
  "id": 1,
  "name": "Jane Smith - Updated Company",
  "email": "test.recruiter@example.com",
  "phone": "9876543210",
  "active": true
}
```

---

## Test 7: Deactivate Recruiter (Admin Required) ✅

**Using Swagger UI (as admin):**
1. Authorize with admin token
2. Find `DELETE /api/recruiters/{id}/`
3. Enter ID: `1`
4. Click "Execute"

**Expected Response (204):**
```json
{
  "message": "Recruiter deactivated successfully"
}
```

**Verify deactivation:**
```bash
curl -X GET http://127.0.0.1:8000/api/recruiters/1/ \
  -H "Authorization: Bearer <token>"
```

**Expected:** `active` field should be `false`

---

## Test 8: Field Validations ✅

### Test Invalid Email:
```json
{
  "email": "invalid-email",
  ...
}
```
**Expected (400):** "Enter a valid email address."

### Test Password Mismatch:
```json
{
  "password": "Pass123!",
  "confirm_password": "DifferentPass123!",
  ...
}
```
**Expected (400):** "Passwords do not match."

### Test Weak Password:
```json
{
  "password": "123",
  "confirm_password": "123",
  ...
}
```
**Expected (400):** Password validation errors

### Test Invalid Phone:
```json
{
  "phone": "123",
  ...
}
```
**Expected (400):** "Phone must contain 10-12 digits only"

### Test Duplicate Email:
```json
{
  "email": "test.recruiter@example.com",  // Already exists
  ...
}
```
**Expected (400):** "A user with this email already exists."

---

## Test 9: Permission Tests ✅

### Test Update Without Admin (should fail):
```bash
# Login as regular recruiter (not admin)
TOKEN="<recruiter_token>"

curl -X PATCH http://127.0.0.1:8000/api/recruiters/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "1111111111"}'
```
**Expected (403):** "You do not have permission to perform this action."

### Test List Without Authentication (should fail):
```bash
curl -X GET http://127.0.0.1:8000/api/recruiters/
```
**Expected (401):** "Authentication credentials were not provided."

---

## Test 10: Admin Panel Access ✅

**Browser:** Navigate to:
```
http://127.0.0.1:8000/admin/
```

**Login with:**
- Username: `admin@example.com`
- Password: `AdminPass123!`

**Verify:**
- Can see Recruiters section
- Can view/edit recruiter records
- Can see assignments

---

## 📊 Test Results Checklist

Use this checklist to verify all tests pass:

- [ ] Homepage loads with beautiful blue/white design
- [ ] Recruiter registration succeeds with valid data
- [ ] Recruiter login returns JWT tokens
- [ ] List recruiters returns array of recruiters
- [ ] Get recruiter details returns full information
- [ ] Update recruiter works for admin users
- [ ] Delete recruiter sets active=false
- [ ] Invalid email returns 400 error
- [ ] Password mismatch returns 400 error
- [ ] Weak password returns 400 error
- [ ] Invalid phone returns 400 error
- [ ] Duplicate email returns 400 error
- [ ] Non-admin cannot update recruiters (403)
- [ ] Unauthenticated requests fail (401)
- [ ] Admin panel accessible and functional
- [ ] Swagger UI shows all endpoints
- [ ] All API documentation complete

---

## 🐛 Common Issues & Solutions

### Issue: "Authentication credentials were not provided"
**Solution:** Add `Authorization: Bearer <token>` header

### Issue: "You do not have permission"
**Solution:** Use admin token, or check if user is staff

### Issue: "Page not found"
**Solution:** Check URL (use `/api/recruiters/` not `/recruiters/`)

### Issue: CSRF token error
**Solution:** Disable CSRF for API endpoints (already configured)

### Issue: Template not found
**Solution:** Verify `templates/` directory exists and is in settings

---

## 📈 Performance Tests

### Test Response Times:
```bash
# Use -w flag to measure time
curl -w "@curl-format.txt" -o /dev/null -s \
  http://127.0.0.1:8000/api/recruiters/

# Create curl-format.txt:
echo "time_total: %{time_total}s\n" > curl-format.txt
```

**Expected:** < 100ms for simple queries

---

## 🎉 Success Criteria

All tests pass when:
1. ✅ All API endpoints return expected status codes
2. ✅ Authentication/authorization works correctly
3. ✅ Field validations catch invalid data
4. ✅ Homepage loads and looks professional
5. ✅ Swagger documentation is complete
6. ✅ Admin panel is accessible
7. ✅ No errors in console/logs

---

Happy Testing! 🚀
