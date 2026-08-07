# Epic 12 – Market & Treasury Risk

## Scope

Epic 12 implements the roadmap capability for FX, interest-rate, commodity and funding risk management. The implementation is intentionally model-governed: advanced statistical overlays are available only when their diagnostics demonstrate measurable value over simpler baselines.

## Delivered capabilities

- Exposure aggregation by risk factor with gross long, gross short, net and delta-equivalent views.
- Parallel sensitivity shocks for market factors.
- Historical and Student-t Value-at-Risk and Expected Shortfall.
- Student-t GARCH(1,1) volatility model with stationarity checks and BIC activation gate.
- Two-state Gaussian Hidden Markov regime overlay with BIC, state-separation and persistence gates.
- Peaks-over-threshold Generalized Pareto EVT overlay with explicit threshold and minimum-exceedance diagnostics.
- Gaussian versus Student-t copula comparison using AIC and tail-dependence diagnostics.
- Hedge-ratio and variance-reduction effectiveness analytics.
- Kupiec unconditional-coverage and Christoffersen independence backtests.
- Versioned FastAPI endpoints under `/api/v1/market-risk`.

## Statistical design decisions

### GARCH-t

The GARCH model is constrained to positive variance and alpha + beta < 0.999. It is not considered active merely because the optimizer converges. The fitted model must improve BIC over a static-volatility Student-t baseline.

### Hidden Markov regime model

The regime overlay uses two zero-mean Gaussian states with different conditional variances. It is activated only when all of the following hold:

1. BIC improves over the single-state Gaussian baseline.
2. The high-volatility state variance is at least 1.5 times the low-volatility state variance.
3. Both states show minimum transition persistence of 60 percent.

This prevents unstable or weakly identified regimes from entering decision workflows.

### EVT

The tail overlay follows peaks-over-threshold logic. The threshold is explicit and configurable. At least 30 exceedances are required, the GPD scale must be positive, and the fitted shape must remain below one so the modeled mean tail loss is finite.

### Copulas

Both Gaussian and Student-t dependence models are estimated from rank-based pseudo-observations. The Student-t copula is selected only if it improves AIC materially and produces non-trivial tail dependence. Otherwise the simpler Gaussian dependence model remains the default.

### VaR backtesting

VaR validation includes:

- Kupiec likelihood-ratio test for unconditional exception coverage.
- Christoffersen likelihood-ratio test for independence of exceptions.

Both p-values and pass/fail flags are returned rather than reducing validation to a single opaque status.

## API surface

- `POST /api/v1/market-risk/exposures/aggregate`
- `POST /api/v1/market-risk/sensitivities`
- `POST /api/v1/market-risk/var-es`
- `POST /api/v1/market-risk/models/garch-t`
- `POST /api/v1/market-risk/models/regime-hmm`
- `POST /api/v1/market-risk/models/evt`
- `POST /api/v1/market-risk/models/copula`
- `POST /api/v1/market-risk/hedges/effectiveness`
- `POST /api/v1/market-risk/backtests/var`

## Acceptance evidence

| Acceptance criterion | Evidence |
| --- | --- |
| Risk models are reproducible and documented | deterministic services, explicit parameters and this document |
| GARCH is activated only with demonstrated value | BIC gate versus static-volatility baseline |
| HMM is activated only with demonstrated value | BIC, variance-separation and persistence gates |
| Tail overlay is statistically controlled | POT-GPD threshold and exceedance checks |
| Dependence model addresses tail risk | Student-t copula selected only with AIC improvement and tail dependence |
| VaR models are validated | Kupiec and Christoffersen backtests |
| Hedge decisions are quantitatively measurable | optimal ratio and variance-reduction effectiveness |
| Existing application behavior is preserved | regression suite plus Epic 12 tests in CI |

## Research rationale

The implementation follows established risk-model practice that treats model selection and backtesting as part of the model, not as optional reporting. Published copula research shows that Gaussian dependence can understate joint downside risk relative to Student-t dependence, while EVT literature emphasizes threshold selection as a core modeling choice. Recent regime-model research also reinforces the need for out-of-sample validation and explicit anti-look-ahead design. The production architecture therefore exposes advanced models as governed overlays instead of unconditional defaults.
