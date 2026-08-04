# Simulation Methodology

## Return representation

Historical prices are aggregated to the last available observation of each calendar month. Both simple and logarithmic returns are calculated. Portfolio wealth uses multiplicative returns; parametric models are calibrated in log-return space.

## Expected-return shrinkage

The historical mean is noisy. The model combines historical and assumed monthly log returns:

```text
w = n / (n + k)
mu = w * mu_historical + (1 - w) * mu_assumed
```

The historical volatility remains calibrated from the selected lookback window.

## Simulation methods

- Normal: transparent baseline.
- Student-t: heavier symmetric tails; preferred parametric MVP method.
- Historical bootstrap: preserves empirical marginal distribution.
- Moving-block bootstrap: preserves short local dependence and volatility clustering.

## Reproducibility

Every run records seed, NumPy version, Python version, model, path count, horizon, and resolved configuration.

## Interpretation

Results are distributions, not point forecasts. The median is not a guaranteed outcome. Tail percentiles and the probability of underperforming paid-in capital should always be reviewed alongside the median.
