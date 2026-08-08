import { useQuery } from "@tanstack/react-query";

import { getMockActionCapitalSnapshot } from "./mock";
import type { WorkspaceSelection } from "./contracts";

export function useActionCapitalSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["action-capital", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockActionCapitalSnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
