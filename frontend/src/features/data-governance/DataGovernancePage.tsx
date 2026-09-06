import type { DataImportResponse } from '@/generated/models';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { apiClient } from '@/shared/api/client';
import { apiConfig } from '@/shared/api/config';
import { describeApiError, toApiContractError } from '@/shared/api/errors';
import { useWorkspaceContext } from '@/app/context/useWorkspaceContext';
import { StatusIndicator, TacticalFrame } from '@/features/finance-ui';

type Item = Record<string, unknown>;
type Import = DataImportResponse;
type SourceAccount = { account: string; total: string };
type PlanningMapping = {
  mapping_set_id: string;
  source_snapshot_id: string;
  version_label: string;
  status: string;
  mappings: Array<{
    source_account: string;
    category: string;
    sign_multiplier: string;
  }>;
};
type PlanningBaseline = {
  baseline_id: string;
  forecast_eligible: boolean;
  missing_categories: string[];
  values: Record<string, string>;
};
type AccountMappingInput = { category: string; sign_multiplier: string };
const items = (value: unknown): Item[] =>
  Array.isArray(value)
    ? value.filter((item): item is Item => item !== null && typeof item === 'object')
    : [];
const value = (item: Item, key: string, fallback = '—') =>
  typeof item[key] === 'string' || typeof item[key] === 'number'
    ? String(item[key])
    : fallback;

const planningCategories = [
  'revenue',
  'variable_cost',
  'personnel_cost',
  'fixed_operating_cost',
  'depreciation',
  'cash',
  'accounts_receivable',
  'inventory',
  'accounts_payable',
  'debt',
  'other',
];

function defaultPlanningMapping(account: string): AccountMappingInput {
  if (account.startsWith('4')) return { category: 'revenue', sign_multiplier: '1' };
  if (account.startsWith('5'))
    return { category: 'variable_cost', sign_multiplier: '-1' };
  if (account.startsWith('6'))
    return { category: 'fixed_operating_cost', sign_multiplier: '-1' };
  if (account === '1000') return { category: 'cash', sign_multiplier: '-1' };
  return { category: 'other', sign_multiplier: '1' };
}

const localActors = [
  { id: 'developer', label: 'DEVELOPER / PREPARER' },
  { id: 'reviewer', label: 'LOCAL REVIEWER' },
  { id: 'approver', label: 'LOCAL APPROVER' },
];

async function fileBase64(file: File) {
  const buffer = await file.arrayBuffer();
  let binary = '';
  new Uint8Array(buffer).forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return window.btoa(binary);
}

