"""Simple structured logging configuration."""

import logging
from typing import Optional

from .config import get_settings


def configure_logging(level: Optional[str] = None) -> None:
    settings = get_settings()
    logging_level = (level or settings.log_level).upper()
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
