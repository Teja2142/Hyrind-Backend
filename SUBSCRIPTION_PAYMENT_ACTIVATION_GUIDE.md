# Subscription Payment & Activation Guide

## Table of Contents
- [Overview](#overview)
- [Complete Payment Flow](#complete-payment-flow)
- [API Classification](#api-classification)
- [Step-by-Step Guide](#step-by-step-guide)
- [All API Endpoints](#all-api-endpoints)
- [CURL Examples with Sample Data](#curl-examples-with-sample-data)
- [Common Use Cases](#common-use-cases)
- [Error Handling](#error-handling)

---

## Overview

The subscription system has **2 types of plans**:
1. **Base Subscription** - Mandatory for all users ($400/month)
2. **Add-on Services** - Optional services with admin-controlled pricing

### Payment Flow
```
Step 1: User browses plans (PUBLIC API)
   ↓
Step 2: Frontend initiates Razorpay payment
   ↓
Step 3: User completes payment on Razorpay
   ↓
Step 4: Frontend receives razorpay_payment_id & razorpay_order_id
   ↓
Step 5: Frontend creates subscription record (USER API)
   ↓
Step 6: Frontend activates subscription with payment IDs (USER API)
   ↓
Step 7: Subscription is now ACTIVE ✓
```

---

## API Classification

### 🌐 PUBLIC APIs (No Authentication Required)
These APIs can be accessed without login:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/subscriptions/plans/` | GET | List all available plans |
| `/api/subscriptions/plans/{id}/` | GET | Get specific plan details |
| `/api/subscriptions/plans/base_plan/` | GET | Get mandatory base plan |
| `/api/subscriptions/plans/addons/` | GET | Get all add-on plans |

### 👤 USER APIs (Requires Authentication)
These APIs require JWT token in Authorization header:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/subscriptions/my-subscriptions/` | GET | List user's subscriptions |
| `/api/subscriptions/my-subscriptions/` | POST | Create subscription after payment |
| `/api/subscriptions/my-subscriptions/{id}/` | GET | Get subscription details |
| `/api/subscriptions/my-subscriptions/{id}/` | PATCH | Update subscription |
| `/api/subscriptions/my-subscriptions/{id}/activate/` | POST | **Activate after payment** |
| `/api/subscriptions/my-subscriptions/{id}/cancel/` | POST | Cancel subscription |
| `/api/subscriptions/my-subscriptions/summary/` | GET | Get subscription summary |
| `/api/subscriptions/billing-history/` | GET | View payment history |

### 🔧 ADMIN APIs (Django Admin Panel)
Access at: `http://127.0.0.1:8000/admin/subscriptions/`

| Section | Purpose |
|---------|---------|
| Subscription Plans | Create/edit/delete plans, set pricing |
| User Subscriptions | View all subscriptions, customize pricing per user |
| Billing History | View all transactions, export to CSV |

**Admin Actions:**
- Create new subscription plans
- Set base prices for add-ons
- Override prices for specific users
- Activate/deactivate plans
- View revenue reports
- Export billing data

---

## Complete Payment Flow

### Step 1: Browse Available Plans (PUBLIC)

**Frontend calls:**
```bash
GET /api/subscriptions/plans/
```

**User sees:**
- Base plan: $400/month (mandatory)
- Add-on 1: Skill Development Training - $150/month
- Add-on 2: Premium Job Matching - $200/month
- Add-on 3: Career Mentorship - $250/month
- Add-on 4: Certification Assistance - $100/month

---

### Step 2: User Selects Plans & Initiates Payment

**User selects:**
- Base plan (mandatory): $400
- Add-on: Career Mentorship: $250
- **Total: $650**

**Frontend:**
1. Creates Razorpay order with amount $650
2. Opens Razorpay payment modal
3. User completes payment

---

### Step 3: Payment Success - Razorpay Returns IDs

**Razorpay returns:**
```json
{
  "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
  "razorpay_order_id": "order_NaXv5j2u1wInq1",
  "razorpay_signature": "signature_here"
}
```

---

### Step 4: Create Subscription Records (USER API)

**Frontend creates 2 subscriptions** (one for base, one for add-on):

**Request 1: Create Base Subscription**
```bash
POST /api/subscriptions/my-subscriptions/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "plan": "uuid-of-base-plan",
  "price": "400.00"
}
```

**Response:**
```json
{
  "id": "sub-uuid-1",
  "plan": {
    "id": "plan-uuid-base",
    "name": "Profile Marketing Services Fee",
    "plan_type": "base",
    "base_price": "400.00"
  },
  "price": "400.00",
  "status": "inactive",
  "started_at": null,
  "next_billing_date": null
}
```

**Request 2: Create Add-on Subscription**
```bash
POST /api/subscriptions/my-subscriptions/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "plan": "uuid-of-mentorship-addon",
  "price": "250.00"
}
```

**Response:**
```json
{
  "id": "sub-uuid-2",
  "plan": {
    "id": "plan-uuid-mentorship",
    "name": "Career Mentorship Program",
    "plan_type": "addon",
    "base_price": "250.00"
  },
  "price": "250.00",
  "status": "inactive",
  "started_at": null,
  "next_billing_date": null
}
```

---

### Step 5: Activate Subscriptions (USER API)

**⚠️ CRITICAL: This is where payment is confirmed and subscriptions become active**

**For Base Subscription:**
```bash
POST /api/subscriptions/my-subscriptions/sub-uuid-1/activate/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
  "razorpay_order_id": "order_NaXv5j2u1wInq1",
  "amount": "400.00"
}
```

**Response:**
```json
{
  "id": "sub-uuid-1",
  "plan": {
    "id": "plan-uuid-base",
    "name": "Profile Marketing Services Fee",
    "plan_type": "base",
    "base_price": "400.00"
  },
  "price": "400.00",
  "status": "active",
  "razorpay_subscription_id": "pay_NaXv5j2u1wInq1",
  "started_at": "2025-12-20T10:30:00Z",
  "next_billing_date": "2026-01-20",
  "billing_history": [
    {
      "id": "bill-uuid-1",
      "amount": "400.00",
      "status": "success",
      "description": "Subscription activated: Profile Marketing Services Fee",
      "created_at": "2025-12-20T10:30:00Z"
    }
  ]
}
```

**For Add-on Subscription:**
```bash
POST /api/subscriptions/my-subscriptions/sub-uuid-2/activate/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
  "razorpay_order_id": "order_NaXv5j2u1wInq1",
  "amount": "250.00"
}
```

**Response:**
```json
{
  "id": "sub-uuid-2",
  "plan": {
    "id": "plan-uuid-mentorship",
    "name": "Career Mentorship Program",
    "plan_type": "addon",
    "base_price": "250.00"
  },
  "price": "250.00",
  "status": "active",
  "razorpay_subscription_id": "pay_NaXv5j2u1wInq1",
  "started_at": "2025-12-20T10:30:01Z",
  "next_billing_date": "2026-01-20",
  "billing_history": [
    {
      "id": "bill-uuid-2",
      "amount": "250.00",
      "status": "success",
      "description": "Subscription activated: Career Mentorship Program",
      "created_at": "2025-12-20T10:30:01Z"
    }
  ]
}
```

---

## Step-by-Step Guide

### How to Activate a Subscription After Payment

#### Option A: Create → Activate (Recommended)

**1. Create subscription record first:**
```bash
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "plan-uuid-here",
    "price": "400.00"
  }'
```

**2. User completes Razorpay payment**

**3. Activate with payment details:**
```bash
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/SUBSCRIPTION_ID/activate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1",
    "amount": "400.00"
  }'
```

#### Option B: Using Webhook (Alternative)

If you prefer server-to-server communication:

```bash
curl -X POST http://127.0.0.1:8000/api/subscriptions/webhook/payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_id": "sub-uuid-here",
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1",
    "amount": "400.00",
    "status": "success"
  }'
```

---

## All API Endpoints

### 1. List All Plans (PUBLIC)

**GET** `/api/subscriptions/plans/`

**Purpose:** Browse all available subscription plans

**Authentication:** None required

**CURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/subscriptions/plans/
```

**Response:**
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Profile Marketing Services Fee",
    "plan_type": "base",
    "description": "Mandatory base subscription for all users",
    "base_price": "400.00",
    "is_mandatory": true,
    "is_active": true,
    "billing_cycle": "monthly",
    "features": [
      "Profile visibility on platform",
      "Basic job matching",
      "Email notifications"
    ],
    "created_at": "2025-12-15T10:00:00Z"
  },
  {
    "id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
    "name": "Skill Development Training",
    "plan_type": "addon",
    "description": "Access to skill development courses and workshops",
    "base_price": "150.00",
    "is_mandatory": false,
    "is_active": true,
    "billing_cycle": "monthly",
    "features": [
      "Access to 100+ courses",
      "Live workshops",
      "Certification exams"
    ],
    "created_at": "2025-12-15T10:05:00Z"
  }
]
```

**Query Parameters:**
- `?type=base` - Filter for base plan only
- `?type=addon` - Filter for add-ons only

---

### 2. Get Base Plan (PUBLIC)

**GET** `/api/subscriptions/plans/base_plan/`

**Purpose:** Get the mandatory base subscription

**Authentication:** None required

**CURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/subscriptions/plans/base_plan/
```

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Profile Marketing Services Fee",
  "plan_type": "base",
  "description": "Mandatory base subscription for all users",
  "base_price": "400.00",
  "is_mandatory": true,
  "is_active": true,
  "billing_cycle": "monthly",
  "features": [
    "Profile visibility on platform",
    "Basic job matching",
    "Email notifications"
  ]
}
```

---

### 3. Get Add-on Plans (PUBLIC)

**GET** `/api/subscriptions/plans/addons/`

**Purpose:** Get all available add-on services

**Authentication:** None required

**CURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/subscriptions/plans/addons/
```

**Response:**
```json
[
  {
    "id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
    "name": "Skill Development Training",
    "plan_type": "addon",
    "base_price": "150.00",
    "features": ["100+ courses", "Live workshops"]
  },
  {
    "id": "c3d4e5f6-g7h8-9012-cdef-g23456789012",
    "name": "Premium Job Matching",
    "plan_type": "addon",
    "base_price": "200.00",
    "features": ["AI-powered matching", "Priority applications"]
  }
]
```

---

### 4. List My Subscriptions (USER)

**GET** `/api/subscriptions/my-subscriptions/`

**Purpose:** View all your active and past subscriptions

**Authentication:** Required (JWT Token)

**CURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/subscriptions/my-subscriptions/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
[
  {
    "id": "sub-12345678-1234-1234-1234-123456789012",
    "plan": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Profile Marketing Services Fee",
      "plan_type": "base",
      "base_price": "400.00"
    },
    "price": "400.00",
    "status": "active",
    "razorpay_subscription_id": "pay_NaXv5j2u1wInq1",
    "billing_cycle": "monthly",
    "next_billing_date": "2026-01-20",
    "started_at": "2025-12-20T10:30:00Z",
    "ended_at": null,
    "total_paid": "400.00",
    "billing_history": [
      {
        "id": "bill-uuid-1",
        "amount": "400.00",
        "status": "success",
        "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
        "razorpay_order_id": "order_NaXv5j2u1wInq1",
        "description": "Subscription activated: Profile Marketing Services Fee",
        "created_at": "2025-12-20T10:30:00Z"
      }
    ]
  },
  {
    "id": "sub-23456789-2345-2345-2345-234567890123",
    "plan": {
      "id": "c3d4e5f6-g7h8-9012-cdef-g23456789012",
      "name": "Career Mentorship Program",
      "plan_type": "addon",
      "base_price": "250.00"
    },
    "price": "250.00",
    "status": "active",
    "razorpay_subscription_id": "pay_NaXv5j2u1wInq1",
    "billing_cycle": "monthly",
    "next_billing_date": "2026-01-20",
    "started_at": "2025-12-20T10:30:01Z",
    "ended_at": null,
    "total_paid": "250.00"
  }
]
```

---

### 5. Create Subscription (USER)

**POST** `/api/subscriptions/my-subscriptions/`

**Purpose:** Create a new subscription record (call AFTER payment succeeds)

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "plan": "plan-uuid-here",
  "price": "400.00"
}
```

**CURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "price": "400.00"
  }'
```

**Response:**
```json
{
  "id": "sub-12345678-1234-1234-1234-123456789012",
  "plan": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Profile Marketing Services Fee",
    "plan_type": "base",
    "base_price": "400.00"
  },
  "price": "400.00",
  "status": "inactive",
  "billing_cycle": "monthly",
  "started_at": null,
  "next_billing_date": null,
  "created_at": "2025-12-20T10:29:00Z"
}
```

**Validation:**
- Plan must exist and be active
- User cannot have duplicate active subscriptions for same plan
- Price must be positive

---

### 6. Activate Subscription (USER) ⭐ MOST IMPORTANT

**POST** `/api/subscriptions/my-subscriptions/{id}/activate/`

**Purpose:** Activate subscription after successful payment

**Authentication:** Required (JWT Token)

**⚠️ This is the KEY endpoint that makes a subscription active!**

**Request Body:**
```json
{
  "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
  "razorpay_order_id": "order_NaXv5j2u1wInq1",
  "amount": "400.00"
}
```

**CURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/sub-12345678-1234-1234-1234-123456789012/activate/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1",
    "amount": "400.00"
  }'
```

**Response:**
```json
{
  "id": "sub-12345678-1234-1234-1234-123456789012",
  "plan": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Profile Marketing Services Fee",
    "plan_type": "base",
    "base_price": "400.00"
  },
  "price": "400.00",
  "status": "active",
  "razorpay_subscription_id": "pay_NaXv5j2u1wInq1",
  "billing_cycle": "monthly",
  "next_billing_date": "2026-01-20",
  "started_at": "2025-12-20T10:30:00Z",
  "ended_at": null,
  "total_paid": "400.00",
  "billing_history": [
    {
      "id": "bill-uuid-1",
      "amount": "400.00",
      "status": "success",
      "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
      "razorpay_order_id": "order_NaXv5j2u1wInq1",
      "description": "Subscription activated: Profile Marketing Services Fee",
      "created_at": "2025-12-20T10:30:00Z"
    }
  ]
}
```

**What happens when you activate:**
1. Status changes from `inactive` → `active`
2. `started_at` timestamp is set
3. `next_billing_date` is calculated (30 days from now)
4. `razorpay_subscription_id` is saved
5. Billing history record is created
6. Audit log is created

---

### 7. Cancel Subscription (USER)

**POST** `/api/subscriptions/my-subscriptions/{id}/cancel/`

**Purpose:** Cancel an active subscription

**Authentication:** Required (JWT Token)

**CURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/sub-12345678-1234-1234-1234-123456789012/cancel/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "id": "sub-12345678-1234-1234-1234-123456789012",
  "status": "cancelled",
  "ended_at": "2025-12-20T15:30:00Z"
}
```

**What happens when you cancel:**
1. Status changes to `cancelled`
2. `ended_at` timestamp is set
3. Subscription stops renewing
4. Audit log is created

---

### 8. Get Subscription Summary (USER)

**GET** `/api/subscriptions/my-subscriptions/summary/`

**Purpose:** Get dashboard overview of all subscriptions

**Authentication:** Required (JWT Token)

**CURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/subscriptions/my-subscriptions/summary/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
{
  "total_subscriptions": 2,
  "active_subscriptions": 2,
  "monthly_cost": "650.00",
  "next_billing_date": "2026-01-20",
  "base_subscription": {
    "id": "sub-12345678-1234-1234-1234-123456789012",
    "plan": {
      "name": "Profile Marketing Services Fee",
      "base_price": "400.00"
    },
    "price": "400.00",
    "status": "active",
    "next_billing_date": "2026-01-20"
  },
  "addons": [
    {
      "id": "sub-23456789-2345-2345-2345-234567890123",
      "plan": {
        "name": "Career Mentorship Program",
        "base_price": "250.00"
      },
      "price": "250.00",
      "status": "active",
      "next_billing_date": "2026-01-20"
    }
  ]
}
```

---

### 9. View Billing History (USER)

**GET** `/api/subscriptions/billing-history/`

**Purpose:** View all payment transactions

**Authentication:** Required (JWT Token)

**CURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/subscriptions/billing-history/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
[
  {
    "id": "bill-uuid-1",
    "user_subscription": {
      "id": "sub-12345678-1234-1234-1234-123456789012",
      "plan_name": "Profile Marketing Services Fee"
    },
    "amount": "400.00",
    "status": "success",
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1",
    "description": "Subscription activated: Profile Marketing Services Fee",
    "created_at": "2025-12-20T10:30:00Z"
  },
  {
    "id": "bill-uuid-2",
    "user_subscription": {
      "id": "sub-23456789-2345-2345-2345-234567890123",
      "plan_name": "Career Mentorship Program"
    },
    "amount": "250.00",
    "status": "success",
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1",
    "description": "Subscription activated: Career Mentorship Program",
    "created_at": "2025-12-20T10:30:01Z"
  }
]
```

---

### 10. Payment Webhook (NO AUTH)

**POST** `/api/subscriptions/webhook/payment/`

**Purpose:** Alternative way to activate subscription (server-to-server)

**Authentication:** None (webhook endpoint)

**Request Body:**
```json
{
  "subscription_id": "sub-12345678-1234-1234-1234-123456789012",
  "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
  "razorpay_order_id": "order_NaXv5j2u1wInq1",
  "amount": "400.00",
  "status": "success"
}
```

**CURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/subscriptions/webhook/payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_id": "sub-12345678-1234-1234-1234-123456789012",
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1",
    "amount": "400.00",
    "status": "success"
  }'
```

**Response:**
```json
{
  "message": "Payment processed successfully",
  "subscription": {
    "id": "sub-12345678-1234-1234-1234-123456789012",
    "status": "active",
    "started_at": "2025-12-20T10:30:00Z"
  },
  "billing": {
    "id": "bill-uuid-1",
    "amount": "400.00",
    "status": "success",
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1"
  }
}
```

---

## Common Use Cases

### Use Case 1: New User Signs Up

**Flow:**
1. User registers → Gets JWT token
2. Frontend fetches base plan: `GET /api/subscriptions/plans/base_plan/`
3. Frontend creates Razorpay order for $400
4. User pays via Razorpay
5. Frontend creates subscription: `POST /api/subscriptions/my-subscriptions/`
6. Frontend activates: `POST /api/subscriptions/my-subscriptions/{id}/activate/`

**Complete CURL Sequence:**
```bash
# Step 1: Get base plan details
curl -X GET http://127.0.0.1:8000/api/subscriptions/plans/base_plan/

# Step 2: User pays $400 on Razorpay (frontend handles this)
# Razorpay returns: pay_NaXv5j2u1wInq1, order_NaXv5j2u1wInq1

# Step 3: Create subscription
SUBSCRIPTION_RESPONSE=$(curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "price": "400.00"
  }')

SUBSCRIPTION_ID=$(echo $SUBSCRIPTION_RESPONSE | jq -r '.id')

# Step 4: Activate subscription
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/$SUBSCRIPTION_ID/activate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_NaXv5j2u1wInq1",
    "razorpay_order_id": "order_NaXv5j2u1wInq1",
    "amount": "400.00"
  }'
```

---

### Use Case 2: User Adds Add-on Service

**Flow:**
1. User browses add-ons: `GET /api/subscriptions/plans/addons/`
2. User selects "Career Mentorship" - $250
3. Frontend creates Razorpay order for $250
4. User pays
5. Frontend creates subscription + activates

**Complete CURL Sequence:**
```bash
# Step 1: Browse add-ons
curl -X GET http://127.0.0.1:8000/api/subscriptions/plans/addons/

# Step 2: User pays $250 on Razorpay
# Razorpay returns: pay_AbCd123456, order_AbCd123456

# Step 3: Create subscription
ADDON_RESPONSE=$(curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "c3d4e5f6-g7h8-9012-cdef-g23456789012",
    "price": "250.00"
  }')

ADDON_ID=$(echo $ADDON_RESPONSE | jq -r '.id')

# Step 4: Activate add-on
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/$ADDON_ID/activate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_AbCd123456",
    "razorpay_order_id": "order_AbCd123456",
    "amount": "250.00"
  }'
```

---

### Use Case 3: User Cancels Add-on

**Flow:**
1. User views subscriptions: `GET /api/subscriptions/my-subscriptions/`
2. User cancels unwanted add-on: `POST /api/subscriptions/my-subscriptions/{id}/cancel/`

**Complete CURL Sequence:**
```bash
# Step 1: List subscriptions
curl -X GET http://127.0.0.1:8000/api/subscriptions/my-subscriptions/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Step 2: Cancel specific add-on
curl -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/sub-23456789-2345-2345-2345-234567890123/cancel/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

### Use Case 4: Admin Customizes Pricing

**Flow:**
1. Admin logs into Django admin: `http://127.0.0.1:8000/admin/`
2. Navigates to "User Subscriptions"
3. Finds user's subscription
4. Changes price from $250 to $200
5. Saves

**Next billing cycle charges $200 instead of $250**

---

### Use Case 5: View Dashboard Summary

**Flow:**
1. User logs in
2. Dashboard calls: `GET /api/subscriptions/my-subscriptions/summary/`
3. Shows:
   - Total monthly cost: $650
   - Base plan: Active
   - Add-ons: 1 active
   - Next billing: Jan 20, 2026

**CURL Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/subscriptions/my-subscriptions/summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Error Handling

### Common Errors

#### 1. Unauthorized (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Solution:** Include JWT token in Authorization header

#### 2. Duplicate Active Subscription (400)
```json
{
  "non_field_errors": [
    "User already has an active subscription for this plan"
  ]
}
```
**Solution:** User already has this plan active

#### 3. Plan Not Found (404)
```json
{
  "error": "Subscription plan not found"
}
```
**Solution:** Use valid plan UUID

#### 4. Invalid Price (400)
```json
{
  "price": [
    "Ensure this value is greater than or equal to 0.00"
  ]
}
```
**Solution:** Price must be positive

#### 5. Already Active (200)
```json
{
  "message": "Subscription is already active"
}
```
**Solution:** Subscription was already activated

#### 6. Missing Payment Details (400)
```json
{
  "error": "Missing required fields: subscription_id, razorpay_payment_id, amount"
}
```
**Solution:** Include all required fields in activation request

---

## Testing with Sample Data

### Get Actual Plan UUIDs

```bash
# Get all plans
curl -X GET http://127.0.0.1:8000/api/subscriptions/plans/

# Note down the UUIDs from response
# BASE_PLAN_ID = "a1b2c3d4-..."
# ADDON_PLAN_ID = "b2c3d4e5-..."
```

### Complete Test Flow

```bash
# 1. Get JWT token (login first)
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# 2. Get base plan
BASE_PLAN=$(curl -s -X GET http://127.0.0.1:8000/api/subscriptions/plans/base_plan/)
BASE_PLAN_ID=$(echo $BASE_PLAN | jq -r '.id')

# 3. Create subscription
CREATE_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"plan\": \"$BASE_PLAN_ID\",
    \"price\": \"400.00\"
  }")

SUB_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
echo "Created subscription: $SUB_ID"

# 4. Simulate Razorpay payment (in real app, user pays on Razorpay)
PAYMENT_ID="pay_TEST123456789"
ORDER_ID="order_TEST123456789"

# 5. Activate subscription
ACTIVATE_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/subscriptions/my-subscriptions/$SUB_ID/activate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"razorpay_payment_id\": \"$PAYMENT_ID\",
    \"razorpay_order_id\": \"$ORDER_ID\",
    \"amount\": \"400.00\"
  }")

echo "Activation response:"
echo $ACTIVATE_RESPONSE | jq '.'

# 6. View summary
curl -s -X GET http://127.0.0.1:8000/api/subscriptions/my-subscriptions/summary/ \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 7. View billing history
curl -s -X GET http://127.0.0.1:8000/api/subscriptions/billing-history/ \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## Frontend Integration Example (React)

```javascript
// Step 1: Create subscription record
const createSubscription = async (planId, price) => {
  const response = await fetch('http://127.0.0.1:8000/api/subscriptions/my-subscriptions/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      plan: planId,
      price: price
    })
  });
  return await response.json();
};

