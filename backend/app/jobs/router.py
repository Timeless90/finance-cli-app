from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.jobs.schemas import (
    JobCreateRequest,
    JobResponse,
)
from app.shared.application.services import ModelRunCommand
from app.shared.infrastructure.jobs import InMemoryJobManager, JobRecord


def _to_response(record: JobRecord) -> JobResponse:
    return JobResponse(
        job_id=record.job_id,
        status=record.status,
        progress=record.progress,
        attempt=record.attempt,
        created_at=record.created_at,
        updated_at=record.updated_at,
        run_id=record.run_id,
        error_message=record.error_message,
    )


def build_job_router(manager: InMemoryJobManager) -> APIRouter:
    router = APIRouter(prefix="/jobs", tags=["jobs"])

    @router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
    def create_job(payload: JobCreateRequest) -> JobResponse:
        record = manager.submit(
            ModelRunCommand(
                model_id=payload.model_id,
                model_version=payload.model_version,
                input_snapshot_id=payload.input_snapshot_id,
                parameters=payload.parameters,
                random_seed=payload.random_seed,
            )
        )
        return _to_response(record)

    @router.get("/{job_id}", response_model=JobResponse)
    def get_job(job_id: UUID) -> JobResponse:
        record = manager.get(job_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return _to_response(record)

    @router.post("/{job_id}/cancel", response_model=JobResponse)
    def cancel_job(job_id: UUID) -> JobResponse:
        record = manager.cancel(job_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return _to_response(record)

    @router.post("/{job_id}/resume", response_model=JobResponse)
    def resume_job(job_id: UUID) -> JobResponse:
        record = manager.resume(job_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return _to_response(record)

    return router


__all__ = ["JobCreateRequest", "JobResponse", "_to_response", "build_job_router"]
