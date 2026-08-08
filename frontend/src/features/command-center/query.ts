import { useQuery } from "@tanstack/react-query";

import { getMockCommandCenterSnapshot } from "./mock";
import type { CommandCenterContext, CommandCenterSnapshot } from "./contracts";

export async function getCommandCenterSnapshot(
  context: CommandCenterContext,
): Promise<CommandCenterSnapshot> {
  return Promise.resolve(getMockCommandCenterSnapshot(context));
}

export function useCommandCenterSnapshot(context: CommandCenterContext) {
  return useQuery({
    queryKey: ["command-center", context.companyId, context.periodId, context.scenarioId],
    queryFn: () => getCommandCenterSnapshot(context),
    staleTime: Number.POSITIVE_INFINITY,
    retry: false,
  });
}
