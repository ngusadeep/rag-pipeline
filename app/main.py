"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import engine, Base
from app.routes import query, admin
from app.services.auth import AuthService
from app.core.database import SessionLocal
import structlog

# Configure logging
configure_logging(settings.log_level)
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="BiasharaPlus Customer Support AI Agent with RAG",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store settings in app state
app.state.settings = settings

# Include routers
app.include_router(query.router)
app.include_router(admin.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and create default admin on startup."""
    logger.info("Starting application", version=settings.app_version)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Create default admin user
    db = SessionLocal()
    try:
        AuthService.create_default_admin(db)
    finally:
        db.close()
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

