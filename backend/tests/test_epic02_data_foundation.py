from __future__ import annotations

import base64
import io
from decimal import Decimal

from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.data.data_foundation import CanonicalExcelImporter, FinanceRecord
from app.data.data_reconciliation import (
    FinanceReconciliationService,
    ReconciliationRule,
)
from app.data.data_semantics import (
    AccountMapping,
    FinanceSemanticService,
    SemanticModel,
)
from app.data.data_store import InMemoryDataSnapshotRepository
from app.data.data_workflow import FinanceDataWorkflow, FinanceImportCommand
from app.factory import create_app
from app.shared.composition import build_container
from app.shared.config import ApiSettings


def _csv() -> bytes:
    return (
        b"company,account,period,scenario,value,currency,dim_cost_center\n"
        b"DE01,4000,2026-01,actual,100.00,EUR,CC100\n"
        b"DE01,5000,2026-01,actual,-40.00,EUR,CC100\n"
    )


def test_excel_ingestion_matches_canonical_contract() -> None:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(["company", "account", "period", "scenario", "value", "currency"])
    sheet.append(["DE01", "4000", "2026-01", "actual", 100, "EUR"])
    buffer = io.BytesIO()
    workbook.save(buffer)

    records = CanonicalExcelImporter().load(buffer.getvalue())

    assert len(records) == 1
    assert records[0].value == Decimal(100)
    assert records[0].currency == "EUR"


def test_semantic_mapping_normalizes_accounts_and_signs() -> None:
    record = FinanceRecord("DE01", "REV", "2026-01", "actual", Decimal(100), "EUR")
    model = SemanticModel(
        version="1.0",
        account_mappings=(AccountMapping("REV", "4000", "revenue", Decimal(-1)),),
    )

    result = FinanceSemanticService().apply((record,), model)

    assert result.complete is True
    assert result.records[0].account == "4000"
    assert result.records[0].value == Decimal(-100)


def test_reconciliation_blocks_variance_outside_tolerance() -> None:
    records = (FinanceRecord("DE01", "4000", "2026-01", "actual", Decimal(100), "EUR"),)
    report = FinanceReconciliationService().reconcile(
        records,
        (
            ReconciliationRule(
                rule_id="trial-balance",
                expected_total=Decimal(0),
                absolute_tolerance=Decimal("0.01"),
                blocking=True,
            ),
        ),
    )

    assert report.blocking is True
    assert report.results[0].variance == Decimal(100)


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
                    expected_total=Decimal(60),
                    absolute_tolerance=Decimal(0),
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
                    expected_total=Decimal(0),
                    absolute_tolerance=Decimal(0),
                ),
            ),
        )
    )

    assert rejected.run_eligible is False
    assert rejected.snapshot is None


