from __future__ import annotations

import json
from decimal import Decimal
from threading import RLock
from typing import Protocol

from app.data.data_foundation import DataSnapshot, FinanceRecord


class DataSnapshotRepository(Protocol):
    def save(self, snapshot: DataSnapshot) -> None: ...

    def get(self, snapshot_id: str) -> DataSnapshot | None: ...

    def exists(self, snapshot_id: str) -> bool: ...

    def list_all(self) -> tuple[DataSnapshot, ...]: ...


class InMemoryDataSnapshotRepository:
    def __init__(self) -> None:
        self._snapshots: dict[str, DataSnapshot] = {}
        self._lock = RLock()

    def save(self, snapshot: DataSnapshot) -> None:
        with self._lock:
            existing = self._snapshots.get(snapshot.snapshot_id)
            if existing is not None and existing.content_hash != snapshot.content_hash:
                raise ValueError("snapshot identity collision detected")
            self._snapshots[snapshot.snapshot_id] = snapshot

    def get(self, snapshot_id: str) -> DataSnapshot | None:
        with self._lock:
            return self._snapshots.get(snapshot_id)

    def exists(self, snapshot_id: str) -> bool:
        with self._lock:
            return snapshot_id in self._snapshots

    def list_all(self) -> tuple[DataSnapshot, ...]:
        with self._lock:
            return tuple(
                self._snapshots[snapshot_id] for snapshot_id in sorted(self._snapshots)
            )


class PostgresDataSnapshotRepository:
    """Durable snapshot adapter for the local PostgreSQL Finance App server."""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS data_snapshots (
        snapshot_id TEXT PRIMARY KEY,
        content_hash TEXT NOT NULL,
        payload JSONB NOT NULL
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

    def save(self, snapshot: DataSnapshot) -> None:
        payload = json.dumps(_snapshot_payload(snapshot), sort_keys=True)
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT content_hash FROM data_snapshots WHERE snapshot_id = %s",
                (snapshot.snapshot_id,),
            )
            existing = cursor.fetchone()
            if existing is not None:
                if str(existing[0]) != snapshot.content_hash:
                    raise ValueError("snapshot identity collision detected")
                return
            cursor.execute(
                "INSERT INTO data_snapshots(snapshot_id, content_hash, payload) VALUES (%s, %s, %s::jsonb)",
                (snapshot.snapshot_id, snapshot.content_hash, payload),
            )

    def get(self, snapshot_id: str) -> DataSnapshot | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM data_snapshots WHERE snapshot_id = %s",
                (snapshot_id,),
            )
            row = cursor.fetchone()
        return None if row is None else _snapshot_from_payload(row[0])

    def exists(self, snapshot_id: str) -> bool:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM data_snapshots WHERE snapshot_id = %s", (snapshot_id,)
            )
            return cursor.fetchone() is not None

    def list_all(self) -> tuple[DataSnapshot, ...]:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT payload FROM data_snapshots ORDER BY snapshot_id")
            rows = cursor.fetchall()
        return tuple(_snapshot_from_payload(row[0]) for row in rows)


def _snapshot_payload(snapshot: DataSnapshot) -> dict[str, object]:
    return {
        "snapshot_id": snapshot.snapshot_id,
        "content_hash": snapshot.content_hash,
        "row_count": snapshot.row_count,
        "records": [
            {
                "company": record.company,
                "account": record.account,
                "period": record.period,
                "scenario": record.scenario,
                "value": str(record.value),
                "currency": record.currency,
                "dimensions": list(record.dimensions),
                "source_row": record.source_row,
            }
            for record in snapshot.records
        ],
    }


def _snapshot_from_payload(payload: object) -> DataSnapshot:
    raw = payload if isinstance(payload, dict) else json.loads(str(payload))
    records = tuple(
        FinanceRecord(
            company=str(item["company"]),
            account=str(item["account"]),
            period=str(item["period"]),
            scenario=str(item["scenario"]),
            value=Decimal(str(item["value"])),
            currency=str(item["currency"]),
            dimensions=tuple(
                (str(key), str(value)) for key, value in item.get("dimensions", [])
            ),
            source_row=item.get("source_row"),
        )
        for item in raw["records"]
    )
    return DataSnapshot(
        snapshot_id=str(raw["snapshot_id"]),
        content_hash=str(raw["content_hash"]),
        row_count=int(raw["row_count"]),
        records=records,
    )
