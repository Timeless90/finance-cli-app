from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from app.governance.governance import (
    AuditAction,
    AuditEvent,
    GovernanceStatus,
    GovernedRun,
    RunLineage,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS governed_runs (
    run_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    immutable INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_aggregate
ON audit_events(aggregate_type, aggregate_id, occurred_at);
"""


class _PostgresBase:
    def __init__(self, database_url: str) -> None:
        import psycopg

        self._database_url = database_url
        with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
            cursor.execute(_SCHEMA)

    def _connect(self):  # type: ignore[no-untyped-def]
        import psycopg

        return psycopg.connect(self._database_url)


class PostgresGovernedRunRepository(_PostgresBase):
    def add(self, run: GovernedRun) -> None:
        payload = json.dumps(asdict(run), default=str, sort_keys=True)
        try:
            with self._connect() as connection, connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO governed_runs(run_id, payload, immutable) VALUES (%s, %s, %s)",
                    (run.run_id, payload, int(run.immutable)),
                )
        except Exception as exc:
            if "unique" in str(exc).lower():
                raise ValueError("run already exists") from exc
            raise

    def get(self, run_id: str) -> GovernedRun | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM governed_runs WHERE run_id = %s", (run_id,)
            )
            row = cursor.fetchone()
        return None if row is None else _decode_run(str(row[0]))

    def replace(self, run: GovernedRun) -> None:
        current = self.get(run.run_id)
        if current is None:
            raise KeyError(run.run_id)
        if current.immutable and current != run:
            raise ValueError("approved or retired runs cannot be overwritten")
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE governed_runs SET payload = %s, immutable = %s WHERE run_id = %s",
                (
                    json.dumps(asdict(run), default=str, sort_keys=True),
                    int(run.immutable),
                    run.run_id,
                ),
            )

    def list_all(self) -> tuple[GovernedRun, ...]:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT payload FROM governed_runs ORDER BY run_id")
            rows = cursor.fetchall()
        return tuple(_decode_run(str(row[0])) for row in rows)


class PostgresAuditEventRepository(_PostgresBase):
    def append(self, event: AuditEvent) -> None:
        payload = json.dumps(asdict(event), default=str, sort_keys=True)
        try:
            with self._connect() as connection, connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO audit_events(event_id, aggregate_type, aggregate_id, occurred_at, payload) VALUES (%s, %s, %s, %s, %s)",
                    (
                        event.event_id,
                        event.aggregate_type,
                        event.aggregate_id,
                        event.occurred_at,
                        payload,
                    ),
                )
        except Exception as exc:
            if "unique" in str(exc).lower():
                raise ValueError("audit event already exists") from exc
            raise

    def list_for(
        self, aggregate_type: str, aggregate_id: str
    ) -> tuple[AuditEvent, ...]:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM audit_events WHERE aggregate_type = %s AND aggregate_id = %s ORDER BY occurred_at, event_id",
                (aggregate_type, aggregate_id),
            )
            rows = cursor.fetchall()
        return tuple(_decode_event(str(row[0])) for row in rows)


class SqliteGovernedRunRepository:
    def __init__(self, database_path: str | Path) -> None:
        self._path = str(database_path)
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        return connection

    def add(self, run: GovernedRun) -> None:
        payload = json.dumps(asdict(run), default=str, sort_keys=True)
        try:
            with self._connect() as connection:
                connection.execute(
                    "INSERT INTO governed_runs(run_id, payload, immutable) VALUES (?, ?, ?)",
                    (run.run_id, payload, int(run.immutable)),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("run already exists") from exc

    def get(self, run_id: str) -> GovernedRun | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM governed_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return None if row is None else _decode_run(str(row["payload"]))

    def replace(self, run: GovernedRun) -> None:
        current = self.get(run.run_id)
        if current is None:
            raise KeyError(run.run_id)
        if current.immutable and current != run:
            raise ValueError("approved or retired runs cannot be overwritten")
        payload = json.dumps(asdict(run), default=str, sort_keys=True)
        with self._connect() as connection:
            connection.execute(
                "UPDATE governed_runs SET payload = ?, immutable = ? WHERE run_id = ?",
                (payload, int(run.immutable), run.run_id),
            )

    def list_all(self) -> tuple[GovernedRun, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM governed_runs ORDER BY run_id"
            ).fetchall()
        return tuple(_decode_run(str(row["payload"])) for row in rows)


class SqliteAuditEventRepository:
    def __init__(self, database_path: str | Path) -> None:
        self._path = str(database_path)
        with sqlite3.connect(self._path) as connection:
            connection.executescript(_SCHEMA)

    def append(self, event: AuditEvent) -> None:
        payload = json.dumps(asdict(event), default=str, sort_keys=True)
        try:
            with sqlite3.connect(self._path) as connection:
                connection.execute(
                    "INSERT INTO audit_events(event_id, aggregate_type, aggregate_id, occurred_at, payload) VALUES (?, ?, ?, ?, ?)",
                    (
                        event.event_id,
                        event.aggregate_type,
                        event.aggregate_id,
                        event.occurred_at.isoformat(),
                        payload,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("audit event already exists") from exc

    def list_for(
        self, aggregate_type: str, aggregate_id: str
    ) -> tuple[AuditEvent, ...]:
        with sqlite3.connect(self._path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT payload FROM audit_events WHERE aggregate_type = ? AND aggregate_id = ? ORDER BY occurred_at, event_id",
                (aggregate_type, aggregate_id),
            ).fetchall()
        return tuple(_decode_event(str(row["payload"])) for row in rows)


def _decode_run(payload: str) -> GovernedRun:
    raw = json.loads(payload)
    lineage_raw = raw["lineage"]
    return GovernedRun(
        run_id=raw["run_id"],
        lineage=RunLineage(**lineage_raw),
        status=GovernanceStatus(raw["status"]),
        created_by=raw["created_by"],
        created_at=datetime.fromisoformat(raw["created_at"]),
        validated_by=raw.get("validated_by"),
        approved_by=raw.get("approved_by"),
        retired_by=raw.get("retired_by"),
        supersedes_run_id=raw.get("supersedes_run_id"),
        output_hash=raw.get("output_hash"),
    )


def _decode_event(payload: str) -> AuditEvent:
    raw = json.loads(payload)
    return AuditEvent(
        event_id=raw["event_id"],
        aggregate_type=raw["aggregate_type"],
        aggregate_id=raw["aggregate_id"],
        action=AuditAction(raw["action"]),
        actor=raw["actor"],
        occurred_at=datetime.fromisoformat(raw["occurred_at"]),
        reason=raw["reason"],
        correlation_id=raw["correlation_id"],
        before_hash=raw.get("before_hash"),
        after_hash=raw["after_hash"],
    )
