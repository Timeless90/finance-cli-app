import { useQuery } from "@tanstack/react-query";

import { getMockRiskCommandSnapshot } from "./mock";
import type { WorkspaceSelection } from "./contracts";

export function useRiskCommandSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["risk-command", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockRiskCommandSnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
