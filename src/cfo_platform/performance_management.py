from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from math import sqrt
from statistics import mean, median
from typing import Iterable, Mapping, Sequence


class ComparisonType(StrEnum):
    PLAN_ACTUAL = "plan_actual"
    FORECAST_ACTUAL = "forecast_actual"
    FORECAST_FORECAST = "forecast_forecast"


class VarianceStatus(StrEnum):
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    UNFAVORABLE = "unfavorable"


class CommentaryStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    PROVIDED = "provided"


@dataclass(frozen=True, slots=True)
class DimensionKey:
    entity: str = "group"
    segment: str = "all"
    product: str = "all"
    cost_center: str = "all"

    def __post_init__(self) -> None:
        if not all(value.strip() for value in self.as_tuple()):
            raise ValueError("dimension values must not be empty")

    def as_tuple(self) -> tuple[str, str, str, str]:
        return self.entity, self.segment, self.product, self.cost_center


@dataclass(frozen=True, slots=True)
class PerformanceValue:
    period: str
    kpi: str
    value: Decimal
    version_id: str
    snapshot_id: str
    dimensions: DimensionKey = DimensionKey()

    def __post_init__(self) -> None:
        for value in (self.period, self.kpi, self.version_id, self.snapshot_id):
            if not value.strip():
                raise ValueError("performance value references must not be empty")


@dataclass(frozen=True, slots=True)
class KpiNode:
    kpi: str
    children: tuple[str, ...] = ()
    subtract_children: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.kpi.strip():
            raise ValueError("kpi must not be empty")
        overlap = set(self.children) & set(self.subtract_children)
        if overlap:
            raise ValueError(f"children cannot be both additive and subtractive: {overlap}")


@dataclass(frozen=True, slots=True)
class KpiEvaluation:
    kpi: str
    value: Decimal
    components: Mapping[str, Decimal]


class KpiTree:
    def __init__(self, nodes: Iterable[KpiNode]) -> None:
        self._nodes = {node.kpi: node for node in nodes}
        if len(self._nodes) == 0:
            raise ValueError("at least one KPI node is required")
        self._validate_references()

    def _validate_references(self) -> None:
        for node in self._nodes.values():
            for child in (*node.children, *node.subtract_children):
                if child not in self._nodes:
                    raise ValueError(f"unknown KPI child: {child}")
        for kpi in self._nodes:
            self._visit(kpi, set(), set())

    def _visit(self, kpi: str, visiting: set[str], visited: set[str]) -> None:
        if kpi in visiting:
            raise ValueError("KPI tree must be acyclic")
        if kpi in visited:
            return
        visiting.add(kpi)
        node = self._nodes[kpi]
        for child in (*node.children, *node.subtract_children):
            self._visit(child, visiting, visited)
        visiting.remove(kpi)
        visited.add(kpi)

    def evaluate(self, kpi: str, leaf_values: Mapping[str, Decimal]) -> KpiEvaluation:
        if kpi not in self._nodes:
            raise KeyError(kpi)
        components: dict[str, Decimal] = {}

        def resolve(name: str) -> Decimal:
            node = self._nodes[name]
            if not node.children and not node.subtract_children:
                if name not in leaf_values:
                    raise ValueError(f"missing leaf value for {name}")
                value = leaf_values[name]
            else:
                value = sum((resolve(child) for child in node.children), Decimal("0"))
                value -= sum(
                    (resolve(child) for child in node.subtract_children), Decimal("0")
                )
            components[name] = value
            return value

        value = resolve(kpi)
        return KpiEvaluation(kpi=kpi, value=value, components=components)


@dataclass(frozen=True, slots=True)
class VarianceContribution:
    driver: str
    amount: Decimal
    source_snapshot_id: str

    def __post_init__(self) -> None:
        if not self.driver.strip() or not self.source_snapshot_id.strip():
            raise ValueError("variance contribution references must not be empty")


