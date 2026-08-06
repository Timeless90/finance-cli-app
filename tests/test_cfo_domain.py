from decimal import Decimal

import pytest

from cfo_platform.domain import (
    Company,
    CurrencyCode,
    DimensionMember,
    FiscalPeriod,
    MetricObservation,
    Money,
    VersionId,
)


def test_money_rejects_cross_currency_arithmetic() -> None:
    eur = Money(Decimal("10"), CurrencyCode("eur"))
    usd = Money(Decimal("5"), CurrencyCode("USD"))

    with pytest.raises(ValueError, match="matching currencies"):
        _ = eur + usd


def test_fiscal_period_round_trip() -> None:
    period = FiscalPeriod.parse("2027-03")

    assert period.year == 2027
    assert period.month == 3
    assert str(period) == "2027-03"


def test_metric_observation_rejects_duplicate_dimension_members() -> None:
    company = Company("DE01", "Example GmbH", CurrencyCode("EUR"))
    member = DimensionMember("cost_center", "CC100", "Sales")

    with pytest.raises(ValueError, match="duplicate dimension"):
        MetricObservation(
            company_id=company.id,
            metric_code="revenue",
            period=FiscalPeriod(2027, 1),
            scenario_code="forecast",
            version=VersionId("v1"),
            value=Decimal("1000000"),
            currency=CurrencyCode("EUR"),
            dimensions=(member, member),
            source="erp",
        )
