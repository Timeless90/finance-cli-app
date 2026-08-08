import { useQuery } from "@tanstack/react-query";

import { getMockReportingCopilotSnapshot } from "./mock";
import type { WorkspaceSelection } from "./contracts";

export function useReportingCopilotSnapshot(selection: WorkspaceSelection) {
  return useQuery({
    queryKey: ["reporting-copilot", selection.companyId, selection.periodId, selection.scenarioId],
    queryFn: () => Promise.resolve(getMockReportingCopilotSnapshot(selection)),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
