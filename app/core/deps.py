"""FastAPI dependencies."""

from fastapi import Request
from app.core.config import Settings


def get_settings(request: Request) -> Settings:
    """Expose Settings via FastAPI dependency."""
    return request.app.state.settings

