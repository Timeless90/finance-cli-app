"""Deterministic non-production data for integrated UAT environments."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from app.actions.action_management import (
    ActionImpact,
    ActionStatus,
    BenefitObservation,
    BenefitTrackingDefinition,
    ImpactMetric,
    ManagementAction,
)
from app.capital.capital_allocation import (
    CapitalCandidateDefinition,
    CapitalProject,
    FundingOption,
    FundingScenarioDefinition,
    PortfolioConstraints,
)
from app.data.data_foundation import DataSnapshot, FinanceRecord
from app.risk.risk_management import (
    FrequencyModel,
    RiskCategory,
    RiskQuantification,
    RiskRecord,
    SeverityDistribution,
)
from app.shared.rbac import Principal, Role
from app.workspace.workspace_integration import (
    CommandCenterSnapshot,
    WorkspaceProjectionSnapshot,
)

if TYPE_CHECKING:
    from app.shared.composition import ApplicationContainer


UAT_SNAPSHOT_ID = "uat-snapshot-v1"
UAT_COMPANIES = ("AURELIA", "EUROPE")
UAT_PERIOD = "2026-08"
UAT_SCENARIOS = ("base", "downside")


def seed_uat_data(container: ApplicationContainer) -> None:
    """Publish repeatable non-personal read models once per application container."""

    snapshot_exists = any(
        snapshot.snapshot_id == UAT_SNAPSHOT_ID
        for snapshot in container.data_snapshot_repository.list_all()
    )

    records = tuple(
        FinanceRecord(
            company=company,
            account=account,
            period=UAT_PERIOD,
            scenario=scenario,
            value=value,
            currency="EUR",
        )
        for company, company_factor in (
            ("AURELIA", Decimal("1.00")),
            ("EUROPE", Decimal("0.62")),
        )
        for scenario, scenario_factor in (
            ("base", Decimal("1.00")),
            ("downside", Decimal("0.86")),
        )
        for account, value in (
            ("revenue", Decimal("486.3") * company_factor * scenario_factor),
            ("ebitda", Decimal("82.4") * company_factor * scenario_factor),
            ("cash", Decimal("41.7") * company_factor * scenario_factor),
        )
    )
    if not snapshot_exists:
        container.data_snapshot_repository.save(
            DataSnapshot(
                snapshot_id=UAT_SNAPSHOT_ID,
                content_hash="uat-v1",
                row_count=len(records),
                records=records,
            )
        )
    for risk_id, title, owner, probability, losses in (
        (
            "UAT-R-ENERGY",
            "Energy cost escalation",
            "Treasury",
            "0.62",
            ("1800000", "4200000", "8400000"),
        ),
        (
            "UAT-R-VOLUME",
            "Volume softness",
            "Commercial Finance",
            "0.54",
            ("1200000", "3100000", "6500000"),
        ),
    ):
        container.risk_register_service.register(
            RiskRecord(
                risk_id=risk_id,
                title=title,
                cause="Deterministic UAT risk driver",
                event="UAT financial impact",
                owner=owner,
                category=RiskCategory.MARKET,
                horizon_months=12,
                quantification=RiskQuantification(
                    distribution=SeverityDistribution.EMPIRICAL,
                    frequency_model=FrequencyModel.BERNOULLI,
                    occurrence_probability=Decimal(probability),
                    empirical_losses=tuple(Decimal(loss) for loss in losses),
                ),
            )
        )

    publisher = Principal(
        user_id="uat-publisher",
        roles=frozenset({Role.CFO}),
        company_scopes=frozenset(UAT_COMPANIES),
    )
    for company in UAT_COMPANIES:
        for scenario in UAT_SCENARIOS:
            downside = scenario == "downside"
            action_id = f"UAT-ACT-{company}-{scenario}".upper()
            container.action_catalogue_service.register(
                ManagementAction(
                    action_id=action_id,
                    title="Deterministic UAT price-corridor action",
                    owner="Commercial Finance",
                    due_period=9,
                    cost=Decimal("0.40"),
                    impacts=(
                        ActionImpact(
                            period=9,
                            metric=ImpactMetric.EBITDA,
                            amount=Decimal("2.80"),
                            impact_key=f"{action_id}-ebitda",
                        ),
                        ActionImpact(
                            period=9,
                            metric=ImpactMetric.CASH,
                            amount=Decimal("2.20"),
                            impact_key=f"{action_id}-cash",
                        ),
                    ),
                    confidence=Decimal("0.61") if downside else Decimal("0.84"),
                    status=ActionStatus.ACTIVE,
                )
            )
            container.benefit_tracking_catalog.register(
                BenefitTrackingDefinition(
                    company_id=company,
                    period_id=UAT_PERIOD,
                    scenario_id=scenario,
                    action_id=action_id,
                    source_snapshot_ids=(UAT_SNAPSHOT_ID,),
                    observations=(
                        BenefitObservation(
                            action_id=action_id,
                            metric=ImpactMetric.EBITDA,
                            period=9,
                            planned_amount=Decimal("2.80"),
                            realized_amount=Decimal("1.70")
                            if downside
                            else Decimal("2.30"),
                        ),
                        BenefitObservation(
                            action_id=action_id,
                            metric=ImpactMetric.CASH,
                            period=9,
                            planned_amount=Decimal("2.20"),
                            realized_amount=Decimal("1.30")
                            if downside
                            else Decimal("1.90"),
                        ),
                    ),
                )
            )
            for candidate_id, investment, cash_flow, risk_adjusted_npv in (
                ("INV-104", 8.4, 3.2, 16.4),
                ("INV-118", 12.7, 4.1, 13.8),
            ):
                container.capital_candidate_catalog.register(
                    CapitalCandidateDefinition(
                        company_id=company,
                        period_id=UAT_PERIOD,
                        scenario_id=scenario,
                        candidate_id=candidate_id,
                        source_snapshot_ids=(UAT_SNAPSHOT_ID,),
                        project=CapitalProject(
                            project_id=candidate_id,
                            name=f"UAT {candidate_id}",
                            initial_investment=investment,
                            cash_flows=(cash_flow, cash_flow, cash_flow, cash_flow),
                            strategic_score=86.0 if candidate_id == "INV-104" else 82.0,
                            cash_headroom_impact=1.8 if downside else 3.6,
                            leverage_delta=0.04 if candidate_id == "INV-104" else 0.07,
                            interest_cover_delta=-0.03
                            if candidate_id == "INV-104"
                            else -0.05,
                        ),
                        discount_rate=0.11 if downside else 0.09,
                        risk_adjusted_npv=risk_adjusted_npv
                        * (0.82 if downside else 1.0),
                    )
                )
            container.capital_candidate_catalog.register_constraints(
                company_id=company,
                period_id=UAT_PERIOD,
                scenario_id=scenario,
                constraints=PortfolioConstraints(
                    budget=28.0,
                    opening_cash_headroom=21.0 if downside else 32.0,
                    minimum_cash_headroom=20.0 if downside else 12.0,
                    base_leverage=2.4,
                    maximum_leverage=2.75,
                    base_interest_cover=4.2,
                    minimum_interest_cover=3.0,
                ),
            )
            container.capital_candidate_catalog.register_funding(
                FundingScenarioDefinition(
                    company_id=company,
                    period_id=UAT_PERIOD,
                    scenario_id=scenario,
                    option=FundingOption(
                        option_id="RCF-2026",
                        amount=12.0,
                        annual_rate=0.055,
                        term_years=3,
                        upfront_fee=0.12,
                    ),
                    source_snapshot_ids=(UAT_SNAPSHOT_ID,),
                    base_debt=165.0,
                    base_ebitda=68.9 if downside else 82.4,
                    base_interest_expense=13.5,
                    maximum_leverage=2.75,
                )
            )
            context = container.context_catalog_service.resolve(
                publisher,
                company_id=company,
                period_id=UAT_PERIOD,
                scenario_id=scenario,
            )
            snapshot = _projection(context, company=company, scenario=scenario)
            container.workspace_read_model_service.publish_command_center(
                CommandCenterSnapshot(
                    context=context,
                    as_of=snapshot.as_of,
                    metrics=tuple(snapshot.data["command_center_metrics"]),
                    forecast=snapshot.data["command_center_forecast"],
                    liquidity=snapshot.data["command_center_liquidity"],
                    risk=snapshot.data["command_center_risk"],
                    variance_drivers=tuple(
                        snapshot.data["command_center_variance_drivers"]
                    ),
                    actions=tuple(snapshot.data["command_center_actions"]),
                    briefing=str(snapshot.data["command_center_briefing"]),
                    assurance=snapshot.assurance,
                    source_snapshot_ids=snapshot.source_snapshot_ids,
                    projection_version=snapshot.projection_version,
                )
            )
            for workspace in container.workspace_read_model_service.WORKSPACE_KEYS:
                container.workspace_read_model_service.publish_workspace(
                    workspace,
                    _for_workspace(snapshot, workspace),
                )


def _for_workspace(
    snapshot: WorkspaceProjectionSnapshot,
    workspace: str,
) -> WorkspaceProjectionSnapshot:
    data = snapshot.data
    keys_by_workspace = {
        "planning": {
            "scenarios",
            "active_forecast",
            "forecast_series",
            "financial_statement",
            "drivers",
            "thresholds",
            "forecast_assurance",
        },
        "performance": {
            "metrics",
            "kpi_tree",
            "variance_bridge",
            "trend",
            "anomalies",
            "commentary_requirements",
        },
        "profitability": {
            "metrics",
            "segments",
            "margin_waterfall",
            "profitability_matrix",
            "sensitivity_summary",
            "allocation_assurance",
        },
        "liquidity": {
            "metrics",
            "cash_forecast",
            "working_capital",
            "debt",
            "covenants",
            "stresses",
        },
        "risk": {
            "portfolio",
            "percentile_curve",
            "risks",
            "categories",
            "appetite_radar",
            "correlation",
            "scenario",
            "controls",
            "regimes",
            "tail",
        },
        "market-risk": {"assets", "selected_runs", "threshold_states"},
        "actions": {"actions", "benefit_series", "dependencies"},
        "capital": {
            "capital_portfolio",
            "candidates",
            "constraints",
            "allocation",
            "frontier_points",
            "approvals",
            "funding_options",
        },
        "reporting": {
            "active_report",
            "sections",
            "versions",
            "source_pack",
            "findings",
            "export_targets",
        },
        "data-governance": {
            "snapshots",
            "quality_findings",
            "governed_runs",
            "models",
            "governance_approvals",
            "governance_lineage",
        },
    }
    workspace_data = {key: data[key] for key in keys_by_workspace[workspace]}
    if workspace == "actions":
        workspace_data["metrics"] = data["action_metrics"]
    if workspace == "capital":
        workspace_data["portfolio"] = workspace_data.pop("capital_portfolio")
    return replace(snapshot, data=workspace_data)


def _projection(
    context: Any, *, company: str, scenario: str
) -> WorkspaceProjectionSnapshot:
    downside = scenario == "downside"
    company_label = "Aurelia Holding" if company == "AURELIA" else "Europe Division"
    revenue = "€451.7M" if downside else "€486.3M"
    ebitda = "€68.9M" if downside else "€82.4M"
    cash = "€24.6M" if downside else "€41.7M"
    delta = "-€9.6M vs plan" if downside else "+€3.9M vs plan"
    tone = "negative" if downside else "positive"
    value = 68.9 if downside else 82.4
    assurance = {
        "data_freshness": "UAT deterministic dataset",
        "coverage": "complete",
        "model_status": "validated",
        "lineage_status": "complete",
    }
    data: dict[str, Any] = {
        "command_center_metrics": [
            {
                "metric_id": "revenue",
                "label": "REVENUE",
                "value": revenue,
                "delta": "-2.6% vs plan" if downside else "+4.8% vs plan",
                "delta_tone": tone,
                "meta": "FY26 UAT outlook",
            },
            {
                "metric_id": "ebitda",
                "label": "EBITDA",
                "value": ebitda,
                "delta": delta,
                "delta_tone": tone,
                "meta": "validated projection",
            },
            {
                "metric_id": "free_cash_flow",
                "label": "FREE CASH FLOW",
                "value": cash,
                "delta": "-€19.5M vs plan" if downside else "+€1.7M vs plan",
                "delta_tone": tone,
                "meta": "working capital outlook",
            },
        ],
        "command_center_forecast": {
            "title": "EBITDA trajectory",
            "subtitle": "Validated UAT projection // €M",
            "points": [
                {
                    "period": "P08",
                    "actual": value,
                    "base": value,
                    "upside": value,
                    "downside": value,
                },
                {
                    "period": "P09",
                    "base": value + 1.1,
                    "upside": value + 2.2,
                    "downside": value - 2.4,
                },
            ],
        },
        "command_center_liquidity": {
            "cash": cash,
            "runway": "11.2 months" if downside else "17.4 months",
            "minimum_headroom": "€5.7M" if downside else "€14.2M",
            "covenant_headroom": "19%" if downside else "38%",
            "tone": "warning" if downside else "positive",
        },
        "command_center_risk": {
            "score": "67 / 100" if downside else "42 / 100",
            "expected_loss": "€11.7M" if downside else "€6.6M",
            "tail_loss": "€31.4M" if downside else "€18.9M",
            "appetite_usage": "88%" if downside else "61%",
            "signals": [
                {
                    "risk_id": "R-017",
                    "title": "Energy cost escalation",
                    "owner": "Treasury",
                    "exposure": "€5.8M",
                    "severity": "HIGH",
                    "trend": "UP",
                }
            ],
        },
        "command_center_variance_drivers": [
            {
                "label": "Volume",
                "amount": "-€5.6M" if downside else "+€5.6M",
                "share": "46%",
                "tone": tone,
            },
            {"label": "Energy", "amount": "-€2.4M", "share": "20%", "tone": "negative"},
        ],
        "command_center_actions": [
            {
                "action_id": "ACT-042",
                "title": "Accelerate price corridor update",
                "owner": "Commercial Finance",
                "due": "P09 W2",
                "status": "AT RISK" if downside else "ON TRACK",
                "impact": "+€2.8M EBITDA",
                "confidence": "71%" if downside else "84%",
            }
        ],
        "command_center_briefing": (
            f"{company_label}: downside requires immediate margin and cash protection."
            if downside
            else f"{company_label}: validated base scenario remains above plan."
        ),
        "scenarios": [
            {
                "scenario_id": "base",
                "label": "Base",
                "type": "BASE",
                "status": "APPROVED",
                "revenue": "€486.3M",
                "ebitda": "€82.4M",
                "free_cash_flow": "€41.7M",
                "owner": "Group FP&A",
            },
            {
                "scenario_id": "downside",
                "label": "Downside",
                "type": "DOWNSIDE",
                "status": "APPROVED",
                "revenue": "€451.7M",
                "ebitda": "€68.9M",
                "free_cash_flow": "€24.6M",
                "owner": "Group FP&A",
            },
        ],
        "active_forecast": {
            "version_id": f"uat-{scenario}-v1",
            "snapshot_id": UAT_SNAPSHOT_ID,
            "assumption_set_id": f"uat-{scenario}-assumptions",
            "model_version": "uat-planning-v1",
            "status": "approved",
            "label": scenario.title(),
        },
        "forecast_series": [
            {
                "period": "P08",
                "actual": value,
                "plan": 78.5,
                "forecast": value,
                "lower": value - 4,
                "upper": value + 4,
            }
        ],
        "financial_statement": [
            {
                "line_item": "EBITDA",
                "label": "EBITDA",
                "actual": ebitda,
                "plan": "€78.5M",
                "forecast": ebitda,
                "variance": delta,
                "variance_tone": tone,
                "level": 0,
            }
        ],
        "drivers": [
            {
                "driver_id": "volume",
                "label": "Volume growth",
                "value": "-2.6" if downside else "+4.8",
                "unit": "%",
                "delta": "-1.0pp" if downside else "+0.9pp",
                "owner": "Commercial Finance",
                "status": "REVIEW" if downside else "LOCKED",
            }
        ],
        "thresholds": [
            {
                "metric_id": "EBITDA margin",
                "target": ">= 16.5%",
                "warning": "< 15.5%",
                "current": "14.9%" if downside else "16.9%",
                "status": "WARNING" if downside else "ON_TARGET",
            }
        ],
        "forecast_assurance": {
            "confidence": "71%" if downside else "82%",
            "mape": "5.8%" if downside else "4.6%",
            "bias": "-1.9%" if downside else "+0.8%",
        },
        "metrics": [
            {
                "metric_id": "ebitda",
                "label": "EBITDA",
                "value": ebitda,
                "delta": delta,
                "delta_tone": tone,
                "meta": "validated projection",
            }
        ],
        "kpi_tree": [
            {
                "node_id": "ebitda",
                "label": "EBITDA",
                "value": ebitda,
                "variance": delta,
                "tone": tone,
            }
        ],
        "variance_bridge": {
            "kpi": "EBITDA",
            "comparison": "ACTUAL_VS_PLAN",
            "baseline": "€78.5M",
            "actual": ebitda,
            "explained": "€9.6M" if downside else "€3.9M",
            "unexplained": "€0.0M",
            "fully_explained": True,
            "steps": [
                {
                    "id": "baseline",
                    "label": "Plan",
                    "amount": 78.5,
                    "display": "€78.5M",
                    "type": "start",
                },
                {
                    "id": "actual",
                    "label": "Actual",
                    "amount": value,
                    "display": ebitda,
                    "type": "end",
                },
            ],
        },
        "trend": [{"period": "P08", "actual": value, "plan": 78.5, "forecast": value}],
        "anomalies": [
            {
                "anomaly_id": "AN-031",
                "period": "P08",
                "kpi": "EBITDA",
                "observation": "Downside pressure"
                if downside
                else "Within expected range",
                "severity": "HIGH" if downside else "LOW",
                "status": "OPEN" if downside else "REVIEWED",
            }
        ],
        "commentary_requirements": [
            {
                "commentary_id": "COM-01",
                "kpi": "EBITDA",
                "variance": delta,
                "threshold": "€2.0M",
                "status": "REQUIRED" if downside else "COMPLETE",
                "owner": "Group FP&A",
            }
        ],
        "portfolio": {
            "mean_gross_loss": "€15.2M" if downside else "€9.4M",
            "mean_net_loss": "€11.7M" if downside else "€6.7M",
            "p50_net_loss": "€8.9M" if downside else "€4.6M",
            "p95_net_loss": "€28.6M" if downside else "€15.4M",
            "p99_net_loss": "€43.9M" if downside else "€23.6M",
            "expected_shortfall_95": "€36.7M" if downside else "€19.8M",
            "appetite_usage": "88%" if downside else "61%",
            "paths": "10,000",
            "seed": "20260809",
        },
        "percentile_curve": [
            {"percentile": 50, "loss": 8.9 if downside else 4.6},
            {"percentile": 95, "loss": 28.6 if downside else 15.4},
            {"percentile": 99, "loss": 43.9 if downside else 23.6},
        ],
        "risks": [
            {
                "risk_id": "UAT-R-ENERGY",
                "title": "Energy cost escalation",
                "category": "Market",
                "owner": "Treasury",
                "probability": 0.74 if downside else 0.62,
                "impact": 0.78,
                "expected_loss": "€4.2M" if downside else "€2.9M",
                "p95_loss": "€11.2M" if downside else "€8.4M",
                "residual_loss": "€3.2M" if downside else "€2.1M",
                "mitigation_effect": "€1.0M",
                "appetite_usage": "112%" if downside else "74%",
                "status": "BREACHED" if downside else "WARNING",
                "trend": "UP",
            },
            {
                "risk_id": "UAT-R-VOLUME",
                "title": "Volume softness",
                "category": "Strategic",
                "owner": "Commercial Finance",
                "probability": 0.66 if downside else 0.54,
                "impact": 0.72,
                "expected_loss": "€3.1M" if downside else "€2.1M",
                "p95_loss": "€8.8M" if downside else "€6.5M",
                "residual_loss": "€2.5M" if downside else "€1.8M",
                "mitigation_effect": "€0.6M",
                "appetite_usage": "104%" if downside else "67%",
                "status": "BREACHED" if downside else "WARNING",
                "trend": "STABLE",
            },
        ],
        "categories": [
            {
                "category_id": "market",
                "label": "Market",
                "gross_exposure": 84,
                "residual_exposure": 71,
                "appetite": 60,
                "tone": "negative",
            }
        ],
        "appetite_radar": [{"dimension": "Market", "exposure": 71, "appetite": 60}],
        "correlation": {"labels": ["Energy", "Volume"], "matrix": [[1, 0.3], [0.3, 1]]},
        "scenario": {
            "name": "Combined downside" if downside else "Base outlook",
            "description": "Published deterministic UAT risk scenario.",
            "earnings_at_risk": "€24.9M EBITDA" if downside else "€13.8M EBITDA",
            "cash_at_risk": "€22.1M FCF" if downside else "€10.6M FCF",
            "probability": "29%" if downside else "17%",
            "top_drivers": ["Energy escalation", "Volume compression"],
        },
        "controls": [
            {
                "control_id": "CTL-UAT-ENERGY",
                "risk_id": "UAT-R-ENERGY",
                "name": "Energy hedge ladder",
                "owner": "Treasury",
                "effectiveness": "38%",
                "annual_cost": "€0.42M",
                "avoided_loss": "€1.0M",
                "status": "ACTIVE",
            }
        ],
        "regimes": {
            "lifecycle": "LIVE_RUN_AVAILABLE",
            "current_state": "PRESSURE" if downside else "NORMAL",
            "state_confidence": "68%",
            "states": [
                {
                    "id": "S1",
                    "label": "Normal",
                    "probability": 0.32,
                    "expected_loss_multiplier": "1.00x",
                },
                {
                    "id": "S2",
                    "label": "Pressure",
                    "probability": 0.68,
                    "expected_loss_multiplier": "1.42x",
                },
            ],
            "transition_matrix": [[0.72, 0.28], [0.22, 0.78]],
        },
        "tail": {
            "lifecycle": "LIVE_RUN_AVAILABLE",
            "threshold": "€11.7M / P90",
            "shape": "ξ = 0.21",
            "scale": "β = €4.8M",
            "expected_shortfall": "€36.7M" if downside else "€19.8M",
            "qq": [
                {"theoretical": 1.0, "observed": 1.1},
                {"theoretical": 5.0, "observed": 5.4},
                {"theoretical": 10.0, "observed": 11.2},
            ],
        },
        "segments": [
            {
                "segment_id": "core",
                "label": "Core Products",
                "revenue": "€198.4M" if downside else "€214.6M",
                "contribution_margin": "€48.7M" if downside else "€58.5M",
                "contribution_margin_pct": "24.5%" if downside else "27.3%",
                "ebitda": "€24.8M" if downside else "€31.2M",
                "allocated_cost": "€18.8M",
                "margin_at_risk": "€8.9M" if downside else "€5.4M",
                "status": "WATCH" if downside else "STRONG",
            }
        ],
        "margin_waterfall": [
            {
                "id": "revenue",
                "label": "REVENUE",
                "amount": 451.7 if downside else 486.3,
                "display": "€451.7M" if downside else "€486.3M",
                "type": "start",
            },
            {
                "id": "ebitda",
                "label": "EBITDA",
                "amount": value,
                "display": ebitda,
                "type": "end",
            },
        ],
        "profitability_matrix": [
            {
                "id": "core-strategic",
                "product": "CX-400",
                "customer": "Key Accounts",
                "channel": "Partner",
                "revenue": "€56.1M" if downside else "€61.5M",
                "margin_pct": "21.4%" if downside else "26.1%",
                "margin_at_risk": "€4.2M" if downside else "€2.9M",
                "status": "WATCH" if downside else "STRONG",
            }
        ],
        "sensitivity_summary": [
            {
                "lever": "Price recovery",
                "movement": "+1.5%",
                "ebitda_impact": "+€6.8M",
                "margin_impact": "+1.5pp",
                "tone": "positive",
            }
        ],
        "allocation_assurance": {
            "version_id": "uat-allocation-v1",
            "snapshot_id": UAT_SNAPSHOT_ID,
            "method": "DRIVER + ABC",
            "source_cost": "€62.24M",
            "allocated_cost": "€62.20M",
            "reconciliation_difference": "€0.04M",
            "reconciled": True,
        },
        "cash_forecast": {
            "minimum_liquidity": "€20.0M",
            "minimum_headroom": "€5.7M" if downside else "€14.2M",
            "forecast_accuracy": "86.1%" if downside else "92.4%",
            "points": [
                {
                    "period": "W01",
                    "opening": 31.5,
                    "inflow": 13.2 if downside else 14.5,
                    "outflow": 14.4 if downside else 13.8,
                    "closing": 30.3 if downside else 32.2,
                    "minimum": 20,
                }
            ],
        },
        "working_capital": [
            {
                "metric_id": "dso",
                "label": "DSO",
                "current": "56d" if downside else "48d",
                "target": "45d",
                "cash_impact": "-€14.2M" if downside else "-€3.9M",
                "status": "BREACH" if downside else "WATCH",
            }
        ],
        "debt": [
            {
                "debt_id": "RCF-01",
                "instrument": "Revolving Credit Facility",
                "principal": "€18.0M",
                "rate": "3.85%",
                "maturity": "FY29 P06",
                "committed_limit": "€50.0M",
                "headroom": "€32.0M",
                "status": "NORMAL",
            }
        ],
        "covenants": [
            {
                "covenant_id": "COV-LIQ",
                "metric": "Minimum liquidity",
                "actual": "€24.6M" if downside else "€36.8M",
                "threshold": ">= €20.0M",
                "headroom": "€4.6M" if downside else "€16.8M",
                "projected_minimum": "€17.6M" if downside else "€34.2M",
                "status": "WATCH" if downside else "PASS",
            }
        ],
        "stresses": [
            {
                "stress_id": "S-COMB",
                "name": "Combined downside",
                "closing_cash": "€7.4M" if downside else "€17.6M",
                "headroom": "-€12.6M" if downside else "-€2.4M",
                "breach": True,
                "mitigation": "Spend gate + RCF + working-capital actions",
            }
        ],
        "assets": [
            {
                "asset_id": "eurusd",
                "label": "EUR/USD",
                "asset_class": "FX",
                "exposure": "€42.0M",
                "spot": "1.148",
                "daily_vol": "0.74%",
                "annualized_vol": "11.8%",
                "var95": "€0.52M",
                "es95": "€0.71M",
                "beta": "0.18",
                "status": "NORMAL",
            },
            {
                "asset_id": "brent",
                "label": "Brent",
                "asset_class": "COMMODITY",
                "exposure": "€28.5M",
                "spot": "$82.4",
                "daily_vol": "1.92%",
                "annualized_vol": "42.8%" if downside else "30.5%",
                "var95": "€1.31M" if downside else "€0.91M",
                "es95": "€1.82M" if downside else "€1.24M",
                "beta": "0.41",
                "status": "STRESS" if downside else "WATCH",
            },
        ],
        "selected_runs": {
            "selected_asset_id": "brent",
            "model_lifecycle": "LIVE_RUN_AVAILABLE",
            "garch": {
                "model": "GARCH(1,1)-t",
                "run_id": "uat-garch-brent-v1",
                "convergence": "CONVERGED",
                "log_likelihood": "-1,842.6",
                "aic": "3,695.2",
                "bic": "3,721.8",
                "persistence": "0.964",
                "unconditional_vol": "42.8%" if downside else "30.5%",
                "parameters": [
                    {
                        "name": "α₁",
                        "estimate": "0.081",
                        "std_error": "0.018",
                        "t_stat": "4.50",
                        "p_value": "<0.001",
                    }
                ],
                "volatility": [
                    {
                        "index": 1,
                        "observed": 1.2,
                        "fitted": 1.1,
                        "lower": 0.9,
                        "upper": 1.4,
                    },
                    {
                        "index": 2,
                        "observed": 1.5,
                        "fitted": 1.4,
                        "lower": 1.1,
                        "upper": 1.7,
                    },
                ],
                "residuals": [
                    {"index": 1, "value": -0.42},
                    {"index": 2, "value": 0.94},
                ],
                "qq": [
                    {"theoretical": -1.0, "observed": -1.1},
                    {"theoretical": 1.0, "observed": 1.2},
                ],
            },
            "regimes": {
                "model": "2-STATE MARKOV SWITCHING",
                "run_id": "uat-regime-v1",
                "current_state": "HIGH VOL" if downside else "LOW VOL",
                "confidence": "82%" if downside else "59%",
                "states": [
                    {
                        "id": "S1",
                        "label": "LOW VOL",
                        "probability": 0.18 if downside else 0.41,
                        "mean": "+0.03%",
                        "volatility": "18.2%",
                    },
                    {
                        "id": "S2",
                        "label": "HIGH VOL",
                        "probability": 0.82 if downside else 0.59,
                        "mean": "-0.06%",
                        "volatility": "38.7%",
                    },
                ],
                "probabilities": [
                    {"index": 1, "low": 0.41, "high": 0.59},
                    {"index": 2, "low": 0.18, "high": 0.82},
                ],
                "transition_matrix": [[0.94, 0.06], [0.11, 0.89]],
            },
            "marginals": [
                {
                    "asset_id": "brent",
                    "family": "Student-t",
                    "location": "-0.02%",
                    "scale": "1.76%",
                    "dof": "6.4",
                    "aic": "-7,216",
                    "ks_p_value": "0.22",
                }
            ],
            "dependency": {
                "model": "t-COPULA",
                "run_id": "uat-copula-v1",
                "dof": "5.9",
                "log_likelihood": "2,184.7",
                "tail_dependence": "0.21",
                "labels": ["EUR/USD", "Brent"],
                "matrix": [[1, -0.18], [-0.18, 1]],
                "edges": [
                    {
                        "source": "EUR/USD",
                        "target": "Brent",
                        "correlation": -0.18,
                        "tail_dependence": 0.12,
                    }
                ],
            },
            "simulation": {
                "run_id": "uat-market-var-v1",
                "paths": "50,000",
                "horizon": "252D",
                "seed": "20260809",
                "var95": "€8.9M" if downside else "€4.8M",
                "es95": "€12.7M" if downside else "€6.7M",
                "fan": [
                    {
                        "horizon": 0,
                        "p05": 100,
                        "p25": 100,
                        "p50": 100,
                        "p75": 100,
                        "p95": 100,
                    },
                    {
                        "horizon": 252,
                        "p05": 63,
                        "p25": 83,
                        "p50": 105,
                        "p75": 129,
                        "p95": 160,
                    },
                ],
            },
            "backtest": {
                "window": "500D",
                "observations": 500,
                "var_exceptions": 31 if downside else 21,
                "expected_exceptions": "25.0",
                "kupiec_p_value": "0.08" if downside else "0.39",
                "christoffersen_p_value": "0.28",
                "traffic_light": "YELLOW" if downside else "GREEN",
                "breaches": [
                    {
                        "date": "2026-07-21",
                        "return": "-5.2%",
                        "var_limit": "-4.0%",
                        "severity": "1.30x",
                        "documented": False,
                        "note": "Documentation required",
                    }
                ],
            },
            "model_comparison": [
                {
                    "id": "M3",
                    "model": "GARCH(1,1)-t",
                    "aic": "3,695",
                    "bic": "3,722",
                    "out_of_sample_loss": "0.79",
                    "var_coverage": "95.8%",
                    "tail_fit": "GOOD",
                    "status": "CHAMPION",
                }
            ],
        },
        "threshold_states": [
            {
                "threshold_id": "TH-VAR",
                "metric": "1D VaR 95",
                "warning": "> €0.85M",
                "breach": "> €1.10M",
                "current": "€1.31M" if downside else "€0.91M",
                "status": "BREACH" if downside else "WARNING",
                "documentation": "Review hedge ratio in Treasury meeting",
            }
        ],
        "action_metrics": {
            "items": [
                {
                    "metric_id": "impact",
                    "label": "EXPECTED EBITDA IMPACT",
                    "value": "+€18.9M" if downside else "+€14.8M",
                    "delta": "+€6.2M protection"
                    if downside
                    else "+€2.1M vs prior gate",
                    "delta_tone": "positive",
                    "meta": "published action projection",
                }
            ]
        },
        "actions": [
            {
                "action_id": f"UAT-ACT-{company}-{scenario}".upper(),
                "title": "Accelerate price corridor update",
                "source": "Performance / DACH",
                "owner": "Commercial Finance",
                "sponsor": "CCO",
                "due": "P09 W2",
                "status": "AT_RISK" if downside else "IN_EXECUTION",
                "priority": "P0",
                "confidence": "61%" if downside else "84%",
                "expected_ebitda": "+€2.8M",
                "expected_cash": "+€2.2M",
                "realized_ebitda": "+€1.7M",
                "realized_cash": "+€1.3M",
                "realization_pct": "61%",
                "risk_reduction": "€0.9M",
                "evidence": "Pricing wave approved",
                "next_gate": "P09 W1 review",
            }
        ],
        "benefit_series": [
            {"period": "P08", "expected": 9.4, "realized": 6.8},
            {"period": "P09", "expected": 14.8, "realized": 10.7},
        ],
        "dependencies": [
            {"action_id": "ACT-042", "depends_on": "ACT-036", "type": "ENABLING"}
        ],
        "capital_portfolio": {
            "budget": "€96.0M",
            "committed": "€58.4M",
            "approved": "€18.6M",
            "unallocated": "€9.0M" if downside else "€19.0M",
            "liquidity_reserve": "€20.0M" if downside else "€12.0M",
            "expected_portfolio_npv": "€61.7M" if downside else "€74.8M",
            "downside_capital_at_risk": "€27.8M" if downside else "€16.2M",
        },
        "candidates": [
            {
                "candidate_id": "INV-104",
                "name": "Digital pricing platform",
                "category": "Digital",
                "sponsor": "CCO",
                "capital_required": "€8.4M",
                "npv": "€19.6M",
                "irr": "31%",
                "payback": "2.1y",
                "risk_adjusted_score": 86,
                "strategic_fit": 92,
                "liquidity_impact": "-€5.1M Y1",
                "downside_loss": "€3.2M",
                "status": "APPROVED",
            }
        ],
        "constraints": [
            {
                "constraint_id": "CAP-LIQ",
                "label": "Minimum liquidity reserve",
                "limit": ">= €20.0M" if downside else ">= €12.0M",
                "used": "€5.7M" if downside else "€14.2M",
                "headroom": "-€14.3M" if downside else "€2.2M",
                "status": "BREACH" if downside else "WATCH",
            }
        ],
        "allocation": [
            {
                "category": "Digital",
                "amount": "€16.8M",
                "share": 22,
                "expected_npv": "€26.3M",
            }
        ],
        "frontier_points": [
            {
                "portfolio_id": "P2",
                "label": "Balanced",
                "risk": 31,
                "return": 67,
                "selected": True,
            }
        ],
        "approvals": [
            {
                "approval_id": "APR-209",
                "candidate_id": "INV-104",
                "gate": "Investment Committee",
                "owner": "CFO",
                "status": "APPROVED",
                "due": "P08 W3",
            }
        ],
        "funding_options": [
            {
                "option_id": "RCF-2026",
                "label": "Revolving credit facility",
                "status": "AVAILABLE",
                "source_snapshot_ids": [UAT_SNAPSHOT_ID],
            }
        ],
        "active_report": {
            "report_id": f"UAT-RPT-{company}-{scenario}".upper(),
            "title": "UAT CFO management pack",
            "template": "Management Pack v1",
            "status": "PUBLISHED",
            "current_version_id": "v1",
            "reporting_date": "2026-08-09",
            "completeness": "100%",
            "source_coverage": "100%",
        },
        "sections": [
            {
                "id": "kpi",
                "title": "Executive KPIs",
                "status": "APPROVED",
                "source_count": 1,
            },
            {
                "id": "performance",
                "title": "Performance",
                "status": "APPROVED",
                "source_count": 1,
            },
            {
                "id": "forecast",
                "title": "Forecast",
                "status": "APPROVED",
                "source_count": 1,
            },
            {
                "id": "cash",
                "title": "Liquidity",
                "status": "APPROVED",
                "source_count": 1,
            },
        ],
        "versions": [
            {
                "version_id": "v1",
                "status": "PUBLISHED",
                "source_snapshot_ids": [UAT_SNAPSHOT_ID],
                "content_hash": "uat-report-v1",
            }
        ],
        "source_pack": [
            {
                "source_id": UAT_SNAPSHOT_ID,
                "label": "UAT finance snapshot",
                "status": "APPROVED",
                "as_of": "2026-08-09T08:00:00Z",
            }
        ],
        "findings": [],
        "export_targets": [
            {"format": "PDF", "status": "READY"},
            {"format": "XLSX", "status": "READY"},
        ],
        "snapshots": [
            {
                "snapshot_id": UAT_SNAPSHOT_ID,
                "row_count": 12,
                "content_hash": "uat-v1",
                "status": "APPROVED",
            }
        ],
        "quality_findings": [],
        "governed_runs": [
            {
                "run_id": "uat-projection-v1",
                "status": "APPROVED",
                "model_id": "workspace-projection",
                "snapshot_id": UAT_SNAPSHOT_ID,
            }
        ],
        "models": [
            {
                "model_id": "workspace-projection",
                "version": "uat-v1",
                "status": "VALIDATED",
            }
        ],
        "governance_approvals": [
            {
                "approval_id": "uat-projection-approval",
                "status": "APPROVED",
                "actor": "uat-publisher",
            }
        ],
        "governance_lineage": {
            "snapshot_id": UAT_SNAPSHOT_ID,
            "projection_version": 1,
            "source": "uat-seed",
        },
    }
    return WorkspaceProjectionSnapshot(
        context=context,
        as_of=datetime(2026, 8, 9, 8, 0, tzinfo=UTC),
        data=data,
        lineage={"seed": "uat-v1", "company": company, "scenario": scenario},
        assurance=assurance,
        source_snapshot_ids=(UAT_SNAPSHOT_ID,),
        projection_version=1,
    )
