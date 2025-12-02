
# Infield API Documentation

**Version:** v1
**Last Updated:** 2025-11-04
**Base URL:** `http://localhost:8000`

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Current Implementation Status](#current-implementation-status)
4. [Implemented Endpoints](#implemented-endpoints)
5. [Authentication APIs](#authentication-apis)
6. [User Management APIs](#user-management-apis)
7. [Form Management APIs](#form-management-apis)
8. [Submission APIs](#submission-apis)
9. [Data Models & Database Schema](#data-models--database-schema)
10. [Authentication & Authorization](#authentication--authorization)
11. [Multi-Tenancy Architecture](#multi-tenancy-architecture)
12. [Configuration](#configuration)
13. [Auto-Generated Documentation](#auto-generated-documentation)
14. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

Infield is a multi-tenant SaaS application for form management and approval workflows. It provides a comprehensive platform for creating custom forms, collecting submissions, and managing approval processes with role-based access control.

**Key Features:**
- Multi-tenant architecture with automatic tenant isolation
- JWT-based authentication with role-based permissions
- Dynamic form builder with 12+ field types
- Approval workflow management
- File upload support
- Comprehensive audit logging
- RESTful API design

**Project Location:** `/Users/riz/development/projects/form_app/infield_backend/`

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.109+ |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy (Async) | 2.0+ |
| Migrations | Alembic | Latest |
| Validation | Pydantic | 2.x |
| Authentication | JWT (python-jose) | Latest |
| Password Hashing | Argon2 (passlib) | Latest |
| Cache/Queue | Redis | Latest |
| Task Queue | Celery | Latest |
| HTTP Client | HTTPX (async) | Latest |
| Web Server | Uvicorn | Latest |
| Container | Docker | Latest |
| Python | 3.11+ | Required |

---

## Current Implementation Status

### ✅ Completed
- Complete database schema (11 models)
- Authentication infrastructure (JWT, Argon2 hashing)
- Multi-tenancy architecture with freemium pricing
- Configuration management
- Docker deployment setup
- Auto-generated API documentation (Swagger/ReDoc)
- Middleware and CORS configuration
- Comprehensive documentation
- **Authentication API endpoints** (register, login, refresh, me)
- **Tenant Management API** (self-service signup, tenant CRUD)
- **Form Management API** (complete CRUD with field management)
- **Service layer** (auth_service, tenant_service, form_service)
- **Plan limit enforcement** (user and form limits based on subscription tier)

### ❌ Pending Implementation
- User management API endpoints (invite, list, update, delete)
- Form submission API endpoints
- Role and permission management API
- File upload endpoints
- Background tasks (email notifications, reports)
- Unit and integration tests
- Payment integration for plan upgrades

**Implementation Progress:** ~60% Complete

---

## Implemented Endpoints

### 1. Health Check

Check the health status of the API.

**Endpoint:** `GET /health`
**Tags:** Health
**Authentication:** None required
**File Location:** `app/main.py:53-65`

**Response:**
```json
{
  "status": "healthy",
  "app": "Infield API",
  "version": "v1"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Root Endpoint

Get basic API information and available endpoints.

**Endpoint:** `GET /`
**Tags:** Root
**Authentication:** None required
**File Location:** `app/main.py:68-81`

**Response:**
```json
{
  "message": "Welcome to Infield API",
  "version": "v1",
  "docs": "/docs",
  "health": "/health"
}
```

**Status Codes:**
- `200 OK` - Success

---

## Authentication APIs

All authentication endpoints will be available under `/api/v1/auth`.

### 1. Register User

Register a new user account within an existing tenant.

**Endpoint:** `POST /api/v1/auth/register`
**Tags:** Authentication
**Authentication:** None required
**Status:** ✅ Implemented

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "designation": "Project Manager",
  "phone": "+1234567890",
  "tenant_id": 1
}
```

**Request Schema:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email format |
| password | string | Yes | Min 8 characters |
| full_name | string | No | Max 200 characters |
| designation | string | No | Max 100 characters |
| phone | string | No | Max 20 characters |
| tenant_id | integer | Yes | Valid tenant ID |

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `201 Created` - User successfully registered
- `400 Bad Request` - Invalid input data or tenant inactive
- `403 Forbidden` - User limit exceeded for tenant's plan
- `404 Not Found` - Tenant not found
- `409 Conflict` - Email already exists

**Business Logic:**
1. Validate email format and uniqueness
2. Check password strength (min 8 characters)
3. Verify tenant exists and is active
4. **Check tenant's user limit based on subscription plan**
5. Hash password using Argon2
6. Create user record in database
7. Generate JWT access and refresh tokens
8. Return tokens for immediate login

**File Location:** `app/api/v1/auth.py:42-67`, `app/services/auth_service.py:51-114`

---

### 2. Login

Authenticate user and receive access tokens.

**Endpoint:** `POST /api/v1/auth/login`
**Tags:** Authentication
**Authentication:** None required
**Status:** ✅ Implemented

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Request Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email address |
| password | string | Yes | User's password |

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account is inactive

**Business Logic:**
1. Find user by email
2. Verify password using Argon2
3. Check if user is active
4. Update last_login_at timestamp
5. Generate JWT access token (30 min expiry)
6. Generate JWT refresh token (7 day expiry)
7. Return tokens

**OAuth2 Configuration:**
- Token URL: `/api/v1/auth/login`
- Scheme: OAuth2PasswordBearer
- Configured in: `app/api/deps.py:16`

**File Location:** `app/api/v1/auth.py:70-88`, `app/services/auth_service.py:19-48`

---

### 3. Refresh Token

Obtain new access and refresh tokens using a refresh token.

**Endpoint:** `POST /api/v1/auth/refresh`
**Tags:** Authentication
**Authentication:** None required (refresh token in body)
**Status:** ✅ Implemented

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK` - New tokens generated
- `401 Unauthorized` - Invalid or expired refresh token

**Business Logic:**
1. Validate refresh token signature
2. Check token type is "refresh"
3. Verify token not expired
4. Extract user_id from token
5. Verify user still exists and is active
6. Generate new access token and refresh token
7. Return both tokens

**File Location:** `app/api/v1/auth.py:91-104`, `app/services/auth_service.py:158-201`

---

### 4. Get Current User

Get details of the currently authenticated user.

**Endpoint:** `GET /api/v1/auth/me`
**Tags:** Authentication
**Authentication:** Bearer token required
**Status:** ✅ Implemented

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "full_name": "John Doe",
  "designation": "Project Manager",
  "phone": "+1234567890",
  "is_active": true,
  "is_superuser": false,
  "email_verified": true,
  "mfa_enabled": false,
  "tenant_id": 1,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "last_login_at": "2025-11-02T08:15:00Z",
  "roles": [
    {
      "id": 1,
      "name": "Admin",
      "description": "Administrator with full access to tenant resources"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - User details retrieved
- `401 Unauthorized` - Invalid or missing token

**Business Logic:**
1. Extract JWT from Authorization header
2. Validate token signature and expiry
3. Fetch user from database by user_id in token
4. Verify user is active
5. Include user's roles
6. Return user details

**File Location:** `app/api/v1/auth.py:107-115`, `app/api/deps.py:19-58`

---

## Tenant Management APIs

All tenant management endpoints are available under `/api/v1/tenants`.

### 1. Organization Signup (Self-Service)

Create a new organization with an admin user in one step. This is the primary signup flow for new customers.

**Endpoint:** `POST /api/v1/tenants/signup`
**Tags:** Tenants
**Authentication:** None required (public endpoint)
**Status:** ✅ Implemented

**Request Body:**
```json
{
  "organization_name": "Acme Corporation",
  "subdomain": "acme",
  "email": "admin@acme.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "contact_email": "contact@acme.com",
  "contact_phone": "+1234567890"
}
```

**Request Schema:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| organization_name | string | Yes | 2-200 characters |
| subdomain | string | Yes | 3-63 chars, lowercase alphanumeric with hyphens |
| email | string | Yes | Valid email (admin user) |
| password | string | Yes | Min 8 characters |
| full_name | string | No | Max 200 characters |
| contact_email | string | No | Valid email format |
| contact_phone | string | No | Max 20 characters |

**Subdomain Validation:**
- Must contain only lowercase letters, numbers, and hyphens
- Cannot start or end with a hyphen
- Reserved names blocked: www, api, admin, app, mail, ftp, localhost, test, demo

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "tenant": {
    "id": 1,
    "name": "Acme Corporation",
    "subdomain": "acme",
    "is_active": true,
    "plan": "free",
    "max_users": 1,
    "max_forms": 3,
    "trial_started_at": null,
    "trial_ends_at": null,
    "contact_email": "contact@acme.com",
    "contact_phone": "+1234567890",
    "created_at": "2025-11-04T10:30:00Z"
  },
  "user_id": 1,
  "email": "admin@acme.com"
}
```

**Status Codes:**
- `201 Created` - Organization and admin user created successfully
- `400 Bad Request` - Invalid input data or subdomain format
- `409 Conflict` - Email or subdomain already taken

**Business Logic:**
1. Validate subdomain format and check reserved names
2. Check if subdomain is available
3. Check if email already exists
4. Create tenant with FREE plan (1 user, 3 forms)
5. Create admin user with hashed password
6. Create tenant-specific Admin role with all permissions
7. Assign Admin role to user
8. Generate JWT tokens for immediate login
9. Return tokens and tenant details

**Freemium Plan Details:**
- **FREE**: 1 user, 3 forms (permanent, no time limit)
- **PRO**: 10 users, 30 forms (requires payment)
- **ADVANCED**: 100 users, 300 forms (requires payment)
- **ENTERPRISE**: Unlimited users and forms (requires payment)

**File Location:** `app/api/v1/tenants.py:19-41`, `app/services/auth_service.py:204-310`

---

### 2. Get My Tenant

Get details of the authenticated user's tenant.

**Endpoint:** `GET /api/v1/tenants/me`
**Tags:** Tenants
**Authentication:** Bearer token required
**Status:** ✅ Implemented

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "subdomain": "acme",
  "is_active": true,
  "plan": "free",
  "max_users": 1,
  "max_forms": 3,
  "trial_started_at": null,
  "trial_ends_at": null,
  "contact_email": "contact@acme.com",
  "contact_phone": "+1234567890",
  "address": null,
  "created_at": "2025-11-04T10:30:00Z",
  "updated_at": "2025-11-04T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Tenant details retrieved
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Tenant not found

**File Location:** `app/api/v1/tenants.py:44-57`

---

### 3. Update My Tenant

Update the authenticated user's tenant (admin only).

**Endpoint:** `PUT /api/v1/tenants/me`
**Tags:** Tenants
**Authentication:** Bearer token required (Admin only)
**Status:** ✅ Implemented

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Acme Corporation Inc.",
  "contact_email": "newcontact@acme.com",
  "contact_phone": "+9876543210",
  "address": "123 Main St, City, Country"
}
```

**Request Schema (all fields optional):**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| name | string | No | 2-200 characters |
| contact_email | string | No | Valid email format |
| contact_phone | string | No | Max 20 characters |
| address | string | No | Max 500 characters |

**Response:**
```json
{
  "id": 1,
  "name": "Acme Corporation Inc.",
  "subdomain": "acme",
  "is_active": true,
  "plan": "free",
  "max_users": 1,
  "max_forms": 3,
  "contact_email": "newcontact@acme.com",
  "contact_phone": "+9876543210",
  "address": "123 Main St, City, Country",
  "created_at": "2025-11-04T10:30:00Z",
  "updated_at": "2025-11-04T11:45:00Z"
}
```

**Status Codes:**
- `200 OK` - Tenant updated successfully
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - User is not an admin
- `404 Not Found` - Tenant not found

**Note:** Subdomain and plan cannot be changed via this endpoint.

**File Location:** `app/api/v1/tenants.py:60-76`

---

### 4. Get Tenant by ID

Get tenant details by ID (admin only).

**Endpoint:** `GET /api/v1/tenants/{tenant_id}`
**Tags:** Tenants
**Authentication:** Bearer token required (Admin only)
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | integer | Yes | Tenant ID |

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "subdomain": "acme",
  "is_active": true,
  "plan": "free",
  "max_users": 1,
  "max_forms": 3,
  "trial_started_at": null,
  "trial_ends_at": null,
  "contact_email": "contact@acme.com",
  "contact_phone": "+1234567890",
  "address": null,
  "created_at": "2025-11-04T10:30:00Z",
  "updated_at": "2025-11-04T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Tenant details retrieved
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - User is not an admin
- `404 Not Found` - Tenant not found

**File Location:** `app/api/v1/tenants.py:79-92`

---

## User Management APIs

All user management endpoints are available under `/api/v1/users`.

### 1. List Users

Get a paginated list of users (filtered by tenant).

**Endpoint:** `GET /api/v1/users`
**Tags:** Users
**Authentication:** Bearer token required
**Status:** ✅ Implemented

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 20 | Number of records to return (max 100) |
| search | string | No | - | Search query (email, full name) |

**Example Request:**
```
GET /api/v1/users?skip=0&limit=20&search=john
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 123,
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "designation": "Project Manager",
      "phone": "+1234567890",
      "is_active": true,
      "is_superuser": false,
      "email_verified": true,
      "mfa_enabled": false,
      "tenant_id": 1,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z",
      "last_login_at": "2025-11-02T08:15:00Z",
      "roles": [
        {
          "id": 1,
          "name": "admin",
          "description": "Administrator role"
        }
      ]
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

**Status Codes:**
- `200 OK` - Users retrieved successfully
- `401 Unauthorized` - Invalid or missing token

**Business Logic:**
1. Verify user is authenticated
2. Apply tenant filter automatically
3. Apply search query if provided (email, full_name using ILIKE)
4. Apply pagination (order by created_at DESC)
5. Eager load user roles
6. Return paginated results with total count

**File Location:** `app/api/v1/users.py:68-103`, `app/services/user_service.py:116-165`

---

### 2. Invite User

Invite a new user to the tenant (admin only).

**Endpoint:** `POST /api/v1/users/invite`
**Tags:** Users
**Authentication:** Bearer token required
**Permission Required:** Admin role
**Status:** ✅ Implemented

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "full_name": "Jane Smith",
  "designation": "Developer",
  "phone": "+1234567891",
  "role_ids": [1, 2]
}
```

**Response:**
```json
{
  "user": {
    "id": 124,
    "email": "newuser@example.com",
    "full_name": "Jane Smith",
    "designation": "Developer",
    "phone": "+1234567891",
    "is_active": true,
    "is_superuser": false,
    "email_verified": false,
    "mfa_enabled": false,
    "tenant_id": 1,
    "created_at": "2025-11-02T10:30:00Z",
    "updated_at": "2025-11-02T10:30:00Z",
    "last_login_at": null,
    "roles": [
      {
        "id": 1,
        "name": "admin",
        "description": "Administrator role"
      }
    ]
  },
  "temporary_password": "aB3$xY9!mK2L",
  "message": "User invited successfully. Temporary password should be sent via email."
}
```

**Status Codes:**
- `201 Created` - User invited successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions (not admin)
- `409 Conflict` - Email already exists

**Business Logic:**
1. Check current user has admin role (`require_tenant_admin`)
2. Validate email uniqueness (global check, not just tenant)
3. Check tenant user limit based on subscription plan
4. Generate secure random temporary password (12 characters)
5. Hash password using Argon2
6. Set tenant_id from current user's context
7. Create user record with `email_verified=False`
8. Assign roles if role_ids provided (validates roles belong to tenant)
9. Return user details with temporary password
10. TODO: Send invitation email with temporary password (not yet implemented)

**Note:** In production, the temporary password should only be sent via email, not returned in the response. This is for development/testing purposes.

**File Location:** `app/api/v1/users.py:27-65`, `app/services/user_service.py:33-113`

---

### 3. Get User by ID

Retrieve details of a specific user.

**Endpoint:** `GET /api/v1/users/{user_id}`
**Tags:** Users
**Authentication:** Bearer token required
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | User ID |

**Example Request:**
```
GET /api/v1/users/123
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "full_name": "John Doe",
  "designation": "Project Manager",
  "phone": "+1234567890",
  "is_active": true,
  "is_superuser": false,
  "email_verified": true,
  "mfa_enabled": false,
  "tenant_id": 1,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "last_login_at": "2025-11-02T08:15:00Z",
  "roles": [
    {
      "id": 1,
      "name": "admin",
      "description": "Administrator role"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - User retrieved successfully
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User not found or belongs to different tenant

**Business Logic:**
1. Verify user is authenticated
2. Apply tenant filter (security - only returns user if in same tenant)
3. Fetch user by ID with eager loading of roles
4. Return 404 if user not found (not 403 to prevent information disclosure)
5. Return user details with roles

**File Location:** `app/api/v1/users.py:106-137`, `app/services/user_service.py:168-192`

---

### 4. Update User

Update user information (admin only).

**Endpoint:** `PUT /api/v1/users/{user_id}`
**Tags:** Users
**Authentication:** Bearer token required
**Permission Required:** Admin role
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | User ID |

**Request Body:**
```json
{
  "full_name": "John Updated Doe",
  "designation": "Senior Project Manager",
  "phone": "+1234567899",
  "is_active": true
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Response:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "full_name": "John Updated Doe",
  "designation": "Senior Project Manager",
  "phone": "+1234567899",
  "is_active": true,
  "is_superuser": false,
  "email_verified": true,
  "mfa_enabled": false,
  "tenant_id": 1,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-11-02T11:00:00Z",
  "last_login_at": "2025-11-02T08:15:00Z",
  "roles": [
    {
      "id": 1,
      "name": "admin",
      "description": "Administrator role"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - User updated successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions (not admin)
- `404 Not Found` - User not found

**Business Logic:**
1. Check current user has admin role (`require_tenant_admin`)
2. Verify user exists in tenant
3. Update only provided fields (partial update using `exclude_unset=True`)
4. Set updated_at timestamp automatically
5. Return updated user details with roles

**File Location:** `app/api/v1/users.py:140-174`, `app/services/user_service.py:195-232`

---

### 5. Delete User

Delete a user (soft delete recommended).

**Endpoint:** `DELETE /api/v1/users/{id}`
**Tags:** Users
**Authentication:** Bearer token required
**Permission Required:** `users.delete`
**Status:** 🔴 Not Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | User ID |

**Example Request:**
```
DELETE /api/v1/users/123
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "User deleted successfully",
  "id": 123
}
```

**Status Codes:**
- `200 OK` - User deleted successfully
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - User not found

**Business Logic:**
1. Check user has `users.delete` permission
2. Verify user exists in tenant
3. Check for dependencies (created forms, submissions)
4. Soft delete: Set is_active = false (recommended)
5. Or hard delete: Remove record (cascades)
6. Create audit log entry
7. Return success message

**File Location (Planned):** `app/api/v1/users.py`, `app/services/user_service.py`

---

## Form Management APIs

All form management endpoints will be available under `/api/v1/forms`.

### 1. List Forms

Get a paginated list of forms (filtered by tenant with automatic tenant isolation).

**Endpoint:** `GET /api/v1/forms`
**Tags:** Forms
**Authentication:** Bearer token required
**Status:** ✅ Implemented

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 20 | Number of records to return (max 100) |
| q | string | No | - | Search query (title, description) |
| is_published | boolean | No | - | Filter by published status |
| created_by | integer | No | - | Filter by creator user ID |
| sort_by | string | No | created_at | Field to sort by |
| order | string | No | desc | Sort order (asc/desc) |

**Example Request:**
```
GET /api/v1/forms?skip=0&limit=20&is_published=true&sort_by=created_at&order=desc
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Employee Feedback Form",
      "description": "Annual employee feedback collection",
      "header": {
        "logo": "https://example.com/logo.png",
        "org_name": "ACME Corp",
        "address": "123 Main St, City, State"
      },
      "is_active": true,
      "is_published": true,
      "version": 1,
      "allow_multiple_submissions": true,
      "requires_approval": true,
      "tenant_id": 1,
      "created_by": 123,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z",
      "published_at": "2025-01-16T09:00:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

**Status Codes:**
- `200 OK` - Forms retrieved successfully
- `401 Unauthorized` - Invalid or missing token

**Business Logic:**
1. Verify user is authenticated
2. Apply tenant filter automatically
3. Apply search query if provided (title, description)
4. Apply filters (is_published, created_by)
5. Apply sorting
6. Apply pagination
7. Return paginated results with total count

**File Location (Planned):** `app/api/v1/forms.py`, `app/services/form_service.py`

---

### 2. Create Form

Create a new form template with fields. Enforces plan limits (FREE plan: max 3 forms).

**Endpoint:** `POST /api/v1/forms`
**Tags:** Forms
**Authentication:** Bearer token required
**Permission Required:** `forms.create`
**Status:** ✅ Implemented

**Request Body:**
```json
{
  "title": "Employee Feedback Form",
  "description": "Annual employee feedback collection",
  "header": {
    "logo": "https://example.com/logo.png",
    "org_name": "ACME Corp",
    "address": "123 Main St, City, State"
  },
  "is_published": false,
  "allow_multiple_submissions": true,
  "requires_approval": true,
  "fields": [
    {
      "field_type": "text",
      "label": "Full Name",
      "placeholder": "Enter your full name",
      "help_text": "Please provide your legal name",
      "required": true,
      "order": 0,
      "validation_rules": {
        "min_length": 2,
        "max_length": 100
      }
    },
    {
      "field_type": "email",
      "label": "Email Address",
      "placeholder": "you@example.com",
      "required": true,
      "order": 1
    },
    {
      "field_type": "number",
      "label": "Years of Experience",
      "required": true,
      "order": 2,
      "validation_rules": {
        "min": 0,
        "max": 50
      }
    },
    {
      "field_type": "select",
      "label": "Department",
      "required": true,
      "order": 3,
      "options": ["Engineering", "Sales", "Marketing", "HR", "Finance"]
    },
    {
      "field_type": "radio",
      "label": "Employment Type",
      "required": true,
      "order": 4,
      "options": ["Full-time", "Part-time", "Contract"]
    },
    {
      "field_type": "checkbox",
      "label": "Skills",
      "order": 5,
      "options": ["Python", "JavaScript", "React", "Node.js", "SQL"]
    },
    {
      "field_type": "textarea",
      "label": "Comments",
      "placeholder": "Additional feedback...",
      "order": 6,
      "validation_rules": {
        "max_length": 1000
      }
    },
    {
      "field_type": "date",
      "label": "Start Date",
      "required": true,
      "order": 7
    },
    {
      "field_type": "file",
      "label": "Resume",
      "help_text": "Upload your resume (PDF, DOC, DOCX - Max 10MB)",
      "order": 8
    }
  ]
}
```

**Supported Field Types:**
| Type | Description | Value Storage |
|------|-------------|---------------|
| text | Single-line text input | value_text |
| textarea | Multi-line text input | value_text |
| number | Numeric input | value_number |
| email | Email address with validation | value_text |
| url | URL with validation | value_text |
| phone | Phone number | value_text |
| select | Dropdown selection | value_text or value_json |
| radio | Radio button selection | value_text |
| checkbox | Multiple checkboxes | value_json |
| file | File upload | file_attachment_id |
| date | Date picker | value_date |
| time | Time picker | value_date |

**Response:**
```json
{
  "id": 1,
  "title": "Employee Feedback Form",
  "description": "Annual employee feedback collection",
  "header": {
    "logo": "https://example.com/logo.png",
    "org_name": "ACME Corp",
    "address": "123 Main St, City, State"
  },
  "is_active": true,
  "is_published": false,
  "version": 1,
  "allow_multiple_submissions": true,
  "requires_approval": true,
  "tenant_id": 1,
  "created_by": 123,
  "created_at": "2025-11-02T10:30:00Z",
  "updated_at": "2025-11-02T10:30:00Z",
  "published_at": null,
  "fields": [
    {
      "id": 1,
      "form_id": 1,
      "field_type": "text",
      "label": "Full Name",
      "placeholder": "Enter your full name",
      "help_text": "Please provide your legal name",
      "required": true,
      "order": 0,
      "validation_rules": {
        "min_length": 2,
        "max_length": 100
      },
      "created_at": "2025-11-02T10:30:00Z",
      "updated_at": "2025-11-02T10:30:00Z"
    }
    // ... more fields
  ]
}
```

**Status Codes:**
- `201 Created` - Form created successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Form limit exceeded for tenant's plan

**Business Logic:**
1. Validate form data and field configurations
2. **Check tenant form limit based on subscription plan**
3. Set tenant_id from current user's context (automatic tenant isolation)
4. Set created_by to current user ID
5. Create form record with version = 1
6. Create all form fields with proper ordering
7. Validate field types and options
8. Return created form with all fields

**File Location:** `app/api/v1/forms.py:20-39`, `app/services/form_service.py:17-79`

---

### 3. Get Form Details

Retrieve complete form details including all fields (with tenant isolation).

**Endpoint:** `GET /api/v1/forms/{id}`
**Tags:** Forms
**Authentication:** Bearer token required
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Form ID |

**Example Request:**
```
GET /api/v1/forms/1
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Employee Feedback Form",
  "description": "Annual employee feedback collection",
  "header": {
    "logo": "https://example.com/logo.png",
    "org_name": "ACME Corp",
    "address": "123 Main St, City, State"
  },
  "is_active": true,
  "is_published": true,
  "version": 1,
  "allow_multiple_submissions": true,
  "requires_approval": true,
  "tenant_id": 1,
  "created_by": 123,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "published_at": "2025-01-16T09:00:00Z",
  "fields": [
    {
      "id": 1,
      "form_id": 1,
      "field_type": "text",
      "label": "Full Name",
      "placeholder": "Enter your full name",
      "help_text": "Please provide your legal name",
      "required": true,
      "order": 0,
      "options": null,
      "validation_rules": {
        "min_length": 2,
        "max_length": 100
      },
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
    // ... more fields ordered by 'order' field
  ]
}
```

**Status Codes:**
- `200 OK` - Form retrieved successfully
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Form not found or belongs to different tenant

**Business Logic:**
1. Verify user is authenticated
2. Apply tenant filter (security)
3. Fetch form by ID with eager loading of fields
4. Sort fields by order
5. Return 404 (not 403) to prevent information disclosure
6. Return complete form details

**File Location (Planned):** `app/api/v1/forms.py`, `app/services/form_service.py`

---

### 4. Update Form

Update form template metadata (with tenant isolation).

**Endpoint:** `PUT /api/v1/forms/{id}`
**Tags:** Forms
**Authentication:** Bearer token required
**Permission Required:** `forms.update`
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Form ID |

**Request Body:**
```json
{
  "title": "Updated Employee Feedback Form",
  "description": "Updated annual employee feedback collection",
  "is_published": true,
  "fields": [
    {
      "id": 1,
      "label": "Full Legal Name",
      "placeholder": "Enter your full legal name"
    },
    {
      "field_type": "text",
      "label": "New Field",
      "order": 10
    }
  ]
}
```

**Note:**
- All fields are optional. Only provided fields will be updated.
- If form is published, creates a new version
- Fields with `id` will be updated, fields without `id` will be created

**Response:**
```json
{
  "id": 1,
  "title": "Updated Employee Feedback Form",
  "description": "Updated annual employee feedback collection",
  "version": 2,
  "is_published": true,
  "updated_at": "2025-11-02T11:00:00Z",
  "fields": [...]
}
```

**Status Codes:**
- `200 OK` - Form updated successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Form not found

**Business Logic:**
1. Check user has `forms.update` permission
2. Verify form exists in tenant
3. If form is published and has submissions:
   - Create new version (version++)
   - Keep old version for historical data
4. Update form fields
5. Update existing fields or create new ones
6. Set updated_at timestamp
7. Create audit log entry with changes
8. Return updated form details

**File Location (Planned):** `app/api/v1/forms.py`, `app/services/form_service.py`

---

### 5. Delete Form

Soft delete a form template (sets is_active=False, with tenant isolation).

**Endpoint:** `DELETE /api/v1/forms/{id}`
**Tags:** Forms
**Authentication:** Bearer token required
**Permission Required:** `forms.delete`
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Form ID |

**Example Request:**
```
DELETE /api/v1/forms/1
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Form deleted successfully",
  "id": 1,
  "deleted_fields": 9,
  "deleted_submissions": 25
}
```

**Status Codes:**
- `200 OK` - Form deleted successfully
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Form not found

**Business Logic:**
1. Check user has `forms.delete` permission
2. Verify form exists in tenant
3. Check if form is published (warn if it is)
4. Soft delete: Set is_active = false (recommended)
5. Or hard delete: Remove record (cascades to fields, submissions, responses)
6. Create audit log entry
7. Return success message with counts

**Cascade Behavior (on hard delete):**
- All form_fields records deleted
- All submission records deleted
- All submission_responses deleted
- All form_approvals deleted

**File Location:** `app/api/v1/forms.py:152-170`, `app/services/form_service.py:197-228`

---

### 6. Publish/Unpublish Form

Publish or unpublish a form to make it available for submissions.

**Endpoint:** `POST /api/v1/forms/{form_id}/publish`
**Tags:** Forms
**Authentication:** Bearer token required
**Permission Required:** `forms.update`
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| form_id | integer | Yes | Form ID |

**Request Body:**
```json
{
  "is_published": true
}
```

**Request Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| is_published | boolean | Yes | true to publish, false to unpublish |

**Response:**
```json
{
  "id": 1,
  "title": "Employee Feedback Form",
  "description": "Annual employee feedback collection",
  "is_published": true,
  "published_at": "2025-11-04T14:30:00Z",
  "version": 1,
  "tenant_id": 1,
  "created_by": 123,
  "created_at": "2025-11-04T10:30:00Z",
  "updated_at": "2025-11-04T14:30:00Z",
  "fields": [...]
}
```

**Status Codes:**
- `200 OK` - Form publish status updated successfully
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Form not found

**Business Logic:**
1. Verify form exists and belongs to tenant
2. Update is_published status
3. Set published_at timestamp when publishing for the first time
4. Return updated form

**File Location:** `app/api/v1/forms.py:173-199`, `app/services/form_service.py:231-267`

---

### 7. Add Field to Form

Add a new field to an existing form.

**Endpoint:** `POST /api/v1/forms/{form_id}/fields`
**Tags:** Forms
**Authentication:** Bearer token required
**Permission Required:** `forms.update`
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| form_id | integer | Yes | Form ID |

**Request Body:**
```json
{
  "field_type": "text",
  "label": "Additional Comments",
  "placeholder": "Enter any additional comments",
  "help_text": "Optional field for extra feedback",
  "required": false,
  "order": 5,
  "validation_rules": {
    "max_length": 500
  }
}
```

**Request Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| field_type | string | Yes | One of: text, email, number, select, radio, checkbox, textarea, date, time, file |
| label | string | Yes | Field label (max 200 chars) |
| placeholder | string | No | Placeholder text (max 200 chars) |
| help_text | string | No | Help/hint text |
| required | boolean | No | Whether field is required (default: false) |
| options | array | No | Options for select/radio/checkbox fields |
| order | integer | Yes | Display order (0-based) |
| validation_rules | object | No | Field-specific validation rules (JSON) |

**Response:**
```json
{
  "id": 6,
  "form_id": 1,
  "field_type": "text",
  "label": "Additional Comments",
  "placeholder": "Enter any additional comments",
  "help_text": "Optional field for extra feedback",
  "required": false,
  "options": null,
  "order": 5,
  "validation_rules": {
    "max_length": 500
  },
  "created_at": "2025-11-04T15:00:00Z",
  "updated_at": "2025-11-04T15:00:00Z"
}
```

**Status Codes:**
- `201 Created` - Field added successfully
- `400 Bad Request` - Invalid field data
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Form not found

**Business Logic:**
1. Verify form exists and belongs to tenant
2. Validate field type and configuration
3. Create new form field with specified order
4. Return created field

**File Location:** `app/api/v1/forms.py:202-227`, `app/services/form_service.py:270-317`

---

### 8. Assign Form for Approval

Assign a form to a user for review and approval.

**Endpoint:** `POST /api/v1/forms/{id}/assign`
**Tags:** Forms
**Authentication:** Bearer token required
**Permission Required:** `forms.assign`
**Status:** 🔴 Not Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Form ID |

**Request Body:**
```json
{
  "assigned_to": 456,
  "comments": "Please review this form by end of week"
}
```

**Response:**
```json
{
  "id": 1,
  "form_id": 1,
  "assigned_to": 456,
  "assigned_by": 123,
  "status": "pending",
  "comments": "Please review this form by end of week",
  "tenant_id": 1,
  "assigned_at": "2025-11-02T10:30:00Z",
  "reviewed_at": null,
  "approved_at": null,
  "rejected_at": null
}
```

**Status Codes:**
- `201 Created` - Form assigned successfully
- `400 Bad Request` - Invalid user ID or form already assigned
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Form not found

**Business Logic:**
1. Check user has `forms.assign` permission
2. Verify form exists in tenant
3. Verify assigned_to user exists in same tenant
4. Check if form already has pending approval
5. Create form_approval record
6. Set assigned_by to current user ID
7. Set status to "pending"
8. Send notification email to assigned_to user
9. Create audit log entry
10. Return approval assignment details

**File Location (Planned):** `app/api/v1/forms.py`, `app/services/form_service.py`, `app/services/approval_service.py`

---

## Submission APIs

All submission endpoints will be available under `/api/v1/submissions`.

### 1. Submit Form

Submit a completed form response.

**Endpoint:** `POST /api/v1/forms/{id}/submit`
**Tags:** Submissions
**Authentication:** Bearer token required (optional for anonymous forms)
**Status:** 🔴 Not Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Form ID |

**Request Body:**
```json
{
  "submitted_by_email": "user@example.com",
  "submitted_by_name": "John Doe",
  "submission_metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "location": "New York, USA"
  },
  "responses": [
    {
      "field_id": 1,
      "value_text": "John Doe"
    },
    {
      "field_id": 2,
      "value_text": "john@example.com"
    },
    {
      "field_id": 3,
      "value_number": 5
    },
    {
      "field_id": 4,
      "value_text": "Engineering"
    },
    {
      "field_id": 5,
      "value_text": "Full-time"
    },
    {
      "field_id": 6,
      "value_json": ["Python", "JavaScript", "SQL"]
    },
    {
      "field_id": 7,
      "value_text": "Great experience working here!"
    },
    {
      "field_id": 8,
      "value_date": "2020-01-15T00:00:00Z"
    },
    {
      "field_id": 9,
      "file_attachment_id": 123
    }
  ]
}
```

**Field Response Rules:**
- **text/textarea/email/url/phone/select/radio:** Use `value_text`
- **number:** Use `value_number`
- **checkbox:** Use `value_json` (array of selected values)
- **date/time:** Use `value_date` (ISO 8601 format)
- **file:** Use `file_attachment_id` (upload file first, get ID)

**Response:**
```json
{
  "id": 100,
  "form_id": 1,
  "submitted_by": 123,
  "submitted_by_email": "user@example.com",
  "submitted_by_name": "John Doe",
  "status": "submitted",
  "submission_metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "location": "New York, USA"
  },
  "tenant_id": 1,
  "created_at": "2025-11-02T10:00:00Z",
  "submitted_at": "2025-11-02T10:30:00Z",
  "updated_at": "2025-11-02T10:30:00Z"
}
```

**Status Codes:**
- `201 Created` - Submission created successfully
- `400 Bad Request` - Invalid input data or validation errors
- `401 Unauthorized` - Authentication required (if not anonymous)
- `404 Not Found` - Form not found or not published

**Business Logic:**
1. Verify form exists and is published
2. Check if form allows multiple submissions
3. For authenticated users: Set submitted_by to user ID
4. For anonymous: Use submitted_by_email and submitted_by_name
5. Validate all required fields are present
6. Validate field responses match field types
7. Apply field validation rules (min/max, pattern, etc.)
8. Create submission record with status "submitted"
9. Create submission_response records for each field
10. If requires_approval: Set status to "pending"
11. Send notification to form owner
12. Create audit log entry
13. Return submission details

**Validation Errors Example:**
```json
{
  "detail": [
    {
      "field_id": 1,
      "field_label": "Full Name",
      "error": "Field is required"
    },
    {
      "field_id": 3,
      "field_label": "Years of Experience",
      "error": "Value must be between 0 and 50"
    }
  ]
}
```

**File Location (Planned):** `app/api/v1/submissions.py`, `app/services/submission_service.py`

---

### 2. List Submissions

Get a paginated list of form submissions (filtered by tenant).

**Endpoint:** `GET /api/v1/submissions`
**Tags:** Submissions
**Authentication:** Bearer token required
**Status:** 🔴 Not Implemented

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 20 | Number of records to return (max 100) |
| form_id | integer | No | - | Filter by form ID |
| status | string | No | - | Filter by status (draft, submitted, pending, approved, rejected) |
| submitted_by | integer | No | - | Filter by submitter user ID |
| sort_by | string | No | submitted_at | Field to sort by |
| order | string | No | desc | Sort order (asc/desc) |

**Example Request:**
```
GET /api/v1/submissions?form_id=1&status=submitted&skip=0&limit=20
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 100,
      "form_id": 1,
      "form_title": "Employee Feedback Form",
      "submitted_by": 123,
      "submitted_by_email": "user@example.com",
      "submitted_by_name": "John Doe",
      "status": "submitted",
      "tenant_id": 1,
      "created_at": "2025-11-02T10:00:00Z",
      "submitted_at": "2025-11-02T10:30:00Z",
      "updated_at": "2025-11-02T10:30:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

**Status Codes:**
- `200 OK` - Submissions retrieved successfully
- `401 Unauthorized` - Invalid or missing token

**Submission Status Values:**
- `draft` - Submission started but not completed
- `submitted` - Submission completed
- `pending` - Awaiting approval
- `approved` - Approved by reviewer
- `rejected` - Rejected by reviewer

**Business Logic:**
1. Verify user is authenticated
2. Apply tenant filter automatically
3. Apply filters (form_id, status, submitted_by)
4. Apply sorting
5. Apply pagination
6. Return paginated results with total count

**File Location (Planned):** `app/api/v1/submissions.py`, `app/services/submission_service.py`

---

### 3. Get Form Submissions

Get all submissions for a specific form.

**Endpoint:** `GET /api/v1/submissions/form/{form_id}`
**Tags:** Submissions
**Authentication:** Bearer token required
**Status:** ✅ Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| form_id | integer | Yes | Form ID |

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 20 | Number of records to return (max 100) |
| status | string | No | - | Filter by status (submitted, pending, approved, rejected) |

**Example Request:**
```
GET /api/v1/submissions/form/1?status=submitted&skip=0&limit=20
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 100,
      "form_id": 1,
      "form_title": "Employee Feedback Form",
      "submitted_by": 123,
      "submitted_by_email": "user@example.com",
      "submitted_by_name": "John Doe",
      "status": "submitted",
      "tenant_id": 1,
      "created_at": "2025-11-02T10:00:00Z",
      "submitted_at": "2025-11-02T10:30:00Z",
      "updated_at": "2025-11-02T10:30:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20
}
```

**Status Codes:**
- `200 OK` - Submissions retrieved successfully
- `401 Unauthorized` - Invalid or missing token

**Business Logic:**
1. Verify user is authenticated
2. Apply tenant filter automatically
3. Filter submissions by form_id
4. Apply optional status filter
5. Apply pagination
6. Return paginated results with total count

**File Location:** `app/api/v1/submissions.py`, `app/services/submission_service.py`

---

### 4. Get Submission Details

Retrieve complete submission details including all responses.

**Endpoint:** `GET /api/v1/submissions/{id}`
**Tags:** Submissions
**Authentication:** Bearer token required
**Status:** 🔴 Not Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Submission ID |

**Example Request:**
```
GET /api/v1/submissions/100
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 100,
  "form": {
    "id": 1,
    "title": "Employee Feedback Form",
    "description": "Annual employee feedback collection"
  },
  "submitted_by": 123,
  "submitted_by_email": "user@example.com",
  "submitted_by_name": "John Doe",
  "status": "submitted",
  "submission_metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "location": "New York, USA"
  },
  "tenant_id": 1,
  "created_at": "2025-11-02T10:00:00Z",
  "submitted_at": "2025-11-02T10:30:00Z",
  "updated_at": "2025-11-02T10:30:00Z",
  "responses": [
    {
      "id": 1,
      "field": {
        "id": 1,
        "field_type": "text",
        "label": "Full Name"
      },
      "value_text": "John Doe",
      "value_number": null,
      "value_boolean": null,
      "value_date": null,
      "value_json": null,
      "file_attachment": null
    },
    {
      "id": 2,
      "field": {
        "id": 2,
        "field_type": "email",
        "label": "Email Address"
      },
      "value_text": "john@example.com",
      "value_number": null,
      "value_boolean": null,
      "value_date": null,
      "value_json": null,
      "file_attachment": null
    },
    {
      "id": 3,
      "field": {
        "id": 3,
        "field_type": "number",
        "label": "Years of Experience"
      },
      "value_text": null,
      "value_number": 5,
      "value_boolean": null,
      "value_date": null,
      "value_json": null,
      "file_attachment": null
    },
    {
      "id": 6,
      "field": {
        "id": 6,
        "field_type": "checkbox",
        "label": "Skills"
      },
      "value_text": null,
      "value_number": null,
      "value_boolean": null,
      "value_date": null,
      "value_json": ["Python", "JavaScript", "SQL"],
      "file_attachment": null
    },
    {
      "id": 9,
      "field": {
        "id": 9,
        "field_type": "file",
        "label": "Resume"
      },
      "value_text": null,
      "value_number": null,
      "value_boolean": null,
      "value_date": null,
      "value_json": null,
      "file_attachment": {
        "id": 123,
        "original_filename": "resume.pdf",
        "file_size": 256000,
        "mime_type": "application/pdf",
        "uploaded_at": "2025-11-02T10:25:00Z"
      }
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Submission retrieved successfully
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Submission not found or belongs to different tenant

**Business Logic:**
1. Verify user is authenticated
2. Apply tenant filter (security)
3. Fetch submission by ID with eager loading of:
   - Form details
   - All responses
   - Field details for each response
   - File attachments
4. Return 404 (not 403) to prevent information disclosure
5. Return complete submission details

**File Location (Planned):** `app/api/v1/submissions.py`, `app/services/submission_service.py`

---

### 4. Approve Submission

Approve a submission (requires approval permission).

**Endpoint:** `PUT /api/v1/submissions/{id}/approve`
**Tags:** Submissions
**Authentication:** Bearer token required
**Permission Required:** `submissions.approve`
**Status:** 🔴 Not Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Submission ID |

**Request Body:**
```json
{
  "comments": "Approved with recommendations for future improvements"
}
```

**Response:**
```json
{
  "id": 100,
  "form_id": 1,
  "status": "approved",
  "approval": {
    "approved_by": 456,
    "approved_at": "2025-11-02T14:00:00Z",
    "comments": "Approved with recommendations for future improvements"
  },
  "updated_at": "2025-11-02T14:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Submission approved successfully
- `400 Bad Request` - Submission already approved/rejected
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Submission not found

**Business Logic:**
1. Check user has `submissions.approve` permission
2. Verify submission exists in tenant
3. Check submission is in "pending" status
4. Update status to "approved"
5. Record approval timestamp
6. Record approver (current user ID)
7. Add comments to submission
8. Send notification to submitter
9. Create audit log entry
10. Return updated submission details

**File Location (Planned):** `app/api/v1/submissions.py`, `app/services/submission_service.py`

---

### 5. Reject Submission

Reject a submission with feedback (requires approval permission).

**Endpoint:** `PUT /api/v1/submissions/{id}/reject`
**Tags:** Submissions
**Authentication:** Bearer token required
**Permission Required:** `submissions.approve`
**Status:** 🔴 Not Implemented

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Submission ID |

**Request Body:**
```json
{
  "comments": "Please revise the following sections and resubmit:\n- Years of experience seems incorrect\n- Missing required skills information"
}
```

**Response:**
```json
{
  "id": 100,
  "form_id": 1,
  "status": "rejected",
  "rejection": {
    "rejected_by": 456,
    "rejected_at": "2025-11-02T14:00:00Z",
    "comments": "Please revise the following sections and resubmit:\n- Years of experience seems incorrect\n- Missing required skills information"
  },
  "updated_at": "2025-11-02T14:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Submission rejected successfully
- `400 Bad Request` - Submission already approved/rejected or comments required
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Submission not found

**Business Logic:**
1. Check user has `submissions.approve` permission
2. Verify submission exists in tenant
3. Check submission is in "pending" status
4. Require comments (rejection reason)
5. Update status to "rejected"
6. Record rejection timestamp
7. Record rejector (current user ID)
8. Add comments to submission
9. Send notification to submitter with feedback
10. Create audit log entry
11. Return updated submission details

**File Location (Planned):** `app/api/v1/submissions.py`, `app/services/submission_service.py`

---

## Data Models & Database Schema

### Complete Entity-Relationship Overview

The database schema consists of 11 models across 7 files in `app/models/`.

### Database Indexes

Critical indexes for query performance:

```sql
-- Tenant filtering (most common queries)
CREATE INDEX idx_forms_tenant_id ON forms(tenant_id);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_submissions_tenant_id ON submissions(tenant_id);

-- Lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_forms_created_by ON forms(created_by);
CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);

-- Status filtering
CREATE INDEX idx_submissions_status ON submissions(status);

-- Relationships
CREATE INDEX idx_form_fields_form_id ON form_fields(form_id);
CREATE INDEX idx_submissions_form_id ON submissions(form_id);
CREATE INDEX idx_submission_responses_submission_id ON submission_responses(submission_id);
CREATE INDEX idx_submission_responses_field_id ON submission_responses(field_id);

-- Audit trail
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

---

### 1. Tenant Model

**File:** `app/models/tenant.py`
**Table:** `tenants`

Multi-tenant organization/company record with freemium subscription model.

```python
{
  "id": integer (PK, auto-increment),
  "name": string(200),              # Organization name
  "subdomain": string(63),          # Unique subdomain (indexed, unique)
  "is_active": boolean,             # Tenant active status
  "contact_email": string(255),
  "contact_phone": string(20),
  "address": text,
  "plan": enum(PlanType),           # Subscription plan: FREE, PRO, ADVANCED, ENTERPRISE
  "max_users": integer,             # User limit based on plan
  "max_forms": integer,             # Form limit based on plan
  "trial_started_at": datetime,     # Trial start date (nullable, for promotional trials)
  "trial_ends_at": datetime,        # Trial end date (nullable, for promotional trials)
  "created_at": datetime,
  "updated_at": datetime
}
```

**PlanType Enum:**
- `FREE`: 1 user, 3 forms (permanent, no time limit)
- `PRO`: 10 users, 30 forms
- `ADVANCED`: 100 users, 300 forms
- `ENTERPRISE`: 999999 users, 999999 forms (effectively unlimited)

**Helper Methods:**
- `get_plan_limits(plan: PlanType) -> dict`: Returns max_users and max_forms for a given plan
- `is_trial_active() -> bool`: Checks if promotional trial is still active
- `is_within_user_limit(current_user_count: int) -> bool`: Validates user count against limit
- `is_within_form_limit(current_form_count: int) -> bool`: Validates form count against limit

**Relationships:**
- Has many: Users, Forms, Roles, Submissions, FormApprovals, FileAttachments, AuditLogs

**Constraints:**
- Unique subdomain (for tenant identification)
- Subdomain max 63 characters (DNS label limit)
- Subdomain validation: lowercase alphanumeric with hyphens, no leading/trailing hyphens
- Reserved subdomains: www, api, admin, app, mail, ftp, localhost, test, demo

**Business Rules:**
- New signups automatically get FREE plan
- Trial fields (trial_started_at, trial_ends_at) are NULL by default
- Plan upgrades require payment integration (not yet implemented)
- User and form creation automatically checked against plan limits

---

### 2. User Model

**File:** `app/models/user.py`
**Table:** `users`

User account within a tenant.

```python
{
  "id": integer (PK, auto-increment),
  "email": string(255),             # Unique, indexed
  "hashed_password": string(255),   # Argon2 hashed password
  "full_name": string(200),
  "designation": string(100),       # Job title/role
  "phone": string(20),
  "is_active": boolean,             # Account active status
  "is_superuser": boolean,          # Platform administrator
  "email_verified": boolean,        # Email verification status
  "mfa_enabled": boolean,           # Multi-factor authentication enabled
  "mfa_secret": string(32),         # TOTP secret for MFA
  "tenant_id": integer (FK -> tenants.id, indexed),
  "created_at": datetime,
  "updated_at": datetime,
  "last_login_at": datetime         # Last successful login
}
```

**Relationships:**
- Belongs to: Tenant
- Many-to-many: Roles (through `user_roles` junction table)
- Has many: Forms (created_by), Submissions (submitted_by), FileAttachments (uploaded_by), AuditLogs

**Constraints:**
- Email must be unique
- Email indexed for fast lookups
- tenant_id indexed for tenant filtering

**Security:**
- Password hashed with Argon2 (OWASP recommended)
- Fallback to bcrypt if Argon2 unavailable
- MFA support for enhanced security

---

### 3. Role Model

**File:** `app/models/user.py`
**Table:** `roles`

Role definition for RBAC (tenant-specific).

```python
{
  "id": integer (PK, auto-increment),
  "name": string(50),               # Role name: admin, editor, viewer, approver
  "description": text,              # Role description
  "tenant_id": integer (FK -> tenants.id),
  "is_system_role": boolean,        # System role (cannot be modified/deleted)
  "created_at": datetime,
  "updated_at": datetime
}
```

**Relationships:**
- Belongs to: Tenant
- Many-to-many: Users (through `user_roles`), Permissions (through `role_permissions`)

**Common Roles:**
- **admin** - Full access to all resources
- **editor** - Can create and edit forms
- **viewer** - Read-only access
- **approver** - Can approve/reject submissions

---

### 4. Permission Model

**File:** `app/models/user.py`
**Table:** `permissions`

Permission definition for fine-grained access control.

```python
{
  "id": integer (PK, auto-increment),
  "name": string(100),              # Unique: "resource.action" format
  "resource": string(50),           # Resource: forms, users, submissions
  "action": string(50),             # Action: create, read, update, delete, approve
  "description": text,
  "created_at": datetime
}
```

**Permission Format:** `resource.action`

**Examples:**
- `forms.create` - Create forms
- `forms.update` - Update forms
- `forms.delete` - Delete forms
- `users.create` - Create users
- `users.update` - Update users
- `users.delete` - Delete users
- `submissions.approve` - Approve/reject submissions

**Relationships:**
- Many-to-many: Roles (through `role_permissions` junction table)

---

### 5. Form Model

**File:** `app/models/form.py`
**Table:** `forms`

Form template definition.

```python
{
  "id": integer (PK, auto-increment),
  "title": string(200),
  "description": text,
  "header": json,                   # Logo, org name, address
  "is_active": boolean,
  "is_published": boolean,          # Available for submissions
  "tenant_id": integer (FK -> tenants.id, indexed),
  "created_by": integer (FK -> users.id, indexed),
  "version": integer,               # Version control
  "allow_multiple_submissions": boolean,
  "requires_approval": boolean,
  "created_at": datetime,
  "updated_at": datetime,
  "published_at": datetime          # When form was published
}
```

**Relationships:**
- Belongs to: Tenant, User (creator)
- Has many: FormFields, Submissions, FormApprovals

**Header JSON Structure:**
```json
{
  "logo": "https://example.com/logo.png",
  "org_name": "ACME Corporation",
  "address": "123 Main St, City, State 12345"
}
```

**Versioning:**
- Version increments when published form is modified
- Allows historical tracking of form changes

---

### 6. FormField Model

**File:** `app/models/form.py`
**Table:** `form_fields`

Individual field within a form.

```python
{
  "id": integer (PK, auto-increment),
  "form_id": integer (FK -> forms.id, indexed),
  "field_type": enum(FieldType),    # See field types below
  "label": string(200),             # Field label
  "placeholder": string(200),       # Placeholder text
  "help_text": text,                # Help/hint text
  "required": boolean,              # Is field required?
  "options": json,                  # Options for select/radio/checkbox
  "order": integer,                 # Display order (0-based)
  "validation_rules": json,         # Custom validation rules
  "created_at": datetime,
  "updated_at": datetime
}
```

**Field Types (enum):**
- `TEXT` - Single-line text input
- `TEXTAREA` - Multi-line text input
- `NUMBER` - Numeric input
- `EMAIL` - Email address with validation
- `URL` - URL with validation
- `PHONE` - Phone number
- `SELECT` - Dropdown selection (single choice)
- `RADIO` - Radio buttons (single choice)
- `CHECKBOX` - Checkboxes (multiple choices)
- `FILE` - File upload
- `DATE` - Date picker
- `TIME` - Time picker

**Options JSON (for SELECT/RADIO/CHECKBOX):**
```json
["Option 1", "Option 2", "Option 3"]
```

**Validation Rules JSON:**
```json
{
  "min_length": 2,
  "max_length": 100,
  "min": 0,
  "max": 50,
  "pattern": "^[A-Za-z]+$"
}
```

**Relationships:**
- Belongs to: Form
- Has many: SubmissionResponses

---

### 7. Submission Model

**File:** `app/models/submission.py`
**Table:** `submissions`

Form submission record.

```python
{
  "id": integer (PK, auto-increment),
  "form_id": integer (FK -> forms.id, indexed),
  "submitted_by": integer (FK -> users.id, nullable),  # null for anonymous
  "submitted_by_email": string(255),    # For anonymous submissions
  "submitted_by_name": string(200),     # For anonymous submissions
  "status": enum(SubmissionStatus),     # draft, submitted, pending, approved, rejected
  "submission_metadata": json,          # IP address, user agent, location
  "tenant_id": integer (FK -> tenants.id, indexed),
  "created_at": datetime,               # When submission was started
  "submitted_at": datetime,             # When submission was completed
  "updated_at": datetime
}
```

**Status Enum:**
- `draft` - Submission started but not completed
- `submitted` - Submission completed
- `pending` - Awaiting approval
- `approved` - Approved by reviewer
- `rejected` - Rejected by reviewer

**Submission Metadata JSON:**
```json
{
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "location": "New York, USA"
}
```

**Relationships:**
- Belongs to: Form, Tenant, User (submitter, nullable)
- Has many: SubmissionResponses

**Status Lifecycle:**
```
draft → submitted → pending → approved/rejected
```

---

### 8. SubmissionResponse Model

**File:** `app/models/submission.py`
**Table:** `submission_responses`

Individual field response within a submission.

```python
{
  "id": integer (PK, auto-increment),
  "submission_id": integer (FK -> submissions.id, indexed),
  "field_id": integer (FK -> form_fields.id, indexed),
  # Polymorphic value columns (use appropriate one based on field type)
  "value_text": text,               # For TEXT, TEXTAREA, EMAIL, URL, PHONE, SELECT, RADIO
  "value_number": integer,          # For NUMBER
  "value_boolean": boolean,         # For single CHECKBOX (yes/no)
  "value_date": datetime,           # For DATE, TIME
  "value_json": json,               # For multi-select CHECKBOX or complex data
  "file_attachment_id": integer (FK -> file_attachments.id),  # For FILE
  "created_at": datetime,
  "updated_at": datetime
}
```

**Value Column Usage by Field Type:**

| Field Type | Value Column |
|------------|--------------|
| TEXT | value_text |
| TEXTAREA | value_text |
| EMAIL | value_text |
| URL | value_text |
| PHONE | value_text |
| NUMBER | value_number |
| SELECT (single) | value_text |
| RADIO | value_text |
| CHECKBOX (single) | value_boolean |
| CHECKBOX (multiple) | value_json (array) |
| DATE | value_date |
| TIME | value_date |
| FILE | file_attachment_id |

**Relationships:**
- Belongs to: Submission, FormField, FileAttachment (nullable)

---

### 9. FormApproval Model

**File:** `app/models/form_approval.py`
**Table:** `form_approvals`

Form approval assignment and tracking.

```python
{
  "id": integer (PK, auto-increment),
  "form_id": integer (FK -> forms.id, indexed),
  "assigned_to": integer (FK -> users.id),      # Reviewer
  "assigned_by": integer (FK -> users.id),      # Assigner
  "status": enum,                               # pending, approved, rejected
  "comments": text,                             # Reviewer notes
  "tenant_id": integer (FK -> tenants.id, indexed),
  "assigned_at": datetime,
  "reviewed_at": datetime,                      # When review was completed
  "approved_at": datetime,
  "rejected_at": datetime
}
```

**Status Values:**
- `pending` - Awaiting review
- `approved` - Form approved
- `rejected` - Form rejected

**Relationships:**
- Belongs to: Form, Tenant
- References: assigned_to User, assigned_by User

**Workflow:**
1. Form creator assigns form to reviewer (assigned_by → assigned_to)
2. Status set to "pending"
3. Reviewer approves or rejects with comments
4. Timestamp recorded (approved_at or rejected_at)

---

### 10. FileAttachment Model

**File:** `app/models/file_attachment.py`
**Table:** `file_attachments`

File upload storage metadata.

```python
{
  "id": integer (PK, auto-increment),
  "original_filename": string(255),     # User's original filename
  "stored_filename": string(255),       # Unique server filename
  "file_path": string(500),             # Full path on server
  "file_size": biginteger,              # Size in bytes
  "mime_type": string(100),             # MIME type (e.g., application/pdf)
  "uploaded_by": integer (FK -> users.id),
  "tenant_id": integer (FK -> tenants.id, indexed),
  "uploaded_at": datetime
}
```

**File Upload Configuration (from `app/core/config.py`):**
- Max upload size: 10MB (10,485,760 bytes)
- Allowed MIME types:
  - `image/jpeg`
  - `image/png`
  - `application/pdf`
  - `application/msword`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Upload directory: `./uploads` (configurable)

**Relationships:**
- Belongs to: User (uploader), Tenant
- Referenced by: SubmissionResponses (for FILE field type)

**File Naming:**
- stored_filename should be unique (UUID + extension recommended)
- Prevents filename collisions and enhances security

---

### 11. AuditLog Model

**File:** `app/models/audit_log.py`
**Table:** `audit_logs`

Complete audit trail for compliance and debugging.

```python
{
  "id": integer (PK, auto-increment),
  "user_id": integer (FK -> users.id, indexed),
  "action": string(100),                # Indexed: create, update, delete, login
  "resource_type": string(50),          # Indexed: form, user, submission
  "resource_id": integer,               # ID of affected resource
  "description": text,                  # Human-readable description
  "changes": json,                      # Before/after values
  "ip_address": string(45),             # IPv4 or IPv6
  "user_agent": string(500),
  "tenant_id": integer (FK -> tenants.id, indexed),
  "created_at": datetime                # Indexed
}
```

**Common Actions:**
- `login` - User login
- `logout` - User logout
- `create` - Resource created
- `update` - Resource updated
- `delete` - Resource deleted
- `approve` - Submission approved
- `reject` - Submission rejected
- `assign` - Form assigned for approval

**Changes JSON Structure:**
```json
{
  "before": {
    "status": "pending",
    "title": "Old Title"
  },
  "after": {
    "status": "approved",
    "title": "New Title"
  }
}
```

**Relationships:**
- Belongs to: User, Tenant

**Purpose:**
- Compliance (GDPR, HIPAA, etc.)
- Security monitoring
- Debugging and troubleshooting
- User activity tracking

---

## Authentication & Authorization

### JWT Token Structure

**Implementation:** `app/core/security.py`

#### Access Token (30 minutes default)

```json
{
  "user_id": 123,
  "tenant_id": 456,
  "email": "user@example.com",
  "roles": ["admin", "editor"],
  "exp": 1730545800,
  "iat": 1730544000,
  "type": "access"
}
```

#### Refresh Token (7 days default)

```json
{
  "user_id": 123,
  "tenant_id": 456,
  "exp": 1731148800,
  "iat": 1730544000,
  "type": "refresh"
}
```

**Token Configuration:**
- Algorithm: HS256
- Secret Key: Configured via `SECRET_KEY` environment variable
- Access Token Expiry: 30 minutes (configurable)
- Refresh Token Expiry: 7 days (configurable)

### Password Hashing

**Implementation:** `app/core/security.py`

```python
# Argon2 (OWASP recommended)
# Fallback to bcrypt if Argon2 unavailable
# Cost factor: 12 (bcrypt) or default Argon2 parameters
```

**Security Features:**
- Argon2id algorithm (memory-hard, side-channel resistant)
- Automatic salt generation
- Password verification with timing attack protection

### Authentication Dependencies

**File:** `app/api/deps.py`

#### 1. `get_current_user(token: str)`

Extracts and validates JWT token, returns User object.

```python
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Validates JWT token and returns authenticated user.
    Automatically sets tenant context for request.
    """
```

**Process:**
1. Extract token from Authorization header
2. Verify token signature
3. Check token expiry
4. Extract user_id and tenant_id from payload
5. Fetch user from database
6. Set tenant context for request
7. Return User object

**Raises:**
- `401 Unauthorized` - Invalid or expired token
- `401 Unauthorized` - User not found

---

#### 2. `get_current_active_user(current_user: User)`

Ensures user account is active.

```python
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Checks if authenticated user is active.
    """
```

**Raises:**
- `403 Forbidden` - User account is inactive

---

#### 3. `require_permission(permission: str)`

Dependency factory for permission-based access control.

```python
def require_permission(permission: str):
    """
    Dependency factory that checks if user has specific permission.

    Args:
        permission: Permission in format "resource.action" (e.g., "forms.create")

    Returns:
        Dependency function that validates permission
    """
```

**Usage in Routes:**
```python
@router.post(
    "/forms",
    dependencies=[Depends(require_permission("forms.create"))]
)
async def create_form(...):
    pass
```

**Process:**
1. Get current active user
2. Check if user is superuser (bypass all checks)
3. Fetch user's roles
4. Fetch permissions for those roles
5. Check if permission exists
6. Return user if authorized

**Raises:**
- `403 Forbidden` - User lacks required permission

---

#### 4. `get_current_superuser(current_user: User)`

Ensures user is a platform superuser.

```python
async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Checks if user is a platform superuser.
    """
```

**Raises:**
- `403 Forbidden` - User is not a superuser

---

### Pagination & Search Parameters

**File:** `app/api/deps.py`

#### PaginationParams

Dependency for standardized pagination across all list endpoints.

```python
class PaginationParams:
    skip: int = 0        # Offset (>= 0)
    limit: int = 20      # Page size (1-100)
```

**Usage:**
```python
@router.get("/items")
async def list_items(pagination: Annotated[PaginationParams, Depends()]):
    items = await repository.get_all(
        skip=pagination.skip,
        limit=pagination.limit
    )
```

---

#### SearchParams

Dependency for search and sorting.

```python
class SearchParams:
    q: str | None = None          # Search query (min 1 char)
    sort_by: str = "created_at"   # Sort field
    order: str = "asc" | "desc"   # Sort order
```

**Usage:**
```python
@router.get("/items")
async def list_items(
    search: Annotated[SearchParams, Depends()],
    pagination: Annotated[PaginationParams, Depends()]
):
    items = await repository.search(
        query=search.q,
        sort_by=search.sort_by,
        order=search.order,
        skip=pagination.skip,
        limit=pagination.limit
    )
```

---

### OAuth2 Configuration

**File:** `app/api/deps.py:16`

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
```

**Token URL:** `/api/v1/auth/login`
**Scheme:** Bearer authentication
**Header Format:** `Authorization: Bearer <access_token>`

---

## Multi-Tenancy Architecture

### Tenant Isolation Strategy

**Approach:** Shared database, shared schema with automatic row-level filtering

**Key Principles:**
1. Every tenant-scoped table has `tenant_id` column (indexed)
2. Tenant ID extracted from JWT token during authentication
3. Set in context variable via `set_current_tenant_id()`
4. All database queries automatically filtered by `tenant_id`
5. Repository pattern applies tenant filter transparently

### Tenant Context Middleware

**File:** `app/middleware/tenant_context.py`

```python
# Context variable to store current tenant ID
_tenant_context_var: ContextVar[Optional[int]] = ContextVar('tenant_id', default=None)

def set_current_tenant_id(tenant_id: int) -> None:
    """Set current tenant ID for request context"""
    _tenant_context_var.set(tenant_id)

def get_current_tenant_id() -> Optional[int]:
    """Get current tenant ID from request context"""
    return _tenant_context_var.get()
```

**Usage Flow:**
1. User authenticates → JWT contains `tenant_id`
2. `get_current_user()` extracts `tenant_id` from token
3. `set_current_tenant_id(tenant_id)` stores in context
4. Repository layer automatically applies: `.filter(Model.tenant_id == get_current_tenant_id())`
5. User can only access data from their tenant

### Security Considerations

**Data Isolation:**
- Users cannot access other tenants' data
- Returns `404 Not Found` (not `403 Forbidden`) when accessing other tenant's resources
- Prevents information disclosure

**Tables with Tenant Isolation:**
- `users`
- `forms`
- `form_fields` (through form relationship)
- `submissions`
- `submission_responses` (through submission relationship)
- `form_approvals`
- `file_attachments`
- `audit_logs`
- `roles`

**Global Tables (No tenant_id):**
- `tenants` (the tenant registry itself)
- `permissions` (shared across all tenants)

### Tenant Subdomain

**Format:** `{subdomain}.infield.com`

**Examples:**
- `acme.infield.com` → tenant_id: 1
- `techcorp.infield.com` → tenant_id: 2

**Subdomain Resolution:**
- Extract subdomain from request host
- Look up tenant by subdomain
- Use tenant_id for authentication and filtering

---

## Configuration

### Environment Variables

**File:** `app/core/config.py`

Configuration is loaded from `.env` file in project root.

### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | "Infield API" | Application name |
| `DEBUG` | boolean | False | Debug mode (development only) |
| `API_VERSION` | string | "v1" | API version |

### Database

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | postgresql+asyncpg://... | Async PostgreSQL connection string |

**Format:** `postgresql+asyncpg://user:password@host:port/database`

### Security

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECRET_KEY` | string | *must change* | JWT signing key (keep secret!) |
| `ALGORITHM` | string | "HS256" | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | 30 | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | int | 7 | Refresh token lifetime |

### CORS

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `BACKEND_CORS_ORIGINS` | string | localhost:3000,localhost:5173 | Comma-separated allowed origins |

**Example:** `https://app.example.com,https://admin.example.com`

### Redis & Celery

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CELERY_BROKER_URL` | string | redis://localhost:6379/0 | Celery message broker |
| `REDIS_URL` | string | redis://localhost:6379/0 | Redis cache URL |

### Email

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EMAIL_FROM` | string | noreply@infield.com | Sender email address |
| `SMTP_HOST` | string | - | SMTP server hostname |
| `SMTP_PORT` | int | 587 | SMTP server port |
| `SMTP_USER` | string | - | SMTP username |
| `SMTP_PASSWORD` | string | - | SMTP password |

### File Upload

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `UPLOAD_DIR` | string | ./uploads | File upload directory |
| `MAX_UPLOAD_SIZE` | int | 10485760 | Max file size in bytes (10MB) |

### Rate Limiting

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RATE_LIMIT_PER_MINUTE` | int | 60 | API requests per minute per user |

### Pagination

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEFAULT_PAGE_SIZE` | int | 20 | Default pagination limit |
| `MAX_PAGE_SIZE` | int | 100 | Maximum pagination limit |

### Monitoring

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SENTRY_DSN` | string | None | Sentry error tracking DSN |

### Example .env File

```bash
# App
APP_NAME=Infield API
DEBUG=False
API_VERSION=v1

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/infield

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis & Celery
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_FROM=noreply@infield.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Monitoring
SENTRY_DSN=
```

---

## Auto-Generated Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

**URL:** `http://localhost:8000/docs`

**Features:**
- Interactive API explorer
- "Try it out" functionality for testing endpoints
- Request/response examples
- Authentication support (Bearer token)
- Download OpenAPI specification

**Configuration:** `app/main.py:35`

---

### ReDoc

**URL:** `http://localhost:8000/redoc`

**Features:**
- Clean, responsive documentation interface
- Three-panel layout
- Code samples in multiple languages
- Search functionality

**Configuration:** `app/main.py:36`

---

### OpenAPI JSON Schema

**URL:** `http://localhost:8000/openapi.json`

**Purpose:**
- Machine-readable API specification
- Can be used to generate client SDKs
- Import into Postman, Insomnia, etc.

**Configuration:** `app/main.py:37`

---

## Implementation Roadmap

### Current Status

**✅ Completed (~60%):**
- Complete database schema (11 models)
- Authentication infrastructure (JWT, Argon2)
- Multi-tenancy architecture with freemium pricing
- Configuration management
- Docker deployment setup
- Auto-generated API documentation
- Middleware and CORS configuration
- Comprehensive documentation
- **✅ Phase 1: Core Authentication (COMPLETED)**
- **✅ Phase 1.5: Tenant Management (COMPLETED)**
- **✅ Phase 3: Form Management (COMPLETED)**

**❌ Pending (~40%):**
- Phase 2: User Management API endpoints
- Phase 4: Form Submission API endpoints
- Phase 5: Role & Permission Management API
- File upload endpoints
- Background tasks (email notifications)
- Unit and integration tests
- Payment integration for plan upgrades

---

### Phase 1: Core Authentication ✅ COMPLETED

**Priority:** HIGH
**Status:** ✅ Implemented

**Completed Tasks:**
1. ✅ Created `app/api/v1/auth.py`
   - ✅ Register endpoint with user limit checking
   - ✅ Login endpoint with password verification
   - ✅ Refresh token endpoint
   - ✅ Get current user endpoint
2. ✅ Created `app/services/auth_service.py`
   - ✅ Registration logic with validation
   - ✅ Login logic with Argon2 password verification
   - ✅ Token generation and refresh
   - ✅ Organization signup with admin user creation
3. ✅ Tested authentication flow with Swagger UI

**Files Created:**
- ✅ `app/api/v1/auth.py` (4 endpoints)
- ✅ `app/services/auth_service.py` (6 functions)
- ✅ `app/schemas/auth.py` (request/response schemas)

---

### Phase 1.5: Tenant Management (Self-Service SaaS) ✅ COMPLETED

**Priority:** HIGH
**Status:** ✅ Implemented

**Completed Tasks:**
1. ✅ Designed freemium pricing model (FREE, PRO, ADVANCED, ENTERPRISE)
2. ✅ Created `app/schemas/tenant.py`
   - ✅ TenantCreate, TenantUpdate, TenantResponse schemas
   - ✅ OrganizationSignupRequest with subdomain validation
3. ✅ Created `app/services/tenant_service.py`
   - ✅ Tenant creation with plan limits
   - ✅ User limit checking
   - ✅ Form limit checking
   - ✅ Plan upgrade functionality
4. ✅ Created `app/api/v1/tenants.py`
   - ✅ Self-service organization signup (public endpoint)
   - ✅ Get my tenant endpoint
   - ✅ Update my tenant endpoint (admin only)
   - ✅ Get tenant by ID endpoint (admin only)
5. ✅ Updated Tenant model with PlanType enum and helper methods
6. ✅ Implemented automatic admin role creation with all permissions

**Files Created:**
- ✅ `app/api/v1/tenants.py` (4 endpoints)
- ✅ `app/services/tenant_service.py` (9 functions)
- ✅ `app/schemas/tenant.py` (schemas with validation)
- ✅ Updated `app/models/tenant.py` (added PlanType enum)

**Business Logic Implemented:**
- ✅ Self-service signup creates both tenant and admin user atomically
- ✅ FREE plan enforces 1 user, 3 forms limit
- ✅ Subdomain validation with reserved name checking
- ✅ Direct SQL inserts to avoid lazy loading in async context

---

### Phase 2: User Management ❌ PENDING

**Priority:** HIGH
**Status:** ❌ Not Implemented

**Tasks:**
1. Create `app/api/v1/users.py`
   - Implement list users endpoint (with pagination/search)
   - Implement create user endpoint (invite user to tenant)
   - Implement get user by ID endpoint
   - Implement update user endpoint
   - Implement delete user endpoint
2. Create `app/services/user_service.py`
   - User CRUD operations
   - User search and filtering
3. Implement permission checks for user management

**Files to Create:**
- `app/api/v1/users.py`
- `app/services/user_service.py`

---

### Phase 3: Form Management ✅ COMPLETED

**Priority:** HIGH
**Status:** ✅ Implemented

**Completed Tasks:**
1. ✅ Created form Pydantic schemas in `app/schemas/form.py`
   - ✅ FormCreate, FormUpdate, FormResponse
   - ✅ FormFieldCreate, FormFieldResponse
   - ✅ FormListResponse with pagination
   - ✅ FormPublishRequest
2. ✅ Created `app/api/v1/forms.py`
   - ✅ List forms endpoint (with pagination and filtering)
   - ✅ Create form endpoint (with fields and limit checking)
   - ✅ Get form details endpoint (with tenant isolation)
   - ✅ Update form endpoint
   - ✅ Delete form endpoint (soft delete)
   - ✅ Publish/unpublish form endpoint
   - ✅ Add field to form endpoint
3. ✅ Created `app/services/form_service.py`
   - ✅ Form CRUD operations with tenant isolation
   - ✅ Form field creation and validation
   - ✅ Publish/unpublish logic with published_at timestamp
   - ✅ Form limit enforcement based on plan
4. ✅ Tested form creation with limit enforcement

**Files Created:**
- ✅ `app/api/v1/forms.py` (7 endpoints)
- ✅ `app/services/form_service.py` (8 functions)
- ✅ `app/schemas/form.py` (complete schemas)

**Business Logic Implemented:**
- ✅ Automatic tenant isolation in all queries
- ✅ Form creation checks plan limits (blocks 4th form on FREE plan)
- ✅ Eager loading of form fields to avoid N+1 queries
- ✅ Soft delete preserves data integrity

**Files to Continue:**
- `app/schemas/form.py`
- `app/api/v1/forms.py`
- `app/services/form_service.py`
- `app/repositories/form_repository.py`
- `app/services/approval_service.py`
- `app/schemas/form_approval.py`

---

### Phase 4: Submissions (3-4 days)

**Priority:** HIGH

**Tasks:**
1. Create submission Pydantic schemas in `app/schemas/submission.py`
   - SubmissionCreate, SubmissionUpdate, SubmissionResponse
   - SubmissionResponseCreate
2. Create `app/api/v1/submissions.py`
   - Implement submit form endpoint (with validation)
   - Implement list submissions endpoint (with filters)
   - Implement get submission details endpoint
   - Implement approve submission endpoint
   - Implement reject submission endpoint
3. Create `app/services/submission_service.py`
   - Submission creation with field validation
   - Approval/rejection logic
4. Create `app/repositories/submission_repository.py`
   - Complex queries with response relationships

**Files to Create:**
- `app/schemas/submission.py`
- `app/api/v1/submissions.py`
- `app/services/submission_service.py`
- `app/repositories/submission_repository.py`

---

### Phase 5: File Upload (1-2 days)

**Priority:** MEDIUM

**Tasks:**
1. Create `app/api/v1/files.py`
   - Implement file upload endpoint
   - Implement file download endpoint
   - Implement file delete endpoint
2. Create `app/services/file_service.py`
   - File validation (size, type)
   - File storage with unique naming
   - File retrieval with security checks
3. Create `app/schemas/file_attachment.py`

**Files to Create:**
- `app/api/v1/files.py`
- `app/services/file_service.py`
- `app/schemas/file_attachment.py`

---

### Phase 6: Background Tasks (1-2 days)

**Priority:** MEDIUM

**Tasks:**
1. Create `app/tasks/email_tasks.py`
   - Send email notifications for submissions
   - Send approval request emails
   - Send approval/rejection notifications
2. Create `app/tasks/report_tasks.py`
   - Generate submission reports (CSV, PDF)
3. Create `app/tasks/reminder_tasks.py`
   - Send periodic reminders for pending approvals

**Files to Create:**
- `app/tasks/email_tasks.py`
- `app/tasks/report_tasks.py`
- `app/tasks/reminder_tasks.py`

---

### Phase 7: Testing (2-3 days)

**Priority:** MEDIUM

**Tasks:**
1. Write unit tests for services
   - `tests/services/test_auth_service.py`
   - `tests/services/test_user_service.py`
   - `tests/services/test_form_service.py`
   - `tests/services/test_submission_service.py`
2. Write integration tests for API endpoints
   - `tests/api/test_auth.py`
   - `tests/api/test_users.py`
   - `tests/api/test_forms.py`
   - `tests/api/test_submissions.py`
3. Write tenant isolation tests
   - `tests/test_tenant_isolation.py`
4. Write security tests
   - `tests/security/test_authentication.py`
   - `tests/security/test_permissions.py`

**Files to Create:**
- Multiple test files in `tests/` directory

---

### Phase 8: Polish & Documentation (1 day)

**Priority:** LOW

**Tasks:**
1. Add API response examples to all endpoints
2. Add comprehensive docstrings
3. Update README with deployment instructions
4. Create API usage examples
5. Create Postman collection

**Files to Update:**
- All route files (add examples)
- README.md
- Create: DEPLOYMENT.md
- Create: API_EXAMPLES.md

---

### Total Timeline

| Phase | Duration | Priority | Dependencies |
|-------|----------|----------|--------------|
| 1. Core Authentication | 2-3 days | HIGH | None |
| 2. User Management | 1-2 days | HIGH | Phase 1 |
| 3. Form Management | 3-4 days | HIGH | Phase 1, 2 |
| 4. Submissions | 3-4 days | HIGH | Phase 1, 2, 3 |
| 5. File Upload | 1-2 days | MEDIUM | Phase 1, 4 |
| 6. Background Tasks | 1-2 days | MEDIUM | Phase 1-5 |
| 7. Testing | 2-3 days | MEDIUM | Phase 1-6 |
| 8. Polish | 1 day | LOW | Phase 1-7 |

**Total Estimated Time:** 14-21 days
**Minimum Viable Product (MVP):** 11-16 days (Phases 1-5)

---

### Next Immediate Steps

1. **Connect API router to main app**
   - Uncomment line 85 in `app/main.py`: `app.include_router(api_router, prefix="/api/v1")`

2. **Create API router file**
   - Create `app/api/v1/router.py` to aggregate all route modules

3. **Start with Phase 1**
   - Implement authentication endpoints
   - Test thoroughly with Swagger UI before moving to Phase 2

4. **Iterative Development**
   - Complete one phase before moving to the next
   - Test each phase thoroughly
   - Ensure tenant isolation works correctly at each step

---

## API Design Best Practices

### Followed in This API

✅ **RESTful Design** - Standard HTTP methods (GET, POST, PUT, DELETE)
✅ **Consistent URL Structure** - `/api/v1/{resource}/{id}`
✅ **Versioned API** - `/api/v1/` prefix
✅ **Pagination** - Standardized skip/limit parameters
✅ **Search & Filtering** - Query parameters for filtering
✅ **Proper Status Codes** - 200, 201, 400, 401, 403, 404
✅ **JWT Authentication** - Industry-standard bearer tokens
✅ **Permission-Based Access Control** - Fine-grained permissions
✅ **Multi-Tenancy** - Automatic tenant isolation
✅ **Audit Logging** - Complete audit trail
✅ **Auto-Generated Documentation** - Swagger/ReDoc
✅ **Validation** - Pydantic schema validation
✅ **Error Handling** - Consistent error responses

---

## Security Best Practices

### Implemented

✅ **Password Hashing** - Argon2 (OWASP recommended)
✅ **JWT Tokens** - Short-lived access tokens, long-lived refresh tokens
✅ **Multi-Tenancy** - Row-level security with automatic filtering
✅ **Permission System** - Role-based access control (RBAC)
✅ **SQL Injection Protection** - Parameterized queries (SQLAlchemy ORM)
✅ **CORS Configuration** - Whitelist allowed origins
✅ **Audit Logging** - Complete audit trail for compliance

### Planned

⏳ **Rate Limiting** - Prevent abuse
⏳ **Input Sanitization** - XSS protection
⏳ **File Upload Validation** - MIME type and size checks
⏳ **MFA Support** - Two-factor authentication
⏳ **Email Verification** - Verify user email addresses
⏳ **Password Reset** - Secure password recovery
⏳ **Security Headers** - X-Frame-Options, CSP, etc.
⏳ **Refresh Token Rotation** - Enhanced security

---

## Performance Considerations

### Database

✅ **Indexes** - Critical columns indexed (tenant_id, email, foreign keys)
✅ **Async SQLAlchemy** - Non-blocking database queries
✅ **Connection Pooling** - Efficient connection management
⏳ **Query Optimization** - Use `select_related` for eager loading
⏳ **Caching** - Redis for frequently accessed data

### API

✅ **Pagination** - Prevent large result sets
⏳ **Rate Limiting** - Protect against abuse
⏳ **Response Compression** - Gzip compression
⏳ **CDN** - Static file delivery

---

## Monitoring & Observability

### Planned

⏳ **Sentry Integration** - Error tracking and alerting
⏳ **Prometheus Metrics** - Performance metrics
⏳ **Structured Logging** - JSON logs for analysis
⏳ **Health Checks** - Deep health checks for dependencies
⏳ **Celery Flower** - Task queue monitoring

---

## Conclusion

This API is a well-architected foundation for a multi-tenant SaaS form management system. With the database schema, authentication infrastructure, and configuration complete, the primary remaining work is implementing the route handlers and business logic layer.

Once completed, this API will support:
- Multi-tenant form creation and management
- Dynamic form fields with validation
- Form submission and approval workflows
- Role-based access control
- File uploads
- Comprehensive audit logging
- Background task processing

**For Questions or Support:**
- Check the auto-generated documentation at `/docs`
- Review the codebase README and ARCHITECTURE docs
- Inspect the model files for database schema details

---

**Generated:** 2025-11-02
**API Version:** v1
**Framework:** FastAPI
**Python Version:** 3.11+
