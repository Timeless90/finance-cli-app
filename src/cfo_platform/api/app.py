from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cfo_platform.composition import ApplicationContainer, build_container

from .action_routes import build_action_router
from .capital_routes import build_capital_router
from .copilot_routes import build_copilot_router
from .data_routes import build_data_router
from .governance_routes import build_governance_router
from .job_routes import build_job_router
from .liquidity_routes import build_liquidity_router
from .market_risk_routes import build_market_risk_router
from .performance_routes import build_performance_router
from .planning_routes import build_planning_router
from .profitability_routes import build_profitability_router
from .reporting_routes import build_reporting_router
from .risk_routes import build_risk_router
from .routes import (
    build_module_foundation_router,
    build_platform_router,
    build_system_router,
)
from .settings import ApiSettings, get_settings


def create_app(
    settings: ApiSettings | None = None,
    container: ApplicationContainer | None = None,
) -> FastAPI:
    resolved = settings or get_settings()
    resolved_container = container or build_container()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        resolved_container.shutdown()

    app = FastAPI(
        title="CFO Command Center API",
        version=resolved.build_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = resolved
    app.state.container = resolved_container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(build_system_router(resolved))
    app.include_router(build_platform_router(), prefix=resolved.api_prefix)
    app.include_router(build_module_foundation_router(), prefix=resolved.api_prefix)
    app.include_router(build_job_router(resolved_container.job_manager), prefix=resolved.api_prefix)
    app.include_router(build_data_router(resolved_container.finance_data_workflow), prefix=resolved.api_prefix)
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
        build_reporting_router(
            resolved_container.reporting_factory,
            resolved_container.report_exporter,
        ),
        prefix=resolved.api_prefix,
    )
    app.include_router(
        build_copilot_router(
            resolved_container.finance_copilot_service,
            resolved_container.ai_model_routing,
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
