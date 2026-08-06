from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import build_platform_router, build_system_router
from .settings import ApiSettings, get_settings


def create_app(settings: ApiSettings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    app = FastAPI(
        title="CFO Command Center API",
        version=resolved.build_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.settings = resolved
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(build_system_router(resolved))
    app.include_router(build_platform_router(), prefix=resolved.api_prefix)
    return app
