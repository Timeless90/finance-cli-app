import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import type { ManagementAction } from "@/features/action-capital/contracts";
import { useActionCapitalSnapshot } from "@/features/action-capital/query";

function BenefitChart({ points }: { points: Array<{ period: string; expected: number; realized: number }> }) {
  const width = 720;
  const height = 220;
  const padding = 22;
  const max = Math.max(...points.flatMap((point) => [point.expected, point.realized]), 1) * 1.08;
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - (value / max) * (height - padding * 2);
  const line = (key: "expected" | "realized") => points.map((point, index) => `${x(index)},${y(point[key])}`).join(" ");
  return (
    <div>
      <svg aria-label="Expected and realized action benefits" className="h-56 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
        {[0.25, 0.5, 0.75].map((ratio) => <line key={ratio} stroke="var(--grid-line)" x1="0" x2={width} y1={height * ratio} y2={height * ratio} />)}
        <polyline fill="none" points={line("expected")} stroke="var(--text-muted)" strokeDasharray="7 8" strokeWidth="1.7" />
        <polyline fill="none" points={line("realized")} stroke="var(--signal-primary)" strokeWidth="2.8" />
      </svg>
      <div className="grid border-t border-[var(--frame-muted)] pt-2" style={{ gridTemplateColumns: `repeat(${points.length}, minmax(0, 1fr))` }}>
        {points.map((point) => <span className="data-value text-center text-[0.58rem] text-[var(--text-muted)]" key={point.period}>{point.period}</span>)}
      </div>
    </div>
  );
}

function statusClass(status: ManagementAction["status"]) {
  if (status === "COMPLETED") return "text-[var(--signal-positive)]";
  if (status === "AT_RISK") return "text-[var(--signal-negative)]";
  if (status === "IN_EXECUTION" || status === "APPROVED") return "text-[var(--signal-primary)]";
  return "text-[var(--signal-warning)]";
}

