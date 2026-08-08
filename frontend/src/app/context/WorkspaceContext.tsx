import { type PropsWithChildren, useMemo, useState } from "react";

import {
  companies,
  periods,
  scenarios,
  WorkspaceContext,
} from "@/app/context/workspace-context";

export function WorkspaceContextProvider({ children }: PropsWithChildren) {
  const [companyId, setCompanyId] = useState(companies[0].id);
  const [periodId, setPeriodId] = useState(periods[0].id);
  const [scenarioId, setScenarioId] = useState(scenarios[0].id);

  const value = useMemo(
    () => ({
      companies,
      periods,
      scenarios,
      companyId,
      periodId,
      scenarioId,
      setCompanyId,
      setPeriodId,
      setScenarioId,
    }),
    [companyId, periodId, scenarioId],
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}
