from fastapi.testclient import TestClient

from app.factory import create_app
from app.shared.config import ApiSettings


def test_response_has_request_correlation_and_security_headers() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health/live", headers={"X-Request-ID": "test-request"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_api_rate_limit_is_explicitly_configurable() -> None:
    with TestClient(
        create_app(settings=ApiSettings(rate_limit_requests_per_minute=1))
    ) as client:
        first = client.get("/api/v1/platform")
        limited = client.get("/api/v1/platform")
    assert first.status_code == 200
    assert limited.status_code == 429
    assert limited.headers["Retry-After"] == "60"
