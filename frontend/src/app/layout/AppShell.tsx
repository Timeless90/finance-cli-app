import { Outlet, useLocation } from '@tanstack/react-router';
import { NavLink } from '@/app/nav-link';

import { ApiProvider } from '@/shared/api/ApiProvider';
import { useSystemContract } from '@/shared/api/system';
import { WorkspaceContextProvider } from '@/app/context/WorkspaceContext';
import { useWorkspaceContext } from '@/app/context/useWorkspaceContext';
import { getWorkspaceByPath, workspaceNavigation } from '@/app/navigation';
import { StatusIndicator } from '@/features/finance-ui';

const navGroups = [
  { id: 'steer' as const, label: 'STEER' },
  { id: 'decide' as const, label: 'DECIDE' },
  { id: 'system' as const, label: 'SYSTEM' },
];

function ContextSelect({
  label,
  value,
  options,
  onChange,
  disabled = false,
}: {
  label: string;
  value: string;
  options: Array<{ id: string; label: string }>;
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  return (
    <label className="grid min-w-36 gap-1.5">
      <span className="interface-label text-[var(--text-muted)]">{label}</span>
      <select
        className="data-value h-9 border border-[var(--frame-muted)] bg-[var(--surface-panel)] px-2 text-xs text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--frame-active)]"
        onChange={(event) => onChange(event.target.value)}
        value={value}
        disabled={disabled || !options.length}
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
  const detail =
    context.status === 'ready' &&
    (!context.companies.length || !context.periods.length || !context.scenarios.length)
      ? 'NO PUBLISHED COMPANY DATA'
      : context.status === 'ready'
        ? `${context.source?.toUpperCase() ?? 'LOCAL'} CONTEXT // BACKEND-BOUND`
        : context.status === 'error'
          ? 'CONTEXT UNAVAILABLE'
          : 'LOADING BACKEND CONTEXT';

  return (
    <div className="grid gap-3 border-b border-[var(--frame-muted)] bg-[var(--surface-panel)] px-4 py-3 lg:grid-cols-[1fr_auto] lg:items-end lg:px-5">
      <div className="flex min-w-0 items-center gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center border border-[var(--frame-active)] bg-[var(--surface-canvas)] text-[var(--signal-primary)]">
          <span className="data-value text-xs">CFO</span>
        </div>
        <div className="min-w-0">
          <p className="interface-label m-0 truncate text-[var(--signal-primary)]">
            FINANCE 2060 // COMMAND LAYER
          </p>
          <p className="data-value m-0 mt-1 truncate text-xs text-[var(--text-secondary)]">
            {detail}
          </p>
        </div>
      </div>
      <div className="grid gap-2 sm:grid-cols-3">
        <ContextSelect
          disabled={context.status !== 'ready'}
          label="COMPANY"
          onChange={context.setCompanyId}
          options={context.companies}
          value={context.companyId}
        />
        <ContextSelect
          disabled={context.status !== 'ready'}
          label="PERIOD"
          onChange={context.setPeriodId}
          options={context.periods}
          value={context.periodId}
        />
        <ContextSelect
          disabled={context.status !== 'ready'}
          label="SCENARIO"
          onChange={context.setScenarioId}
          options={context.scenarios}
          value={context.scenarioId}
        />
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
            <div className="interface-label px-2 pb-2 text-[var(--text-muted)]">
              {group.label}
            </div>
            <div className="grid gap-1">
              {workspaceNavigation
                .filter((item) => item.group === group.id)
                .map((item) => (
                  <NavLink
                    className={({ isActive }) =>
                      [
                        'group grid grid-cols-[2rem_1fr] items-center border px-2 py-2.5 no-underline transition-colors',
                        isActive
                          ? 'border-[var(--frame-active)] bg-[var(--surface-panel-hover)] text-[var(--text-primary)]'
                          : 'border-transparent text-[var(--text-secondary)] hover:border-[var(--frame-default)] hover:bg-[var(--surface-panel-raised)]',
                      ].join(' ')
                    }
                    key={item.path}
                    to={item.path}
                  >
                    <span className="data-value text-[0.65rem] text-[var(--text-muted)] group-[.active]:text-[var(--signal-primary)]">
                      {item.code}
                    </span>
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
              'data-value whitespace-nowrap border px-3 py-2 text-[0.68rem] no-underline',
              isActive
                ? 'border-[var(--frame-active)] bg-[var(--surface-panel-hover)] text-[var(--signal-primary)]'
                : 'border-[var(--frame-muted)] text-[var(--text-secondary)]',
            ].join(' ')
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
  const context = useWorkspaceContext();
  const systemContract = useSystemContract();
  const apiDetail = systemContract.isSuccess
    ? systemContract.data.readiness.status.toUpperCase()
    : systemContract.isError
      ? 'OFFLINE'
      : 'CHECKING';
  const apiTone = systemContract.isSuccess
    ? 'positive'
    : systemContract.isError
      ? 'negative'
      : 'neutral';
  const platformDetail =
    systemContract.data?.platform.api_version.toUpperCase() ?? 'UNBOUND';

  return (
    <footer className="grid gap-px border-t border-[var(--frame-muted)] bg-[var(--frame-muted)] sm:grid-cols-4">
      <StatusIndicator
        label="CONTEXT"
        detail={
          context.status === 'ready'
            ? (context.source ?? 'mock').toUpperCase()
            : (context.status?.toUpperCase() ?? 'LOCAL')
        }
        tone={
          context.status === 'error'
            ? 'negative'
            : context.source === 'live'
              ? 'positive'
              : 'warning'
        }
      />
      <StatusIndicator label="API" detail={apiDetail} tone={apiTone} />
      <StatusIndicator
        label="CONTRACT"
        detail={platformDetail}
        tone={systemContract.isSuccess ? 'positive' : 'neutral'}
      />
      <StatusIndicator label="MODEL" detail="UNBOUND" tone="neutral" />
    </footer>
  );
}

function ShellContent() {
  const location = useLocation();
  const workspace = getWorkspaceByPath(location.pathname);
  const context = useWorkspaceContext();

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
                WORKSPACE //{' '}
                <span className="text-[var(--signal-primary)]">
                  {workspace?.code ?? '--'}
                </span>
              </div>
              <div className="data-value text-[0.68rem] text-[var(--text-muted)]">
                FE-05 // EXECUTIVE COCKPIT
              </div>
            </div>
            {context.status === 'loading' && (
              <div className="p-6 text-sm text-[var(--text-secondary)]">
                Loading authoritative workspace context…
              </div>
            )}
            {context.status === 'error' && (
              <div className="p-6 text-sm text-[var(--signal-negative)]">
                Workspace context is unavailable. {context.error?.message}
              </div>
            )}
            {context.status === 'ready' && <Outlet />}
          </section>
        </div>
        <StatusBar />
      </div>
    </main>
  );
}

export function AppShell() {
  return (
    <ApiProvider>
      <WorkspaceContextProvider>
        <ShellContent />
      </WorkspaceContextProvider>
    </ApiProvider>
  );
}
