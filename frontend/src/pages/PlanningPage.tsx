import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import type { ForecastSeriesPoint } from "@/features/planning-performance/contracts";
import { usePlanningSnapshot } from "@/features/planning-performance/query";

function ForecastChart({ points }: { points: ForecastSeriesPoint[] }) {
  const width = 820;
  const height = 240;
  const padding = 20;
  const values = points.flatMap((point) => [point.plan, point.forecast, point.lower, point.upper]);
  const min = Math.min(...values) - 1;
  const max = Math.max(...values) + 1;
  const range = Math.max(max - min, 1);
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);
  const polyline = (selector: (point: ForecastSeriesPoint) => number) =>
    points.map((point, index) => `${x(index)},${y(selector(point))}`).join(" ");
  const actual = points
    .map((point, index) => (point.actual === undefined ? null : `${x(index)},${y(point.actual)}`))
    .filter((point): point is string => point !== null)
    .join(" ");
  const corridor = [
    ...points.map((point, index) => `${x(index)},${y(point.upper)}`),
    ...[...points].reverse().map((point, reverseIndex) => {
      const index = points.length - 1 - reverseIndex;
      return `${x(index)},${y(point.lower)}`;
    }),
  ].join(" ");

  return (
    <div>
      <svg aria-label="EBITDA rolling forecast with confidence corridor" className="h-60 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
        {[0.25, 0.5, 0.75].map((ratio) => (
          <line key={ratio} stroke="var(--grid-line)" x1="0" x2={width} y1={height * ratio} y2={height * ratio} />
        ))}
        <polygon fill="var(--signal-primary)" fillOpacity="0.08" points={corridor} />
        <polyline fill="none" points={polyline((point) => point.plan)} stroke="var(--text-muted)" strokeDasharray="7 8" strokeWidth="1.5" />
        <polyline fill="none" points={polyline((point) => point.forecast)} stroke="var(--signal-primary)" strokeWidth="2.8" />
        <polyline fill="none" points={actual} stroke="var(--text-primary)" strokeWidth="2" />
      </svg>
      <div className="grid grid-cols-5 border-t border-[var(--frame-muted)] pt-2 sm:grid-cols-10">
        {points.map((point) => (
          <span className="data-value text-center text-[0.58rem] text-[var(--text-muted)]" key={point.period}>{point.period}</span>
        ))}
      </div>
    </div>
  );
}

