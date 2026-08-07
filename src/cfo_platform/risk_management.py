from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from math import exp, isclose, log, sqrt
from random import Random
from statistics import NormalDist, mean


ZERO = Decimal("0")
ONE = Decimal("1")
_NORMAL = NormalDist()


class RiskCategory(StrEnum):
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    CYBER = "cyber"
    MARKET = "market"
    LIQUIDITY = "liquidity"
    OTHER = "other"


class SeverityDistribution(StrEnum):
    EMPIRICAL = "empirical"
    LOGNORMAL = "lognormal"
    PARETO = "pareto"
    CUSTOM = "custom"


class FrequencyModel(StrEnum):
    BERNOULLI = "bernoulli"
    POISSON = "poisson"


class ControlStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    INEFFECTIVE = "ineffective"
    RETIRED = "retired"


class LimitStatus(StrEnum):
    HEALTHY = "healthy"
    WARNING = "warning"
    BREACHED = "breached"


class LimitScope(StrEnum):
    CATEGORY = "category"
    KPI = "kpi"
    RISK_CAPACITY = "risk_capacity"


class FinancialStatement(StrEnum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


@dataclass(frozen=True, slots=True)
class RiskControl:
    control_id: str
    name: str
    owner: str
    effectiveness: Decimal
    annual_cost: Decimal = ZERO
    status: ControlStatus = ControlStatus.ACTIVE

    def __post_init__(self) -> None:
        if not ZERO <= self.effectiveness <= ONE:
            raise ValueError("control effectiveness must be between 0 and 1")
        if self.annual_cost < ZERO:
            raise ValueError("control cost must be non-negative")


@dataclass(frozen=True, slots=True)
class RiskQuantification:
    distribution: SeverityDistribution
    frequency_model: FrequencyModel = FrequencyModel.BERNOULLI
    occurrence_probability: Decimal = ONE
    annual_frequency: Decimal = ONE
    empirical_losses: tuple[Decimal, ...] = ()
    custom_losses: tuple[Decimal, ...] = ()
    lognormal_mu: Decimal | None = None
    lognormal_sigma: Decimal | None = None
    pareto_scale: Decimal | None = None
    pareto_shape: Decimal | None = None

    def __post_init__(self) -> None:
        if not ZERO <= self.occurrence_probability <= ONE:
            raise ValueError("occurrence probability must be between 0 and 1")
        if self.annual_frequency < ZERO:
            raise ValueError("annual frequency must be non-negative")
        if self.distribution == SeverityDistribution.EMPIRICAL:
            self._validate_losses(self.empirical_losses, "empirical")
        elif self.distribution == SeverityDistribution.CUSTOM:
            self._validate_losses(self.custom_losses, "custom")
        elif self.distribution == SeverityDistribution.LOGNORMAL:
            if self.lognormal_mu is None or self.lognormal_sigma is None:
                raise ValueError("lognormal distribution requires mu and sigma")
            if self.lognormal_sigma <= ZERO:
                raise ValueError("lognormal sigma must be positive")
        elif self.distribution == SeverityDistribution.PARETO:
            if self.pareto_scale is None or self.pareto_shape is None:
                raise ValueError("Pareto distribution requires scale and shape")
            if self.pareto_scale <= ZERO or self.pareto_shape <= ONE:
                raise ValueError("Pareto scale must be positive and shape must exceed 1")

    @staticmethod
    def _validate_losses(values: tuple[Decimal, ...], label: str) -> None:
        if not values:
            raise ValueError(f"{label} distribution requires loss observations")
        if any(value < ZERO for value in values):
            raise ValueError(f"{label} losses must be non-negative")


@dataclass(frozen=True, slots=True)
class RiskRecord:
    risk_id: str
    title: str
    cause: str
    event: str
    owner: str
    category: RiskCategory
    horizon_months: int
    quantification: RiskQuantification
    controls: tuple[RiskControl, ...] = ()
    gross_description: str = ""
    net_description: str = ""
    double_count_group: str | None = None

    def __post_init__(self) -> None:
        if not self.risk_id.strip():
            raise ValueError("risk_id must not be empty")
        if not self.title.strip() or not self.owner.strip():
            raise ValueError("risk title and owner must not be empty")
        if self.horizon_months < 1:
            raise ValueError("risk horizon must be positive")


class InMemoryRiskRegister:
    def __init__(self) -> None:
        self._risks: dict[str, RiskRecord] = {}

    def save(self, risk: RiskRecord) -> RiskRecord:
        if risk.risk_id in self._risks:
            raise ValueError(f"risk already exists: {risk.risk_id}")
        self._risks[risk.risk_id] = risk
        return risk

    def replace(self, risk: RiskRecord) -> RiskRecord:
        if risk.risk_id not in self._risks:
            raise KeyError(risk.risk_id)
        self._risks[risk.risk_id] = risk
        return risk

    def get(self, risk_id: str) -> RiskRecord:
        try:
            return self._risks[risk_id]
        except KeyError as exc:
            raise KeyError(f"unknown risk: {risk_id}") from exc

    def list(self) -> tuple[RiskRecord, ...]:
        return tuple(self._risks[key] for key in sorted(self._risks))


class RiskRegisterService:
    def __init__(self, repository: InMemoryRiskRegister) -> None:
        self._repository = repository

    def register(self, risk: RiskRecord) -> RiskRecord:
        return self._repository.save(risk)

    def replace(self, risk: RiskRecord) -> RiskRecord:
        return self._repository.replace(risk)

    def get(self, risk_id: str) -> RiskRecord:
        return self._repository.get(risk_id)

    def list(self) -> tuple[RiskRecord, ...]:
        return self._repository.list()


@dataclass(frozen=True, slots=True)
class RiskMitigationResult:
    risk_id: str
    gross_loss: Decimal
    residual_loss: Decimal
    avoided_loss: Decimal
    annual_control_cost: Decimal
    residual_factor: Decimal


class RiskQuantificationEngine:
    def expected_severity(self, model: RiskQuantification) -> Decimal:
        if model.distribution == SeverityDistribution.EMPIRICAL:
            return Decimal(str(mean(model.empirical_losses)))
        if model.distribution == SeverityDistribution.CUSTOM:
            return Decimal(str(mean(model.custom_losses)))
        if model.distribution == SeverityDistribution.LOGNORMAL:
            assert model.lognormal_mu is not None
            assert model.lognormal_sigma is not None
            value = exp(float(model.lognormal_mu) + float(model.lognormal_sigma) ** 2 / 2)
            return Decimal(str(value))
        assert model.pareto_scale is not None
        assert model.pareto_shape is not None
        return model.pareto_scale * model.pareto_shape / (model.pareto_shape - ONE)

    def expected_gross_loss(self, risk: RiskRecord) -> Decimal:
        model = risk.quantification
        severity = self.expected_severity(model)
        if model.frequency_model == FrequencyModel.BERNOULLI:
            return model.occurrence_probability * severity
        return model.annual_frequency * severity

    def mitigation(self, risk: RiskRecord, gross_loss: Decimal) -> RiskMitigationResult:
        factor = ONE
        annual_cost = ZERO
        for control in risk.controls:
            if control.status == ControlStatus.ACTIVE:
                factor *= ONE - control.effectiveness
                annual_cost += control.annual_cost
        residual = gross_loss * factor
        return RiskMitigationResult(
            risk_id=risk.risk_id,
            gross_loss=gross_loss,
            residual_loss=residual,
            avoided_loss=gross_loss - residual,
            annual_control_cost=annual_cost,
            residual_factor=factor,
        )

    def sample_severity(self, model: RiskQuantification, uniform: float) -> Decimal:
        bounded = min(max(uniform, 1e-12), 1 - 1e-12)
        if model.distribution == SeverityDistribution.EMPIRICAL:
            return self._sample_discrete(model.empirical_losses, bounded)
        if model.distribution == SeverityDistribution.CUSTOM:
            return self._sample_discrete(model.custom_losses, bounded)
        if model.distribution == SeverityDistribution.LOGNORMAL:
            assert model.lognormal_mu is not None
            assert model.lognormal_sigma is not None
            z_score = _NORMAL.inv_cdf(bounded)
            value = exp(float(model.lognormal_mu) + float(model.lognormal_sigma) * z_score)
            return Decimal(str(value))
        assert model.pareto_scale is not None
        assert model.pareto_shape is not None
        value = float(model.pareto_scale) / ((1 - bounded) ** (1 / float(model.pareto_shape)))
        return Decimal(str(value))

    @staticmethod
    def _sample_discrete(values: tuple[Decimal, ...], uniform: float) -> Decimal:
        index = min(int(uniform * len(values)), len(values) - 1)
        return values[index]


@dataclass(frozen=True, slots=True)
class RiskContribution:
    risk_id: str
    mean_gross_loss: Decimal
    mean_net_loss: Decimal
    p95_net_loss: Decimal
    expected_loss_share: Decimal
    mitigation_effect: Decimal


@dataclass(frozen=True, slots=True)
class RiskPortfolioDistribution:
    paths: int
    seed: int
    mean_gross_loss: Decimal
    mean_net_loss: Decimal
    p50_net_loss: Decimal
    p90_net_loss: Decimal
    p95_net_loss: Decimal
    p99_net_loss: Decimal
    expected_shortfall_95: Decimal
    contributions: tuple[RiskContribution, ...]


class RiskAggregationEngine:
    def __init__(self, quantification: RiskQuantificationEngine | None = None) -> None:
        self._quantification = quantification or RiskQuantificationEngine()

    def aggregate(
        self,
        risks: tuple[RiskRecord, ...],
        correlation_matrix: tuple[tuple[Decimal, ...], ...],
        *,
        paths: int = 10_000,
        seed: int = 42,
    ) -> RiskPortfolioDistribution:
        if not risks:
            raise ValueError("at least one risk is required")
        if paths < 100:
            raise ValueError("at least 100 Monte Carlo paths are required")
        self._check_double_count_groups(risks)
        factor = self._cholesky(self._validate_correlation(correlation_matrix, len(risks)))
        rng = Random(seed)
        gross_by_risk = [[] for _ in risks]
        net_by_risk = [[] for _ in risks]
        gross_totals: list[Decimal] = []
        net_totals: list[Decimal] = []

        for _ in range(paths):
            occurrence_uniforms = self._correlated_uniforms(rng, factor)
            severity_uniforms = self._correlated_uniforms(rng, factor)
            gross_total = ZERO
            net_total = ZERO
            for index, risk in enumerate(risks):
                gross = self._sample_annual_loss(
                    risk,
                    occurrence_uniforms[index],
                    severity_uniforms[index],
                    rng,
                )
                mitigation = self._quantification.mitigation(risk, gross)
                gross_by_risk[index].append(gross)
                net_by_risk[index].append(mitigation.residual_loss)
                gross_total += gross
                net_total += mitigation.residual_loss
            gross_totals.append(gross_total)
            net_totals.append(net_total)

        mean_gross = self._mean_decimal(gross_totals)
        mean_net = self._mean_decimal(net_totals)
        contributions: list[RiskContribution] = []
        for risk, gross_values, net_values in zip(risks, gross_by_risk, net_by_risk, strict=True):
            risk_mean_gross = self._mean_decimal(gross_values)
            risk_mean_net = self._mean_decimal(net_values)
            share = risk_mean_net / mean_net if mean_net > ZERO else ZERO
            contributions.append(
                RiskContribution(
                    risk_id=risk.risk_id,
                    mean_gross_loss=risk_mean_gross,
                    mean_net_loss=risk_mean_net,
                    p95_net_loss=self._percentile(net_values, Decimal("0.95")),
                    expected_loss_share=share,
                    mitigation_effect=risk_mean_gross - risk_mean_net,
                )
            )
        contributions.sort(key=lambda item: item.mean_net_loss, reverse=True)
        p95 = self._percentile(net_totals, Decimal("0.95"))
        tail = [value for value in net_totals if value >= p95]
        return RiskPortfolioDistribution(
            paths=paths,
            seed=seed,
            mean_gross_loss=mean_gross,
            mean_net_loss=mean_net,
            p50_net_loss=self._percentile(net_totals, Decimal("0.50")),
            p90_net_loss=self._percentile(net_totals, Decimal("0.90")),
            p95_net_loss=p95,
            p99_net_loss=self._percentile(net_totals, Decimal("0.99")),
            expected_shortfall_95=self._mean_decimal(tail),
            contributions=tuple(contributions),
        )

    def _sample_annual_loss(
        self,
        risk: RiskRecord,
        occurrence_uniform: float,
        severity_uniform: float,
        rng: Random,
    ) -> Decimal:
        model = risk.quantification
        if model.frequency_model == FrequencyModel.BERNOULLI:
            events = 1 if occurrence_uniform < float(model.occurrence_probability) else 0
        else:
            events = self._poisson_from_uniform(float(model.annual_frequency), occurrence_uniform)
        total = ZERO
        for event_index in range(events):
            uniform = severity_uniform if event_index == 0 else rng.random()
            total += self._quantification.sample_severity(model, uniform)
        return total

    @staticmethod
    def _poisson_from_uniform(rate: float, uniform: float) -> int:
        if rate <= 0:
            return 0
        probability = exp(-rate)
        cumulative = probability
        count = 0
        while uniform > cumulative:
            count += 1
            probability *= rate / count
            cumulative += probability
            if count > 10_000:
                raise RuntimeError("Poisson inverse CDF did not converge")
        return count

    @staticmethod
    def _validate_correlation(
        matrix: tuple[tuple[Decimal, ...], ...], size: int
    ) -> list[list[float]]:
        if len(matrix) != size or any(len(row) != size for row in matrix):
            raise ValueError("correlation matrix dimensions must match risk count")
        converted = [[float(value) for value in row] for row in matrix]
        for row_index in range(size):
            if not isclose(converted[row_index][row_index], 1.0, abs_tol=1e-9):
                raise ValueError("correlation matrix diagonal must equal 1")
            for column_index in range(size):
                value = converted[row_index][column_index]
                if value < -1 or value > 1:
                    raise ValueError("correlations must be between -1 and 1")
                if not isclose(value, converted[column_index][row_index], abs_tol=1e-9):
                    raise ValueError("correlation matrix must be symmetric")
        return converted

    @staticmethod
    def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
        size = len(matrix)
        lower = [[0.0] * size for _ in range(size)]
        for row in range(size):
            for column in range(row + 1):
                subtotal = sum(lower[row][k] * lower[column][k] for k in range(column))
                if row == column:
                    diagonal = matrix[row][row] - subtotal
                    if diagonal < -1e-10:
                        raise ValueError("correlation matrix must be positive semidefinite")
                    lower[row][column] = sqrt(max(diagonal, 0.0))
                elif lower[column][column] > 1e-12:
                    lower[row][column] = (matrix[row][column] - subtotal) / lower[column][column]
                elif abs(matrix[row][column] - subtotal) > 1e-10:
                    raise ValueError("correlation matrix must be positive semidefinite")
        return lower

    @staticmethod
    def _correlated_uniforms(rng: Random, lower: list[list[float]]) -> list[float]:
        independent = [rng.gauss(0.0, 1.0) for _ in lower]
        correlated = [
            sum(lower[row][column] * independent[column] for column in range(row + 1))
            for row in range(len(lower))
        ]
        return [_NORMAL.cdf(value) for value in correlated]

    @staticmethod
    def _mean_decimal(values: list[Decimal]) -> Decimal:
        return sum(values, ZERO) / Decimal(len(values)) if values else ZERO

    @staticmethod
    def _percentile(values: list[Decimal], probability: Decimal) -> Decimal:
        ordered = sorted(values)
        if not ordered:
            return ZERO
        position = float(probability) * (len(ordered) - 1)
        lower_index = int(position)
        upper_index = min(lower_index + 1, len(ordered) - 1)
        fraction = Decimal(str(position - lower_index))
        return ordered[lower_index] + (ordered[upper_index] - ordered[lower_index]) * fraction

    @staticmethod
    def _check_double_count_groups(risks: tuple[RiskRecord, ...]) -> None:
        groups: dict[str, list[str]] = {}
        for risk in risks:
            if risk.double_count_group:
                groups.setdefault(risk.double_count_group, []).append(risk.risk_id)
        duplicates = {group: ids for group, ids in groups.items() if len(ids) > 1}
        if duplicates:
            details = ", ".join(f"{group}={ids}" for group, ids in sorted(duplicates.items()))
            raise ValueError(f"potential double counting detected: {details}")


@dataclass(frozen=True, slots=True)
class RiskLimit:
    limit_id: str
    scope: LimitScope
    scope_key: str
    maximum: Decimal
    warning_ratio: Decimal = Decimal("0.80")

    def __post_init__(self) -> None:
        if self.maximum <= ZERO:
            raise ValueError("risk limit maximum must be positive")
        if not ZERO < self.warning_ratio < ONE:
            raise ValueError("warning ratio must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class RiskLimitResult:
    limit_id: str
    exposure: Decimal
    maximum: Decimal
    utilization: Decimal
    headroom: Decimal
    status: LimitStatus


class RiskAppetiteEngine:
    def evaluate(self, limit: RiskLimit, exposure: Decimal) -> RiskLimitResult:
        utilization = exposure / limit.maximum
        if exposure > limit.maximum:
            status = LimitStatus.BREACHED
        elif utilization >= limit.warning_ratio:
            status = LimitStatus.WARNING
        else:
            status = LimitStatus.HEALTHY
        return RiskLimitResult(
            limit_id=limit.limit_id,
            exposure=exposure,
            maximum=limit.maximum,
            utilization=utilization,
            headroom=limit.maximum - exposure,
            status=status,
        )


@dataclass(frozen=True, slots=True)
class RiskPlanMapping:
    risk_id: str
    statement: FinancialStatement
    metric: str
    period: str
    loss_factor: Decimal = ONE
    impact_key: str = ""

    def resolved_impact_key(self) -> str:
        return self.impact_key or f"{self.statement}:{self.metric}:{self.period}:{self.risk_id}"


@dataclass(frozen=True, slots=True)
class RiskPlanImpact:
    risk_id: str
    statement: FinancialStatement
    metric: str
    period: str
    amount: Decimal
    impact_key: str


class RiskToPlanEngine:
    def integrate(
        self,
        losses: dict[str, Decimal],
        mappings: tuple[RiskPlanMapping, ...],
    ) -> tuple[RiskPlanImpact, ...]:
        seen_keys: set[str] = set()
        impacts: list[RiskPlanImpact] = []
        for mapping in mappings:
            key = mapping.resolved_impact_key()
            if key in seen_keys:
                raise ValueError(f"duplicate plan impact mapping: {key}")
            seen_keys.add(key)
            if mapping.risk_id not in losses:
                raise ValueError(f"missing risk loss for mapping: {mapping.risk_id}")
            impacts.append(
                RiskPlanImpact(
                    risk_id=mapping.risk_id,
                    statement=mapping.statement,
                    metric=mapping.metric,
                    period=mapping.period,
                    amount=-losses[mapping.risk_id] * mapping.loss_factor,
                    impact_key=key,
                )
            )
        return tuple(impacts)


@dataclass(frozen=True, slots=True)
class RiskHeatmapPoint:
    risk_id: str
    probability_band: str
    impact_band: str
    expected_gross_loss: Decimal
    expected_net_loss: Decimal


@dataclass(frozen=True, slots=True)
class RiskReport:
    top_risks: tuple[RiskContribution, ...]
    heatmap: tuple[RiskHeatmapPoint, ...]
    portfolio: RiskPortfolioDistribution
    methodology: tuple[str, ...]
    mitigation_total: Decimal


class RiskReportingService:
    def __init__(self, quantification: RiskQuantificationEngine | None = None) -> None:
        self._quantification = quantification or RiskQuantificationEngine()

    def build(
        self,
        risks: tuple[RiskRecord, ...],
        portfolio: RiskPortfolioDistribution,
        *,
        top_n: int = 10,
    ) -> RiskReport:
        contribution_by_id = {item.risk_id: item for item in portfolio.contributions}
        heatmap: list[RiskHeatmapPoint] = []
        for risk in risks:
            expected_gross = self._quantification.expected_gross_loss(risk)
            mitigation = self._quantification.mitigation(risk, expected_gross)
            heatmap.append(
                RiskHeatmapPoint(
                    risk_id=risk.risk_id,
                    probability_band=self._probability_band(risk.quantification),
                    impact_band=self._impact_band(mitigation.residual_loss),
                    expected_gross_loss=expected_gross,
                    expected_net_loss=mitigation.residual_loss,
                )
            )
        mitigation_total = sum(
            (item.mitigation_effect for item in contribution_by_id.values()),
            ZERO,
        )
        return RiskReport(
            top_risks=portfolio.contributions[:top_n],
            heatmap=tuple(heatmap),
            portfolio=portfolio,
            methodology=(
                "Monte Carlo aggregation with deterministic random seed",
                "Linear correlation matrix validated for symmetry and positive semidefiniteness",
                "Gross and residual risk are reported separately",
                "Copula dependence is intentionally deferred until data and governance maturity",
            ),
            mitigation_total=mitigation_total,
        )

    @staticmethod
    def _probability_band(model: RiskQuantification) -> str:
        probability = (
            model.occurrence_probability
            if model.frequency_model == FrequencyModel.BERNOULLI
            else ONE - Decimal(str(exp(-float(model.annual_frequency))))
        )
        if probability < Decimal("0.10"):
            return "low"
        if probability < Decimal("0.30"):
            return "medium"
        if probability < Decimal("0.60"):
            return "high"
        return "very_high"

    @staticmethod
    def _impact_band(loss: Decimal) -> str:
        if loss < Decimal("100000"):
            return "low"
        if loss < Decimal("1000000"):
            return "medium"
        if loss < Decimal("10000000"):
            return "high"
        return "very_high"
