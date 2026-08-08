import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import type { PerformanceTrendPoint, VarianceStep } from "@/features/planning-performance/contracts";
import { usePerformanceSnapshot } from "@/features/planning-performance/query";

function VarianceBridge({ steps }: { steps: VarianceStep[] }) {
  const max = Math.max(...steps.map((step) => Math.abs(step.amount)), 1);
  return (
    <div className="grid min-h-64 grid-cols-7 items-end gap-2 border-b border-[var(--frame-muted)] px-3 pb-3 pt-6">
      {steps.map((step) => {
        const height = step.type === "start" || step.type === "end" ? 82 : 24 + (Math.abs(step.amount) / max) * 58;
        const barClass = step.type === "positive" ? "bg-[var(--signal-positive)]" : step.type === "negative" ? "bg-[var(--signal-negative)]" : step.type === "end" ? "bg-[var(--signal-primary)]" : "bg-[var(--frame-active)]";
        return (
          <div className="grid h-full grid-rows-[1fr_auto] items-end gap-2" key={step.id}>
            <div className="flex h-full flex-col justify-end">
              <div className="data-value mb-2 text-center text-[0.62rem] text-[var(--text-secondary)]">{step.display}</div>
              <div className={`mx-auto w-full max-w-14 ${barClass}`} style={{ height: `${height}%` }} />
            </div>
            <div className="interface-label min-h-8 text-center text-[0.56rem] leading-4 text-[var(--text-muted)]">{step.label}</div>
          </div>
        );
      })}
    </div>
  );
}

function TrendChart({ points }: { points: PerformanceTrendPoint[] }) {
  const width = 720;
  const height = 210;
  const padding = 20;
  const values = points.flatMap((point) => [point.actual, point.plan, point.forecast]);
  const min = Math.min(...values) - 0.8;
  const max = Math.max(...values) + 0.8;
  const range = Math.max(max - min, 1);
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);
  const line = (selector: (point: PerformanceTrendPoint) => number) => points.map((point, index) => `${x(index)},${y(selector(point))}`).join(" ");

  return (
    <div>
      <svg aria-label="EBITDA margin actual plan and forecast trend" className="h-52 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
        {[0.25, 0.5, 0.75].map((ratio) => <line key={ratio} stroke="var(--grid-line)" x1="0" x2={width} y1={height * ratio} y2={height * ratio} />)}
        <polyline fill="none" points={line((point) => point.plan)} stroke="var(--text-muted)" strokeDasharray="7 8" strokeWidth="1.5" />
        <polyline fill="none" points={line((point) => point.forecast)} stroke="var(--signal-primary)" strokeWidth="2.5" />
        <polyline fill="none" points={line((point) => point.actual)} stroke="var(--text-primary)" strokeWidth="2" />
      </svg>
      <div className="grid border-t border-[var(--frame-muted)] pt-2" style={{ gridTemplateColumns: `repeat(${points.length}, minmax(0, 1fr))` }}>
        {points.map((point) => <span className="data-value text-center text-[0.58rem] text-[var(--text-muted)]" key={point.period}>{point.period}</span>)}
      </div>
    </div>
  );
}

