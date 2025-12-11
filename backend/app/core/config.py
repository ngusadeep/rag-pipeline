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

    # LangSmith tracing (optional)
    # Supports both LANGSMITH_* and LANGCHAIN_* naming conventions
    langchain_tracing_v2: Optional[str] = None  # Set to "true" to enable
    langchain_api_key: Optional[str] = None  # LangSmith API key
    langchain_project: Optional[str] = None  # Project name in LangSmith
    langchain_endpoint: Optional[str] = None  # LangSmith endpoint (optional)
    
    # Alternative naming: LANGSMITH_* variables (mapped to LANGCHAIN_*)
    langsmith_tracing: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None
    langsmith_endpoint: Optional[str] = None
    
    # Authentication
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # Default admin user (created on startup if doesn't exist)
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    
    # Database
    database_url: str = "sqlite:///./data/users.db"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_database).expanduser().resolve()

    @property
    def documents_path(self) -> Path:
        return Path(self.data_directory).expanduser().resolve()
    
    def _get_tracing_config(self) -> dict[str, Optional[str]]:
        """Get tracing configuration, preferring LANGCHAIN_* over LANGSMITH_*."""
        return {
            "tracing": self.langchain_tracing_v2 or self.langsmith_tracing,
            "api_key": self.langchain_api_key or self.langsmith_api_key,
            "project": self.langchain_project or self.langsmith_project,
            "endpoint": self.langchain_endpoint or self.langsmith_endpoint,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
