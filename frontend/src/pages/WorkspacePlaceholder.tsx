import { useLocation } from "react-router-dom";

import { getWorkspaceByPath } from "@/app/navigation";
import { useWorkspaceContext } from "@/app/context/WorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";

export function WorkspacePlaceholder() {
  const location = useLocation();
  const workspace = getWorkspaceByPath(location.pathname);
  const context = useWorkspaceContext();

  if (!workspace) {
    return null;
  }

  return (
    <div className="grid gap-5 p-4 lg:p-6">
      <header className="grid gap-4 border-b border-[var(--frame-muted)] pb-5 lg:grid-cols-[1fr_auto] lg:items-end">
        <div>
          <p className="interface-label m-0 text-[var(--signal-primary)]">{workspace.code} // {workspace.group.toUpperCase()}</p>
          <h1 className="m-0 mt-2 font-display text-4xl font-semibold uppercase leading-none tracking-[-0.035em] sm:text-5xl">
            {workspace.label}
          </h1>
          <p className="mb-0 mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">{workspace.description}</p>
        </div>
        <StatusIndicator label="INTEGRATION" detail="PLACEHOLDER" tone="warning" />
      </header>

      {workspace.path === "/app/command-center" ? (
        <section className="grid gap-3 md:grid-cols-3">
          <MetricPanel delta="LOCAL" deltaTone="neutral" label="EBITDA" meta="NO BACKEND VALUE" value="—" />
          <MetricPanel delta="LOCAL" deltaTone="neutral" label="CASH" meta="NO BACKEND VALUE" value="—" />
          <MetricPanel delta="LOCAL" deltaTone="neutral" label="RISK" meta="NO BACKEND VALUE" value="—" />
        </section>
      ) : null}

      <section className="grid gap-4 lg:grid-cols-[1.4fr_0.8fr]">
        <TacticalFrame label="WORKSPACE STATUS" tone="active">
          <div className="grid min-h-64 content-start gap-4 p-5">
            <div className="interface-label text-[var(--text-muted)]">UI ROUTE READY</div>
            <div className="data-value text-2xl text-[var(--signal-primary)]">{workspace.path}</div>
            <p className="m-0 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
              FE-02 establishes navigation, responsive application framing and global presentation context. Domain data is intentionally not loaded yet.
            </p>
          </div>
        </TacticalFrame>

        <TacticalFrame label="ACTIVE LOCAL CONTEXT" tone="muted">
          <dl className="m-0 grid gap-px bg-[var(--frame-muted)]">
            {[
              ["COMPANY", context.companyId],
              ["PERIOD", context.periodId],
              ["SCENARIO", context.scenarioId],
            ].map(([label, value]) => (
              <div className="bg-[var(--surface-panel)] p-4" key={label}>
                <dt className="interface-label text-[var(--text-muted)]">{label}</dt>
                <dd className="data-value m-0 mt-2 text-xs text-[var(--signal-warning)]">{value}</dd>
              </div>
            ))}
          </dl>
        </TacticalFrame>
      </section>
    </div>
  );
}