@dataclass(frozen=True, slots=True)
class VarianceBridge:
    comparison_type: ComparisonType
    kpi: str
    baseline_version_id: str
    comparison_version_id: str
    baseline_value: Decimal
    comparison_value: Decimal
    contributions: tuple[VarianceContribution, ...]
    dimensions: DimensionKey = DimensionKey()

    @property
    def total_variance(self) -> Decimal:
        return self.comparison_value - self.baseline_value

    @property
    def explained_variance(self) -> Decimal:
        return sum((item.amount for item in self.contributions), Decimal("0"))

    @property
    def unexplained_variance(self) -> Decimal:
        return self.total_variance - self.explained_variance

    @property
    def is_fully_explained(self) -> bool:
        return self.unexplained_variance == Decimal("0")

    def assert_fully_explained(self) -> None:
        if not self.is_fully_explained:
            raise ValueError(
                f"variance bridge is incomplete by {self.unexplained_variance}"
            )


class VarianceAnalysisEngine:
    def build_bridge(
        self,
        *,
        comparison_type: ComparisonType,
        kpi: str,
        baseline_version_id: str,
        comparison_version_id: str,
        baseline_value: Decimal,
        comparison_value: Decimal,
        contributions: Sequence[VarianceContribution],
        dimensions: DimensionKey = DimensionKey(),
    ) -> VarianceBridge:
        bridge = VarianceBridge(
            comparison_type=comparison_type,
            kpi=kpi,
            baseline_version_id=baseline_version_id,
            comparison_version_id=comparison_version_id,
            baseline_value=baseline_value,
            comparison_value=comparison_value,
            contributions=tuple(contributions),
            dimensions=dimensions,
        )
        bridge.assert_fully_explained()
        return bridge

    def price_volume_mix(
        self,
        *,
        baseline_price: Decimal,
        actual_price: Decimal,
        baseline_volume: Decimal,
        actual_volume: Decimal,
        baseline_mix: Decimal,
        actual_mix: Decimal,
        source_snapshot_id: str,
    ) -> tuple[VarianceContribution, ...]:
        price = (actual_price - baseline_price) * baseline_volume * baseline_mix
        volume = (actual_volume - baseline_volume) * baseline_price * baseline_mix
        mix = actual_price * actual_volume * (actual_mix - baseline_mix)
        interaction = (
            actual_price * actual_volume * actual_mix
            - baseline_price * baseline_volume * baseline_mix
            - price
            - volume
            - mix
        )
        return (
            VarianceContribution("price", price, source_snapshot_id),
            VarianceContribution("volume", volume, source_snapshot_id),
            VarianceContribution("mix", mix, source_snapshot_id),
            VarianceContribution("interaction", interaction, source_snapshot_id),
        )


@dataclass(frozen=True, slots=True)
class AccuracyObservation:
    kpi: str
    horizon: int
    actual: Decimal
    forecast: Decimal
    business_unit: str
    model_id: str

    @property
    def error(self) -> Decimal:
        return self.forecast - self.actual


@dataclass(frozen=True, slots=True)
class AccuracyMetrics:
    count: int
    mae: Decimal
    wape: Decimal
    bias: Decimal


@dataclass(frozen=True, slots=True)
class AccuracySlice:
    kpi: str
    business_unit: str
    horizon: int
    model_id: str
    metrics: AccuracyMetrics


class ForecastAccuracyService:
    def summarize(self, observations: Iterable[AccuracyObservation]) -> tuple[AccuracySlice, ...]:
        grouped: dict[tuple[str, str, int, str], list[AccuracyObservation]] = {}
        for item in observations:
            key = (item.kpi, item.business_unit, item.horizon, item.model_id)
            grouped.setdefault(key, []).append(item)
        slices = []
        for (kpi, business_unit, horizon, model_id), items in sorted(grouped.items()):
            absolute_error = sum((abs(item.error) for item in items), Decimal("0"))
            actual_total = sum((abs(item.actual) for item in items), Decimal("0"))
            count = len(items)
            metrics = AccuracyMetrics(
                count=count,
                mae=absolute_error / Decimal(count),
                wape=(absolute_error / actual_total) if actual_total else Decimal("0"),
                bias=sum((item.error for item in items), Decimal("0")) / Decimal(count),
            )
            slices.append(
                AccuracySlice(
                    kpi=kpi,
                    business_unit=business_unit,
                    horizon=horizon,
                    model_id=model_id,
                    metrics=metrics,
                )
            )
        return tuple(slices)


@dataclass(frozen=True, slots=True)
class AnomalyObservation:
    period: str
    kpi: str
    value: Decimal
    dimensions: DimensionKey = DimensionKey()


