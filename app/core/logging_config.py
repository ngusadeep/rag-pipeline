import logging
from logging.config import dictConfig
from typing import Any

from .config import get_settings


def configure_logging() -> None:
    """Configure basic structured logging for the app."""
    settings = get_settings()
    log_level = settings.log_level.upper()

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
            }
        },
        "root": {"level": log_level, "handlers": ["console"]},
    }
    dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
