import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { StatusIndicator, TacticalFrame } from "@/components/finance";
import type {
  MarketRiskSnapshot,
  TimePoint,
} from "@/features/market-risk/contracts";
import { useMarketRiskSnapshot } from "@/features/market-risk/query";

function LineChart({
  points,
  ariaLabel,
}: {
  points: TimePoint[];
  ariaLabel: string;
}) {
  const width = 760;
  const height = 220;
  const padding = 22;
  const values = points.flatMap((point) => [point.observed, point.fitted, point.upper, point.lower]);
  const min = Math.min(...values) - 0.12;
  const max = Math.max(...values) + 0.12;
  const range = Math.max(max - min, 1);
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);
  const poly = (selector: (point: TimePoint) => number) => points.map((point, index) => `${x(index)},${y(selector(point))}`).join(" ");
  const band = [
    ...points.map((point, index) => `${x(index)},${y(point.upper)}`),
    ...[...points].reverse().map((point, reverseIndex) => {
      const index = points.length - 1 - reverseIndex;
      return `${x(index)},${y(point.lower)}`;
    }),
  ].join(" ");

  return (
    <svg aria-label={ariaLabel} className="h-56 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      {[0.25, 0.5, 0.75].map((ratio) => <line key={ratio} stroke="var(--grid-line)" x1="0" x2={width} y1={height * ratio} y2={height * ratio} />)}
      <polygon fill="var(--signal-primary)" fillOpacity="0.06" points={band} />
      <polyline fill="none" points={poly((point) => point.observed)} stroke="var(--text-primary)" strokeWidth="1.5" />
      <polyline fill="none" points={poly((point) => point.fitted)} stroke="var(--signal-primary)" strokeWidth="2.5" />
    </svg>
  );
}

