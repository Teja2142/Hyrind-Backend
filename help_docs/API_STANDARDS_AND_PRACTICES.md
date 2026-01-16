# 🎯 API Standards & Best Practices Applied

## Overview

This document outlines the industry-standard practices applied to all APIs in the Hyrind platform, ensuring consistency, clarity, and developer experience.

---

## 📋 Standards Applied Across All APIs

### 1. **Clear Operation Naming**

Every endpoint has:
- **operation_summary**: What the API does (max 10 words)
- **operation_description**: Why/when to use it (2-3 sentences)
- **tags**: API category for organization

**Example**:
```python
@swagger_auto_schema(
    operation_summary="List all job postings",  # What
    operation_description="Retrieve active jobs with filtering and pagination",  # Why
    tags=['Jobs']  # Category
)
```

### 2. **RESTful HTTP Methods**

| Method | Purpose | Status Code |
|--------|---------|-------------|
| GET | Retrieve data | 200 |
| POST | Create resource | 201 |
| PATCH | Partial update | 200 |
| PUT | Full replace | 200 |
| DELETE | Remove resource | 204 |

**Applied to**:
- ✅ User profiles: GET/PATCH/DELETE
- ✅ Job postings: GET/POST/PATCH/DELETE
- ✅ Forms: GET/POST/PATCH
- ✅ Subscriptions: GET/POST/PATCH
- ✅ Onboarding: GET/PATCH

### 3. **Semantic Status Codes**

All endpoints return appropriate HTTP status codes:

```python
# Success
200 OK - GET, PATCH, PUT successful
201 Created - POST successful (resource created)
204 No Content - DELETE successful

# Client Errors
400 Bad Request - Invalid input data
401 Unauthorized - Missing/invalid auth token
403 Forbidden - Authenticated but no permission
404 Not Found - Resource doesn't exist
409 Conflict - Resource already exists (e.g., intake form)

# Server Errors
500 Internal Server Error - Unexpected server error
```

### 4. **Consistent Request/Response Format**

#### Success Response
```json
{
    "success": true,
    "message": "Operation successful",
    "data": { /* resource data */ },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Error message",
    "details": { /* specific errors */ },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### 5. **Authentication**

- **Type**: JWT (JSON Web Tokens)
- **Header**: `Authorization: Bearer <token>`
- **Endpoints**: Login endpoints return `access` and `refresh` tokens
- **Refresh**: Use `refresh` token to get new `access` token

**Applied to all protected endpoints**:
```python
permission_classes = [permissions.IsAuthenticated]
```

### 6. **Authorization Levels**

```python
# Public - Anyone
permission_classes = [AllowAny]

# Authenticated - Any logged-in user
permission_classes = [IsAuthenticated]

# Admin only
permission_classes = [IsAdminUser]

