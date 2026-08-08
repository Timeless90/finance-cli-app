import { Link } from "react-router-dom";

import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import { Button } from "@/components/ui/button";
import type { ForecastPoint, SignalTone } from "@/features/command-center/contracts";
import { useCommandCenterSnapshot } from "@/features/command-center/query";

const signalClasses: Record<SignalTone, string> = {
  positive: "text-[var(--signal-positive)]",
  negative: "text-[var(--signal-negative)]",
  warning: "text-[var(--signal-warning)]",
  neutral: "text-[var(--text-secondary)]",
};

function ForecastChart({ points }: { points: ForecastPoint[] }) {
  const width = 760;
  const height = 220;
  const padding = 18;
  const values = points.flatMap((point) => [point.base, point.upside, point.downside]);
  const min = Math.min(...values) - 1;
  const max = Math.max(...values) + 1;
  const range = Math.max(max - min, 1);
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);
  const line = (selector: (point: ForecastPoint) => number) =>
    points.map((point, index) => `${x(index)},${y(selector(point))}`).join(" ");
  const actual = points
    .map((point, index) => (point.actual === undefined ? null : `${x(index)},${y(point.actual)}`))
    .filter((point): point is string => point !== null)
    .join(" ");

  return (
    <div>
      <svg
        aria-label="EBITDA actual and scenario trajectory"
        className="h-56 w-full"
        role="img"
        viewBox={`0 0 ${width} ${height}`}
      >
        {[0.25, 0.5, 0.75].map((ratio) => (
          <line
            key={ratio}
            stroke="var(--grid-line)"
            x1="0"
            x2={width}
            y1={height * ratio}
            y2={height * ratio}
          />
        ))}
        <polyline
          fill="none"
          points={line((point) => point.upside)}
          stroke="var(--signal-positive)"
          strokeDasharray="6 8"
          strokeOpacity="0.65"
          strokeWidth="1.5"
        />
        <polyline
          fill="none"
          points={line((point) => point.downside)}
          stroke="var(--signal-negative)"
          strokeDasharray="6 8"
          strokeOpacity="0.75"
          strokeWidth="1.5"
        />
        <polyline
          fill="none"
          points={line((point) => point.base)}
          stroke="var(--signal-primary)"
          strokeWidth="2.8"
        />
        <polyline fill="none" points={actual} stroke="var(--text-primary)" strokeWidth="2" />
      </svg>
      <div className="grid grid-cols-5 border-t border-[var(--frame-muted)] pt-2 sm:grid-cols-10">
        {points.map((point) => (
          <span className="data-value text-center text-[0.58rem] text-[var(--text-muted)]" key={point.period}>
            {point.period}
          </span>
        ))}
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="grid gap-3 p-4 lg:grid-cols-4 lg:p-6" aria-label="Loading command center">
      {Array.from({ length: 8 }, (_, index) => (
        <div className="h-36 animate-pulse border border-[var(--frame-muted)] bg-[var(--surface-panel)]" key={index} />
      ))}
    </div>
  );
}

function ErrorState() {
  return (
    <div className="p-4 lg:p-6">
      <TacticalFrame label="COMMAND CENTER // DATA ERROR" tone="negative">
        <div className="p-6">
          <h1 className="font-[var(--font-display)] text-2xl font-semibold">Command Center unavailable</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
            The executive snapshot could not be loaded. No finance calculation is attempted in the browser.
          </p>
        </div>
      </TacticalFrame>
    </div>
  );
}

