from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException, Response, status

from app.reporting.report_workflow import ReportRun, ReportRunService
from app.reporting.reporting_factory import (
    ExportFormat,
    NarrativeStatement,
    ReportExporter,
    ReportingFactory,
    ReportSection,
    ReportValue,
)
from app.reporting.schemas import (
    ApproveReportRequest,
    GenerateReportRequest,
    NarrativePayload,
    ReportRunContextResponse,
    ReportRunRequest,
    ReportRunResponse,
    ReportSectionPayload,
    ReportValuePayload,
)
from app.shared.principal import parse_principal


def _report_run_response(run: ReportRun, artifact: Any) -> ReportRunResponse:
    context = run.context
    return ReportRunResponse(
        report_id=run.report_id,
        status=run.status.value,
        artifact_status=artifact.status.value,
        template_id=artifact.template_id,
        template_version=artifact.template_version,
        report_type=artifact.report_type.value,
        external=artifact.external,
        generated_at=artifact.generated_at.isoformat(),
        content_hash=artifact.content_hash,
        context=ReportRunContextResponse(
            company_id=context.company_id,
            company_label=context.company_label,
            period_id=context.period_id,
            period_label=context.period_label,
            scenario_id=context.scenario_id,
            scenario_label=context.scenario_label,
            currency=context.currency,
        ),
        source_snapshot_ids=list(run.source_snapshot_ids),
        projection_version=run.projection_version,
        created_by=run.created_by,
        reviewed_by=run.reviewed_by,
        approved_by=run.approved_by,
        published_by=run.published_by,
        section_count=len(artifact.sections),
    )


def build_reporting_router(
    factory: ReportingFactory,
    exporter: ReportExporter,
    report_runs: ReportRunService,
) -> APIRouter:
    router = APIRouter(prefix="/reporting", tags=["reporting"])

    @router.get("/templates")
    def list_templates() -> dict[str, Any]:
        return {"templates": factory.list_templates()}

    @router.post("/reports")
    def generate_report(payload: GenerateReportRequest) -> dict[str, Any]:
        sections = tuple(_to_section(section) for section in payload.sections)
        report = factory.generate(
            payload.template_id, payload.template_version, sections
        )
        return {"report": report}

    def principal(user: str, roles: str, companies: str):
        try:
            return parse_principal(user, roles, companies)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def workflow_error(exc: Exception) -> HTTPException:
        if isinstance(exc, PermissionError):
            return HTTPException(status_code=403, detail=str(exc))
        if isinstance(exc, KeyError):
            return HTTPException(
                status_code=404,
                detail="report, source snapshot, or context was not found",
            )
        return HTTPException(status_code=422, detail=str(exc))

    @router.post(
        "/runs", response_model=ReportRunResponse, status_code=status.HTTP_201_CREATED
    )
    def create_report_run(
        payload: ReportRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ReportRunResponse:
        try:
            run, artifact = report_runs.create(
                principal(x_user, x_roles, x_companies),
                company_id=payload.company_id,
                period_id=payload.period_id,
                scenario_id=payload.scenario_id,
                template_id=payload.template_id,
                template_version=payload.template_version,
                source_snapshot_ids=tuple(payload.source_snapshot_ids),
                projection_version=payload.projection_version,
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise workflow_error(exc) from exc
        return _report_run_response(run, artifact)

    @router.get("/runs", response_model=list[ReportRunResponse])
    def list_report_runs(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[ReportRunResponse]:
        try:
            return [
                _report_run_response(run, artifact)
                for run, artifact in report_runs.list(
                    principal(x_user, x_roles, x_companies),
                    company_id=company_id,
                    period_id=period_id,
                    scenario_id=scenario_id,
                )
            ]
        except (KeyError, PermissionError, ValueError) as exc:
            raise workflow_error(exc) from exc

    @router.get("/runs/{report_id}", response_model=ReportRunResponse)
    def get_report_run(
        report_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ReportRunResponse:
        try:
            run, artifact = report_runs.get(
                principal(x_user, x_roles, x_companies), report_id
            )
        except (KeyError, PermissionError) as exc:
            raise workflow_error(exc) from exc
        return _report_run_response(run, artifact)

    @router.post("/runs/{report_id}/review", response_model=ReportRunResponse)
    def review_report_run(
        report_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ReportRunResponse:
        try:
            run, artifact = report_runs.submit_review(
                principal(x_user, x_roles, x_companies), report_id
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise workflow_error(exc) from exc
        return _report_run_response(run, artifact)

    @router.post("/runs/{report_id}/approve", response_model=ReportRunResponse)
    def approve_report_run(
        report_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ReportRunResponse:
        try:
            run, artifact = report_runs.approve(
                principal(x_user, x_roles, x_companies), report_id
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise workflow_error(exc) from exc
        return _report_run_response(run, artifact)

    @router.post("/runs/{report_id}/publish", response_model=ReportRunResponse)
    def publish_report_run(
        report_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ReportRunResponse:
        try:
            run, artifact = report_runs.publish(
                principal(x_user, x_roles, x_companies), report_id
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise workflow_error(exc) from exc
        return _report_run_response(run, artifact)

    @router.get("/reports/{report_id}")
    def get_report(report_id: str) -> dict[str, Any]:
        return {"report": factory.get(report_id)}

    @router.post("/reports/{report_id}/approve")
    def approve_report(report_id: str, payload: ApproveReportRequest) -> dict[str, Any]:
        return {"report": factory.approve(report_id, payload.approver)}

    @router.get("/reports/{report_id}/export/{export_format}")
    def export_report(report_id: str, export_format: ExportFormat) -> Response:
        report = factory.get(report_id)
        try:
            data = exporter.export(report, export_format)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        media_type = _media_type(export_format)
        filename = (
            f"{report.report_type.value}-{report.report_id}.{export_format.value}"
        )
        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    return router


def _to_section(payload: ReportSectionPayload) -> ReportSection:
    return ReportSection(
        section_id=payload.section_id,
        title=payload.title,
        values=tuple(ReportValue(**item.model_dump()) for item in payload.values),
        statements=tuple(
            NarrativeStatement(text=item.text, source_refs=tuple(item.source_refs))
            for item in payload.statements
        ),
        metadata=tuple(sorted(payload.metadata.items())),
    )


def _media_type(export_format: ExportFormat) -> str:
    return {
        ExportFormat.JSON: "application/json",
        ExportFormat.CSV: "text/csv; charset=utf-8",
        ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ExportFormat.PDF: "application/pdf",
        ExportFormat.POWERPOINT: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }[export_format]


__all__ = [
    "ApproveReportRequest",
    "GenerateReportRequest",
    "NarrativePayload",
    "ReportRunContextResponse",
    "ReportRunRequest",
    "ReportRunResponse",
    "ReportSectionPayload",
    "ReportValuePayload",
    "_media_type",
    "_report_run_response",
    "_to_section",
    "build_reporting_router",
]
