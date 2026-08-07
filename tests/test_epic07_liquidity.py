from decimal import Decimal

from fastapi.testclient import TestClient

from cfo_platform.api.app import create_app
from cfo_platform.liquidity_management import (
    CashAccuracyObservation,
    CashForecastAccuracyService,
    CovenantDefinition,
    CovenantDirection,
    CovenantEngine,
    DebtInstrument,
    DebtScheduleEngine,
    LiquidityStressEngine,
    LiquidityStressScenario,
    MonthlyLiquidityForecast,
    MonthlyLiquidityInput,
    ThirteenWeekCashForecast,
    WeeklyCashFlow,
    WorkingCapitalAssumptions,
    WorkingCapitalModel,
)


D = Decimal


def _weekly_flows() -> tuple[WeeklyCashFlow, ...]:
    flows: list[WeeklyCashFlow] = []
    opening = D("100")
    for week in range(1, 14):
        flow = WeeklyCashFlow(
            week=week,
            bank_opening=opening,
            ar_collections=D("20"),
            ap_payments=D("10"),
            payroll=D("3"),
            taxes=D("2"),
            capex=D("1"),
        )
        flows.append(flow)
        opening += D("4")
    return tuple(flows)


def test_13_week_cash_forecast_reconciles_bank_opening_and_closing() -> None:
    result = ThirteenWeekCashForecast().forecast(_weekly_flows())
    assert len(result) == 13
    assert result[0].closing_cash == D("104")
    assert result[-1].closing_cash == D("152")
    for prior, current in zip(result[:-1], result[1:], strict=True):
        assert current.opening_cash == prior.closing_cash


def test_monthly_liquidity_calculates_headroom_and_funding_gap() -> None:
    periods: list[MonthlyLiquidityInput] = []
    opening = D("50")
    for month in range(1, 13):
        periods.append(
            MonthlyLiquidityInput(
                month=month,
                opening_cash=opening,
                operating_cash_flow=D("5"),
                investing_cash_flow=D("-2"),
                financing_cash_flow=D("0"),
                minimum_liquidity=D("40"),
            )
        )
        opening += D("3")
    result = MonthlyLiquidityForecast().forecast(tuple(periods))
    assert result[0].closing_cash == D("53")
    assert result[0].headroom == D("13")
    assert result[0].funding_gap == D("0")


def test_working_capital_matches_dso_dpo_dio_formulae() -> None:
    position = WorkingCapitalModel().calculate(
        WorkingCapitalAssumptions(
            annual_revenue=D("3650"),
            annual_cogs=D("1825"),
            dso=D("30"),
            dpo=D("40"),
            dio=D("50"),
        )
    )
    assert position.receivables == D("300")
    assert position.payables == D("200")
    assert position.inventory == D("250")
    assert position.net_working_capital == D("350")


def test_debt_schedule_calculates_interest_and_maturity_repayment() -> None:
    instrument = DebtInstrument(
        instrument_id="TL-1",
        opening_principal=D("1200"),
        annual_interest_rate=D("0.12"),
        monthly_amortization=D("100"),
        maturity_month=6,
    )
    schedule = DebtScheduleEngine().schedule(instrument, 6)
    assert schedule[0].interest == D("12")
    assert schedule[0].closing_principal == D("1100")
    assert schedule[-1].closing_principal == D("0")


def test_covenant_contract_examples_and_breach_probability() -> None:
    engine = CovenantEngine()
    leverage = engine.leverage_ratio(D("300"), D("100"))
    cover = engine.interest_cover(D("120"), D("30"))
    assert leverage == D("3")
    assert cover == D("4")

    result = engine.evaluate(
        CovenantDefinition(
            covenant_id="LEV",
            metric="net_debt_to_ebitda",
            threshold=D("3.5"),
            direction=CovenantDirection.MAXIMUM,
        ),
        actual=D("3"),
        simulated_values=(D("3"), D("3.6"), D("4"), D("2.5")),
    )
    assert result.headroom == D("0.5")
    assert result.breached is False
    assert result.breach_probability == D("0.5")


def test_liquidity_stress_includes_mitigation_and_funding_gap() -> None:
    result = LiquidityStressEngine().apply(
        base_cash=D("100"),
        baseline_revenue_cash=D("200"),
        baseline_cost_cash=D("150"),
        minimum_liquidity=D("50"),
        scenario=LiquidityStressScenario(
            name="downside",
            revenue_change_pct=D("-0.20"),
            collection_delay_pct=D("0.10"),
            cost_change_pct=D("0.10"),
            refinancing_shock=D("20"),
            mitigation_cash=D("30"),
        ),
    )
    assert result.stressed_cash == D("35")
    assert result.funding_gap == D("15")


def test_cash_forecast_accuracy_is_sliced_by_horizon() -> None:
    result = CashForecastAccuracyService().summarize(
        (
            CashAccuracyObservation(horizon=1, actual=D("100"), forecast=D("110")),
            CashAccuracyObservation(horizon=1, actual=D("100"), forecast=D("90")),
            CashAccuracyObservation(horizon=4, actual=D("100"), forecast=D("120")),
        )
    )
    assert result[0].horizon == 1
    assert result[0].mae == D("10")
    assert result[0].bias == D("0")
    assert result[1].horizon == 4
    assert result[1].mae == D("20")


def test_liquidity_api_exposes_covenant_and_working_capital_contracts() -> None:
    with TestClient(create_app()) as client:
        covenant = client.post(
            "/api/v1/liquidity/covenants/evaluate",
            json={
                "covenant_id": "ICR",
                "metric": "interest_cover",
                "threshold": "2.0",
                "direction": "minimum",
                "actual": "2.5",
                "simulated_values": ["2.5", "1.8"],
            },
        )
        assert covenant.status_code == 200
        assert covenant.json()["result"]["breach_probability"] == "0.5"

        wc = client.post(
            "/api/v1/liquidity/working-capital",
            json={
                "annual_revenue": "3650",
                "annual_cogs": "1825",
                "dso": "30",
                "dpo": "40",
                "dio": "50",
            },
        )
        assert wc.status_code == 200
        assert wc.json()["position"]["net_working_capital"] == "350"