export function CommandCenterPage() {
  const workspace = useWorkspaceContext();
  const query = useCommandCenterSnapshot({
    companyId: workspace.companyId,
    periodId: workspace.periodId,
    scenarioId: workspace.scenarioId,
  });

  if (query.isLoading) {
    return <LoadingState />;
  }

  if (query.isError || !query.data) {
    return <ErrorState />;
  }

  const snapshot = query.data;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="grid gap-4 xl:grid-cols-[1fr_auto] xl:items-end">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">EXECUTIVE COCKPIT // FE-05</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">
            Command Center
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">
            Cross-module view of performance, liquidity, risk and management actions for {snapshot.context.companyLabel}.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" />
          <StatusIndicator label="SCENARIO" detail={snapshot.context.scenarioLabel} tone="positive" />
          <StatusIndicator label="COVERAGE" detail={snapshot.assurance.coverage} tone="positive" />
        </div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">CONTRACT BOUNDARY</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
          Executive finance values are simulated frontend fixtures. The live backend does not yet expose the aggregate
          Command Center read contract; local Company / Period / Scenario IDs are not submitted to finance APIs.
        </p>
      </div>

      <section aria-label="Executive metrics" className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-4">
        {snapshot.metrics.map((metric) => (
          <MetricPanel
            delta={metric.delta}
            deltaTone={metric.deltaTone}
            key={metric.id}
            label={metric.label}
            meta={metric.meta}
            value={metric.value}
          />
        ))}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.55fr_0.75fr]">
        <TacticalFrame
          label={`${snapshot.forecast.title} // ${snapshot.forecast.subtitle}`}
          labelAction={<span className="interface-label text-[var(--text-muted)]">{snapshot.context.periodLabel}</span>}
        >
          <div className="p-4">
            <ForecastChart points={snapshot.forecast.points} />
            <div className="mt-3 flex flex-wrap gap-5 border-t border-[var(--frame-muted)] pt-3">
              <span className="interface-label text-[var(--text-primary)]">— ACTUAL</span>
              <span className="interface-label text-[var(--signal-primary)]">— BASE</span>
              <span className="interface-label text-[var(--signal-positive)]">-- UPSIDE</span>
              <span className="interface-label text-[var(--signal-negative)]">-- DOWNSIDE</span>
            </div>
          </div>
        </TacticalFrame>

        <TacticalFrame label="LIQUIDITY ENVELOPE" tone={snapshot.liquidity.tone === "positive" ? "positive" : "default"}>
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2 2xl:grid-cols-1">
            {[
              ["CASH", snapshot.liquidity.cash],
              ["RUNWAY", snapshot.liquidity.runway],
              ["MIN HEADROOM", snapshot.liquidity.minimumHeadroom],
              ["COVENANT HEADROOM", snapshot.liquidity.covenantHeadroom],
            ].map(([label, value]) => (
              <div className="bg-[var(--surface-panel)] p-4" key={label}>
                <div className="interface-label text-[var(--text-muted)]">{label}</div>
                <div className={`data-value mt-2 text-2xl ${signalClasses[snapshot.liquidity.tone]}`}>{value}</div>
              </div>
            ))}
          </div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 xl:grid-cols-2 2xl:grid-cols-[0.9fr_1.1fr_1fr]">
        <TacticalFrame label="PERFORMANCE DRIVERS">
          <div className="divide-y divide-[var(--frame-muted)]">
            {snapshot.varianceDrivers.map((driver) => (
              <div className="grid grid-cols-[1fr_auto_auto] items-center gap-4 p-4" key={driver.label}>
                <span className="text-sm">{driver.label}</span>
                <span className={`data-value text-sm ${signalClasses[driver.tone]}`}>{driver.amount}</span>
                <span className="data-value text-xs text-[var(--text-muted)]">{driver.share}</span>
              </div>
            ))}
          </div>
          <div className="border-t border-[var(--frame-muted)] p-3 text-right">
            <Button asChild size="sm" variant="ghost">
              <Link to="/app/performance">OPEN PERFORMANCE →</Link>
            </Button>
          </div>
        </TacticalFrame>

        <TacticalFrame
          label="ENTERPRISE RISK"
          labelAction={<span className="data-value text-xs text-[var(--signal-warning)]">SCORE {snapshot.risk.score}</span>}
        >
          <div className="grid grid-cols-3 gap-px bg-[var(--frame-muted)]">
            {[
              ["EXPECTED LOSS", snapshot.risk.expectedLoss],
              ["TAIL LOSS", snapshot.risk.tailLoss],
              ["APPETITE", snapshot.risk.appetiteUsage],
            ].map(([label, value]) => (
              <div className="bg-[var(--surface-panel)] p-3" key={label}>
                <div className="interface-label text-[var(--text-muted)]">{label}</div>
                <div className="data-value mt-2 text-lg text-[var(--signal-warning)]">{value}</div>
              </div>
            ))}
          </div>
          <div className="divide-y divide-[var(--frame-muted)]">
            {snapshot.risk.signals.map((risk) => (
              <div className="grid gap-2 p-4 sm:grid-cols-[auto_1fr_auto] sm:items-center" key={risk.id}>
                <span className="data-value text-xs text-[var(--signal-primary)]">{risk.id}</span>
                <div>
                  <div className="text-sm font-medium">{risk.title}</div>
                  <div className="data-value mt-1 text-[0.62rem] text-[var(--text-muted)]">OWNER // {risk.owner}</div>
                </div>
                <div className="text-right">
                  <div className="data-value text-sm text-[var(--signal-negative)]">{risk.exposure}</div>
                  <div className="data-value mt-1 text-[0.62rem] text-[var(--text-muted)]">
                    {risk.severity} // {risk.trend}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="border-t border-[var(--frame-muted)] p-3 text-right">
            <Button asChild size="sm" variant="ghost">
              <Link to="/app/risk">OPEN RISK COMMAND →</Link>
            </Button>
          </div>
        </TacticalFrame>

        <TacticalFrame label="ASSURANCE">
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2 xl:grid-cols-1">
            <StatusIndicator label="FRESHNESS" detail={snapshot.assurance.dataFreshness} tone="positive" />
            <StatusIndicator label="DATA COVERAGE" detail={snapshot.assurance.coverage} tone="positive" />
            <StatusIndicator label="MODEL" detail={snapshot.assurance.modelStatus} tone="positive" />
            <StatusIndicator label="LINEAGE" detail={snapshot.assurance.lineageStatus} tone="positive" />
          </div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.2fr_0.8fr]">
        <TacticalFrame label="MANAGEMENT ACTION QUEUE">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-sm">
              <thead className="border-b border-[var(--frame-muted)] text-[var(--text-muted)]">
                <tr className="interface-label">
                  <th className="px-4 py-3 font-normal">ID</th>
                  <th className="px-4 py-3 font-normal">ACTION</th>
                  <th className="px-4 py-3 font-normal">OWNER</th>
                  <th className="px-4 py-3 font-normal">DUE</th>
                  <th className="px-4 py-3 font-normal">IMPACT</th>
                  <th className="px-4 py-3 font-normal">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--frame-muted)]">
                {snapshot.actions.map((action) => (
                  <tr key={action.id}>
                    <td className="data-value px-4 py-3 text-[var(--signal-primary)]">{action.id}</td>
                    <td className="px-4 py-3 font-medium">{action.title}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{action.owner}</td>
                    <td className="data-value px-4 py-3 text-[var(--text-secondary)]">{action.due}</td>
                    <td className="data-value px-4 py-3">{action.impact}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`data-value text-xs ${
                          action.status === "ON TRACK"
                            ? "text-[var(--signal-positive)]"
                            : action.status === "AT RISK"
                              ? "text-[var(--signal-warning)]"
                              : "text-[var(--signal-negative)]"
                        }`}
                      >
                        {action.status} // {action.confidence}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="border-t border-[var(--frame-muted)] p-3 text-right">
            <Button asChild size="sm" variant="ghost">
              <Link to="/app/actions">OPEN ACTION STEERING →</Link>
            </Button>
          </div>
        </TacticalFrame>

        <TacticalFrame label="CFO BRIEFING // SIMULATED" tone="active">
          <div className="p-5">
            <h2 className="font-[var(--font-display)] text-xl font-semibold leading-tight text-[var(--text-primary)]">
              {snapshot.briefing.headline}
            </h2>
            <p className="mt-4 text-sm leading-6 text-[var(--text-secondary)]">{snapshot.briefing.summary}</p>
            <div className="mt-5 border-t border-[var(--frame-muted)] pt-4">
              <div className="interface-label text-[var(--signal-primary)]">DECISIONS TO TAKE</div>
              <ol className="mt-3 grid gap-3">
                {snapshot.briefing.decisions.map((decision, index) => (
                  <li className="grid grid-cols-[1.5rem_1fr] gap-2 text-sm leading-5" key={decision}>
                    <span className="data-value text-[var(--signal-primary)]">{String(index + 1).padStart(2, "0")}</span>
                    <span>{decision}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </TacticalFrame>
      </section>
    </div>
  );
}
