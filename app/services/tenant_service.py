"""
Tenant service - business logic for tenant/organization management.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.tenant import Tenant, PlanType
from app.models.user import User
from app.models.form import Form
from app.schemas.tenant import TenantCreate, TenantUpdate


async def validate_subdomain_available(
    db: AsyncSession,
    subdomain: str
) -> bool:
    """
    Check if subdomain is available (not already taken).

    Args:
        db: Database session
        subdomain: Subdomain to check

    Returns:
        True if available, False if taken
    """
    result = await db.execute(
        select(Tenant).where(Tenant.subdomain == subdomain.lower())
    )
    existing_tenant = result.scalar_one_or_none()
    return existing_tenant is None


async def create_tenant(
    db: AsyncSession,
    tenant_data: TenantCreate,
    plan: PlanType = PlanType.FREE
) -> Tenant:
    """
    Create a new tenant/organization.

    Args:
        db: Database session
        tenant_data: Tenant creation data
        plan: Subscription plan (default: FREE)

    Returns:
        Created tenant object

    Raises:
        HTTPException: If subdomain already exists
    """
    # Check subdomain availability
    is_available = await validate_subdomain_available(db, tenant_data.subdomain)
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Subdomain '{tenant_data.subdomain}' is already taken"
        )

    # Prepare tenant data
    tenant_dict = tenant_data.model_dump()

    # Set plan and limits based on plan type
    plan_limits = Tenant.get_plan_limits(plan)
    tenant_dict['plan'] = plan
    tenant_dict['max_users'] = plan_limits['max_users']
    tenant_dict['max_forms'] = plan_limits['max_forms']

    # Trial dates are NULL for regular signups (can be set later for promotional trials)
    tenant_dict['trial_started_at'] = None
    tenant_dict['trial_ends_at'] = None

    # Create tenant
    new_tenant = Tenant(**tenant_dict)
    db.add(new_tenant)
    await db.commit()
    await db.refresh(new_tenant)

    return new_tenant


async def get_tenant_by_id(
    db: AsyncSession,
    tenant_id: int
) -> Optional[Tenant]:
    """
    Get tenant by ID.

    Args:
        db: Database session
        tenant_id: Tenant ID

    Returns:
        Tenant object or None
    """
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    return result.scalar_one_or_none()


async def get_tenant_by_subdomain(
    db: AsyncSession,
    subdomain: str
) -> Optional[Tenant]:
    """
    Get tenant by subdomain.

    Args:
        db: Database session
        subdomain: Subdomain to search for

    Returns:
        Tenant object or None
    """
    result = await db.execute(
        select(Tenant).where(Tenant.subdomain == subdomain.lower())
    )
    return result.scalar_one_or_none()


async def update_tenant(
    db: AsyncSession,
    tenant_id: int,
    tenant_data: TenantUpdate
) -> Optional[Tenant]:
    """
    Update tenant information.

    Args:
        db: Database session
        tenant_id: Tenant ID
        tenant_data: Update data

    Returns:
        Updated tenant object or None

    Raises:
        HTTPException: If tenant not found
    """
    tenant = await get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Update fields
    update_data = tenant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)

    return tenant


async def check_user_limit(
    db: AsyncSession,
    tenant_id: int
) -> bool:
    """
    Check if tenant can add more users.

    Args:
        db: Database session
        tenant_id: Tenant ID

    Returns:
        True if within limit, False otherwise

    Raises:
        HTTPException: If tenant not found or user limit exceeded
    """
    tenant = await get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Count current users
    result = await db.execute(
        select(func.count()).select_from(User).where(
            User.tenant_id == tenant_id,
            User.is_active == True
        )
    )
    current_user_count = result.scalar()

    # Check limit
    if not tenant.is_within_user_limit(current_user_count):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User limit reached. Your plan allows maximum {tenant.max_users} users. "
                   f"Please upgrade your plan to add more users."
        )

    return True


async def check_form_limit(
    db: AsyncSession,
    tenant_id: int
) -> bool:
    """
    Check if tenant can create more forms.

    Args:
        db: Database session
        tenant_id: Tenant ID

    Returns:
        True if within limit, False otherwise

    Raises:
        HTTPException: If tenant not found or form limit exceeded
    """
    tenant = await get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Count current forms
    result = await db.execute(
        select(func.count()).select_from(Form).where(
            Form.tenant_id == tenant_id,
            Form.is_active == True
        )
    )
    current_form_count = result.scalar()

    # Check limit
    if not tenant.is_within_form_limit(current_form_count):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Form limit reached. Your plan allows maximum {tenant.max_forms} forms. "
                   f"Please upgrade your plan to create more forms."
        )

    return True


async def deactivate_tenant(
    db: AsyncSession,
    tenant_id: int
) -> Tenant:
    """
    Deactivate a tenant (soft delete).

    Args:
        db: Database session
        tenant_id: Tenant ID

    Returns:
        Deactivated tenant object

    Raises:
        HTTPException: If tenant not found
    """
    tenant = await get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    tenant.is_active = False
    await db.commit()
    await db.refresh(tenant)

    return tenant


async def activate_tenant(
    db: AsyncSession,
    tenant_id: int
) -> Tenant:
    """
    Activate a tenant.

    Args:
        db: Database session
        tenant_id: Tenant ID

    Returns:
        Activated tenant object

    Raises:
        HTTPException: If tenant not found
    """
    tenant = await get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    tenant.is_active = True
    await db.commit()
    await db.refresh(tenant)

    return tenant


async def upgrade_tenant_plan(
    db: AsyncSession,
    tenant_id: int,
    new_plan: PlanType
) -> Tenant:
    """
    Upgrade (or downgrade) a tenant's subscription plan.

    Args:
        db: Database session
        tenant_id: Tenant ID
        new_plan: New plan type

    Returns:
        Updated tenant object

    Raises:
        HTTPException: If tenant not found
    """
    tenant = await get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Get limits for new plan
    plan_limits = Tenant.get_plan_limits(new_plan)

    # Update plan and limits
    tenant.plan = new_plan
    tenant.max_users = plan_limits['max_users']
    tenant.max_forms = plan_limits['max_forms']

    await db.commit()
    await db.refresh(tenant)

    return tenant
