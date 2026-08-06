from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cfo_platform.composition import ApplicationContainer, build_container

from .data_routes import build_data_router
from .job_routes import build_job_router
from .routes import (
    build_module_foundation_router,
    build_platform_router,
    build_system_router,
)
from .settings import ApiSettings, get_settings


def create_app(
    settings: ApiSettings | None = None,
    container: ApplicationContainer | None = None,
) -> FastAPI:
    resolved = settings or get_settings()
    resolved_container = container or build_container()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        resolved_container.shutdown()

    app = FastAPI(
        title="CFO Command Center API",
        version=resolved.build_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = resolved
    app.state.container = resolved_container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(build_system_router(resolved))
    app.include_router(build_platform_router(), prefix=resolved.api_prefix)
    app.include_router(build_module_foundation_router(), prefix=resolved.api_prefix)
    app.include_router(
        build_job_router(resolved_container.job_manager),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_data_router(resolved_container.finance_data_workflow),
        prefix=resolved.api_prefix,
    )
    return app