# Owner or Admin
# Custom permission check in view
```

---

## 🔍 API Categories

### User & Authentication APIs
- Register, login, password reset
- Profile management
- Current user info

### Form/Onboarding APIs
- Client intake sheet (CRUD)
- Credential sheet (CRUD)
- Form completion status
- Onboarding workflow tracking

### Recruiter APIs
- Recruiter registration & login
- Dashboard & assignments
- Client management

### Job APIs
- Job listings with search/filter
- Job details
- Job creation (recruiter/admin)
- Job updates/deletion

### Payment APIs
- Payment history
- Create payment orders
- Verify payments
- Webhook handling

### Subscription APIs
- List plans
- View user subscriptions
- Billing history
- Admin subscription management

### Admin APIs
- Candidate approval/rejection
- Candidate activation/deactivation
- Candidate placement marking
- User management
- Admin registration

---

## 📊 Swagger Documentation Details

### What's Documented for Each Endpoint

```python
@swagger_auto_schema(
    operation_summary="Clear 1-line description",
    operation_description="Why/when to use this endpoint. What problem does it solve.",
    request_body=SerializerClass,  # Shows expected input
    responses={
        200: SchemaObject,           # Success response
        400: 'Bad request error',    # Error responses
        401: 'Authentication error',
        403: 'Permission error',
        404: 'Not found error'
    },
    manual_parameters=[...],         # Query parameters
    tags=['Category']                # Organize in Swagger
)
```

### Documentation Locations

1. **Help Docs Folder**: Complete API guides
   - `help_docs/API_DOCUMENTATION_GUIDE.md` - Everything
   - `help_docs/CLIENT_FORMS_API.md` - Form details
   - `help_docs/CLIENT_FORMS_API_FIELD_VALIDATIONS.md` - Validations

2. **Swagger UI**: Interactive at `/swagger/`
   - Try-it-out feature for all endpoints
   - Shows live request/response examples
   - Automatic schema validation

3. **ReDoc**: Clean view at `/redoc/`
   - Non-interactive documentation
   - Organized by tags
   - Better for reading/sharing

4. **README.md**: Quick guide
   - Overview of key endpoints
   - Getting started section
   - Common workflows

---

## 🎓 For API Consumers (Frontend/Mobile)

### What They See in Swagger

1. **Endpoint Summary**: "List all job postings"
2. **Full Description**: "Retrieve a list of all active job postings with filtering and pagination"
3. **How to Use**:
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - See live response

### What They Learn from Docs

1. **What the API does**: Clear one-liner
2. **When to call it**: Use cases and workflows
3. **Why it exists**: Business logic/purpose
4. **How to handle errors**: Status codes and messages
5. **Request format**: Example JSON with descriptions
6. **Response format**: Example JSON with field descriptions

### Example: Client Intake Form API

**Swagger shows**:
- This API submits candidate information
- Required for recruiter matching
- Only authenticated users can submit
- Sends confirmation email automatically
- Returns form ID and submission timestamp

**Help docs show**:
- All 40+ fields with descriptions
- Field validation rules
- What happens after submission
- How to update (PATCH)
- Email template examples

---

## ✅ Best Practices Applied

### 1. **One Responsibility Per Endpoint**
- Create: POST /resource/
- List: GET /resource/
- Retrieve: GET /resource/{id}/
- Update: PATCH /resource/{id}/
- Delete: DELETE /resource/{id}/

### 2. **Logical Grouping**
- `/api/users/` - User operations
- `/api/recruiters/` - Recruiter operations
- `/api/jobs/` - Job operations
- `/api/payments/` - Payment operations
- `/api/subscriptions/` - Subscription operations

### 3. **Clear Error Messages**
```json
{
    "error": "Form already exists for this user",
    "message": "Use PATCH to update existing form",
    "form_id": "660e8400-e29b-41d4-a716-446655440001",
    "update_url": "/api/users/client-intake/660e8400-e29b-41d4-a716-446655440001/"
}
```

### 4. **Security**
- Never expose passwords in responses (masked as "••••••")
- JWT tokens required for protected operations
- Permission checks at view level
- Validation at serializer level
- CORS configured for frontend

### 5. **Pagination**
- Default page size: 10 items
- Includes `count`, `next`, `previous`, `results`
- Supports: `?page=2&page_size=20`

### 6. **Filtering & Search**
- `?search=keyword` - Full-text search
- `?status=approved` - Filter by field
- Supports multiple filters: `?status=approved&active=true`

### 7. **Error Handling**
- All endpoints return appropriate status codes
- Error messages are descriptive
- Validation errors list specific fields
- Server errors logged for debugging

---

## 🔄 Common Workflows Documented

### Candidate Registration Flow
1. Register → GET JWT
2. Submit intake form → Confirmation email
3. Submit credential sheet → Confirmation email
4. Check form status → All complete?
5. Make payment → Status updated
6. Admin activation → Ready for recruiter
7. Recruiter assignment → Start job matching

### Recruiter Job Posting Flow
1. Recruiter login → GET JWT
2. Create job → Job becomes searchable
3. Candidates apply → Assignment tracking
4. Update job → Job modified
5. Mark placement → Candidate placed

### Admin Candidate Management Flow
1. Admin login → GET JWT
2. View pending candidates → List with filters
3. Approve candidate → Status change + email
4. Monitor recruitment → Dashboard stats
5. Mark placement → Workflow complete

---

## 📈 Metrics & Monitoring

Each API endpoint provides:
- Operation name for logging
- Tags for categorization
- Status codes for success/failure
- Response time tracking
- Error rate monitoring

---

## 🚀 Future Enhancements

1. **API Versioning**: `/api/v1/`, `/api/v2/`
2. **Rate Limiting**: Prevent abuse
3. **API Keys**: For third-party integrations
4. **Webhooks**: Real-time event notifications
5. **GraphQL**: Alternative query language
6. **SDK**: Auto-generated client libraries

---

## 📞 Developer Support

### For Developers Using the API

1. **Start Here**: [API_DOCUMENTATION_GUIDE.md](API_DOCUMENTATION_GUIDE.md)
2. **Interactive Testing**: http://localhost:8000/swagger/
3. **Specific Guides**: Check `help_docs/` folder
4. **Code Examples**: curl, Postman, Python examples

### For API Maintainers

1. **Add Swagger**: Use `@swagger_auto_schema` decorator
2. **Document**: Add operation_summary and operation_description
3. **Validate**: Test in Swagger UI
4. **Update Docs**: Keep help_docs files current
5. **Release Notes**: Document API changes

---

## ✨ Summary

Every API in this system:
- ✅ Has clear naming (what it does)
- ✅ Has proper documentation (why/when to use)
- ✅ Uses REST conventions (GET/POST/PATCH/DELETE)
- ✅ Returns semantic status codes (200/201/400/401/403/404)
- ✅ Follows security best practices (JWT, permissions, validation)
- ✅ Provides error messages (clear, actionable)
- ✅ Is testable in Swagger (try-it-out feature)
- ✅ Is documented for developers (markdown guides)

---

**Last Updated**: January 16, 2026  
**API Version**: 1.0  
**Standards**: REST, JSON, JWT, OpenAPI 3.0
