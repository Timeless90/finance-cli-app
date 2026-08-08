from __future__ import annotations

from dataclasses import dataclass

from cfo_platform.action_management import (
    ActionCatalogueService,
    ActionPortfolioPrioritizer,
    ActionReviewService,
    ActionSimulationEngine,
    BenefitTrackingService,
    InMemoryActionRepository,
)
from cfo_platform.ai_foundry import (
    FinanceCopilotService,
    InMemoryAIInteractionRepository,
    ModelRoutingTable,
    build_foundry_gateway,
)
from cfo_platform.application.services import ExecuteModelRun
from cfo_platform.capital_allocation import (
    CapitalPortfolioOptimizer,
    FundingScenarioEngine,
    MonteCarloNpvEngine,
    ProjectValuationService,
)
from cfo_platform.data_store import InMemoryDataSnapshotRepository
from cfo_platform.data_workflow import FinanceDataWorkflow
from cfo_platform.forecast_backtesting import RollingOriginBacktester
from cfo_platform.forecast_thresholds import GoalThresholdEngine
from cfo_platform.governance import (
    GovernedRunService,
    InMemoryAuditEventRepository,
    InMemoryGovernedRunRepository,
)
from cfo_platform.governance_catalog import (
    InMemoryModelRegistryRepository,
    InMemoryScenarioRepository,
    ModelRegistryService,
    ScenarioService,
)
from cfo_platform.infrastructure.in_memory import (
    InMemoryModelRunRepository,
    RegisteredModelExecutor,
)
from cfo_platform.infrastructure.jobs import InMemoryJobManager
from cfo_platform.liquidity_management import (
    CashForecastAccuracyService,
    CovenantEngine,
    DebtScheduleEngine,
    LiquidityStressEngine,
    MonthlyLiquidityForecast,
    ThirteenWeekCashForecast,
    WorkingCapitalModel,
)
from cfo_platform.market_treasury_risk import (
    CopulaDependenceModel,
    EvtTailOverlay,
    ExposureManagementService,
    GaussianHmmRegimeModel,
    GarchTModel,
    HedgeScenarioEngine,
    MarketRiskMetrics,
    SensitivityEngine,
    VarBacktester,
)
from cfo_platform.performance_management import (
    AnomalyDetectionService,
    ForecastAccuracyService,
    ManagementCommentaryService,
    VarianceAnalysisEngine,
)
from cfo_platform.planning_workflow import (
    InMemoryRollingForecastRepository,
    RollingForecastService,
)
from cfo_platform.probabilistic_forecast import ProbabilisticForecastEngine
from cfo_platform.profitability_management import (
    ActivityBasedCostingService,
    CostAllocationService,
    MarginAtRiskService,
    MarginSensitivityService,
    ProfitabilityReconciliationService,
    ProfitabilityService,
)
from cfo_platform.quant.builtin import EchoForecastModel
from cfo_platform.quant.legacy_portfolio import LegacyPortfolioSimulationModel
from cfo_platform.quant.registry import QuantModelRegistry
from cfo_platform.rbac import AccessControlService
from cfo_platform.reporting_factory import (
    InMemoryReportRepository,
    ReportExporter,
    ReportingFactory,
    TemplateRegistry,
    built_in_templates,
)
from cfo_platform.risk_management import (
    InMemoryRiskRegister,
    RiskAggregationEngine,
    RiskAppetiteEngine,
    RiskQuantificationEngine,
    RiskRegisterService,
    RiskReportingService,
    RiskToPlanEngine,
)
from cfo_platform.workspace_integration import (
    ContextCatalogService,
    InMemoryWorkspaceReadModelRepository,
    WorkspaceReadModelService,
)


