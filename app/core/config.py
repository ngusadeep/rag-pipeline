"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # FastAPI metadata
    app_name: str = "BiasharaPlus RAG API"
    app_description: str = (
        "RAG over BiasharaPlus docs using FastAPI, LangChain, Zvec, and OpenAI."
    )
    app_version: str = "0.1.0"
    app_author: str = "iPF Softwares"

    # OpenAI
    openai_api_key: str
    openai_api_base: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Zvec / data
    zvec_database: str = "./data/zvec"
    zvec_collection_name: str = "bplus-rag"
    embedding_dimension: int = 1536  # text-embedding-3-small
    data_directory: str = "./data/documents"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def zvec_path(self) -> Path:
        """Directory for the Zvec collection (one collection per path)."""
        base = Path(self.zvec_database).expanduser().resolve()
        return base / self.zvec_collection_name

    @property
    def documents_path(self) -> Path:
        return Path(self.data_directory).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
