import { useQuery } from "@tanstack/react-query";

import { getMockPerformanceSnapshot, getMockPlanningSnapshot } from "./mock";
import type { WorkspaceSelection } from "./contracts";

export function usePlanningSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["planning-workspace", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockPlanningSnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}

export function usePerformanceSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["performance-workspace", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockPerformanceSnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