export function ActionsPage() {
  const workspace = useWorkspaceContext();
  const query = useActionCapitalSnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });
  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading action steering…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Action steering unavailable.</div>;
  const snapshot = query.data;
  const atRisk = snapshot.actions.queue.filter((action) => action.status === "AT_RISK").length;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-10 // VALUE REALIZATION</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Action Steering</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">Turn variance, risk and liquidity signals into owned management actions with gates, evidence and measurable benefit realization.</p>
        </div>
        <div className="flex flex-wrap gap-2"><StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" /><StatusIndicator label="SCENARIO" detail={snapshot.context.scenarioLabel} tone="positive" /><StatusIndicator label="AT RISK" detail={String(atRisk)} tone={atRisk > 0 ? "negative" : "positive"} /></div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">STEERING READ MODEL PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">The backend already exposes an action list, but FE-10 needs a governed company/period/scenario steering snapshot that joins lifecycle, evidence, source signal, benefit baseline, realized benefits and dependencies. Displayed benefit values are fixtures until that contract is available.</p>
      </div>

      <section className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-4">
        {snapshot.actions.metrics.map((metric) => <MetricPanel delta={metric.delta} deltaTone={metric.deltaTone} key={metric.id} label={metric.label} meta={metric.meta} value={metric.value} />)}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.25fr_0.75fr]">
        <TacticalFrame label="BENEFIT REALIZATION // EBITDA €M"><div className="p-4"><BenefitChart points={snapshot.actions.benefitTrend} /><div className="mt-3 flex gap-5 border-t border-[var(--frame-muted)] pt-3"><span className="interface-label text-[var(--signal-primary)]">— REALIZED</span><span className="interface-label text-[var(--text-muted)]">-- EXPECTED</span></div></div></TacticalFrame>
        <TacticalFrame label="ACTION LIFECYCLE"><div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-5 2xl:grid-cols-1">{snapshot.actions.statusMix.map((item) => <div className="flex items-center justify-between bg-[var(--surface-panel)] p-4" key={item.status}><span className={`data-value text-xs ${statusClass(item.status)}`}>{item.status.replaceAll("_", " ")}</span><span className="data-value text-xl">{item.count}</span></div>)}</div></TacticalFrame>
      </section>

      <TacticalFrame label="MANAGEMENT ACTION QUEUE">
        <div className="overflow-x-auto"><table className="w-full min-w-[1280px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">ACTION</th><th className="px-4 py-3 font-normal">SOURCE</th><th className="px-4 py-3 font-normal">OWNER</th><th className="px-4 py-3 font-normal">DUE / GATE</th><th className="px-4 py-3 text-right font-normal">CONF.</th><th className="px-4 py-3 text-right font-normal">EXPECTED EBITDA</th><th className="px-4 py-3 text-right font-normal">REALIZED EBITDA</th><th className="px-4 py-3 text-right font-normal">EXPECTED CASH</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead><tbody className="divide-y divide-[var(--frame-muted)]">{snapshot.actions.queue.map((action) => <tr key={action.id}><td className="px-4 py-3"><div className="flex items-center gap-2"><span className="data-value text-xs text-[var(--signal-primary)]">{action.id}</span><span className={`data-value text-[0.58rem] ${action.priority === "P0" ? "text-[var(--signal-negative)]" : action.priority === "P1" ? "text-[var(--signal-warning)]" : "text-[var(--text-muted)]"}`}>{action.priority}</span></div><div className="mt-1 font-medium">{action.title}</div><div className="mt-1 text-xs text-[var(--text-muted)]">Evidence: {action.evidence}</div></td><td className="px-4 py-3 text-[var(--text-secondary)]">{action.source}</td><td className="px-4 py-3"><div>{action.owner}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">SPONSOR {action.sponsor}</div></td><td className="px-4 py-3"><div className="data-value">{action.due}</div><div className="mt-1 text-xs text-[var(--text-muted)]">{action.nextGate}</div></td><td className="data-value px-4 py-3 text-right">{action.confidence}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-primary)]">{action.expectedEbitda}</td><td className="px-4 py-3 text-right"><div className="data-value text-[var(--signal-positive)]">{action.realizedEbitda}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">{action.realizationPct}</div></td><td className="data-value px-4 py-3 text-right text-[var(--signal-primary)]">{action.expectedCash}</td><td className={`data-value px-4 py-3 text-xs ${statusClass(action.status)}`}>{action.status.replaceAll("_", " ")}</td></tr>)}</tbody></table></div>
      </TacticalFrame>

      <section className="grid gap-4 xl:grid-cols-2">
        <TacticalFrame label="DEPENDENCY CONTROL"><div className="divide-y divide-[var(--frame-muted)]">{snapshot.actions.dependencies.map((dependency) => <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 p-4" key={`${dependency.actionId}-${dependency.dependsOn}`}><span className="data-value text-sm text-[var(--signal-primary)]">{dependency.actionId}</span><span className={`data-value text-[0.58rem] ${dependency.type === "BLOCKING" ? "text-[var(--signal-negative)]" : "text-[var(--signal-warning)]"}`}>{dependency.type}</span><span className="data-value text-right text-sm">{dependency.dependsOn}</span></div>)}</div></TacticalFrame>
        <TacticalFrame label="VALUE ASSURANCE"><div className="p-5"><div className="interface-label text-[var(--text-muted)]">STEERING PRINCIPLE</div><p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">Every action requires an originating signal, accountable owner, expected value baseline, evidence, next decision gate and realized-benefit trace. CFO steering should manage confidence and execution risk, not only gross opportunity value.</p><div className="mt-5 grid grid-cols-2 gap-px bg-[var(--frame-muted)]"><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">ACTIVE QUEUE</div><div className="data-value mt-2 text-xl">{snapshot.actions.queue.length}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">AT RISK</div><div className="data-value mt-2 text-xl text-[var(--signal-negative)]">{atRisk}</div></div></div></div></TacticalFrame>
      </section>
    </div>
  );
}
