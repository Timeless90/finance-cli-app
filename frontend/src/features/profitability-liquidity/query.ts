import { useQuery } from "@tanstack/react-query";

import { getMockLiquiditySnapshot, getMockProfitabilitySnapshot } from "./mock";
import type { WorkspaceSelection } from "./contracts";

export function useProfitabilitySnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["profitability-workspace", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockProfitabilitySnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}

export function useLiquiditySnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["liquidity-workspace", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockLiquiditySnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
