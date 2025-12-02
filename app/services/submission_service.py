"""
Submission service - business logic for form submissions.
"""
from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status

from app.models.submission import Submission, SubmissionResponse, SubmissionStatus
from app.models.form import Form, FormField, FieldType
from app.models.file_attachment import FileAttachment
from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionUpdate, SubmissionApprovalRequest
from app.utils.signature import (
    validate_base64,
    base64_to_png,
    validate_signature_size,
    save_signature_file,
    generate_signature_filename,
    SignatureValidationError
)
from app.core.config import settings


# Custom error classes for validation

class TableValidationError(ValueError):
    """Raised when table data validation fails"""
    pass


class SignatureValidationErrorWrapper(ValueError):
    """Raised when signature validation fails"""
    pass


# Validation functions for new field types

def validate_table_field_submission(field: FormField, data: Any) -> bool:
    """
    Validate table field submission data.

    Args:
        field: FormField with type TABLE and field_config
        data: List of row objects from submission

    Returns:
        True if valid

    Raises:
        TableValidationError: If validation fails
    """
    if data is None:
        if field.required:
            raise TableValidationError(f"Table field '{field.label}' is required")
        return True

    # Must be a list
    if not isinstance(data, list):
        raise TableValidationError(
            f"Table field '{field.label}' expects an array of rows, got {type(data).__name__}"
        )

    table_config = field.field_config
    if not table_config:
        raise TableValidationError(f"Table field '{field.label}' missing configuration")

    columns = table_config.get('columns', [])
    if not columns:
        raise TableValidationError(f"Table field '{field.label}' has no columns defined")

    min_rows = table_config.get('minRows', table_config.get('min_rows'))
    max_rows = table_config.get('maxRows', table_config.get('max_rows'))

    # Validate row count
    row_count = len(data)

    if min_rows is not None and row_count < min_rows:
        raise TableValidationError(
            f"Table field '{field.label}' requires minimum {min_rows} rows, got {row_count}"
        )

    if max_rows is not None and row_count > max_rows:
        raise TableValidationError(
            f"Table field '{field.label}' allows maximum {max_rows} rows, got {row_count}"
        )

    # Validate each row
    for row_index, row in enumerate(data, 1):
        if not isinstance(row, dict):
            raise TableValidationError(
                f"Row {row_index} in table '{field.label}' must be an object, got {type(row).__name__}"
            )

        # Validate required columns
        for column in columns:
            column_id = column.get('id')
            column_label = column.get('label', column_id)
            is_required = column.get('required', False)

            if is_required:
                value = row.get(column_id)
                if value is None or (isinstance(value, str) and not value.strip()):
                    raise TableValidationError(
                        f"Required column '{column_label}' is missing or empty in row {row_index}"
                    )

    return True


async def process_signature_field_submission(
    field: FormField,
    base64_data: str,
    user_id: int,
    tenant_id: int,
    db: AsyncSession
) -> int:
    """
    Process signature field submission.
    Converts base64 to PNG file and returns file_attachment_id.

    Args:
        field: FormField with type SIGNATURE
        base64_data: Base64 encoded signature from frontend
        user_id: Current user ID
        tenant_id: Current tenant ID
        db: Database session

    Returns:
        file_attachment_id: ID of created file attachment

    Raises:
        SignatureValidationErrorWrapper: If signature is invalid or too large
    """
    try:
        # Validate base64 format
        if not validate_base64(base64_data):
            raise SignatureValidationError("Invalid base64 signature data")

        # Validate size (5MB default)
        validate_signature_size(base64_data)

        # Convert to PNG bytes
        png_bytes = base64_to_png(base64_data)

        # Generate filename
        filename = generate_signature_filename(user_id, field.id, tenant_id)

        # Save file
        upload_dir = f"{settings.UPLOAD_DIR}/signatures"
        file_path = save_signature_file(png_bytes, filename, upload_dir)

        # Create FileAttachment record
        file_attachment = FileAttachment(
            original_filename=f"signature_{field.label}.png",
            stored_filename=filename,
            file_path=file_path,
            file_size=len(png_bytes),
            mime_type="image/png",
            uploaded_by=user_id,
            tenant_id=tenant_id
        )

        db.add(file_attachment)
        await db.flush()  # Get the ID

        return file_attachment.id

    except SignatureValidationError as e:
        raise SignatureValidationErrorWrapper(str(e))
    except Exception as e:
        raise SignatureValidationErrorWrapper(f"Failed to process signature: {str(e)}")


