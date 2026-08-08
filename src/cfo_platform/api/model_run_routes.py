from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel, Field

from cfo_platform.finance_model_runs import (
    FinanceModelRun,
    FinanceModelRunDomain,
    FinanceModelRunService,
    MarketRiskModelType,
    MarketRiskVarMethod,
    ModelRunStateConflict,
    ModelRunStatus,
)

from .principal import parse_principal


class ModelRunContextResponse(BaseModel):
    company_id: str
    company_label: str
    period_id: str
    period_label: str
    scenario_id: str
    scenario_label: str
    currency: str | None


class FinanceModelRunResponse(BaseModel):
    run_id: str
    domain: FinanceModelRunDomain
    model_type: str
    status: ModelRunStatus
    input_context: ModelRunContextResponse
    input_payload: dict[str, Any] = Field(default_factory=dict)
    source_snapshot_ids: list[str] = Field(default_factory=list)
    projection_version: int
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RiskModelRunRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    risk_ids: list[str] = Field(min_length=1)
    correlation_matrix: list[list[Decimal]]
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42


class MarketRiskModelRunRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    model_type: MarketRiskModelType
    losses: list[float] = Field(default_factory=list)
    returns: list[float] = Field(default_factory=list)
    returns_matrix: list[list[float]] = Field(default_factory=list)
    realized_losses: list[float] = Field(default_factory=list)
    var_forecasts: list[float] = Field(default_factory=list)
    confidence: float = Field(default=0.99, gt=0.5, lt=1.0)
    method: MarketRiskVarMethod = MarketRiskVarMethod.HISTORICAL
    threshold_quantile: float = Field(default=0.95, ge=0.90, lt=0.995)
    significance: float = Field(default=0.05, gt=0.0, lt=1.0)

    def execution_payload(self) -> dict[str, Any]:
        return {
            "losses": tuple(self.losses),
            "returns": tuple(self.returns),
            "returns_matrix": tuple(tuple(row) for row in self.returns_matrix),
            "realized_losses": tuple(self.realized_losses),
            "var_forecasts": tuple(self.var_forecasts),
            "confidence": self.confidence,
            "method": self.method.value,
            "threshold_quantile": self.threshold_quantile,
            "significance": self.significance,
        }


def build_model_run_router(service: FinanceModelRunService) -> APIRouter:
    router = APIRouter(tags=["finance-model-runs"])

    def principal(user: str, roles: str, companies: str):
        try:
            return parse_principal(user, roles, companies)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def response(run: FinanceModelRun) -> FinanceModelRunResponse:
        context = run.input_context
        return FinanceModelRunResponse(
            run_id=run.run_id,
            domain=run.domain,
            model_type=run.model_type,
            status=run.status,
            input_context=ModelRunContextResponse(
                company_id=context.company_id,
                company_label=context.company_label,
                period_id=context.period_id,
                period_label=context.period_label,
                scenario_id=context.scenario_id,
                scenario_label=context.scenario_label,
                currency=context.currency,
            ),
            input_payload=dict(run.input_payload),
            source_snapshot_ids=list(run.source_snapshot_ids),
            projection_version=run.projection_version,
            result=dict(run.result) if run.result is not None else None,
            error=run.error,
            created_at=run.created_at,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )

    def not_found(exc: KeyError) -> HTTPException:
        detail = (
            "model run not found"
            if exc.args and exc.args[0] == "model_run"
            else f"{exc.args[0]} not found"
        )
        return HTTPException(status_code=404, detail=detail)

    @router.post(
        "/risk/model-runs",
        response_model=FinanceModelRunResponse,
        status_code=202,
    )
    def create_risk_model_run(
        request: RiskModelRunRequest,
        background_tasks: BackgroundTasks,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceModelRunResponse:
        actor = principal(x_user, x_roles, x_companies)
        try:
            run = service.create_risk_aggregation(
                actor,
                company_id=request.company_id,
                period_id=request.period_id,
                scenario_id=request.scenario_id,
                risk_ids=tuple(request.risk_ids),
                correlation_matrix=tuple(
                    tuple(value for value in row)
                    for row in request.correlation_matrix
                ),
                paths=request.paths,
                seed=request.seed,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            raise not_found(exc) from exc
        except ModelRunStateConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        background_tasks.add_task(service.execute, run.run_id)
        return response(run)

    @router.get(
        "/risk/model-runs/{run_id}",
        response_model=FinanceModelRunResponse,
    )
    def get_risk_model_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceModelRunResponse:
        actor = principal(x_user, x_roles, x_companies)
        try:
            run = service.get(
                actor,
                domain=FinanceModelRunDomain.RISK,
                run_id=run_id,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            raise not_found(exc) from exc
        return response(run)

    @router.post(
        "/market-risk/model-runs",
        response_model=FinanceModelRunResponse,
        status_code=202,
    )
    def create_market_risk_model_run(
        request: MarketRiskModelRunRequest,
        background_tasks: BackgroundTasks,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceModelRunResponse:
        actor = principal(x_user, x_roles, x_companies)
        try:
            run = service.create_market_risk(
                actor,
                company_id=request.company_id,
                period_id=request.period_id,
                scenario_id=request.scenario_id,
                model_type=request.model_type,
                payload=request.execution_payload(),
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            raise not_found(exc) from exc
        except ModelRunStateConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        background_tasks.add_task(service.execute, run.run_id)
        return response(run)

    @router.get(
        "/market-risk/model-runs/{run_id}",
        response_model=FinanceModelRunResponse,
    )
    def get_market_risk_model_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceModelRunResponse:
        actor = principal(x_user, x_roles, x_companies)
        try:
            run = service.get(
                actor,
                domain=FinanceModelRunDomain.MARKET_RISK,
                run_id=run_id,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            raise not_found(exc) from exc
        return response(run)

    return router
