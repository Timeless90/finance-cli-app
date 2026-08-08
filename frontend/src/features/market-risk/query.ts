import { useQuery } from "@tanstack/react-query";

import { getMockMarketRiskSnapshot } from "./mock";
import type { WorkspaceSelection } from "./contracts";

export function useMarketRiskSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["market-risk-lab", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockMarketRiskSnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
