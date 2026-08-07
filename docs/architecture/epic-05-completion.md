# Epic 05 Completion — Financial Performance Management

## Scope

Epic 05 implements the performance-management layer defined by the CFO product roadmap. It converts plan, forecast and actual values into reproducible KPI calculations, fully explained variance bridges, forecast-accuracy slices, anomaly signals and governed management-commentary requirements.

## Delivered capabilities

### KPI tree

- Hierarchical KPI calculation from revenue through EBITDA, EBIT and NOPAT.
- Free-cash-flow calculation from operating cash flow and capex.
- Explicit additive and subtractive child relationships.
- Cycle and missing-leaf validation.
- Drilldown-compatible dimension key for entity, segment, product and cost center.

### Variance analysis

- Plan-versus-actual, forecast-versus-actual and forecast-versus-forecast comparisons.
- Reproducible bridge contributions with source snapshot IDs.
- Price-volume-mix decomposition including interaction effect.
- Hard validation that explained variance equals reported variance exactly.

### Forecast accuracy

- MAE, WAPE and bias.
- Slicing by KPI, business unit, horizon and model.
- Deterministic grouping and output order.

### Anomaly detection

- Robust median/MAD z-score signals.
- Lower- and upper-bound rules.
- Combined statistical and rule-based evidence.
- Dimension-aware output.

### Management commentary

- Materiality-driven commentary requirement.
- Commentary ownership and action references.
- Validation that commentary belongs to the evaluated KPI and period.

### API

- `POST /api/v1/performance/kpi-tree/evaluate`
- `POST /api/v1/performance/variance-bridges`
- `POST /api/v1/performance/forecast-accuracy`
- `POST /api/v1/performance/anomalies`
- `POST /api/v1/performance/commentary/requirements`

## Acceptance criteria evidence

| Criterion | Evidence |
|---|---|
| Variance bridges explain 100 percent of reported variance | `VarianceBridge.assert_fully_explained` rejects every non-zero unexplained remainder. |
| Every contribution is reproducible | Each contribution stores a driver, amount and immutable source snapshot ID. |
| KPI drilldown supports key management dimensions | `DimensionKey` carries entity, segment, product and cost center. |
| Forecast accuracy is visible by KPI, unit, horizon and model | `ForecastAccuracyService.summarize` groups by the full four-part slice. |
| Material deviations require management commentary | `ManagementCommentaryService` applies an explicit materiality threshold. |
| API contracts are versioned and tested | Routes are registered under `/api/v1/performance`; tests exercise bridge and commentary endpoints. |

## Test coverage

`tests/test_epic05_performance.py` covers:

- EBITDA, EBIT and free-cash-flow KPI calculations.
- Complete price-volume-mix bridge reconciliation.
- Rejection of incomplete variance bridges.
- Forecast-accuracy slicing and metrics.
- Statistical and rule-based anomaly detection.
- Commentary materiality rules.
- FastAPI contracts.

## Dependency and merge strategy

The branch is stacked on `feature/epic-04-integrated-planning-rolling-forecast`. After Epic 04 is merged, this pull request can be retargeted to `main` without changing the Epic 05 implementation diff.
