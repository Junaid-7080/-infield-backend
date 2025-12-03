"""
Database session management with async SQLAlchemy.
"""
from typing import AsyncGenerator
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Fix DATABASE_URL to use asyncpg driver for async support
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with connection pooling for non-SQLite databases
url_obj = make_url(database_url)

engine_kwargs = {
    "echo": settings.DEBUG,
}

if not url_obj.drivername.startswith("sqlite"):
    engine_kwargs.update(
        pool_size=10,       # Connections to keep open
        max_overflow=20,    # Additional connections above pool_size
        pool_timeout=30,    # Seconds to wait for connection
        pool_recycle=1800,  # Recycle connections after 30 minutes
        pool_pre_ping=True, # Test connections before using
    )

engine = create_async_engine(
    database_url,  # Use fixed URL here
    **engine_kwargs,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides database session to routes.

    Yields:
        AsyncSession: Database session

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()