from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from cfo_platform.data_foundation import (
    CanonicalCsvImporter,
    CanonicalExcelImporter,
    DataQualityReport,
    DataSnapshot,
    DataSnapshotFactory,
    FinanceDataQualityService,
    FinanceRecord,
)
from cfo_platform.data_reconciliation import (
    FinanceReconciliationService,
    ReconciliationReport,
    ReconciliationRule,
)
from cfo_platform.data_semantics import FinanceSemanticService, SemanticModel
from cfo_platform.data_store import DataSnapshotRepository


@dataclass(frozen=True, slots=True)
class FinanceImportCommand:
    content: bytes
    file_type: str
    column_mapping: Mapping[str, str] | None = None
    semantic_model: SemanticModel | None = None
    reconciliation_rules: tuple[ReconciliationRule, ...] = ()
    allowed_currencies: set[str] | None = None
    required_dimensions: set[str] | None = None
    sheet_name: str | None = None


@dataclass(frozen=True, slots=True)
class FinanceImportResult:
    records: tuple[FinanceRecord, ...]
    quality_report: DataQualityReport
    reconciliation_report: ReconciliationReport
    snapshot: DataSnapshot | None
    unmapped_accounts: tuple[str, ...] = ()

    @property
    def run_eligible(self) -> bool:
        return (
            not self.quality_report.blocking
            and not self.reconciliation_report.blocking
            and not self.unmapped_accounts
            and self.snapshot is not None
        )


class FinanceDataWorkflow:
    def __init__(self, snapshot_repository: DataSnapshotRepository) -> None:
        self._snapshot_repository = snapshot_repository
        self._csv = CanonicalCsvImporter()
        self._excel = CanonicalExcelImporter()
        self._quality = FinanceDataQualityService()
        self._semantics = FinanceSemanticService()
        self._reconciliation = FinanceReconciliationService()
        self._snapshots = DataSnapshotFactory()

    def execute(self, command: FinanceImportCommand) -> FinanceImportResult:
        records = self._load(command)
        unmapped: tuple[str, ...] = ()
        if command.semantic_model is not None:
            mapped = self._semantics.apply(records, command.semantic_model)
            records = mapped.records
            unmapped = mapped.unmapped_accounts
        quality = self._quality.validate(
            records,
            allowed_currencies=command.allowed_currencies,
            required_dimensions=command.required_dimensions,
        )
        reconciliation = self._reconciliation.reconcile(
            records,
            command.reconciliation_rules,
        )
        snapshot: DataSnapshot | None = None
        if not quality.blocking and not reconciliation.blocking and not unmapped:
            snapshot = self._snapshots.create(records)
            self._snapshot_repository.save(snapshot)
        return FinanceImportResult(
            records=records,
            quality_report=quality,
            reconciliation_report=reconciliation,
            snapshot=snapshot,
            unmapped_accounts=unmapped,
        )

    def require_snapshot(self, snapshot_id: str) -> DataSnapshot:
        snapshot = self._snapshot_repository.get(snapshot_id)
        if snapshot is None:
            raise KeyError(f"Unknown data snapshot: {snapshot_id}")
        return snapshot

    def _load(self, command: FinanceImportCommand) -> tuple[FinanceRecord, ...]:
        normalized = command.file_type.lower().lstrip(".")
        if normalized == "csv":
            return self._csv.load(command.content, column_mapping=command.column_mapping)
        if normalized in {"xlsx", "xlsm"}:
            return self._excel.load(
                command.content,
                column_mapping=command.column_mapping,
                sheet_name=command.sheet_name,
            )
        raise ValueError(f"Unsupported finance import file type: {command.file_type}")
