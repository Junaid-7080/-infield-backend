"""
User Management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.session import get_db
from app.schemas.user import (
    UserInvite,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from app.services import user_service
from app.api.deps import (
    get_current_active_user,
    require_tenant_admin,
    PaginationParams
)
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/invite",
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def invite_user(
    user_data: UserInvite,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Invite a new user to the tenant (admin only).

    Creates a user account with a temporary password.
    The user will receive an invitation email (when email service is implemented).

    **Required:** Admin role

    **Returns:** User details and temporary password (password should be sent via email in production)

    **Checks:**
    - Email uniqueness
    - Tenant user limit based on subscription plan
    - Role validity

    **Note:** In production, the temporary password should only be sent via email,
    not returned in the response. This is for development/testing purposes.
    """
    user, temp_password = await user_service.invite_user(
        db,
        user_data,
        current_user.tenant_id
    )

    return {
        "user": UserResponse.model_validate(user),
        "temporary_password": temp_password,
        "message": "User invited successfully. Temporary password should be sent via email."
    }


@router.get(
    "",
    response_model=UserListResponse
)
async def list_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by email or full name"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of users in the current tenant.

    **Query Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 20, max: 100)
    - **search**: Search query for email or full name (optional)

    **Returns:** Paginated list of users with total count

    **Tenant Isolation:** Automatically filters users by current user's tenant
    """
    users, total = await user_service.get_users_list(
        db,
        current_user.tenant_id,
        pagination.skip,
        pagination.limit,
        search
    )

    return UserListResponse(
        items=users,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific user by ID.

    **Path Parameters:**
    - **user_id**: User ID

    **Returns:** User details with roles

    **Tenant Isolation:** Only returns user if they belong to the same tenant
    """
    user = await user_service.get_user_by_id(
        db,
        user_id,
        current_user.tenant_id
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user (admin only).

    **Required:** Admin role

    **Path Parameters:**
    - **user_id**: User ID

    **Request Body:** Only specified fields will be updated (partial update)
    - **full_name**: User's full name (optional)
    - **designation**: User's job title (optional)
    - **phone**: User's phone number (optional)
    - **is_active**: Account active status (optional)

    **Returns:** Updated user details

    **Tenant Isolation:** Only updates user if they belong to the same tenant
    """
    user = await user_service.update_user(
        db,
        user_id,
        user_data,
        current_user.tenant_id
    )
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user (soft delete - admin only).

    **Required:** Admin role

    **Path Parameters:**
    - **user_id**: User ID

    **Action:** Sets `is_active=False` instead of permanently deleting

    **Tenant Isolation:** Only deletes user if they belong to the same tenant

    **Note:** User data is preserved for audit purposes
    """
    await user_service.delete_user(
        db,
        user_id,
        current_user.tenant_id
    )
    return None


@router.post(
    "/{user_id}/roles",
    response_model=UserResponse
)
async def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign roles to a user (admin only).

    **Required:** Admin role

    **Path Parameters:**
    - **user_id**: User ID

    **Request Body:**
    - **role_ids**: List of role IDs to assign (replaces existing roles)

    **Returns:** Updated user details with new roles

    **Tenant Isolation:**
    - Only assigns roles to users in the same tenant
    - Only allows tenant-specific or global roles
    """
    user = await user_service.assign_roles_to_user(
        db,
        user_id,
        role_ids,
        current_user.tenant_id
    )
    return user
