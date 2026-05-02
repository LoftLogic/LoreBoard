from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://loreboard:loreboard@localhost:5432/loreboard"
    database_url_sync: str = "postgresql+psycopg2://loreboard:loreboard@localhost:5432/loreboard"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Anthropic
    anthropic_api_key: str = ""
    default_model: str = "claude-opus-4-7"

    # Working memory
    working_memory_ttl: int = 3600

    # Telemetry
    log_level: str = "INFO"
    enable_otel: bool = False
    otel_endpoint: str = "http://localhost:4317"

    # App
    app_env: str = "development"
    secret_key: str = "change-me-in-production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
