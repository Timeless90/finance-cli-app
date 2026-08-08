import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import { Button } from "@/components/ui/button";

const metrics = [
  { label: "EBITDA", value: "€184.2M", delta: "+8.4%", deltaTone: "positive" as const },
  { label: "FREE CASH FLOW", value: "€72.8M", delta: "+€5.3M", deltaTone: "positive" as const },
  { label: "VAR 95%", value: "€13.6M", delta: "-2.1%", deltaTone: "negative" as const },
];

export function App() {
  return (
    <main className="ds-environment min-h-screen px-4 py-6 sm:px-6 lg:px-10 lg:py-10">
      <div className="mx-auto grid max-w-7xl gap-6">
        <header className="flex flex-col gap-6 border-b border-[var(--frame-default)] pb-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="interface-label mb-3 text-[var(--signal-primary)]">
              CFO COMMAND CENTER // FE-01
            </p>
            <h1 className="max-w-4xl font-display text-4xl font-semibold uppercase leading-[0.92] tracking-[-0.045em] sm:text-6xl lg:text-7xl">
              Tactical finance interface.
            </h1>
            <p className="mt-5 max-w-2xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
              Finance 2060 foundations establish the visual language for planning, liquidity, risk,
              capital allocation and AI-assisted finance workflows.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button>RUN PREVIEW</Button>
            <Button variant="outline">VIEW TOKENS</Button>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-3" aria-label="Finance metric components">
          {metrics.map((metric) => (
            <MetricPanel key={metric.label} {...metric} meta="DEMO VALUE // FRONTEND ONLY" />
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.65fr_0.75fr]">
          <TacticalFrame
            label="FORECAST VISUAL LANGUAGE"
            tone="active"
            labelAction={<StatusIndicator label="MODE" detail="DESIGN PREVIEW" tone="active" />}
          >
            <div className="grid min-h-80 gap-6 p-5 lg:grid-cols-[1fr_auto]">
              <div className="relative overflow-hidden border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-5">
                <div className="interface-label text-[var(--text-muted)]">P10 / P50 / P90 GRAMMAR</div>
                <svg
                  aria-label="Illustrative forecast styling preview"
                  className="mt-5 h-52 w-full"
                  role="img"
                  viewBox="0 0 720 220"
                >
                  <path d="M0 180 C120 155 165 164 240 128 S390 103 470 73 S610 42 720 28" fill="none" stroke="var(--signal-positive)" strokeOpacity="0.35" strokeWidth="1" strokeDasharray="5 7" />
                  <path d="M0 180 C120 166 175 143 240 137 S385 120 470 102 S615 72 720 62" fill="none" stroke="var(--signal-positive)" strokeWidth="2.5" />
                  <path d="M0 180 C120 174 172 154 240 146 S390 145 470 151 S610 168 720 187" fill="none" stroke="var(--signal-negative)" strokeOpacity="0.7" strokeWidth="1" strokeDasharray="6 8" />
                  <line x1="250" x2="250" y1="16" y2="205" stroke="var(--frame-default)" strokeDasharray="2 7" />
                  <circle cx="250" cy="135" fill="var(--signal-primary)" r="4" />
                </svg>
                <div className="interface-label flex justify-between border-t border-[var(--frame-muted)] pt-3 text-[var(--text-muted)]">
                  <span>NOW</span>
                  <span>12M OUTLOOK</span>
                </div>
              </div>
              <div className="grid content-start gap-4 lg:w-48">
                <StatusIndicator label="DATA" detail="VALIDATED" tone="positive" />
                <StatusIndicator label="MODEL" detail="APPROVED" tone="positive" />
                <StatusIndicator label="RUN" detail="PREVIEW" tone="active" />
              </div>
            </div>
          </TacticalFrame>

          <TacticalFrame label="BACKEND CONTRACT" tone="muted">
            <div className="grid gap-5 p-5">
              <div>
                <div className="interface-label text-[var(--text-muted)]">FE-01</div>
                <div className="data-value mt-2 text-xl text-[var(--signal-positive)]">
                  NO BACKEND CONTRACT
                </div>
              </div>
              <p className="m-0 text-sm leading-6 text-[var(--text-secondary)]">
                Tokens and UI primitives remain independent from FastAPI. API coupling begins in
                FE-03 through generated OpenAPI contracts and frontend adapters.
              </p>
            </div>
          </TacticalFrame>
        </section>
      </div>
    </main>
  );
}