@dataclass(frozen=True, slots=True)
class AnomalySignal:
    period: str
    kpi: str
    value: Decimal
    median: Decimal
    robust_z_score: Decimal
    rule_breaches: tuple[str, ...]
    dimensions: DimensionKey


class AnomalyDetectionService:
    _MAD_SCALE = Decimal("0.6744897501960817")

    def detect(
        self,
        observations: Sequence[AnomalyObservation],
        *,
        robust_z_threshold: Decimal = Decimal("3.5"),
        lower_bound: Decimal | None = None,
        upper_bound: Decimal | None = None,
    ) -> tuple[AnomalySignal, ...]:
        if len(observations) < 3:
            return ()
        values = [item.value for item in observations]
        center = Decimal(str(median(values)))
        deviations = [abs(value - center) for value in values]
        mad = Decimal(str(median(deviations)))
        signals = []
        for item in observations:
            robust_z = (
                self._MAD_SCALE * (item.value - center) / mad
                if mad != Decimal("0")
                else Decimal("0")
            )
            breaches = []
            if abs(robust_z) > robust_z_threshold:
                breaches.append("robust_z_score")
            if lower_bound is not None and item.value < lower_bound:
                breaches.append("lower_bound")
            if upper_bound is not None and item.value > upper_bound:
                breaches.append("upper_bound")
            if breaches:
                signals.append(
                    AnomalySignal(
                        period=item.period,
                        kpi=item.kpi,
                        value=item.value,
                        median=center,
                        robust_z_score=robust_z,
                        rule_breaches=tuple(breaches),
                        dimensions=item.dimensions,
                    )
                )
        return tuple(signals)


@dataclass(frozen=True, slots=True)
class ManagementCommentary:
    commentary_id: str
    kpi: str
    period: str
    owner: str
    text: str
    action_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value in (self.commentary_id, self.kpi, self.period, self.owner, self.text):
            if not value.strip():
                raise ValueError("commentary fields must not be empty")


@dataclass(frozen=True, slots=True)
class CommentaryRequirement:
    kpi: str
    period: str
    variance: Decimal
    threshold: Decimal
    status: CommentaryStatus
    commentary: ManagementCommentary | None = None


class ManagementCommentaryService:
    def evaluate(
        self,
        *,
        kpi: str,
        period: str,
        variance: Decimal,
        materiality_threshold: Decimal,
        commentary: ManagementCommentary | None = None,
    ) -> CommentaryRequirement:
        if materiality_threshold < 0:
            raise ValueError("materiality_threshold must be non-negative")
        required = abs(variance) >= materiality_threshold
        if commentary is not None:
            if commentary.kpi != kpi or commentary.period != period:
                raise ValueError("commentary must reference the evaluated KPI and period")
            status = CommentaryStatus.PROVIDED
        elif required:
            status = CommentaryStatus.REQUIRED
        else:
            status = CommentaryStatus.NOT_REQUIRED
        return CommentaryRequirement(
            kpi=kpi,
            period=period,
            variance=variance,
            threshold=materiality_threshold,
            status=status,
            commentary=commentary,
        )


def default_cfo_kpi_tree() -> KpiTree:
    return KpiTree(
        (
            KpiNode("revenue"),
            KpiNode("variable_cost"),
            KpiNode("personnel_cost"),
            KpiNode("fixed_operating_cost"),
            KpiNode(
                "ebitda",
                children=("revenue",),
                subtract_children=(
                    "variable_cost",
                    "personnel_cost",
                    "fixed_operating_cost",
                ),
            ),
            KpiNode("depreciation"),
            KpiNode("ebit", children=("ebitda",), subtract_children=("depreciation",)),
            KpiNode("tax"),
            KpiNode("nopat", children=("ebit",), subtract_children=("tax",)),
            KpiNode("operating_cash_flow"),
            KpiNode("capex"),
            KpiNode(
                "free_cash_flow",
                children=("operating_cash_flow",),
                subtract_children=("capex",),
            ),
            KpiNode("invested_capital"),
        )
    )


def population_standard_deviation(values: Sequence[Decimal]) -> Decimal:
    if not values:
        raise ValueError("values must not be empty")
    float_values = [float(value) for value in values]
    center = mean(float_values)
    variance = sum((value - center) ** 2 for value in float_values) / len(float_values)
    return Decimal(str(sqrt(variance)))
