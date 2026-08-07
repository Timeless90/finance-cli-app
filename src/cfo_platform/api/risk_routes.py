from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from cfo_platform.risk_management import (
    ControlStatus,
    FinancialStatement,
    FrequencyModel,
    LimitScope,
    RiskAggregationEngine,
    RiskAppetiteEngine,
    RiskCategory,
    RiskControl,
    RiskLimit,
    RiskPlanMapping,
    RiskQuantification,
    RiskQuantificationEngine,
    RiskRecord,
    RiskRegisterService,
    RiskReportingService,
    RiskToPlanEngine,
    SeverityDistribution,
)


class RiskControlPayload(BaseModel):
    control_id: str
    name: str
    owner: str
    effectiveness: Decimal = Field(ge=0, le=1)
    annual_cost: Decimal = Decimal("0")
    status: ControlStatus = ControlStatus.ACTIVE


class RiskQuantificationPayload(BaseModel):
    distribution: SeverityDistribution
    frequency_model: FrequencyModel = FrequencyModel.BERNOULLI
    occurrence_probability: Decimal = Field(default=Decimal("1"), ge=0, le=1)
    annual_frequency: Decimal = Field(default=Decimal("1"), ge=0)
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
    loss_factor: Decimal = Decimal("1")
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


def _to_domain(payload: RiskPayload) -> RiskRecord:
    quantification = RiskQuantification(
        distribution=payload.quantification.distribution,
        frequency_model=payload.quantification.frequency_model,
        occurrence_probability=payload.quantification.occurrence_probability,
        annual_frequency=payload.quantification.annual_frequency,
        empirical_losses=tuple(payload.quantification.empirical_losses),
        custom_losses=tuple(payload.quantification.custom_losses),
        lognormal_mu=payload.quantification.lognormal_mu,
        lognormal_sigma=payload.quantification.lognormal_sigma,
        pareto_scale=payload.quantification.pareto_scale,
        pareto_shape=payload.quantification.pareto_shape,
    )
    controls = tuple(RiskControl(**item.model_dump()) for item in payload.controls)
    return RiskRecord(
        risk_id=payload.risk_id,
        title=payload.title,
        cause=payload.cause,
        event=payload.event,
        owner=payload.owner,
        category=payload.category,
        horizon_months=payload.horizon_months,
        quantification=quantification,
        controls=controls,
        gross_description=payload.gross_description,
        net_description=payload.net_description,
        double_count_group=payload.double_count_group,
    )


def build_risk_router(
    register: RiskRegisterService,
    quantification: RiskQuantificationEngine,
    aggregation: RiskAggregationEngine,
    appetite: RiskAppetiteEngine,
    risk_to_plan: RiskToPlanEngine,
    reporting: RiskReportingService,
) -> APIRouter:
    router = APIRouter(prefix="/risk", tags=["risk"])

    @router.post("/register")
    def register_risk(payload: RiskPayload) -> dict[str, object]:
        return {"risk": register.register(_to_domain(payload))}

    @router.get("/register")
    def list_risks() -> dict[str, object]:
        return {"risks": register.list()}

    @router.get("/register/{risk_id}")
    def get_risk(risk_id: str) -> dict[str, object]:
        return {"risk": register.get(risk_id)}

    @router.post("/quantification/expected-loss")
    def expected_loss(payload: RiskPayload) -> dict[str, object]:
        risk = _to_domain(payload)
        gross = quantification.expected_gross_loss(risk)
        mitigation = quantification.mitigation(risk, gross)
        return {"gross_expected_loss": gross, "mitigation": mitigation}

    @router.post("/aggregation")
    def aggregate_risks(payload: AggregateRiskRequest) -> dict[str, object]:
        risks = tuple(register.get(risk_id) for risk_id in payload.risk_ids)
        result = aggregation.aggregate(
            risks,
            tuple(tuple(row) for row in payload.correlation_matrix),
            paths=payload.paths,
            seed=payload.seed,
        )
        return {"portfolio": result}

    @router.post("/limits/evaluate")
    def evaluate_limit(payload: RiskLimitRequest) -> dict[str, object]:
        definition = RiskLimit(
            limit_id=payload.limit_id,
            scope=payload.scope,
            scope_key=payload.scope_key,
            maximum=payload.maximum,
            warning_ratio=payload.warning_ratio,
        )
        return {"result": appetite.evaluate(definition, payload.exposure)}

    @router.post("/plan/integrate")
    def integrate_plan(payload: RiskToPlanRequest) -> dict[str, object]:
        mappings = tuple(RiskPlanMapping(**item.model_dump()) for item in payload.mappings)
        return {"impacts": risk_to_plan.integrate(payload.losses, mappings)}

    @router.post("/reports")
    def build_report(payload: RiskReportRequest) -> dict[str, object]:
        risks = tuple(register.get(risk_id) for risk_id in payload.risk_ids)
        portfolio = aggregation.aggregate(
            risks,
            tuple(tuple(row) for row in payload.correlation_matrix),
            paths=payload.paths,
            seed=payload.seed,
        )
        return {"report": reporting.build(risks, portfolio, top_n=payload.top_n)}

    return router
