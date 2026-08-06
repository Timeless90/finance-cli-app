from __future__ import annotations

import base64
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from cfo_platform.data_reconciliation import ReconciliationRule
from cfo_platform.data_workflow import FinanceDataWorkflow, FinanceImportCommand


class ReconciliationRuleRequest(BaseModel):
    rule_id: str = Field(min_length=1)
    account: str | None = None
    company: str | None = None
    period: str | None = None
    scenario: str | None = None
    expected_total: Decimal = Decimal("0")
    absolute_tolerance: Decimal = Decimal("0.01")
    blocking: bool = True


class DataImportRequest(BaseModel):
    content_base64: str = Field(min_length=1)
    file_type: str = Field(min_length=1)
    column_mapping: dict[str, str] = Field(default_factory=dict)
    allowed_currencies: set[str] | None = None
    required_dimensions: set[str] | None = None
    sheet_name: str | None = None
    reconciliation_rules: list[ReconciliationRuleRequest] = Field(default_factory=list)


class FindingResponse(BaseModel):
    code: str
    severity: str
    message: str
    row_number: int | None


class ReconciliationResponse(BaseModel):
    rule_id: str
    actual_total: Decimal
    expected_total: Decimal
    variance: Decimal
    status: str
    blocking: bool


class DataImportResponse(BaseModel):
    row_count: int
    quality_score: float
    quality_blocking: bool
    reconciliation_blocking: bool
    run_eligible: bool
    snapshot_id: str | None
    content_hash: str | None
    unmapped_accounts: list[str]
    findings: list[FindingResponse]
    reconciliations: list[ReconciliationResponse]


class SnapshotResponse(BaseModel):
    snapshot_id: str
    content_hash: str
    row_count: int


def build_data_router(workflow: FinanceDataWorkflow) -> APIRouter:
    router = APIRouter(prefix="/data", tags=["data"])

    @router.post("/imports", response_model=DataImportResponse, status_code=status.HTTP_201_CREATED)
    def import_finance_data(payload: DataImportRequest) -> DataImportResponse:
        try:
            content = base64.b64decode(payload.content_base64, validate=True)
            rules = tuple(
                ReconciliationRule(
                    rule_id=item.rule_id,
                    account=item.account,
                    company=item.company,
                    period=item.period,
                    scenario=item.scenario,
                    expected_total=item.expected_total,
                    absolute_tolerance=item.absolute_tolerance,
                    blocking=item.blocking,
                )
                for item in payload.reconciliation_rules
            )
            result = workflow.execute(
                FinanceImportCommand(
                    content=content,
                    file_type=payload.file_type,
                    column_mapping=payload.column_mapping,
                    allowed_currencies=payload.allowed_currencies,
                    required_dimensions=payload.required_dimensions,
                    sheet_name=payload.sheet_name,
                    reconciliation_rules=rules,
                )
            )
        except (ValueError, UnicodeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        snapshot = result.snapshot
        return DataImportResponse(
            row_count=result.quality_report.row_count,
            quality_score=result.quality_report.score,
            quality_blocking=result.quality_report.blocking,
            reconciliation_blocking=result.reconciliation_report.blocking,
            run_eligible=result.run_eligible,
            snapshot_id=snapshot.snapshot_id if snapshot else None,
            content_hash=snapshot.content_hash if snapshot else None,
            unmapped_accounts=list(result.unmapped_accounts),
            findings=[
                FindingResponse(
                    code=item.code,
                    severity=item.severity.value,
                    message=item.message,
                    row_number=item.row_number,
                )
                for item in result.quality_report.findings
            ],
            reconciliations=[
                ReconciliationResponse(
                    rule_id=item.rule_id,
                    actual_total=item.actual_total,
                    expected_total=item.expected_total,
                    variance=item.variance,
                    status=item.status.value,
                    blocking=item.blocking,
                )
                for item in result.reconciliation_report.results
            ],
        )

    @router.get("/snapshots/{snapshot_id:path}", response_model=SnapshotResponse)
    def get_snapshot(snapshot_id: str) -> SnapshotResponse:
        try:
            snapshot = workflow.require_snapshot(snapshot_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Data snapshot not found") from exc
        return SnapshotResponse(
            snapshot_id=snapshot.snapshot_id,
            content_hash=snapshot.content_hash,
            row_count=snapshot.row_count,
        )

    return router