def test_data_api_import_and_snapshot_lookup() -> None:
    container = build_container()
    settings = ApiSettings(environment="test", build_version="test")
    headers = {"X-User": "preparer", "X-Roles": "fp_and_a", "X-Companies": "DE01"}
    with TestClient(create_app(settings, container)) as client:
        response = client.post(
            "/api/v1/data/imports",
            headers=headers,
            json={
                "content_base64": base64.b64encode(_csv()).decode(),
                "file_name": "trial-balance.csv",
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
        assert payload["status"] == "draft"

        lookup = client.get(f"/api/v1/data/snapshots/{snapshot_id}", headers=headers)
        assert lookup.status_code == 200
        assert lookup.json()["row_count"] == 2


def test_data_import_requires_review_approval_and_publish_before_workspace_is_visible() -> (
    None
):
    container = build_container()
    settings = ApiSettings(environment="test", build_version="test")
    preparer = {"X-User": "preparer", "X-Roles": "fp_and_a", "X-Companies": "DE01"}
    reviewer = {"X-User": "controller", "X-Roles": "controller", "X-Companies": "DE01"}
    approver = {"X-User": "cfo", "X-Roles": "cfo", "X-Companies": "DE01"}
    with TestClient(create_app(settings, container)) as client:
        created = client.post(
            "/api/v1/data/imports",
            headers=preparer,
            json={
                "content_base64": base64.b64encode(_csv()).decode(),
                "file_name": "actuals.csv",
                "file_type": "csv",
                "allowed_currencies": ["EUR"],
                "required_dimensions": ["cost_center"],
                "reconciliation_rules": [
                    {
                        "rule_id": "total",
                        "expected_total": "60",
                        "absolute_tolerance": "0",
                    }
                ],
            },
        )
        assert created.status_code == 201, created.text
        import_id = created.json()["import_id"]
        assert (
            client.post(
                f"/api/v1/data/imports/{import_id}/review", headers=preparer, json={}
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/v1/data/imports/{import_id}/review",
                headers=reviewer,
                json={"note": "reconciled"},
            ).status_code
            == 200
        )
        assert (
            client.post(
                f"/api/v1/data/imports/{import_id}/approve",
                headers=approver,
                json={"note": "approved"},
            ).status_code
            == 200
        )
        published = client.post(
            f"/api/v1/data/imports/{import_id}/publish", headers=approver
        )
        assert published.status_code == 200, published.text
        assert published.json()["status"] == "published"
        workspace = client.get(
            "/api/v1/planning/workspace?company_id=DE01&period_id=2026-01&scenario_id=actual",
            headers=preparer,
        )
        assert workspace.status_code == 200, workspace.text
        assert workspace.json()["source_snapshot_ids"] == [
            created.json()["snapshot_id"]
        ]


def test_planning_baseline_requires_a_reviewed_mapping_and_published_source() -> None:
    content = (
        b"company,account,period,scenario,value,currency,dim_cost_center\n"
        b"DE01,4000,2026-01,actual,100.00,EUR,CC100\n"
        b"DE01,5000,2026-01,actual,-40.00,EUR,CC100\n"
        b"DE01,6100,2026-01,actual,-60.00,EUR,CC100\n"
    )
    container = build_container()
    settings = ApiSettings(environment="test", build_version="test")
    preparer = {"X-User": "preparer", "X-Roles": "fp_and_a", "X-Companies": "DE01"}
    reviewer = {"X-User": "controller", "X-Roles": "controller", "X-Companies": "DE01"}
    approver = {"X-User": "cfo", "X-Roles": "cfo", "X-Companies": "DE01"}
    with TestClient(create_app(settings, container)) as client:
        created = client.post(
            "/api/v1/data/imports",
            headers=preparer,
            json={
                "content_base64": base64.b64encode(content).decode(),
                "file_name": "baseline.csv",
                "file_type": "csv",
                "allowed_currencies": ["EUR"],
                "required_dimensions": ["cost_center"],
                "reconciliation_rules": [
                    {
                        "rule_id": "total",
                        "expected_total": "0",
                        "absolute_tolerance": "0",
                    }
                ],
            },
        )
        assert created.status_code == 201, created.text
        import_id = created.json()["import_id"]
        snapshot_id = created.json()["snapshot_id"]
        assert (
            client.post(
                f"/api/v1/data/imports/{import_id}/review", headers=reviewer, json={}
            ).status_code
            == 200
        )
        assert (
            client.post(
                f"/api/v1/data/imports/{import_id}/approve", headers=approver, json={}
            ).status_code
            == 200
        )
        assert (
            client.post(
                f"/api/v1/data/imports/{import_id}/publish", headers=approver
            ).status_code
            == 200
        )

        accounts = client.get(
            f"/api/v1/data/imports/{import_id}/accounts", headers=preparer
        )
        assert accounts.status_code == 200, accounts.text
        assert accounts.json() == [
            {"account": "4000", "total": "100.00"},
            {"account": "5000", "total": "-40.00"},
            {"account": "6100", "total": "-60.00"},
        ]
        mapping = client.post(
            "/api/v1/data/planning-mappings",
            headers=preparer,
            json={
                "company_id": "DE01",
                "source_snapshot_id": snapshot_id,
                "version_label": "DE01 GL v1",
                "mappings": [
                    {
                        "source_account": "4000",
                        "category": "revenue",
                        "sign_multiplier": "1",
                    },
                    {
                        "source_account": "5000",
                        "category": "variable_cost",
                        "sign_multiplier": "-1",
                    },
                    {
                        "source_account": "6100",
                        "category": "fixed_operating_cost",
                        "sign_multiplier": "-1",
                    },
                ],
            },
        )
        assert mapping.status_code == 201, mapping.text
        mapping_id = mapping.json()["mapping_set_id"]
        assert (
            client.post(
                f"/api/v1/data/planning-mappings/{mapping_id}/review",
                headers=preparer,
                json={},
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/v1/data/planning-mappings/{mapping_id}/review",
                headers=reviewer,
                json={},
            ).status_code
            == 200
        )
        assert (
            client.post(
                f"/api/v1/data/planning-mappings/{mapping_id}/approve",
                headers=approver,
                json={},
            ).status_code
            == 200
        )

        baseline = client.post(
            "/api/v1/data/planning-baselines",
            headers=approver,
            json={
                "mapping_set_id": mapping_id,
                "period_id": "2026-01",
                "scenario_id": "actual",
            },
        )
        assert baseline.status_code == 201, baseline.text
        assert baseline.json()["forecast_eligible"] is True
        assert baseline.json()["values"] == {
            "accounts_payable": "0",
            "accounts_receivable": "0",
            "cash": "0",
            "debt": "0",
            "depreciation": "0",
            "fixed_operating_cost": "60.00",
            "inventory": "0",
            "other": "0",
            "personnel_cost": "0",
            "revenue": "100.00",
            "variable_cost": "40.00",
        }
