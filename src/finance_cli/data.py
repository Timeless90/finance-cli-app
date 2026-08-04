from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ReturnSeries:
    monthly_prices: pd.Series
    simple_returns: pd.Series
    log_returns: pd.Series


def load_price_csv(path: Path, date_column: str, price_column: str) -> pd.Series:
    frame = pd.read_csv(path)
    missing = {date_column, price_column} - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required CSV columns: {sorted(missing)}")

    frame = frame[[date_column, price_column]].copy()
    frame[date_column] = pd.to_datetime(frame[date_column], errors="coerce", utc=True)
    frame[price_column] = pd.to_numeric(frame[price_column], errors="coerce")
    frame = frame.dropna().sort_values(date_column)
    frame = frame[frame[price_column] > 0]
    if frame.empty:
        raise ValueError("No valid positive price observations found")

    series = frame.set_index(date_column)[price_column]
    series = series[~series.index.duplicated(keep="last")]
    return series.astype(float)


def to_monthly_returns(prices: pd.Series) -> ReturnSeries:
    monthly = prices.resample("ME").last().dropna()
    if len(monthly) < 3:
        raise ValueError("At least three monthly price observations are required")
    simple = monthly.pct_change().dropna()
    log = np.log(monthly).diff().dropna()
    return ReturnSeries(monthly_prices=monthly, simple_returns=simple, log_returns=log)
