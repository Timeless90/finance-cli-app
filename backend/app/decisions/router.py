from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Header, HTTPException

from app.actions.action_management import (
    ActionCatalogueService,
    ActionPortfolioPrioritizer,
    ActionSimulationEngine,
    BenefitTrackingService,
    InMemoryBenefitTrackingCatalog,
)
from app.capital.capital_allocation import (
    CapitalPortfolioOptimizer,
    FundingScenarioEngine,
    InMemoryCapitalCandidateCatalog,
    MonteCarloNpvEngine,
    ProjectValuationService,
)
from app.decisions.decision_workflow import (
    DecisionRun,
    DecisionRunKind,
    DecisionRunService,
    IdempotencyConflict,
)
from app.decisions.schemas import (
    ActionBenefitTrackingRunRequest,
    ActionDecisionRunRequest,
    CapitalAllocationRunRequest,
    CapitalDecisionRunRequest,
    CapitalMonteCarloRunRequest,
    DecisionContextRequest,
    DecisionContextResponse,
    DecisionRunEventResponse,
    DecisionRunResponse,
    FundingScenarioRunRequest,
    RejectDecisionRunRequest,
)
from app.shared.principal import parse_principal


def build_decision_run_router(
    decision_runs: DecisionRunService,
    actions: ActionCatalogueService,
    action_simulation: ActionSimulationEngine,
    action_prioritizer: ActionPortfolioPrioritizer,
    benefit_tracking: BenefitTrackingService,
    benefit_catalog: InMemoryBenefitTrackingCatalog,
    candidates: InMemoryCapitalCandidateCatalog,
    valuation: ProjectValuationService,
    monte_carlo: MonteCarloNpvEngine,
    optimizer: CapitalPortfolioOptimizer,
    funding: FundingScenarioEngine,
) -> APIRouter:
    router = APIRouter(tags=["decision-runs"])

    def actor(user: str, roles: str, companies: str):
        try:
            return parse_principal(user, roles, companies)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def response(run: DecisionRun) -> DecisionRunResponse:
        context = run.context
        return DecisionRunResponse(
            run_id=run.run_id,
            kind=run.kind,
            status=run.status.value,
            context=DecisionContextResponse(
                company_id=context.company_id,
                company_label=context.company_label,
                period_id=context.period_id,
                period_label=context.period_label,
                scenario_id=context.scenario_id,
                scenario_label=context.scenario_label,
                currency=context.currency,
            ),
            references=list(run.references),
            source_snapshot_ids=list(run.source_snapshot_ids),
            projection_version=run.projection_version,
            model_version=run.model_version,
            parameters=dict(run.parameters),
            result=dict(run.result),
            created_by=run.created_by,
            created_at=run.created_at,
            validated_by=run.validated_by,
            approved_by=run.approved_by,
            rejected_by=run.rejected_by,
            rejection_reason=run.rejection_reason,
        )

    def create_run(
        request: DecisionContextRequest,
        *,
        kind: DecisionRunKind,
        references: tuple[str, ...],
        parameters: dict[str, Any],
        result: dict[str, Any],
        x_user: str,
        x_roles: str,
        x_companies: str,
        idempotency_key: str,
        x_correlation_id: str,
    ) -> tuple[DecisionRun, bool]:
        principal = actor(x_user, x_roles, x_companies)
        run = decision_runs.create(
            principal,
            kind=kind,
            company_id=request.company_id,
            period_id=request.period_id,
            scenario_id=request.scenario_id,
            references=references,
            source_snapshot_ids=tuple(request.source_snapshot_ids),
            projection_version=request.projection_version,
            model_version=request.model_version,
            parameters=parameters,
            result=result,
            idempotency_key=idempotency_key,
            correlation_id=x_correlation_id,
        )
        return (
            run,
            run.created_by == principal.user_id
            and run.idempotency_key == idempotency_key,
        )

    def create_error(exc: Exception) -> HTTPException:
        if isinstance(exc, PermissionError):
            return HTTPException(
                status_code=403, detail="decision run is not permitted"
            )
        if isinstance(exc, KeyError):
            return HTTPException(
                status_code=404, detail="decision source or context was not found"
            )
        if isinstance(exc, IdempotencyConflict):
            return HTTPException(status_code=409, detail=str(exc))
        return HTTPException(status_code=422, detail=str(exc))

    @router.post("/actions/runs", response_model=DecisionRunResponse, status_code=201)
    def create_action_run(
        request: ActionDecisionRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        if request.kind not in {
            DecisionRunKind.ACTION_SIMULATION,
            DecisionRunKind.ACTION_PRIORITIZATION,
        }:
            raise HTTPException(
                status_code=422, detail="action run kind is not supported"
            )
        try:
            selected = tuple(actions.get(action_id) for action_id in request.action_ids)
            result = (
                asdict(action_simulation.simulate(selected))
                if request.kind is DecisionRunKind.ACTION_SIMULATION
                else {
                    "priorities": [
                        asdict(item) for item in action_prioritizer.prioritize(selected)
                    ]
                }
            )
            run, _ = create_run(
                request,
                kind=request.kind,
                references=tuple(request.action_ids),
                parameters={"action_ids": request.action_ids},
                result=result,
                x_user=x_user,
                x_roles=x_roles,
                x_companies=x_companies,
                idempotency_key=idempotency_key,
                x_correlation_id=x_correlation_id,
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise create_error(exc) from exc
        return response(run)

    @router.post(
        "/actions/runs/benefit-tracking",
        response_model=DecisionRunResponse,
        status_code=201,
    )
    def create_action_benefit_tracking_run(
        request: ActionBenefitTrackingRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        try:
            definitions = tuple(
                benefit_catalog.get(
                    company_id=request.company_id,
                    period_id=request.period_id,
                    scenario_id=request.scenario_id,
                    action_id=action_id,
                )
                for action_id in request.action_ids
            )
            if any(
                not set(definition.source_snapshot_ids)
                <= set(request.source_snapshot_ids)
                for definition in definitions
            ):
                raise ValueError(
                    "benefit source snapshots must be included in the run request"
                )
            observations = tuple(
                observation
                for definition in definitions
                for observation in definition.observations
            )
            run, _ = create_run(
                request,
                kind=DecisionRunKind.ACTION_BENEFIT_TRACKING,
                references=tuple(request.action_ids),
                parameters={"action_ids": request.action_ids},
                result={
                    "results": [
                        asdict(item)
                        for item in benefit_tracking.summarize(observations)
                    ]
                },
                x_user=x_user,
                x_roles=x_roles,
                x_companies=x_companies,
                idempotency_key=idempotency_key,
                x_correlation_id=x_correlation_id,
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise create_error(exc) from exc
        return response(run)

    def capital_candidates(request: CapitalDecisionRunRequest):
        selected = tuple(
            candidates.get(
                company_id=request.company_id,
                period_id=request.period_id,
                scenario_id=request.scenario_id,
                candidate_id=candidate_id,
            )
            for candidate_id in request.candidate_ids
        )
        request_sources = set(request.source_snapshot_ids)
        for candidate in selected:
            if not set(candidate.source_snapshot_ids) <= request_sources:
                raise ValueError(
                    "candidate source snapshots must be included in the run request"
                )
        return selected

    @router.post(
        "/capital/runs/valuation", response_model=DecisionRunResponse, status_code=201
    )
    def create_capital_valuation_run(
        request: CapitalDecisionRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        if len(request.candidate_ids) != 1:
            raise HTTPException(
                status_code=422, detail="valuation requires exactly one candidate_id"
            )
        try:
            candidate = capital_candidates(request)[0]
            run, _ = create_run(
                request,
                kind=DecisionRunKind.CAPITAL_VALUATION,
                references=tuple(request.candidate_ids),
                parameters={"candidate_ids": request.candidate_ids},
                result=asdict(
                    valuation.evaluate(candidate.project, candidate.discount_rate)
                ),
                x_user=x_user,
                x_roles=x_roles,
                x_companies=x_companies,
                idempotency_key=idempotency_key,
                x_correlation_id=x_correlation_id,
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise create_error(exc) from exc
        return response(run)

    @router.post(
        "/capital/runs/monte-carlo-npv",
        response_model=DecisionRunResponse,
        status_code=201,
    )
    def create_capital_monte_carlo_run(
        request: CapitalMonteCarloRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        if len(request.candidate_ids) != 1:
            raise HTTPException(
                status_code=422,
                detail="Monte Carlo valuation requires exactly one candidate_id",
            )
        try:
            candidate = capital_candidates(request)[0]
            parameters = request.model_dump(
                exclude={
                    "company_id",
                    "period_id",
                    "scenario_id",
                    "source_snapshot_ids",
                    "projection_version",
                    "model_version",
                    "candidate_ids",
                }
            )
            result = asdict(
                monte_carlo.simulate(
                    candidate.project,
                    discount_rate=candidate.discount_rate,
                    **parameters,
                )
            )
            run, _ = create_run(
                request,
                kind=DecisionRunKind.CAPITAL_MONTE_CARLO_NPV,
                references=tuple(request.candidate_ids),
                parameters={"candidate_ids": request.candidate_ids, **parameters},
                result=result,
                x_user=x_user,
                x_roles=x_roles,
                x_companies=x_companies,
                idempotency_key=idempotency_key,
                x_correlation_id=x_correlation_id,
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise create_error(exc) from exc
        return response(run)

    @router.post(
        "/capital/runs/allocation", response_model=DecisionRunResponse, status_code=201
    )
    def create_capital_allocation_run(
        request: CapitalAllocationRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        try:
            selected = capital_candidates(request)
            constraints = candidates.constraints_for(
                company_id=request.company_id,
                period_id=request.period_id,
                scenario_id=request.scenario_id,
            )
            result = asdict(
                optimizer.optimize(
                    [candidate.project for candidate in selected],
                    risk_adjusted_npvs={
                        candidate.candidate_id: candidate.risk_adjusted_npv
                        for candidate in selected
                    },
                    constraints=constraints,
                    strategic_weight=request.strategic_weight,
                )
            )
            run, _ = create_run(
                request,
                kind=DecisionRunKind.CAPITAL_ALLOCATION,
                references=tuple(request.candidate_ids),
                parameters={
                    "candidate_ids": request.candidate_ids,
                    "strategic_weight": request.strategic_weight,
                },
                result=result,
                x_user=x_user,
                x_roles=x_roles,
                x_companies=x_companies,
                idempotency_key=idempotency_key,
                x_correlation_id=x_correlation_id,
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise create_error(exc) from exc
        return response(run)

    @router.post(
        "/capital/runs/funding", response_model=DecisionRunResponse, status_code=201
    )
    def create_funding_scenario_run(
        request: FundingScenarioRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        try:
            definition = candidates.funding_for(
                company_id=request.company_id,
                period_id=request.period_id,
                scenario_id=request.scenario_id,
                option_id=request.funding_option_id,
            )
            if not set(definition.source_snapshot_ids) <= set(
                request.source_snapshot_ids
            ):
                raise ValueError(
                    "funding source snapshots must be included in the run request"
                )
            result = asdict(
                funding.evaluate(
                    definition.option,
                    base_debt=definition.base_debt,
                    base_ebitda=definition.base_ebitda,
                    base_interest_expense=definition.base_interest_expense,
                    maximum_leverage=definition.maximum_leverage,
                )
            )
            run, _ = create_run(
                request,
                kind=DecisionRunKind.FUNDING_SCENARIO,
                references=(request.funding_option_id,),
                parameters={"funding_option_id": request.funding_option_id},
                result=result,
                x_user=x_user,
                x_roles=x_roles,
                x_companies=x_companies,
                idempotency_key=idempotency_key,
                x_correlation_id=x_correlation_id,
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise create_error(exc) from exc
        return response(run)

    def transition_error(exc: Exception) -> HTTPException:
        if isinstance(exc, PermissionError):
            return HTTPException(
                status_code=403, detail="decision transition is not permitted"
            )
        if isinstance(exc, KeyError):
            return HTTPException(status_code=404, detail="decision run was not found")
        return HTTPException(status_code=409, detail=str(exc))

    @router.get("/decision-runs", response_model=list[DecisionRunResponse])
    def list_decision_runs(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[DecisionRunResponse]:
        try:
            runs = decision_runs.list(
                actor(x_user, x_roles, x_companies),
                company_id=company_id,
                period_id=period_id,
                scenario_id=scenario_id,
            )
        except (KeyError, PermissionError) as exc:
            raise transition_error(exc) from exc
        return [response(run) for run in runs]

    @router.get("/decision-runs/{run_id}", response_model=DecisionRunResponse)
    def get_decision_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> DecisionRunResponse:
        try:
            return response(
                decision_runs.get(actor(x_user, x_roles, x_companies), run_id)
            )
        except (KeyError, PermissionError) as exc:
            raise transition_error(exc) from exc

    @router.post("/decision-runs/{run_id}/validate", response_model=DecisionRunResponse)
    def validate_decision_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        try:
            return response(
                decision_runs.validate(
                    actor(x_user, x_roles, x_companies),
                    run_id,
                    correlation_id=x_correlation_id,
                )
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise transition_error(exc) from exc

    @router.post("/decision-runs/{run_id}/approve", response_model=DecisionRunResponse)
    def approve_decision_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        try:
            return response(
                decision_runs.approve(
                    actor(x_user, x_roles, x_companies),
                    run_id,
                    correlation_id=x_correlation_id,
                )
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise transition_error(exc) from exc

    @router.post("/decision-runs/{run_id}/reject", response_model=DecisionRunResponse)
    def reject_decision_run(
        run_id: str,
        request: RejectDecisionRunRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        x_correlation_id: str = Header(default="api"),
    ) -> DecisionRunResponse:
        try:
            return response(
                decision_runs.reject(
                    actor(x_user, x_roles, x_companies),
                    run_id,
                    reason=request.reason,
                    correlation_id=x_correlation_id,
                )
            )
        except (KeyError, PermissionError, ValueError) as exc:
            raise transition_error(exc) from exc

    @router.get(
        "/decision-runs/{run_id}/events", response_model=list[DecisionRunEventResponse]
    )
    def decision_run_events(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[DecisionRunEventResponse]:
        try:
            return [
                DecisionRunEventResponse(
                    event_type=event.event_type.value,
                    actor=event.actor,
                    correlation_id=event.correlation_id,
                    occurred_at=event.occurred_at,
                    reason=event.reason,
                )
                for event in decision_runs.events(
                    actor(x_user, x_roles, x_companies), run_id
                )
            ]
        except (KeyError, PermissionError) as exc:
            raise transition_error(exc) from exc

    return router


__all__ = [
    "ActionBenefitTrackingRunRequest",
    "ActionDecisionRunRequest",
    "CapitalAllocationRunRequest",
    "CapitalDecisionRunRequest",
    "CapitalMonteCarloRunRequest",
    "DecisionContextRequest",
    "DecisionContextResponse",
    "DecisionRunEventResponse",
    "DecisionRunResponse",
    "FundingScenarioRunRequest",
    "RejectDecisionRunRequest",
    "build_decision_run_router",
]
