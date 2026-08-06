from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from .value_objects import CurrencyCode, FiscalPeriod, VersionId


class AccountType(StrEnum):
    REVENUE = "revenue"
    EXPENSE = "expense"
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    CASH_FLOW = "cash_flow"
    STATISTICAL = "statistical"


class ScenarioType(StrEnum):
    ACTUAL = "actual"
    BUDGET = "budget"
    FORECAST = "forecast"
    UPSIDE = "upside"
    DOWNSIDE = "downside"
    STRESS = "stress"


@dataclass(frozen=True, slots=True)
class Company:
    code: str
    name: str
    reporting_currency: CurrencyCode
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("Company code must not be empty")
        if not self.name.strip():
            raise ValueError("Company name must not be empty")


@dataclass(frozen=True, slots=True)
class Account:
    code: str
    name: str
    account_type: AccountType
    parent_code: str | None = None

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("Account code must not be empty")
        if not self.name.strip():
            raise ValueError("Account name must not be empty")
        if self.parent_code == self.code:
            raise ValueError("Account cannot be its own parent")


@dataclass(frozen=True, slots=True)
class DimensionMember:
    dimension: str
    code: str
    name: str
    parent_code: str | None = None

    def __post_init__(self) -> None:
        if not self.dimension.strip():
            raise ValueError("Dimension must not be empty")
        if not self.code.strip():
            raise ValueError("Dimension member code must not be empty")
        if not self.name.strip():
            raise ValueError("Dimension member name must not be empty")
        if self.parent_code == self.code:
            raise ValueError("Dimension member cannot be its own parent")


@dataclass(frozen=True, slots=True)
class Scenario:
    code: str
    name: str
    scenario_type: ScenarioType
    version: VersionId

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("Scenario code must not be empty")
        if not self.name.strip():
            raise ValueError("Scenario name must not be empty")


@dataclass(frozen=True, slots=True)
class FinancialMetric:
    code: str
    name: str
    unit: str
    account_code: str | None = None

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("Metric code must not be empty")
        if not self.name.strip():
            raise ValueError("Metric name must not be empty")
        if not self.unit.strip():
            raise ValueError("Metric unit must not be empty")


@dataclass(frozen=True, slots=True)
class MetricObservation:
    company_id: UUID
    metric_code: str
    period: FiscalPeriod
    scenario_code: str
    version: VersionId
    value: Decimal
    currency: CurrencyCode | None
    dimensions: tuple[DimensionMember, ...] = ()
    source: str = "unknown"

    def __post_init__(self) -> None:
        if not self.metric_code.strip():
            raise ValueError("Observation metric code must not be empty")
        if not self.scenario_code.strip():
            raise ValueError("Observation scenario code must not be empty")
        if not self.value.is_finite():
            raise ValueError("Observation value must be finite")
        if not self.source.strip():
            raise ValueError("Observation source must not be empty")
        keys = [(member.dimension, member.code) for member in self.dimensions]
        if len(keys) != len(set(keys)):
            raise ValueError("Observation contains duplicate dimension members")
