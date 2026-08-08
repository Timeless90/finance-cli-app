import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import type { CapitalCandidate } from "@/features/action-capital/contracts";
import { useActionCapitalSnapshot } from "@/features/action-capital/query";

function Frontier({ points }: { points: Array<{ id: string; label: string; risk: number; return: number; selected: boolean }> }) {
  const width = 620;
  const height = 300;
  const padding = 45;
  const x = (risk: number) => padding + (risk / 100) * (width - padding * 2);
  const y = (value: number) => height - padding - (value / 100) * (height - padding * 2);
  return (
    <svg aria-label="Risk adjusted capital allocation frontier" className="h-72 w-full" role="img" viewBox={`0 0 ${width} ${height}`}>
      {[25, 50, 75].map((value) => <g key={value}><line stroke="var(--grid-line)" x1={x(value)} x2={x(value)} y1={padding} y2={height - padding} /><line stroke="var(--grid-line)" x1={padding} x2={width - padding} y1={y(value)} y2={y(value)} /></g>)}
      <polyline fill="none" points={points.map((point) => `${x(point.risk)},${y(point.return)}`).join(" ")} stroke="var(--signal-primary)" strokeWidth="2" />
      {points.map((point) => <g key={point.id}><circle cx={x(point.risk)} cy={y(point.return)} fill={point.selected ? "var(--signal-positive)" : "var(--surface-canvas)"} r={point.selected ? 9 : 6} stroke={point.selected ? "var(--signal-positive)" : "var(--signal-primary)"} strokeWidth="2" /><text fill="var(--text-secondary)" fontFamily="var(--font-data)" fontSize="8" textAnchor="middle" x={x(point.risk)} y={y(point.return) - 14}>{point.label}</text></g>)}
      <text fill="var(--text-muted)" fontFamily="var(--font-data)" fontSize="8" x={width / 2} y={height - 10}>RISK / CAPITAL AT RISK →</text>
      <text fill="var(--text-muted)" fontFamily="var(--font-data)" fontSize="8" x="8" y="18">VALUE ↑</text>
    </svg>
  );
}

function candidateStatusClass(status: CapitalCandidate["status"]) {
  if (status === "APPROVED") return "text-[var(--signal-positive)]";
  if (status === "DEFERRED" || status === "REJECTED") return "text-[var(--signal-negative)]";
  if (status === "SCREENED") return "text-[var(--signal-primary)]";
  return "text-[var(--signal-warning)]";
}

