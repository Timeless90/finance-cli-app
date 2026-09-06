from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.performance.performance_management import (
    ComparisonType,
    DimensionKey,
)


class DimensionPayload(BaseModel):
    entity: str = "group"
    segment: str = "all"
    product: str = "all"
    cost_center: str = "all"

    def to_domain(self) -> DimensionKey:
        return DimensionKey(**self.model_dump())


class KpiEvaluationRequest(BaseModel):
    kpi: str
    leaf_values: dict[str, Decimal]


class VarianceContributionPayload(BaseModel):
    driver: str
    amount: Decimal
    source_snapshot_id: str


class VarianceBridgeRequest(BaseModel):
    comparison_type: ComparisonType
    kpi: str
    baseline_version_id: str
    comparison_version_id: str
    baseline_value: Decimal
    comparison_value: Decimal
    contributions: list[VarianceContributionPayload]
    dimensions: DimensionPayload = Field(default_factory=DimensionPayload)


class AccuracyObservationPayload(BaseModel):
    kpi: str
    horizon: int = Field(ge=1)
    actual: Decimal
    forecast: Decimal
    business_unit: str
    model_id: str


class AccuracyRequest(BaseModel):
    observations: list[AccuracyObservationPayload]


class AnomalyObservationPayload(BaseModel):
    period: str
    kpi: str
    value: Decimal
    dimensions: DimensionPayload = Field(default_factory=DimensionPayload)


class AnomalyRequest(BaseModel):
    observations: list[AnomalyObservationPayload]
    robust_z_threshold: Decimal = Decimal("3.5")
    lower_bound: Decimal | None = None
    upper_bound: Decimal | None = None


class CommentaryPayload(BaseModel):
    commentary_id: str
    kpi: str
    period: str
    owner: str
    text: str
    action_ids: list[str] = Field(default_factory=list)


class CommentaryRequirementRequest(BaseModel):
    kpi: str
    period: str
    variance: Decimal
    materiality_threshold: Decimal = Field(ge=0)
    commentary: CommentaryPayload | None = None
