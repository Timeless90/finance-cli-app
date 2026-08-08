import { createContext } from "react";

export type ContextOption = {
  id: string;
  label: string;
};

export type WorkspaceContextValue = {
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

export const companies: ContextOption[] = [
  { id: "local-holding", label: "AURELIA HOLDING" },
  { id: "local-eu", label: "EUROPE DIVISION" },
];

export const periods: ContextOption[] = [
  { id: "local-fy26-p08", label: "FY26 // P08" },
  { id: "local-fy26-p07", label: "FY26 // P07" },
];

export const scenarios: ContextOption[] = [
  { id: "local-base", label: "BASE" },
  { id: "local-upside", label: "UPSIDE" },
  { id: "local-downside", label: "DOWNSIDE" },
];

export const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);