export function CapitalPage() {
  const workspace = useWorkspaceContext();
  const query = useActionCapitalSnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });
  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading capital allocation…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Capital allocation unavailable.</div>;
  const snapshot = query.data;
  const capital = snapshot.capital;
  const constraintBreaches = capital.constraints.filter((item) => item.status === "BREACH").length;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-10 // CAPITAL DECISION ENGINE</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Capital Allocation</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">Prioritize investment candidates against NPV, risk, strategic fit, liquidity and governance constraints rather than ranking projects by IRR alone.</p>
        </div>
        <div className="flex flex-wrap gap-2"><StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" /><StatusIndicator label="SCENARIO" detail={snapshot.context.scenarioLabel} tone="positive" /><StatusIndicator label="CONSTRAINT BREACHES" detail={String(constraintBreaches)} tone={constraintBreaches > 0 ? "negative" : "positive"} /></div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">CAPITAL PORTFOLIO READ MODEL PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">Capital ranking, constrained portfolio selection and approval evidence must remain backend-owned. FE-10 displays typed fixtures until versioned candidate, constraint, allocation-run and approval read contracts are exposed.</p>
      </div>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-7">
        <MetricPanel label="BUDGET" value={capital.budget} meta="FY26 envelope" />
        <MetricPanel label="COMMITTED" value={capital.committed} meta="in delivery" />
        <MetricPanel label="APPROVED" value={capital.approved} meta="not yet committed" />
        <MetricPanel label="UNALLOCATED" value={capital.unallocated} meta="decision capacity" />
        <MetricPanel label="LIQUIDITY RESERVE" value={capital.liquidityReserve} meta="protected cash" />
        <MetricPanel label="PORTFOLIO NPV" value={capital.expectedPortfolioNpv} meta="selected outlook" />
        <MetricPanel label="CAPITAL AT RISK" value={capital.downsideCapitalAtRisk} meta="downside exposure" />
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.05fr_0.95fr]">
        <TacticalFrame label="RISK × VALUE ALLOCATION FRONTIER"><div className="p-4"><Frontier points={capital.frontier} /><div className="interface-label mt-2 text-[var(--signal-positive)]">SELECTED POLICY // BALANCED</div></div></TacticalFrame>
        <TacticalFrame label="CAPITAL CONSTRAINTS"><div className="divide-y divide-[var(--frame-muted)]">{capital.constraints.map((constraint) => <div className="p-4" key={constraint.id}><div className="flex items-start justify-between gap-4"><div><div className="data-value text-xs text-[var(--signal-primary)]">{constraint.id}</div><div className="mt-1 text-sm font-medium">{constraint.label}</div></div><span className={`data-value text-xs ${constraint.status === "PASS" ? "text-[var(--signal-positive)]" : constraint.status === "WATCH" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{constraint.status}</span></div><div className="mt-3 grid grid-cols-3 gap-2"><div><div className="interface-label text-[var(--text-muted)]">LIMIT</div><div className="data-value mt-1 text-sm">{constraint.limit}</div></div><div><div className="interface-label text-[var(--text-muted)]">USED</div><div className="data-value mt-1 text-sm">{constraint.used}</div></div><div><div className="interface-label text-[var(--text-muted)]">HEADROOM</div><div className={`data-value mt-1 text-sm ${constraint.status === "BREACH" ? "text-[var(--signal-negative)]" : "text-[var(--signal-primary)]"}`}>{constraint.headroom}</div></div></div></div>)}</div></TacticalFrame>
      </section>

      <TacticalFrame label="INVESTMENT CANDIDATES / RISK-ADJUSTED RANKING">
        <div className="overflow-x-auto"><table className="w-full min-w-[1180px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">CANDIDATE</th><th className="px-4 py-3 font-normal">SPONSOR</th><th className="px-4 py-3 text-right font-normal">CAPITAL</th><th className="px-4 py-3 text-right font-normal">NPV</th><th className="px-4 py-3 text-right font-normal">IRR</th><th className="px-4 py-3 text-right font-normal">PAYBACK</th><th className="px-4 py-3 text-right font-normal">RA SCORE</th><th className="px-4 py-3 text-right font-normal">STRATEGIC FIT</th><th className="px-4 py-3 text-right font-normal">DOWNSIDE LOSS</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead><tbody className="divide-y divide-[var(--frame-muted)]">{[...capital.candidates].sort((a, b) => b.riskAdjustedScore - a.riskAdjustedScore).map((candidate) => <tr key={candidate.id}><td className="px-4 py-3"><div className="data-value text-xs text-[var(--signal-primary)]">{candidate.id}</div><div className="mt-1 font-medium">{candidate.name}</div><div className="mt-1 text-xs text-[var(--text-muted)]">{candidate.category} // {candidate.liquidityImpact}</div></td><td className="px-4 py-3 text-[var(--text-secondary)]">{candidate.sponsor}</td><td className="data-value px-4 py-3 text-right">{candidate.capitalRequired}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-positive)]">{candidate.npv}</td><td className="data-value px-4 py-3 text-right">{candidate.irr}</td><td className="data-value px-4 py-3 text-right">{candidate.payback}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-primary)]">{candidate.riskAdjustedScore}</td><td className="data-value px-4 py-3 text-right">{candidate.strategicFit}</td><td className="data-value px-4 py-3 text-right text-[var(--signal-warning)]">{candidate.downsideLoss}</td><td className={`data-value px-4 py-3 text-xs ${candidateStatusClass(candidate.status)}`}>{candidate.status}</td></tr>)}</tbody></table></div>
      </TacticalFrame>

      <section className="grid gap-4 2xl:grid-cols-[0.8fr_1.2fr]">
        <TacticalFrame label="SELECTED PORTFOLIO MIX"><div className="divide-y divide-[var(--frame-muted)]">{capital.allocation.map((item) => <div className="p-4" key={item.category}><div className="flex items-center justify-between gap-4"><span className="text-sm font-medium">{item.category}</span><span className="data-value text-sm">{item.amount}</span></div><div className="mt-3 h-2 bg-[var(--frame-muted)]"><div className="h-full bg-[var(--signal-primary)]" style={{ width: `${item.share}%` }} /></div><div className="mt-2 flex justify-between data-value text-[0.6rem] text-[var(--text-muted)]"><span>{item.share}% CAPITAL</span><span>NPV {item.expectedNpv}</span></div></div>)}</div></TacticalFrame>
        <TacticalFrame label="APPROVAL GATES"><div className="overflow-x-auto"><table className="w-full min-w-[680px] border-collapse text-left text-sm"><thead className="border-b border-[var(--frame-muted)]"><tr className="interface-label text-[var(--text-muted)]"><th className="px-4 py-3 font-normal">APPROVAL</th><th className="px-4 py-3 font-normal">CANDIDATE</th><th className="px-4 py-3 font-normal">GATE</th><th className="px-4 py-3 font-normal">OWNER</th><th className="px-4 py-3 font-normal">DUE</th><th className="px-4 py-3 font-normal">STATUS</th></tr></thead><tbody className="divide-y divide-[var(--frame-muted)]">{capital.approvals.map((approval) => <tr key={approval.id}><td className="data-value px-4 py-3 text-[var(--signal-primary)]">{approval.id}</td><td className="data-value px-4 py-3">{approval.candidateId}</td><td className="px-4 py-3">{approval.gate}</td><td className="px-4 py-3 text-[var(--text-secondary)]">{approval.owner}</td><td className="data-value px-4 py-3">{approval.due}</td><td className={`data-value px-4 py-3 text-xs ${approval.status === "APPROVED" ? "text-[var(--signal-positive)]" : approval.status === "PENDING" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{approval.status}</td></tr>)}</tbody></table></div></TacticalFrame>
      </section>
    </div>
  );
}
