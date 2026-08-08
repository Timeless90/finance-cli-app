import { useWorkspaceContext } from "@/app/context/useWorkspaceContext";
import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import { useReportingCopilotSnapshot } from "@/features/reporting-copilot/query";

export function ReportsPage() {
  const workspace = useWorkspaceContext();
  const query = useReportingCopilotSnapshot({ companyId: workspace.companyId, periodId: workspace.periodId, scenarioId: workspace.scenarioId });
  if (query.isLoading) return <div className="p-6 text-sm text-[var(--text-secondary)]">Loading reporting studio…</div>;
  if (query.isError || !query.data) return <div className="p-6 text-sm text-[var(--signal-negative)]">Reporting studio unavailable.</div>;
  const { reporting, context } = query.data;
  const highOpen = reporting.findings.filter((finding) => finding.status === "OPEN" && finding.severity === "HIGH").length;

  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">FE-11 // REPORTING STUDIO</div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">Reporting Studio</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">Versioned, auditable CFO reporting with source lineage, narrative review, publication gates and evidence-ready exports for {context.companyLabel}.</p>
        </div>
        <div className="flex flex-wrap gap-2"><StatusIndicator label="DATA" detail="MOCK CONNECTED" tone="warning" /><StatusIndicator label="REPORT" detail={reporting.activeReport.status} tone="warning" /><StatusIndicator label="HIGH FINDINGS" detail={String(highOpen)} tone={highOpen > 0 ? "negative" : "positive"} /></div>
      </section>

      <div className="border border-[var(--signal-warning)] bg-[color:oklch(0.82_0.15_85/0.06)] px-4 py-3">
        <div className="interface-label text-[var(--signal-warning)]">REPORTING CONTRACT PENDING</div>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">Narratives, source binding, report versions and exports must be generated and persisted by backend services. This screen visualizes fixtures only and does not generate regulated or board-facing prose in the browser.</p>
      </div>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricPanel label="COMPLETENESS" value={reporting.activeReport.completeness} meta="approved + reviewed sections" />
        <MetricPanel label="SOURCE COVERAGE" value={reporting.activeReport.sourceCoverage} meta="validated source pack" />
        <MetricPanel label="OPEN FINDINGS" value={String(reporting.activeReport.unresolvedFindings)} meta="publication blockers / review items" />
        <MetricPanel label="CURRENT VERSION" value={reporting.activeReport.currentVersionId.split("-").at(-1)?.toUpperCase() ?? "V?"} meta={reporting.activeReport.template} />
      </section>

      <section className="grid gap-4 2xl:grid-cols-[1.15fr_0.85fr]">
        <TacticalFrame label="ACTIVE REPORT / SECTION CONTROL">
          <div className="border-b border-[var(--frame-muted)] p-5"><div className="interface-label text-[var(--signal-primary)]">{reporting.activeReport.id}</div><h2 className="mt-2 font-[var(--font-display)] text-2xl font-semibold">{reporting.activeReport.title}</h2><div className="mt-3 flex flex-wrap gap-4 data-value text-xs text-[var(--text-muted)]"><span>DATE {reporting.activeReport.reportingDate}</span><span>REVIEWER {reporting.activeReport.reviewer}</span><span>APPROVER {reporting.activeReport.approver}</span></div></div>
          <div className="divide-y divide-[var(--frame-muted)]">{reporting.sections.map((section) => <div className="grid gap-3 p-4 sm:grid-cols-[auto_1fr_auto] sm:items-center" key={section.id}><span className="data-value text-xs text-[var(--signal-primary)]">{section.id}</span><div><div className="font-medium">{section.title}</div><div className="mt-1 text-xs text-[var(--text-secondary)]">{section.purpose}</div><div className="data-value mt-2 text-[0.58rem] text-[var(--text-muted)]">OWNER {section.owner} // {section.sourceCount} SOURCES // {section.wordCount} WORDS</div></div><div className="text-right"><div className={`data-value text-xs ${section.status === "APPROVED" ? "text-[var(--signal-positive)]" : section.status === "REVIEWED" ? "text-[var(--signal-primary)]" : "text-[var(--signal-warning)]"}`}>{section.status}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">{section.materiality}</div></div></div>)}</div>
        </TacticalFrame>

        <TacticalFrame label="VERSION / LINEAGE">
          <div className="divide-y divide-[var(--frame-muted)]">{reporting.versions.map((version) => <div className="p-4" key={version.id}><div className="flex items-start justify-between gap-4"><div><div className="data-value text-xs text-[var(--signal-primary)]">{version.id}</div><div className="mt-1 text-sm font-medium">{version.label}</div></div><span className={`data-value text-xs ${version.status === "APPROVED" ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{version.status}</span></div><div className="mt-3 text-xs text-[var(--text-secondary)]">{version.createdAt} // {version.createdBy}</div><div className="data-value mt-2 text-[0.58rem] text-[var(--text-muted)]">SNAPSHOTS {version.sourceSnapshotIds.length} // MODEL RUNS {version.modelRunIds.length} // {version.checksum}</div></div>)}</div>
        </TacticalFrame>
      </section>

      <section className="grid gap-4 2xl:grid-cols-[0.95fr_1.05fr]">
        <TacticalFrame label="SOURCE PACK"><div className="divide-y divide-[var(--frame-muted)]">{reporting.sourcePack.map((source) => <div className="grid grid-cols-[auto_1fr_auto] items-center gap-3 p-4" key={source.id}><span className="data-value text-xs text-[var(--signal-primary)]">{source.id}</span><div><div className="text-sm font-medium">{source.label}</div><div className="data-value mt-1 text-[0.58rem] text-[var(--text-muted)]">{source.type} // {source.owner} // {source.asOf}</div></div><span className={`data-value text-xs ${source.status === "VALIDATED" ? "text-[var(--signal-positive)]" : source.status === "STALE" ? "text-[var(--signal-warning)]" : "text-[var(--signal-negative)]"}`}>{source.status}</span></div>)}</div></TacticalFrame>
        <TacticalFrame label="NARRATIVE PREVIEW"><div className="divide-y divide-[var(--frame-muted)]">{reporting.narrativePreview.map((narrative) => <article className="p-5" key={narrative.id}><div className="flex items-center justify-between"><h3 className="font-[var(--font-display)] text-lg font-semibold">{narrative.heading}</h3><span className={`data-value text-xs ${narrative.status === "REVIEWED" ? "text-[var(--signal-positive)]" : "text-[var(--signal-warning)]"}`}>{narrative.status}</span></div><p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">{narrative.content}</p><div className="mt-3 flex flex-wrap gap-2">{narrative.citations.map((citation) => <span className="data-value border border-[var(--frame-muted)] px-2 py-1 text-[0.58rem] text-[var(--signal-primary)]" key={citation}>{citation}</span>)}</div></article>)}</div></TacticalFrame>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <TacticalFrame label="REVIEW FINDINGS"><div className="divide-y divide-[var(--frame-muted)]">{reporting.findings.map((finding) => <div className="grid gap-2 p-4 sm:grid-cols-[auto_1fr_auto] sm:items-center" key={finding.id}><span className={`data-value text-xs ${finding.severity === "HIGH" ? "text-[var(--signal-negative)]" : finding.severity === "MEDIUM" ? "text-[var(--signal-warning)]" : "text-[var(--text-muted)]"}`}>{finding.id} // {finding.severity}</span><div><div className="text-sm font-medium">{finding.finding}</div><div className="mt-1 text-xs text-[var(--text-muted)]">{finding.section} // {finding.owner}</div></div><span className="data-value text-xs text-[var(--signal-warning)]">{finding.status}</span></div>)}</div></TacticalFrame>
        <TacticalFrame label="EXPORT TARGETS"><div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2">{reporting.exportTargets.map((target) => <div className="bg-[var(--surface-panel)] p-4" key={target.id}><div className="flex items-start justify-between"><span className="data-value text-xs text-[var(--signal-primary)]">{target.format}</span><span className={`data-value text-xs ${target.status === "READY" ? "text-[var(--signal-positive)]" : "text-[var(--signal-negative)]"}`}>{target.status}</span></div><div className="mt-3 text-sm font-medium">{target.label}</div><div className="mt-2 text-xs text-[var(--text-secondary)]">{target.note}</div></div>)}</div></TacticalFrame>
      </section>
    </div>
  );
}
