import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { StatusIndicator, TacticalFrame } from "@/components/finance";
import { useReportingCopilotSnapshot } from "@/features/reporting-copilot/query";

export function CopilotPage() {
  const workspace = useWorkspaceContext();
  const query = useReportingCopilotSnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });
  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading Financial Copilot…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Financial Copilot unavailable.</div>;
  const { copilot, context } = query.data;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-11 // GROUNDED FINANCE ASSISTANT</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Financial Copilot</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">Grounded finance reasoning across validated snapshots, model runs, risk, actions and reports for {context.companyLabel}. No uncited numeric claims and no autonomous writes.</p>
        </div>
        <div className="flex flex-wrap gap-2"><StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" /><StatusIndicator label="COPILOT" detail="CONTRACT PENDING" tone="warning" /><StatusIndicator label="GROUNDING" detail="VALIDATED ONLY" tone="positive" /></div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">COPILOT CONTRACT PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">The browser does not call Foundry deployments directly, select production models, synthesize source citations or execute writes. A backend orchestration contract must enforce identity, grounding, model routing, citations, tool authorization and audit logging.</p>
      </div>

      <section className="grid gap-4 2xl:grid-cols-[0.72fr_1.28fr]">
        <div className="grid content-start gap-4">
          <TacticalFrame label="GROUNDING CONTEXT"><div className="divide-y divide-[var(--frame-muted)]">{copilot.contextSources.map((source) => <div className="flex items-center justify-between gap-4 p-4" key={source.id}><div><div className="text-sm font-medium">{source.label}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">{source.type} // {source.id}</div></div><div className="text-right"><div className={`data-value text-xs ${source.status === "VALIDATED" ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{source.status}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">{source.enabled ? "ENABLED" : "DISABLED"}</div></div></div>)}</div></TacticalFrame>

          <TacticalFrame label="MODEL ROUTING / FOUNDRY"><div className="divide-y divide-[var(--frame-muted)]">{copilot.routes.map((route) => <div className="p-4" key={route.id}><div className="flex items-start justify-between gap-3"><div><div className="data-value text-xs text-[var(--signal-primary)]">{route.id}</div><div className="mt-1 text-sm font-medium">{route.workload}</div></div><span className={`data-value text-xs ${route.status === "ACTIVE" ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{route.status}</span></div><div className="mt-3 grid grid-cols-2 gap-2"><div><div className="interface-label text-[var(--text-muted)]">MODEL ROLE</div><div className="data-value mt-1 text-xs">{route.modelLabel}</div></div><div><div className="interface-label text-[var(--text-muted)]">REASONING</div><div className="data-value mt-1 text-xs">{route.reasoning}</div></div></div><div className="data-value mt-2 truncate text-[0.58rem] text-[var(--text-muted)]">DEPLOYMENT // {route.deployment}</div></div>)}</div></TacticalFrame>

          <TacticalFrame label="GUARDRAILS"><div className="divide-y divide-[var(--frame-muted)]">{copilot.guardrails.map((guardrail) => <div className="p-4" key={guardrail.id}><div className="flex items-center justify-between gap-3"><span className="text-sm font-medium">{guardrail.label}</span><span className={`data-value text-xs ${guardrail.status === "ENFORCED" ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{guardrail.status}</span></div><p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">{guardrail.detail}</p></div>)}</div></TacticalFrame>
        </div>

        <div className="grid content-start gap-4">
          <TacticalFrame label={`COPILOT SESSION // ${copilot.sessionId}`} tone="active">
            <div className="divide-y divide-[var(--frame-muted)]">{copilot.messages.map((message) => <div className={`p-5 ${message.role === "ASSISTANT" ? "bg-[color:oklch(0.18_0.018_43/0.42)]" : ""}`} key={message.id}><div className="flex items-center justify-between gap-4"><span className={`data-value text-xs ${message.role === "ASSISTANT" ? "text-[var(--signal-primary)]" : "text-[var(--text-muted)]"}`}>{message.role}</span><span className="data-value text-[0.58rem] text-[var(--text-muted)]">{message.createdAt}</span></div><p className="mt-3 text-sm leading-7 text-[var(--text-primary)]">{message.content}</p>{message.role === "ASSISTANT" && <div className="mt-4"><div className="flex flex-wrap gap-3 data-value text-[0.58rem] text-[var(--text-muted)]"><span>CONFIDENCE {message.confidence}</span><span>ROUTE {message.routeId}</span><span>MODEL {message.modelLabel}</span></div><div className="mt-3 grid gap-2">{message.citations.map((citation) => <div className="border border-[var(--frame-muted)] bg-[var(--surface-panel)] p-3" key={citation.id}><div className="flex items-center justify-between gap-3"><span className="data-value text-[0.6rem] text-[var(--signal-primary)]">{citation.id} // {citation.sourceType}</span><span className={`data-value text-[0.58rem] ${citation.verified ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{citation.verified ? "VERIFIED" : "UNVERIFIED"}</span></div><div className="mt-1 text-xs font-medium">{citation.label}</div><div className="mt-1 text-xs text-[var(--text-secondary)]">{citation.excerpt}</div><div className="data-value mt-1 text-[0.56rem] text-[var(--text-muted)]">SOURCE {citation.sourceId}</div></div>)}</div></div>}</div>)}</div>
            <div className="border-t border-[var(--frame-muted)] p-4"><label className="interface-label text-[var(--text-muted)]" htmlFor="copilot-prompt">ASK FINANCE</label><div className="mt-2 grid gap-2 sm:grid-cols-[1fr_auto]"><textarea className="min-h-24 resize-y border border-[var(--frame-default)] bg-[var(--surface-canvas)] p-3 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--frame-active)]" id="copilot-prompt" placeholder="Ask a grounded question…" readOnly value="" /><button className="interface-label min-h-12 border border-[var(--signal-primary)] px-5 text-[var(--signal-primary)] opacity-60" disabled type="button">SEND // BACKEND PENDING</button></div></div>
          </TacticalFrame>

          <TacticalFrame label="SUGGESTED GROUNDED PROMPTS"><div className="grid gap-2 p-4 sm:grid-cols-2">{copilot.suggestedPrompts.map((prompt) => <button className="border border-[var(--frame-muted)] bg-[var(--surface-panel)] p-3 text-left text-xs leading-5 text-[var(--text-secondary)] hover:border-[var(--frame-active)]" key={prompt} type="button">{prompt}</button>)}</div></TacticalFrame>

          <TacticalFrame label="PROPOSED MANAGEMENT ACTIONS"><div className="divide-y divide-[var(--frame-muted)]">{copilot.proposedActions.map((action) => <div className="grid gap-3 p-4 sm:grid-cols-[1fr_auto]" key={action.id}><div><div className="data-value text-xs text-[var(--signal-primary)]">{action.id}</div><div className="mt-1 text-sm font-medium">{action.title}</div><p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">{action.sourceInsight}</p><div className="data-value mt-2 text-[0.58rem] text-[var(--text-muted)]">IMPACT {action.estimatedImpact} // CONFIDENCE {action.confidence}</div></div><div className="self-center text-right"><span className="data-value text-xs text-[var(--signal-warning)]">{action.status.replaceAll("_", " ")}</span><button className="interface-label mt-3 block border border-[var(--frame-muted)] px-3 py-2 text-[var(--text-muted)] opacity-60" disabled type="button">REVIEW</button></div></div>)}</div></TacticalFrame>
        </div>
      </section>
    </div>
  );
}
