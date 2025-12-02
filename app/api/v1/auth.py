"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserResponse
from app.services import auth_service
from app.api.deps import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    registration: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: User's full name (optional)
    - **designation**: Job title/position (optional)
    - **phone**: Contact number (optional)
    - **tenant_id**: Organization ID

    Returns JWT access and refresh tokens for immediate login.
    """
    # Create user
    user = await auth_service.register_user(db, registration)

    # Update last login
    await auth_service.update_last_login(db, user)

    # Generate tokens
    tokens = auth_service.create_tokens_for_user(user)

    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.

    OAuth2 compatible token login, use username field for email.

    - **username**: User's email address (use email here)
    - **password**: User's password

    Returns JWT access and refresh tokens.
    """
    # Authenticate user (username field contains email)
    user = await auth_service.authenticate_user(
        db,
        form_data.username,  # OAuth2 uses 'username' but we treat it as email
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    await auth_service.update_last_login(db, user)

    # Generate tokens
    tokens = auth_service.create_tokens_for_user(user)

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token

    Returns new JWT access and refresh tokens.
    """
    tokens = await auth_service.refresh_access_token(db, refresh_request.refresh_token)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.

    Requires valid JWT access token in Authorization header.

    Returns user profile information.
    """
    return current_user
