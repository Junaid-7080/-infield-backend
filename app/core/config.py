"""
Application configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All values must be defined in .env file - no hardcoded defaults.
    """

    # Application
    APP_NAME: str
    DEBUG: bool
    API_VERSION: str

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # CORS
    BACKEND_CORS_ORIGINS: str

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Redis
    REDIS_URL: str

    # Email (AWS SES)
    EMAIL_FROM: str
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str

    # File Upload
    UPLOAD_DIR: str
    MAX_UPLOAD_SIZE: int
    ALLOWED_UPLOAD_TYPES: str

    @property
    def allowed_upload_types_list(self) -> list[str]:
        """Parse allowed upload types from comma-separated string"""
        return [t.strip() for t in self.ALLOWED_UPLOAD_TYPES.split(",")]

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int

    # Pagination
    DEFAULT_PAGE_SIZE: int
    MAX_PAGE_SIZE: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
