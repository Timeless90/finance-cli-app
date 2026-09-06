from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PrincipalResponse(BaseModel):
    user_id: str
    roles: list[str]
    company_scopes: list[str]
    permissions: list[str]


class CompanyOptionResponse(BaseModel):
    company_id: str
    label: str
    currency: str | None
    data_available: bool


class PeriodOptionResponse(BaseModel):
    period_id: str
    label: str


class ScenarioOptionResponse(BaseModel):
    scenario_id: str
    label: str
    kind: str | None
    status: str
    version: int | None
    source: str


class WorkspaceContextResponse(BaseModel):
    company_id: str
    company_label: str
    period_id: str
    period_label: str
    scenario_id: str
    scenario_label: str
    currency: str | None


class PublishedWorkspaceResponse(BaseModel):
    context: WorkspaceContextResponse
    as_of: datetime
    lineage: dict[str, Any] = Field(default_factory=dict)
    assurance: dict[str, Any] = Field(default_factory=dict)
    source_snapshot_ids: list[str] = Field(default_factory=list)
    projection_version: int


class CommandCenterSnapshotResponse(BaseModel):
    context: WorkspaceContextResponse
    as_of: datetime
    metrics: list[dict[str, Any]] = Field(default_factory=list)
    forecast: dict[str, Any] | None = None
    liquidity: dict[str, Any] | None = None
    risk: dict[str, Any] | None = None
    variance_drivers: list[dict[str, Any]] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    briefing: str | None = None
    assurance: dict[str, Any] = Field(default_factory=dict)
    source_snapshot_ids: list[str] = Field(default_factory=list)
    projection_version: int


class PlanningWorkspaceResponse(PublishedWorkspaceResponse):
    scenarios: list[dict[str, Any]] = Field(default_factory=list)
    active_forecast: dict[str, Any] | None = None
    forecast_series: list[dict[str, Any]] = Field(default_factory=list)
    financial_statement: list[dict[str, Any]] = Field(default_factory=list)
    drivers: list[dict[str, Any]] = Field(default_factory=list)
    thresholds: list[dict[str, Any]] = Field(default_factory=list)
    forecast_assurance: dict[str, Any] = Field(default_factory=dict)


class PerformanceWorkspaceResponse(PublishedWorkspaceResponse):
    metrics: list[dict[str, Any]] = Field(default_factory=list)
    kpi_tree: list[dict[str, Any]] = Field(default_factory=list)
    variance_bridge: dict[str, Any] | None = None
    trend: list[dict[str, Any]] = Field(default_factory=list)
    anomalies: list[dict[str, Any]] = Field(default_factory=list)
    commentary_requirements: list[dict[str, Any]] = Field(default_factory=list)


class ProfitabilityWorkspaceResponse(PublishedWorkspaceResponse):
    metrics: list[dict[str, Any]] = Field(default_factory=list)
    segments: list[dict[str, Any]] = Field(default_factory=list)
    margin_waterfall: list[dict[str, Any]] = Field(default_factory=list)
    profitability_matrix: list[dict[str, Any]] = Field(default_factory=list)
    sensitivity_summary: list[dict[str, Any]] = Field(default_factory=list)
    allocation_assurance: dict[str, Any] = Field(default_factory=dict)


class LiquidityWorkspaceResponse(PublishedWorkspaceResponse):
    metrics: list[dict[str, Any]] = Field(default_factory=list)
    cash_forecast: dict[str, Any] | None = None
    working_capital: list[dict[str, Any]] = Field(default_factory=list)
    debt: list[dict[str, Any]] = Field(default_factory=list)
    covenants: list[dict[str, Any]] = Field(default_factory=list)
    stresses: list[dict[str, Any]] = Field(default_factory=list)


class RiskWorkspaceResponse(PublishedWorkspaceResponse):
    portfolio: dict[str, Any] | None = None
    percentile_curve: list[dict[str, Any]] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    categories: list[dict[str, Any]] = Field(default_factory=list)
    appetite_radar: list[dict[str, Any]] = Field(default_factory=list)
    correlation: dict[str, Any] | None = None
    scenario: dict[str, Any] | None = None
    controls: list[dict[str, Any]] = Field(default_factory=list)
    regimes: dict[str, Any] | None = None
    tail: dict[str, Any] | None = None


class MarketRiskWorkspaceResponse(PublishedWorkspaceResponse):
    assets: list[dict[str, Any]] = Field(default_factory=list)
    selected_runs: dict[str, Any] = Field(default_factory=dict)
    threshold_states: list[dict[str, Any]] = Field(default_factory=list)


class ActionSteeringWorkspaceResponse(PublishedWorkspaceResponse):
    metrics: dict[str, Any] = Field(default_factory=dict)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    benefit_series: list[dict[str, Any]] = Field(default_factory=list)
    dependencies: list[dict[str, Any]] = Field(default_factory=list)


class CapitalAllocationWorkspaceResponse(PublishedWorkspaceResponse):
    portfolio: dict[str, Any] | None = None
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    constraints: list[dict[str, Any]] = Field(default_factory=list)
    allocation: list[dict[str, Any]] = Field(default_factory=list)
    frontier_points: list[dict[str, Any]] = Field(default_factory=list)
    approvals: list[dict[str, Any]] = Field(default_factory=list)
    funding_options: list[dict[str, Any]] = Field(default_factory=list)
    selected_allocation_run_id: str | None = None


class ReportingWorkspaceResponse(PublishedWorkspaceResponse):
    active_report: dict[str, Any] | None = None
    sections: list[dict[str, Any]] = Field(default_factory=list)
    versions: list[dict[str, Any]] = Field(default_factory=list)
    source_pack: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    export_targets: list[dict[str, Any]] = Field(default_factory=list)


class DataGovernanceWorkspaceResponse(PublishedWorkspaceResponse):
    snapshots: list[dict[str, Any]] = Field(default_factory=list)
    quality_findings: list[dict[str, Any]] = Field(default_factory=list)
    governed_runs: list[dict[str, Any]] = Field(default_factory=list)
    models: list[dict[str, Any]] = Field(default_factory=list)
    governance_approvals: list[dict[str, Any]] = Field(default_factory=list)
    governance_lineage: dict[str, Any] = Field(default_factory=dict)
