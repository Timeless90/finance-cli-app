from __future__ import annotations

from datetime import datetime
from typing import Any, Self

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from pydantic import BaseModel, Field, model_validator

from cfo_platform.finance_decision_runs import (
    ActionDecisionRunType,
    CapitalDecisionRunType,
    DecisionRunDomain,
    DecisionValidationStatus,
    FinanceDecisionRun,
    FinanceDecisionRunService,
)
from cfo_platform.finance_model_runs import ModelRunStateConflict, ModelRunStatus

from .action_routes import BenefitObservationPayload
from .capital_routes import FundingOptionPayload, PortfolioConstraintsPayload, ProjectPayload
from .principal import parse_principal


class DecisionRunContextResponse(BaseModel):
    company_id: str
    company_label: str
    period_id: str
    period_label: str
    scenario_id: str
    scenario_label: str
    currency: str | None


class FinanceDecisionRunResponse(BaseModel):
    run_id: str
    domain: DecisionRunDomain
    run_type: str
    status: ModelRunStatus
    validation_status: DecisionValidationStatus
    input_context: DecisionRunContextResponse
    input_payload: dict[str, Any]
    source_snapshot_ids: list[str]
    upstream_run_ids: list[str]
    run_version: int
    engine_version: str
    result: dict[str, Any] | None
    error: str | None
    created_by: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    validated_by: str | None
    validated_at: datetime | None
    approved_by: str | None
    approved_at: datetime | None
    rejected_by: str | None
    rejected_at: datetime | None
    decision_rationale: str | None


class ActionDecisionRunRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    run_type: ActionDecisionRunType
    action_ids: list[str] = Field(default_factory=list)
    observations: list[BenefitObservationPayload] = Field(default_factory=list)
    upstream_run_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_input(self) -> Self:
        if self.run_type in {
            ActionDecisionRunType.SIMULATION,
            ActionDecisionRunType.PRIORITIZATION,
        } and not self.action_ids:
            raise ValueError("action_ids are required")
        if (
            self.run_type is ActionDecisionRunType.BENEFIT_TRACKING
            and not self.observations
        ):
            raise ValueError("observations are required")
        return self

    def payload(self) -> dict[str, Any]:
        return {
            "action_ids": tuple(self.action_ids),
            "observations": tuple(
                item.model_dump(mode="json") for item in self.observations
            ),
        }


class CapitalDecisionRunRequest(BaseModel):
    company_id: str
    period_id: str
    scenario_id: str
    run_type: CapitalDecisionRunType
    upstream_run_ids: list[str] = Field(default_factory=list)
    project: ProjectPayload | None = None
    discount_rate: float | None = None
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42
    cash_flow_volatility: float = Field(default=0.15, ge=0.0)
    risk_event_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_event_impact: float = 0.0
    scenario_multiplier: float = Field(default=1.0, gt=0.0)
    projects: list[ProjectPayload] = Field(default_factory=list)
    risk_adjusted_npvs: dict[str, float] = Field(default_factory=dict)
    constraints: PortfolioConstraintsPayload | None = None
    strategic_weight: float = 0.0
    option: FundingOptionPayload | None = None
    base_debt: float | None = Field(default=None, ge=0.0)
    base_ebitda: float | None = Field(default=None, gt=0.0)
    base_interest_expense: float | None = Field(default=None, ge=0.0)
    maximum_leverage: float | None = None

    @model_validator(mode="after")
    def validate_input(self) -> Self:
        if self.run_type in {
            CapitalDecisionRunType.PROJECT_VALUATION,
            CapitalDecisionRunType.MONTE_CARLO_NPV,
        } and (self.project is None or self.discount_rate is None):
            raise ValueError("project and discount_rate are required")
        if self.run_type is CapitalDecisionRunType.PORTFOLIO_ALLOCATION and (
            not self.projects or self.constraints is None
        ):
            raise ValueError("projects and constraints are required")
        if self.run_type is CapitalDecisionRunType.FUNDING_SCENARIO and any(
            value is None
            for value in (
                self.option,
                self.base_debt,
                self.base_ebitda,
                self.base_interest_expense,
                self.maximum_leverage,
            )
        ):
            raise ValueError("funding option and base funding metrics are required")
        return self

    def payload(self) -> dict[str, Any]:
        if self.run_type is CapitalDecisionRunType.PROJECT_VALUATION:
            assert self.project is not None and self.discount_rate is not None
            return {
                "project": self.project.model_dump(mode="json"),
                "discount_rate": self.discount_rate,
            }
        if self.run_type is CapitalDecisionRunType.MONTE_CARLO_NPV:
            assert self.project is not None and self.discount_rate is not None
            return {
                "project": self.project.model_dump(mode="json"),
                "discount_rate": self.discount_rate,
                "paths": self.paths,
                "seed": self.seed,
                "cash_flow_volatility": self.cash_flow_volatility,
                "risk_event_probability": self.risk_event_probability,
                "risk_event_impact": self.risk_event_impact,
                "scenario_multiplier": self.scenario_multiplier,
            }
        if self.run_type is CapitalDecisionRunType.PORTFOLIO_ALLOCATION:
            assert self.constraints is not None
            return {
                "projects": tuple(
                    item.model_dump(mode="json") for item in self.projects
                ),
                "risk_adjusted_npvs": self.risk_adjusted_npvs,
                "constraints": self.constraints.model_dump(mode="json"),
                "strategic_weight": self.strategic_weight,
            }
        assert self.option is not None
        assert self.base_debt is not None
        assert self.base_ebitda is not None
        assert self.base_interest_expense is not None
        assert self.maximum_leverage is not None
        return {
            "option": self.option.model_dump(mode="json"),
            "base_debt": self.base_debt,
            "base_ebitda": self.base_ebitda,
            "base_interest_expense": self.base_interest_expense,
            "maximum_leverage": self.maximum_leverage,
        }


