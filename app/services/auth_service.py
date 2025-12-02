"""
Authentication service - business logic for user authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User, Role, Permission, role_permissions
from app.models.tenant import Tenant, PlanType
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.tenant import OrganizationSignupRequest, TenantCreate
from app.services import tenant_service


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password.

    Args:
        db: Database session
        email: User email
        password: Plain password

    Returns:
        User object if authentication successful, None otherwise
    """
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        return None

    # Check if user is active
    if not user.is_active:
        return None

    return user


async def register_user(db: AsyncSession, registration: RegisterRequest) -> User:
    """
    Register a new user.

    Args:
        db: Database session
        registration: Registration data

    Returns:
        Created user object

    Raises:
        HTTPException: If email already exists or tenant not found
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == registration.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Verify tenant exists and is active
    result = await db.execute(
        select(Tenant).where(Tenant.id == registration.tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant account is not active"
        )

    # Check user limit before creating new user
    await tenant_service.check_user_limit(db, registration.tenant_id)

    # Create new user
    new_user = User(
        email=registration.email,
        hashed_password=get_password_hash(registration.password),
        full_name=registration.full_name,
        designation=registration.designation,
        phone=registration.phone,
        tenant_id=registration.tenant_id,
        is_active=True,
        email_verified=False  # Email verification can be added later
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


def create_tokens_for_user(user: User) -> TokenResponse:
    """
    Create access and refresh tokens for a user.

    Args:
        user: User object

    Returns:
        TokenResponse with access and refresh tokens
    """
    # Token payload
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "sub": user.email  # Subject claim (standard JWT claim)
    }

    # Create tokens
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"user_id": user.id, "sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


async def update_last_login(db: AsyncSession, user: User) -> None:
    """
    Update user's last login timestamp.

    Args:
        db: Database session
        user: User object
    """
    user.last_login_at = datetime.utcnow()
    await db.commit()


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """
    Generate new access token from refresh token.

    Args:
        db: Database session
        refresh_token: Refresh token string

    Returns:
        TokenResponse with new access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify refresh token
    payload = verify_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    return create_tokens_for_user(user)


async def register_organization_admin(
    db: AsyncSession,
    signup_data: OrganizationSignupRequest
) -> tuple[User, Tenant]:
    """
    Register a new organization with an admin user (self-service signup).

    This creates both the tenant (organization) and the first user,
    who becomes the admin of the organization.

    Args:
        db: Database session
        signup_data: Organization signup data

    Returns:
        Tuple of (created user, created tenant)

    Raises:
        HTTPException: If email exists, subdomain taken, or validation fails
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == signup_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create tenant with FREE plan
    tenant_create = TenantCreate(
        name=signup_data.organization_name,
        subdomain=signup_data.subdomain,
        contact_email=signup_data.contact_email or signup_data.email,
        contact_phone=signup_data.contact_phone
    )

    tenant = await tenant_service.create_tenant(
        db=db,
        tenant_data=tenant_create,
        plan=PlanType.FREE  # All new signups start with free plan
    )

    # Find Admin role (should exist from seed data) with permissions
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(
            Role.name == "Admin",
            Role.tenant_id == None  # Global role or first tenant's role
        ).limit(1)
    )
    admin_role = result.scalar_one_or_none()

    # Create admin user
    new_user = User(
        email=signup_data.email,
        hashed_password=get_password_hash(signup_data.password),
        full_name=signup_data.full_name,
        tenant_id=tenant.id,
        is_active=True,
        email_verified=False,
        is_superuser=False  # Admin, not superuser
    )

    db.add(new_user)
    await db.flush()  # Flush to get user ID

    # Create tenant-specific admin role with permissions
    tenant_admin_role = Role(
        name="Admin",
        description="Administrator with full access to tenant resources",
        tenant_id=tenant.id
    )
    db.add(tenant_admin_role)
    await db.flush()  # Flush to get role ID

    # Get all permissions (all permissions in the system)
    result = await db.execute(select(Permission))
    all_permissions = result.scalars().all()

    # Assign all permissions to the new admin role using direct insert to association table
    for permission in all_permissions:
        await db.execute(
            role_permissions.insert().values(
                role_id=tenant_admin_role.id,
                permission_id=permission.id
            )
        )

    # Assign role to user - also use direct insert to avoid lazy loading
    from app.models.user import user_roles
    await db.execute(
        user_roles.insert().values(
            user_id=new_user.id,
            role_id=tenant_admin_role.id
        )
    )

    await db.commit()
    await db.refresh(new_user)
    await db.refresh(tenant)

    return new_user, tenant
