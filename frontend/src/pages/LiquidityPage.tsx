import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import type { CashPoint } from "@/features/profitability-liquidity/contracts";
import { useLiquiditySnapshot } from "@/features/profitability-liquidity/query";

function CashForecastChart({ points }: { points: CashPoint[] }) {
  const width = 820;
  const height = 240;
  const padding = 20;
  const values = points.flatMap((point) => [point.closing, point.minimum]);
  const min = Math.min(...values) - 3;
  const max = Math.max(...values) + 3;
  const range = Math.max(max - min, 1);
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);
  const line = (selector: (point: CashPoint) => number) => points.map((point, index) => `${x(index)},${y(selector(point))}`).join(" ");

  return (
    <div>
      <svg aria-label="13 week closing cash forecast and minimum liquidity threshold" className="h-60 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
        {[0.25, 0.5, 0.75].map((ratio) => <line key={ratio} stroke="var(--grid-line)" x1="0" x2={width} y1={height * ratio} y2={height * ratio} />)}
        <polyline fill="none" points={line((point) => point.minimum)} stroke="var(--signal-negative)" strokeDasharray="7 8" strokeWidth="1.5" />
        <polyline fill="none" points={line((point) => point.closing)} stroke="var(--signal-primary)" strokeWidth="2.8" />
        {points.map((point, index) => <circle cx={x(index)} cy={y(point.closing)} fill="var(--signal-primary)" key={point.period} r="3" />)}
      </svg>
      <div className="grid grid-cols-7 border-t border-[var(--frame-muted)] pt-2 sm:grid-cols-13">
        {points.map((point) => <span className="data-value text-center text-[0.55rem] text-[var(--text-muted)]" key={point.period}>{point.period}</span>)}
      </div>
    </div>
  );
}

