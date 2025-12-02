"""
Form Management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.schemas.form import (
    FormCreate,
    FormUpdate,
    FormResponse,
    FormListResponse,
    FormPublishRequest,
    FormFieldCreate,
    FormFieldResponse
)
from app.services import form_service
from app.api.deps import get_current_active_user, PaginationParams, require_permission
from app.models.user import User


router = APIRouter(prefix="/forms", tags=["Forms"])


@router.post(
    "",
    response_model=FormResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("forms.create"))]
)
async def create_form(
    form_data: FormCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new form.

    **Required Permission:** `forms.create`

    - **title**: Form title (max 200 characters)
    - **description**: Form description (optional)
    - **header**: Form header/letterhead configuration (optional JSON)
    - **fields**: Array of form fields
    - **is_published**: Whether form is immediately published (default: false)
    - **allow_multiple_submissions**: Allow multiple submissions (default: true)
    - **requires_approval**: Require approval for submissions (default: false)

    Returns the created form with all fields.
    """
    form = await form_service.create_form(db, form_data, current_user)
    return form


@router.get(
    "",
    response_model=FormListResponse,
    dependencies=[Depends(require_permission("forms.read"))]
)
async def list_forms(
    pagination: PaginationParams = Depends(),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of forms.

    **Required Permission:** `forms.read`

    Query Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 20, max: 100)
    - **is_published**: Filter by published status (optional)

    Returns paginated list of forms with total count.
    """
    forms, total = await form_service.get_forms_list(
        db,
        current_user.tenant_id,
        pagination.skip,
        pagination.limit,
        is_published
    )

    return FormListResponse(
        items=forms,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.get(
    "/{form_id}",
    response_model=FormResponse,
    dependencies=[Depends(require_permission("forms.read"))]
)
async def get_form(
    form_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific form by ID.

    **Required Permission:** `forms.read`

    Returns form details with all fields.
    """
    form = await form_service.get_form_by_id(db, form_id, current_user.tenant_id)

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return form


@router.put(
    "/{form_id}",
    response_model=FormResponse,
    dependencies=[Depends(require_permission("forms.update"))]
)
async def update_form(
    form_id: int,
    form_data: FormUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a form.

    **Required Permission:** `forms.update`

    Only specified fields will be updated (partial update).

    Returns the updated form.
    """
    form = await form_service.update_form(
        db,
        form_id,
        form_data,
        current_user.tenant_id
    )
    return form


@router.delete(
    "/{form_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("forms.delete"))]
)
async def delete_form(
    form_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a form (soft delete).

    **Required Permission:** `forms.delete`

    Sets `is_active=False` instead of permanently deleting.
    """
    await form_service.delete_form(db, form_id, current_user.tenant_id)
    return None


@router.post(
    "/{form_id}/publish",
    response_model=FormResponse,
    dependencies=[Depends(require_permission("forms.update"))]
)
async def publish_form(
    form_id: int,
    publish_data: FormPublishRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish or unpublish a form.

    **Required Permission:** `forms.update`

    - **is_published**: true to publish, false to unpublish

    Published forms are available for submissions.
    """
    form = await form_service.publish_form(
        db,
        form_id,
        current_user.tenant_id,
        publish_data.is_published
    )
    return form


@router.post(
    "/{form_id}/fields",
    response_model=FormFieldResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("forms.update"))]
)
async def add_field_to_form(
    form_id: int,
    field_data: FormFieldCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new field to an existing form.

    **Required Permission:** `forms.update`

    Returns the created field.
    """
    field = await form_service.add_field_to_form(
        db,
        form_id,
        field_data,
        current_user.tenant_id
    )
    return field
