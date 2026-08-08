from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from cfo_platform.workspace_integration import (
    ContextCatalogService,
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

    return router
