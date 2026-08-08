import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import type { ProfitabilitySnapshot } from "@/features/profitability-liquidity/contracts";
import { useProfitabilitySnapshot } from "@/features/profitability-liquidity/query";

function MarginWaterfall({ steps }: { steps: ProfitabilitySnapshot["waterfall"] }) {
  const max = Math.max(...steps.map((step) => Math.abs(step.amount)), 1);
  return (
    <div className="grid min-h-72 grid-cols-6 items-end gap-2 border-b border-[var(--frame-muted)] px-3 pb-3 pt-6">
      {steps.map((step) => {
        const height = step.type === "start" || step.type === "end" ? 86 : 22 + (Math.abs(step.amount) / max) * 64;
        const tone = step.type === "negative" ? "bg-[var(--signal-negative)]" : step.type === "end" ? "bg-[var(--signal-primary)]" : step.type === "positive" ? "bg-[var(--signal-positive)]" : "bg-[var(--frame-active)]";
        return (
          <div className="grid h-full grid-rows-[1fr_auto] gap-2" key={step.id}>
            <div className="flex h-full flex-col justify-end">
              <div className="data-value mb-2 text-center text-[0.62rem] text-[var(--text-secondary)]">{step.display}</div>
              <div className={`mx-auto w-full max-w-16 ${tone}`} style={{ height: `${height}%` }} />
            </div>
            <div className="interface-label min-h-8 text-center text-[0.55rem] leading-4 text-[var(--text-muted)]">{step.label}</div>
          </div>
        );
      })}
    </div>
  );
}

