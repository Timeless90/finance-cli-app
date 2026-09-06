# Finance App Mock Data

These non-personal CSV fixtures are reusable local/UAT import sources for the
Finance App. They use the canonical import columns:

```text
company,account,period,scenario,value,currency,dim_cost_center,dim_profit_center
```

Import a file in **Data & Governance**. For the `*-balanced.csv` files, add a
blocking reconciliation rule with `expected_total = 0` and
`absolute_tolerance = 0`. Each file can then follow the governed lifecycle:

```text
Developer / Preparer -> upload
Local Reviewer       -> review
Local Approver       -> approve and publish
```

`erp-source-columns.csv` intentionally uses ERP-style headers. Import it with
`erp-column-mapping.json` pasted into the column-mapping field to exercise the
mapping path. `invalid-missing-currency.csv` is deliberately invalid and is
for testing validation and error states only.

All values are fictional and expressed in EUR.
