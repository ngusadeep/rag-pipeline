"""FastAPI entrypoint for the RAG Pipeline API."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
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
        # Ensure vector store (Zvec) and document folders exist
        settings.documents_path.mkdir(parents=True, exist_ok=True)
        get_vector_store()
        logging.getLogger(__name__).info(
            "Application started; Zvec vector store ready."
        )

    app.include_router(api_router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
