// Generated from OpenAPI and Orval. Do not edit.
import * as operations from './api';
import type { ClientOptions } from '../shared/api/client';
export const dispatch = {
  'GET /api/v1/actions': (options: ClientOptions) =>
    operations.listActionsApiV1ActionsGet(options.request),
  'POST /api/v1/actions/benefits/track': (options: ClientOptions) =>
    operations.trackBenefitsApiV1ActionsBenefitsTrackPost(
      options.body as Parameters<
        typeof operations.trackBenefitsApiV1ActionsBenefitsTrackPost
      >[0],
      options.request,
    ),
  'POST /api/v1/actions/portfolio/prioritize': (options: ClientOptions) =>
    operations.prioritizeActionsApiV1ActionsPortfolioPrioritizePost(
      options.body as Parameters<
        typeof operations.prioritizeActionsApiV1ActionsPortfolioPrioritizePost
      >[0],
      options.request,
    ),
  'POST /api/v1/actions/register': (options: ClientOptions) =>
    operations.registerActionApiV1ActionsRegisterPost(
      options.body as Parameters<
        typeof operations.registerActionApiV1ActionsRegisterPost
      >[0],
      options.request,
    ),
  'POST /api/v1/actions/runs': (options: ClientOptions) =>
    operations.createActionRunApiV1ActionsRunsPost(
      options.body as Parameters<
        typeof operations.createActionRunApiV1ActionsRunsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/actions/runs/benefit-tracking': (options: ClientOptions) =>
    operations.createActionBenefitTrackingRunApiV1ActionsRunsBenefitTrackingPost(
      options.body as Parameters<
        typeof operations.createActionBenefitTrackingRunApiV1ActionsRunsBenefitTrackingPost
      >[0],
      options.request,
    ),
  'POST /api/v1/actions/simulate': (options: ClientOptions) =>
    operations.simulateActionsApiV1ActionsSimulatePost(
      options.body as Parameters<
        typeof operations.simulateActionsApiV1ActionsSimulatePost
      >[0],
      options.request,
    ),
  'GET /api/v1/actions/workspace': (options: ClientOptions) =>
    operations.actionsWorkspaceApiV1ActionsWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.actionsWorkspaceApiV1ActionsWorkspaceGet
      >[0],
      options.request,
    ),
  'GET /api/v1/actions/{action_id}': (options: ClientOptions) =>
    operations.getActionApiV1ActionsActionIdGet(
      String(options.params?.path?.['action_id']) as Parameters<
        typeof operations.getActionApiV1ActionsActionIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/actions/{action_id}/review': (options: ClientOptions) =>
    operations.reviewActionApiV1ActionsActionIdReviewPost(
      String(options.params?.path?.['action_id']) as Parameters<
        typeof operations.reviewActionApiV1ActionsActionIdReviewPost
      >[0],
      options.body as Parameters<
        typeof operations.reviewActionApiV1ActionsActionIdReviewPost
      >[1],
      options.request,
    ),
  'POST /api/v1/actions/{action_id}/status': (options: ClientOptions) =>
    operations.changeStatusApiV1ActionsActionIdStatusPost(
      String(options.params?.path?.['action_id']) as Parameters<
        typeof operations.changeStatusApiV1ActionsActionIdStatusPost
      >[0],
      options.body as Parameters<
        typeof operations.changeStatusApiV1ActionsActionIdStatusPost
      >[1],
      options.request,
    ),
  'POST /api/v1/capital/funding/evaluate': (options: ClientOptions) =>
    operations.evaluateFundingApiV1CapitalFundingEvaluatePost(
      options.body as Parameters<
        typeof operations.evaluateFundingApiV1CapitalFundingEvaluatePost
      >[0],
      options.request,
    ),
  'POST /api/v1/capital/portfolio/optimize': (options: ClientOptions) =>
    operations.optimizePortfolioApiV1CapitalPortfolioOptimizePost(
      options.body as Parameters<
        typeof operations.optimizePortfolioApiV1CapitalPortfolioOptimizePost
      >[0],
      options.request,
    ),
  'POST /api/v1/capital/projects/monte-carlo': (options: ClientOptions) =>
    operations.monteCarloApiV1CapitalProjectsMonteCarloPost(
      options.body as Parameters<
        typeof operations.monteCarloApiV1CapitalProjectsMonteCarloPost
      >[0],
      options.request,
    ),
  'POST /api/v1/capital/projects/value': (options: ClientOptions) =>
    operations.valueProjectApiV1CapitalProjectsValuePost(
      options.body as Parameters<
        typeof operations.valueProjectApiV1CapitalProjectsValuePost
      >[0],
      options.request,
    ),
  'POST /api/v1/capital/runs/allocation': (options: ClientOptions) =>
    operations.createCapitalAllocationRunApiV1CapitalRunsAllocationPost(
      options.body as Parameters<
        typeof operations.createCapitalAllocationRunApiV1CapitalRunsAllocationPost
      >[0],
      options.request,
    ),
  'POST /api/v1/capital/runs/funding': (options: ClientOptions) =>
    operations.createFundingScenarioRunApiV1CapitalRunsFundingPost(
      options.body as Parameters<
        typeof operations.createFundingScenarioRunApiV1CapitalRunsFundingPost
      >[0],
      options.request,
    ),
  'POST /api/v1/capital/runs/monte-carlo-npv': (options: ClientOptions) =>
    operations.createCapitalMonteCarloRunApiV1CapitalRunsMonteCarloNpvPost(
      options.body as Parameters<
        typeof operations.createCapitalMonteCarloRunApiV1CapitalRunsMonteCarloNpvPost
      >[0],
      options.request,
    ),
  'POST /api/v1/capital/runs/valuation': (options: ClientOptions) =>
    operations.createCapitalValuationRunApiV1CapitalRunsValuationPost(
      options.body as Parameters<
        typeof operations.createCapitalValuationRunApiV1CapitalRunsValuationPost
      >[0],
      options.request,
    ),
  'GET /api/v1/capital/workspace': (options: ClientOptions) =>
    operations.capitalWorkspaceApiV1CapitalWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.capitalWorkspaceApiV1CapitalWorkspaceGet
      >[0],
      options.request,
    ),
  'GET /api/v1/command-center/overview': (options: ClientOptions) =>
    operations.commandCenterOverviewApiV1CommandCenterOverviewGet(
      options.params?.query as Parameters<
        typeof operations.commandCenterOverviewApiV1CommandCenterOverviewGet
      >[0],
      options.request,
    ),
  'GET /api/v1/context/companies': (options: ClientOptions) =>
    operations.listCompaniesApiV1ContextCompaniesGet(options.request),
  'GET /api/v1/context/periods': (options: ClientOptions) =>
    operations.listPeriodsApiV1ContextPeriodsGet(
      options.params?.query as Parameters<
        typeof operations.listPeriodsApiV1ContextPeriodsGet
      >[0],
      options.request,
    ),
  'GET /api/v1/context/principal': (options: ClientOptions) =>
    operations.getPrincipalApiV1ContextPrincipalGet(options.request),
  'GET /api/v1/context/resolve': (options: ClientOptions) =>
    operations.resolveContextApiV1ContextResolveGet(
      options.params?.query as Parameters<
        typeof operations.resolveContextApiV1ContextResolveGet
      >[0],
      options.request,
    ),
  'GET /api/v1/context/scenarios': (options: ClientOptions) =>
    operations.listScenariosApiV1ContextScenariosGet(
      options.params?.query as Parameters<
        typeof operations.listScenariosApiV1ContextScenariosGet
      >[0],
      options.request,
    ),
  'GET /api/v1/copilot/routes': (options: ClientOptions) =>
    operations.listRoutesApiV1CopilotRoutesGet(options.request),
  'GET /api/v1/copilot/routes/resolve': (options: ClientOptions) =>
    operations.resolveRouteApiV1CopilotRoutesResolveGet(
      options.params?.query as Parameters<
        typeof operations.resolveRouteApiV1CopilotRoutesResolveGet
      >[0],
      options.request,
    ),
  'POST /api/v1/copilot/sessions': (options: ClientOptions) =>
    operations.createSessionApiV1CopilotSessionsPost(
      options.body as Parameters<
        typeof operations.createSessionApiV1CopilotSessionsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/copilot/sessions/{session_id}/messages': (options: ClientOptions) =>
    operations.sendMessageApiV1CopilotSessionsSessionIdMessagesPost(
      String(options.params?.path?.['session_id']) as Parameters<
        typeof operations.sendMessageApiV1CopilotSessionsSessionIdMessagesPost
      >[0],
      options.body as Parameters<
        typeof operations.sendMessageApiV1CopilotSessionsSessionIdMessagesPost
      >[1],
      options.request,
    ),
  'GET /api/v1/data': (options: ClientOptions) =>
    operations.dataFoundationApiV1DataGet(options.request),
  'GET /api/v1/data-governance/workspace': (options: ClientOptions) =>
    operations.dataGovernanceWorkspaceApiV1DataGovernanceWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.dataGovernanceWorkspaceApiV1DataGovernanceWorkspaceGet
      >[0],
      options.request,
    ),
  'GET /api/v1/data/imports': (options: ClientOptions) =>
    operations.listImportsApiV1DataImportsGet(options.request),
  'POST /api/v1/data/imports': (options: ClientOptions) =>
    operations.importFinanceDataApiV1DataImportsPost(
      options.body as Parameters<
        typeof operations.importFinanceDataApiV1DataImportsPost
      >[0],
      options.request,
    ),
  'GET /api/v1/data/imports/{import_id}/accounts': (options: ClientOptions) =>
    operations.listSourceAccountsApiV1DataImportsImportIdAccountsGet(
      String(options.params?.path?.['import_id']) as Parameters<
        typeof operations.listSourceAccountsApiV1DataImportsImportIdAccountsGet
      >[0],
      options.request,
    ),
  'POST /api/v1/data/imports/{import_id}/approve': (options: ClientOptions) =>
    operations.approveImportApiV1DataImportsImportIdApprovePost(
      String(options.params?.path?.['import_id']) as Parameters<
        typeof operations.approveImportApiV1DataImportsImportIdApprovePost
      >[0],
      options.body as Parameters<
        typeof operations.approveImportApiV1DataImportsImportIdApprovePost
      >[1],
      options.request,
    ),
  'POST /api/v1/data/imports/{import_id}/publish': (options: ClientOptions) =>
    operations.publishImportApiV1DataImportsImportIdPublishPost(
      String(options.params?.path?.['import_id']) as Parameters<
        typeof operations.publishImportApiV1DataImportsImportIdPublishPost
      >[0],
      options.request,
    ),
  'POST /api/v1/data/imports/{import_id}/review': (options: ClientOptions) =>
    operations.reviewImportApiV1DataImportsImportIdReviewPost(
      String(options.params?.path?.['import_id']) as Parameters<
        typeof operations.reviewImportApiV1DataImportsImportIdReviewPost
      >[0],
      options.body as Parameters<
        typeof operations.reviewImportApiV1DataImportsImportIdReviewPost
      >[1],
      options.request,
    ),
  'GET /api/v1/data/imports/{import_id}/source': (options: ClientOptions) =>
    operations.downloadSourceApiV1DataImportsImportIdSourceGet(
      String(options.params?.path?.['import_id']) as Parameters<
        typeof operations.downloadSourceApiV1DataImportsImportIdSourceGet
      >[0],
      options.request,
    ),
  'GET /api/v1/data/planning-baselines': (options: ClientOptions) =>
    operations.listPlanningBaselinesApiV1DataPlanningBaselinesGet(
      options.params?.query as Parameters<
        typeof operations.listPlanningBaselinesApiV1DataPlanningBaselinesGet
      >[0],
      options.request,
    ),
  'POST /api/v1/data/planning-baselines': (options: ClientOptions) =>
    operations.publishPlanningBaselineApiV1DataPlanningBaselinesPost(
      options.body as Parameters<
        typeof operations.publishPlanningBaselineApiV1DataPlanningBaselinesPost
      >[0],
      options.request,
    ),
  'GET /api/v1/data/planning-mappings': (options: ClientOptions) =>
    operations.listPlanningMappingsApiV1DataPlanningMappingsGet(
      options.params?.query as Parameters<
        typeof operations.listPlanningMappingsApiV1DataPlanningMappingsGet
      >[0],
      options.request,
    ),
  'POST /api/v1/data/planning-mappings': (options: ClientOptions) =>
    operations.createPlanningMappingApiV1DataPlanningMappingsPost(
      options.body as Parameters<
        typeof operations.createPlanningMappingApiV1DataPlanningMappingsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/data/planning-mappings/{mapping_set_id}/approve': (
    options: ClientOptions,
  ) =>
    operations.approvePlanningMappingApiV1DataPlanningMappingsMappingSetIdApprovePost(
      String(options.params?.path?.['mapping_set_id']) as Parameters<
        typeof operations.approvePlanningMappingApiV1DataPlanningMappingsMappingSetIdApprovePost
      >[0],
      options.body as Parameters<
        typeof operations.approvePlanningMappingApiV1DataPlanningMappingsMappingSetIdApprovePost
      >[1],
      options.request,
    ),
  'POST /api/v1/data/planning-mappings/{mapping_set_id}/review': (
    options: ClientOptions,
  ) =>
    operations.reviewPlanningMappingApiV1DataPlanningMappingsMappingSetIdReviewPost(
      String(options.params?.path?.['mapping_set_id']) as Parameters<
        typeof operations.reviewPlanningMappingApiV1DataPlanningMappingsMappingSetIdReviewPost
      >[0],
      options.body as Parameters<
        typeof operations.reviewPlanningMappingApiV1DataPlanningMappingsMappingSetIdReviewPost
      >[1],
      options.request,
    ),
  'GET /api/v1/data/snapshots/{snapshot_id}': (options: ClientOptions) =>
    operations.getSnapshotApiV1DataSnapshotsSnapshotIdGet(
      String(options.params?.path?.['snapshot_id']) as Parameters<
        typeof operations.getSnapshotApiV1DataSnapshotsSnapshotIdGet
      >[0],
      options.request,
    ),
  'GET /api/v1/decision-runs': (options: ClientOptions) =>
    operations.listDecisionRunsApiV1DecisionRunsGet(
      options.params?.query as Parameters<
        typeof operations.listDecisionRunsApiV1DecisionRunsGet
      >[0],
      options.request,
    ),
  'GET /api/v1/decision-runs/{run_id}': (options: ClientOptions) =>
    operations.getDecisionRunApiV1DecisionRunsRunIdGet(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.getDecisionRunApiV1DecisionRunsRunIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/decision-runs/{run_id}/approve': (options: ClientOptions) =>
    operations.approveDecisionRunApiV1DecisionRunsRunIdApprovePost(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.approveDecisionRunApiV1DecisionRunsRunIdApprovePost
      >[0],
      options.request,
    ),
  'GET /api/v1/decision-runs/{run_id}/events': (options: ClientOptions) =>
    operations.decisionRunEventsApiV1DecisionRunsRunIdEventsGet(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.decisionRunEventsApiV1DecisionRunsRunIdEventsGet
      >[0],
      options.request,
    ),
  'POST /api/v1/decision-runs/{run_id}/reject': (options: ClientOptions) =>
    operations.rejectDecisionRunApiV1DecisionRunsRunIdRejectPost(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.rejectDecisionRunApiV1DecisionRunsRunIdRejectPost
      >[0],
      options.body as Parameters<
        typeof operations.rejectDecisionRunApiV1DecisionRunsRunIdRejectPost
      >[1],
      options.request,
    ),
  'POST /api/v1/decision-runs/{run_id}/validate': (options: ClientOptions) =>
    operations.validateDecisionRunApiV1DecisionRunsRunIdValidatePost(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.validateDecisionRunApiV1DecisionRunsRunIdValidatePost
      >[0],
      options.request,
    ),
  'GET /api/v1/forecast': (options: ClientOptions) =>
    operations.forecastFoundationApiV1ForecastGet(options.request),
  'POST /api/v1/governance/models': (options: ClientOptions) =>
    operations.registerModelApiV1GovernanceModelsPost(
      options.body as Parameters<
        typeof operations.registerModelApiV1GovernanceModelsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/governance/runs': (options: ClientOptions) =>
    operations.createRunApiV1GovernanceRunsPost(
      options.body as Parameters<typeof operations.createRunApiV1GovernanceRunsPost>[0],
      options.request,
    ),
  'POST /api/v1/governance/runs/{run_id}/approve': (options: ClientOptions) =>
    operations.approveRunApiV1GovernanceRunsRunIdApprovePost(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.approveRunApiV1GovernanceRunsRunIdApprovePost
      >[0],
      options.request,
    ),
  'GET /api/v1/governance/runs/{run_id}/lineage': (options: ClientOptions) =>
    operations.lineageApiV1GovernanceRunsRunIdLineageGet(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.lineageApiV1GovernanceRunsRunIdLineageGet
      >[0],
      options.request,
    ),
  'POST /api/v1/governance/runs/{run_id}/retire': (options: ClientOptions) =>
    operations.retireRunApiV1GovernanceRunsRunIdRetirePost(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.retireRunApiV1GovernanceRunsRunIdRetirePost
      >[0],
      options.body as Parameters<
        typeof operations.retireRunApiV1GovernanceRunsRunIdRetirePost
      >[1],
      options.request,
    ),
  'POST /api/v1/governance/runs/{run_id}/validate': (options: ClientOptions) =>
    operations.validateRunApiV1GovernanceRunsRunIdValidatePost(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.validateRunApiV1GovernanceRunsRunIdValidatePost
      >[0],
      options.request,
    ),
  'POST /api/v1/governance/scenarios': (options: ClientOptions) =>
    operations.createScenarioApiV1GovernanceScenariosPost(
      options.body as Parameters<
        typeof operations.createScenarioApiV1GovernanceScenariosPost
      >[0],
      options.request,
    ),
  'POST /api/v1/jobs': (options: ClientOptions) =>
    operations.createJobApiV1JobsPost(
      options.body as Parameters<typeof operations.createJobApiV1JobsPost>[0],
      options.request,
    ),
  'GET /api/v1/jobs/{job_id}': (options: ClientOptions) =>
    operations.getJobApiV1JobsJobIdGet(
      String(options.params?.path?.['job_id']) as Parameters<
        typeof operations.getJobApiV1JobsJobIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/jobs/{job_id}/cancel': (options: ClientOptions) =>
    operations.cancelJobApiV1JobsJobIdCancelPost(
      String(options.params?.path?.['job_id']) as Parameters<
        typeof operations.cancelJobApiV1JobsJobIdCancelPost
      >[0],
      options.request,
    ),
  'POST /api/v1/jobs/{job_id}/resume': (options: ClientOptions) =>
    operations.resumeJobApiV1JobsJobIdResumePost(
      String(options.params?.path?.['job_id']) as Parameters<
        typeof operations.resumeJobApiV1JobsJobIdResumePost
      >[0],
      options.request,
    ),
  'POST /api/v1/liquidity/cash-forecast/13-week': (options: ClientOptions) =>
    operations.forecast13WeekApiV1LiquidityCashForecast13WeekPost(
      options.body as Parameters<
        typeof operations.forecast13WeekApiV1LiquidityCashForecast13WeekPost
      >[0],
      options.request,
    ),
  'POST /api/v1/liquidity/cash-forecast/accuracy': (options: ClientOptions) =>
    operations.summarizeAccuracyApiV1LiquidityCashForecastAccuracyPost(
      options.body as Parameters<
        typeof operations.summarizeAccuracyApiV1LiquidityCashForecastAccuracyPost
      >[0],
      options.request,
    ),
  'POST /api/v1/liquidity/cash-forecast/monthly': (options: ClientOptions) =>
    operations.forecastMonthlyApiV1LiquidityCashForecastMonthlyPost(
      options.body as Parameters<
        typeof operations.forecastMonthlyApiV1LiquidityCashForecastMonthlyPost
      >[0],
      options.request,
    ),
  'POST /api/v1/liquidity/covenants/evaluate': (options: ClientOptions) =>
    operations.evaluateCovenantApiV1LiquidityCovenantsEvaluatePost(
      options.body as Parameters<
        typeof operations.evaluateCovenantApiV1LiquidityCovenantsEvaluatePost
      >[0],
      options.request,
    ),
  'POST /api/v1/liquidity/debt-schedules': (options: ClientOptions) =>
    operations.buildDebtScheduleApiV1LiquidityDebtSchedulesPost(
      options.body as Parameters<
        typeof operations.buildDebtScheduleApiV1LiquidityDebtSchedulesPost
      >[0],
      options.request,
    ),
  'POST /api/v1/liquidity/stress-tests': (options: ClientOptions) =>
    operations.runStressApiV1LiquidityStressTestsPost(
      options.body as Parameters<
        typeof operations.runStressApiV1LiquidityStressTestsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/liquidity/working-capital': (options: ClientOptions) =>
    operations.calculateWorkingCapitalApiV1LiquidityWorkingCapitalPost(
      options.body as Parameters<
        typeof operations.calculateWorkingCapitalApiV1LiquidityWorkingCapitalPost
      >[0],
      options.request,
    ),
  'GET /api/v1/liquidity/workspace': (options: ClientOptions) =>
    operations.liquidityWorkspaceApiV1LiquidityWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.liquidityWorkspaceApiV1LiquidityWorkspaceGet
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/backtests/var': (options: ClientOptions) =>
    operations.backtestApiV1MarketRiskBacktestsVarPost(
      options.body as Parameters<
        typeof operations.backtestApiV1MarketRiskBacktestsVarPost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/exposures/aggregate': (options: ClientOptions) =>
    operations.aggregateApiV1MarketRiskExposuresAggregatePost(
      options.body as Parameters<
        typeof operations.aggregateApiV1MarketRiskExposuresAggregatePost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/hedges/effectiveness': (options: ClientOptions) =>
    operations.hedgeEffectivenessApiV1MarketRiskHedgesEffectivenessPost(
      options.body as Parameters<
        typeof operations.hedgeEffectivenessApiV1MarketRiskHedgesEffectivenessPost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/model-runs': (options: ClientOptions) =>
    operations.createMarketRiskModelRunApiV1MarketRiskModelRunsPost(
      options.body as Parameters<
        typeof operations.createMarketRiskModelRunApiV1MarketRiskModelRunsPost
      >[0],
      options.request,
    ),
  'GET /api/v1/market-risk/model-runs/{run_id}': (options: ClientOptions) =>
    operations.getMarketRiskModelRunApiV1MarketRiskModelRunsRunIdGet(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.getMarketRiskModelRunApiV1MarketRiskModelRunsRunIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/models/copula': (options: ClientOptions) =>
    operations.fitCopulaApiV1MarketRiskModelsCopulaPost(
      options.body as Parameters<
        typeof operations.fitCopulaApiV1MarketRiskModelsCopulaPost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/models/evt': (options: ClientOptions) =>
    operations.fitEvtApiV1MarketRiskModelsEvtPost(
      options.body as Parameters<
        typeof operations.fitEvtApiV1MarketRiskModelsEvtPost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/models/garch-t': (options: ClientOptions) =>
    operations.fitGarchApiV1MarketRiskModelsGarchTPost(
      options.body as Parameters<
        typeof operations.fitGarchApiV1MarketRiskModelsGarchTPost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/models/regime-hmm': (options: ClientOptions) =>
    operations.fitHmmApiV1MarketRiskModelsRegimeHmmPost(
      options.body as Parameters<
        typeof operations.fitHmmApiV1MarketRiskModelsRegimeHmmPost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/sensitivities': (options: ClientOptions) =>
    operations.sensitivitiesApiV1MarketRiskSensitivitiesPost(
      options.body as Parameters<
        typeof operations.sensitivitiesApiV1MarketRiskSensitivitiesPost
      >[0],
      options.request,
    ),
  'POST /api/v1/market-risk/var-es': (options: ClientOptions) =>
    operations.varEsApiV1MarketRiskVarEsPost(
      options.body as Parameters<typeof operations.varEsApiV1MarketRiskVarEsPost>[0],
      options.request,
    ),
  'GET /api/v1/market-risk/workspace': (options: ClientOptions) =>
    operations.marketRiskWorkspaceApiV1MarketRiskWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.marketRiskWorkspaceApiV1MarketRiskWorkspaceGet
      >[0],
      options.request,
    ),
  'POST /api/v1/performance/anomalies': (options: ClientOptions) =>
    operations.detectAnomaliesApiV1PerformanceAnomaliesPost(
      options.body as Parameters<
        typeof operations.detectAnomaliesApiV1PerformanceAnomaliesPost
      >[0],
      options.request,
    ),
  'POST /api/v1/performance/commentary/requirements': (options: ClientOptions) =>
    operations.evaluateCommentaryApiV1PerformanceCommentaryRequirementsPost(
      options.body as Parameters<
        typeof operations.evaluateCommentaryApiV1PerformanceCommentaryRequirementsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/performance/forecast-accuracy': (options: ClientOptions) =>
    operations.summarizeAccuracyApiV1PerformanceForecastAccuracyPost(
      options.body as Parameters<
        typeof operations.summarizeAccuracyApiV1PerformanceForecastAccuracyPost
      >[0],
      options.request,
    ),
  'POST /api/v1/performance/kpi-tree/evaluate': (options: ClientOptions) =>
    operations.evaluateKpiApiV1PerformanceKpiTreeEvaluatePost(
      options.body as Parameters<
        typeof operations.evaluateKpiApiV1PerformanceKpiTreeEvaluatePost
      >[0],
      options.request,
    ),
  'POST /api/v1/performance/variance-bridges': (options: ClientOptions) =>
    operations.buildVarianceBridgeApiV1PerformanceVarianceBridgesPost(
      options.body as Parameters<
        typeof operations.buildVarianceBridgeApiV1PerformanceVarianceBridgesPost
      >[0],
      options.request,
    ),
  'GET /api/v1/performance/workspace': (options: ClientOptions) =>
    operations.performanceWorkspaceApiV1PerformanceWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.performanceWorkspaceApiV1PerformanceWorkspaceGet
      >[0],
      options.request,
    ),
  'POST /api/v1/planning/backtests': (options: ClientOptions) =>
    operations.backtestApiV1PlanningBacktestsPost(
      options.body as Parameters<
        typeof operations.backtestApiV1PlanningBacktestsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/planning/forecasts': (options: ClientOptions) =>
    operations.createForecastApiV1PlanningForecastsPost(
      options.body as Parameters<
        typeof operations.createForecastApiV1PlanningForecastsPost
      >[0],
      options.request,
    ),
  'GET /api/v1/planning/forecasts/{version_id}': (options: ClientOptions) =>
    operations.getForecastApiV1PlanningForecastsVersionIdGet(
      String(options.params?.path?.['version_id']) as Parameters<
        typeof operations.getForecastApiV1PlanningForecastsVersionIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/planning/probabilistic': (options: ClientOptions) =>
    operations.probabilisticApiV1PlanningProbabilisticPost(
      options.body as Parameters<
        typeof operations.probabilisticApiV1PlanningProbabilisticPost
      >[0],
      options.request,
    ),
  'POST /api/v1/planning/thresholds/evaluate': (options: ClientOptions) =>
    operations.evaluateThresholdApiV1PlanningThresholdsEvaluatePost(
      options.body as Parameters<
        typeof operations.evaluateThresholdApiV1PlanningThresholdsEvaluatePost
      >[0],
      options.request,
    ),
  'GET /api/v1/planning/workspace': (options: ClientOptions) =>
    operations.planningWorkspaceApiV1PlanningWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.planningWorkspaceApiV1PlanningWorkspaceGet
      >[0],
      options.request,
    ),
  'GET /api/v1/platform': (options: ClientOptions) =>
    operations.platformInfoApiV1PlatformGet(options.request),
  'POST /api/v1/profitability/activity-based-costing': (options: ClientOptions) =>
    operations.activityBasedCostingApiV1ProfitabilityActivityBasedCostingPost(
      options.body as Parameters<
        typeof operations.activityBasedCostingApiV1ProfitabilityActivityBasedCostingPost
      >[0],
      options.request,
    ),
  'POST /api/v1/profitability/allocations': (options: ClientOptions) =>
    operations.allocateCostsApiV1ProfitabilityAllocationsPost(
      options.body as Parameters<
        typeof operations.allocateCostsApiV1ProfitabilityAllocationsPost
      >[0],
      options.request,
    ),
  'POST /api/v1/profitability/margin-at-risk': (options: ClientOptions) =>
    operations.marginAtRiskApiV1ProfitabilityMarginAtRiskPost(
      options.body as Parameters<
        typeof operations.marginAtRiskApiV1ProfitabilityMarginAtRiskPost
      >[0],
      options.request,
    ),
  'POST /api/v1/profitability/reconcile': (options: ClientOptions) =>
    operations.reconcileApiV1ProfitabilityReconcilePost(
      options.body as Parameters<
        typeof operations.reconcileApiV1ProfitabilityReconcilePost
      >[0],
      options.request,
    ),
  'POST /api/v1/profitability/sensitivity': (options: ClientOptions) =>
    operations.sensitivityApiV1ProfitabilitySensitivityPost(
      options.body as Parameters<
        typeof operations.sensitivityApiV1ProfitabilitySensitivityPost
      >[0],
      options.request,
    ),
  'POST /api/v1/profitability/summary': (options: ClientOptions) =>
    operations.summarizeApiV1ProfitabilitySummaryPost(
      options.body as Parameters<
        typeof operations.summarizeApiV1ProfitabilitySummaryPost
      >[0],
      options.request,
    ),
  'GET /api/v1/profitability/workspace': (options: ClientOptions) =>
    operations.profitabilityWorkspaceApiV1ProfitabilityWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.profitabilityWorkspaceApiV1ProfitabilityWorkspaceGet
      >[0],
      options.request,
    ),
  'POST /api/v1/reporting/reports': (options: ClientOptions) =>
    operations.generateReportApiV1ReportingReportsPost(
      options.body as Parameters<
        typeof operations.generateReportApiV1ReportingReportsPost
      >[0],
      options.request,
    ),
  'GET /api/v1/reporting/reports/{report_id}': (options: ClientOptions) =>
    operations.getReportApiV1ReportingReportsReportIdGet(
      String(options.params?.path?.['report_id']) as Parameters<
        typeof operations.getReportApiV1ReportingReportsReportIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/reporting/reports/{report_id}/approve': (options: ClientOptions) =>
    operations.approveReportApiV1ReportingReportsReportIdApprovePost(
      String(options.params?.path?.['report_id']) as Parameters<
        typeof operations.approveReportApiV1ReportingReportsReportIdApprovePost
      >[0],
      options.body as Parameters<
        typeof operations.approveReportApiV1ReportingReportsReportIdApprovePost
      >[1],
      options.request,
    ),
  'GET /api/v1/reporting/reports/{report_id}/export/{export_format}': (
    options: ClientOptions,
  ) =>
    operations.exportReportApiV1ReportingReportsReportIdExportExportFormatGet(
      String(options.params?.path?.['report_id']) as Parameters<
        typeof operations.exportReportApiV1ReportingReportsReportIdExportExportFormatGet
      >[0],
      String(options.params?.path?.['export_format']) as Parameters<
        typeof operations.exportReportApiV1ReportingReportsReportIdExportExportFormatGet
      >[1],
      options.request,
    ),
  'GET /api/v1/reporting/runs': (options: ClientOptions) =>
    operations.listReportRunsApiV1ReportingRunsGet(
      options.params?.query as Parameters<
        typeof operations.listReportRunsApiV1ReportingRunsGet
      >[0],
      options.request,
    ),
  'POST /api/v1/reporting/runs': (options: ClientOptions) =>
    operations.createReportRunApiV1ReportingRunsPost(
      options.body as Parameters<
        typeof operations.createReportRunApiV1ReportingRunsPost
      >[0],
      options.request,
    ),
  'GET /api/v1/reporting/runs/{report_id}': (options: ClientOptions) =>
    operations.getReportRunApiV1ReportingRunsReportIdGet(
      String(options.params?.path?.['report_id']) as Parameters<
        typeof operations.getReportRunApiV1ReportingRunsReportIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/reporting/runs/{report_id}/approve': (options: ClientOptions) =>
    operations.approveReportRunApiV1ReportingRunsReportIdApprovePost(
      String(options.params?.path?.['report_id']) as Parameters<
        typeof operations.approveReportRunApiV1ReportingRunsReportIdApprovePost
      >[0],
      options.request,
    ),
  'POST /api/v1/reporting/runs/{report_id}/publish': (options: ClientOptions) =>
    operations.publishReportRunApiV1ReportingRunsReportIdPublishPost(
      String(options.params?.path?.['report_id']) as Parameters<
        typeof operations.publishReportRunApiV1ReportingRunsReportIdPublishPost
      >[0],
      options.request,
    ),
  'POST /api/v1/reporting/runs/{report_id}/review': (options: ClientOptions) =>
    operations.reviewReportRunApiV1ReportingRunsReportIdReviewPost(
      String(options.params?.path?.['report_id']) as Parameters<
        typeof operations.reviewReportRunApiV1ReportingRunsReportIdReviewPost
      >[0],
      options.request,
    ),
  'GET /api/v1/reporting/templates': (options: ClientOptions) =>
    operations.listTemplatesApiV1ReportingTemplatesGet(options.request),
  'GET /api/v1/reporting/workspace': (options: ClientOptions) =>
    operations.reportingWorkspaceApiV1ReportingWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.reportingWorkspaceApiV1ReportingWorkspaceGet
      >[0],
      options.request,
    ),
  'GET /api/v1/risk': (options: ClientOptions) =>
    operations.riskFoundationApiV1RiskGet(options.request),
  'POST /api/v1/risk/aggregation': (options: ClientOptions) =>
    operations.aggregateRisksApiV1RiskAggregationPost(
      options.body as Parameters<
        typeof operations.aggregateRisksApiV1RiskAggregationPost
      >[0],
      options.request,
    ),
  'POST /api/v1/risk/limits/evaluate': (options: ClientOptions) =>
    operations.evaluateLimitApiV1RiskLimitsEvaluatePost(
      options.body as Parameters<
        typeof operations.evaluateLimitApiV1RiskLimitsEvaluatePost
      >[0],
      options.request,
    ),
  'POST /api/v1/risk/model-runs': (options: ClientOptions) =>
    operations.createRiskModelRunApiV1RiskModelRunsPost(
      options.body as Parameters<
        typeof operations.createRiskModelRunApiV1RiskModelRunsPost
      >[0],
      options.request,
    ),
  'GET /api/v1/risk/model-runs/{run_id}': (options: ClientOptions) =>
    operations.getRiskModelRunApiV1RiskModelRunsRunIdGet(
      String(options.params?.path?.['run_id']) as Parameters<
        typeof operations.getRiskModelRunApiV1RiskModelRunsRunIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/risk/plan/integrate': (options: ClientOptions) =>
    operations.integratePlanApiV1RiskPlanIntegratePost(
      options.body as Parameters<
        typeof operations.integratePlanApiV1RiskPlanIntegratePost
      >[0],
      options.request,
    ),
  'POST /api/v1/risk/quantification/expected-loss': (options: ClientOptions) =>
    operations.expectedLossApiV1RiskQuantificationExpectedLossPost(
      options.body as Parameters<
        typeof operations.expectedLossApiV1RiskQuantificationExpectedLossPost
      >[0],
      options.request,
    ),
  'GET /api/v1/risk/register': (options: ClientOptions) =>
    operations.listRisksApiV1RiskRegisterGet(options.request),
  'POST /api/v1/risk/register': (options: ClientOptions) =>
    operations.registerRiskApiV1RiskRegisterPost(
      options.body as Parameters<
        typeof operations.registerRiskApiV1RiskRegisterPost
      >[0],
      options.request,
    ),
  'GET /api/v1/risk/register/{risk_id}': (options: ClientOptions) =>
    operations.getRiskApiV1RiskRegisterRiskIdGet(
      String(options.params?.path?.['risk_id']) as Parameters<
        typeof operations.getRiskApiV1RiskRegisterRiskIdGet
      >[0],
      options.request,
    ),
  'POST /api/v1/risk/reports': (options: ClientOptions) =>
    operations.buildReportApiV1RiskReportsPost(
      options.body as Parameters<typeof operations.buildReportApiV1RiskReportsPost>[0],
      options.request,
    ),
  'GET /api/v1/risk/workspace': (options: ClientOptions) =>
    operations.riskWorkspaceApiV1RiskWorkspaceGet(
      options.params?.query as Parameters<
        typeof operations.riskWorkspaceApiV1RiskWorkspaceGet
      >[0],
      options.request,
    ),
  'GET /health/live': (options: ClientOptions) =>
    operations.livenessHealthLiveGet(options.request),
  'GET /health/ready': (options: ClientOptions) =>
    operations.readinessHealthReadyGet(options.request),
};
export type ResponseData = {
  'GET /api/v1/actions': Extract<
    Awaited<ReturnType<typeof operations.listActionsApiV1ActionsGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/benefits/track': Extract<
    Awaited<ReturnType<typeof operations.trackBenefitsApiV1ActionsBenefitsTrackPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/portfolio/prioritize': Extract<
    Awaited<
      ReturnType<typeof operations.prioritizeActionsApiV1ActionsPortfolioPrioritizePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/register': Extract<
    Awaited<ReturnType<typeof operations.registerActionApiV1ActionsRegisterPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/runs': Extract<
    Awaited<ReturnType<typeof operations.createActionRunApiV1ActionsRunsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/runs/benefit-tracking': Extract<
    Awaited<
      ReturnType<
        typeof operations.createActionBenefitTrackingRunApiV1ActionsRunsBenefitTrackingPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/simulate': Extract<
    Awaited<ReturnType<typeof operations.simulateActionsApiV1ActionsSimulatePost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/actions/workspace': Extract<
    Awaited<ReturnType<typeof operations.actionsWorkspaceApiV1ActionsWorkspaceGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/actions/{action_id}': Extract<
    Awaited<ReturnType<typeof operations.getActionApiV1ActionsActionIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/{action_id}/review': Extract<
    Awaited<ReturnType<typeof operations.reviewActionApiV1ActionsActionIdReviewPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/actions/{action_id}/status': Extract<
    Awaited<ReturnType<typeof operations.changeStatusApiV1ActionsActionIdStatusPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/funding/evaluate': Extract<
    Awaited<
      ReturnType<typeof operations.evaluateFundingApiV1CapitalFundingEvaluatePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/portfolio/optimize': Extract<
    Awaited<
      ReturnType<typeof operations.optimizePortfolioApiV1CapitalPortfolioOptimizePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/projects/monte-carlo': Extract<
    Awaited<ReturnType<typeof operations.monteCarloApiV1CapitalProjectsMonteCarloPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/projects/value': Extract<
    Awaited<ReturnType<typeof operations.valueProjectApiV1CapitalProjectsValuePost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/runs/allocation': Extract<
    Awaited<
      ReturnType<
        typeof operations.createCapitalAllocationRunApiV1CapitalRunsAllocationPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/runs/funding': Extract<
    Awaited<
      ReturnType<typeof operations.createFundingScenarioRunApiV1CapitalRunsFundingPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/runs/monte-carlo-npv': Extract<
    Awaited<
      ReturnType<
        typeof operations.createCapitalMonteCarloRunApiV1CapitalRunsMonteCarloNpvPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/capital/runs/valuation': Extract<
    Awaited<
      ReturnType<
        typeof operations.createCapitalValuationRunApiV1CapitalRunsValuationPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/capital/workspace': Extract<
    Awaited<ReturnType<typeof operations.capitalWorkspaceApiV1CapitalWorkspaceGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/command-center/overview': Extract<
    Awaited<
      ReturnType<typeof operations.commandCenterOverviewApiV1CommandCenterOverviewGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/context/companies': Extract<
    Awaited<ReturnType<typeof operations.listCompaniesApiV1ContextCompaniesGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/context/periods': Extract<
    Awaited<ReturnType<typeof operations.listPeriodsApiV1ContextPeriodsGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/context/principal': Extract<
    Awaited<ReturnType<typeof operations.getPrincipalApiV1ContextPrincipalGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/context/resolve': Extract<
    Awaited<ReturnType<typeof operations.resolveContextApiV1ContextResolveGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/context/scenarios': Extract<
    Awaited<ReturnType<typeof operations.listScenariosApiV1ContextScenariosGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/copilot/routes': Extract<
    Awaited<ReturnType<typeof operations.listRoutesApiV1CopilotRoutesGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/copilot/routes/resolve': Extract<
    Awaited<ReturnType<typeof operations.resolveRouteApiV1CopilotRoutesResolveGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/copilot/sessions': Extract<
    Awaited<ReturnType<typeof operations.createSessionApiV1CopilotSessionsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/copilot/sessions/{session_id}/messages': Extract<
    Awaited<
      ReturnType<typeof operations.sendMessageApiV1CopilotSessionsSessionIdMessagesPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data': Extract<
    Awaited<ReturnType<typeof operations.dataFoundationApiV1DataGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data-governance/workspace': Extract<
    Awaited<
      ReturnType<
        typeof operations.dataGovernanceWorkspaceApiV1DataGovernanceWorkspaceGet
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data/imports': Extract<
    Awaited<ReturnType<typeof operations.listImportsApiV1DataImportsGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/imports': Extract<
    Awaited<ReturnType<typeof operations.importFinanceDataApiV1DataImportsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data/imports/{import_id}/accounts': Extract<
    Awaited<
      ReturnType<
        typeof operations.listSourceAccountsApiV1DataImportsImportIdAccountsGet
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/imports/{import_id}/approve': Extract<
    Awaited<
      ReturnType<typeof operations.approveImportApiV1DataImportsImportIdApprovePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/imports/{import_id}/publish': Extract<
    Awaited<
      ReturnType<typeof operations.publishImportApiV1DataImportsImportIdPublishPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/imports/{import_id}/review': Extract<
    Awaited<
      ReturnType<typeof operations.reviewImportApiV1DataImportsImportIdReviewPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data/imports/{import_id}/source': Extract<
    Awaited<
      ReturnType<typeof operations.downloadSourceApiV1DataImportsImportIdSourceGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data/planning-baselines': Extract<
    Awaited<
      ReturnType<typeof operations.listPlanningBaselinesApiV1DataPlanningBaselinesGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/planning-baselines': Extract<
    Awaited<
      ReturnType<
        typeof operations.publishPlanningBaselineApiV1DataPlanningBaselinesPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data/planning-mappings': Extract<
    Awaited<
      ReturnType<typeof operations.listPlanningMappingsApiV1DataPlanningMappingsGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/planning-mappings': Extract<
    Awaited<
      ReturnType<typeof operations.createPlanningMappingApiV1DataPlanningMappingsPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/planning-mappings/{mapping_set_id}/approve': Extract<
    Awaited<
      ReturnType<
        typeof operations.approvePlanningMappingApiV1DataPlanningMappingsMappingSetIdApprovePost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/data/planning-mappings/{mapping_set_id}/review': Extract<
    Awaited<
      ReturnType<
        typeof operations.reviewPlanningMappingApiV1DataPlanningMappingsMappingSetIdReviewPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/data/snapshots/{snapshot_id}': Extract<
    Awaited<ReturnType<typeof operations.getSnapshotApiV1DataSnapshotsSnapshotIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/decision-runs': Extract<
    Awaited<ReturnType<typeof operations.listDecisionRunsApiV1DecisionRunsGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/decision-runs/{run_id}': Extract<
    Awaited<ReturnType<typeof operations.getDecisionRunApiV1DecisionRunsRunIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/decision-runs/{run_id}/approve': Extract<
    Awaited<
      ReturnType<typeof operations.approveDecisionRunApiV1DecisionRunsRunIdApprovePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/decision-runs/{run_id}/events': Extract<
    Awaited<
      ReturnType<typeof operations.decisionRunEventsApiV1DecisionRunsRunIdEventsGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/decision-runs/{run_id}/reject': Extract<
    Awaited<
      ReturnType<typeof operations.rejectDecisionRunApiV1DecisionRunsRunIdRejectPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/decision-runs/{run_id}/validate': Extract<
    Awaited<
      ReturnType<
        typeof operations.validateDecisionRunApiV1DecisionRunsRunIdValidatePost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/forecast': Extract<
    Awaited<ReturnType<typeof operations.forecastFoundationApiV1ForecastGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/governance/models': Extract<
    Awaited<ReturnType<typeof operations.registerModelApiV1GovernanceModelsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/governance/runs': Extract<
    Awaited<ReturnType<typeof operations.createRunApiV1GovernanceRunsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/governance/runs/{run_id}/approve': Extract<
    Awaited<
      ReturnType<typeof operations.approveRunApiV1GovernanceRunsRunIdApprovePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/governance/runs/{run_id}/lineage': Extract<
    Awaited<ReturnType<typeof operations.lineageApiV1GovernanceRunsRunIdLineageGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/governance/runs/{run_id}/retire': Extract<
    Awaited<ReturnType<typeof operations.retireRunApiV1GovernanceRunsRunIdRetirePost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/governance/runs/{run_id}/validate': Extract<
    Awaited<
      ReturnType<typeof operations.validateRunApiV1GovernanceRunsRunIdValidatePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/governance/scenarios': Extract<
    Awaited<ReturnType<typeof operations.createScenarioApiV1GovernanceScenariosPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/jobs': Extract<
    Awaited<ReturnType<typeof operations.createJobApiV1JobsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/jobs/{job_id}': Extract<
    Awaited<ReturnType<typeof operations.getJobApiV1JobsJobIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/jobs/{job_id}/cancel': Extract<
    Awaited<ReturnType<typeof operations.cancelJobApiV1JobsJobIdCancelPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/jobs/{job_id}/resume': Extract<
    Awaited<ReturnType<typeof operations.resumeJobApiV1JobsJobIdResumePost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/liquidity/cash-forecast/13-week': Extract<
    Awaited<
      ReturnType<typeof operations.forecast13WeekApiV1LiquidityCashForecast13WeekPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/liquidity/cash-forecast/accuracy': Extract<
    Awaited<
      ReturnType<
        typeof operations.summarizeAccuracyApiV1LiquidityCashForecastAccuracyPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/liquidity/cash-forecast/monthly': Extract<
    Awaited<
      ReturnType<typeof operations.forecastMonthlyApiV1LiquidityCashForecastMonthlyPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/liquidity/covenants/evaluate': Extract<
    Awaited<
      ReturnType<typeof operations.evaluateCovenantApiV1LiquidityCovenantsEvaluatePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/liquidity/debt-schedules': Extract<
    Awaited<
      ReturnType<typeof operations.buildDebtScheduleApiV1LiquidityDebtSchedulesPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/liquidity/stress-tests': Extract<
    Awaited<ReturnType<typeof operations.runStressApiV1LiquidityStressTestsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/liquidity/working-capital': Extract<
    Awaited<
      ReturnType<
        typeof operations.calculateWorkingCapitalApiV1LiquidityWorkingCapitalPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/liquidity/workspace': Extract<
    Awaited<ReturnType<typeof operations.liquidityWorkspaceApiV1LiquidityWorkspaceGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/backtests/var': Extract<
    Awaited<ReturnType<typeof operations.backtestApiV1MarketRiskBacktestsVarPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/exposures/aggregate': Extract<
    Awaited<
      ReturnType<typeof operations.aggregateApiV1MarketRiskExposuresAggregatePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/hedges/effectiveness': Extract<
    Awaited<
      ReturnType<
        typeof operations.hedgeEffectivenessApiV1MarketRiskHedgesEffectivenessPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/model-runs': Extract<
    Awaited<
      ReturnType<typeof operations.createMarketRiskModelRunApiV1MarketRiskModelRunsPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/market-risk/model-runs/{run_id}': Extract<
    Awaited<
      ReturnType<
        typeof operations.getMarketRiskModelRunApiV1MarketRiskModelRunsRunIdGet
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/models/copula': Extract<
    Awaited<ReturnType<typeof operations.fitCopulaApiV1MarketRiskModelsCopulaPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/models/evt': Extract<
    Awaited<ReturnType<typeof operations.fitEvtApiV1MarketRiskModelsEvtPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/models/garch-t': Extract<
    Awaited<ReturnType<typeof operations.fitGarchApiV1MarketRiskModelsGarchTPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/models/regime-hmm': Extract<
    Awaited<ReturnType<typeof operations.fitHmmApiV1MarketRiskModelsRegimeHmmPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/sensitivities': Extract<
    Awaited<
      ReturnType<typeof operations.sensitivitiesApiV1MarketRiskSensitivitiesPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/market-risk/var-es': Extract<
    Awaited<ReturnType<typeof operations.varEsApiV1MarketRiskVarEsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/market-risk/workspace': Extract<
    Awaited<
      ReturnType<typeof operations.marketRiskWorkspaceApiV1MarketRiskWorkspaceGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/performance/anomalies': Extract<
    Awaited<ReturnType<typeof operations.detectAnomaliesApiV1PerformanceAnomaliesPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/performance/commentary/requirements': Extract<
    Awaited<
      ReturnType<
        typeof operations.evaluateCommentaryApiV1PerformanceCommentaryRequirementsPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/performance/forecast-accuracy': Extract<
    Awaited<
      ReturnType<
        typeof operations.summarizeAccuracyApiV1PerformanceForecastAccuracyPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/performance/kpi-tree/evaluate': Extract<
    Awaited<
      ReturnType<typeof operations.evaluateKpiApiV1PerformanceKpiTreeEvaluatePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/performance/variance-bridges': Extract<
    Awaited<
      ReturnType<
        typeof operations.buildVarianceBridgeApiV1PerformanceVarianceBridgesPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/performance/workspace': Extract<
    Awaited<
      ReturnType<typeof operations.performanceWorkspaceApiV1PerformanceWorkspaceGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/planning/backtests': Extract<
    Awaited<ReturnType<typeof operations.backtestApiV1PlanningBacktestsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/planning/forecasts': Extract<
    Awaited<ReturnType<typeof operations.createForecastApiV1PlanningForecastsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/planning/forecasts/{version_id}': Extract<
    Awaited<
      ReturnType<typeof operations.getForecastApiV1PlanningForecastsVersionIdGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/planning/probabilistic': Extract<
    Awaited<ReturnType<typeof operations.probabilisticApiV1PlanningProbabilisticPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/planning/thresholds/evaluate': Extract<
    Awaited<
      ReturnType<typeof operations.evaluateThresholdApiV1PlanningThresholdsEvaluatePost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/planning/workspace': Extract<
    Awaited<ReturnType<typeof operations.planningWorkspaceApiV1PlanningWorkspaceGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/platform': Extract<
    Awaited<ReturnType<typeof operations.platformInfoApiV1PlatformGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/profitability/activity-based-costing': Extract<
    Awaited<
      ReturnType<
        typeof operations.activityBasedCostingApiV1ProfitabilityActivityBasedCostingPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/profitability/allocations': Extract<
    Awaited<
      ReturnType<typeof operations.allocateCostsApiV1ProfitabilityAllocationsPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/profitability/margin-at-risk': Extract<
    Awaited<
      ReturnType<typeof operations.marginAtRiskApiV1ProfitabilityMarginAtRiskPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/profitability/reconcile': Extract<
    Awaited<ReturnType<typeof operations.reconcileApiV1ProfitabilityReconcilePost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/profitability/sensitivity': Extract<
    Awaited<ReturnType<typeof operations.sensitivityApiV1ProfitabilitySensitivityPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/profitability/summary': Extract<
    Awaited<ReturnType<typeof operations.summarizeApiV1ProfitabilitySummaryPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/profitability/workspace': Extract<
    Awaited<
      ReturnType<typeof operations.profitabilityWorkspaceApiV1ProfitabilityWorkspaceGet>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/reporting/reports': Extract<
    Awaited<ReturnType<typeof operations.generateReportApiV1ReportingReportsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/reporting/reports/{report_id}': Extract<
    Awaited<ReturnType<typeof operations.getReportApiV1ReportingReportsReportIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/reporting/reports/{report_id}/approve': Extract<
    Awaited<
      ReturnType<
        typeof operations.approveReportApiV1ReportingReportsReportIdApprovePost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/reporting/reports/{report_id}/export/{export_format}': Extract<
    Awaited<
      ReturnType<
        typeof operations.exportReportApiV1ReportingReportsReportIdExportExportFormatGet
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/reporting/runs': Extract<
    Awaited<ReturnType<typeof operations.listReportRunsApiV1ReportingRunsGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/reporting/runs': Extract<
    Awaited<ReturnType<typeof operations.createReportRunApiV1ReportingRunsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/reporting/runs/{report_id}': Extract<
    Awaited<ReturnType<typeof operations.getReportRunApiV1ReportingRunsReportIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/reporting/runs/{report_id}/approve': Extract<
    Awaited<
      ReturnType<
        typeof operations.approveReportRunApiV1ReportingRunsReportIdApprovePost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/reporting/runs/{report_id}/publish': Extract<
    Awaited<
      ReturnType<
        typeof operations.publishReportRunApiV1ReportingRunsReportIdPublishPost
      >
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/reporting/runs/{report_id}/review': Extract<
    Awaited<
      ReturnType<typeof operations.reviewReportRunApiV1ReportingRunsReportIdReviewPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/reporting/templates': Extract<
    Awaited<ReturnType<typeof operations.listTemplatesApiV1ReportingTemplatesGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/reporting/workspace': Extract<
    Awaited<ReturnType<typeof operations.reportingWorkspaceApiV1ReportingWorkspaceGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/risk': Extract<
    Awaited<ReturnType<typeof operations.riskFoundationApiV1RiskGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/risk/aggregation': Extract<
    Awaited<ReturnType<typeof operations.aggregateRisksApiV1RiskAggregationPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/risk/limits/evaluate': Extract<
    Awaited<ReturnType<typeof operations.evaluateLimitApiV1RiskLimitsEvaluatePost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/risk/model-runs': Extract<
    Awaited<ReturnType<typeof operations.createRiskModelRunApiV1RiskModelRunsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/risk/model-runs/{run_id}': Extract<
    Awaited<ReturnType<typeof operations.getRiskModelRunApiV1RiskModelRunsRunIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/risk/plan/integrate': Extract<
    Awaited<ReturnType<typeof operations.integratePlanApiV1RiskPlanIntegratePost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/risk/quantification/expected-loss': Extract<
    Awaited<
      ReturnType<typeof operations.expectedLossApiV1RiskQuantificationExpectedLossPost>
    >,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/risk/register': Extract<
    Awaited<ReturnType<typeof operations.listRisksApiV1RiskRegisterGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/risk/register': Extract<
    Awaited<ReturnType<typeof operations.registerRiskApiV1RiskRegisterPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/risk/register/{risk_id}': Extract<
    Awaited<ReturnType<typeof operations.getRiskApiV1RiskRegisterRiskIdGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'POST /api/v1/risk/reports': Extract<
    Awaited<ReturnType<typeof operations.buildReportApiV1RiskReportsPost>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /api/v1/risk/workspace': Extract<
    Awaited<ReturnType<typeof operations.riskWorkspaceApiV1RiskWorkspaceGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /health/live': Extract<
    Awaited<ReturnType<typeof operations.livenessHealthLiveGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
  'GET /health/ready': Extract<
    Awaited<ReturnType<typeof operations.readinessHealthReadyGet>>,
    { status: 200 | 201 | 202 | 204 }
  >['data'];
};
