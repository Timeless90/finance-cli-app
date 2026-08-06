from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Iterable, Mapping


class FindingSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class FinanceRecord:
    company: str
    account: str
    period: str
    scenario: str
    value: Decimal
    currency: str
    dimensions: tuple[tuple[str, str], ...] = ()
    source_row: int | None = None

    def canonical_key(self) -> tuple[object, ...]:
        return (
            self.company,
            self.account,
            self.period,
            self.scenario,
            self.currency,
            self.dimensions,
        )


@dataclass(frozen=True, slots=True)
class DataQualityFinding:
    code: str
    severity: FindingSeverity
    message: str
    row_number: int | None = None


@dataclass(frozen=True, slots=True)
class DataQualityReport:
    row_count: int
    findings: tuple[DataQualityFinding, ...]

    @property
    def blocking(self) -> bool:
        return any(item.severity == FindingSeverity.ERROR for item in self.findings)

    @property
    def score(self) -> float:
        if self.row_count == 0:
            return 0.0
        penalty = sum(10 if item.severity == FindingSeverity.ERROR else 2 for item in self.findings)
        return max(0.0, round(100.0 - penalty / self.row_count, 2))


@dataclass(frozen=True, slots=True)
class DataSnapshot:
    snapshot_id: str
    content_hash: str
    row_count: int
    records: tuple[FinanceRecord, ...]


class CanonicalCsvImporter:
    REQUIRED_COLUMNS = {"company", "account", "period", "scenario", "value", "currency"}

    def load_text(
        self,
        content: str,
        *,
        column_mapping: Mapping[str, str] | None = None,
    ) -> tuple[FinanceRecord, ...]:
        mapping = dict(column_mapping or {})
        reader = csv.DictReader(io.StringIO(content))
        source_columns = set(reader.fieldnames or ())
        required_sources = {mapping.get(name, name) for name in self.REQUIRED_COLUMNS}
        missing = sorted(required_sources - source_columns)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        records: list[FinanceRecord] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                value = Decimal(row[mapping.get("value", "value")].strip())
            except (InvalidOperation, AttributeError) as exc:
                raise ValueError(f"Invalid decimal value at row {row_number}") from exc
            dimensions = tuple(
                sorted(
                    (key.removeprefix("dim_"), value.strip())
                    for key, value in row.items()
                    if key.startswith("dim_") and value and value.strip()
                )
            )
            records.append(
                FinanceRecord(
                    company=row[mapping.get("company", "company")].strip(),
                    account=row[mapping.get("account", "account")].strip(),
                    period=row[mapping.get("period", "period")].strip(),
                    scenario=row[mapping.get("scenario", "scenario")].strip(),
                    value=value,
                    currency=row[mapping.get("currency", "currency")].strip().upper(),
                    dimensions=dimensions,
                    source_row=row_number,
                )
            )
        return tuple(records)


class FinanceDataQualityService:
    def validate(self, records: Iterable[FinanceRecord]) -> DataQualityReport:
        materialized = tuple(records)
        findings: list[DataQualityFinding] = []
        seen: set[tuple[object, ...]] = set()
        for record in materialized:
            required = {
                "company": record.company,
                "account": record.account,
                "period": record.period,
                "scenario": record.scenario,
                "currency": record.currency,
            }
            for field, value in required.items():
                if not value:
                    findings.append(
                        DataQualityFinding(
                            code=f"missing_{field}",
                            severity=FindingSeverity.ERROR,
                            message=f"{field} must not be empty",
                            row_number=record.source_row,
                        )
                    )
            if len(record.period) != 7 or record.period[4:5] != "-":
                findings.append(
                    DataQualityFinding(
                        code="invalid_period",
                        severity=FindingSeverity.ERROR,
                        message="period must use YYYY-MM format",
                        row_number=record.source_row,
                    )
                )
            if len(record.currency) != 3 or not record.currency.isalpha():
                findings.append(
                    DataQualityFinding(
                        code="invalid_currency",
                        severity=FindingSeverity.ERROR,
                        message="currency must be a three-letter code",
                        row_number=record.source_row,
                    )
                )
            key = record.canonical_key()
            if key in seen:
                findings.append(
                    DataQualityFinding(
                        code="duplicate_record",
                        severity=FindingSeverity.ERROR,
                        message="duplicate canonical finance record",
                        row_number=record.source_row,
                    )
                )
            seen.add(key)
        return DataQualityReport(row_count=len(materialized), findings=tuple(findings))


class DataSnapshotFactory:
    def create(self, records: Iterable[FinanceRecord]) -> DataSnapshot:
        ordered = tuple(sorted(records, key=lambda item: item.canonical_key()))
        payload = [
            {
                **asdict(record),
                "value": format(record.value, "f"),
                "dimensions": list(record.dimensions),
                "source_row": None,
            }
            for record in ordered
        ]
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return DataSnapshot(
            snapshot_id=f"sha256:{digest}",
            content_hash=digest,
            row_count=len(ordered),
            records=ordered,
        )
