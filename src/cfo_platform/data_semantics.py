from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Iterable, Mapping

from cfo_platform.data_foundation import FinanceRecord


class AggregationMethod(StrEnum):
    SUM = "sum"
    AVERAGE = "average"
    LAST = "last"


@dataclass(frozen=True, slots=True)
class AccountMapping:
    source_account: str
    canonical_account: str
    metric_code: str
    sign_multiplier: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if not self.source_account.strip() or not self.canonical_account.strip():
            raise ValueError("account mapping codes must not be empty")
        if not self.metric_code.strip():
            raise ValueError("metric_code must not be empty")
        if self.sign_multiplier not in {Decimal("1"), Decimal("-1")}:
            raise ValueError("sign_multiplier must be 1 or -1")


@dataclass(frozen=True, slots=True)
class KpiDefinition:
    code: str
    name: str
    account_codes: tuple[str, ...]
    aggregation: AggregationMethod = AggregationMethod.SUM

    def __post_init__(self) -> None:
        if not self.code.strip() or not self.name.strip():
            raise ValueError("KPI code and name must not be empty")
        if not self.account_codes:
            raise ValueError("KPI must reference at least one account")


@dataclass(frozen=True, slots=True)
class SemanticModel:
    version: str
    account_mappings: tuple[AccountMapping, ...]
    kpis: tuple[KpiDefinition, ...] = ()

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("semantic model version must not be empty")
        sources = [item.source_account for item in self.account_mappings]
        if len(sources) != len(set(sources)):
            raise ValueError("source accounts must be unique within a semantic model")

    def mapping_index(self) -> Mapping[str, AccountMapping]:
        return {item.source_account: item for item in self.account_mappings}


@dataclass(frozen=True, slots=True)
class SemanticMappingResult:
    records: tuple[FinanceRecord, ...]
    unmapped_accounts: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.unmapped_accounts


class FinanceSemanticService:
    def apply(
        self,
        records: Iterable[FinanceRecord],
        model: SemanticModel,
        *,
        allow_unmapped: bool = False,
    ) -> SemanticMappingResult:
        index = model.mapping_index()
        mapped: list[FinanceRecord] = []
        unmapped: set[str] = set()
        for record in records:
            mapping = index.get(record.account)
            if mapping is None:
                unmapped.add(record.account)
                if allow_unmapped:
                    mapped.append(record)
                continue
            mapped.append(
                FinanceRecord(
                    company=record.company,
                    account=mapping.canonical_account,
                    period=record.period,
                    scenario=record.scenario,
                    value=record.value * mapping.sign_multiplier,
                    currency=record.currency,
                    dimensions=record.dimensions,
                    source_row=record.source_row,
                )
            )
        return SemanticMappingResult(
            records=tuple(mapped),
            unmapped_accounts=tuple(sorted(unmapped)),
        )
