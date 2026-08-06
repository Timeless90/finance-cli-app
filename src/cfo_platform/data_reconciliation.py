from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Iterable, Mapping

from cfo_platform.data_foundation import FinanceRecord


class ReconciliationStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ReconciliationRule:
    rule_id: str
    account: str | None = None
    company: str | None = None
    period: str | None = None
    scenario: str | None = None
    expected_total: Decimal = Decimal("0")
    absolute_tolerance: Decimal = Decimal("0.01")
    blocking: bool = True

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id must not be empty")
        if self.absolute_tolerance < 0:
            raise ValueError("absolute_tolerance must not be negative")


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    rule_id: str
    actual_total: Decimal
    expected_total: Decimal
    variance: Decimal
    status: ReconciliationStatus
    blocking: bool

    @property
    def passed(self) -> bool:
        return self.status == ReconciliationStatus.PASSED


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    results: tuple[ReconciliationResult, ...]

    @property
    def blocking(self) -> bool:
        return any(item.blocking and not item.passed for item in self.results)

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.results)


class FinanceReconciliationService:
    def reconcile(
        self,
        records: Iterable[FinanceRecord],
        rules: Iterable[ReconciliationRule],
    ) -> ReconciliationReport:
        materialized = tuple(records)
        results: list[ReconciliationResult] = []
        for rule in rules:
            total = sum(
                (
                    record.value
                    for record in materialized
                    if self._matches(record, rule)
                ),
                Decimal("0"),
            )
            variance = total - rule.expected_total
            if abs(variance) <= rule.absolute_tolerance:
                status = ReconciliationStatus.PASSED
            elif rule.blocking:
                status = ReconciliationStatus.FAILED
            else:
                status = ReconciliationStatus.WARNING
            results.append(
                ReconciliationResult(
                    rule_id=rule.rule_id,
                    actual_total=total,
                    expected_total=rule.expected_total,
                    variance=variance,
                    status=status,
                    blocking=rule.blocking,
                )
            )
        return ReconciliationReport(results=tuple(results))

    @staticmethod
    def aggregate_by_account_period(
        records: Iterable[FinanceRecord],
    ) -> Mapping[tuple[str, str, str], Decimal]:
        totals: dict[tuple[str, str, str], Decimal] = {}
        for record in records:
            key = (record.company, record.account, record.period)
            totals[key] = totals.get(key, Decimal("0")) + record.value
        return totals

    @staticmethod
    def _matches(record: FinanceRecord, rule: ReconciliationRule) -> bool:
        return (
            (rule.account is None or record.account == rule.account)
            and (rule.company is None or record.company == rule.company)
            and (rule.period is None or record.period == rule.period)
            and (rule.scenario is None or record.scenario == rule.scenario)
        )
