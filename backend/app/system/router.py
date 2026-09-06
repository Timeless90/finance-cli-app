from __future__ import annotations

from fastapi import APIRouter

from app.shared.config import ApiSettings
from app.system.schemas import (
    HealthResponse,
    ModuleFoundationResponse,
    PlatformResponse,
)


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
        return ModuleFoundationResponse(
            module="forecast", api_version="v1", status="available"
        )

    @router.get("/risk", response_model=ModuleFoundationResponse)
    def risk_foundation() -> ModuleFoundationResponse:
        return ModuleFoundationResponse(
            module="risk", api_version="v1", status="available"
        )

    @router.get("/data", response_model=ModuleFoundationResponse)
    def data_foundation() -> ModuleFoundationResponse:
        return ModuleFoundationResponse(
            module="data", api_version="v1", status="available"
        )

    return router


__all__ = [
    "HealthResponse",
    "ModuleFoundationResponse",
    "PlatformResponse",
    "build_module_foundation_router",
    "build_platform_router",
    "build_system_router",
]
