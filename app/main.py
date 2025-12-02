"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.init_db import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events (startup and shutdown).
    """
    # Startup
    print(f"\n{'='*60}")
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"{'='*60}")
    print(f"📝 Debug mode: {settings.DEBUG}")
    print(f"🗄️  Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"{'='*60}\n")

    # Initialize database (create tables and seed data)
    try:
        await init_db()
    except Exception as e:
        print(f"\n⚠️  Warning: Database initialization failed: {e}")
        print("   Application will continue but database may not be ready.\n")

    print(f"\n{'='*60}")
    print(f"✅ {settings.APP_NAME} is ready!")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"{'='*60}\n")

    yield

    # Shutdown
    print(f"\n👋 Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Infield - Form Management and Approval System API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
