import { NavLink, Outlet, useLocation } from "react-router-dom";

import { WorkspaceContextProvider } from "@/app/context/WorkspaceContext";
import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { getWorkspaceByPath, workspaceNavigation } from "@/app/navigation";
import { StatusIndicator } from "@/components/finance";

const navGroups = [
  { id: "steer" as const, label: "STEER" },
  { id: "decide" as const, label: "DECIDE" },
  { id: "system" as const, label: "SYSTEM" },
];

function ContextSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<{ id: string; label: string }>;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid min-w-36 gap-1.5">
      <span className="interface-label text-[var(--text-muted)]">{label}</span>
      <select
        className="data-value h-9 border border-[var(--frame-muted)] bg-[var(--surface-panel)] px-2 text-xs text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--frame-active)]"
        onChange={(event) => onChange(event.target.value)}
        value={value}
      >
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function ContextBar() {
  const context = useWorkspaceContext();

  return (
    <div className="grid gap-3 border-b border-[var(--frame-muted)] bg-[var(--surface-panel)] px-4 py-3 lg:grid-cols-[1fr_auto] lg:items-end lg:px-5">
      <div className="flex min-w-0 items-center gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center border border-[var(--frame-active)] bg-[var(--surface-canvas)] text-[var(--signal-primary)]">
          <span className="data-value text-xs">CFO</span>
        </div>
        <div className="min-w-0">
          <p className="interface-label m-0 truncate text-[var(--signal-primary)]">FINANCE 2060 // COMMAND LAYER</p>
          <p className="data-value m-0 mt-1 truncate text-xs text-[var(--text-secondary)]">LOCAL CONTEXT // NOT YET BACKEND-BOUND</p>
        </div>
      </div>
      <div className="grid gap-2 sm:grid-cols-3">
        <ContextSelect label="COMPANY" onChange={context.setCompanyId} options={context.companies} value={context.companyId} />
        <ContextSelect label="PERIOD" onChange={context.setPeriodId} options={context.periods} value={context.periodId} />
        <ContextSelect label="SCENARIO" onChange={context.setScenarioId} options={context.scenarios} value={context.scenarioId} />
      </div>
    </div>
  );
}

function PrimaryNavigation() {
  return (
    <aside className="hidden min-h-0 border-r border-[var(--frame-muted)] bg-[var(--surface-panel)] xl:block">
      <nav aria-label="Primary application navigation" className="grid gap-5 p-3">
        {navGroups.map((group) => (
          <div key={group.id}>
            <div className="interface-label px-2 pb-2 text-[var(--text-muted)]">{group.label}</div>
            <div className="grid gap-1">
              {workspaceNavigation
                .filter((item) => item.group === group.id)
                .map((item) => (
                  <NavLink
                    className={({ isActive }) =>
                      [
                        "group grid grid-cols-[2rem_1fr] items-center border px-2 py-2.5 no-underline transition-colors",
                        isActive
                          ? "border-[var(--frame-active)] bg-[var(--surface-panel-hover)] text-[var(--text-primary)]"
                          : "border-transparent text-[var(--text-secondary)] hover:border-[var(--frame-default)] hover:bg-[var(--surface-panel-raised)]",
                      ].join(" ")
                    }
                    key={item.path}
                    to={item.path}
                  >
                    <span className="data-value text-[0.65rem] text-[var(--text-muted)] group-[.active]:text-[var(--signal-primary)]">{item.code}</span>
                    <span className="text-sm">{item.label}</span>
                  </NavLink>
                ))}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}

function MobileNavigation() {
  return (
    <nav
      aria-label="Mobile application navigation"
      className="flex gap-1 overflow-x-auto border-b border-[var(--frame-muted)] bg-[var(--surface-panel)] p-2 xl:hidden"
    >
      {workspaceNavigation.map((item) => (
        <NavLink
          className={({ isActive }) =>
            [
              "data-value whitespace-nowrap border px-3 py-2 text-[0.68rem] no-underline",
              isActive
                ? "border-[var(--frame-active)] bg-[var(--surface-panel-hover)] text-[var(--signal-primary)]"
                : "border-[var(--frame-muted)] text-[var(--text-secondary)]",
            ].join(" ")
          }
          key={item.path}
          to={item.path}
        >
          {item.code} // {item.label.toUpperCase()}
        </NavLink>
      ))}
    </nav>
  );
}

function StatusBar() {
  return (
    <footer className="grid gap-px border-t border-[var(--frame-muted)] bg-[var(--frame-muted)] sm:grid-cols-4">
      <StatusIndicator label="CONTEXT" detail="LOCAL" tone="warning" />
      <StatusIndicator label="API" detail="UNBOUND" tone="neutral" />
      <StatusIndicator label="DATA" detail="UNBOUND" tone="neutral" />
      <StatusIndicator label="MODEL" detail="UNBOUND" tone="neutral" />
    </footer>
  );
}

function ShellContent() {
  const location = useLocation();
  const workspace = getWorkspaceByPath(location.pathname);

  return (
    <main className="ds-environment min-h-screen p-2 sm:p-3">
      <div className="mx-auto grid min-h-[calc(100vh-1rem)] max-w-[1800px] overflow-hidden border border-[var(--frame-default)] bg-[var(--surface-canvas)] shadow-[0_0_50px_var(--glow-primary)] sm:min-h-[calc(100vh-1.5rem)]">
        <ContextBar />
        <MobileNavigation />
        <div className="grid min-h-0 xl:grid-cols-[15rem_1fr]">
          <PrimaryNavigation />
          <section className="min-w-0 overflow-auto">
            <div className="flex items-center justify-between border-b border-[var(--frame-muted)] px-4 py-2.5 lg:px-6">
              <div className="interface-label text-[var(--text-muted)]">
                WORKSPACE // <span className="text-[var(--signal-primary)]">{workspace?.code ?? "--"}</span>
              </div>
              <div className="data-value text-[0.68rem] text-[var(--text-muted)]">FE-02 // APP SHELL</div>
            </div>
            <Outlet />
          </section>
        </div>
        <StatusBar />
      </div>
    </main>
  );
}

export function AppShell() {
  return (
    <WorkspaceContextProvider>
      <ShellContent />
    </WorkspaceContextProvider>
  );
}
