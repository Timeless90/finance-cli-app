from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.api.settings import ApiSettings


def _client() -> TestClient:
    settings = ApiSettings(
        environment="test",
        build_version="test-version",
        allowed_origins=["http://localhost:3000"],
    )
    return TestClient(create_app(settings))


def test_liveness_endpoint() -> None:
    response = _client().get("/health/live")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "cfo-platform-api",
        "environment": "test",
        "version": "test-version",
    }


def test_readiness_endpoint() -> None:
    response = _client().get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_platform_endpoint_is_versioned() -> None:
    response = _client().get("/api/v1/platform")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "CFO Command Center"
    assert payload["api_version"] == "v1"


def test_openapi_schema_is_available() -> None:
    response = _client().get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "CFO Command Center API"
