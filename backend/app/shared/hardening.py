"""Local production-hardening middleware with explicit configuration.

The in-process limiter is appropriate for a single local/UAT process only.
Production deployments must replace it with a distributed gateway limiter.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from time import monotonic
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.shared.observability.setup import request_id as request_id_context


class RequestHardeningMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, requests_per_minute: int) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._limit = requests_per_minute
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID", "").strip() or str(uuid4())
        if self._limit > 0 and request.url.path.startswith("/api/"):
            client = request.client.host if request.client else "unknown"
            now = monotonic()
            recent = self._requests[client]
            while recent and now - recent[0] >= 60:
                recent.popleft()
            if len(recent) >= self._limit:
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "rate limit exceeded", "request_id": request_id},
                    headers={"Retry-After": "60"},
                )
                return self._harden(response, request_id)
            recent.append(now)
        token = request_id_context.set(request_id)
        try:
            response = await call_next(request)
            logging.getLogger("app.request").info(
                "%s %s %s", request.method, request.url.path, response.status_code
            )
            return self._harden(response, request_id)
        finally:
            request_id_context.reset(token)

    @staticmethod
    def _harden(response: Response, request_id: str) -> Response:
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response
