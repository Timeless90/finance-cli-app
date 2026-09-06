from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException

from app.model_runs.finance_model_runs import (
    FinanceModelRun,
    FinanceModelRunDomain,
    FinanceModelRunService,
    ModelRunStateConflict,
)
from app.model_runs.schemas import (
    FinanceModelRunResponse,
    MarketRiskModelRunRequest,
    ModelRunContextResponse,
    RiskModelRunRequest,
)
from app.shared.principal import parse_principal


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
                    tuple(value for value in row) for row in request.correlation_matrix
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


__all__ = [
    "FinanceModelRunResponse",
    "MarketRiskModelRunRequest",
    "ModelRunContextResponse",
    "RiskModelRunRequest",
    "build_model_run_router",
]
