import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import type { EnterpriseRisk, RiskCommandSnapshot, RiskTone } from "@/features/risk-command/contracts";
import { useRiskCommandSnapshot } from "@/features/risk-command/query";

const toneClass: Record<RiskTone, string> = {
  positive: "text-[var(--signal-positive)]",
  warning: "text-[var(--signal-warning)]",
  negative: "text-[var(--signal-negative)]",
  neutral: "text-[var(--text-secondary)]",
};

function LossDistribution({ points }: { points: RiskCommandSnapshot["portfolio"]["distribution"] }) {
  const width = 760;
  const height = 220;
  const padding = 22;
  const maxLoss = Math.max(...points.map((point) => point.loss), 1);
  const x = (percentile: number) => padding + (percentile / 100) * (width - padding * 2);
  const y = (loss: number) => height - padding - (loss / maxLoss) * (height - padding * 2);
  const line = points.map((point) => `${x(point.percentile)},${y(point.loss)}`).join(" ");

  return (
    <svg aria-label="Portfolio loss percentile curve" className="h-56 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      {[0.25, 0.5, 0.75].map((ratio) => (
        <line key={ratio} stroke="var(--grid-line)" x1="0" x2={width} y1={height * ratio} y2={height * ratio} />
      ))}
      <line stroke="var(--signal-warning)" strokeDasharray="6 8" x1={x(95)} x2={x(95)} y1="0" y2={height} />
      <line stroke="var(--signal-negative)" strokeDasharray="6 8" x1={x(99)} x2={x(99)} y1="0" y2={height} />
      <polyline fill="none" points={line} stroke="var(--signal-primary)" strokeWidth="2.8" />
      {points.map((point) => (
        <circle cx={x(point.percentile)} cy={y(point.loss)} fill="var(--signal-primary)" key={point.percentile} r="2.8" />
      ))}
    </svg>
  );
}

function RiskMatrix({ risks }: { risks: EnterpriseRisk[] }) {
  return (
    <div className="relative aspect-[1.35/1] min-h-72 overflow-hidden border border-[var(--frame-muted)] bg-[var(--surface-panel)]">
      <div className="absolute inset-0 grid grid-cols-5 grid-rows-5 opacity-90">
        {Array.from({ length: 25 }, (_, index) => {
          const row = Math.floor(index / 5);
          const column = index % 5;
          const severity = (4 - row) + column;
          const background = severity >= 7 ? "bg-[color:oklch(0.58_0.23_28/0.16)]" : severity >= 5 ? "bg-[color:oklch(0.82_0.15_85/0.12)]" : "bg-[color:oklch(0.68_0.18_145/0.08)]";
          return <div className={`border-b border-r border-[var(--grid-line)] ${background}`} key={index} />;
        })}
      </div>
      <div className="absolute bottom-2 left-3 interface-label text-[var(--text-muted)]">PROBABILITY →</div>
      <div className="absolute left-2 top-3 origin-top-left -rotate-90 -translate-x-full interface-label text-[var(--text-muted)]">IMPACT →</div>
      {risks.map((risk) => (
        <div
          className={`absolute grid h-9 w-9 -translate-x-1/2 translate-y-1/2 place-items-center rounded-full border bg-[var(--surface-canvas)] shadow-[0_0_18px_var(--glow-primary)] ${risk.status === "BREACHED" ? "border-[var(--signal-negative)] text-[var(--signal-negative)]" : risk.status === "WARNING" ? "border-[var(--signal-warning)] text-[var(--signal-warning)]" : "border-[var(--signal-primary)] text-[var(--signal-primary)]"}`}
          key={risk.id}
          style={{ left: `${8 + risk.probability * 84}%`, bottom: `${8 + risk.impact * 82}%` }}
          title={`${risk.id} ${risk.title}`}
        >
          <span className="data-value text-[0.55rem]">{risk.id.replace("R-", "")}</span>
        </div>
      ))}
    </div>
  );
}

