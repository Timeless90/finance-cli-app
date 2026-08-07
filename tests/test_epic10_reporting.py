from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.reporting_factory import (
    ExportFormat,
    InMemoryReportRepository,
    NarrativeStatement,
    ReportExporter,
    ReportingFactory,
    ReportSection,
    ReportStatus,
    ReportValue,
    TemplateRegistry,
    built_in_templates,
)


D = Decimal


def _value(key: str, value: str = "100") -> ReportValue:
    return ReportValue(
        key=key,
        value=D(value),
        unit="EUR",
        snapshot_id="snapshot-2026-07",
        run_id="run-approved-1",
        run_status="approved",
    )


def _section(section_id: str) -> ReportSection:
    return ReportSection(
        section_id=section_id,
        title=section_id.replace("-", " ").title(),
        values=(_value(f"{section_id}-metric"),),
        statements=(
            NarrativeStatement(
                text=f"Material statement for {section_id}.",
                source_refs=("run-approved-1", "snapshot-2026-07"),
            ),
        ),
    )


def _factory() -> ReportingFactory:
    return ReportingFactory(
        TemplateRegistry(built_in_templates()),
        InMemoryReportRepository(),
    )


def test_management_pack_uses_only_approved_values_and_has_stable_hash() -> None:
    factory = _factory()
    sections = tuple(_section(item) for item in ("kpi", "performance", "forecast", "cash"))
    first = factory.generate("management-pack", 1, sections)
    second = factory.generate("management-pack", 1, sections)

    assert first.status is ReportStatus.DRAFT
    assert first.content_hash == second.content_hash
    assert first.sections[0].values[0].value == D("100")
    assert first.sections[0].values[0].run_id == "run-approved-1"


def test_reporting_factory_rejects_unapproved_run_values() -> None:
    factory = _factory()
    invalid = ReportSection(
        section_id="kpi",
        title="KPI",
        values=(
            ReportValue(
                key="ebitda",
                value=D("100"),
                unit="EUR",
                snapshot_id="snapshot-1",
                run_id="run-draft",
                run_status="draft",
            ),
        ),
    )
    remaining = tuple(_section(item) for item in ("performance", "forecast", "cash"))

    with pytest.raises(ValueError, match="approved run"):
        factory.generate("management-pack", 1, (invalid, *remaining))


def test_material_statements_require_lineage() -> None:
    factory = _factory()
    invalid = ReportSection(
        section_id="kpi",
        title="KPI",
        values=(_value("ebitda"),),
        statements=(NarrativeStatement(text="EBITDA improved.", source_refs=()),),
    )
    remaining = tuple(_section(item) for item in ("performance", "forecast", "cash"))

    with pytest.raises(ValueError, match="source references"):
        factory.generate("management-pack", 1, (invalid, *remaining))


def test_external_lagebericht_requires_human_approval_before_export() -> None:
    factory = _factory()
    exporter = ReportExporter()
    sections = tuple(
        _section(item) for item in ("economic-report", "forecast", "opportunities", "risks")
    )
    report = factory.generate("lagebericht-draft", 1, sections)

    with pytest.raises(ValueError, match="human approval"):
        exporter.export(report, ExportFormat.PDF)

    approved = factory.approve(report.report_id, "CFO Reviewer")
    assert approved.status is ReportStatus.APPROVED
    assert approved.approval is not None
    assert approved.approval.approver == "CFO Reviewer"
    assert exporter.export(approved, ExportFormat.PDF).startswith(b"%PDF")


def test_all_required_export_formats_create_valid_artifacts() -> None:
    factory = _factory()
    exporter = ReportExporter()
    sections = tuple(_section(item) for item in ("kpi", "performance", "forecast", "cash"))
    report = factory.generate("management-pack", 1, sections)

    assert exporter.export(report, ExportFormat.JSON).lstrip().startswith(b"{")
    assert exporter.export(report, ExportFormat.CSV).startswith(b"section,key,value")
    assert exporter.export(report, ExportFormat.EXCEL).startswith(b"PK")
    assert exporter.export(report, ExportFormat.PDF).startswith(b"%PDF")
    assert exporter.export(report, ExportFormat.POWERPOINT).startswith(b"PK")


def test_reporting_api_generates_approves_and_exports_external_report() -> None:
    section_ids = ("economic-report", "forecast", "opportunities", "risks")
    sections = [
        {
            "section_id": section_id,
            "title": section_id,
            "values": [
                {
                    "key": f"{section_id}-metric",
                    "value": "100",
                    "unit": "EUR",
                    "snapshot_id": "snapshot-2026-07",
                    "run_id": "run-approved-1",
                    "run_status": "approved",
                }
            ],
            "statements": [
                {
                    "text": f"Statement {section_id}",
                    "source_refs": ["run-approved-1"],
                }
            ],
        }
        for section_id in section_ids
    ]

    with TestClient(create_app()) as client:
        templates = client.get("/api/v1/reporting/templates")
        assert templates.status_code == 200
        assert len(templates.json()["templates"]) == 5

        created = client.post(
            "/api/v1/reporting/reports",
            json={
                "template_id": "lagebericht-draft",
                "template_version": 1,
                "sections": sections,
            },
        )
        assert created.status_code == 200
        report_id = created.json()["report"]["report_id"]

        blocked = client.get(f"/api/v1/reporting/reports/{report_id}/export/pdf")
        assert blocked.status_code == 409
        assert "human approval" in blocked.json()["detail"]

        approved = client.post(
            f"/api/v1/reporting/reports/{report_id}/approve",
            json={"approver": "Board Reviewer"},
        )
        assert approved.status_code == 200
        assert approved.json()["report"]["status"] == "approved"

        exported = client.get(f"/api/v1/reporting/reports/{report_id}/export/pdf")
        assert exported.status_code == 200
        assert exported.content.startswith(b"%PDF")
