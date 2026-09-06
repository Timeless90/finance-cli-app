from __future__ import annotations

import pandas as pd

from finance_cli.data import to_monthly_returns


def test_monthly_returns_are_calculated() -> None:
    prices = pd.Series(
        [100.0, 105.0, 103.0, 110.0],
        index=pd.to_datetime(
            ["2025-01-31", "2025-02-28", "2025-03-31", "2025-04-30"], utc=True
        ),
    )
    result = to_monthly_returns(prices)
    assert len(result.simple_returns) == 3
    assert len(result.log_returns) == 3