export function LiquidityPage() {
  const workspace = useWorkspaceContext();
  const query = useLiquiditySnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });

  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading liquidity workspace…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Liquidity workspace unavailable.</div>;
  const snapshot = query.data;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-07 // LIQUIDITY CONTROL</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Liquidity</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">13-week cash, working capital, debt, covenant and liquidity stress control for {snapshot.context.companyLabel}.</p>
        </div>
        <div className="flex flex-wrap gap-2"><StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" /><StatusIndicator label="SCENARIO" detail={snapshot.context.scenarioLabel} tone="positive" /><StatusIndicator label="ACCURACY" detail={snapshot.cashForecast.forecastAccuracy} tone="positive" /></div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">READ CONTRACT PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">Liquidity APIs calculate cash forecasts, working capital, debt schedules, covenants, stresses and forecast accuracy from supplied source data. FE-07 does not synthesize those source inputs in the browser; persisted workspace read models are still required.</p>
      </div>

      <section aria-label="Liquidity metrics" className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-4">
        {snapshot.metrics.map((metric) => <MetricPanel delta={metric.delta} deltaTone={metric.deltaTone} key={metric.id} label={metric.label} meta={metric.meta} value={metric.value} />)}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.35fr_0.65fr]">
        <TacticalFrame label="13-WEEK CASH FORECAST" labelAction={<span className="interface-label text-[var(--text-muted)]">MIN LIQ {snapshot.cashForecast.minimumLiquidity}</span>}>
          <div className="p-4"><CashForecastChart points={snapshot.cashForecast.points} /><div className="mt-3 flex gap-5 border-t border-[var(--frame-muted)] pt-3"><span className="interface-label text-[var(--signal-primary)]">— CLOSING CASH</span><span className="interface-label text-[var(--signal-negative)]">-- MINIMUM LIQUIDITY</span></div></div>
        </TacticalFrame>

        <TacticalFrame label="WORKING CAPITAL">
          <div className="divide-y divide-[var(--frame-muted)]">
            {snapshot.workingCapital.map((item) => <div className="p-4" key={item.id}><div className="flex items-start justify-between gap-4"><div><div className="text-sm font-medium">{item.label}</div><div className="data-value mt-1 text-[0.6rem] text-[var(--text-muted)]">TARGET // {item.target}</div></div><span className={`data-value text-xs ${item.status === "ON_TARGET" ? "text-[var(--signal-positive)]" : item.status === "WATCH" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{item.status}</span></div><div className="mt-3 flex items-end justify-between gap-4"><span className="data-value text-2xl">{item.current}</span><span className={`data-value text-sm ${item.cashImpact.startsWith("+") ? "text-[var(--signal-positive)]" : "text-[var(--signal-negative)]"}`}>{item.cashImpact}</span></div></div>)}
          </div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1fr_1fr]">
        <TacticalFrame label="DEBT & FUNDING">
          <div className="overflow-x-auto"><table className="w-full min-w-[720px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">INSTRUMENT</th><th className="px-4 py-3 text-right font-normal">PRINCIPAL</th><th className="px-4 py-3 text-right font-normal">RATE</th><th className="px-4 py-3 font-normal">MATURITY</th><th className="px-4 py-3 text-right font-normal">HEADROOM</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead><tbody className="divide-y divide-[var(--frame-muted)]">{snapshot.debt.map((item) => <tr key={item.id}><td className="px-4 py-3"><div className="font-medium">{item.instrument}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">{item.id} // LIMIT {item.committedLimit}</div></td><td className="data-value px-4 py-3 text-right">{item.principal}</td><td className="data-value px-4 py-3 text-right">{item.rate}</td><td className="data-value px-4 py-3 text-[var(--text-secondary)]">{item.maturity}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-primary)]">{item.headroom}</td><td className={`data-value px-4 py-3 text-xs ${item.status === "NORMAL" ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{item.status}</td></tr>)}</tbody></table></div>
        </TacticalFrame>

        <TacticalFrame label="COVENANT MONITOR">
          <div className="divide-y divide-[var(--frame-muted)]">{snapshot.covenants.map((item) => <div className="grid gap-3 p-4 sm:grid-cols-[1fr_auto_auto] sm:items-center" key={item.id}><div><div className="text-sm font-medium">{item.metric}</div><div className="data-value mt-1 text-[0.6rem] text-[var(--text-muted)]">{item.id} // LIMIT {item.threshold}</div></div><div className="sm:text-right"><div className="interface-label text-[var(--text-muted)]">ACTUAL</div><div className="data-value mt-1 text-base">{item.actual}</div></div><div className="sm:text-right"><div className={`data-value text-xs ${item.status === "PASS" ? "text-[var(--signal-positive)]" : item.status === "WATCH" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{item.status}</div><div className="data-value mt-1 text-[0.6rem] text-[var(--text-muted)]">HEADROOM {item.headroom} // MIN {item.projectedMinimum}</div></div></div>)}</div>
        </TacticalFrame>
      </section>

      <TacticalFrame label="LIQUIDITY STRESS MATRIX">
        <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2 xl:grid-cols-4">
          {snapshot.stresses.map((stress) => <div className="bg-[var(--surface-panel)] p-4" key={stress.id}><div className="flex items-start justify-between gap-3"><span className="data-value text-xs text-[var(--signal-primary)]">{stress.id}</span><span className={`data-value text-xs ${stress.breach ? "text-[var(--signal-negative)]" : "text-[var(--signal-positive)]"}`}>{stress.breach ? "BREACH" : "PASS"}</span></div><div className="mt-4 min-h-10 text-sm font-medium">{stress.name}</div><div className="mt-4 grid grid-cols-2 gap-3 border-t border-[var(--frame-muted)] pt-3"><div><div className="interface-label text-[var(--text-muted)]">CASH</div><div className="data-value mt-1 text-lg">{stress.closingCash}</div></div><div><div className="interface-label text-[var(--text-muted)]">HEADROOM</div><div className={`data-value mt-1 text-lg ${stress.breach ? "text-[var(--signal-negative)]" : "text-[var(--signal-positive)]"}`}>{stress.headroom}</div></div></div><div className="interface-label mt-4 text-[var(--text-muted)]">MITIGATION // {stress.mitigation}</div></div>)}
        </div>
      </TacticalFrame>
    </div>
  );
}
