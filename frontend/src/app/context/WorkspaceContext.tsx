import { createContext, type PropsWithChildren, useContext, useMemo, useState } from "react";

export type ContextOption = {
  id: string;
  label: string;
};

type WorkspaceContextValue = {
  companies: ContextOption[];
  periods: ContextOption[];
  scenarios: ContextOption[];
  companyId: string;
  periodId: string;
  scenarioId: string;
  setCompanyId: (value: string) => void;
  setPeriodId: (value: string) => void;
  setScenarioId: (value: string) => void;
};

const companies: ContextOption[] = [
  { id: "local-holding", label: "AURELIA HOLDING" },
  { id: "local-eu", label: "EUROPE DIVISION" },
];

const periods: ContextOption[] = [
  { id: "local-fy26-p08", label: "FY26 // P08" },
  { id: "local-fy26-p07", label: "FY26 // P07" },
];

const scenarios: ContextOption[] = [
  { id: "local-base", label: "BASE" },
  { id: "local-upside", label: "UPSIDE" },
  { id: "local-downside", label: "DOWNSIDE" },
];

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

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

export function useWorkspaceContext() {
  const context = useContext(WorkspaceContext);

  if (!context) {
    throw new Error("useWorkspaceContext must be used inside WorkspaceContextProvider");
  }

  return context;
}