// Step 2: Initialize Razorpay payment
const initiatePayment = (subscriptionId, amount) => {
  const options = {
    key: 'YOUR_RAZORPAY_KEY',
    amount: amount * 100, // Razorpay expects paise
    currency: 'USD',
    name: 'Hyrind Platform',
    description: 'Subscription Payment',
    handler: async function(response) {
      // Step 3: Activate subscription after payment
      await activateSubscription(
        subscriptionId,
        response.razorpay_payment_id,
        response.razorpay_order_id,
        amount
      );
    }
  };
  
  const rzp = new Razorpay(options);
  rzp.open();
};

// Step 3: Activate subscription
const activateSubscription = async (subId, paymentId, orderId, amount) => {
  const response = await fetch(
    `http://127.0.0.1:8000/api/subscriptions/my-subscriptions/${subId}/activate/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        razorpay_payment_id: paymentId,
        razorpay_order_id: orderId,
        amount: amount
      })
    }
  );
  
  const data = await response.json();
  console.log('Subscription activated:', data);
  return data;
};

// Complete flow
const subscribeToPlans = async (planId, price) => {
  try {
    // 1. Create subscription
    const subscription = await createSubscription(planId, price);
    console.log('Subscription created:', subscription.id);
    
    // 2. Initiate payment
    initiatePayment(subscription.id, price);
    
    // 3. Activation happens in payment handler
  } catch (error) {
    console.error('Subscription error:', error);
  }
};
```

---

## Summary

### Key Points

1. **PUBLIC APIs (No Auth):**
   - Browse plans
   - Get base plan
   - Get add-ons

2. **USER APIs (Require JWT):**
   - Create subscription
   - **Activate subscription** (most important!)
   - Cancel subscription
   - View subscriptions
   - View billing history
   - Get summary

3. **ADMIN APIs (Django Admin Panel):**
   - Create/edit plans
   - Customize pricing per user
   - View all subscriptions
   - Export billing data

4. **Payment Flow:**
   - User pays on Razorpay
   - Frontend creates subscription
   - Frontend activates with payment IDs
   - Subscription becomes active

5. **Critical Fields:**
   - `razorpay_payment_id` - Required for activation
   - `razorpay_order_id` - Required for activation
   - `amount` - Payment amount
   - `status` - inactive → active → cancelled

---

## Questions?

For any issues or clarifications, check:
- Server: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/
- API Docs: http://127.0.0.1:8000/api/subscriptions/

**Need help?** Contact the backend team with:
- API endpoint used
- Request body
- Response received
- Error message (if any)
