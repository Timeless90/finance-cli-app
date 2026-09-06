from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.actions.router import build_action_router
from app.capital.router import build_capital_router
from app.copilot.router import build_copilot_router
from app.data.router import build_data_router
from app.decisions.router import build_decision_run_router
from app.governance.router import build_governance_router
from app.jobs.router import build_job_router
from app.liquidity.router import build_liquidity_router
from app.market_risk.router import build_market_risk_router
from app.model_runs.finance_model_runs import (
    FinanceModelRunService,
    InMemoryFinanceModelRunRepository,
)
from app.model_runs.router import build_model_run_router
from app.performance.router import build_performance_router
from app.planning.router import build_planning_router
from app.profitability.router import build_profitability_router
from app.reporting.router import build_reporting_router
from app.risk.router import build_risk_router
from app.shared.composition import ApplicationContainer, build_container
from app.shared.config import ApiSettings, get_settings
from app.shared.hardening import RequestHardeningMiddleware
from app.shared.observability.setup import configure
from app.shared.uat import seed_uat_data
from app.system.router import (
    build_module_foundation_router,
    build_platform_router,
    build_system_router,
)
from app.workspace.router import build_workspace_router


def create_app(
    settings: ApiSettings | None = None,
    container: ApplicationContainer | None = None,
) -> FastAPI:
    resolved = settings or get_settings()
    resolved_container = container or build_container(
        governance_database_path=resolved.governance_database_path,
        governance_database_url=resolved.governance_database_url,
        import_storage_path=resolved.import_storage_path,
    )
    if resolved.environment.lower() == "uat":
        seed_uat_data(resolved_container)
    finance_model_runs = FinanceModelRunService(
        resolved_container.context_catalog_service,
        resolved_container.data_snapshot_repository,
        InMemoryFinanceModelRunRepository(),
        resolved_container.risk_register_service,
        resolved_container.risk_aggregation_engine,
        resolved_container.market_risk_metrics,
        resolved_container.garch_t_model,
        resolved_container.regime_hmm_model,
        resolved_container.evt_tail_overlay,
        resolved_container.copula_dependence_model,
        resolved_container.var_backtester,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            resolved_container.shutdown()
            close_telemetry()

    app = FastAPI(
        title="CFO Command Center API",
        version=resolved.build_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    close_telemetry = configure(app, resolved)
    app.state.settings = resolved
    app.state.container = resolved_container
    app.state.finance_model_run_service = finance_model_runs
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RequestHardeningMiddleware,
        requests_per_minute=resolved.rate_limit_requests_per_minute,
    )
    app.include_router(build_system_router(resolved))
    app.include_router(build_platform_router(), prefix=resolved.api_prefix)
    app.include_router(build_module_foundation_router(), prefix=resolved.api_prefix)
    app.include_router(
        build_job_router(resolved_container.job_manager),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_data_router(
            resolved_container.finance_import_publication_service,
            resolved_container.planning_baseline_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_governance_router(
            resolved_container.governed_run_service,
            resolved_container.scenario_service,
            resolved_container.model_registry_service,
            resolved_container.access_control,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_workspace_router(
            resolved_container.context_catalog_service,
            resolved_container.workspace_read_model_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_model_run_router(finance_model_runs),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_planning_router(
            resolved_container.rolling_forecast_service,
            resolved_container.probabilistic_forecast_engine,
            resolved_container.rolling_origin_backtester,
            resolved_container.goal_threshold_engine,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_performance_router(
            resolved_container.variance_analysis_engine,
            resolved_container.forecast_accuracy_service,
            resolved_container.anomaly_detection_service,
            resolved_container.management_commentary_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_profitability_router(
            resolved_container.profitability_service,
            resolved_container.cost_allocation_service,
            resolved_container.activity_based_costing_service,
            resolved_container.profitability_reconciliation_service,
            resolved_container.margin_sensitivity_service,
            resolved_container.margin_at_risk_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_liquidity_router(
            resolved_container.thirteen_week_cash_forecast,
            resolved_container.monthly_liquidity_forecast,
            resolved_container.working_capital_model,
            resolved_container.debt_schedule_engine,
            resolved_container.covenant_engine,
            resolved_container.liquidity_stress_engine,
            resolved_container.cash_forecast_accuracy_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_market_risk_router(
            resolved_container.exposure_management_service,
            resolved_container.market_sensitivity_engine,
            resolved_container.market_risk_metrics,
            resolved_container.garch_t_model,
            resolved_container.regime_hmm_model,
            resolved_container.evt_tail_overlay,
            resolved_container.copula_dependence_model,
            resolved_container.hedge_scenario_engine,
            resolved_container.var_backtester,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_risk_router(
            resolved_container.risk_register_service,
            resolved_container.risk_quantification_engine,
            resolved_container.risk_aggregation_engine,
            resolved_container.risk_appetite_engine,
            resolved_container.risk_to_plan_engine,
            resolved_container.risk_reporting_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_action_router(
            resolved_container.action_catalogue_service,
            resolved_container.action_simulation_engine,
            resolved_container.action_portfolio_prioritizer,
            resolved_container.action_review_service,
            resolved_container.benefit_tracking_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_decision_run_router(
            resolved_container.decision_run_service,
            resolved_container.action_catalogue_service,
            resolved_container.action_simulation_engine,
            resolved_container.action_portfolio_prioritizer,
            resolved_container.benefit_tracking_service,
            resolved_container.benefit_tracking_catalog,
            resolved_container.capital_candidate_catalog,
            resolved_container.project_valuation_service,
            resolved_container.monte_carlo_npv_engine,
            resolved_container.capital_portfolio_optimizer,
            resolved_container.funding_scenario_engine,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_reporting_router(
            resolved_container.reporting_factory,
            resolved_container.report_exporter,
            resolved_container.report_run_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_copilot_router(
            resolved_container.finance_copilot_service,
            resolved_container.ai_model_routing,
            resolved_container.context_catalog_service,
            resolved_container.workspace_read_model_service,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_capital_router(
            resolved_container.project_valuation_service,
            resolved_container.monte_carlo_npv_engine,
            resolved_container.capital_portfolio_optimizer,
            resolved_container.funding_scenario_engine,
        ),
        prefix=resolved.api_prefix,
    )
    return app
