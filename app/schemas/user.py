"""
Pydantic schemas for User model.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class RoleInfo(BaseModel):
    """Schema for role information in user response"""
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=200)
    designation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserInvite(BaseModel):
    """Schema for inviting a new user (admin invites user to tenant)"""
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=200)
    designation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_ids: Optional[List[int]] = Field(default_factory=list, description="Role IDs to assign to user")


class UserCreate(UserBase):
    """Schema for creating a new user (with password)"""
    password: str = Field(..., min_length=8)
    tenant_id: int


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = Field(None, max_length=200)
    designation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    tenant_id: int
    is_active: bool
    is_superuser: bool
    email_verified: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    roles: List[RoleInfo] = []

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    items: list[UserResponse]
    total: int
    skip: int
    limit: int
