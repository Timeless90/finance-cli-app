import { type PropsWithChildren, useMemo, useState } from 'react';

import { apiConfig } from '@/shared/api/config';
import {
  useCompanies,
  usePeriods,
  usePrincipal,
  useScenarios,
} from '@/shared/api/context';
import type { WorkspaceContextValue } from '@/app/context/workspace-context';
import {
  companies,
  periods,
  scenarios,
  WorkspaceContext,
} from '@/app/context/workspace-context';

export function WorkspaceContextProvider({ children }: PropsWithChildren) {
  const isLive = apiConfig.mode === 'live';
  const stored = (key: string) => {
    try {
      return typeof window === 'undefined'
        ? ''
        : (window.localStorage.getItem(`cfo-context-${key}`) ?? '');
    } catch {
      return '';
    }
  };
  const persist = (key: string, value: string) => {
    try {
      window.localStorage.setItem(`cfo-context-${key}`, value);
    } catch {
      /* unavailable in non-browser tests */
    }
  };
  const [companyId, setCompanyId] = useState(() => stored('company'));
  const [periodId, setPeriodId] = useState(() => stored('period'));
  const [scenarioId, setScenarioId] = useState(() => stored('scenario'));
  const principalQuery = usePrincipal(isLive);
  const companiesQuery = useCompanies(isLive);
  const availableCompanies = isLive
    ? (companiesQuery.data ?? []).map((company) => ({
        id: company.company_id,
        label: company.label,
      }))
    : companies;
  const activeCompanyId =
    availableCompanies.find((company) => company.id === companyId)?.id ||
    availableCompanies[0]?.id ||
    '';
  const periodsQuery = usePeriods(activeCompanyId, isLive);
  const availablePeriods = isLive
    ? (periodsQuery.data ?? []).map((period) => ({
        id: period.period_id,
        label: period.label,
      }))
    : periods;
  const activePeriodId =
    availablePeriods.find((period) => period.id === periodId)?.id ||
    availablePeriods[0]?.id ||
    '';
  const scenariosQuery = useScenarios(activeCompanyId, activePeriodId, isLive);
  const availableScenarios = isLive
    ? (scenariosQuery.data ?? []).map((scenario) => ({
        id: scenario.scenario_id,
        label: scenario.label,
      }))
    : scenarios;
  const activeScenarioId =
    availableScenarios.find((scenario) => scenario.id === scenarioId)?.id ||
    availableScenarios[0]?.id ||
    '';

  const failedQuery = [
    principalQuery,
    companiesQuery,
    periodsQuery,
    scenariosQuery,
  ].find((query) => query.isError);
  const status: NonNullable<WorkspaceContextValue['status']> = isLive
    ? failedQuery
      ? 'error'
      : principalQuery.isSuccess &&
          companiesQuery.isSuccess &&
          (!availableCompanies.length ||
            (periodsQuery.isSuccess &&
              (!availablePeriods.length || scenariosQuery.isSuccess)))
        ? 'ready'
        : 'loading'
    : 'ready';

  const value = useMemo(
    () => ({
      companies: availableCompanies,
      periods: availablePeriods,
      scenarios: availableScenarios,
      companyId: activeCompanyId,
      periodId: activePeriodId,
      scenarioId: activeScenarioId,
      setCompanyId: (value: string) => {
        setCompanyId(value);
        setPeriodId('');
        setScenarioId('');
        persist('company', value);
        persist('period', '');
        persist('scenario', '');
      },
      setPeriodId: (value: string) => {
        setPeriodId(value);
        setScenarioId('');
        persist('period', value);
        persist('scenario', '');
      },
      setScenarioId: (value: string) => {
        setScenarioId(value);
        persist('scenario', value);
      },
      principal: isLive
        ? {
            userId: principalQuery.data?.user_id ?? null,
            permissions: principalQuery.data?.permissions ?? [],
          }
        : { userId: 'mock-user', permissions: [] },
      source: isLive ? ('live' as const) : ('mock' as const),
      status,
      error: failedQuery?.error instanceof Error ? failedQuery.error : null,
    }),
    [
      activeCompanyId,
      activePeriodId,
      activeScenarioId,
      availableCompanies,
      availablePeriods,
      availableScenarios,
      failedQuery?.error,
      isLive,
      principalQuery.data?.permissions,
      principalQuery.data?.user_id,
      status,
    ],
  );

  return (
    <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>
  );
}
