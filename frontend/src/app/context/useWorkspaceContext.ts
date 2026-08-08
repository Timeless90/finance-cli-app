import { useContext } from "react";

import { WorkspaceContext } from "@/app/context/workspace-context";

export function useWorkspaceContext() {
  const context = useContext(WorkspaceContext);

  if (!context) {
    throw new Error("useWorkspaceContext must be used inside WorkspaceContextProvider");
  }

  return context;
}
