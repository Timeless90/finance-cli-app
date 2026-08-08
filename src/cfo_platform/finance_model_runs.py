from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from threading import RLock
from typing import Any, Mapping, Protocol
from uuid import uuid4

import numpy as np

from cfo_platform.data_store import DataSnapshotRepository
from cfo_platform.market_treasury_risk import (
    CopulaDependenceModel,
    EvtTailOverlay,
    GaussianHmmRegimeModel,
    GarchTModel,
    MarketRiskMetrics,
    VarBacktester,
)
from cfo_platform.rbac import Principal
from cfo_platform.risk_management import RiskAggregationEngine, RiskRegisterService
from cfo_platform.workspace_integration import ContextCatalogService, WorkspaceContext


class ModelRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class FinanceModelRunDomain(StrEnum):
    RISK = "risk"
    MARKET_RISK = "market-risk"


class MarketRiskModelType(StrEnum):
    VAR_ES = "var_es"
    GARCH_T = "garch_t"
    REGIME_HMM = "regime_hmm"
    EVT = "evt"
    COPULA = "copula"
    VAR_BACKTEST = "var_backtest"


class MarketRiskVarMethod(StrEnum):
    HISTORICAL = "historical"
    STUDENT_T = "student_t"


class ModelRunStateConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FinanceModelRun:
    run_id: str
    domain: FinanceModelRunDomain
    model_type: str
    status: ModelRunStatus
    input_context: WorkspaceContext
    input_payload: Mapping[str, Any]
    source_snapshot_ids: tuple[str, ...]
    projection_version: int
    result: Mapping[str, Any] | None
    error: str | None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class FinanceModelRunRepository(Protocol):
    def create(self, run: FinanceModelRun) -> None: ...

    def get(self, run_id: str) -> FinanceModelRun | None: ...

    def transition(
        self,
        run_id: str,
        *,
        expected: ModelRunStatus,
        target: ModelRunStatus,
        result: Mapping[str, Any] | None = None,
        error: str | None = None,
        timestamp: datetime,
    ) -> FinanceModelRun: ...


class InMemoryFinanceModelRunRepository:
    _ALLOWED_TRANSITIONS = {
        ModelRunStatus.PENDING: frozenset({ModelRunStatus.RUNNING}),
        ModelRunStatus.RUNNING: frozenset(
            {ModelRunStatus.SUCCEEDED, ModelRunStatus.FAILED}
        ),
        ModelRunStatus.SUCCEEDED: frozenset(),
        ModelRunStatus.FAILED: frozenset(),
    }

    def __init__(self) -> None:
        self._runs: dict[str, FinanceModelRun] = {}
        self._lock = RLock()

    def create(self, run: FinanceModelRun) -> None:
        with self._lock:
            if run.run_id in self._runs:
                raise ModelRunStateConflict(f"model run {run.run_id} already exists")
            if run.status is not ModelRunStatus.PENDING:
                raise ModelRunStateConflict("new model runs must start in pending state")
            self._runs[run.run_id] = run

    def get(self, run_id: str) -> FinanceModelRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def transition(
        self,
        run_id: str,
        *,
        expected: ModelRunStatus,
        target: ModelRunStatus,
        result: Mapping[str, Any] | None = None,
        error: str | None = None,
        timestamp: datetime,
    ) -> FinanceModelRun:
        with self._lock:
            current = self._runs.get(run_id)
            if current is None:
                raise KeyError("model_run")
            if current.status is not expected:
                raise ModelRunStateConflict(
                    f"model run {run_id} is {current.status}, expected {expected}"
                )
            if target not in self._ALLOWED_TRANSITIONS[current.status]:
                raise ModelRunStateConflict(
                    f"invalid model run transition {current.status} -> {target}"
                )
            started_at = current.started_at
            completed_at = current.completed_at
            if target is ModelRunStatus.RUNNING:
                started_at = timestamp
            if target in {ModelRunStatus.SUCCEEDED, ModelRunStatus.FAILED}:
                completed_at = timestamp
            updated = replace(
                current,
                status=target,
                result=result,
                error=error,
                started_at=started_at,
                completed_at=completed_at,
            )
            self._runs[run_id] = updated
            return updated


