"""
Pydantic schemas for Submission model.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from app.models.submission import SubmissionStatus


class SubmissionResponseCreate(BaseModel):
    """Schema for creating a submission response (answer to a field)"""
    field_id: int
    value_text: Optional[str] = None
    value_number: Optional[int] = None
    value_boolean: Optional[bool] = None
    value_date: Optional[datetime] = None
    value_json: Optional[Dict[str, Any]] = None
    file_attachment_id: Optional[int] = None


class SubmissionResponseData(BaseModel):
    """Schema for submission response data in response"""
    id: int
    field_id: int
    value_text: Optional[str] = None
    value_number: Optional[int] = None
    value_boolean: Optional[bool] = None
    value_date: Optional[datetime] = None
    value_json: Optional[Dict[str, Any]] = None
    file_attachment_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    """Schema for creating a new submission"""
    form_id: int
    responses: List[SubmissionResponseCreate]
    submitted_by_email: Optional[EmailStr] = Field(None, description="Email for anonymous submissions")
    submitted_by_name: Optional[str] = Field(None, max_length=200, description="Name for anonymous submissions")
    submission_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata (IP, user agent, location, etc.)"
    )


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission"""
    status: Optional[SubmissionStatus] = None
    responses: Optional[List[SubmissionResponseCreate]] = None


class SubmissionResponse(BaseModel):
    """Schema for submission response"""
    id: int
    form_id: int
    submitted_by: Optional[int] = None
    submitted_by_email: Optional[str] = None
    submitted_by_name: Optional[str] = None
    status: SubmissionStatus
    submission_metadata: Optional[Dict[str, Any]] = None
    tenant_id: int
    created_at: datetime
    submitted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    responses: List[SubmissionResponseData] = []

    class Config:
        from_attributes = True


class SubmissionWithFormInfo(SubmissionResponse):
    """Schema for submission with form information"""
    form_title: Optional[str] = None
    form_description: Optional[str] = None


class SubmissionListResponse(BaseModel):
    """Schema for paginated submission list"""
    items: List[SubmissionResponse]
    total: int
    skip: int
    limit: int


class SubmissionApprovalRequest(BaseModel):
    """Schema for approving/rejecting a submission"""
    status: SubmissionStatus = Field(..., description="approved or rejected")
    comments: Optional[str] = Field(None, description="Optional approval/rejection comments")

    class Config:
        use_enum_values = True
