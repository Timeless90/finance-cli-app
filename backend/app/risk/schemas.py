from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.risk.risk_management import (
    ControlStatus,
    FinancialStatement,
    FrequencyModel,
    LimitScope,
    RiskCategory,
    SeverityDistribution,
)


class RiskControlPayload(BaseModel):
    control_id: str
    name: str
    owner: str
    effectiveness: Decimal = Field(ge=0, le=1)
    annual_cost: Decimal = Decimal(0)
    status: ControlStatus = ControlStatus.ACTIVE


class RiskQuantificationPayload(BaseModel):
    distribution: SeverityDistribution
    frequency_model: FrequencyModel = FrequencyModel.BERNOULLI
    occurrence_probability: Decimal = Field(default=Decimal(1), ge=0, le=1)
    annual_frequency: Decimal = Field(default=Decimal(1), ge=0)
    empirical_losses: list[Decimal] = Field(default_factory=list)
    custom_losses: list[Decimal] = Field(default_factory=list)
    lognormal_mu: Decimal | None = None
    lognormal_sigma: Decimal | None = None
    pareto_scale: Decimal | None = None
    pareto_shape: Decimal | None = None


class RiskPayload(BaseModel):
    risk_id: str
    title: str
    cause: str
    event: str
    owner: str
    category: RiskCategory
    horizon_months: int = Field(ge=1)
    quantification: RiskQuantificationPayload
    controls: list[RiskControlPayload] = Field(default_factory=list)
    gross_description: str = ""
    net_description: str = ""
    double_count_group: str | None = None


class AggregateRiskRequest(BaseModel):
    risk_ids: list[str]
    correlation_matrix: list[list[Decimal]]
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42


class RiskLimitRequest(BaseModel):
    limit_id: str
    scope: LimitScope
    scope_key: str
    maximum: Decimal = Field(gt=0)
    warning_ratio: Decimal = Field(default=Decimal("0.80"), gt=0, lt=1)
    exposure: Decimal = Field(ge=0)


class RiskPlanMappingPayload(BaseModel):
    risk_id: str
    statement: FinancialStatement
    metric: str
    period: str
    loss_factor: Decimal = Decimal(1)
    impact_key: str = ""


class RiskToPlanRequest(BaseModel):
    losses: dict[str, Decimal]
    mappings: list[RiskPlanMappingPayload]


class RiskReportRequest(BaseModel):
    risk_ids: list[str]
    correlation_matrix: list[list[Decimal]]
    paths: int = Field(default=10_000, ge=100)
    seed: int = 42
    top_n: int = Field(default=10, ge=1)
