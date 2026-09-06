from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.actions.action_management import (
    ActionCatalogueService,
    ActionPortfolioPrioritizer,
    ActionReviewService,
    ActionSimulationEngine,
    BenefitTrackingService,
    InMemoryActionRepository,
    InMemoryBenefitTrackingCatalog,
)
from app.capital.capital_allocation import (
    CapitalPortfolioOptimizer,
    FundingScenarioEngine,
    InMemoryCapitalCandidateCatalog,
    MonteCarloNpvEngine,
    ProjectValuationService,
)
from app.copilot.ai_foundry import (
    FinanceCopilotService,
    InMemoryAIInteractionRepository,
    ModelRoutingTable,
    build_foundry_gateway,
)
from app.data.data_publication import (
    FinanceImportPublicationService,
    InMemoryFinanceImportRepository,
    LocalImportObjectStore,
    PostgresFinanceImportRepository,
)
from app.data.data_store import (
    InMemoryDataSnapshotRepository,
    PostgresDataSnapshotRepository,
)
from app.data.data_workflow import FinanceDataWorkflow
from app.decisions.decision_workflow import (
    DecisionRunService,
    InMemoryDecisionRunRepository,
)
from app.governance.governance import (
    GovernedRunService,
    InMemoryAuditEventRepository,
    InMemoryGovernedRunRepository,
)
from app.governance.governance_catalog import (
    InMemoryModelRegistryRepository,
    InMemoryScenarioRepository,
    ModelRegistryService,
    ScenarioService,
)
from app.governance.governance_persistence import (
    PostgresAuditEventRepository,
    PostgresGovernedRunRepository,
    SqliteAuditEventRepository,
    SqliteGovernedRunRepository,
)
from app.liquidity.liquidity_management import (
    CashForecastAccuracyService,
    CovenantEngine,
    DebtScheduleEngine,
    LiquidityStressEngine,
    MonthlyLiquidityForecast,
    ThirteenWeekCashForecast,
    WorkingCapitalModel,
)
from app.market_risk.market_treasury_risk import (
    CopulaDependenceModel,
    EvtTailOverlay,
    ExposureManagementService,
    GarchTModel,
    GaussianHmmRegimeModel,
    HedgeScenarioEngine,
    MarketRiskMetrics,
    SensitivityEngine,
    VarBacktester,
)
from app.performance.performance_management import (
    AnomalyDetectionService,
    ForecastAccuracyService,
    ManagementCommentaryService,
    VarianceAnalysisEngine,
)
from app.planning.forecast_backtesting import RollingOriginBacktester
from app.planning.forecast_thresholds import GoalThresholdEngine
from app.planning.planning_baseline import (
    InMemoryPlanningBaselineRepository,
    PlanningBaselineService,
    PostgresPlanningBaselineRepository,
)
from app.planning.planning_workflow import (
    InMemoryRollingForecastRepository,
    RollingForecastService,
)
from app.planning.probabilistic_forecast import ProbabilisticForecastEngine
from app.profitability.profitability_management import (
    ActivityBasedCostingService,
    CostAllocationService,
    MarginAtRiskService,
    MarginSensitivityService,
    ProfitabilityReconciliationService,
    ProfitabilityService,
)
from app.reporting.report_workflow import (
    InMemoryReportRunRepository,
    ReportRunService,
)
from app.reporting.reporting_factory import (
    InMemoryReportRepository,
    ReportExporter,
    ReportingFactory,
    TemplateRegistry,
    built_in_templates,
)
from app.risk.risk_management import (
    InMemoryRiskRegister,
    RiskAggregationEngine,
    RiskAppetiteEngine,
    RiskQuantificationEngine,
    RiskRegisterService,
    RiskReportingService,
    RiskToPlanEngine,
)
from app.shared.application.services import ExecuteModelRun
from app.shared.infrastructure.in_memory import (
    InMemoryModelRunRepository,
    RegisteredModelExecutor,
)
from app.shared.infrastructure.jobs import InMemoryJobManager
from app.shared.quant.builtin import EchoForecastModel
from app.shared.quant.legacy_portfolio import LegacyPortfolioSimulationModel
from app.shared.quant.registry import QuantModelRegistry
from app.shared.rbac import AccessControlService
from app.workspace.workspace_integration import (
    ContextCatalogService,
    InMemoryWorkspaceReadModelRepository,
    WorkspaceReadModelService,
)
from app.workspace.workspace_persistence import PostgresWorkspaceReadModelRepository


