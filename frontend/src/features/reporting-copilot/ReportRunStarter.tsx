import { useState } from 'react';

import { createManagementPackRun, type ReportRun } from './report-runs';

export function ReportRunStarter({
  companyId,
  periodId,
  scenarioId,
  sourceSnapshotIds,
  projectionVersion,
}: {
  companyId: string;
  periodId: string;
  scenarioId: string;
  sourceSnapshotIds: string[];
  projectionVersion: number;
}) {
  const [run, setRun] = useState<ReportRun>();
  const [error, setError] = useState<string>();
  const [pending, setPending] = useState(false);
  const start = async () => {
    setPending(true);
    setError(undefined);
    try {
      setRun(
        await createManagementPackRun({
          companyId,
          periodId,
          scenarioId,
          sourceSnapshotIds,
          projectionVersion,
        }),
      );
    } catch {
      setError(
        'Report creation failed. Confirm that a published source is available for the active context.',
      );
    } finally {
      setPending(false);
    }
  };
  return (
    <div className="border border-[var(--frame-muted)] bg-[var(--surface-panel)] p-4">
      <div className="interface-label text-[var(--signal-primary)]">
        SERVER-OWNED REPORT RUN
      </div>
      <p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">
        Creates a Management Pack from backend-bound published sources. The browser
        sends context and source IDs, never financial values or narrative content.
      </p>
      <button
        className="interface-label mt-3 border border-[var(--signal-primary)] px-3 py-2 text-[var(--signal-primary)] disabled:opacity-50"
        disabled={pending || sourceSnapshotIds.length === 0}
        onClick={() => void start()}
        type="button"
      >
        {pending ? 'CREATING…' : 'CREATE MANAGEMENT PACK'}
      </button>
      {error && (
        <p className="mt-2 text-xs text-[var(--signal-negative)]" role="alert">
          {error}
        </p>
      )}
      {run && (
        <div className="mt-3 text-xs text-[var(--text-secondary)]">
          <span className="data-value text-[var(--signal-positive)]">
            {run.status.toUpperCase()} // {run.report_id}
          </span>
          <div className="mt-1">
            Artifact {run.artifact_status.toUpperCase()} · {run.section_count}{' '}
            source-bound sections · {run.content_hash.slice(0, 12)}
          </div>
        </div>
      )}
    </div>
  );
}