class DecisionRunTransitionRequest(BaseModel):
    rationale: str | None = None


def build_decision_run_router(service: FinanceDecisionRunService) -> APIRouter:
    router = APIRouter(tags=["finance-decision-runs"])

    def actor(user: str, roles: str, companies: str):
        try:
            return parse_principal(user, roles, companies)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def response(run: FinanceDecisionRun) -> FinanceDecisionRunResponse:
        context = run.input_context
        return FinanceDecisionRunResponse(
            run_id=run.run_id,
            domain=run.domain,
            run_type=run.run_type,
            status=run.status,
            validation_status=run.validation_status,
            input_context=DecisionRunContextResponse(
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
            upstream_run_ids=list(run.upstream_run_ids),
            run_version=run.run_version,
            engine_version=run.engine_version,
            result=dict(run.result) if run.result is not None else None,
            error=run.error,
            created_by=run.created_by,
            created_at=run.created_at,
            started_at=run.started_at,
            completed_at=run.completed_at,
            validated_by=run.validated_by,
            validated_at=run.validated_at,
            approved_by=run.approved_by,
            approved_at=run.approved_at,
            rejected_by=run.rejected_by,
            rejected_at=run.rejected_at,
            decision_rationale=run.decision_rationale,
        )

    def call(operation, *args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            detail = (
                "decision run not found"
                if exc.args and exc.args[0] == "decision_run"
                else f"{exc.args[0]} not found"
            )
            raise HTTPException(status_code=404, detail=detail) from exc
        except ModelRunStateConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def transition(
        operation: str,
        domain: DecisionRunDomain,
        run_id: str,
        request: DecisionRunTransitionRequest,
        principal,
    ) -> FinanceDecisionRunResponse:
        return response(
            call(
                getattr(service, operation),
                principal,
                domain=domain,
                run_id=run_id,
                rationale=request.rationale,
            )
        )

    @router.post(
        "/actions/runs", response_model=FinanceDecisionRunResponse, status_code=202
    )
    def create_action_run(
        request: ActionDecisionRunRequest,
        background_tasks: BackgroundTasks,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        principal = actor(x_user, x_roles, x_companies)
        run = call(
            service.create,
            principal,
            domain=DecisionRunDomain.ACTION,
            run_type=request.run_type.value,
            company_id=request.company_id,
            period_id=request.period_id,
            scenario_id=request.scenario_id,
            payload=request.payload(),
            upstream_run_ids=tuple(request.upstream_run_ids),
        )
        background_tasks.add_task(service.execute, run.run_id)
        return response(run)

    @router.get("/actions/runs", response_model=list[FinanceDecisionRunResponse])
    def list_action_runs(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[FinanceDecisionRunResponse]:
        principal = actor(x_user, x_roles, x_companies)
        runs = call(
            service.list,
            principal,
            domain=DecisionRunDomain.ACTION,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        return [response(run) for run in runs]

    @router.get(
        "/actions/runs/{run_id}", response_model=FinanceDecisionRunResponse
    )
    def get_action_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        principal = actor(x_user, x_roles, x_companies)
        return response(
            call(
                service.get,
                principal,
                domain=DecisionRunDomain.ACTION,
                run_id=run_id,
            )
        )

    @router.post(
        "/actions/runs/{run_id}/validate", response_model=FinanceDecisionRunResponse
    )
    def validate_action_run(
        run_id: str,
        request: DecisionRunTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        return transition(
            "validate",
            DecisionRunDomain.ACTION,
            run_id,
            request,
            actor(x_user, x_roles, x_companies),
        )

    @router.post(
        "/actions/runs/{run_id}/approve", response_model=FinanceDecisionRunResponse
    )
    def approve_action_run(
        run_id: str,
        request: DecisionRunTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        return transition(
            "approve",
            DecisionRunDomain.ACTION,
            run_id,
            request,
            actor(x_user, x_roles, x_companies),
        )

    @router.post(
        "/actions/runs/{run_id}/reject", response_model=FinanceDecisionRunResponse
    )
    def reject_action_run(
        run_id: str,
        request: DecisionRunTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        return transition(
            "reject",
            DecisionRunDomain.ACTION,
            run_id,
            request,
            actor(x_user, x_roles, x_companies),
        )

    @router.post(
        "/capital/runs", response_model=FinanceDecisionRunResponse, status_code=202
    )
    def create_capital_run(
        request: CapitalDecisionRunRequest,
        background_tasks: BackgroundTasks,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        principal = actor(x_user, x_roles, x_companies)
        run = call(
            service.create,
            principal,
            domain=DecisionRunDomain.CAPITAL,
            run_type=request.run_type.value,
            company_id=request.company_id,
            period_id=request.period_id,
            scenario_id=request.scenario_id,
            payload=request.payload(),
            upstream_run_ids=tuple(request.upstream_run_ids),
        )
        background_tasks.add_task(service.execute, run.run_id)
        return response(run)

    @router.get("/capital/runs", response_model=list[FinanceDecisionRunResponse])
    def list_capital_runs(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[FinanceDecisionRunResponse]:
        principal = actor(x_user, x_roles, x_companies)
        runs = call(
            service.list,
            principal,
            domain=DecisionRunDomain.CAPITAL,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        return [response(run) for run in runs]

    @router.get(
        "/capital/runs/{run_id}", response_model=FinanceDecisionRunResponse
    )
    def get_capital_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        principal = actor(x_user, x_roles, x_companies)
        return response(
            call(
                service.get,
                principal,
                domain=DecisionRunDomain.CAPITAL,
                run_id=run_id,
            )
        )

    @router.post(
        "/capital/runs/{run_id}/validate", response_model=FinanceDecisionRunResponse
    )
    def validate_capital_run(
        run_id: str,
        request: DecisionRunTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        return transition(
            "validate",
            DecisionRunDomain.CAPITAL,
            run_id,
            request,
            actor(x_user, x_roles, x_companies),
        )

    @router.post(
        "/capital/runs/{run_id}/approve", response_model=FinanceDecisionRunResponse
    )
    def approve_capital_run(
        run_id: str,
        request: DecisionRunTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        return transition(
            "approve",
            DecisionRunDomain.CAPITAL,
            run_id,
            request,
            actor(x_user, x_roles, x_companies),
        )

    @router.post(
        "/capital/runs/{run_id}/reject", response_model=FinanceDecisionRunResponse
    )
    def reject_capital_run(
        run_id: str,
        request: DecisionRunTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> FinanceDecisionRunResponse:
        return transition(
            "reject",
            DecisionRunDomain.CAPITAL,
            run_id,
            request,
            actor(x_user, x_roles, x_companies),
        )

    return router
