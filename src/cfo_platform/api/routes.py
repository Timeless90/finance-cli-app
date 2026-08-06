from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .settings import ApiSettings


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


def build_system_router(settings: ApiSettings) -> APIRouter:
    router = APIRouter(tags=["system"])

    @router.get("/health/live", response_model=HealthResponse)
    def liveness() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=settings.service_name,
            environment=settings.environment,
            version=settings.build_version,
        )

    @router.get("/health/ready", response_model=HealthResponse)
    def readiness() -> HealthResponse:
        return HealthResponse(
            status="ready",
            service=settings.service_name,
            environment=settings.environment,
            version=settings.build_version,
        )

    return router


def build_platform_router() -> APIRouter:
    router = APIRouter(prefix="/platform", tags=["platform"])

    @router.get("", response_model=PlatformResponse)
    def platform_info() -> PlatformResponse:
        return PlatformResponse(
            name="CFO Command Center",
            api_version="v1",
            capabilities=[
                "enterprise-domain",
                "model-execution-ports",
                "planning-foundation",
                "risk-foundation",
                "background-jobs",
            ],
        )

    return router


def build_module_foundation_router() -> APIRouter:
    router = APIRouter(tags=["module-foundation"])

    @router.get("/forecast", response_model=ModuleFoundationResponse)
    def forecast_foundation() -> ModuleFoundationResponse:
        return ModuleFoundationResponse(module="forecast", api_version="v1", status="available")

    @router.get("/risk", response_model=ModuleFoundationResponse)
    def risk_foundation() -> ModuleFoundationResponse:
        return ModuleFoundationResponse(module="risk", api_version="v1", status="available")

    @router.get("/data", response_model=ModuleFoundationResponse)
    def data_foundation() -> ModuleFoundationResponse:
        return ModuleFoundationResponse(module="data", api_version="v1", status="available")

    return router
