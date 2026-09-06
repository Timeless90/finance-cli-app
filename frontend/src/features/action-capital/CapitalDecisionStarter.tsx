import { useState } from 'react';

import { useMutation, useQueryClient } from '@tanstack/react-query';

import { describeApiError } from '@/shared/api/errors';
import { TacticalFrame } from '@/features/finance-ui';

import {
  startCapitalMonteCarloNpv,
  startCapitalValuation,
  startFundingScenario,
  type DecisionRun,
  type DecisionRunContext,
} from './decision-runs';

type CapitalDecisionStarterProps = {
  context: DecisionRunContext;
  isLive: boolean;
  candidates: Array<{ id: string; label: string }>;
  fundingOptions: Array<{ id: string; label: string }>;
};

function RunResult({ run }: { run: DecisionRun }) {
  return (
    <div className="border-t border-[var(--frame-muted)] px-4 py-3 text-xs text-[var(--text-secondary)]">
      <div>
        <span className="data-value text-[var(--signal-primary)]">
          {run.status.toUpperCase()}
        </span>{' '}
        // RUN {run.run_id}
      </div>
      <div className="mt-1">
        MODEL {run.model_version} // SOURCES {run.source_snapshot_ids.join(', ')}
      </div>
      <details className="mt-2">
        <summary className="cursor-pointer text-[var(--signal-primary)]">
          VIEW SERVER RESULT & LINEAGE
        </summary>
        <pre className="mt-2 overflow-x-auto whitespace-pre-wrap border border-[var(--frame-muted)] p-2 text-[0.68rem]">
          {JSON.stringify({ references: run.references, result: run.result }, null, 2)}
        </pre>
      </details>
    </div>
  );
}

export function CapitalDecisionStarter({
  context,
  isLive,
  candidates,
  fundingOptions,
}: CapitalDecisionStarterProps) {
  const queryClient = useQueryClient();
  const [candidateId, setCandidateId] = useState('');
  const [fundingOptionId, setFundingOptionId] = useState('');
  const selectedCandidateId = candidateId || candidates[0]?.id || '';
  const selectedFundingOptionId = fundingOptionId || fundingOptions[0]?.id || '';
  const refresh = () =>
    queryClient.invalidateQueries({
      queryKey: [
        'decision-runs',
        context.companyId,
        context.periodId,
        context.scenarioId,
      ],
    });
  const valuation = useMutation({
    mutationFn: () => startCapitalValuation(context, selectedCandidateId),
    onSuccess: refresh,
  });
  const monteCarlo = useMutation({
    mutationFn: () => startCapitalMonteCarloNpv(context, selectedCandidateId),
    onSuccess: refresh,
  });
  const funding = useMutation({
    mutationFn: () => startFundingScenario(context, selectedFundingOptionId),
    onSuccess: refresh,
  });
  const error = valuation.error ?? monteCarlo.error ?? funding.error;
  const disabled = !isLive || context.sourceSnapshotIds.length === 0;

  return (
    <TacticalFrame label="CAPITAL VALUATION & FUNDING RUNS">
      <div className="grid gap-4 p-4 xl:grid-cols-[1fr_auto]">
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="grid gap-1 text-xs text-[var(--text-secondary)]">
            CANDIDATE
            <select
              aria-label="Capital candidate"
              className="border border-[var(--frame-muted)] bg-transparent px-2 py-2 text-sm text-[var(--text-primary)]"
              onChange={(event) => setCandidateId(event.target.value)}
              value={selectedCandidateId}
            >
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.id} // {candidate.label}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-1 text-xs text-[var(--text-secondary)]">
            FUNDING OPTION
            <select
              aria-label="Funding option"
              className="border border-[var(--frame-muted)] bg-transparent px-2 py-2 text-sm text-[var(--text-primary)]"
              onChange={(event) => setFundingOptionId(event.target.value)}
              value={selectedFundingOptionId}
            >
              {fundingOptions.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="flex flex-wrap content-end gap-2">
          <button
            className="interface-label border border-[var(--signal-primary)] px-3 py-2 text-[var(--signal-primary)] disabled:opacity-40"
            disabled={disabled || !selectedCandidateId || valuation.isPending}
            onClick={() => valuation.mutate()}
            type="button"
          >
            {valuation.isPending ? 'VALUING…' : 'VALUE CANDIDATE'}
          </button>
          <button
            className="interface-label border border-[var(--signal-primary)] px-3 py-2 text-[var(--signal-primary)] disabled:opacity-40"
            disabled={disabled || !selectedCandidateId || monteCarlo.isPending}
            onClick={() => monteCarlo.mutate()}
            type="button"
          >
            {monteCarlo.isPending ? 'SIMULATING…' : 'SIMULATE NPV'}
          </button>
          <button
            className="interface-label border border-[var(--signal-primary)] px-3 py-2 text-[var(--signal-primary)] disabled:opacity-40"
            disabled={disabled || !selectedFundingOptionId || funding.isPending}
            onClick={() => funding.mutate()}
            type="button"
          >
            {funding.isPending ? 'EVALUATING…' : 'EVALUATE FUNDING'}
          </button>
        </div>
      </div>
      {valuation.data && <RunResult run={valuation.data} />}
      {monteCarlo.data && <RunResult run={monteCarlo.data} />}
      {funding.data && <RunResult run={funding.data} />}
      {error && (
        <p className="border-t border-[var(--frame-muted)] px-4 py-3 text-xs text-[var(--signal-negative)]">
          {describeApiError(error, 'Capital decision run')}
        </p>
      )}
    </TacticalFrame>
  );
}
