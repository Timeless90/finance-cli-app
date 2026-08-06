from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="CFO_",
        env_file=".env",
        extra="ignore",
    )

    service_name: str = "cfo-platform-api"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    build_version: str = "0.3.0"
    azure_region: str | None = None
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])


@lru_cache(maxsize=1)
def get_settings() -> ApiSettings:
    return ApiSettings()
