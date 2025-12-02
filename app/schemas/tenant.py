"""
Tenant schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class TenantBase(BaseModel):
    """Base tenant schema with common fields."""
    name: str = Field(..., min_length=2, max_length=200, description="Organization name")
    contact_email: Optional[str] = Field(None, max_length=255, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    address: Optional[str] = Field(None, description="Organization address")


class TenantCreate(TenantBase):
    """Schema for creating a new tenant."""
    subdomain: str = Field(
        ...,
        min_length=3,
        max_length=63,
        description="Unique subdomain (alphanumeric and hyphens only)"
    )

    @field_validator('subdomain')
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        """Validate subdomain format."""
        # Convert to lowercase
        v = v.lower().strip()

        # Check format: alphanumeric and hyphens, cannot start/end with hyphen
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', v):
            raise ValueError(
                'Subdomain must contain only lowercase letters, numbers, and hyphens. '
                'Cannot start or end with a hyphen.'
            )

        # Reserved subdomains
        reserved = ['www', 'api', 'admin', 'app', 'mail', 'ftp', 'localhost', 'test', 'demo']
        if v in reserved:
            raise ValueError(f'Subdomain "{v}" is reserved')

        return v


class TenantUpdate(BaseModel):
    """Schema for updating tenant information."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class TenantResponse(TenantBase):
    """Schema for tenant response."""
    id: int
    subdomain: str
    is_active: bool
    plan: str
    max_users: int
    max_forms: int
    trial_started_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationSignupRequest(BaseModel):
    """
    Schema for organization signup (creates tenant + admin user in one step).

    This is used for self-service SaaS signup where the first user
    creates their organization and becomes the admin.
    """
    # Organization details
    organization_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Organization/Company name"
    )
    subdomain: str = Field(
        ...,
        min_length=3,
        max_length=63,
        description="Unique subdomain for your organization"
    )

    # Admin user details
    email: str = Field(..., description="Admin user email address")
    password: str = Field(..., min_length=8, description="Admin user password")
    full_name: Optional[str] = Field(None, max_length=200, description="Admin user full name")

    # Optional organization contact info
    contact_email: Optional[str] = Field(None, description="Organization contact email")
    contact_phone: Optional[str] = Field(None, description="Organization contact phone")

    @field_validator('subdomain')
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        """Validate subdomain format."""
        v = v.lower().strip()

        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', v):
            raise ValueError(
                'Subdomain must contain only lowercase letters, numbers, and hyphens. '
                'Cannot start or end with a hyphen.'
            )

        reserved = ['www', 'api', 'admin', 'app', 'mail', 'ftp', 'localhost', 'test', 'demo']
        if v in reserved:
            raise ValueError(f'Subdomain "{v}" is reserved')

        return v


class OrganizationSignupResponse(BaseModel):
    """Response after successful organization signup."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    tenant: TenantResponse
    user_id: int
    email: str

    class Config:
        from_attributes = True
