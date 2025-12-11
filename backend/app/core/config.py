"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # FastAPI metadata
    app_name: str = "BiasharaPlus RAG API"
    app_description: str = (
        "RAG over BiasharaPlus docs using FastAPI, LangChain, ChromaDB, and OpenAI."
    )
    app_version: str = "0.1.0"
    app_author: str = "iPF Softwares"

    # OpenAI
    openai_api_key: str
    openai_api_base: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Chroma / data
    chroma_api_key: Optional[str] = None  # kept for future remote deployments
    chroma_tenant: Optional[str] = None
    chroma_database: str = "./data/chroma"
    chroma_collection_name: str = "bplus-rag"
    data_directory: str = "./data/documents"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_database).expanduser().resolve()

    @property
    def documents_path(self) -> Path:
        return Path(self.data_directory).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
