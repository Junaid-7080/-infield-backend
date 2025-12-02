"""
Common dependencies for API routes.
"""
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.db.session import get_db
from app.core.security import verify_token
from app.models.user import User, Role
from app.middleware.tenant_context import set_current_tenant_id, get_current_tenant_id

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify and decode token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Fetch user from database with eager loading of roles and permissions
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        .where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # Set tenant context for this request
    set_current_tenant_id(user.tenant_id)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (convenience dependency).

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user object

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission: str):
    """
    Dependency factory for permission checking.

    Args:
        permission: Required permission (e.g., "forms.create")

    Returns:
        Dependency function that checks permission

    Usage:
        @router.post("/forms", dependencies=[Depends(require_permission("forms.create"))])
    """
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        # Get all permissions for user's roles
        user_permissions = [
            f"{perm.resource}.{perm.action}"
            for role in current_user.roles
            for perm in role.permissions
        ]

        # Check if user has required permission
        if permission not in user_permissions and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required"
            )

        return current_user

    return permission_checker


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current superuser.

    Args:
        current_user: Current user from get_current_active_user

    Returns:
        Superuser object

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    return current_user


class PaginationParams:
    """
    Common pagination parameters.

    Usage:
        pagination: PaginationParams = Depends()
    """
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(20, ge=1, le=100, description="Number of records to return")
    ):
        self.skip = skip
        self.limit = limit


class SearchParams:
    """
    Common search and sorting parameters.

    Usage:
        search: SearchParams = Depends()
    """
    def __init__(
        self,
        q: Optional[str] = Query(None, min_length=1, description="Search query"),
        sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
        order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
    ):
        self.query = q
        self.sort_by = sort_by
        self.order = order


async def require_tenant_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Require user to be a tenant admin.

    Checks if the user has the "Admin" role for their tenant.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if user is admin

    Raises:
        HTTPException: If user is not a tenant admin

    Usage:
        @router.post("/endpoint", dependencies=[Depends(require_tenant_admin)])
    """
    # Check if user has Admin role
    is_admin = any(role.name == "Admin" for role in current_user.roles)

    if not is_admin and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Only tenant administrators can perform this action."
        )

    return current_user
