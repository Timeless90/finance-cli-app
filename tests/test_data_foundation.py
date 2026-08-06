from decimal import Decimal

from cfo_platform.data_foundation import (
    CanonicalCsvImporter,
    DataSnapshotFactory,
    FinanceDataQualityService,
)


def test_csv_import_quality_and_snapshot_are_deterministic() -> None:
    content = (
        "company,account,period,scenario,value,currency,dim_cost_center\n"
        "DE01,4000,2026-01,actual,100.00,eur,CC100\n"
        "DE01,5000,2026-01,actual,-40.00,eur,CC100\n"
    )
    importer = CanonicalCsvImporter()
    records = importer.load_text(content)

    assert records[0].value == Decimal("100.00")
    assert records[0].currency == "EUR"
    assert records[0].dimensions == (("cost_center", "CC100"),)

    report = FinanceDataQualityService().validate(records)
    assert report.blocking is False
    assert report.score == 100.0

    factory = DataSnapshotFactory()
    first = factory.create(records)
    second = factory.create(reversed(records))

    assert first.snapshot_id == second.snapshot_id
    assert first.content_hash == second.content_hash
    assert first.row_count == 2


def test_duplicate_canonical_record_is_blocking() -> None:
    content = (
        "company,account,period,scenario,value,currency\n"
        "DE01,4000,2026-01,actual,100.00,EUR\n"
        "DE01,4000,2026-01,actual,120.00,EUR\n"
    )
    records = CanonicalCsvImporter().load_text(content)

    report = FinanceDataQualityService().validate(records)

    assert report.blocking is True
    assert {finding.code for finding in report.findings} == {"duplicate_record"}