@dataclass(slots=True)
class ApplicationContainer:
    model_registry: QuantModelRegistry
    run_repository: InMemoryModelRunRepository
    model_executor: RegisteredModelExecutor
    execute_model_run: ExecuteModelRun
    job_manager: InMemoryJobManager
    data_snapshot_repository: (
        InMemoryDataSnapshotRepository | PostgresDataSnapshotRepository
    )
    finance_data_workflow: FinanceDataWorkflow
    finance_import_publication_service: FinanceImportPublicationService
    planning_baseline_service: PlanningBaselineService
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
    benefit_tracking_catalog: InMemoryBenefitTrackingCatalog
    reporting_factory: ReportingFactory
    report_exporter: ReportExporter
    report_run_service: ReportRunService
    ai_model_routing: ModelRoutingTable
    ai_interaction_repository: InMemoryAIInteractionRepository
    finance_copilot_service: FinanceCopilotService
    project_valuation_service: ProjectValuationService
    monte_carlo_npv_engine: MonteCarloNpvEngine
    capital_portfolio_optimizer: CapitalPortfolioOptimizer
    funding_scenario_engine: FundingScenarioEngine
    capital_candidate_catalog: InMemoryCapitalCandidateCatalog
    decision_run_service: DecisionRunService

    def shutdown(self) -> None:
        self.job_manager.shutdown()


def build_container(
    *,
    governance_database_path: Path | None = None,
    governance_database_url: str | None = None,
    import_storage_path: Path = Path(".local/imports"),
) -> ApplicationContainer:
    registry = QuantModelRegistry(
        [EchoForecastModel(), LegacyPortfolioSimulationModel()]
    )
    repository = InMemoryModelRunRepository()
    executor = RegisteredModelExecutor(registry)
    service = ExecuteModelRun(executor, repository)
    jobs = InMemoryJobManager(service)
    snapshot_repository = (
        PostgresDataSnapshotRepository(governance_database_url)
        if governance_database_url is not None
        else InMemoryDataSnapshotRepository()
    )
    data_workflow = FinanceDataWorkflow(snapshot_repository)
    if governance_database_url is not None:
        governed_run_repository = PostgresGovernedRunRepository(governance_database_url)
        audit_event_repository = PostgresAuditEventRepository(governance_database_url)
    elif governance_database_path is None:
        governed_run_repository = InMemoryGovernedRunRepository()
        audit_event_repository = InMemoryAuditEventRepository()
    else:
        governed_run_repository = SqliteGovernedRunRepository(governance_database_path)
        audit_event_repository = SqliteAuditEventRepository(governance_database_path)
    governed_runs = GovernedRunService(governed_run_repository, audit_event_repository)
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
        PostgresWorkspaceReadModelRepository(governance_database_url)
        if governance_database_url is not None
        else InMemoryWorkspaceReadModelRepository(),
    )
    finance_import_repository = (
        PostgresFinanceImportRepository(governance_database_url)
        if governance_database_url is not None
        else InMemoryFinanceImportRepository()
    )
    finance_import_publication_service = FinanceImportPublicationService(
        data_workflow,
        finance_import_repository,
        LocalImportObjectStore(import_storage_path),
        access_control,
        workspace_read_model_service,
    )
    planning_baseline_service = PlanningBaselineService(
        snapshot_repository,
        finance_import_repository,
        PostgresPlanningBaselineRepository(governance_database_url)
        if governance_database_url is not None
        else InMemoryPlanningBaselineRepository(),
        access_control,
    )
    rolling_forecast_service = RollingForecastService(
        InMemoryRollingForecastRepository()
    )
    risk_quantification = RiskQuantificationEngine()
    action_catalogue = ActionCatalogueService(InMemoryActionRepository())
    benefit_tracking_catalog = InMemoryBenefitTrackingCatalog()
    capital_candidate_catalog = InMemoryCapitalCandidateCatalog()
    decision_run_service = DecisionRunService(
        context_catalog_service,
        snapshot_repository,
        access_control,
        InMemoryDecisionRunRepository(),
    )
    reporting_factory = ReportingFactory(
        TemplateRegistry(built_in_templates()),
        InMemoryReportRepository(),
    )
    report_run_service = ReportRunService(
        context_catalog_service,
        snapshot_repository,
        access_control,
        reporting_factory,
        InMemoryReportRunRepository(),
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
        finance_import_publication_service=finance_import_publication_service,
        planning_baseline_service=planning_baseline_service,
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
        benefit_tracking_catalog=benefit_tracking_catalog,
        reporting_factory=reporting_factory,
        report_exporter=ReportExporter(),
        report_run_service=report_run_service,
        ai_model_routing=ai_model_routing,
        ai_interaction_repository=ai_interactions,
        finance_copilot_service=finance_copilot_service,
        project_valuation_service=ProjectValuationService(),
        monte_carlo_npv_engine=MonteCarloNpvEngine(),
        capital_portfolio_optimizer=CapitalPortfolioOptimizer(),
        funding_scenario_engine=FundingScenarioEngine(),
        capital_candidate_catalog=capital_candidate_catalog,
        decision_run_service=decision_run_service,
    )
