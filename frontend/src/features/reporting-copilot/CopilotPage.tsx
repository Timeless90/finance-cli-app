import { useState } from 'react';

import { apiConfig } from '@/shared/api/config';
import { describeApiError } from '@/shared/api/errors';
import { useWorkspaceContext } from '@/app/context/useWorkspaceContext';
import { StatusIndicator, TacticalFrame } from '@/features/finance-ui';
import {
  createCopilotSession,
  sendCopilotMessage,
  type CopilotAnswer,
  type CopilotSession,
} from '@/features/reporting-copilot/copilot-session';

export function CopilotPage() {
  const workspace = useWorkspaceContext();
  const [session, setSession] = useState<CopilotSession>();
  const [answer, setAnswer] = useState<CopilotAnswer>();
  const [question, setQuestion] = useState('');
  const [error, setError] = useState<unknown>();
  const [pending, setPending] = useState(false);
  const start = async () => {
    setPending(true);
    setError(undefined);
    try {
      setSession(await createCopilotSession(workspace));
      setAnswer(undefined);
    } catch (cause) {
      setError(cause);
    } finally {
      setPending(false);
    }
  };
  const ask = async () => {
    if (!session || !question.trim()) return;
    setPending(true);
    setError(undefined);
    try {
      setAnswer(await sendCopilotMessage(session.session_id, question));
    } catch (cause) {
      setError(cause);
    } finally {
      setPending(false);
    }
  };
  const live = apiConfig.mode === 'live';
  return (
    <div className="grid gap-4 p-4 lg:p-6">
      <section className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <div className="interface-label text-[var(--signal-primary)]">
            FE-10 // GOVERNED FINANCE COPILOT
          </div>
          <h1 className="mt-2 font-[var(--font-display)] text-3xl font-semibold">
            Financial Copilot
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">
            Sessions are scoped to the selected backend context. The browser never sends
            a principal, source facts, model deployment, or direct Foundry request.
          </p>
        </div>
        <div className="flex gap-2">
          <StatusIndicator
            label="DATA"
            detail={live ? 'LIVE API CONNECTED' : 'MOCK MODE'}
            tone={live ? 'positive' : 'warning'}
          />
          <StatusIndicator label="GROUNDING" detail="BACKEND SOURCES" tone="positive" />
        </div>
      </section>
      <TacticalFrame label="SESSION & GROUNDED SOURCES">
        <div className="p-4">
          <button
            className="interface-label border border-[var(--signal-primary)] px-3 py-2 text-[var(--signal-primary)] disabled:opacity-50"
            disabled={!live || pending}
            onClick={() => void start()}
            type="button"
          >
            {pending ? 'CONNECTING…' : 'START SECURE SESSION'}
          </button>
          {session && (
            <div className="mt-3 text-xs text-[var(--text-secondary)]">
              <div className="data-value text-[var(--signal-positive)]">
                SESSION // {session.session_id}
              </div>
              <div className="mt-1">
                ROUTE {session.route_id} · SOURCES {session.source_refs.join(', ')}
              </div>
            </div>
          )}
        </div>
      </TacticalFrame>
      <TacticalFrame label="ASK FINANCE">
        <div className="p-4">
          <label
            className="interface-label text-[var(--text-muted)]"
            htmlFor="copilot-prompt"
          >
            QUESTION
          </label>
          <div className="mt-2 grid gap-2 sm:grid-cols-[1fr_auto]">
            <textarea
              className="min-h-24 resize-y border border-[var(--frame-default)] bg-[var(--surface-canvas)] p-3 text-sm"
              id="copilot-prompt"
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask about published sources…"
              value={question}
            />
            <button
              className="interface-label border border-[var(--signal-primary)] px-4 text-[var(--signal-primary)] disabled:opacity-50"
              disabled={!session || !question.trim() || pending}
              onClick={() => void ask()}
              type="button"
            >
              SEND
            </button>
          </div>
          {answer && (
            <article className="mt-4 border border-[var(--frame-muted)] p-4">
              <p className="text-sm leading-6">{String(answer.answer.text)}</p>
              <div className="data-value mt-3 text-[0.6rem] text-[var(--text-muted)]">
                ROUTE {String(answer.answer.route_id)} // DEPLOYMENT{' '}
                {String(answer.answer.selected_deployment)} // SOURCES{' '}
                {answer.answer.source_refs.map(String).join(', ')}
              </div>
            </article>
          )}
          {Boolean(error) && (
            <p className="mt-3 text-xs text-[var(--signal-negative)]" role="alert">
              {describeApiError(error, 'Copilot')}
            </p>
          )}
        </div>
      </TacticalFrame>
    </div>
  );
}
