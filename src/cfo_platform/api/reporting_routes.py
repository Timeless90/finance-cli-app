from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from cfo_platform.reporting_factory import (
    ExportFormat,
    NarrativeStatement,
    ReportExporter,
    ReportingFactory,
    ReportSection,
    ReportValue,
)


class ReportValuePayload(BaseModel):
    key: str
    value: Decimal | str | int | float | bool | None = None
    unit: str | None = None
    snapshot_id: str
    run_id: str
    run_status: str = "approved"


class NarrativePayload(BaseModel):
    text: str
    source_refs: list[str] = Field(min_length=1)


class ReportSectionPayload(BaseModel):
    section_id: str
    title: str
    values: list[ReportValuePayload] = Field(default_factory=list)
    statements: list[NarrativePayload] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class GenerateReportRequest(BaseModel):
    template_id: str
    template_version: int = Field(ge=1)
    sections: list[ReportSectionPayload]


class ApproveReportRequest(BaseModel):
    approver: str = Field(min_length=1)


def build_reporting_router(factory: ReportingFactory, exporter: ReportExporter) -> APIRouter:
    router = APIRouter(prefix="/reporting", tags=["reporting"])

    @router.get("/templates")
    def list_templates() -> dict[str, Any]:
        return {"templates": factory.list_templates()}

    @router.post("/reports")
    def generate_report(payload: GenerateReportRequest) -> dict[str, Any]:
        sections = tuple(_to_section(section) for section in payload.sections)
        report = factory.generate(payload.template_id, payload.template_version, sections)
        return {"report": report}

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
        filename = f"{report.report_type.value}-{report.report_id}.{export_format.value}"
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
