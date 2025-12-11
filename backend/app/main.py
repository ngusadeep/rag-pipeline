"""FastAPI entrypoint for the BiasharaPlus RAG API."""

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.logging_config import configure_logging
from app.core.security import get_password_hash
from app.models.user import User
from app.services.vector_store import get_vector_store


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        contact={"name": settings.app_author},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _startup_event() -> None:
        # Initialize database
        # Ensure data directory exists for SQLite
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        if db_path.parent != Path("."):
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        Base.metadata.create_all(bind=engine)
        logger = logging.getLogger(__name__)
        
        # Create default admin user if it doesn't exist
        db: Session = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == settings.admin_email).first()
            if not admin_user:
                admin_user = User(
                    email=settings.admin_email,
                    hashed_password=get_password_hash(settings.admin_password),
                    is_active=True,
                    is_admin=True,
                )
                db.add(admin_user)
                db.commit()
                logger.info(f"Created default admin user: {settings.admin_email}")
            else:
                logger.info(f"Admin user already exists: {settings.admin_email}")
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            db.rollback()
        finally:
            db.close()
        
        # Configure LangSmith tracing if enabled
        tracing_config = settings._get_tracing_config()
        tracing_enabled = tracing_config["tracing"] and tracing_config["tracing"].lower() == "true"
        
        if tracing_enabled:
            if tracing_config["api_key"]:
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
                os.environ["LANGCHAIN_API_KEY"] = tracing_config["api_key"]
                
                if tracing_config["project"]:
                    os.environ["LANGCHAIN_PROJECT"] = tracing_config["project"]
                
                if tracing_config["endpoint"]:
                    os.environ["LANGCHAIN_ENDPOINT"] = tracing_config["endpoint"]
                
                project_name = tracing_config["project"] or "default"
                endpoint_info = f" (endpoint: {tracing_config['endpoint']})" if tracing_config["endpoint"] else ""
                logger.info(
                    f"LangSmith tracing enabled (project: {project_name}{endpoint_info})"
                )
            else:
                logger.warning(
                    "LangSmith tracing is enabled but API key is not set. Tracing disabled."
                )
        
        # Ensure vector store is initialised and data folders exist
        settings.documents_path.mkdir(parents=True, exist_ok=True)
        get_vector_store()
        logger.info("Application started; vector store ready.")

    app.include_router(api_router)
    return app


app = create_app()