export function PlanningPage() {
  const workspace = useWorkspaceContext();
  const query = usePlanningSnapshot({
    companyId: workspace.companyId,
    periodId: workspace.periodId,
    scenarioId: workspace.scenarioId,
  });

  if (query.isLoading) {
    return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading planning workspace…</div>;
  }
  if (query.isError || !query.data) {
    return <div className="p-6 text-sm text-[var(--signal-negative)]">Planning workspace unavailable.</div>;
  }

  const snapshot = query.data;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-06 // ROLLING FORECAST CONTROL</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Planning</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">
            Scenario steering, forecast versions, financial statement outlook and operational assumptions for {snapshot.context.companyLabel}.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" />
          <StatusIndicator label="VERSION" detail={snapshot.activeScenario.status} tone="positive" />
          <StatusIndicator label="CONFIDENCE" detail={snapshot.forecast.confidence} tone="positive" />
        </div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">READ CONTRACT PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
          The backend can create forecasts and retrieve a forecast by known version ID, but it does not yet expose a company/period scoped forecast catalog or planning workspace read model. Displayed finance values are simulated fixtures.
        </p>
      </div>

      <section aria-label="Planning scenarios" className="grid gap-3 md:grid-cols-3">
        {snapshot.scenarios.map((scenario) => {
          const active = scenario.id === workspace.scenarioId;
          return (
            <button
              className={`border p-4 text-left transition-colors ${active ? "border-[var(--frame-active)] bg-[var(--surface-panel-hover)]" : "border-[var(--frame-muted)] bg-[var(--surface-panel)] hover:border-[var(--frame-default)]"}`}
              key={scenario.id}
              onClick={() => workspace.setScenarioId(scenario.id)}
              type="button"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="data-value text-xs text-[var(--signal-primary)]">{scenario.type}</span>
                <span className={`data-value text-[0.62rem] ${active ? "text-[var(--signal-positive)]" : "text-[var(--text-muted)]"}`}>{active ? "SELECTED" : scenario.status}</span>
              </div>
              <div className="mt-4 font-[var(--font-display)] text-lg font-semibold">{scenario.label}</div>
              <div className="mt-4 grid grid-cols-3 gap-2 border-t border-[var(--frame-muted)] pt-3">
                <div><div className="interface-label text-[var(--text-muted)]">REV</div><div className="data-value mt-1 text-sm">{scenario.revenue}</div></div>
                <div><div className="interface-label text-[var(--text-muted)]">EBITDA</div><div className="data-value mt-1 text-sm">{scenario.ebitda}</div></div>
                <div><div className="interface-label text-[var(--text-muted)]">FCF</div><div className="data-value mt-1 text-sm">{scenario.freeCashFlow}</div></div>
              </div>
            </button>
          );
        })}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.45fr_0.55fr]">
        <TacticalFrame label={`ROLLING FORECAST // ${snapshot.forecast.kpi} // ${snapshot.forecast.horizon}`} labelAction={<span className="interface-label text-[var(--text-muted)]">{snapshot.context.scenarioLabel}</span>}>
          <div className="p-4">
            <ForecastChart points={snapshot.forecast.points} />
            <div className="mt-3 flex flex-wrap gap-5 border-t border-[var(--frame-muted)] pt-3">
              <span className="interface-label text-[var(--text-primary)]">— ACTUAL</span>
              <span className="interface-label text-[var(--signal-primary)]">— FORECAST</span>
              <span className="interface-label text-[var(--text-muted)]">-- PLAN</span>
              <span className="interface-label text-[var(--signal-primary)]">SHADE // CONFIDENCE</span>
            </div>
          </div>
        </TacticalFrame>

        <TacticalFrame label="FORECAST ASSURANCE">
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-3 2xl:grid-cols-1">
            <MetricPanel label="CONFIDENCE" value={snapshot.forecast.confidence} meta="mock interval coverage" />
            <MetricPanel label="MAPE" value={snapshot.forecast.mape} meta="rolling backtest" />
            <MetricPanel label="BIAS" value={snapshot.forecast.bias} meta="signed forecast error" />
          </div>
          <div className="border-t border-[var(--frame-muted)] p-4">
            <div className="interface-label text-[var(--text-muted)]">VERSION TRACE</div>
            <dl className="mt-3 grid gap-2 text-xs">
              {[
                ["VERSION", snapshot.activeScenario.versionId],
                ["SNAPSHOT", snapshot.activeScenario.snapshotId],
                ["ASSUMPTIONS", snapshot.activeScenario.assumptionSetId],
                ["MODEL", snapshot.activeScenario.modelVersion],
              ].map(([label, value]) => (
                <div className="grid grid-cols-[7rem_1fr] gap-2" key={label}><dt className="data-value text-[var(--text-muted)]">{label}</dt><dd className="data-value m-0 truncate text-[var(--text-secondary)]">{value}</dd></div>
              ))}
            </dl>
          </div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.35fr_0.65fr]">
        <TacticalFrame label={`INCOME STATEMENT OUTLOOK // ${snapshot.context.periodLabel}`}>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-sm">
              <thead className="border-b border-[var(--frame-muted)]">
                <tr className="interface-label text-[var(--text-muted)]">
                  <th className="px-4 py-3 font-normal">LINE ITEM</th><th className="px-4 py-3 text-right font-normal">ACTUAL YTD</th><th className="px-4 py-3 text-right font-normal">PLAN YTD</th><th className="px-4 py-3 text-right font-normal">FY FORECAST</th><th className="px-4 py-3 text-right font-normal">VARIANCE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--frame-muted)]">
                {snapshot.statement.map((row) => (
                  <tr className={row.level === 0 ? "bg-[color:oklch(0.18_0.018_43/0.45)]" : ""} key={row.id}>
                    <td className={`px-4 py-3 ${row.level === 0 ? "font-semibold" : "pl-8 text-[var(--text-secondary)]"}`}>{row.label}</td>
                    <td className="data-value px-4 py-3 text-right">{row.actual}</td><td className="data-value px-4 py-3 text-right text-[var(--text-secondary)]">{row.plan}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-primary)]">{row.forecast}</td>
                    <td className={`data-value px-4 py-3 text-right ${row.varianceTone === "positive" ? "text-[var(--signal-positive)]" : row.varianceTone === "negative" ? "text-[var(--signal-negative)]" : "text-[var(--text-secondary)]"}`}>{row.variance}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TacticalFrame>

        <TacticalFrame label="GOAL THRESHOLDS">
          <div className="divide-y divide-[var(--frame-muted)]">
            {snapshot.thresholds.map((threshold) => (
              <div className="p-4" key={threshold.kpi}>
                <div className="flex items-start justify-between gap-3"><span className="text-sm font-medium">{threshold.kpi}</span><span className={`data-value text-xs ${threshold.status === "ON_TARGET" ? "text-[var(--signal-positive)]" : threshold.status === "WARNING" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{threshold.status}</span></div>
                <div className="data-value mt-3 text-2xl">{threshold.current}</div>
                <div className="data-value mt-2 text-[0.62rem] text-[var(--text-muted)]">TARGET {threshold.target} // WARNING {threshold.warning}</div>
              </div>
            ))}
          </div>
        </TacticalFrame>
      </section>

      <TacticalFrame label="PLANNING DRIVERS & ASSUMPTIONS">
        <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2 xl:grid-cols-3">
          {snapshot.drivers.map((driver) => (
            <div className="bg-[var(--surface-panel)] p-4" key={driver.id}>
              <div className="flex items-center justify-between gap-3"><span className="interface-label text-[var(--text-muted)]">{driver.label}</span><span className={`data-value text-[0.62rem] ${driver.status === "LOCKED" ? "text-[var(--signal-positive)]" : driver.status === "REVIEW" ? "text-[var(--signal-warning)]" : "text-[var(--text-secondary)]"}`}>{driver.status}</span></div>
              <div className="mt-3 flex items-end gap-2"><span className="data-value text-2xl">{driver.value}</span><span className="data-value pb-1 text-xs text-[var(--text-muted)]">{driver.unit}</span></div>
              <div className="data-value mt-2 text-xs text-[var(--signal-primary)]">{driver.delta}</div>
              <div className="interface-label mt-4 border-t border-[var(--frame-muted)] pt-2 text-[var(--text-muted)]">OWNER // {driver.owner}</div>
            </div>
          ))}
        </div>
      </TacticalFrame>
    </div>
  );
}
