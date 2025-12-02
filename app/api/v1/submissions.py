"""
Submission API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionListResponse,
    SubmissionApprovalRequest
)
from app.models.submission import SubmissionStatus
from app.services import submission_service
from app.api.deps import (
    get_current_active_user,
    require_tenant_admin,
    PaginationParams
)
from app.models.user import User


router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: Optional[User] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a form (authenticated or anonymous).

    **Authentication:** Optional - supports both authenticated and anonymous submissions

    **Request Body:**
    - **form_id**: ID of the form to submit
    - **responses**: Array of field responses with values
    - **submitted_by_email**: Email for anonymous submissions (optional)
    - **submitted_by_name**: Name for anonymous submissions (optional)
    - **submission_metadata**: Additional metadata like IP, user agent (optional)

    **Validation:**
    - Form must be published
    - All required fields must have responses
    - Multiple submissions checked if disabled

    **Status:**
    - Forms requiring approval: status = PENDING
    - Forms without approval: status = SUBMITTED

    **Returns:** Created submission with all responses
    """
    submission = await submission_service.create_submission(
        db,
        submission_data,
        current_user
    )
    return submission


@router.get(
    "",
    response_model=SubmissionListResponse
)
async def list_submissions(
    pagination: PaginationParams = Depends(),
    form_id: Optional[int] = Query(None, description="Filter by form ID"),
    status_filter: Optional[SubmissionStatus] = Query(None, alias="status", description="Filter by status"),
    submitted_by: Optional[int] = Query(None, description="Filter by submitter user ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of submissions.

    **Authentication:** Required

    **Query Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 20, max: 100)
    - **form_id**: Filter by specific form (optional)
    - **status**: Filter by status (submitted, pending, approved, rejected) (optional)
    - **submitted_by**: Filter by submitter user ID (optional)

    **Tenant Isolation:** Only returns submissions for current user's tenant

    **Returns:** Paginated list of submissions with total count
    """
    submissions, total = await submission_service.get_submissions_list(
        db,
        current_user.tenant_id,
        pagination.skip,
        pagination.limit,
        form_id=form_id,
        status_filter=status_filter,
        submitted_by=submitted_by
    )

    return SubmissionListResponse(
        items=submissions,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse
)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific submission by ID.

    **Authentication:** Required

    **Path Parameters:**
    - **submission_id**: Submission ID

    **Returns:** Submission details with all field responses

    **Tenant Isolation:** Only returns submission if it belongs to current user's tenant
    """
    submission = await submission_service.get_submission_by_id(
        db,
        submission_id,
        current_user.tenant_id
    )

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    return submission


@router.get(
    "/form/{form_id}",
    response_model=SubmissionListResponse
)
async def get_form_submissions(
    form_id: int,
    pagination: PaginationParams = Depends(),
    status_filter: Optional[SubmissionStatus] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all submissions for a specific form.

    **Authentication:** Required

    **Path Parameters:**
    - **form_id**: Form ID

    **Query Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 20)
    - **status**: Filter by status (optional)

    **Returns:** Paginated list of submissions for the form
    """
    submissions, total = await submission_service.get_form_submissions(
        db,
        form_id,
        current_user.tenant_id,
        pagination.skip,
        pagination.limit,
        status_filter=status_filter
    )

    return SubmissionListResponse(
        items=submissions,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.put(
    "/{submission_id}/approve",
    response_model=SubmissionResponse
)
async def approve_or_reject_submission(
    submission_id: int,
    approval_data: SubmissionApprovalRequest,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve or reject a submission (admin only).

    **Required:** Admin role

    **Path Parameters:**
    - **submission_id**: Submission ID

    **Request Body:**
    - **status**: "approved" or "rejected"
    - **comments**: Optional approval/rejection comments

    **Use Cases:**
    - Approve submissions that require approval before processing
    - Reject invalid or inappropriate submissions

    **Returns:** Updated submission with new status

    **Tenant Isolation:** Only allows updating submissions in admin's tenant
    """
    submission = await submission_service.update_submission_status(
        db,
        submission_id,
        approval_data,
        current_user.tenant_id
    )
    return submission


@router.delete(
    "/{submission_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_submission(
    submission_id: int,
    current_user: User = Depends(require_tenant_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a submission (admin only).

    **Required:** Admin role

    **Path Parameters:**
    - **submission_id**: Submission ID

    **Action:** Permanently deletes the submission and all its responses

    **Warning:** This action cannot be undone

    **Tenant Isolation:** Only allows deleting submissions in admin's tenant
    """
    await submission_service.delete_submission(
        db,
        submission_id,
        current_user.tenant_id
    )
    return None
