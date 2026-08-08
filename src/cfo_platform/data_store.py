from __future__ import annotations

from threading import RLock
from typing import Protocol

from cfo_platform.data_foundation import DataSnapshot


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
                self._snapshots[snapshot_id]
                for snapshot_id in sorted(self._snapshots)
            )
