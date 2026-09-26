"""O&G Agentic Canvas - Configuration Management."""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: AppEnvironment = AppEnvironment.DEVELOPMENT
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_title: str = "Agentic Canvas Platform"
    app_version: str = "1.0.0"

    # Database
    database_url: str = "postgresql+asyncpg://ong_user:ong_dev_password@localhost:5432/ong_agentic_canvas"
    database_url_sync: str = "postgresql+psycopg2://ong_user:ong_dev_password@localhost:5432/ong_agentic_canvas"
    database_echo: bool = False

    # LLM Provider
    llm_provider: str = "gemini"
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    llm_model: str = "gemini-2.5-flash"
    llm_fallback_models: str = "gemini-flash-latest,gemini-2.5-flash-lite,gemini-flash-lite-latest"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4096

    # Embeddings
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"

    # Vector Store
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection: str = "ong_brand_rules"

    # CORS
    cors_allowed_origins: str = "http://localhost:4200"

    # Authentication & Security
    jwt_secret_key: str = "ong_agentic_canvas_super_secret_jwt_key_2026_enterprise_compliance_system"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # Guardrails
    max_repair_attempts: int = 3
    guardrail_pass_threshold: float = 75.0

    # Webhook Alerts
    webhook_alert_url: Optional[str] = None

    # Retry
    max_agent_retries: int = 3
    agent_retry_delay_seconds: float = 1.0

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",")]

    @property
    def is_testing(self) -> bool:
        return self.app_env == AppEnvironment.TESTING


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