@dataclass(slots=True)
class ApplicationContainer:
    model_registry: QuantModelRegistry
    run_repository: InMemoryModelRunRepository
    model_executor: RegisteredModelExecutor
    execute_model_run: ExecuteModelRun
    job_manager: InMemoryJobManager
    data_snapshot_repository: InMemoryDataSnapshotRepository
    finance_data_workflow: FinanceDataWorkflow
    governed_run_service: GovernedRunService
    scenario_service: ScenarioService
    model_registry_service: ModelRegistryService
    access_control: AccessControlService
    context_catalog_service: ContextCatalogService
    workspace_read_model_service: WorkspaceReadModelService
    rolling_forecast_service: RollingForecastService
    probabilistic_forecast_engine: ProbabilisticForecastEngine
    rolling_origin_backtester: RollingOriginBacktester
    goal_threshold_engine: GoalThresholdEngine
    variance_analysis_engine: VarianceAnalysisEngine
    forecast_accuracy_service: ForecastAccuracyService
    anomaly_detection_service: AnomalyDetectionService
    management_commentary_service: ManagementCommentaryService
    profitability_service: ProfitabilityService
    cost_allocation_service: CostAllocationService
    activity_based_costing_service: ActivityBasedCostingService
    profitability_reconciliation_service: ProfitabilityReconciliationService
    margin_sensitivity_service: MarginSensitivityService
    margin_at_risk_service: MarginAtRiskService
    thirteen_week_cash_forecast: ThirteenWeekCashForecast
    monthly_liquidity_forecast: MonthlyLiquidityForecast
    working_capital_model: WorkingCapitalModel
    debt_schedule_engine: DebtScheduleEngine
    covenant_engine: CovenantEngine
    liquidity_stress_engine: LiquidityStressEngine
    cash_forecast_accuracy_service: CashForecastAccuracyService
    exposure_management_service: ExposureManagementService
    market_sensitivity_engine: SensitivityEngine
    market_risk_metrics: MarketRiskMetrics
    garch_t_model: GarchTModel
    regime_hmm_model: GaussianHmmRegimeModel
    evt_tail_overlay: EvtTailOverlay
    copula_dependence_model: CopulaDependenceModel
    hedge_scenario_engine: HedgeScenarioEngine
    var_backtester: VarBacktester
    risk_register_service: RiskRegisterService
    risk_quantification_engine: RiskQuantificationEngine
    risk_aggregation_engine: RiskAggregationEngine
    risk_appetite_engine: RiskAppetiteEngine
    risk_to_plan_engine: RiskToPlanEngine
    risk_reporting_service: RiskReportingService
    action_catalogue_service: ActionCatalogueService
    action_simulation_engine: ActionSimulationEngine
    action_portfolio_prioritizer: ActionPortfolioPrioritizer
    action_review_service: ActionReviewService
    benefit_tracking_service: BenefitTrackingService
    reporting_factory: ReportingFactory
    report_exporter: ReportExporter
    ai_model_routing: ModelRoutingTable
    ai_interaction_repository: InMemoryAIInteractionRepository
    finance_copilot_service: FinanceCopilotService
    project_valuation_service: ProjectValuationService
    monte_carlo_npv_engine: MonteCarloNpvEngine
    capital_portfolio_optimizer: CapitalPortfolioOptimizer
    funding_scenario_engine: FundingScenarioEngine

    def shutdown(self) -> None:
        self.job_manager.shutdown()


