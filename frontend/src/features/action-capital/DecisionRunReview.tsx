import { useState } from 'react';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiConfig } from '@/shared/api/config';
import { describeApiError } from '@/shared/api/errors';
import { TacticalFrame } from '@/features/finance-ui';

import {
  approveDecisionRun,
  getDecisionRuns,
  rejectDecisionRun,
  type DecisionRunContext,
  validateDecisionRun,
} from './decision-runs';

type DecisionRunReviewProps = {
  context: DecisionRunContext;
  userId: string | null;
  permissions: string[];
};

function can(permissions: string[], permission: string): boolean {
  return permissions.includes(permission);
}

export function DecisionRunReview({
  context,
  userId,
  permissions,
}: DecisionRunReviewProps) {
  const queryClient = useQueryClient();
  const [reason, setReason] = useState('');
  const queryKey = [
    'decision-runs',
    context.companyId,
    context.periodId,
    context.scenarioId,
  ];
  const runs = useQuery({
    queryKey,
    queryFn: () => getDecisionRuns(context),
    enabled: apiConfig.mode === 'live' && context.sourceSnapshotIds.length > 0,
    staleTime: 10_000,
  });
  const refresh = () => queryClient.invalidateQueries({ queryKey });
  const validation = useMutation({
    mutationFn: validateDecisionRun,
    onSuccess: refresh,
  });
  const approval = useMutation({ mutationFn: approveDecisionRun, onSuccess: refresh });
  const rejection = useMutation({
    mutationFn: (runId: string) => rejectDecisionRun(runId, reason),
    onSuccess: () => {
      setReason('');
      refresh();
    },
  });
  const error = validation.error ?? approval.error ?? rejection.error ?? runs.error;

  return (
    <TacticalFrame label="DECISION RUN REVIEW">
      {apiConfig.mode !== 'live' ? (
        <p className="p-4 text-xs text-[var(--text-secondary)]">
          Review is available only with a live backend connection.
        </p>
      ) : (
        <>
          <div className="flex flex-wrap items-end justify-between gap-3 border-b border-[var(--frame-muted)] p-4">
            <div>
              <div className="text-sm font-medium">Context-scoped review queue</div>
              <p className="mt-1 text-xs text-[var(--text-secondary)]">
                Only runs for this company, period and scenario are listed. Server
                permissions remain authoritative.
              </p>
            </div>
            <label className="grid gap-1 text-xs text-[var(--text-secondary)]">
              Rejection rationale
              <input
                aria-label="Rejection rationale"
                className="border border-[var(--frame-muted)] bg-transparent px-2 py-1 text-sm text-[var(--text-primary)]"
                onChange={(event) => setReason(event.target.value)}
                value={reason}
              />
            </label>
          </div>
          {runs.isLoading && (
            <p className="p-4 text-xs text-[var(--text-secondary)]">
              Loading decision runs…
            </p>
          )}
          {runs.data?.length === 0 && (
            <p className="p-4 text-xs text-[var(--text-secondary)]">
              No decision runs have been created for this context.
            </p>
          )}
          {runs.data && runs.data.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[840px] border-collapse text-left text-sm">
                <thead className="border-b border-[var(--frame-muted)]">
                  <tr className="interface-label text-[var(--text-muted)]">
                    <th className="px-4 py-3 font-normal">RUN</th>
                    <th className="px-4 py-3 font-normal">TYPE</th>
                    <th className="px-4 py-3 font-normal">PREPARED BY</th>
                    <th className="px-4 py-3 font-normal">STATUS</th>
                    <th className="px-4 py-3 font-normal">REVIEW</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--frame-muted)]">
                  {runs.data.map((run) => {
                    const isPreparer = run.created_by === userId;
                    const canValidate =
                      run.status === 'draft' && can(permissions, 'validate_run');
                    const canApprove =
                      run.status === 'validated' &&
                      !isPreparer &&
                      can(permissions, 'approve_run');
                    return (
                      <tr key={run.run_id}>
                        <td className="data-value px-4 py-3 text-xs text-[var(--signal-primary)]">
                          {run.run_id}
                        </td>
                        <td className="px-4 py-3">{run.kind.replaceAll('_', ' ')}</td>
                        <td className="px-4 py-3">{run.created_by}</td>
                        <td className="data-value px-4 py-3 text-xs">
                          {run.status.toUpperCase()}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            <button
                              className="interface-label border border-[var(--frame-muted)] px-2 py-1 disabled:opacity-40"
                              disabled={!canValidate || validation.isPending}
                              onClick={() => validation.mutate(run.run_id)}
                              type="button"
                            >
                              VALIDATE
                            </button>
                            <button
                              className="interface-label border border-[var(--signal-primary)] px-2 py-1 text-[var(--signal-primary)] disabled:opacity-40"
                              disabled={!canApprove || approval.isPending}
                              onClick={() => approval.mutate(run.run_id)}
                              type="button"
                            >
                              APPROVE
                            </button>
                            <button
                              className="interface-label border border-[var(--signal-negative)] px-2 py-1 text-[var(--signal-negative)] disabled:opacity-40"
                              disabled={
                                !canApprove ||
                                rejection.isPending ||
                                reason.trim().length === 0
                              }
                              onClick={() => rejection.mutate(run.run_id)}
                              type="button"
                            >
                              REJECT
                            </button>
                          </div>
                          {isPreparer && run.status === 'validated' && (
                            <p className="mt-1 text-xs text-[var(--text-muted)]">
                              Separate approver required.
                            </p>
                          )}
                          {run.rejection_reason && (
                            <p className="mt-1 text-xs text-[var(--signal-negative)]">
                              {run.rejection_reason}
                            </p>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          {error && (
            <p className="border-t border-[var(--frame-muted)] p-4 text-xs text-[var(--signal-negative)]">
              {describeApiError(error, 'Decision run review')}
            </p>
          )}
        </>
      )}
    </TacticalFrame>
  );
}
