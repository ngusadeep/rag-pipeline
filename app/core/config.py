"""Application configuration management."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str

    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_index_name: str = "biasharaplus-rag"
    pinecone_environment: str = "us-east-1-aws"

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/bplus_rag_db"

    # Application Configuration
    app_name: str = "BiasharaPlus RAG Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Admin Default Credentials
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # RAG Configuration
    chunk_size: int = 800
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    llm_temperature: float = 0.0
    llm_model: str = "gpt-4o-mini"
    rag_mode: str = "chain"  # options: "chain" (default) or "agent"

    model_config = SettingsConfigDict(
        # Load .env file from backend/.env
        # Path resolution: app/core/config.py -> app/core -> app -> backend -> .env
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )


# Create settings instance - loads from .env file automatically
settings = Settings()