export function DataGovernancePage() {
  const workspace = useWorkspaceContext();
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [mapping, setMapping] = useState('{}');
  const [expectedTotal, setExpectedTotal] = useState('0');
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [actor, setActor] = useState(
    () => window.localStorage.getItem('cfo-local-actor') ?? 'developer',
  );
  const [sourceImportId, setSourceImportId] = useState('');
  const [planningMapping, setPlanningMapping] = useState<
    Record<string, AccountMappingInput>
  >({});
  const workspaceQuery = useQuery({
    queryKey: [
      'data-governance',
      workspace.companyId,
      workspace.periodId,
      workspace.scenarioId,
    ],
    queryFn: async () => {
      if (apiConfig.mode === 'mock')
        throw new Error('Data & Governance requires the live API.');
      const { data, error, response } = await apiClient.GET(
        '/api/v1/data-governance/workspace',
        {
          params: {
            query: {
              company_id: workspace.companyId,
              period_id: workspace.periodId,
              scenario_id: workspace.scenarioId,
            },
          },
        } as never,
      );
      if (!data) throw toApiContractError(response, error);
      return data as unknown as Record<string, unknown>;
    },
    retry: apiConfig.mode === 'live' ? 1 : false,
  });
  const importsQuery = useQuery({
    queryKey: ['finance-imports'],
    queryFn: async () => {
      const { data, error, response } = await apiClient.GET(
        '/api/v1/data/imports',
        {} as never,
      );
      if (!data) throw toApiContractError(response, error);
      return data as Import[];
    },
    retry: false,
  });
  const sourceAccountsQuery = useQuery({
    queryKey: ['planning-source-accounts', sourceImportId],
    enabled: Boolean(sourceImportId),
    queryFn: async () => {
      const { data, error, response } = await apiClient.GET(
        '/api/v1/data/imports/{import_id}/accounts',
        { params: { path: { import_id: sourceImportId } } } as never,
      );
      if (!data) throw toApiContractError(response, error);
      return data as SourceAccount[];
    },
    retry: false,
  });
  const mappingsQuery = useQuery({
    queryKey: ['planning-mappings', workspace.companyId],
    queryFn: async () => {
      const { data, error, response } = await apiClient.GET(
        '/api/v1/data/planning-mappings',
        { params: { query: { company_id: workspace.companyId } } } as never,
      );
      if (!data) throw toApiContractError(response, error);
      return data as PlanningMapping[];
    },
    retry: false,
  });
  const baselinesQuery = useQuery({
    queryKey: [
      'planning-baselines',
      workspace.companyId,
      workspace.periodId,
      workspace.scenarioId,
    ],
    queryFn: async () => {
      const { data, error, response } = await apiClient.GET(
        '/api/v1/data/planning-baselines',
        {
          params: {
            query: {
              company_id: workspace.companyId,
              period_id: workspace.periodId,
              scenario_id: workspace.scenarioId,
            },
          },
        } as never,
      );
      if (!data) throw toApiContractError(response, error);
      return data as PlanningBaseline[];
    },
    retry: false,
  });
  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: ['finance-imports'] });
    await queryClient.invalidateQueries({ queryKey: ['data-governance'] });
    await queryClient.invalidateQueries({ queryKey: ['planning'] });
    await queryClient.invalidateQueries({ queryKey: ['planning-mappings'] });
    await queryClient.invalidateQueries({ queryKey: ['planning-baselines'] });
    await queryClient.invalidateQueries({ queryKey: ['context'] });
  };
  const upload = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('Select a CSV or XLSX file.');
      let columnMapping: Record<string, string>;
      try {
        columnMapping = JSON.parse(mapping) as Record<string, string>;
      } catch {
        throw new Error('Column mapping must be valid JSON.');
      }
      const suffix = file.name.split('.').pop()?.toLowerCase() ?? 'csv';
      const { data, error, response } = await apiClient.POST('/api/v1/data/imports', {
        body: {
          content_base64: await fileBase64(file),
          file_name: file.name,
          file_type: suffix,
          column_mapping: columnMapping,
          reconciliation_rules: [
            {
              rule_id: 'import-total',
              expected_total: expectedTotal,
              absolute_tolerance: '0',
              blocking: true,
            },
          ],
        },
      } as never);
      if (!data) throw toApiContractError(response, error);
      return data;
    },
    onSuccess: async () => {
      setFile(null);
      setUploadError(null);
      await invalidate();
    },
    onError: (error) =>
      setUploadError(error instanceof Error ? error.message : 'Upload failed.'),
  });
  const transition = useMutation({
    mutationFn: async ({
      id,
      action,
    }: {
      id: string;
      action: 'review' | 'approve' | 'publish';
    }) => {
      const route =
        action === 'review'
          ? '/api/v1/data/imports/{import_id}/review'
          : action === 'approve'
            ? '/api/v1/data/imports/{import_id}/approve'
            : '/api/v1/data/imports/{import_id}/publish';
      const { data, error, response } =
        action === 'publish'
          ? await apiClient.POST(
              route as never,
              { params: { path: { import_id: id } } } as never,
            )
          : await apiClient.POST(
              route as never,
              {
                params: { path: { import_id: id } },
                body: { note: `Local ${action}` },
              } as never,
            );
      if (!data) throw toApiContractError(response, error);
    },
    onSuccess: invalidate,
  });
  const createPlanningMapping = useMutation({
    mutationFn: async () => {
      const selected = (importsQuery.data ?? []).find(
        (item) => item.import_id === sourceImportId,
      );
      if (!selected?.snapshot_id || !sourceAccountsQuery.data?.length)
        throw new Error('Select an eligible import with a snapshot.');
      const { data, error, response } = await apiClient.POST(
        '/api/v1/data/planning-mappings',
        {
          body: {
            company_id: workspace.companyId,
            source_snapshot_id: selected.snapshot_id,
            version_label: `${workspace.companyId} planning mapping ${new Date().toISOString().slice(0, 10)}`,
            mappings: sourceAccountsQuery.data.map((item) => ({
              source_account: item.account,
              ...(planningMapping[item.account] ??
                defaultPlanningMapping(item.account)),
            })),
          },
        } as never,
      );
      if (!data) throw toApiContractError(response, error);
    },
    onSuccess: invalidate,
  });
  const transitionPlanningMapping = useMutation({
    mutationFn: async ({
      id,
      action,
    }: {
      id: string;
      action: 'review' | 'approve';
    }) => {
      const route =
        action === 'review'
          ? '/api/v1/data/planning-mappings/{mapping_set_id}/review'
          : '/api/v1/data/planning-mappings/{mapping_set_id}/approve';
      const { data, error, response } = await apiClient.POST(
        route as never,
        {
          params: { path: { mapping_set_id: id } },
          body: { note: `Local mapping ${action}` },
        } as never,
      );
      if (!data) throw toApiContractError(response, error);
    },
    onSuccess: invalidate,
  });
  const publishBaseline = useMutation({
    mutationFn: async (mappingSetId: string) => {
      const { data, error, response } = await apiClient.POST(
        '/api/v1/data/planning-baselines',
        {
          body: {
            mapping_set_id: mappingSetId,
            period_id: workspace.periodId,
            scenario_id: workspace.scenarioId,
          },
        } as never,
      );
      if (!data) throw toApiContractError(response, error);
    },
    onSuccess: invalidate,
  });
  if (workspaceQuery.isLoading)
    return (
      <div className="p-6 text-sm text-[var(--text-secondary)]">
        Loading data governance…
      </div>
    );
  if (workspaceQuery.isError || !workspaceQuery.data)
    return (
      <div className="p-6 text-sm text-[var(--signal-negative)]">
        {describeApiError(workspaceQuery.error, 'Data & Governance')}
      </div>
    );
  const snapshots = items(workspaceQuery.data.snapshots);
  const findings = items(workspaceQuery.data.quality_findings);
  const runs = items(workspaceQuery.data.governed_runs);
  const models = items(workspaceQuery.data.models);
  const approvals = items(workspaceQuery.data.governance_approvals);
  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">
            FE-11 // DATA & GOVERNANCE
          </div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold">
            Data & Governance
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">
            Upload, validate, review, approve and publish a governed source. Published
            projections are generated by the backend for the selected finance context.
          </p>
        </div>
        <StatusIndicator label="DATA" detail="LIVE API CONNECTED" tone="positive" />
      </section>
      <TacticalFrame label="LOCAL APPROVAL ACTOR">
        <div className="grid gap-3 p-4 md:grid-cols-[1fr_auto]">
          <label className="grid gap-1">
            <span className="interface-label">LOCAL GATEWAY PROFILE</span>
            <select
              aria-label="LOCAL GATEWAY PROFILE"
              className="border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-2 text-sm"
              value={actor}
              onChange={(event) => {
                window.localStorage.setItem('cfo-local-actor', event.target.value);
                setActor(event.target.value);
                window.location.reload();
              }}
            >
              {localActors.map((profile) => (
                <option key={profile.id} value={profile.id}>
                  {profile.label}
                </option>
              ))}
            </select>
          </label>
          <p className="self-end text-xs text-[var(--text-secondary)]">
            The browser supplies only a profile name; Vite replaces it with a fixed
            local identity. Use three profiles to verify segregation of duties.
          </p>
        </div>
      </TacticalFrame>
      <TacticalFrame label="UPLOAD & COLUMN MAPPING">
        <div className="grid gap-3 p-4 lg:grid-cols-[1fr_1fr_10rem_auto]">
          <label className="grid gap-1">
            <span className="interface-label">SOURCE FILE</span>
            <input
              aria-label="SOURCE FILE"
              type="file"
              accept=".csv,.xlsx,.xlsm"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <label className="grid gap-1">
            <span className="interface-label">COLUMN MAPPING (JSON)</span>
            <input
              aria-label="COLUMN MAPPING"
              className="border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-2 text-sm"
              value={mapping}
              onChange={(event) => setMapping(event.target.value)}
              placeholder='{"company":"Entity"}'
            />
          </label>
          <label className="grid gap-1">
            <span className="interface-label">EXPECTED TOTAL</span>
            <input
              aria-label="EXPECTED TOTAL"
              className="border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-2 text-sm"
              value={expectedTotal}
              onChange={(event) => setExpectedTotal(event.target.value)}
            />
          </label>
          <button
            className="border border-[var(--frame-active)] px-4 py-2 text-sm disabled:opacity-50"
            disabled={!file || upload.isPending}
            onClick={() => upload.mutate()}
          >
            {upload.isPending ? 'VALIDATING…' : 'UPLOAD & VALIDATE'}
          </button>
        </div>
        <p className="px-4 pb-4 text-xs text-[var(--text-secondary)]">
          Required canonical columns: company, account, period, scenario, value,
          currency. Dimensions use the prefix dim_. The default reconciliation requires
          a balanced total of 0.
        </p>
        {uploadError && (
          <p role="alert" className="px-4 pb-4 text-sm text-[var(--signal-negative)]">
            {uploadError}
          </p>
        )}
      </TacticalFrame>
      <TacticalFrame label="IMPORT REVIEW QUEUE">
        <div className="divide-y divide-[var(--frame-muted)]">
          {importsQuery.isLoading && <p className="p-4 text-sm">Loading imports…</p>}
          {importsQuery.isError && (
            <p role="alert" className="p-4 text-sm text-[var(--signal-negative)]">
              {describeApiError(importsQuery.error, 'Import queue')}
            </p>
          )}
          {(importsQuery.data ?? []).map((item) => (
            <div className="grid gap-3 p-4 lg:grid-cols-[1fr_auto]">
              <div>
                <div className="text-sm font-medium">{item.file_name}</div>
                <div className="data-value mt-1 text-xs text-[var(--text-muted)]">
                  {item.status.toUpperCase()} // {item.row_count} ROWS // QUALITY{' '}
                  {item.quality_score} // SNAPSHOT {item.snapshot_id ?? 'NOT ELIGIBLE'}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  disabled={item.status !== 'draft' || transition.isPending}
                  onClick={() =>
                    transition.mutate({ id: item.import_id, action: 'review' })
                  }
                >
                  REVIEW
                </button>
                <button
                  disabled={item.status !== 'reviewed' || transition.isPending}
                  onClick={() =>
                    transition.mutate({ id: item.import_id, action: 'approve' })
                  }
                >
                  APPROVE
                </button>
                <button
                  disabled={item.status !== 'approved' || transition.isPending}
                  onClick={() =>
                    transition.mutate({ id: item.import_id, action: 'publish' })
                  }
                >
                  PUBLISH
                </button>
              </div>
            </div>
          ))}
          {!importsQuery.isLoading && !importsQuery.data?.length && (
            <p className="p-4 text-sm text-[var(--text-secondary)]">
              No imported sources yet.
            </p>
          )}
        </div>
        {transition.isError && (
          <p role="alert" className="p-4 text-sm text-[var(--signal-negative)]">
            {describeApiError(transition.error, 'Import transition')}
          </p>
        )}
      </TacticalFrame>
      <TacticalFrame label="PLANNING BASELINE // ACCOUNT MAPPING">
        <div className="grid gap-4 p-4">
          <p className="text-xs leading-5 text-[var(--text-secondary)]">
            Map every account from a published, governed snapshot once. The mapping
            remains a draft until a separate reviewer and approver have accepted it.
            Only an approved mapping can create a Planning baseline.
          </p>
          <label className="grid gap-1">
            <span className="interface-label">SOURCE IMPORT</span>
            <select
              aria-label="SOURCE IMPORT"
              className="border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-2 text-sm"
              value={sourceImportId}
              onChange={(event) => {
                setSourceImportId(event.target.value);
                setPlanningMapping({});
              }}
            >
              <option value="">Select published import…</option>
              {(importsQuery.data ?? [])
                .filter(
                  (item) => item.status === 'published' && Boolean(item.snapshot_id),
                )
                .map((item) => (
                  <option key={item.import_id} value={item.import_id}>
                    {item.file_name} // {item.status.toUpperCase()}
                  </option>
                ))}
            </select>
          </label>
          {sourceAccountsQuery.isLoading && (
            <p className="text-sm text-[var(--text-secondary)]">
              Loading source accounts…
            </p>
          )}
          {sourceAccountsQuery.data?.length ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[680px] text-left text-sm">
                  <thead className="interface-label text-[var(--text-muted)]">
                    <tr>
                      <th className="py-2">ACCOUNT</th>
                      <th className="py-2 text-right">SOURCE TOTAL</th>
                      <th className="py-2">PLANNING CATEGORY</th>
                      <th className="py-2">NORMALIZE SIGN</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--frame-muted)]">
                    {sourceAccountsQuery.data.map((account) => {
                      const selected =
                        planningMapping[account.account] ??
                        defaultPlanningMapping(account.account);
                      return (
                        <tr key={account.account}>
                          <td className="data-value py-2">{account.account}</td>
                          <td className="data-value py-2 text-right">
                            {account.total}
                          </td>
                          <td className="py-2">
                            <select
                              aria-label={`CATEGORY ${account.account}`}
                              className="border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-1 text-sm"
                              value={selected.category}
                              onChange={(event) =>
                                setPlanningMapping((current) => ({
                                  ...current,
                                  [account.account]: {
                                    ...selected,
                                    category: event.target.value,
                                  },
                                }))
                              }
                            >
                              {planningCategories.map((category) => (
                                <option key={category} value={category}>
                                  {category}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td className="py-2">
                            <select
                              aria-label={`SIGN ${account.account}`}
                              className="border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-1 text-sm"
                              value={selected.sign_multiplier}
                              onChange={(event) =>
                                setPlanningMapping((current) => ({
                                  ...current,
                                  [account.account]: {
                                    ...selected,
                                    sign_multiplier: event.target.value,
                                  },
                                }))
                              }
                            >
                              <option value="1">+1</option>
                              <option value="-1">−1</option>
                            </select>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <button
                className="justify-self-start border border-[var(--frame-active)] px-4 py-2 text-sm disabled:opacity-50"
                disabled={createPlanningMapping.isPending}
                onClick={() => createPlanningMapping.mutate()}
              >
                {createPlanningMapping.isPending ? 'SAVING…' : 'CREATE MAPPING DRAFT'}
              </button>
            </>
          ) : null}
          {sourceAccountsQuery.isError && (
            <p role="alert" className="text-sm text-[var(--signal-negative)]">
              {describeApiError(sourceAccountsQuery.error, 'Source accounts')}
            </p>
          )}
          <div className="divide-y divide-[var(--frame-muted)] border-t border-[var(--frame-muted)]">
            {(mappingsQuery.data ?? []).map((item) => (
              <div className="grid gap-2 py-3 lg:grid-cols-[1fr_auto]">
                <div>
                  <div className="text-sm font-medium">{item.version_label}</div>
                  <div className="data-value mt-1 text-xs text-[var(--text-muted)]">
                    {item.status.toUpperCase()} // {item.mappings.length} ACCOUNTS //{' '}
                    {item.source_snapshot_id}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    disabled={
                      item.status !== 'draft' || transitionPlanningMapping.isPending
                    }
                    onClick={() =>
                      transitionPlanningMapping.mutate({
                        id: item.mapping_set_id,
                        action: 'review',
                      })
                    }
                  >
                    REVIEW MAPPING
                  </button>
                  <button
                    disabled={
                      item.status !== 'reviewed' || transitionPlanningMapping.isPending
                    }
                    onClick={() =>
                      transitionPlanningMapping.mutate({
                        id: item.mapping_set_id,
                        action: 'approve',
                      })
                    }
                  >
                    APPROVE MAPPING
                  </button>
                  <button
                    disabled={item.status !== 'approved' || publishBaseline.isPending}
                    onClick={() => publishBaseline.mutate(item.mapping_set_id)}
                  >
                    {publishBaseline.isPending ? 'PUBLISHING…' : 'PUBLISH BASELINE'}
                  </button>
                </div>
              </div>
            ))}
            {!mappingsQuery.isLoading && !mappingsQuery.data?.length && (
              <p className="py-3 text-sm text-[var(--text-secondary)]">
                No Planning account mappings for this company yet.
              </p>
            )}
          </div>
          {(createPlanningMapping.isError ||
            transitionPlanningMapping.isError ||
            publishBaseline.isError) && (
            <p role="alert" className="text-sm text-[var(--signal-negative)]">
              {describeApiError(
                createPlanningMapping.error ??
                  transitionPlanningMapping.error ??
                  publishBaseline.error,
                'Planning baseline',
              )}
            </p>
          )}
          <div className="border-t border-[var(--frame-muted)] pt-3">
            <div className="interface-label text-[var(--text-muted)]">
              PUBLISHED BASELINE // {workspace.periodId} // {workspace.scenarioId}
            </div>
            {(baselinesQuery.data ?? []).map((baseline) => (
              <div className="mt-2 text-xs" key={baseline.baseline_id}>
                <span
                  className={
                    baseline.forecast_eligible
                      ? 'data-value text-[var(--signal-positive)]'
                      : 'data-value text-[var(--signal-warning)]'
                  }
                >
                  {baseline.forecast_eligible
                    ? 'FORECAST ELIGIBLE'
                    : `MISSING ${baseline.missing_categories.join(', ')}`}
                </span>
                <span className="ml-3 text-[var(--text-secondary)]">
                  Revenue {baseline.values.revenue ?? '0'} // Variable cost{' '}
                  {baseline.values.variable_cost ?? '0'} // Fixed cost{' '}
                  {baseline.values.fixed_operating_cost ?? '0'}
                </span>
              </div>
            ))}
            {!baselinesQuery.isLoading && !baselinesQuery.data?.length && (
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                No published Planning baseline for the active context.
              </p>
            )}
          </div>
        </div>
      </TacticalFrame>
      <section className="grid gap-4 xl:grid-cols-2">
        <TacticalFrame label="PUBLISHED SNAPSHOTS">
          <Rows rows={snapshots} primary="snapshot_id" secondary="content_hash" />
        </TacticalFrame>
        <TacticalFrame label="QUALITY FINDINGS">
          <Rows
            rows={findings}
            primary="message"
            secondary="status"
            empty="No open quality findings."
          />
        </TacticalFrame>
        <TacticalFrame label="GOVERNED RUNS">
          <Rows rows={runs} primary="run_id" secondary="status" />
        </TacticalFrame>
        <TacticalFrame label="MODEL REGISTRY">
          <Rows rows={models} primary="model_id" secondary="status" />
        </TacticalFrame>
        <TacticalFrame label="APPROVALS">
          <Rows rows={approvals} primary="approval_id" secondary="status" />
        </TacticalFrame>
      </section>
    </div>
  );
}

function Rows({
  rows,
  primary,
  secondary,
  empty = 'No records published for this context.',
}: {
  rows: Item[];
  primary: string;
  secondary: string;
  empty?: string;
}) {
  if (!rows.length)
    return <p className="p-4 text-sm text-[var(--text-secondary)]">{empty}</p>;
  return (
    <div className="divide-y divide-[var(--frame-muted)]">
      {rows.map((row, index) => (
        <div className="p-4" key={`${value(row, primary)}-${index}`}>
          <div className="text-sm font-medium">{value(row, primary)}</div>
          <div className="data-value mt-1 text-xs text-[var(--text-muted)]">
            {secondary.toUpperCase()} // {value(row, secondary)}
          </div>
        </div>
      ))}
    </div>
  );
}