function Radar({ data }: { data: RiskCommandSnapshot["radar"] }) {
  const size = 260;
  const center = size / 2;
  const radius = 100;
  const polar = (index: number, value: number) => {
    const angle = -Math.PI / 2 + (index / data.length) * Math.PI * 2;
    const scaled = (value / 100) * radius;
    return [center + Math.cos(angle) * scaled, center + Math.sin(angle) * scaled] as const;
  };
  const exposure = data.map((item, index) => polar(index, item.exposure).join(",")).join(" ");
  const appetite = data.map((item, index) => polar(index, item.appetite).join(",")).join(" ");

  return (
    <svg aria-label="Risk exposure radar against appetite" className="mx-auto h-72 w-full max-w-md" role="img" viewBox={`0 0 ${size} ${size}`}>
      {[25, 50, 75, 100].map((level) => (
        <polygon key={level} fill="none" points={data.map((_, index) => polar(index, level).join(",")).join(" ")} stroke="var(--grid-line)" />
      ))}
      {data.map((item, index) => {
        const [x, y] = polar(index, 100);
        const [labelX, labelY] = polar(index, 116);
        return (
          <g key={item.dimension}>
            <line stroke="var(--grid-line)" x1={center} x2={x} y1={center} y2={y} />
            <text fill="var(--text-muted)" fontFamily="var(--font-data)" fontSize="7" textAnchor="middle" x={labelX} y={labelY}>{item.dimension.toUpperCase()}</text>
          </g>
        );
      })}
      <polygon fill="var(--signal-warning)" fillOpacity="0.06" points={appetite} stroke="var(--signal-warning)" strokeDasharray="5 5" strokeWidth="1.2" />
      <polygon fill="var(--signal-primary)" fillOpacity="0.13" points={exposure} stroke="var(--signal-primary)" strokeWidth="2" />
    </svg>
  );
}

function CorrelationMatrix({ correlation }: { correlation: RiskCommandSnapshot["correlation"] }) {
  return (
    <div className="overflow-x-auto">
      <div className="grid min-w-[520px] gap-px bg-[var(--frame-muted)]" style={{ gridTemplateColumns: `7rem repeat(${correlation.labels.length}, minmax(3.5rem, 1fr))` }}>
        <div className="bg-[var(--surface-panel)] p-2" />
        {correlation.labels.map((label) => <div className="interface-label bg-[var(--surface-panel)] p-2 text-center text-[var(--text-muted)]" key={label}>{label}</div>)}
        {correlation.matrix.flatMap((row, rowIndex) => [
          <div className="interface-label bg-[var(--surface-panel)] p-2 text-[var(--text-muted)]" key={`label-${correlation.labels[rowIndex]}`}>{correlation.labels[rowIndex]}</div>,
          ...row.map((value, columnIndex) => {
            const intensity = Math.abs(value);
            return (
              <div
                className="data-value grid min-h-12 place-items-center bg-[var(--surface-panel)] text-xs"
                key={`${rowIndex}-${columnIndex}`}
                style={{ boxShadow: `inset 0 0 0 999px color-mix(in oklch, var(--signal-primary) ${Math.round(intensity * 24)}%, transparent)` }}
              >
                {value.toFixed(2)}
              </div>
            );
          }),
        ])}
      </div>
    </div>
  );
}

function QqPlot({ points }: { points: RiskCommandSnapshot["tail"]["qq"] }) {
  const width = 360;
  const height = 220;
  const padding = 24;
  const max = Math.max(...points.flatMap((point) => [point.theoretical, point.observed]), 1);
  const x = (value: number) => padding + (value / max) * (width - padding * 2);
  const y = (value: number) => height - padding - (value / max) * (height - padding * 2);
  return (
    <svg aria-label="Extreme value QQ diagnostic preview" className="h-56 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      <line stroke="var(--text-muted)" strokeDasharray="5 6" x1={x(0)} x2={x(max)} y1={y(0)} y2={y(max)} />
      {points.map((point) => <circle cx={x(point.theoretical)} cy={y(point.observed)} fill="var(--signal-primary)" key={point.theoretical} r="4" />)}
    </svg>
  );
}

