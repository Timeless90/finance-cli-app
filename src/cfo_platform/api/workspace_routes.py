from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from cfo_platform.workspace_integration import (
    ContextCatalogService,
    WorkspaceProjectionSnapshot,
    WorkspaceReadModelService,
)

from .principal import parse_principal


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
    selected_allocation_run_id: str | None = None


class ReportingWorkspaceResponse(PublishedWorkspaceResponse):
    active_report: dict[str, Any] | None = None
    sections: list[dict[str, Any]] = Field(default_factory=list)
    versions: list[dict[str, Any]] = Field(default_factory=list)
    source_pack: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    export_targets: list[dict[str, Any]] = Field(default_factory=list)


def build_workspace_router(
    context_catalog: ContextCatalogService,
    read_models: WorkspaceReadModelService,
) -> APIRouter:
    router = APIRouter(tags=["workspace-integration"])

    def principal(user: str, roles: str, companies: str):
        try:
            return parse_principal(user, roles, companies)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def get_projection(
        workspace: str,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
        user: str,
        roles: str,
        companies: str,
    ) -> WorkspaceProjectionSnapshot:
        actor = principal(user, roles, companies)
        try:
            return read_models.workspace(
                workspace,
                actor,
                company_id=company_id,
                period_id=period_id,
                scenario_id=scenario_id,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            detail = (
                f"{workspace} workspace snapshot not found"
                if exc.args[0] == workspace
                else f"{exc.args[0]} not found"
            )
            raise HTTPException(status_code=404, detail=detail) from exc

    def projection_payload(
        snapshot: WorkspaceProjectionSnapshot,
    ) -> dict[str, Any]:
        return {
            **dict(snapshot.data),
            "context": WorkspaceContextResponse(**asdict(snapshot.context)),
            "as_of": snapshot.as_of,
            "lineage": dict(snapshot.lineage),
            "assurance": dict(snapshot.assurance),
            "source_snapshot_ids": list(snapshot.source_snapshot_ids),
            "projection_version": snapshot.projection_version,
        }

    @router.get("/context/principal", response_model=PrincipalResponse)
    def get_principal(
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> PrincipalResponse:
        actor = principal(x_user, x_roles, x_companies)
        try:
            return PrincipalResponse(**context_catalog.principal_view(actor))
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.get("/context/companies", response_model=list[CompanyOptionResponse])
    def list_companies(
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[CompanyOptionResponse]:
        actor = principal(x_user, x_roles, x_companies)
        try:
            return [
                CompanyOptionResponse(**asdict(item))
                for item in context_catalog.list_companies(actor)
            ]
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.get("/context/periods", response_model=list[PeriodOptionResponse])
    def list_periods(
        company_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[PeriodOptionResponse]:
        actor = principal(x_user, x_roles, x_companies)
        try:
            return [
                PeriodOptionResponse(**asdict(item))
                for item in context_catalog.list_periods(
                    actor,
                    company_id=company_id,
                )
            ]
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.get("/context/scenarios", response_model=list[ScenarioOptionResponse])
    def list_scenarios(
        company_id: str,
        period_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[ScenarioOptionResponse]:
        actor = principal(x_user, x_roles, x_companies)
        try:
            return [
                ScenarioOptionResponse(**asdict(item))
                for item in context_catalog.list_scenarios(
                    actor,
                    company_id=company_id,
                    period_id=period_id,
                )
            ]
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="period not found") from exc

    @router.get("/context/resolve", response_model=WorkspaceContextResponse)
    def resolve_context(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> WorkspaceContextResponse:
        actor = principal(x_user, x_roles, x_companies)
        try:
            context = context_catalog.resolve(
                actor,
                company_id=company_id,
                period_id=period_id,
                scenario_id=scenario_id,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(
                status_code=404,
                detail=f"{exc.args[0]} not found",
            ) from exc
        return WorkspaceContextResponse(**asdict(context))

    @router.get(
        "/command-center/overview",
        response_model=CommandCenterSnapshotResponse,
    )
    def command_center_overview(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> CommandCenterSnapshotResponse:
        actor = principal(x_user, x_roles, x_companies)
        try:
            snapshot = read_models.command_center(
                actor,
                company_id=company_id,
                period_id=period_id,
                scenario_id=scenario_id,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            detail = (
                "command center snapshot not found"
                if exc.args[0] == "command_center"
                else f"{exc.args[0]} not found"
            )
            raise HTTPException(status_code=404, detail=detail) from exc

        return CommandCenterSnapshotResponse(
            context=WorkspaceContextResponse(**asdict(snapshot.context)),
            as_of=snapshot.as_of,
            metrics=[dict(item) for item in snapshot.metrics],
            forecast=dict(snapshot.forecast) if snapshot.forecast is not None else None,
            liquidity=dict(snapshot.liquidity) if snapshot.liquidity is not None else None,
            risk=dict(snapshot.risk) if snapshot.risk is not None else None,
            variance_drivers=[dict(item) for item in snapshot.variance_drivers],
            actions=[dict(item) for item in snapshot.actions],
            briefing=snapshot.briefing,
            assurance=dict(snapshot.assurance),
            source_snapshot_ids=list(snapshot.source_snapshot_ids),
            projection_version=snapshot.projection_version,
        )

    @router.get("/planning/workspace", response_model=PlanningWorkspaceResponse)
    def planning_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> PlanningWorkspaceResponse:
        snapshot = get_projection(
            "planning",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        return PlanningWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/performance/workspace", response_model=PerformanceWorkspaceResponse)
    def performance_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> PerformanceWorkspaceResponse:
        snapshot = get_projection(
            "performance",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        return PerformanceWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/profitability/workspace", response_model=ProfitabilityWorkspaceResponse)
    def profitability_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ProfitabilityWorkspaceResponse:
        snapshot = get_projection(
            "profitability",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        return ProfitabilityWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/liquidity/workspace", response_model=LiquidityWorkspaceResponse)
    def liquidity_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> LiquidityWorkspaceResponse:
        snapshot = get_projection(
            "liquidity",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        return LiquidityWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/risk/workspace", response_model=RiskWorkspaceResponse)
    def risk_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        aggregation_run_id: str | None = None,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> RiskWorkspaceResponse:
        snapshot = get_projection(
            "risk",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        if (
            aggregation_run_id is not None
            and snapshot.lineage.get("aggregation_run_id") != aggregation_run_id
        ):
            raise HTTPException(
                status_code=404,
                detail="risk workspace snapshot not found for aggregation run",
            )
        return RiskWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/market-risk/workspace", response_model=MarketRiskWorkspaceResponse)
    def market_risk_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        asset_id: str | None = None,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> MarketRiskWorkspaceResponse:
        snapshot = get_projection(
            "market-risk",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        if asset_id is not None:
            assets = [
                item
                for item in snapshot.data.get("assets", ())
                if item.get("asset_id") == asset_id
            ]
            if not assets:
                raise HTTPException(status_code=404, detail="asset not found")
            snapshot = replace(
                snapshot,
                data={**dict(snapshot.data), "assets": assets},
            )
        return MarketRiskWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/actions/workspace", response_model=ActionSteeringWorkspaceResponse)
    def actions_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ActionSteeringWorkspaceResponse:
        snapshot = get_projection(
            "actions",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        return ActionSteeringWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/capital/workspace", response_model=CapitalAllocationWorkspaceResponse)
    def capital_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> CapitalAllocationWorkspaceResponse:
        snapshot = get_projection(
            "capital",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        return CapitalAllocationWorkspaceResponse(**projection_payload(snapshot))

    def reporting_projection(
        company_id: str,
        period_id: str,
        scenario_id: str,
        report_id: str | None,
        x_user: str,
        x_roles: str,
        x_companies: str,
    ) -> ReportingWorkspaceResponse:
        snapshot = get_projection(
            "reporting",
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
            user=x_user,
            roles=x_roles,
            companies=x_companies,
        )
        active_report = snapshot.data.get("active_report")
        if (
            report_id is not None
            and (
                not isinstance(active_report, dict)
                or active_report.get("report_id") != report_id
            )
        ):
            raise HTTPException(
                status_code=404,
                detail="reporting workspace snapshot not found for report",
            )
        return ReportingWorkspaceResponse(**projection_payload(snapshot))

    @router.get("/reporting/workspace", response_model=ReportingWorkspaceResponse)
    def reporting_workspace(
        company_id: str,
        period_id: str,
        scenario_id: str,
        report_id: str | None = None,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ReportingWorkspaceResponse:
        return reporting_projection(
            company_id,
            period_id,
            scenario_id,
            report_id,
            x_user,
            x_roles,
            x_companies,
        )

    @router.get(
        "/reports/workspace",
        response_model=ReportingWorkspaceResponse,
        include_in_schema=False,
    )
    def reports_workspace_alias(
        company_id: str,
        period_id: str,
        scenario_id: str,
        report_id: str | None = None,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> ReportingWorkspaceResponse:
        return reporting_projection(
            company_id,
            period_id,
            scenario_id,
            report_id,
            x_user,
            x_roles,
            x_companies,
        )

    return router