def build_container() -> ApplicationContainer:
    registry = QuantModelRegistry([EchoForecastModel(), LegacyPortfolioSimulationModel()])
    repository = InMemoryModelRunRepository()
    executor = RegisteredModelExecutor(registry)
    service = ExecuteModelRun(executor, repository)
    jobs = InMemoryJobManager(service)
    snapshot_repository = InMemoryDataSnapshotRepository()
    data_workflow = FinanceDataWorkflow(snapshot_repository)
    governed_runs = GovernedRunService(
        InMemoryGovernedRunRepository(),
        InMemoryAuditEventRepository(),
    )
    scenario_repository = InMemoryScenarioRepository()
    scenario_service = ScenarioService(scenario_repository)
    model_registry_service = ModelRegistryService(InMemoryModelRegistryRepository())
    access_control = AccessControlService()
    context_catalog_service = ContextCatalogService(
        snapshot_repository,
        scenario_repository,
        access_control,
    )
    workspace_read_model_service = WorkspaceReadModelService(
        context_catalog_service,
        InMemoryWorkspaceReadModelRepository(),
    )
    rolling_forecast_service = RollingForecastService(InMemoryRollingForecastRepository())
    risk_quantification = RiskQuantificationEngine()
    action_catalogue = ActionCatalogueService(InMemoryActionRepository())
    reporting_factory = ReportingFactory(
        TemplateRegistry(built_in_templates()),
        InMemoryReportRepository(),
    )
    ai_model_routing = ModelRoutingTable.from_environment()
    ai_interactions = InMemoryAIInteractionRepository()
    finance_copilot_service = FinanceCopilotService(
        ai_model_routing,
        build_foundry_gateway(),
        ai_interactions,
        access_control,
    )
    return ApplicationContainer(
        model_registry=registry,
        run_repository=repository,
        model_executor=executor,
        execute_model_run=service,
        job_manager=jobs,
        data_snapshot_repository=snapshot_repository,
        finance_data_workflow=data_workflow,
        governed_run_service=governed_runs,
        scenario_service=scenario_service,
        model_registry_service=model_registry_service,
        access_control=access_control,
        context_catalog_service=context_catalog_service,
        workspace_read_model_service=workspace_read_model_service,
        rolling_forecast_service=rolling_forecast_service,
        probabilistic_forecast_engine=ProbabilisticForecastEngine(),
        rolling_origin_backtester=RollingOriginBacktester(),
        goal_threshold_engine=GoalThresholdEngine(),
        variance_analysis_engine=VarianceAnalysisEngine(),
        forecast_accuracy_service=ForecastAccuracyService(),
        anomaly_detection_service=AnomalyDetectionService(),
        management_commentary_service=ManagementCommentaryService(),
        profitability_service=ProfitabilityService(),
        cost_allocation_service=CostAllocationService(),
        activity_based_costing_service=ActivityBasedCostingService(),
        profitability_reconciliation_service=ProfitabilityReconciliationService(),
        margin_sensitivity_service=MarginSensitivityService(),
        margin_at_risk_service=MarginAtRiskService(),
        thirteen_week_cash_forecast=ThirteenWeekCashForecast(),
        monthly_liquidity_forecast=MonthlyLiquidityForecast(),
        working_capital_model=WorkingCapitalModel(),
        debt_schedule_engine=DebtScheduleEngine(),
        covenant_engine=CovenantEngine(),
        liquidity_stress_engine=LiquidityStressEngine(),
        cash_forecast_accuracy_service=CashForecastAccuracyService(),
        exposure_management_service=ExposureManagementService(),
        market_sensitivity_engine=SensitivityEngine(),
        market_risk_metrics=MarketRiskMetrics(),
        garch_t_model=GarchTModel(),
        regime_hmm_model=GaussianHmmRegimeModel(),
        evt_tail_overlay=EvtTailOverlay(),
        copula_dependence_model=CopulaDependenceModel(),
        hedge_scenario_engine=HedgeScenarioEngine(),
        var_backtester=VarBacktester(),
        risk_register_service=RiskRegisterService(InMemoryRiskRegister()),
        risk_quantification_engine=risk_quantification,
        risk_aggregation_engine=RiskAggregationEngine(risk_quantification),
        risk_appetite_engine=RiskAppetiteEngine(),
        risk_to_plan_engine=RiskToPlanEngine(),
        risk_reporting_service=RiskReportingService(risk_quantification),
        action_catalogue_service=action_catalogue,
        action_simulation_engine=ActionSimulationEngine(),
        action_portfolio_prioritizer=ActionPortfolioPrioritizer(),
        action_review_service=ActionReviewService(),
        benefit_tracking_service=BenefitTrackingService(),
        reporting_factory=reporting_factory,
        report_exporter=ReportExporter(),
        ai_model_routing=ai_model_routing,
        ai_interaction_repository=ai_interactions,
        finance_copilot_service=finance_copilot_service,
        project_valuation_service=ProjectValuationService(),
        monte_carlo_npv_engine=MonteCarloNpvEngine(),
        capital_portfolio_optimizer=CapitalPortfolioOptimizer(),
        funding_scenario_engine=FundingScenarioEngine(),
    )
