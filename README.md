<<<<<<< HEAD
# Infield Backend API

FastAPI-based backend for Infield form management and approval system.

## Features

- **Multi-tenant SaaS Architecture** - Isolated data per organization
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **Role-Based Access Control (RBAC)** - Granular permissions system
- **Form Builder** - Dynamic form creation with multiple field types
- **Approval Workflows** - Form assignment and approval tracking
- **File Uploads** - Support for attachments
- **Audit Logging** - Complete activity tracking
- **Async/Await** - High-performance async database operations
- **PostgreSQL** - Robust relational database
- **Docker** - Containerized deployment
- **Celery** - Background task processing
- **API Documentation** - Auto-generated Swagger/ReDoc docs

## Technology Stack

- **FastAPI** 0.109+ - Modern async web framework
- **SQLAlchemy** 2.0+ - Async ORM
- **PostgreSQL** 15+ - Database
- **Redis** - Caching and Celery broker
- **Celery** - Background tasks
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Docker** - Containerization

## Project Structure

```
infield_backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Common dependencies
│   │   └── v1/                  # API version 1
│   │       ├── router.py        # Main router
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── users.py         # User management
│   │       ├── forms.py         # Form endpoints
│   │       └── submissions.py   # Submission endpoints
│   ├── core/
│   │   ├── config.py            # Settings
│   │   └── security.py          # Security utilities
│   ├── db/
│   │   ├── base.py              # Model imports
│   │   └── session.py           # Database session
│   ├── models/                  # SQLAlchemy models
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── form.py
│   │   ├── submission.py
│   │   ├── form_approval.py
│   │   ├── file_attachment.py
│   │   └── audit_log.py
│   ├── schemas/                 # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── form.py
│   │   └── submission.py
│   ├── services/                # Business logic
│   ├── repositories/            # Data access layer
│   ├── middleware/              # Custom middleware
│   └── main.py                  # Application entry point
├── alembic/                     # Database migrations
├── tests/                       # Test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+ (if running without Docker)

### Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd infield_backend
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Update `.env` with your settings** (especially `SECRET_KEY`)

4. **Start all services:**
   ```bash
   docker-compose up -d
   ```

5. **Check logs:**
   ```bash
   docker-compose logs -f api
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Flower (Celery monitoring): http://localhost:5555

### Option 2: Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Start PostgreSQL and Redis** (via Docker or locally)

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **In another terminal, start Celery worker:**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

## Database Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback one migration:
```bash
alembic downgrade -1
```

### View migration history:
```bash
alembic history
```

### Create migration manually:
```bash
alembic revision -m "Description"
# Edit the generated file in alembic/versions/
```

## Environment Variables

Key environment variables (see `.env.example` for complete list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | **Change in production!** |
| `DEBUG` | Debug mode | `False` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry | `30` |
| `CELERY_BROKER_URL` | Redis URL for Celery | Required |

## API Documentation

### Auto-generated documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Main Endpoints:

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

#### Users
- `GET /api/v1/users` - List users (paginated)
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

#### Forms
- `GET /api/v1/forms` - List forms
- `POST /api/v1/forms` - Create form
- `GET /api/v1/forms/{id}` - Get form details
- `PUT /api/v1/forms/{id}` - Update form
- `DELETE /api/v1/forms/{id}` - Delete form
- `POST /api/v1/forms/{id}/assign` - Assign for approval

#### Submissions
- `POST /api/v1/forms/{id}/submit` - Submit form
- `GET /api/v1/submissions` - List submissions
- `GET /api/v1/submissions/{id}` - Get submission
- `PUT /api/v1/submissions/{id}/approve` - Approve
- `PUT /api/v1/submissions/{id}/reject` - Reject

## Testing

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file:
```bash
pytest tests/unit/test_security.py
```

### Run integration tests only:
```bash
pytest tests/integration/
```

## Database Schema

### Core Tables:

1. **tenants** - Organizations/tenants
2. **users** - User accounts
3. **roles** - RBAC roles
4. **permissions** - Granular permissions
5. **forms** - Form definitions
6. **form_fields** - Form field configurations
7. **submissions** - Form responses
8. **submission_responses** - Individual field answers
9. **form_approvals** - Approval workflow tracking
10. **file_attachments** - Uploaded files
11. **audit_logs** - Activity tracking

### Relationships:

- Tenants have many Users, Forms
- Users belong to one Tenant, have many Roles
- Roles have many Permissions
- Forms have many FormFields, Submissions
- Submissions have many SubmissionResponses

## Multi-Tenancy

The application uses a **shared database, shared schema** approach with tenant isolation:

- Every tenant-specific table has a `tenant_id` column
- Tenant context is automatically set from JWT token
- All queries are automatically filtered by `tenant_id`
- Row-level security prevents data leakage

## Security Features

- **Password Hashing**: Argon2 (OWASP recommended)
- **JWT Tokens**: Secure token-based authentication
- **RBAC**: Role-based access control
- **MFA**: Optional two-factor authentication
- **Rate Limiting**: Prevent abuse
- **Security Headers**: XSS, CSRF protection
- **Tenant Isolation**: Automatic data separation
- **Audit Logging**: Complete activity trail

## Production Deployment

### Before deploying:

1. **Change SECRET_KEY** in `.env`
2. **Set DEBUG=False**
3. **Use proper CORS origins**
4. **Set up SSL/TLS (HTTPS)**
5. **Configure proper database backups**
6. **Set up monitoring (Sentry)**
7. **Configure email service (AWS SES)**
8. **Use proper reverse proxy (Nginx)**

### Docker Production:

```bash
docker-compose -f docker-compose.yml up -d
```

### Scale workers:

```bash
docker-compose up -d --scale celery_worker=4
```

## Monitoring

- **Health Check**: `/health` endpoint
- **Celery Flower**: http://localhost:5555
- **Application Logs**: JSON structured logging
- **Sentry**: Error tracking (configure SENTRY_DSN)

## Troubleshooting

### Database connection issues:
```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs db

# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
```

### Migration issues:
```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head
```

### Celery not processing tasks:
```bash
# Check Celery worker logs
docker-compose logs celery_worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

## Development

### Code formatting:
```bash
black app tests
isort app tests
```

### Linting:
```bash
flake8 app tests
mypy app
```

### Pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files
```

## Contributing

1. Create a feature branch
2. Make changes
3. Write tests
4. Run test suite
5. Format code
6. Submit pull request

## License

Proprietary - All rights reserved

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: http://localhost:8000/docs
- Email: support@infield.com
"# -infield-backend" 
=======
# infield_backend
Fastapi backend 
>>>>>>> 54ee5dc6f14e94b7bd5627ff5cdc919d777bc332
