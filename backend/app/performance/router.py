from __future__ import annotations

from fastapi import APIRouter

from app.performance.performance_management import (
    AccuracyObservation,
    AnomalyDetectionService,
    AnomalyObservation,
    CommentaryStatus,
    ForecastAccuracyService,
    ManagementCommentary,
    ManagementCommentaryService,
    VarianceAnalysisEngine,
    VarianceContribution,
    default_cfo_kpi_tree,
)
from app.performance.schemas import (
    AccuracyObservationPayload,
    AccuracyRequest,
    AnomalyObservationPayload,
    AnomalyRequest,
    CommentaryPayload,
    CommentaryRequirementRequest,
    DimensionPayload,
    KpiEvaluationRequest,
    VarianceBridgeRequest,
    VarianceContributionPayload,
)


def build_performance_router(
    variance_engine: VarianceAnalysisEngine,
    accuracy_service: ForecastAccuracyService,
    anomaly_service: AnomalyDetectionService,
    commentary_service: ManagementCommentaryService,
) -> APIRouter:
    router = APIRouter(prefix="/performance", tags=["performance"])

    @router.post("/kpi-tree/evaluate")
    def evaluate_kpi(payload: KpiEvaluationRequest) -> dict[str, object]:
        result = default_cfo_kpi_tree().evaluate(payload.kpi, payload.leaf_values)
        return {
            "kpi": result.kpi,
            "value": result.value,
            "components": result.components,
        }

    @router.post("/variance-bridges")
    def build_variance_bridge(payload: VarianceBridgeRequest) -> dict[str, object]:
        bridge = variance_engine.build_bridge(
            comparison_type=payload.comparison_type,
            kpi=payload.kpi,
            baseline_version_id=payload.baseline_version_id,
            comparison_version_id=payload.comparison_version_id,
            baseline_value=payload.baseline_value,
            comparison_value=payload.comparison_value,
            contributions=tuple(
                VarianceContribution(**item.model_dump())
                for item in payload.contributions
            ),
            dimensions=payload.dimensions.to_domain(),
        )
        return {
            "comparison_type": bridge.comparison_type,
            "kpi": bridge.kpi,
            "baseline_version_id": bridge.baseline_version_id,
            "comparison_version_id": bridge.comparison_version_id,
            "baseline_value": bridge.baseline_value,
            "comparison_value": bridge.comparison_value,
            "total_variance": bridge.total_variance,
            "explained_variance": bridge.explained_variance,
            "unexplained_variance": bridge.unexplained_variance,
            "is_fully_explained": bridge.is_fully_explained,
            "contributions": bridge.contributions,
            "dimensions": bridge.dimensions,
        }

    @router.post("/forecast-accuracy")
    def summarize_accuracy(payload: AccuracyRequest) -> dict[str, object]:
        slices = accuracy_service.summarize(
            AccuracyObservation(**item.model_dump()) for item in payload.observations
        )
        return {"slices": slices}

    @router.post("/anomalies")
    def detect_anomalies(payload: AnomalyRequest) -> dict[str, object]:
        signals = anomaly_service.detect(
            tuple(
                AnomalyObservation(
                    period=item.period,
                    kpi=item.kpi,
                    value=item.value,
                    dimensions=item.dimensions.to_domain(),
                )
                for item in payload.observations
            ),
            robust_z_threshold=payload.robust_z_threshold,
            lower_bound=payload.lower_bound,
            upper_bound=payload.upper_bound,
        )
        return {"signals": signals}

    @router.post("/commentary/requirements")
    def evaluate_commentary(payload: CommentaryRequirementRequest) -> dict[str, object]:
        commentary = (
            ManagementCommentary(
                commentary_id=payload.commentary.commentary_id,
                kpi=payload.commentary.kpi,
                period=payload.commentary.period,
                owner=payload.commentary.owner,
                text=payload.commentary.text,
                action_ids=tuple(payload.commentary.action_ids),
            )
            if payload.commentary is not None
            else None
        )
        requirement = commentary_service.evaluate(
            kpi=payload.kpi,
            period=payload.period,
            variance=payload.variance,
            materiality_threshold=payload.materiality_threshold,
            commentary=commentary,
        )
        return {
            "kpi": requirement.kpi,
            "period": requirement.period,
            "variance": requirement.variance,
            "threshold": requirement.threshold,
            "status": CommentaryStatus(requirement.status),
            "commentary": requirement.commentary,
        }

    return router


__all__ = [
    "AccuracyObservationPayload",
    "AccuracyRequest",
    "AnomalyObservationPayload",
    "AnomalyRequest",
    "CommentaryPayload",
    "CommentaryRequirementRequest",
    "DimensionPayload",
    "KpiEvaluationRequest",
    "VarianceBridgeRequest",
    "VarianceContributionPayload",
    "build_performance_router",
]