def validate_section_field_submission(field: FormField, data: Any) -> bool:
    """
    Validate section field submission.
    Section fields don't store data themselves - their nested fields do.

    Args:
        field: FormField with type SECTION
        data: Should be None or empty

    Returns:
        True (sections are just containers)
    """
    # Sections are UI containers and don't store data
    # Their nested fields submit as separate field responses
    return True


async def create_submission(
    db: AsyncSession,
    submission_data: SubmissionCreate,
    current_user: Optional[User] = None,
    tenant_id: Optional[int] = None
) -> Submission:
    """
    Create a new form submission.

    Supports both authenticated and anonymous submissions.

    Args:
        db: Database session
        submission_data: Submission data with responses
        current_user: Current authenticated user (optional for anonymous)
        tenant_id: Tenant ID (required for anonymous submissions)

    Returns:
        Created submission object

    Raises:
        HTTPException: If form not found, not published, or validation fails
    """
    # Get form with fields
    result = await db.execute(
        select(Form)
        .options(selectinload(Form.fields))
        .where(Form.id == submission_data.form_id)
    )
    form = result.scalar_one_or_none()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Check if form is published
    if not form.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Form is not published and cannot accept submissions"
        )

    # Determine tenant_id
    if current_user:
        tenant_id = current_user.tenant_id
    elif not tenant_id:
        # For anonymous submissions, use form's tenant
        tenant_id = form.tenant_id

    # Check if multiple submissions are allowed
    if not form.allow_multiple_submissions and current_user:
        # Check if user already submitted
        existing_result = await db.execute(
            select(Submission).where(
                and_(
                    Submission.form_id == form.id,
                    Submission.submitted_by == current_user.id
                )
            )
        )
        existing_submission = existing_result.scalar_one_or_none()

        if existing_submission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted this form. Multiple submissions are not allowed."
            )

    # Validate required fields
    field_ids = {field.id: field for field in form.fields}
    response_field_ids = {resp.field_id for resp in submission_data.responses}

    # Check for required fields
    for field in form.fields:
        if field.required and field.id not in response_field_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Required field '{field.label}' (ID: {field.id}) is missing"
            )

    # Create submission
    new_submission = Submission(
        form_id=form.id,
        submitted_by=current_user.id if current_user else None,
        submitted_by_email=submission_data.submitted_by_email,
        submitted_by_name=submission_data.submitted_by_name,
        status=SubmissionStatus.PENDING if form.requires_approval else SubmissionStatus.SUBMITTED,
        submission_metadata=submission_data.submission_metadata,
        tenant_id=tenant_id,
        submitted_at=datetime.utcnow()
    )

    db.add(new_submission)
    await db.flush()  # Get submission ID

    # Create responses
    for response_data in submission_data.responses:
        # Validate field exists
        if response_data.field_id not in field_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid field ID: {response_data.field_id}"
            )

        field = field_ids[response_data.field_id]

        # Validate and process field-specific data
        try:
            if field.field_type == FieldType.TABLE:
                # Validate table data structure
                validate_table_field_submission(field, response_data.value_json)

            elif field.field_type == FieldType.SIGNATURE:
                # Process signature: convert base64 to PNG file
                if response_data.value_text:
                    file_id = await process_signature_field_submission(
                        field=field,
                        base64_data=response_data.value_text,
                        user_id=current_user.id if current_user else None,
                        tenant_id=tenant_id,
                        db=db
                    )
                    # Store file reference instead of base64
                    response_data.file_attachment_id = file_id
                    response_data.value_text = None  # Clear base64 data

            elif field.field_type == FieldType.SECTION:
                # Validate section field (no-op, sections don't store data)
                validate_section_field_submission(field, None)

        except TableValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except SignatureValidationErrorWrapper as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        response = SubmissionResponse(
            submission_id=new_submission.id,
            field_id=response_data.field_id,
            value_text=response_data.value_text,
            value_number=response_data.value_number,
            value_boolean=response_data.value_boolean,
            value_date=response_data.value_date,
            value_json=response_data.value_json,
            file_attachment_id=response_data.file_attachment_id
        )
        db.add(response)

    await db.commit()

    # Reload with responses
    result = await db.execute(
        select(Submission)
        .options(selectinload(Submission.responses))
        .where(Submission.id == new_submission.id)
    )
    submission_with_responses = result.scalar_one()

    return submission_with_responses


