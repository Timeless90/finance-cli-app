from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT = json.loads(Path(__file__).with_name("project.json").read_text())


class ApiSettings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="CFO_",
        extra="ignore",
    )

    service_name: str = PROJECT["service_name"]
    telemetry_enabled: bool = False
    otlp_endpoint: str = "http://127.0.0.1:4318"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    build_version: str = "0.3.0"
    azure_region: str | None = None
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    governance_database_path: Path | None = None
    governance_database_url: str | None = None
    import_storage_path: Path = Path(".local/imports")
    rate_limit_requests_per_minute: int = Field(default=0, ge=0)

    @field_validator("governance_database_url", mode="before")
    @classmethod
    def empty_database_url_uses_default(cls, value: object) -> object:
        return None if value == "" else value


@lru_cache(maxsize=1)
def get_settings() -> ApiSettings:
    return ApiSettings()