class FinanceModelRunService:
    def __init__(
        self,
        context_catalog: ContextCatalogService,
        snapshots: DataSnapshotRepository,
        repository: FinanceModelRunRepository,
        risk_register: RiskRegisterService,
        risk_aggregation: RiskAggregationEngine,
        market_risk_metrics: MarketRiskMetrics,
        garch_t_model: GarchTModel,
        regime_hmm_model: GaussianHmmRegimeModel,
        evt_tail_overlay: EvtTailOverlay,
        copula_dependence_model: CopulaDependenceModel,
        var_backtester: VarBacktester,
    ) -> None:
        self._context_catalog = context_catalog
        self._snapshots = snapshots
        self._repository = repository
        self._risk_register = risk_register
        self._risk_aggregation = risk_aggregation
        self._market_risk_metrics = market_risk_metrics
        self._garch_t_model = garch_t_model
        self._regime_hmm_model = regime_hmm_model
        self._evt_tail_overlay = evt_tail_overlay
        self._copula_dependence_model = copula_dependence_model
        self._var_backtester = var_backtester

    def create_risk_aggregation(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
        risk_ids: tuple[str, ...],
        correlation_matrix: tuple[tuple[Decimal, ...], ...],
        paths: int,
        seed: int,
    ) -> FinanceModelRun:
        context = self._context_catalog.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        payload: Mapping[str, Any] = {
            "risk_ids": risk_ids,
            "correlation_matrix": tuple(
                tuple(str(value) for value in row) for row in correlation_matrix
            ),
            "paths": paths,
            "seed": seed,
        }
        return self._create(
            domain=FinanceModelRunDomain.RISK,
            model_type="aggregation",
            context=context,
            payload=payload,
        )

    def create_market_risk(
        self,
        principal: Principal,
        *,
        company_id: str,
        period_id: str,
        scenario_id: str,
        model_type: MarketRiskModelType,
        payload: Mapping[str, Any],
    ) -> FinanceModelRun:
        context = self._context_catalog.resolve(
            principal,
            company_id=company_id,
            period_id=period_id,
            scenario_id=scenario_id,
        )
        return self._create(
            domain=FinanceModelRunDomain.MARKET_RISK,
            model_type=model_type.value,
            context=context,
            payload=payload,
        )

    def get(
        self,
        principal: Principal,
        *,
        domain: FinanceModelRunDomain,
        run_id: str,
    ) -> FinanceModelRun:
        run = self._repository.get(run_id)
        if run is None or run.domain is not domain:
            raise KeyError("model_run")
        self._context_catalog.resolve(
            principal,
            company_id=run.input_context.company_id,
            period_id=run.input_context.period_id,
            scenario_id=run.input_context.scenario_id,
        )
        return run

    def execute(self, run_id: str) -> FinanceModelRun:
        run = self._repository.transition(
            run_id,
            expected=ModelRunStatus.PENDING,
            target=ModelRunStatus.RUNNING,
            timestamp=self._now(),
        )
        try:
            if run.domain is FinanceModelRunDomain.RISK:
                result = self._execute_risk(run)
            elif run.domain is FinanceModelRunDomain.MARKET_RISK:
                result = self._execute_market_risk(run)
            else:
                raise ValueError(f"unsupported model-run domain: {run.domain}")
        except Exception as exc:
            return self._repository.transition(
                run_id,
                expected=ModelRunStatus.RUNNING,
                target=ModelRunStatus.FAILED,
                error=f"{type(exc).__name__}: {exc}",
                timestamp=self._now(),
            )
        return self._repository.transition(
            run_id,
            expected=ModelRunStatus.RUNNING,
            target=ModelRunStatus.SUCCEEDED,
            result=result,
            timestamp=self._now(),
        )

    def _create(
        self,
        *,
        domain: FinanceModelRunDomain,
        model_type: str,
        context: WorkspaceContext,
        payload: Mapping[str, Any],
    ) -> FinanceModelRun:
        run = FinanceModelRun(
            run_id=uuid4().hex,
            domain=domain,
            model_type=model_type,
            status=ModelRunStatus.PENDING,
            input_context=context,
            input_payload=payload,
            source_snapshot_ids=self._source_snapshot_ids(context),
            projection_version=1,
            result=None,
            error=None,
            created_at=self._now(),
        )
        self._repository.create(run)
        return run

    def _source_snapshot_ids(self, context: WorkspaceContext) -> tuple[str, ...]:
        snapshot_ids: list[str] = []
        for snapshot in self._snapshots.list_all():
            if any(
                record.company == context.company_id
                and record.period == context.period_id
                and record.scenario == context.scenario_id
                for record in snapshot.records
            ):
                snapshot_ids.append(snapshot.snapshot_id)
        return tuple(snapshot_ids)

    def _execute_risk(self, run: FinanceModelRun) -> Mapping[str, Any]:
        if run.model_type != "aggregation":
            raise ValueError(f"unsupported risk model type: {run.model_type}")
        risk_ids = tuple(str(item) for item in run.input_payload["risk_ids"])
        correlations = tuple(
            tuple(Decimal(str(value)) for value in row)
            for row in run.input_payload["correlation_matrix"]
        )
        risks = tuple(self._risk_register.get(risk_id) for risk_id in risk_ids)
        result = self._risk_aggregation.aggregate(
            risks,
            correlations,
            paths=int(run.input_payload["paths"]),
            seed=int(run.input_payload["seed"]),
        )
        return asdict(result)

    def _execute_market_risk(self, run: FinanceModelRun) -> Mapping[str, Any]:
        model_type = MarketRiskModelType(run.model_type)
        payload = run.input_payload
        if model_type is MarketRiskModelType.VAR_ES:
            losses = np.asarray(payload.get("losses", ()), dtype=float)
            confidence = float(payload.get("confidence", 0.99))
            method = MarketRiskVarMethod(
                str(payload.get("method", MarketRiskVarMethod.HISTORICAL.value))
            )
            if method is MarketRiskVarMethod.HISTORICAL:
                return asdict(
                    self._market_risk_metrics.historical(losses, confidence)
                )
            return asdict(self._market_risk_metrics.student_t(losses, confidence))

        if model_type is MarketRiskModelType.GARCH_T:
            returns = np.asarray(payload.get("returns", ()), dtype=float)
            return asdict(self._garch_t_model.fit(returns))

        if model_type is MarketRiskModelType.REGIME_HMM:
            returns = np.asarray(payload.get("returns", ()), dtype=float)
            return asdict(self._regime_hmm_model.fit(returns))

        if model_type is MarketRiskModelType.EVT:
            losses = np.asarray(payload.get("losses", ()), dtype=float)
            threshold_quantile = float(payload.get("threshold_quantile", 0.95))
            return asdict(
                self._evt_tail_overlay.fit(
                    losses,
                    threshold_quantile=threshold_quantile,
                )
            )

        if model_type is MarketRiskModelType.COPULA:
            returns_matrix = np.asarray(payload.get("returns_matrix", ()), dtype=float)
            return asdict(self._copula_dependence_model.fit(returns_matrix))

        if model_type is MarketRiskModelType.VAR_BACKTEST:
            realized_losses = np.asarray(
                payload.get("realized_losses", ()),
                dtype=float,
            )
            var_forecasts = np.asarray(payload.get("var_forecasts", ()), dtype=float)
            return asdict(
                self._var_backtester.evaluate(
                    realized_losses,
                    var_forecasts,
                    confidence=float(payload.get("confidence", 0.99)),
                    significance=float(payload.get("significance", 0.05)),
                )
            )

        raise ValueError(f"unsupported market-risk model type: {run.model_type}")

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
