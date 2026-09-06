from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from app.workspace.workspace_integration import (
    CommandCenterSnapshot,
    WorkspaceContext,
    WorkspaceContextKey,
    WorkspaceProjectionSnapshot,
)


class PostgresWorkspaceReadModelRepository:
    """Stores published read models by workspace and explicit finance context."""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS workspace_read_models (
        workspace TEXT NOT NULL,
        company_id TEXT NOT NULL,
        period_id TEXT NOT NULL,
        scenario_id TEXT NOT NULL,
        projection_version INTEGER NOT NULL,
        payload JSONB NOT NULL,
        PRIMARY KEY (workspace, company_id, period_id, scenario_id)
    );
    """

    def __init__(self, database_url: str) -> None:
        import psycopg

        self._database_url = database_url
        with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
            cursor.execute(self._SCHEMA)

    def _connect(self):  # type: ignore[no-untyped-def]
        import psycopg

        return psycopg.connect(self._database_url)

    def save_command_center(self, snapshot: CommandCenterSnapshot) -> None:
        self._save("command-center", snapshot)

    def get_command_center(
        self, key: WorkspaceContextKey
    ) -> CommandCenterSnapshot | None:
        payload = self._get("command-center", key)
        if payload is None:
            return None
        return CommandCenterSnapshot(
            context=_context(payload["context"]),
            as_of=datetime.fromisoformat(payload["as_of"]),
            metrics=tuple(payload.get("metrics", [])),
            forecast=payload.get("forecast"),
            liquidity=payload.get("liquidity"),
            risk=payload.get("risk"),
            variance_drivers=tuple(payload.get("variance_drivers", [])),
            actions=tuple(payload.get("actions", [])),
            briefing=payload.get("briefing"),
            assurance=payload.get("assurance", {}),
            source_snapshot_ids=tuple(payload.get("source_snapshot_ids", [])),
            projection_version=int(payload["projection_version"]),
        )

    def save_workspace(
        self, workspace: str, snapshot: WorkspaceProjectionSnapshot
    ) -> None:
        self._save(workspace, snapshot)

    def get_workspace(
        self, workspace: str, key: WorkspaceContextKey
    ) -> WorkspaceProjectionSnapshot | None:
        payload = self._get(workspace, key)
        if payload is None:
            return None
        return WorkspaceProjectionSnapshot(
            context=_context(payload["context"]),
            as_of=datetime.fromisoformat(payload["as_of"]),
            data=payload.get("data", {}),
            lineage=payload.get("lineage", {}),
            assurance=payload.get("assurance", {}),
            source_snapshot_ids=tuple(payload.get("source_snapshot_ids", [])),
            projection_version=int(payload["projection_version"]),
        )

    def _save(
        self,
        workspace: str,
        snapshot: CommandCenterSnapshot | WorkspaceProjectionSnapshot,
    ) -> None:
        key = WorkspaceContextKey.from_context(snapshot.context)
        payload = json.dumps(asdict(snapshot), default=str, sort_keys=True)
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT projection_version, payload FROM workspace_read_models WHERE workspace = %s AND company_id = %s AND period_id = %s AND scenario_id = %s",
                (workspace, key.company_id, key.period_id, key.scenario_id),
            )
            current = cursor.fetchone()
            if current is not None:
                current_version, current_payload = int(current[0]), current[1]
                if current_version > snapshot.projection_version:
                    raise ValueError(
                        "projection_version must increase when replacing a read model"
                    )
                if current_version == snapshot.projection_version:
                    if _canonical_json(current_payload) != _canonical_json(payload):
                        raise ValueError(
                            "projection_version must increase when replacing a read model"
                        )
                    return
            cursor.execute(
                "INSERT INTO workspace_read_models(workspace, company_id, period_id, scenario_id, projection_version, payload) VALUES (%s, %s, %s, %s, %s, %s::jsonb) ON CONFLICT (workspace, company_id, period_id, scenario_id) DO UPDATE SET projection_version = EXCLUDED.projection_version, payload = EXCLUDED.payload",
                (
                    workspace,
                    key.company_id,
                    key.period_id,
                    key.scenario_id,
                    snapshot.projection_version,
                    payload,
                ),
            )

    def _get(self, workspace: str, key: WorkspaceContextKey) -> dict[str, Any] | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM workspace_read_models WHERE workspace = %s AND company_id = %s AND period_id = %s AND scenario_id = %s",
                (workspace, key.company_id, key.period_id, key.scenario_id),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return row[0] if isinstance(row[0], dict) else json.loads(str(row[0]))


def _canonical_json(value: object) -> str:
    if isinstance(value, str):
        value = json.loads(value)
    return json.dumps(value, default=str, sort_keys=True)


def _context(raw: object) -> WorkspaceContext:
    assert isinstance(raw, dict)
    return WorkspaceContext(**raw)