export function PerformancePage() {
  const workspace = useWorkspaceContext();
  const query = usePerformanceSnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });

  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading performance workspace…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Performance workspace unavailable.</div>;
  const snapshot = query.data;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-06 // PERFORMANCE CONTROL</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Performance</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">KPI decomposition, variance explanation, forecast accuracy signals and management commentary control for {snapshot.context.companyLabel}.</p>
        </div>
        <div className="flex flex-wrap gap-2"><StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" /><StatusIndicator label="SCENARIO" detail={snapshot.context.scenarioLabel} tone="positive" /><StatusIndicator label="VARIANCE" detail={snapshot.varianceBridge.fullyExplained ? "EXPLAINED" : "OPEN"} tone={snapshot.varianceBridge.fullyExplained ? "positive" : "warning"} /></div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">READ CONTRACT PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">The backend currently evaluates KPI trees, variance bridges, accuracy, anomalies and commentary requirements through calculation-oriented POST APIs. FE-06 does not fabricate authoritative source snapshots in the browser; the workspace uses labelled fixtures until persisted read models are exposed.</p>
      </div>

      <section aria-label="Performance metrics" className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-4">
        {snapshot.metrics.map((metric) => <MetricPanel delta={metric.delta} deltaTone={metric.deltaTone} key={metric.id} label={metric.label} meta={metric.meta} value={metric.value} />)}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.1fr_0.9fr]">
        <TacticalFrame label={`VARIANCE BRIDGE // ${snapshot.varianceBridge.kpi} // ${snapshot.varianceBridge.comparison}`} labelAction={<span className="data-value text-xs text-[var(--signal-positive)]">{snapshot.varianceBridge.explained} EXPLAINED</span>}>
          <VarianceBridge steps={snapshot.varianceBridge.steps} />
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-4">
            {[["BASELINE", snapshot.varianceBridge.baseline], ["ACTUAL / OUTLOOK", snapshot.varianceBridge.actual], ["EXPLAINED", snapshot.varianceBridge.explained], ["UNEXPLAINED", snapshot.varianceBridge.unexplained]].map(([label, value]) => <div className="bg-[var(--surface-panel)] p-3" key={label}><div className="interface-label text-[var(--text-muted)]">{label}</div><div className="data-value mt-2 text-lg">{value}</div></div>)}
          </div>
        </TacticalFrame>

        <TacticalFrame label={`TREND // ${snapshot.trend.kpi}`}>
          <div className="p-4"><TrendChart points={snapshot.trend.points} /><div className="mt-3 flex gap-5 border-t border-[var(--frame-muted)] pt-3"><span className="interface-label text-[var(--text-primary)]">— ACTUAL</span><span className="interface-label text-[var(--signal-primary)]">— FORECAST</span><span className="interface-label text-[var(--text-muted)]">-- PLAN</span></div></div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1fr_1fr]">
        <TacticalFrame label="CFO KPI TREE">
          <div className="grid gap-2 p-4">
            {snapshot.kpiTree.map((node) => (
              <div className={`grid grid-cols-[1fr_auto_auto] items-center gap-4 border border-[var(--frame-muted)] bg-[var(--surface-panel)] px-4 py-3 ${node.parentId ? "ml-6" : "border-[var(--frame-active)]"}`} key={node.id}>
                <div><div className="text-sm font-medium">{node.label}</div>{node.parentId && <div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">DRIVER OF // {node.parentId.toUpperCase()}</div>}</div>
                <div className="data-value text-sm">{node.value}</div>
                <div className={`data-value text-xs ${node.tone === "positive" ? "text-[var(--signal-positive)]" : node.tone === "negative" ? "text-[var(--signal-negative)]" : "text-[var(--text-secondary)]"}`}>{node.variance}</div>
              </div>
            ))}
          </div>
        </TacticalFrame>

        <TacticalFrame label="ANOMALY SIGNALS">
          <div className="divide-y divide-[var(--frame-muted)]">
            {snapshot.anomalies.map((anomaly) => (
              <div className="grid gap-3 p-4 sm:grid-cols-[auto_1fr_auto] sm:items-center" key={anomaly.id}>
                <span className="data-value text-xs text-[var(--signal-primary)]">{anomaly.id}</span>
                <div><div className="text-sm font-medium">{anomaly.kpi} // {anomaly.period}</div><div className="mt-1 text-xs text-[var(--text-secondary)]">{anomaly.observation}</div></div>
                <div className="text-right"><div className={`data-value text-xs ${anomaly.severity === "HIGH" ? "text-[var(--signal-negative)]" : anomaly.severity === "MEDIUM" ? "text-[var(--signal-warning)]" : "text-[var(--signal-positive)]"}`}>{anomaly.severity}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">{anomaly.status}</div></div>
              </div>
            ))}
          </div>
        </TacticalFrame>
      </section>

      <TacticalFrame label="MANAGEMENT COMMENTARY CONTROL">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left text-sm">
            <thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">ID</th><th className="px-4 py-3 font-normal">KPI</th><th className="px-4 py-3 text-right font-normal">VARIANCE</th><th className="px-4 py-3 text-right font-normal">MATERIALITY</th><th className="px-4 py-3 font-normal">OWNER</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead>
            <tbody className="divide-y divide-[var(--frame-muted)]">
              {snapshot.commentary.map((item) => <tr key={item.id}><td className="data-value px-4 py-3 text-[var(--signal-primary)]">{item.id}</td><td className="px-4 py-3 font-medium">{item.kpi}</td><td className="data-value px-4 py-3 text-right">{item.variance}</td><td className="data-value px-4 py-3 text-right text-[var(--text-secondary)]">{item.threshold}</td><td className="px-4 py-3 text-[var(--text-secondary)]">{item.owner}</td><td className={`data-value px-4 py-3 text-xs ${item.status === "COMPLETE" ? "text-[var(--signal-positive)]" : item.status === "REQUIRED" ? "text-[var(--signal-warning)]" : "text-[var(--text-muted)]"}`}>{item.status}</td></tr>)}
            </tbody>
          </table>
        </div>
      </TacticalFrame>
    </div>
  );
}
