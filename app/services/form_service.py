"""
Form service - business logic for form management.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.form import Form, FormField
from app.models.user import User
from app.schemas.form import FormCreate, FormUpdate, FormFieldCreate
from app.services import tenant_service


async def create_form(
    db: AsyncSession,
    form_data: FormCreate,
    current_user: User
) -> Form:
    """
    Create a new form with fields.

    Args:
        db: Database session
        form_data: Form creation data
        current_user: Current authenticated user

    Returns:
        Created form object

    Raises:
        HTTPException: If form limit exceeded
    """
    # Check form limit before creating
    await tenant_service.check_form_limit(db, current_user.tenant_id)

    # Create form
    new_form = Form(
        title=form_data.title,
        description=form_data.description,
        header=form_data.header,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        is_published=form_data.is_published,
        allow_multiple_submissions=form_data.allow_multiple_submissions,
        requires_approval=form_data.requires_approval
    )

    db.add(new_form)
    await db.flush()

    # Create form fields
    for field_data in form_data.fields:
        form_field = FormField(
            form_id=new_form.id,
            field_type=field_data.field_type,
            label=field_data.label,
            placeholder=field_data.placeholder,
            help_text=field_data.help_text,
            required=field_data.required,
            options=field_data.options,
            order=field_data.order,
            validation_rules=field_data.validation_rules
        )
        db.add(form_field)

    await db.commit()

    # Reload form with fields using eager loading
    result = await db.execute(
        select(Form)
        .options(selectinload(Form.fields))
        .where(Form.id == new_form.id)
    )
    form_with_fields = result.scalar_one()

    return form_with_fields


async def get_form_by_id(
    db: AsyncSession,
    form_id: int,
    tenant_id: int
) -> Optional[Form]:
    """
    Get a form by ID (with tenant isolation).

    Args:
        db: Database session
        form_id: Form ID
        tenant_id: Tenant ID for isolation

    Returns:
        Form object or None
    """
    result = await db.execute(
        select(Form)
        .options(selectinload(Form.fields))
        .where(
            and_(
                Form.id == form_id,
                Form.tenant_id == tenant_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_forms_list(
    db: AsyncSession,
    tenant_id: int,
    skip: int = 0,
    limit: int = 20,
    is_published: Optional[bool] = None
) -> tuple[List[Form], int]:
    """
    Get paginated list of forms for a tenant.

    Args:
        db: Database session
        tenant_id: Tenant ID for isolation
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_published: Filter by published status (optional)

    Returns:
        Tuple of (list of forms, total count)
    """
    # Build query
    query = select(Form).where(Form.tenant_id == tenant_id)

    if is_published is not None:
        query = query.where(Form.is_published == is_published)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results with eager loading
    query = (
        query
        .options(selectinload(Form.fields))
        .order_by(Form.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    forms = result.scalars().all()

    return list(forms), total


async def update_form(
    db: AsyncSession,
    form_id: int,
    form_data: FormUpdate,
    tenant_id: int
) -> Optional[Form]:
    """
    Update a form.

    Args:
        db: Database session
        form_id: Form ID
        form_data: Update data
        tenant_id: Tenant ID for isolation

    Returns:
        Updated form object or None

    Raises:
        HTTPException: If form not found
    """
    # Get form
    form = await get_form_by_id(db, form_id, tenant_id)

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Update fields
    update_data = form_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(form, field, value)

    await db.commit()
    await db.refresh(form)

    return form


async def delete_form(
    db: AsyncSession,
    form_id: int,
    tenant_id: int
) -> bool:
    """
    Delete a form (soft delete by setting is_active=False).

    Args:
        db: Database session
        form_id: Form ID
        tenant_id: Tenant ID for isolation

    Returns:
        True if deleted, False if not found

    Raises:
        HTTPException: If form not found
    """
    form = await get_form_by_id(db, form_id, tenant_id)

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Soft delete
    form.is_active = False
    await db.commit()

    return True


async def publish_form(
    db: AsyncSession,
    form_id: int,
    tenant_id: int,
    is_published: bool = True
) -> Form:
    """
    Publish or unpublish a form.

    Args:
        db: Database session
        form_id: Form ID
        tenant_id: Tenant ID for isolation
        is_published: Publication status

    Returns:
        Updated form object

    Raises:
        HTTPException: If form not found
    """
    form = await get_form_by_id(db, form_id, tenant_id)

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    form.is_published = is_published
    if is_published and not form.published_at:
        form.published_at = datetime.utcnow()

    await db.commit()
    await db.refresh(form)

    return form


async def add_field_to_form(
    db: AsyncSession,
    form_id: int,
    field_data: FormFieldCreate,
    tenant_id: int
) -> FormField:
    """
    Add a field to an existing form.

    Args:
        db: Database session
        form_id: Form ID
        field_data: Field data
        tenant_id: Tenant ID for isolation

    Returns:
        Created form field

    Raises:
        HTTPException: If form not found
    """
    # Verify form exists and belongs to tenant
    form = await get_form_by_id(db, form_id, tenant_id)

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Create field
    new_field = FormField(
        form_id=form_id,
        field_type=field_data.field_type,
        label=field_data.label,
        placeholder=field_data.placeholder,
        help_text=field_data.help_text,
        required=field_data.required,
        options=field_data.options,
        order=field_data.order,
        validation_rules=field_data.validation_rules
    )

    db.add(new_field)
    await db.commit()
    await db.refresh(new_field)

    return new_field
