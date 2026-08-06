from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from threading import RLock
from uuid import UUID, uuid4

from cfo_platform.application.services import ExecuteModelRun, ModelRunCommand


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class JobRecord:
    job_id: UUID
    command: ModelRunCommand
    status: JobStatus
    progress: float
    attempt: int
    created_at: datetime
    updated_at: datetime
    run_id: UUID | None = None
    error_message: str | None = None


class InMemoryJobManager:
    """Thread-backed job manager for local development and API contract validation."""

    def __init__(self, service: ExecuteModelRun, max_workers: int = 2) -> None:
        self._service = service
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="cfo-job")
        self._records: dict[UUID, JobRecord] = {}
        self._futures: dict[UUID, Future[None]] = {}
        self._lock = RLock()

    def submit(self, command: ModelRunCommand) -> JobRecord:
        now = datetime.now(UTC)
        record = JobRecord(
            job_id=uuid4(),
            command=command,
            status=JobStatus.QUEUED,
            progress=0.0,
            attempt=1,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._records[record.job_id] = record
            self._futures[record.job_id] = self._pool.submit(self._run, record.job_id)
        return record

    def get(self, job_id: UUID) -> JobRecord | None:
        with self._lock:
            return self._records.get(job_id)

    def cancel(self, job_id: UUID) -> JobRecord | None:
        with self._lock:
            record = self._records.get(job_id)
            future = self._futures.get(job_id)
            if record is None or future is None:
                return None
            if record.status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}:
                return record
            future.cancel()
            updated = replace(
                record,
                status=JobStatus.CANCELLED,
                updated_at=datetime.now(UTC),
                error_message="Cancellation requested",
            )
            self._records[job_id] = updated
            return updated

    def resume(self, job_id: UUID) -> JobRecord | None:
        with self._lock:
            record = self._records.get(job_id)
            if record is None:
                return None
            if record.status not in {JobStatus.CANCELLED, JobStatus.FAILED}:
                return record
            updated = replace(
                record,
                status=JobStatus.QUEUED,
                progress=0.0,
                attempt=record.attempt + 1,
                updated_at=datetime.now(UTC),
                run_id=None,
                error_message=None,
            )
            self._records[job_id] = updated
            self._futures[job_id] = self._pool.submit(self._run, job_id)
            return updated

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)

    def _run(self, job_id: UUID) -> None:
        with self._lock:
            record = self._records[job_id]
            if record.status == JobStatus.CANCELLED:
                return
            self._records[job_id] = replace(
                record,
                status=JobStatus.RUNNING,
                progress=0.1,
                updated_at=datetime.now(UTC),
            )
            command = record.command
        try:
            receipt = self._service.execute(command)
            with self._lock:
                current = self._records[job_id]
                if current.status == JobStatus.CANCELLED:
                    return
                terminal = (
                    JobStatus.SUCCEEDED
                    if receipt.result.error_message is None
                    else JobStatus.FAILED
                )
                self._records[job_id] = replace(
                    current,
                    status=terminal,
                    progress=1.0,
                    updated_at=datetime.now(UTC),
                    run_id=receipt.run_id,
                    error_message=receipt.result.error_message,
                )
        except Exception as exc:  # noqa: BLE001 - job boundary records failures
            with self._lock:
                current = self._records[job_id]
                if current.status != JobStatus.CANCELLED:
                    self._records[job_id] = replace(
                        current,
                        status=JobStatus.FAILED,
                        progress=1.0,
                        updated_at=datetime.now(UTC),
                        error_message=str(exc),
                    )
