"""
Main API v1 router - combines all v1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1 import auth, forms, tenants, users, submissions


# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(tenants.router)  # Tenants first (includes public signup)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(forms.router)
api_router.include_router(submissions.router)

# Future routers will be added here:
# api_router.include_router(roles.router)
# api_router.include_router(files.router)
