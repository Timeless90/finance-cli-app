from __future__ import annotations

from dataclasses import dataclass

from cfo_platform.application.services import ExecuteModelRun
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
from cfo_platform.risk_management import (
    InMemoryRiskRegister,
    RiskAggregationEngine,
    RiskAppetiteEngine,
    RiskQuantificationEngine,
    RiskRegisterService,
    RiskReportingService,
    RiskToPlanEngine,
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
    risk_register_service: RiskRegisterService
    risk_quantification_engine: RiskQuantificationEngine
    risk_aggregation_engine: RiskAggregationEngine
    risk_appetite_engine: RiskAppetiteEngine
    risk_to_plan_engine: RiskToPlanEngine
    risk_reporting_service: RiskReportingService

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
    scenario_service = ScenarioService(InMemoryScenarioRepository())
    model_registry_service = ModelRegistryService(InMemoryModelRegistryRepository())
    rolling_forecast_service = RollingForecastService(InMemoryRollingForecastRepository())
    risk_quantification = RiskQuantificationEngine()
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
        access_control=AccessControlService(),
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
        risk_register_service=RiskRegisterService(InMemoryRiskRegister()),
        risk_quantification_engine=risk_quantification,
        risk_aggregation_engine=RiskAggregationEngine(risk_quantification),
        risk_appetite_engine=RiskAppetiteEngine(),
        risk_to_plan_engine=RiskToPlanEngine(),
        risk_reporting_service=RiskReportingService(risk_quantification),
    )