function ResidualChart({ residuals }: { residuals: MarketRiskSnapshot["garch"]["residuals"] }) {
  const width = 520;
  const height = 210;
  const padding = 20;
  const max = Math.max(...residuals.map((point) => Math.abs(point.value)), 1);
  const x = (index: number) => padding + (index / Math.max(residuals.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height / 2 - (value / max) * (height / 2 - padding);
  return (
    <svg aria-label="Standardized residual diagnostic" className="h-52 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      <line stroke="var(--frame-default)" x1="0" x2={width} y1={height / 2} y2={height / 2} />
      {residuals.map((point, index) => (
        <line key={point.index} stroke={Math.abs(point.value) > 1.8 ? "var(--signal-warning)" : "var(--signal-primary)"} strokeWidth="3" x1={x(index)} x2={x(index)} y1={height / 2} y2={y(point.value)} />
      ))}
    </svg>
  );
}

function QqChart({ points }: { points: MarketRiskSnapshot["garch"]["qq"] }) {
  const width = 360;
  const height = 210;
  const padding = 24;
  const values = points.flatMap((point) => [point.theoretical, point.observed]);
  const min = Math.min(...values) - 0.2;
  const max = Math.max(...values) + 0.2;
  const range = max - min;
  const x = (value: number) => padding + ((value - min) / range) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);
  return (
    <svg aria-label="Standardized residual QQ plot" className="h-52 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      <line stroke="var(--text-muted)" strokeDasharray="5 6" x1={x(min)} x2={x(max)} y1={y(min)} y2={y(max)} />
      {points.map((point) => <circle cx={x(point.theoretical)} cy={y(point.observed)} fill="var(--signal-primary)" key={point.theoretical} r="3.5" />)}
    </svg>
  );
}

function RegimeChart({ points }: { points: MarketRiskSnapshot["regimes"]["probabilities"] }) {
  const width = 620;
  const height = 190;
  const padding = 18;
  const x = (index: number) => padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
  const y = (probability: number) => height - padding - probability * (height - padding * 2);
  const high = points.map((point, index) => `${x(index)},${y(point.high)}`).join(" ");
  const low = points.map((point, index) => `${x(index)},${y(point.low)}`).join(" ");
  return (
    <svg aria-label="Markov regime state probabilities" className="h-48 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      <line stroke="var(--grid-line)" x1="0" x2={width} y1={y(0.5)} y2={y(0.5)} />
      <polyline fill="none" points={low} stroke="var(--signal-positive)" strokeWidth="2" />
      <polyline fill="none" points={high} stroke="var(--signal-warning)" strokeWidth="2.5" />
    </svg>
  );
}

function FanChart({ fan }: { fan: MarketRiskSnapshot["simulation"]["fan"] }) {
  const width = 760;
  const height = 230;
  const padding = 22;
  const values = fan.flatMap((point) => [point.p05, point.p25, point.p50, point.p75, point.p95]);
  const min = Math.min(...values) - 5;
  const max = Math.max(...values) + 5;
  const range = max - min;
  const x = (index: number) => padding + (index / Math.max(fan.length - 1, 1)) * (width - padding * 2);
  const y = (value: number) => height - padding - ((value - min) / range) * (height - padding * 2);
  const band = (upper: (point: (typeof fan)[number]) => number, lower: (point: (typeof fan)[number]) => number) => [
    ...fan.map((point, index) => `${x(index)},${y(upper(point))}`),
    ...[...fan].reverse().map((point, reverseIndex) => {
      const index = fan.length - 1 - reverseIndex;
      return `${x(index)},${y(lower(point))}`;
    }),
  ].join(" ");
  const median = fan.map((point, index) => `${x(index)},${y(point.p50)}`).join(" ");
  return (
    <svg aria-label="Monte Carlo market risk fan chart" className="h-60 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      {[0.25, 0.5, 0.75].map((ratio) => <line key={ratio} stroke="var(--grid-line)" x1="0" x2={width} y1={height * ratio} y2={height * ratio} />)}
      <polygon fill="var(--signal-primary)" fillOpacity="0.06" points={band((point) => point.p95, (point) => point.p05)} />
      <polygon fill="var(--signal-primary)" fillOpacity="0.12" points={band((point) => point.p75, (point) => point.p25)} />
      <polyline fill="none" points={median} stroke="var(--signal-primary)" strokeWidth="2.5" />
    </svg>
  );
}

function DependencyGraph({ dependency }: { dependency: MarketRiskSnapshot["dependency"] }) {
  const coordinates: Record<string, [number, number]> = {
    "EUR/USD": [80, 80],
    Brent: [280, 55],
    STOXX: [105, 220],
    "EUR 5Y": [300, 220],
  };
  return (
    <svg aria-label="Market risk copula dependency graph" className="h-72 w-full" role="img" viewBox="0 0 380 280">
      {dependency.edges.map((edge) => {
        const source = coordinates[edge.source] ?? [40, 40];
        const target = coordinates[edge.target] ?? [320, 240];
        return <line key={`${edge.source}-${edge.target}`} stroke={edge.correlation < 0 ? "var(--signal-warning)" : "var(--signal-primary)"} strokeOpacity={0.35 + edge.tailDependence} strokeWidth={1 + Math.abs(edge.correlation) * 5} x1={source[0]} x2={target[0]} y1={source[1]} y2={target[1]} />;
      })}
      {dependency.labels.map((label) => {
        const point = coordinates[label] ?? [190, 140];
        return <g key={label}><circle cx={point[0]} cy={point[1]} fill="var(--surface-canvas)" r="32" stroke="var(--frame-active)" strokeWidth="2" /><text fill="var(--text-primary)" fontFamily="var(--font-data)" fontSize="9" textAnchor="middle" x={point[0]} y={point[1] + 3}>{label}</text></g>;
      })}
    </svg>
  );
}

export function MarketRiskPage() {
  const workspace = useWorkspaceContext();
  const query = useMarketRiskSnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });

  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading market risk lab…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Market risk lab unavailable.</div>;
  const snapshot = query.data;
  const selectedAsset = snapshot.assets.find((asset) => asset.id === snapshot.selectedAssetId) ?? snapshot.assets[0]!;
  const breaches = snapshot.thresholds.filter((threshold) => threshold.status === "BREACH").length;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-09 // QUANT MODEL LAB</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Market Risk Lab</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">Explorable volatility, regime, dependency, simulation and backtest diagnostics for Treasury and market-risk exposures.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" />
          <StatusIndicator label="MODELS" detail="CONTRACT PENDING" tone="warning" />
          <StatusIndicator label="SCENARIO" detail={snapshot.context.scenarioLabel} tone="positive" />
          <StatusIndicator label="BREACHES" detail={String(breaches)} tone={breaches > 0 ? "negative" : "positive"} />
        </div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">MODEL CONTRACT PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">The Python CLI contains baseline Monte Carlo and statistical diagnostics, but FastAPI exposes no Market Risk run/read contracts and the repository has no production GARCH, regime or copula service. All model outputs below are simulated fixtures; the browser only renders diagnostics.</p>
      </div>

      <section aria-label="Market risk asset summary" className="grid gap-3 md:grid-cols-2 2xl:grid-cols-4">
        {snapshot.assets.map((asset) => (
          <TacticalFrame key={asset.id} label={`${asset.assetClass} // ${asset.label}`} tone={asset.status === "STRESS" ? "negative" : asset.status === "WATCH" ? "default" : "positive"}>
            <div className="p-4">
              <div className="flex items-end justify-between gap-4"><div><div className="interface-label text-[var(--text-muted)]">EXPOSURE</div><div className="data-value mt-2 text-2xl">{asset.exposure}</div></div><div className="text-right"><div className="interface-label text-[var(--text-muted)]">SPOT</div><div className="data-value mt-2 text-lg text-[var(--signal-primary)]">{asset.spot}</div></div></div>
              <div className="mt-4 grid grid-cols-3 gap-2 border-t border-[var(--frame-muted)] pt-3"><div><div className="interface-label text-[var(--text-muted)]">ANN VOL</div><div className="data-value mt-1 text-sm">{asset.annualizedVol}</div></div><div><div className="interface-label text-[var(--text-muted)]">VaR95</div><div className="data-value mt-1 text-sm">{asset.var95}</div></div><div><div className="interface-label text-[var(--text-muted)]">ES95</div><div className="data-value mt-1 text-sm">{asset.es95}</div></div></div>
            </div>
          </TacticalFrame>
        ))}
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.3fr_0.7fr]">
        <TacticalFrame label={`VOLATILITY DIAGNOSTIC // ${selectedAsset.label} // ${snapshot.garch.model}`} labelAction={<span className="data-value text-[0.6rem] text-[var(--signal-warning)]">MODEL CONTRACT PENDING</span>}>
          <div className="p-4"><LineChart ariaLabel="Observed and GARCH fitted volatility" points={snapshot.garch.volatility} /><div className="mt-3 flex gap-5 border-t border-[var(--frame-muted)] pt-3"><span className="interface-label text-[var(--text-primary)]">— OBSERVED</span><span className="interface-label text-[var(--signal-primary)]">— FITTED</span><span className="interface-label text-[var(--signal-primary)]">SHADE // INTERVAL</span></div></div>
        </TacticalFrame>
        <TacticalFrame label="GARCH RUN ASSURANCE">
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2 2xl:grid-cols-1">{[["RUN", snapshot.garch.runId], ["CONVERGENCE", snapshot.garch.convergence], ["PERSISTENCE", snapshot.garch.persistence], ["UNCONDITIONAL VOL", snapshot.garch.unconditionalVol], ["AIC", snapshot.garch.aic], ["BIC", snapshot.garch.bic]].map(([label, value]) => <div className="bg-[var(--surface-panel)] p-3" key={label}><div className="interface-label text-[var(--text-muted)]">{label}</div><div className="data-value mt-2 text-base">{value}</div></div>)}</div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <TacticalFrame label="GARCH PARAMETERS"><div className="overflow-x-auto"><table className="w-full min-w-[460px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-3 py-2 font-normal">PARAM</th><th className="px-3 py-2 text-right font-normal">EST.</th><th className="px-3 py-2 text-right font-normal">SE</th><th className="px-3 py-2 text-right font-normal">T</th><th className="px-3 py-2 text-right font-normal">P</th></tr></thead><tbody>{snapshot.garch.parameters.map((parameter) => <tr className="border-b border-[var(--frame-muted)]" key={parameter.name}><td className="data-value px-3 py-3 text-[var(--signal-primary)]">{parameter.name}</td><td className="data-value px-3 py-3 text-right">{parameter.estimate}</td><td className="data-value px-3 py-3 text-right text-[var(--text-secondary)]">{parameter.stdError}</td><td className="data-value px-3 py-3 text-right">{parameter.tStat}</td><td className="data-value px-3 py-3 text-right">{parameter.pValue}</td></tr>)}</tbody></table></div></TacticalFrame>
        <TacticalFrame label="STANDARDIZED RESIDUALS"><div className="p-4"><ResidualChart residuals={snapshot.garch.residuals} /></div></TacticalFrame>
        <TacticalFrame label="QQ / TAIL DIAGNOSTIC"><div className="p-4"><QqChart points={snapshot.garch.qq} /></div></TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.05fr_0.95fr]">
        <TacticalFrame label={`REGIME VIEW // ${snapshot.regimes.model}`} labelAction={<span className="data-value text-[0.6rem] text-[var(--signal-warning)]">MODEL CONTRACT PENDING</span>}>
          <div className="p-4"><RegimeChart points={snapshot.regimes.probabilities} /><div className="mt-4 grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2">{snapshot.regimes.states.map((state) => <div className="bg-[var(--surface-panel)] p-4" key={state.id}><div className="flex items-center justify-between"><span className="data-value text-xs text-[var(--signal-primary)]">{state.id}</span><span className="data-value text-xs">{Math.round(state.probability * 100)}%</span></div><div className="mt-3 font-[var(--font-display)] text-lg font-semibold">{state.label}</div><div className="mt-3 grid grid-cols-2 gap-2"><div><div className="interface-label text-[var(--text-muted)]">MEAN</div><div className="data-value mt-1">{state.mean}</div></div><div><div className="interface-label text-[var(--text-muted)]">VOL</div><div className="data-value mt-1">{state.volatility}</div></div></div></div>)}</div></div>
        </TacticalFrame>
        <TacticalFrame label="REGIME TRANSITION MATRIX"><div className="p-4"><div className="mb-4 flex items-end justify-between"><div><div className="interface-label text-[var(--text-muted)]">CURRENT STATE</div><div className="mt-2 font-[var(--font-display)] text-xl font-semibold">{snapshot.regimes.currentState}</div></div><div className="data-value text-xl text-[var(--signal-warning)]">{snapshot.regimes.confidence}</div></div><div className="grid grid-cols-3 gap-px bg-[var(--frame-muted)]"><div className="bg-[var(--surface-panel)] p-3" /><div className="data-value bg-[var(--surface-panel)] p-3 text-center text-xs">LOW</div><div className="data-value bg-[var(--surface-panel)] p-3 text-center text-xs">HIGH</div>{snapshot.regimes.transitionMatrix.flatMap((row, rowIndex) => [<div className="data-value bg-[var(--surface-panel)] p-3 text-xs" key={`row-${rowIndex}`}>{rowIndex === 0 ? "LOW" : "HIGH"}</div>, ...row.map((value, columnIndex) => <div className="data-value grid min-h-14 place-items-center bg-[var(--surface-panel)] text-lg" key={`${rowIndex}-${columnIndex}`}>{Math.round(value * 100)}%</div>)])}</div></div></TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[0.9fr_1.1fr]">
        <TacticalFrame label={`DEPENDENCY // ${snapshot.dependency.model}`} labelAction={<span className="data-value text-[0.6rem] text-[var(--signal-warning)]">MODEL CONTRACT PENDING</span>}><div className="p-4"><DependencyGraph dependency={snapshot.dependency} /><div className="grid grid-cols-3 gap-px bg-[var(--frame-muted)]"><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">DOF</div><div className="data-value mt-2 text-lg">{snapshot.dependency.dof}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">TAIL DEP.</div><div className="data-value mt-2 text-lg">{snapshot.dependency.tailDependence}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">LOG-LIK.</div><div className="data-value mt-2 text-lg">{snapshot.dependency.logLikelihood}</div></div></div></div></TacticalFrame>
        <TacticalFrame label="MARGINAL DISTRIBUTION FITS"><div className="overflow-x-auto"><table className="w-full min-w-[700px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-3 py-3 font-normal">ASSET</th><th className="px-3 py-3 font-normal">FAMILY</th><th className="px-3 py-3 text-right font-normal">LOCATION</th><th className="px-3 py-3 text-right font-normal">SCALE</th><th className="px-3 py-3 text-right font-normal">DOF</th><th className="px-3 py-3 text-right font-normal">AIC</th><th className="px-3 py-3 text-right font-normal">KS P</th></tr></thead><tbody className="divide-y divide-[var(--frame-muted)]">{snapshot.marginals.map((item) => <tr key={item.assetId}><td className="data-value px-3 py-3 text-[var(--signal-primary)]">{item.assetId.toUpperCase()}</td><td className="px-3 py-3">{item.family}</td><td className="data-value px-3 py-3 text-right">{item.location}</td><td className="data-value px-3 py-3 text-right">{item.scale}</td><td className="data-value px-3 py-3 text-right">{item.dof}</td><td className="data-value px-3 py-3 text-right">{item.aic}</td><td className="data-value px-3 py-3 text-right">{item.ksPValue}</td></tr>)}</tbody></table></div></TacticalFrame>
      </section>

      <TacticalFrame label={`MONTE CARLO FAN // ${snapshot.simulation.horizon}`} labelAction={<span className="data-value text-xs text-[var(--text-muted)]">{snapshot.simulation.paths} PATHS // SEED {snapshot.simulation.seed}</span>}>
        <div className="p-4"><FanChart fan={snapshot.simulation.fan} /><div className="mt-3 grid grid-cols-2 gap-px bg-[var(--frame-muted)] sm:grid-cols-4"><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">RUN</div><div className="data-value mt-2 truncate text-sm">{snapshot.simulation.runId}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">VaR95</div><div className="data-value mt-2 text-lg text-[var(--signal-warning)]">{snapshot.simulation.var95}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">ES95</div><div className="data-value mt-2 text-lg text-[var(--signal-negative)]">{snapshot.simulation.es95}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">MODEL</div><div className="data-value mt-2 text-sm">GARCH + REGIME + COPULA</div></div></div></div>
      </TacticalFrame>

      <section className="grid gap-4 2xl:grid-cols-[1fr_1fr]">
        <TacticalFrame label="BACKTEST RESULTS"><div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-4"><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">OBSERVATIONS</div><div className="data-value mt-2 text-lg">{snapshot.backtest.observations}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">EXCEPTIONS</div><div className="data-value mt-2 text-lg">{snapshot.backtest.varExceptions}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">KUPIEC P</div><div className="data-value mt-2 text-lg">{snapshot.backtest.kupiecPValue}</div></div><div className="bg-[var(--surface-panel)] p-3"><div className="interface-label text-[var(--text-muted)]">TRAFFIC LIGHT</div><div className={`data-value mt-2 text-lg ${snapshot.backtest.trafficLight === "GREEN" ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{snapshot.backtest.trafficLight}</div></div></div><div className="divide-y divide-[var(--frame-muted)]">{snapshot.backtest.breaches.map((breach) => <div className="grid gap-2 p-4 sm:grid-cols-[auto_1fr_auto] sm:items-center" key={breach.date}><span className="data-value text-xs text-[var(--signal-primary)]">{breach.date}</span><div><div className="text-sm font-medium">Return {breach.return} vs VaR {breach.varLimit}</div><div className="mt-1 text-xs text-[var(--text-secondary)]">{breach.note}</div></div><span className={`data-value text-xs ${breach.documented ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{breach.documented ? "DOCUMENTED" : "ACTION REQUIRED"}</span></div>)}</div></TacticalFrame>
        <TacticalFrame label="THRESHOLD BREACH DOCUMENTATION"><div className="divide-y divide-[var(--frame-muted)]">{snapshot.thresholds.map((threshold) => <div className="p-4" key={threshold.id}><div className="flex items-start justify-between gap-4"><div><div className="data-value text-xs text-[var(--signal-primary)]">{threshold.id}</div><div className="mt-1 text-sm font-medium">{threshold.metric}</div></div><span className={`data-value text-xs ${threshold.status === "NORMAL" ? "text-[var(--signal-positive)]" : threshold.status === "WARNING" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{threshold.status}</span></div><div className="mt-3 grid grid-cols-3 gap-2"><div><div className="interface-label text-[var(--text-muted)]">CURRENT</div><div className="data-value mt-1">{threshold.current}</div></div><div><div className="interface-label text-[var(--text-muted)]">WARNING</div><div className="data-value mt-1">{threshold.warning}</div></div><div><div className="interface-label text-[var(--text-muted)]">BREACH</div><div className="data-value mt-1">{threshold.breach}</div></div></div><div className="mt-3 border-t border-[var(--frame-muted)] pt-2 text-xs text-[var(--text-secondary)]">{threshold.documentation}</div></div>)}</div></TacticalFrame>
      </section>

      <TacticalFrame label="MODEL COMPARISON / CHAMPION-CHALLENGER">
        <div className="overflow-x-auto"><table className="w-full min-w-[900px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">MODEL</th><th className="px-4 py-3 text-right font-normal">AIC</th><th className="px-4 py-3 text-right font-normal">BIC</th><th className="px-4 py-3 text-right font-normal">OOS LOSS</th><th className="px-4 py-3 text-right font-normal">VaR COVERAGE</th><th className="px-4 py-3 font-normal">TAIL FIT</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead><tbody className="divide-y divide-[var(--frame-muted)]">{snapshot.modelComparison.map((model) => <tr key={model.id}><td className="px-4 py-3"><span className="data-value mr-3 text-xs text-[var(--signal-primary)]">{model.id}</span><span className="font-medium">{model.model}</span></td><td className="data-value px-4 py-3 text-right">{model.aic}</td><td className="data-value px-4 py-3 text-right">{model.bic}</td><td className="data-value px-4 py-3 text-right">{model.outOfSampleLoss}</td><td className="data-value px-4 py-3 text-right">{model.varCoverage}</td><td className="data-value px-4 py-3">{model.tailFit}</td><td className={`data-value px-4 py-3 text-xs ${model.status === "CHAMPION" ? "text-[var(--signal-positive)]" : model.status === "CANDIDATE" ? "text-[var(--signal-warning)]" : "text-[var(--text-muted)]"}`}>{model.status}</td></tr>)}</tbody></table></div>
      </TacticalFrame>
    </div>
  );
}
