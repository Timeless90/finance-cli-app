import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from app.factory import create_app
from app.shared.config import ApiSettings
from app.shared.observability.setup import JsonFormatter, request_id
from finance_cli.cli import app as cli


def test_environment_is_explicit_and_does_not_read_old_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path(".env.local").write_text("CFO_SERVICE_NAME=old-local-project\n")
    assert ApiSettings().service_name == "finance-cli-app-backend"


def test_json_logs_correlate_without_request_content():
    token = request_id.set("migration-request")
    try:
        record = logging.LogRecord(
            "app.request", logging.INFO, "", 0, "GET /health/live 200", (), None
        )
        entry = json.loads(JsonFormatter().format(record))
        assert entry["request_id"] == "migration-request"
        assert entry["event"] == "GET /health/live 200"
        assert len(entry["trace_id"]) == 32
    finally:
        request_id.reset(token)


def test_lifespan_removes_telemetry_handler_and_preserves_request_id():
    logger = logging.getLogger("app")
    before = list(logger.handlers)
    with TestClient(
        create_app(ApiSettings(environment="test", telemetry_enabled=False))
    ) as client:
        response = client.get(
            "/health/live", headers={"X-Request-ID": "test-migration"}
        )
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == "test-migration"
    assert logger.handlers == before


def test_installed_cli_entrypoint():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "simulate" in result.stdout
