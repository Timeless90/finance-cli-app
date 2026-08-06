from __future__ import annotations

import base64
import io
from decimal import Decimal

from fastapi.testclient import TestClient
from openpyxl import Workbook

from cfo_platform.api.app import create_app
from cfo_platform.api.settings import ApiSettings
from cfo_platform.composition import build_container
from cfo_platform.data_foundation import CanonicalExcelImporter, FinanceRecord
from cfo_platform.data_reconciliation import (
    FinanceReconciliationService,
    ReconciliationRule,
)
from cfo_platform.data_semantics import (
    AccountMapping,
    FinanceSemanticService,
    SemanticModel,
)
from cfo_platform.data_store import InMemoryDataSnapshotRepository
from cfo_platform.data_workflow import FinanceDataWorkflow, FinanceImportCommand


def _csv() -> bytes:
    return (
        "company,account,period,scenario,value,currency,dim_cost_center\n"
        "DE01,4000,2026-01,actual,100.00,EUR,CC100\n"
        "DE01,5000,2026-01,actual,-40.00,EUR,CC100\n"
    ).encode()


def test_excel_ingestion_matches_canonical_contract() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["company", "account", "period", "scenario", "value", "currency"])
    sheet.append(["DE01", "4000", "2026-01", "actual", 100, "EUR"])
    buffer = io.BytesIO()
    workbook.save(buffer)

    records = CanonicalExcelImporter().load(buffer.getvalue())

    assert len(records) == 1
    assert records[0].value == Decimal("100")
    assert records[0].currency == "EUR"


def test_semantic_mapping_normalizes_accounts_and_signs() -> None:
    record = FinanceRecord("DE01", "REV", "2026-01", "actual", Decimal("100"), "EUR")
    model = SemanticModel(
        version="1.0",
        account_mappings=(
            AccountMapping("REV", "4000", "revenue", Decimal("-1")),
        ),
    )

    result = FinanceSemanticService().apply((record,), model)

    assert result.complete is True
    assert result.records[0].account == "4000"
    assert result.records[0].value == Decimal("-100")


def test_reconciliation_blocks_variance_outside_tolerance() -> None:
    records = (
        FinanceRecord("DE01", "4000", "2026-01", "actual", Decimal("100"), "EUR"),
    )
    report = FinanceReconciliationService().reconcile(
        records,
        (
            ReconciliationRule(
                rule_id="trial-balance",
                expected_total=Decimal("0"),
                absolute_tolerance=Decimal("0.01"),
                blocking=True,
            ),
        ),
    )

    assert report.blocking is True
    assert report.results[0].variance == Decimal("100")


def test_workflow_only_persists_run_eligible_snapshots() -> None:
    repository = InMemoryDataSnapshotRepository()
    workflow = FinanceDataWorkflow(repository)

    accepted = workflow.execute(
        FinanceImportCommand(
            content=_csv(),
            file_type="csv",
            allowed_currencies={"EUR"},
            required_dimensions={"cost_center"},
            reconciliation_rules=(
                ReconciliationRule(
                    rule_id="total",
                    expected_total=Decimal("60"),
                    absolute_tolerance=Decimal("0"),
                ),
            ),
        )
    )

    assert accepted.run_eligible is True
    assert accepted.snapshot is not None
    assert repository.exists(accepted.snapshot.snapshot_id)

    rejected = workflow.execute(
        FinanceImportCommand(
            content=_csv(),
            file_type="csv",
            reconciliation_rules=(
                ReconciliationRule(
                    rule_id="wrong-total",
                    expected_total=Decimal("0"),
                    absolute_tolerance=Decimal("0"),
                ),
            ),
        )
    )

    assert rejected.run_eligible is False
    assert rejected.snapshot is None


def test_data_api_import_and_snapshot_lookup() -> None:
    container = build_container()
    settings = ApiSettings(environment="test", build_version="test")
    with TestClient(create_app(settings, container)) as client:
        response = client.post(
            "/api/v1/data/imports",
            json={
                "content_base64": base64.b64encode(_csv()).decode(),
                "file_type": "csv",
                "allowed_currencies": ["EUR"],
                "required_dimensions": ["cost_center"],
                "reconciliation_rules": [
                    {
                        "rule_id": "total",
                        "expected_total": "60",
                        "absolute_tolerance": "0",
                        "blocking": True,
                    }
                ],
            },
        )
        assert response.status_code == 201
        payload = response.json()
        assert payload["run_eligible"] is True
        snapshot_id = payload["snapshot_id"]

        lookup = client.get(f"/api/v1/data/snapshots/{snapshot_id}")
        assert lookup.status_code == 200
        assert lookup.json()["row_count"] == 2
