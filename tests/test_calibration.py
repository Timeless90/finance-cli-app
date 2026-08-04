from __future__ import annotations

import numpy as np

from finance_cli.calibration import calibrate


def test_shrunk_mean_is_between_historical_and_assumed() -> None:
    simple = np.array([0.01] * 24)
    log = np.log1p(simple)
    result = calibrate(
        simple,
        log,
        assumed_annual_return=0.06,
        mean_shrinkage_months=60,
    )
    lower = min(result.monthly_log_mean_historical, result.monthly_log_mean_assumed)
    upper = max(result.monthly_log_mean_historical, result.monthly_log_mean_assumed)
    assert lower <= result.monthly_log_mean_shrunk <= upper
