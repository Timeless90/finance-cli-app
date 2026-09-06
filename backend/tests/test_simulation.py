from __future__ import annotations

import numpy as np

from finance_cli.models import ContributionTiming
from finance_cli.simulation import simulate_portfolio


def test_zero_return_matches_paid_in_capital() -> None:
    log_returns = np.zeros((100, 12))
    output = simulate_portfolio(
        log_returns,
        initial_value=1000.0,
        monthly_contribution=100.0,
        timing=ContributionTiming.MONTH_END,
        annual_inflation=0.0,
        annual_external_fee=0.0,
    )
    assert np.allclose(output.values[:, -1], 2200.0)
    assert output.paid_in[-1] == 2200.0
