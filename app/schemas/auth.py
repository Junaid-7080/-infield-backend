"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = Field(None, max_length=200)
    designation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    tenant_id: int = Field(..., description="Tenant/Organization ID")


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str