async def get_submissions_list(
    db: AsyncSession,
    tenant_id: int,
    skip: int = 0,
    limit: int = 20,
    form_id: Optional[int] = None,
    status_filter: Optional[SubmissionStatus] = None,
    submitted_by: Optional[int] = None
) -> tuple[List[Submission], int]:
    """
    Get paginated list of submissions for a tenant.

    Args:
        db: Database session
        tenant_id: Tenant ID for isolation
        skip: Number of records to skip
        limit: Maximum number of records to return
        form_id: Filter by specific form (optional)
        status_filter: Filter by status (optional)
        submitted_by: Filter by submitter user ID (optional)

    Returns:
        Tuple of (list of submissions, total count)
    """
    # Build query
    query = select(Submission).where(Submission.tenant_id == tenant_id)

    # Apply filters
    if form_id:
        query = query.where(Submission.form_id == form_id)

    if status_filter:
        query = query.where(Submission.status == status_filter)

    if submitted_by:
        query = query.where(Submission.submitted_by == submitted_by)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results with eager loading
    query = (
        query
        .options(selectinload(Submission.responses))
        .order_by(Submission.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    submissions = result.scalars().all()

    return list(submissions), total


async def get_submission_by_id(
    db: AsyncSession,
    submission_id: int,
    tenant_id: int
) -> Optional[Submission]:
    """
    Get a submission by ID (with tenant isolation).

    Args:
        db: Database session
        submission_id: Submission ID
        tenant_id: Tenant ID for isolation

    Returns:
        Submission object or None
    """
    result = await db.execute(
        select(Submission)
        .options(
            selectinload(Submission.responses).selectinload(SubmissionResponse.field),
            selectinload(Submission.form)
        )
        .where(
            and_(
                Submission.id == submission_id,
                Submission.tenant_id == tenant_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_form_submissions(
    db: AsyncSession,
    form_id: int,
    tenant_id: int,
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[SubmissionStatus] = None
) -> tuple[List[Submission], int]:
    """
    Get all submissions for a specific form.

    Args:
        db: Database session
        form_id: Form ID
        tenant_id: Tenant ID for isolation
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by status (optional)

    Returns:
        Tuple of (list of submissions, total count)
    """
    # Verify form exists and belongs to tenant
    form_result = await db.execute(
        select(Form).where(
            and_(
                Form.id == form_id,
                Form.tenant_id == tenant_id
            )
        )
    )
    form = form_result.scalar_one_or_none()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return await get_submissions_list(
        db,
        tenant_id,
        skip,
        limit,
        form_id=form_id,
        status_filter=status_filter
    )


async def update_submission_status(
    db: AsyncSession,
    submission_id: int,
    approval_data: SubmissionApprovalRequest,
    tenant_id: int
) -> Submission:
    """
    Update submission status (approve/reject).

    Args:
        db: Database session
        submission_id: Submission ID
        approval_data: Approval/rejection data
        tenant_id: Tenant ID for isolation

    Returns:
        Updated submission object

    Raises:
        HTTPException: If submission not found or invalid status transition
    """
    submission = await get_submission_by_id(db, submission_id, tenant_id)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    # Validate status transition
    valid_statuses = [SubmissionStatus.APPROVED, SubmissionStatus.REJECTED]
    if approval_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join([s.value for s in valid_statuses])}"
        )

    submission.status = approval_data.status
    await db.commit()
    await db.refresh(submission)

    return submission


async def delete_submission(
    db: AsyncSession,
    submission_id: int,
    tenant_id: int
) -> bool:
    """
    Delete a submission.

    Args:
        db: Database session
        submission_id: Submission ID
        tenant_id: Tenant ID for isolation

    Returns:
        True if deleted

    Raises:
        HTTPException: If submission not found
    """
    submission = await get_submission_by_id(db, submission_id, tenant_id)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    await db.delete(submission)
    await db.commit()

    return True
