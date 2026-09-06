from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.planning.planning_baseline import (
    PlanningAccountCategory,
)


class ReconciliationRuleRequest(BaseModel):
    rule_id: str = Field(min_length=1)
    account: str | None = None
    company: str | None = None
    period: str | None = None
    scenario: str | None = None
    expected_total: Decimal = Decimal(0)
    absolute_tolerance: Decimal = Decimal("0.01")
    blocking: bool = True


class DataImportRequest(BaseModel):
    content_base64: str = Field(min_length=1)
    file_name: str = Field(default="upload.csv", min_length=1)
    file_type: str = Field(min_length=1)
    column_mapping: dict[str, str] = Field(default_factory=dict)
    allowed_currencies: set[str] | None = None
    required_dimensions: set[str] | None = None
    sheet_name: str | None = None
    reconciliation_rules: list[ReconciliationRuleRequest] = Field(default_factory=list)


class ImportTransitionRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)


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
    import_id: str
    file_name: str
    file_type: str
    company_ids: list[str]
    status: str
    created_by: str
    created_at: str
    reviewed_by: str | None = None
    approved_by: str | None = None
    published_by: str | None = None
    note: str | None = None
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


class SourceAccountResponse(BaseModel):
    account: str
    total: Decimal


class PlanningAccountMappingRequest(BaseModel):
    source_account: str = Field(min_length=1)
    category: PlanningAccountCategory
    sign_multiplier: Decimal = Decimal(1)


class PlanningMappingCreateRequest(BaseModel):
    company_id: str = Field(min_length=1)
    source_snapshot_id: str = Field(min_length=1)
    version_label: str = Field(min_length=1, max_length=120)
    mappings: list[PlanningAccountMappingRequest] = Field(min_length=1)


class PlanningMappingTransitionRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)


class PlanningMappingResponse(BaseModel):
    mapping_set_id: str
    company_id: str
    source_snapshot_id: str
    version_label: str
    status: str
    created_by: str
    created_at: str
    reviewed_by: str | None = None
    approved_by: str | None = None
    note: str | None = None
    mappings: list[PlanningAccountMappingRequest]


class PlanningBaselinePublishRequest(BaseModel):
    mapping_set_id: str = Field(min_length=1)
    period_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)


class PlanningBaselineResponse(BaseModel):
    baseline_id: str
    company_id: str
    period_id: str
    scenario_id: str
    source_snapshot_id: str
    mapping_set_id: str
    values: dict[str, Decimal]
    missing_categories: list[str]
    forecast_eligible: bool
    created_at: str
    published_by: str
