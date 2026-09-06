from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    version: str


class PlatformResponse(BaseModel):
    name: str
    api_version: str
    capabilities: list[str]


class ModuleFoundationResponse(BaseModel):
    module: str
    api_version: str
    status: str
