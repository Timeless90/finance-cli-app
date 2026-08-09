from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from threading import RLock
from typing import Any, Mapping
from uuid import uuid4

from cfo_platform.action_management import (
    ActionCatalogueService,
    ActionPortfolioPrioritizer,
    ActionSimulationEngine,
    BenefitObservation,
    BenefitTrackingService,
    ImpactMetric,
)
from cfo_platform.capital_allocation import (
    CapitalPortfolioOptimizer,
    CapitalProject,
    FundingOption,
    FundingScenarioEngine,
    MonteCarloNpvEngine,
    PortfolioConstraints,
    ProjectValuationService,
)
from cfo_platform.data_store import DataSnapshotRepository
from cfo_platform.finance_model_runs import ModelRunStateConflict, ModelRunStatus
from cfo_platform.rbac import AccessControlService, Permission, Principal
from cfo_platform.workspace_integration import ContextCatalogService, WorkspaceContext


class DecisionRunDomain(StrEnum):
    ACTION = "action"
    CAPITAL = "capital"


class ActionDecisionRunType(StrEnum):
    SIMULATION = "simulation"
    PRIORITIZATION = "prioritization"
    BENEFIT_TRACKING = "benefit_tracking"


class CapitalDecisionRunType(StrEnum):
    PROJECT_VALUATION = "project_valuation"
    MONTE_CARLO_NPV = "monte_carlo_npv"
    PORTFOLIO_ALLOCATION = "portfolio_allocation"
    FUNDING_SCENARIO = "funding_scenario"


class DecisionValidationStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class FinanceDecisionRun:
    run_id: str
    domain: DecisionRunDomain
    run_type: str
    status: ModelRunStatus
    validation_status: DecisionValidationStatus
    input_context: WorkspaceContext
    input_payload: Mapping[str, Any]
    source_snapshot_ids: tuple[str, ...]
    upstream_run_ids: tuple[str, ...]
    run_version: int
    engine_version: str
    result: Mapping[str, Any] | None
    error: str | None
    created_by: str
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    validated_by: str | None = None
    validated_at: datetime | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejected_by: str | None = None
    rejected_at: datetime | None = None
    decision_rationale: str | None = None


class InMemoryFinanceDecisionRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, FinanceDecisionRun] = {}
        self._lock = RLock()

    def create(self, run: FinanceDecisionRun) -> None:
        with self._lock:
            if run.run_id in self._runs:
                raise ModelRunStateConflict(f"decision run {run.run_id} already exists")
            self._runs[run.run_id] = run

    def get(self, run_id: str) -> FinanceDecisionRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def list(self) -> tuple[FinanceDecisionRun, ...]:
        with self._lock:
            return tuple(
                sorted(self._runs.values(), key=lambda run: (run.created_at, run.run_id))
            )

    def execution(
        self,
        run_id: str,
        expected: ModelRunStatus,
        target: ModelRunStatus,
        *,
        result: Mapping[str, Any] | None = None,
        error: str | None = None,
    ) -> FinanceDecisionRun:
        allowed = {
            ModelRunStatus.PENDING: {ModelRunStatus.RUNNING},
            ModelRunStatus.RUNNING: {ModelRunStatus.SUCCEEDED, ModelRunStatus.FAILED},
            ModelRunStatus.SUCCEEDED: set(),
            ModelRunStatus.FAILED: set(),
        }
        with self._lock:
            current = self._require(run_id)
            if current.status is not expected or target not in allowed[current.status]:
                raise ModelRunStateConflict(
                    f"invalid decision run transition {current.status} -> {target}"
                )
            now = _now()
            updated = replace(
                current,
                status=target,
                result=result,
                error=error,
                started_at=now if target is ModelRunStatus.RUNNING else current.started_at,
                completed_at=(
                    now
                    if target in {ModelRunStatus.SUCCEEDED, ModelRunStatus.FAILED}
                    else current.completed_at
                ),
            )
            self._runs[run_id] = updated
            return updated

    def validation(
        self,
        run_id: str,
        expected: DecisionValidationStatus,
        target: DecisionValidationStatus,
        *,
        actor: str,
        rationale: str | None,
    ) -> FinanceDecisionRun:
        allowed = {
            DecisionValidationStatus.DRAFT: {DecisionValidationStatus.VALIDATED},
            DecisionValidationStatus.VALIDATED: {
                DecisionValidationStatus.APPROVED,
                DecisionValidationStatus.REJECTED,
            },
            DecisionValidationStatus.APPROVED: set(),
            DecisionValidationStatus.REJECTED: set(),
        }
        with self._lock:
            current = self._require(run_id)
            if current.status is not ModelRunStatus.SUCCEEDED:
                raise ModelRunStateConflict("only succeeded decision runs can be governed")
            if current.validation_status is not expected or target not in allowed[expected]:
                raise ModelRunStateConflict(
                    f"invalid validation transition {current.validation_status} -> {target}"
                )
            now = _now()
            values: dict[str, Any] = {
                "validation_status": target,
                "decision_rationale": rationale,
            }
            if target is DecisionValidationStatus.VALIDATED:
                values.update(validated_by=actor, validated_at=now)
            elif target is DecisionValidationStatus.APPROVED:
                values.update(approved_by=actor, approved_at=now)
            else:
                values.update(rejected_by=actor, rejected_at=now)
            updated = replace(current, **values)
            self._runs[run_id] = updated
            return updated

    def _require(self, run_id: str) -> FinanceDecisionRun:
        run = self._runs.get(run_id)
        if run is None:
            raise KeyError("decision_run")
        return run


