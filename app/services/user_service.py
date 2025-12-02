"""
User service - business logic for user management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import secrets
import string

from app.models.user import User, Role, user_roles
from app.schemas.user import UserInvite, UserUpdate
from app.core.security import get_password_hash
from app.services import tenant_service


def generate_random_password(length: int = 12) -> str:
    """
    Generate a secure random password.

    Args:
        length: Password length (default: 12)

    Returns:
        Random password string
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


async def invite_user(
    db: AsyncSession,
    user_data: UserInvite,
    tenant_id: int
) -> tuple[User, str]:
    """
    Invite a new user to the tenant (admin function).

    Creates a user account with a random password and sends invitation email.

    Args:
        db: Database session
        user_data: User invitation data
        tenant_id: Tenant ID

    Returns:
        Tuple of (created user, temporary password)

    Raises:
        HTTPException: If email exists, tenant not found, or user limit exceeded
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Check user limit
    await tenant_service.check_user_limit(db, tenant_id)

    # Generate temporary password
    temp_password = generate_random_password()

    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(temp_password),
        full_name=user_data.full_name,
        designation=user_data.designation,
        phone=user_data.phone,
        tenant_id=tenant_id,
        is_active=True,
        email_verified=False
    )

    db.add(new_user)
    await db.flush()  # Get user ID

    # Assign roles if provided
    if user_data.role_ids:
        for role_id in user_data.role_ids:
            # Verify role exists and belongs to tenant or is global
            role_result = await db.execute(
                select(Role).where(
                    Role.id == role_id,
                    or_(Role.tenant_id == tenant_id, Role.tenant_id == None)
                )
            )
            role = role_result.scalar_one_or_none()

            if role:
                await db.execute(
                    user_roles.insert().values(
                        user_id=new_user.id,
                        role_id=role_id
                    )
                )

    await db.commit()
    await db.refresh(new_user)

    # TODO: Send invitation email with temporary password
    # This should be implemented with a background task

    return new_user, temp_password


async def get_users_list(
    db: AsyncSession,
    tenant_id: int,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None
) -> tuple[List[User], int]:
    """
    Get paginated list of users for a tenant.

    Args:
        db: Database session
        tenant_id: Tenant ID for isolation
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search query for email or full_name

    Returns:
        Tuple of (list of users, total count)
    """
    # Build query
    query = select(User).where(User.tenant_id == tenant_id)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results with eager loading of roles
    query = (
        query
        .options(selectinload(User.roles))
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    users = result.scalars().all()

    return list(users), total


async def get_user_by_id(
    db: AsyncSession,
    user_id: int,
    tenant_id: int
) -> Optional[User]:
    """
    Get a user by ID (with tenant isolation).

    Args:
        db: Database session
        user_id: User ID
        tenant_id: Tenant ID for isolation

    Returns:
        User object or None
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(
            User.id == user_id,
            User.tenant_id == tenant_id
        )
    )
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_data: UserUpdate,
    tenant_id: int
) -> User:
    """
    Update a user.

    Args:
        db: Database session
        user_id: User ID
        user_data: Update data
        tenant_id: Tenant ID for isolation

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found
    """
    user = await get_user_by_id(db, user_id, tenant_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


async def delete_user(
    db: AsyncSession,
    user_id: int,
    tenant_id: int
) -> bool:
    """
    Delete a user (soft delete by setting is_active=False).

    Args:
        db: Database session
        user_id: User ID
        tenant_id: Tenant ID for isolation

    Returns:
        True if deleted

    Raises:
        HTTPException: If user not found
    """
    user = await get_user_by_id(db, user_id, tenant_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete
    user.is_active = False
    await db.commit()

    return True


async def assign_roles_to_user(
    db: AsyncSession,
    user_id: int,
    role_ids: List[int],
    tenant_id: int
) -> User:
    """
    Assign roles to a user (replaces existing roles).

    Args:
        db: Database session
        user_id: User ID
        role_ids: List of role IDs to assign
        tenant_id: Tenant ID for isolation

    Returns:
        Updated user object

    Raises:
        HTTPException: If user or roles not found
    """
    user = await get_user_by_id(db, user_id, tenant_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Remove existing roles
    await db.execute(
        user_roles.delete().where(user_roles.c.user_id == user_id)
    )

    # Add new roles
    for role_id in role_ids:
        # Verify role exists and belongs to tenant or is global
        role_result = await db.execute(
            select(Role).where(
                Role.id == role_id,
                or_(Role.tenant_id == tenant_id, Role.tenant_id == None)
            )
        )
        role = role_result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {role_id} not found"
            )

        await db.execute(
            user_roles.insert().values(
                user_id=user_id,
                role_id=role_id
            )
        )

    await db.commit()
    await db.refresh(user)

    return user