export function ProfitabilityPage() {
  const workspace = useWorkspaceContext();
  const query = useProfitabilitySnapshot({
    companyId: workspace.companyId,
    periodId: workspace.periodId,
    scenarioId: workspace.scenarioId,
  });

  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading profitability workspace…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Profitability workspace unavailable.</div>;
  const snapshot = query.data;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-07 // PROFITABILITY CONTROL</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Profitability</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">
            Segment, product, customer and channel economics with allocation transparency and margin-at-risk for {snapshot.context.companyLabel}.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" />
          <StatusIndicator label="SCENARIO" detail={snapshot.context.scenarioLabel} tone="positive" />
          <StatusIndicator label="ALLOCATION" detail={snapshot.allocation.reconciled ? "RECONCILED" : "OPEN"} tone={snapshot.allocation.reconciled ? "positive" : "warning"} />
        </div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">READ CONTRACT PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
          Profitability APIs currently calculate summaries, allocations, ABC, sensitivity and margin-at-risk from supplied records. No persisted company/period/scenario profitability read model exists yet, so displayed finance values remain explicit fixtures.
        </p>
      </div>

      <section aria-label="Profitability metrics" className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-4">
        {snapshot.metrics.map((metric) => <MetricPanel delta={metric.delta} deltaTone={metric.deltaTone} key={metric.id} label={metric.label} meta={metric.meta} value={metric.value} />)}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.2fr_0.8fr]">
        <TacticalFrame label="PROFITABILITY WATERFALL // REVENUE TO EBITDA">
          <MarginWaterfall steps={snapshot.waterfall} />
        </TacticalFrame>

        <TacticalFrame label="ALLOCATION ASSURANCE">
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2 2xl:grid-cols-1">
            {[
              ["VERSION", snapshot.allocation.versionId],
              ["SOURCE SNAPSHOT", snapshot.allocation.snapshotId],
              ["METHOD", snapshot.allocation.method],
              ["SOURCE COST", snapshot.allocation.sourceCost],
              ["ALLOCATED COST", snapshot.allocation.allocatedCost],
              ["RECONCILIATION", snapshot.allocation.reconciliationDifference],
            ].map(([label, value]) => <div className="bg-[var(--surface-panel)] p-4" key={label}><div className="interface-label text-[var(--text-muted)]">{label}</div><div className="data-value mt-2 text-base text-[var(--text-primary)]">{value}</div></div>)}
          </div>
        </TacticalFrame>
      </section>

      <TacticalFrame label="SEGMENT PROFITABILITY">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-left text-sm">
            <thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">SEGMENT</th><th className="px-4 py-3 text-right font-normal">REVENUE</th><th className="px-4 py-3 text-right font-normal">CONTRIBUTION</th><th className="px-4 py-3 text-right font-normal">CM %</th><th className="px-4 py-3 text-right font-normal">EBITDA</th><th className="px-4 py-3 text-right font-normal">ALLOCATED COST</th><th className="px-4 py-3 text-right font-normal">MARGIN AT RISK</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead>
            <tbody className="divide-y divide-[var(--frame-muted)]">
              {snapshot.segments.map((segment) => (
                <tr key={segment.id}><td className="px-4 py-3 font-medium">{segment.label}</td><td className="data-value px-4 py-3 text-right">{segment.revenue}</td><td className="data-value px-4 py-3 text-right">{segment.contributionMargin}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-primary)]">{segment.contributionMarginPct}</td><td className="data-value px-4 py-3 text-right">{segment.ebitda}</td><td className="data-value px-4 py-3 text-right text-[var(--text-secondary)]">{segment.allocatedCost}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-warning)]">{segment.marginAtRisk}</td><td className={`data-value px-4 py-3 text-xs ${segment.status === "STRONG" ? "text-[var(--signal-positive)]" : segment.status === "WATCH" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{segment.status}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </TacticalFrame>

      <section className="grid gap-4 2xl:grid-cols-[1.25fr_0.75fr]">
        <TacticalFrame label="PRODUCT × CUSTOMER × CHANNEL MARGIN MATRIX">
          <div className="grid gap-2 p-4 sm:grid-cols-2">
            {snapshot.matrix.map((cell) => (
              <div className="border border-[var(--frame-muted)] bg-[var(--surface-panel)] p-4" key={cell.id}>
                <div className="flex items-start justify-between gap-4"><div><div className="font-[var(--font-display)] text-lg font-semibold">{cell.product}</div><div className="interface-label mt-1 text-[var(--text-muted)]">{cell.customer} // {cell.channel}</div></div><span className={`data-value text-xs ${cell.status === "STRONG" ? "text-[var(--signal-positive)]" : cell.status === "WATCH" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{cell.status}</span></div>
                <div className="mt-5 grid grid-cols-3 gap-3 border-t border-[var(--frame-muted)] pt-3"><div><div className="interface-label text-[var(--text-muted)]">REVENUE</div><div className="data-value mt-1 text-sm">{cell.revenue}</div></div><div><div className="interface-label text-[var(--text-muted)]">MARGIN</div><div className="data-value mt-1 text-sm text-[var(--signal-primary)]">{cell.marginPct}</div></div><div><div className="interface-label text-[var(--text-muted)]">MaR</div><div className="data-value mt-1 text-sm text-[var(--signal-warning)]">{cell.marginAtRisk}</div></div></div>
              </div>
            ))}
          </div>
        </TacticalFrame>

        <TacticalFrame label="MARGIN SENSITIVITY">
          <div className="divide-y divide-[var(--frame-muted)]">
            {snapshot.sensitivities.map((item) => (
              <div className="grid grid-cols-[1fr_auto] gap-4 p-4" key={item.lever}><div><div className="text-sm font-medium">{item.lever}</div><div className="data-value mt-1 text-xs text-[var(--text-muted)]">SHOCK // {item.movement}</div></div><div className="text-right"><div className={`data-value text-sm ${item.tone === "positive" ? "text-[var(--signal-positive)]" : "text-[var(--signal-negative)]"}`}>{item.ebitdaImpact}</div><div className="data-value mt-1 text-xs text-[var(--text-muted)]">{item.marginImpact}</div></div></div>
            ))}
          </div>
        </TacticalFrame>
      </section>
    </div>
  );
}
