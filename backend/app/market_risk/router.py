from __future__ import annotations

from dataclasses import asdict

import numpy as np
from fastapi import APIRouter

from app.market_risk.market_treasury_risk import (
    CopulaDependenceModel,
    EvtTailOverlay,
    ExposureManagementService,
    GarchTModel,
    GaussianHmmRegimeModel,
    HedgeScenarioEngine,
    MarketExposure,
    MarketRiskMetrics,
    SensitivityEngine,
    VarBacktester,
)
from app.market_risk.schemas import (
    BacktestRequest,
    CopulaRequest,
    EvtRequest,
    ExposurePayload,
    ExposureRequest,
    HedgeRequest,
    RiskMetricRequest,
    SensitivityRequest,
    SeriesRequest,
)


def _exposures(payload: list[ExposurePayload]) -> list[MarketExposure]:
    return [
        MarketExposure(
            exposure_id=item.exposure_id,
            exposure_type=item.exposure_type,
            risk_factor=item.risk_factor,
            amount=item.amount,
            currency=item.currency,
            delta=item.delta,
        )
        for item in payload
    ]


def build_market_risk_router(
    exposure_service: ExposureManagementService,
    sensitivity_engine: SensitivityEngine,
    metrics: MarketRiskMetrics,
    garch: GarchTModel,
    hmm: GaussianHmmRegimeModel,
    evt: EvtTailOverlay,
    copula: CopulaDependenceModel,
    hedge_engine: HedgeScenarioEngine,
    backtester: VarBacktester,
) -> APIRouter:
    router = APIRouter(prefix="/market-risk", tags=["market-risk"])

    @router.post("/exposures/aggregate")
    def aggregate(request: ExposureRequest) -> list[dict[str, object]]:
        return [
            asdict(item)
            for item in exposure_service.aggregate(_exposures(request.exposures))
        ]

    @router.post("/sensitivities")
    def sensitivities(request: SensitivityRequest) -> list[dict[str, object]]:
        aggregated = exposure_service.aggregate(_exposures(request.exposures))
        return [
            asdict(item)
            for item in sensitivity_engine.evaluate(aggregated, request.shocks)
        ]

    @router.post("/var-es")
    def var_es(request: RiskMetricRequest) -> dict[str, object]:
        losses = np.asarray(request.losses, dtype=float)
        result = (
            metrics.student_t(losses, request.confidence)
            if request.method == "student_t"
            else metrics.historical(losses, request.confidence)
        )
        return asdict(result)

    @router.post("/models/garch-t")
    def fit_garch(request: SeriesRequest) -> dict[str, object]:
        return asdict(garch.fit(np.asarray(request.returns, dtype=float)))

    @router.post("/models/regime-hmm")
    def fit_hmm(request: SeriesRequest) -> dict[str, object]:
        return asdict(hmm.fit(np.asarray(request.returns, dtype=float)))

    @router.post("/models/evt")
    def fit_evt(request: EvtRequest) -> dict[str, object]:
        return asdict(
            evt.fit(
                np.asarray(request.losses, dtype=float),
                threshold_quantile=request.threshold_quantile,
            )
        )

    @router.post("/models/copula")
    def fit_copula(request: CopulaRequest) -> dict[str, object]:
        return asdict(copula.fit(np.asarray(request.returns, dtype=float)))

    @router.post("/hedges/effectiveness")
    def hedge_effectiveness(request: HedgeRequest) -> dict[str, object]:
        exposure = np.asarray(request.exposure_returns, dtype=float)
        hedge = np.asarray(request.hedge_returns, dtype=float)
        ratio = request.hedge_ratio
        if ratio is None:
            ratio = hedge_engine.optimal_ratio(exposure, hedge)
        return asdict(hedge_engine.evaluate(exposure, hedge, hedge_ratio=ratio))

    @router.post("/backtests/var")
    def backtest(request: BacktestRequest) -> dict[str, object]:
        return asdict(
            backtester.evaluate(
                np.asarray(request.realized_losses, dtype=float),
                np.asarray(request.var_forecasts, dtype=float),
                confidence=request.confidence,
                significance=request.significance,
            )
        )

    return router


__all__ = [
    "BacktestRequest",
    "CopulaRequest",
    "EvtRequest",
    "ExposurePayload",
    "ExposureRequest",
    "HedgeRequest",
    "RiskMetricRequest",
    "SensitivityRequest",
    "SeriesRequest",
    "_exposures",
    "build_market_risk_router",
]
