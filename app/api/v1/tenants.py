"""
Tenant/Organization Management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.tenant import (
    OrganizationSignupRequest,
    OrganizationSignupResponse,
    TenantResponse,
    TenantUpdate
)
from app.services import auth_service, tenant_service
from app.api.deps import get_current_active_user, require_tenant_admin
from app.models.user import User


router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post(
    "/signup",
    response_model=OrganizationSignupResponse,
    status_code=status.HTTP_201_CREATED
)
async def organization_signup(
    signup_data: OrganizationSignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Self-service organization signup (public endpoint).

    Creates a new organization (tenant) and the first admin user in one step.
    This is the primary signup endpoint for new customers.

    **Process:**
    1. Creates a new tenant/organization with 14-day trial
    2. Creates the first user as the organization admin
    3. Returns JWT tokens for immediate login

    **Trial Details:**
    - 14-day trial with full features
    - During trial: 100 users, 1000 forms allowed
    - After trial: Free plan with 5 users, 10 forms

    **Request Fields:**
    - **organization_name**: Company/organization name
    - **subdomain**: Unique subdomain (e.g., 'acme' for acme.yourdomain.com)
    - **email**: Admin user email
    - **password**: Admin user password (min 8 characters)
    - **full_name**: Admin user full name (optional)
    - **contact_email**: Organization contact email (optional)
    - **contact_phone**: Organization contact phone (optional)

    Returns organization details, user info, and JWT tokens.
    """
    # Register organization and admin user
    user, tenant = await auth_service.register_organization_admin(db, signup_data)

    # Update last login
    await auth_service.update_last_login(db, user)

    # Generate tokens
    tokens = auth_service.create_tokens_for_user(user)

    # Build response
    return OrganizationSignupResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        tenant=TenantResponse.model_validate(tenant),
        user_id=user.id,
        email=user.email
    )


@router.get(
    "/me",
    response_model=TenantResponse
)
async def get_my_tenant(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's tenant/organization details.

    Returns detailed information about the organization the
    authenticated user belongs to.

    **Required:** Valid JWT access token in Authorization header.

    Returns tenant details including:
    - Organization name and subdomain
    - Plan type and trial status
    - User and form limits
    - Contact information
    """
    tenant = await tenant_service.get_tenant_by_id(db, current_user.tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    return tenant


@router.put(
    "/me",
    response_model=TenantResponse,
    dependencies=[Depends(require_tenant_admin)]
)
async def update_my_tenant(
    tenant_data: TenantUpdate,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's tenant/organization information.

    **Required Permission:** Tenant Admin role

    Only organization administrators can update tenant details.
    Regular users will receive a 403 Forbidden error.

    **Updatable Fields:**
    - Organization name
    - Contact email
    - Contact phone
    - Address

    **Note:** Subdomain cannot be changed after creation.
    Plan and limits are managed separately.

    Returns updated tenant information.
    """
    tenant = await tenant_service.update_tenant(
        db,
        current_user.tenant_id,
        tenant_data
    )

    return tenant


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    dependencies=[Depends(require_tenant_admin)]
)
async def get_tenant(
    tenant_id: int,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get tenant details by ID.

    **Required Permission:** Tenant Admin role

    **Tenant Isolation:** Users can only access their own tenant's details.
    Attempting to access another tenant's information will result in 403 Forbidden.

    Returns complete tenant information.
    """
    # Enforce tenant isolation - users can only view their own tenant
    if current_user.tenant_id != tenant_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own organization's details."
        )

    tenant = await tenant_service.get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    return tenant


@router.post(
    "/me/upgrade",
    response_model=TenantResponse
)
async def upgrade_my_tenant_plan(
    new_plan: str,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Upgrade tenant's subscription plan (admin only - for testing).

    **Required:** Admin role

    **Note:** In production, this should be integrated with payment processing.

    **Plans:**
    - free: 1 user, 3 forms
    - pro: 10 users, 30 forms
    - advanced: 100 users, 300 forms
    - enterprise: Unlimited users and forms
    """
    from app.models.tenant import PlanType

    # Map string to enum
    plan_map = {
        "free": PlanType.FREE,
        "pro": PlanType.PRO,
        "advanced": PlanType.ADVANCED,
        "enterprise": PlanType.ENTERPRISE
    }

    if new_plan.lower() not in plan_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {', '.join(plan_map.keys())}"
        )

    tenant = await tenant_service.upgrade_tenant_plan(
        db,
        current_user.tenant_id,
        plan_map[new_plan.lower()]
    )

    return tenant