export function RiskPage() {
  const workspace = useWorkspaceContext();
  const query = useRiskCommandSnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });

  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading risk command center…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Risk command center unavailable.</div>;
  const snapshot = query.data;

  const breached = snapshot.risks.filter((risk) => risk.status === "BREACHED").length;
  const warning = snapshot.risks.filter((risk) => risk.status === "WARNING").length;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-08 // ENTERPRISE RISK COMMAND</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Risk Command Center</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">Quantified enterprise risk, appetite, Monte Carlo loss distribution, controls and scenario drilldown for {snapshot.context.companyLabel}.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" />
          <StatusIndicator label="APPETITE" detail={snapshot.portfolio.appetiteUsage} tone={breached > 0 ? "negative" : warning > 0 ? "warning" : "positive"} />
          <StatusIndicator label="BREACHES" detail={String(breached)} tone={breached > 0 ? "negative" : "positive"} />
          <StatusIndicator label="MC PATHS" detail={snapshot.portfolio.paths} tone="positive" />
        </div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">RISK CONTRACT BOUNDARY</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">Risk Register reads and Monte-Carlo aggregation exist in FastAPI, but the current register is not company/period/scenario scoped and no persisted Risk Command read model exists. Regime/Markov, EVT and copula outputs are model-contract previews only and are not calculated in the browser.</p>
      </div>

      <section aria-label="Risk portfolio metrics" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
        <MetricPanel label="MEAN GROSS LOSS" meta="before controls" value={snapshot.portfolio.meanGrossLoss} />
        <MetricPanel label="MEAN NET LOSS" meta="after controls" value={snapshot.portfolio.meanNetLoss} />
        <MetricPanel label="P50 NET LOSS" meta="portfolio median" value={snapshot.portfolio.p50NetLoss} />
        <MetricPanel label="P95 / VaR" meta="loss percentile" value={snapshot.portfolio.p95NetLoss} />
        <MetricPanel label="P99 TAIL" meta="extreme percentile" value={snapshot.portfolio.p99NetLoss} />
        <MetricPanel label="ES 95 / CVaR" meta="tail mean" value={snapshot.portfolio.expectedShortfall95} />
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.2fr_0.8fr]">
        <TacticalFrame label="PORTFOLIO LOSS DISTRIBUTION // MONTE CARLO" labelAction={<span className="data-value text-xs text-[var(--text-muted)]">SEED {snapshot.portfolio.seed}</span>}>
          <div className="p-4">
            <LossDistribution points={snapshot.portfolio.distribution} />
            <div className="grid gap-px border-t border-[var(--frame-muted)] bg-[var(--frame-muted)] sm:grid-cols-4">
              {[["P95", snapshot.portfolio.p95NetLoss], ["P99", snapshot.portfolio.p99NetLoss], ["ES95", snapshot.portfolio.expectedShortfall95], ["APPETITE", snapshot.portfolio.appetiteUsage]].map(([label, value]) => <div className="bg-[var(--surface-panel)] p-3" key={label}><div className="interface-label text-[var(--text-muted)]">{label}</div><div className="data-value mt-2 text-lg">{value}</div></div>)}
            </div>
          </div>
        </TacticalFrame>

        <TacticalFrame label="PROBABILITY × IMPACT MAP">
          <div className="p-4"><RiskMatrix risks={snapshot.risks} /></div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <TacticalFrame label="RISK APPETITE RADAR"><div className="p-4"><Radar data={snapshot.radar} /><div className="mt-2 flex justify-center gap-6"><span className="interface-label text-[var(--signal-primary)]">— RESIDUAL EXPOSURE</span><span className="interface-label text-[var(--signal-warning)]">-- APPETITE</span></div></div></TacticalFrame>
        <TacticalFrame label="CATEGORY EXPOSURE">
          <div className="divide-y divide-[var(--frame-muted)]">
            {snapshot.categories.map((category) => <div className="grid grid-cols-[1fr_auto] gap-4 p-4" key={category.id}><div><div className="text-sm font-medium">{category.label}</div><div className="mt-3 h-2 overflow-hidden bg-[var(--frame-muted)]"><div className="h-full bg-[var(--signal-primary)]" style={{ width: `${category.residualExposure}%` }} /></div><div className="mt-1 flex justify-between data-value text-[0.58rem] text-[var(--text-muted)]"><span>RESIDUAL {category.residualExposure}</span><span>APPETITE {category.appetite}</span></div></div><div className={`data-value self-center text-sm ${toneClass[category.tone]}`}>{category.grossExposure} → {category.residualExposure}</div></div>)}
          </div>
        </TacticalFrame>
      </section>

      <TacticalFrame label="ENTERPRISE RISK REGISTER">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1080px] border-collapse text-left text-sm">
            <thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">ID / RISK</th><th className="px-4 py-3 font-normal">CATEGORY</th><th className="px-4 py-3 font-normal">OWNER</th><th className="px-4 py-3 text-right font-normal">PROB.</th><th className="px-4 py-3 text-right font-normal">IMPACT</th><th className="px-4 py-3 text-right font-normal">EXPECTED</th><th className="px-4 py-3 text-right font-normal">P95</th><th className="px-4 py-3 text-right font-normal">RESIDUAL</th><th className="px-4 py-3 font-normal">APPETITE</th></tr></thead>
            <tbody className="divide-y divide-[var(--frame-muted)]">{snapshot.risks.map((risk) => <tr key={risk.id}><td className="px-4 py-3"><div className="data-value text-xs text-[var(--signal-primary)]">{risk.id}</div><div className="mt-1 font-medium">{risk.title}</div></td><td className="px-4 py-3 text-[var(--text-secondary)]">{risk.category}</td><td className="px-4 py-3 text-[var(--text-secondary)]">{risk.owner}</td><td className="data-value px-4 py-3 text-right">{Math.round(risk.probability * 100)}%</td><td className="data-value px-4 py-3 text-right">{Math.round(risk.impact * 100)}%</td><td className="data-value px-4 py-3 text-right">{risk.expectedLoss}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-warning)]">{risk.p95Loss}</td><td className="data-value px-4 py-3 text-right">{risk.residualLoss}</td><td className="px-4 py-3"><div className={`data-value text-xs ${risk.status === "BREACHED" ? "text-[var(--signal-negative)]" : risk.status === "WARNING" ? "text-[var(--signal-warning)]" : "text-[var(--signal-positive)]"}`}>{risk.status} // {risk.appetiteUsage}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">TREND {risk.trend}</div></td></tr>)}</tbody>
          </table>
        </div>
      </TacticalFrame>

      <section className="grid gap-4 2xl:grid-cols-[1.05fr_0.95fr]">
        <TacticalFrame label="DEPENDENCY / CORRELATION MATRIX"><div className="p-4"><CorrelationMatrix correlation={snapshot.correlation} /><div className="interface-label mt-3 text-[var(--signal-warning)]">AGGREGATION SUPPORT EXISTS // PERSISTED MATRIX READ CONTRACT PENDING</div></div></TacticalFrame>
        <TacticalFrame label="SCENARIO DRILLDOWN" tone="active">
          <div className="p-5"><div className="interface-label text-[var(--signal-primary)]">ACTIVE RISK SCENARIO</div><h2 className="mt-3 font-[var(--font-display)] text-2xl font-semibold">{snapshot.scenario.name}</h2><p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">{snapshot.scenario.description}</p><div className="mt-5 grid grid-cols-3 gap-px bg-[var(--frame-muted)]"><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">EARNINGS AT RISK</div><div className="data-value mt-2 text-lg text-[var(--signal-negative)]">{snapshot.scenario.earningsAtRisk}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">CASH AT RISK</div><div className="data-value mt-2 text-lg text-[var(--signal-negative)]">{snapshot.scenario.cashAtRisk}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">PROBABILITY</div><div className="data-value mt-2 text-lg text-[var(--signal-warning)]">{snapshot.scenario.probability}</div></div></div><div className="mt-5 border-t border-[var(--frame-muted)] pt-4"><div className="interface-label text-[var(--text-muted)]">TOP DRIVERS</div><div className="mt-3 flex flex-wrap gap-2">{snapshot.scenario.topDrivers.map((driver) => <span className="data-value border border-[var(--frame-muted)] px-3 py-2 text-xs" key={driver}>{driver}</span>)}</div></div></div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1fr_1fr]">
        <TacticalFrame label="REGIME / MARKOV ANALYSIS" labelAction={<span className="data-value text-[0.6rem] text-[var(--signal-warning)]">MODEL CONTRACT PENDING</span>}>
          <div className="p-4"><div className="flex items-end justify-between gap-4"><div><div className="interface-label text-[var(--text-muted)]">CURRENT STATE</div><div className="mt-2 font-[var(--font-display)] text-xl font-semibold">{snapshot.regimes.currentState}</div></div><div className="text-right"><div className="interface-label text-[var(--text-muted)]">CONFIDENCE</div><div className="data-value mt-2 text-xl text-[var(--signal-warning)]">{snapshot.regimes.stateConfidence}</div></div></div><div className="mt-5 grid gap-px bg-[var(--frame-muted)] sm:grid-cols-4">{snapshot.regimes.states.map((state) => <div className="bg-[var(--surface-panel)] p-3" key={state.id}><div className="data-value text-xs text-[var(--signal-primary)]">{state.id}</div><div className="mt-2 text-sm font-medium">{state.label}</div><div className="data-value mt-3 text-lg">{Math.round(state.probability * 100)}%</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">LOSS {state.expectedLossMultiplier}</div></div>)}</div><div className="mt-4 overflow-x-auto"><div className="grid min-w-[420px] gap-px bg-[var(--frame-muted)]" style={{ gridTemplateColumns: "5rem repeat(4, 1fr)" }}><div className="bg-[var(--surface-panel)] p-2" />{snapshot.regimes.states.map((state) => <div className="data-value bg-[var(--surface-panel)] p-2 text-center text-[0.6rem] text-[var(--text-muted)]" key={state.id}>{state.id}</div>)}{snapshot.regimes.transitionMatrix.flatMap((row, rowIndex) => [<div className="data-value bg-[var(--surface-panel)] p-2 text-[0.6rem] text-[var(--text-muted)]" key={`row-${rowIndex}`}>{snapshot.regimes.states[rowIndex]?.id}</div>, ...row.map((value, colIndex) => <div className="data-value grid min-h-10 place-items-center bg-[var(--surface-panel)] text-xs" key={`${rowIndex}-${colIndex}`}>{Math.round(value * 100)}%</div>)])}</div></div></div>
        </TacticalFrame>

        <TacticalFrame label="EVT TAIL DIAGNOSTIC" labelAction={<span className="data-value text-[0.6rem] text-[var(--signal-warning)]">MODEL CONTRACT PENDING</span>}>
          <div className="grid gap-4 p-4 sm:grid-cols-[1fr_0.8fr]"><QqPlot points={snapshot.tail.qq} /><div className="grid content-start gap-px bg-[var(--frame-muted)]">{[["THRESHOLD", snapshot.tail.threshold], ["SHAPE", snapshot.tail.shape], ["SCALE", snapshot.tail.scale], ["EXPECTED SHORTFALL", snapshot.tail.expectedShortfall]].map(([label, value]) => <div className="bg-[var(--surface-panel)] p-3" key={label}><div className="interface-label text-[var(--text-muted)]">{label}</div><div className="data-value mt-2 text-base">{value}</div></div>)}</div></div>
        </TacticalFrame>
      </section>

      <TacticalFrame label="CONTROL EFFECTIVENESS & MITIGATION">
        <div className="overflow-x-auto"><table className="w-full min-w-[900px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">CONTROL</th><th className="px-4 py-3 font-normal">RISK</th><th className="px-4 py-3 font-normal">OWNER</th><th className="px-4 py-3 text-right font-normal">EFFECTIVENESS</th><th className="px-4 py-3 text-right font-normal">ANNUAL COST</th><th className="px-4 py-3 text-right font-normal">AVOIDED LOSS</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead><tbody className="divide-y divide-[var(--frame-muted)]">{snapshot.controls.map((control) => <tr key={control.id}><td className="px-4 py-3"><div className="data-value text-xs text-[var(--signal-primary)]">{control.id}</div><div className="mt-1 font-medium">{control.name}</div></td><td className="data-value px-4 py-3">{control.riskId}</td><td className="px-4 py-3 text-[var(--text-secondary)]">{control.owner}</td><td className="data-value px-4 py-3 text-right">{control.effectiveness}</td><td className="data-value px-4 py-3 text-right text-[var(--text-secondary)]">{control.annualCost}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-positive)]">{control.avoidedLoss}</td><td className={`data-value px-4 py-3 text-xs ${control.status === "ACTIVE" ? "text-[var(--signal-positive)]" : control.status === "PLANNED" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{control.status}</td></tr>)}</tbody></table></div>
      </TacticalFrame>
    </div>
  );
}
