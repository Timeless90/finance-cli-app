# Phase 2 Research and Implementation Decisions

## Scope

Phase 2 adds model validation, risk reporting, stress and sensitivity analysis, a simplified German tax view, interactive configuration, and chart export. Advanced GARCH, regime-switching, EVT, copula, and multi-asset work remains outside this branch.

## Statistical validation

### Rolling-origin backtesting

The implementation uses one-step-ahead rolling-origin evaluation. Each forecast is calibrated only from observations available before the forecast origin. Coverage diagnostics report nominal coverage, observed coverage, average interval width, and the number of out-of-sample observations for normal and Student-t predictive intervals.

This is intentionally pseudo-out-of-sample. It avoids look-ahead bias and makes interval calibration failures visible. The initial implementation uses a fixed training window; expanding windows and conditional-coverage tests are follow-up extensions.

### Goodness of fit

Normal and Student-t distributions are fitted by maximum likelihood. Model comparison reports:

- log likelihood,
- Akaike information criterion,
- Bayesian information criterion,
- Anderson-Darling Monte Carlo goodness-of-fit statistic and p-value.

A plain analytical KS or Cramer-von Mises p-value is not used after estimating distribution parameters from the same data. SciPy explicitly notes that simple-hypothesis p-values are unreliable for this composite-hypothesis setting. Parametric Monte Carlo refits the model to every null sample and therefore matches the implemented calibration workflow.

## Risk metrics

Metrics are calculated from monthly simulated returns rather than portfolio values with cash contributions. This prevents savings flows from being misclassified as investment performance.

The following path-level metrics are produced and summarized by P5, median, and P95:

- annualized geometric return,
- annualized volatility,
- Sharpe ratio,
- Sortino ratio,
- Omega ratio,
- maximum drawdown,
- Ulcer Index,
- monthly Value at Risk,
- monthly Expected Shortfall.

Expected Shortfall is calculated as the average loss at or beyond the path-specific VaR threshold. It is reported together with VaR because the two measures describe different aspects of tail risk.

## Stress and sensitivity

The stress module provides reusable scenarios combining an immediate market shock, a long-run return shift, and a volatility multiplier. The first CLI sensitivity grid uses deterministic future-value calculations over return and inflation assumptions. This keeps the output explainable and allows a user to distinguish parameter sensitivity from Monte Carlo sampling noise.

## Simplified German tax policy

The tax module is an analytical approximation, not a tax engine. It applies tax only to terminal unrealized gains and includes configurable:

- partial exemption,
- saver allowance,
- capital gains tax,
- solidarity surcharge,
- optional church tax.

The default equity-fund partial exemption is 30%, consistent with Section 20 of the German Investment Tax Act for qualifying equity funds. The implementation does not model annual distributions, loss pots, acquisition lots, Vorabpauschale, changes in tax law, withholding timing, or personal assessment effects. Outputs are explicitly labelled as simplified terminal-gain taxation.

## User experience and outputs

New commands:

- `finance-cli diagnose --config ...`
- `finance-cli backtest --config ...`
- `finance-cli sensitivity --config ...`
- `finance-cli wizard --output ...`

A normal simulation run additionally writes:

- `risk-summary.csv`,
- `tax-summary.json`,
- `distribution-fit.csv` when historical data exists,
- `coverage-backtest.csv` when enough history exists,
- `percentile-paths.png` when chart export is enabled.

## Validation strategy

Unit tests cover:

- drawdown and tail ordering,
- normal versus Student-t fit output,
- rolling-origin coverage bounds,
- partial exemption and allowance behavior,
- sensitivity-grid completeness.

CI continues to run Ruff, mypy, and pytest on Python 3.11 and 3.12.

## Follow-up work

The next statistical increments should be conditional coverage tests, bootstrap confidence intervals for performance ratios, stress scenario configuration in JSON, and rolling sensitivity across multiple historical windows. Advanced stochastic-volatility and multi-asset models remain in the Advanced roadmap.
