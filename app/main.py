from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    contact={"name": settings.app_author},
)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)


app.include_router(api_router, prefix="/api")
