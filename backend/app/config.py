"""Application settings, loaded from environment variables / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Data sources
    fmp_api_key: str = ""
    newsdata_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "stockai/0.1"

    # App
    database_url: str = "sqlite:///./stockai.db"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
