from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


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


class ReportRunRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    template_id: str
    template_version: int = Field(ge=1)
    source_snapshot_ids: list[str] = Field(min_length=1)
    projection_version: int = Field(default=1, ge=1)


class ReportRunContextResponse(BaseModel):
    company_id: str
    company_label: str
    period_id: str
    period_label: str
    scenario_id: str
    scenario_label: str
    currency: str | None


class ReportRunResponse(BaseModel):
    report_id: str
    status: str
    artifact_status: str
    template_id: str
    template_version: int
    report_type: str
    external: bool
    generated_at: str
    content_hash: str
    context: ReportRunContextResponse
    source_snapshot_ids: list[str]
    projection_version: int
    created_by: str
    reviewed_by: str | None = None
    approved_by: str | None = None
    published_by: str | None = None
    section_count: int