class FinanceDecisionRunService:
    _VERSIONS = {
        "simulation": "action-simulation-v1",
        "prioritization": "action-prioritization-v1",
        "benefit_tracking": "action-benefit-tracking-v1",
        "project_valuation": "capital-project-valuation-v1",
        "monte_carlo_npv": "capital-monte-carlo-npv-v1",
        "portfolio_allocation": "capital-portfolio-allocation-v1",
        "funding_scenario": "capital-funding-scenario-v1",
    }

    def __init__(
        self,
        contexts: ContextCatalogService,
        snapshots: DataSnapshotRepository,
        access: AccessControlService,
        repository: InMemoryFinanceDecisionRunRepository,
        actions: ActionCatalogueService,
        simulation: ActionSimulationEngine,
        prioritizer: ActionPortfolioPrioritizer,
        benefits: BenefitTrackingService,
        valuation: ProjectValuationService,
        monte_carlo: MonteCarloNpvEngine,
        optimizer: CapitalPortfolioOptimizer,
        funding: FundingScenarioEngine,
    ) -> None:
        self._contexts = contexts
        self._snapshots = snapshots
        self._access = access
        self._repository = repository
        self._actions = actions
        self._simulation = simulation
        self._prioritizer = prioritizer
        self._benefits = benefits
        self._valuation = valuation
        self._monte_carlo = monte_carlo
        self._optimizer = optimizer
        self._funding = funding

    def create(
        self,
        principal: Principal,
        *,
        domain: DecisionRunDomain,
        run_type: str,
        company_id: str,
        period_id: str,
        scenario_id: str,
        payload: Mapping[str, Any],
        upstream_run_ids: tuple[str, ...] = (),
    ) -> FinanceDecisionRun:
        context = self._contexts.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        self._access.require(
            principal, Permission.CREATE_RUN, company=context.company_id
        )
        run = FinanceDecisionRun(
            run_id=uuid4().hex,
            domain=domain,
            run_type=run_type,
            status=ModelRunStatus.PENDING,
            validation_status=DecisionValidationStatus.DRAFT,
            input_context=context,
            input_payload=payload,
            source_snapshot_ids=self._snapshot_ids(context),
            upstream_run_ids=upstream_run_ids,
            run_version=1,
            engine_version=self._VERSIONS[run_type],
            result=None,
            error=None,
            created_by=principal.user_id,
            created_at=_now(),
        )
        self._repository.create(run)
        return run

    def get(
        self, principal: Principal, *, domain: DecisionRunDomain, run_id: str
    ) -> FinanceDecisionRun:
        run = self._repository.get(run_id)
        if run is None or run.domain is not domain:
            raise KeyError("decision_run")
        self._authorize(principal, run.input_context)
        return run

    def list(
        self,
        principal: Principal,
        *,
        domain: DecisionRunDomain,
        company_id: str,
        period_id: str,
        scenario_id: str,
    ) -> tuple[FinanceDecisionRun, ...]:
        context = self._contexts.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        return tuple(
            run
            for run in self._repository.list()
            if run.domain is domain and run.input_context == context
        )

    def execute(self, run_id: str) -> FinanceDecisionRun:
        run = self._repository.execution(
            run_id, ModelRunStatus.PENDING, ModelRunStatus.RUNNING
        )
        try:
            result = (
                self._action_result(run)
                if run.domain is DecisionRunDomain.ACTION
                else self._capital_result(run)
            )
        except Exception as exc:
            return self._repository.execution(
                run_id,
                ModelRunStatus.RUNNING,
                ModelRunStatus.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )
        return self._repository.execution(
            run_id,
            ModelRunStatus.RUNNING,
            ModelRunStatus.SUCCEEDED,
            result=result,
        )

    def validate(
        self,
        principal: Principal,
        *,
        domain: DecisionRunDomain,
        run_id: str,
        rationale: str | None,
    ) -> FinanceDecisionRun:
        return self._govern(
            principal,
            domain=domain,
            run_id=run_id,
            permission=Permission.VALIDATE_RUN,
            expected=DecisionValidationStatus.DRAFT,
            target=DecisionValidationStatus.VALIDATED,
            rationale=rationale,
        )

    def approve(
        self,
        principal: Principal,
        *,
        domain: DecisionRunDomain,
        run_id: str,
        rationale: str | None,
    ) -> FinanceDecisionRun:
        return self._govern(
            principal,
            domain=domain,
            run_id=run_id,
            permission=Permission.APPROVE_RUN,
            expected=DecisionValidationStatus.VALIDATED,
            target=DecisionValidationStatus.APPROVED,
            rationale=rationale,
        )

    def reject(
        self,
        principal: Principal,
        *,
        domain: DecisionRunDomain,
        run_id: str,
        rationale: str | None,
    ) -> FinanceDecisionRun:
        return self._govern(
            principal,
            domain=domain,
            run_id=run_id,
            permission=Permission.APPROVE_RUN,
            expected=DecisionValidationStatus.VALIDATED,
            target=DecisionValidationStatus.REJECTED,
            rationale=rationale,
        )

    def _govern(
        self,
        principal: Principal,
        *,
        domain: DecisionRunDomain,
        run_id: str,
        permission: Permission,
        expected: DecisionValidationStatus,
        target: DecisionValidationStatus,
        rationale: str | None,
    ) -> FinanceDecisionRun:
        run = self.get(principal, domain=domain, run_id=run_id)
        self._access.require(
            principal, permission, company=run.input_context.company_id
        )
        return self._repository.validation(
            run_id, expected, target, actor=principal.user_id, rationale=rationale
        )

    def _authorize(self, principal: Principal, context: WorkspaceContext) -> None:
        self._contexts.resolve(
            principal,
            company_id=context.company_id,
            period_id=context.period_id,
            scenario_id=context.scenario_id,
        )

    def _snapshot_ids(self, context: WorkspaceContext) -> tuple[str, ...]:
        return tuple(
            snapshot.snapshot_id
            for snapshot in self._snapshots.list_all()
            if any(
                record.company == context.company_id
                and record.period == context.period_id
                and record.scenario == context.scenario_id
                for record in snapshot.records
            )
        )

    def _action_result(self, run: FinanceDecisionRun) -> Mapping[str, Any]:
        run_type = ActionDecisionRunType(run.run_type)
        if run_type in {
            ActionDecisionRunType.SIMULATION,
            ActionDecisionRunType.PRIORITIZATION,
        }:
            actions = tuple(
                self._actions.get(str(item)) for item in run.input_payload["action_ids"]
            )
            if run_type is ActionDecisionRunType.SIMULATION:
                return asdict(self._simulation.simulate(actions))
            return {
                "priorities": [
                    asdict(item) for item in self._prioritizer.prioritize(actions)
                ]
            }
        observations = tuple(
            BenefitObservation(
                action_id=str(item["action_id"]),
                metric=ImpactMetric(str(item["metric"])),
                period=int(item["period"]),
                planned_amount=Decimal(str(item["planned_amount"])),
                realized_amount=Decimal(str(item["realized_amount"])),
                covenant_id=(
                    str(item["covenant_id"])
                    if item.get("covenant_id") is not None
                    else None
                ),
            )
            for item in run.input_payload["observations"]
        )
        return {
            "results": [asdict(item) for item in self._benefits.summarize(observations)]
        }

    def _capital_result(self, run: FinanceDecisionRun) -> Mapping[str, Any]:
        payload = run.input_payload
        run_type = CapitalDecisionRunType(run.run_type)
        if run_type is CapitalDecisionRunType.PROJECT_VALUATION:
            return asdict(
                self._valuation.evaluate(
                    _project(payload["project"]), float(payload["discount_rate"])
                )
            )
        if run_type is CapitalDecisionRunType.MONTE_CARLO_NPV:
            return asdict(
                self._monte_carlo.simulate(
                    _project(payload["project"]),
                    discount_rate=float(payload["discount_rate"]),
                    paths=int(payload["paths"]),
                    seed=int(payload["seed"]),
                    cash_flow_volatility=float(payload["cash_flow_volatility"]),
                    risk_event_probability=float(payload["risk_event_probability"]),
                    risk_event_impact=float(payload["risk_event_impact"]),
                    scenario_multiplier=float(payload["scenario_multiplier"]),
                )
            )
        if run_type is CapitalDecisionRunType.PORTFOLIO_ALLOCATION:
            return asdict(
                self._optimizer.optimize(
                    [_project(item) for item in payload["projects"]],
                    risk_adjusted_npvs={
                        str(key): float(value)
                        for key, value in payload["risk_adjusted_npvs"].items()
                    },
                    constraints=PortfolioConstraints(
                        **{
                            key: float(value)
                            for key, value in payload["constraints"].items()
                        }
                    ),
                    strategic_weight=float(payload.get("strategic_weight", 0.0)),
                )
            )
        option_data = payload["option"]
        option = FundingOption(
            option_id=str(option_data["option_id"]),
            amount=float(option_data["amount"]),
            annual_rate=float(option_data["annual_rate"]),
            term_years=int(option_data["term_years"]),
            upfront_fee=float(option_data.get("upfront_fee", 0.0)),
            amortizing=bool(option_data.get("amortizing", True)),
        )
        return asdict(
            self._funding.evaluate(
                option,
                base_debt=float(payload["base_debt"]),
                base_ebitda=float(payload["base_ebitda"]),
                base_interest_expense=float(payload["base_interest_expense"]),
                maximum_leverage=float(payload["maximum_leverage"]),
            )
        )


def _project(payload: Mapping[str, Any]) -> CapitalProject:
    return CapitalProject(
        project_id=str(payload["project_id"]),
        name=str(payload["name"]),
        initial_investment=float(payload["initial_investment"]),
        cash_flows=tuple(float(value) for value in payload["cash_flows"]),
        annual_nopat=tuple(
            float(value) for value in payload.get("annual_nopat", ())
        ),
        terminal_value=float(payload.get("terminal_value", 0.0)),
        strategic_score=float(payload.get("strategic_score", 0.0)),
        cash_headroom_impact=float(payload.get("cash_headroom_impact", 0.0)),
        leverage_delta=float(payload.get("leverage_delta", 0.0)),
        interest_cover_delta=float(payload.get("interest_cover_delta", 0.0)),
    )


def _now() -> datetime:
    return datetime.now(timezone.utc)
