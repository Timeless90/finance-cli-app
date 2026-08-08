import { Link } from "react-router-dom";

import { MetricPanel, StatusIndicator, TacticalFrame } from "@/components/finance";
import { Button } from "@/components/ui/button";

const features = [
  {
    code: "01",
    title: "Forecast Engine",
    description: "Driver-based planning, rolling forecasts and probabilistic outlooks in one command layer.",
    signal: "P10 / P50 / P90",
  },
  {
    code: "02",
    title: "Risk Command",
    description: "Connect enterprise, liquidity and market risk to the financial plan and decision horizon.",
    signal: "VAR / ES / LIMITS",
  },
  {
    code: "03",
    title: "Scenario Lab",
    description: "Compare base, upside and downside paths without losing model, assumption or run lineage.",
    signal: "WHAT-IF / STRESS",
  },
  {
    code: "04",
    title: "AI Briefings",
    description: "Turn governed finance outputs into evidence-linked explanations, actions and management narratives.",
    signal: "EXPLAIN / ACT",
  },
];

const previewMetrics = [
  { label: "FORECAST CONFIDENCE", value: "87.4%", detail: "+3.1 PP" },
  { label: "CASH RUNWAY", value: "18.4 MO", detail: "+1.8 MO" },
  { label: "VAR 95%", value: "€13.6M", detail: "-2.1%" },
  { label: "SCENARIO PATHS", value: "1,024", detail: "SIMULATED" },
];

function BrandMark() {
  return (
    <Link aria-label="CFO Command Center home" className="flex items-center gap-3 no-underline" to="/">
      <span className="grid h-9 w-9 place-items-center border border-[var(--frame-active)] bg-[var(--surface-canvas)] text-[var(--signal-primary)] shadow-[0_0_18px_var(--glow-primary)]">
        <span className="data-value text-[0.65rem]">CFO</span>
      </span>
      <span>
        <span className="interface-label block text-[var(--signal-primary)]">COMMAND CENTER</span>
        <span className="data-value mt-0.5 block text-[0.6rem] text-[var(--text-muted)]">FINANCE OS // 2060</span>
      </span>
    </Link>
  );
}

function HeroForecast() {
  return (
    <div className="relative overflow-hidden border border-[var(--frame-muted)] bg-[var(--surface-canvas)] p-4 sm:p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="interface-label m-0 text-[var(--text-muted)]">12M PROBABILISTIC OUTLOOK</p>
          <p className="data-value m-0 mt-2 text-lg text-[var(--signal-primary)]">EBITDA // UI PREVIEW</p>
        </div>
        <StatusIndicator detail="SIMULATED" label="DATA" tone="warning" />
      </div>
      <svg
        aria-label="Simulated forecast visualization showing P10, P50 and P90 trajectories"
        className="mt-6 h-56 w-full"
        role="img"
        viewBox="0 0 760 250"
      >
        <defs>
          <linearGradient id="forecast-band" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="var(--signal-positive)" stopOpacity="0.2" />
            <stop offset="100%" stopColor="var(--signal-primary)" stopOpacity="0.02" />
          </linearGradient>
          <filter id="orange-glow">
            <feGaussianBlur result="coloredBlur" stdDeviation="3" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {[50, 100, 150, 200].map((y) => (
          <line key={y} stroke="var(--grid-line)" strokeWidth="1" x1="0" x2="760" y1={y} y2={y} />
        ))}
        {[120, 240, 360, 480, 600].map((x) => (
          <line key={x} stroke="var(--grid-line)" strokeWidth="1" x1={x} x2={x} y1="0" y2="230" />
        ))}
        <path
          d="M0 180 C90 165 130 170 205 140 S335 116 420 82 S575 42 760 25 L760 177 C590 160 545 148 420 150 S290 166 205 176 S80 190 0 190 Z"
          fill="url(#forecast-band)"
        />
        <path
          d="M0 180 C90 165 130 170 205 140 S335 116 420 82 S575 42 760 25"
          fill="none"
          stroke="var(--signal-positive)"
          strokeDasharray="6 8"
          strokeOpacity="0.45"
          strokeWidth="1.3"
        />
        <path
          d="M0 180 C95 172 135 157 205 151 S330 130 420 112 S590 76 760 60"
          fill="none"
          filter="url(#orange-glow)"
          stroke="var(--signal-primary)"
          strokeWidth="2.7"
        />
        <path
          d="M0 190 C80 188 135 185 205 176 S330 157 420 150 S590 160 760 177"
          fill="none"
          stroke="var(--signal-negative)"
          strokeDasharray="6 8"
          strokeOpacity="0.65"
          strokeWidth="1.2"
        />
        <line stroke="var(--frame-active)" strokeDasharray="2 7" x1="310" x2="310" y1="10" y2="230" />
        <circle cx="310" cy="134" fill="var(--signal-primary)" r="4" />
      </svg>
      <div className="interface-label flex justify-between border-t border-[var(--frame-muted)] pt-3 text-[var(--text-muted)]">
        <span>NOW // ACTUAL</span>
        <span>P10</span>
        <span className="text-[var(--signal-primary)]">P50</span>
        <span>P90</span>
        <span>+12M</span>
      </div>
    </div>
  );
}

function ProductPreview() {
  return (
    <div className="relative mx-auto w-full max-w-6xl">
      <div className="pointer-events-none absolute -inset-10 bg-[radial-gradient(circle_at_center,var(--glow-primary),transparent_68%)] opacity-70" />
      <TacticalFrame
        className="relative shadow-[0_0_55px_var(--glow-primary)]"
        label="CFO COMMAND CENTER // PRODUCT PREVIEW"
        labelAction={<StatusIndicator detail="ONLINE" label="SYSTEM" tone="positive" />}
        tone="active"
      >
        <div className="grid gap-px bg-[var(--frame-muted)] lg:grid-cols-[1fr_14rem]">
          <div className="bg-[var(--surface-panel)] p-3 sm:p-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <MetricPanel delta="+8.4%" deltaTone="positive" label="EBITDA" meta="SIMULATED PREVIEW" value="€184.2M" />
              <MetricPanel delta="+€5.3M" deltaTone="positive" label="FREE CASH FLOW" meta="SIMULATED PREVIEW" value="€72.8M" />
              <MetricPanel delta="-2.1%" deltaTone="negative" label="VAR 95%" meta="SIMULATED PREVIEW" value="€13.6M" />
            </div>
            <div className="mt-3">
              <HeroForecast />
            </div>
          </div>
          <aside className="grid content-start gap-px bg-[var(--frame-muted)]">
            <div className="bg-[var(--surface-panel)] p-4">
              <p className="interface-label m-0 text-[var(--text-muted)]">ACTIVE SCENARIO</p>
              <p className="data-value m-0 mt-2 text-xl text-[var(--signal-primary)]">BASE // FY26</p>
            </div>
            <div className="grid gap-3 bg-[var(--surface-panel)] p-4">
              <StatusIndicator detail="VALIDATED" label="DATA" tone="positive" />
              <StatusIndicator detail="APPROVED" label="MODEL" tone="positive" />
              <StatusIndicator detail="42% HEADROOM" label="COVENANT" tone="positive" />
              <StatusIndicator detail="28 / 100" label="RISK" tone="warning" />
            </div>
            <div className="bg-[var(--surface-panel)] p-4">
              <p className="interface-label m-0 text-[var(--text-muted)]">AI BRIEFING</p>
              <p className="mt-3 text-xs leading-5 text-[var(--text-secondary)]">
                Margin pressure remains concentrated in volume and energy cost drivers. No live analysis is executed on this public preview.
              </p>
            </div>
          </aside>
        </div>
      </TacticalFrame>
    </div>
  );
}

export function LandingPage() {
  return (
    <main className="ds-environment min-h-screen overflow-hidden bg-[var(--surface-canvas)] text-[var(--text-primary)]">
      <header className="sticky top-0 z-30 border-b border-[var(--frame-muted)] bg-[color:var(--surface-canvas)]/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-5 px-4 py-3 sm:px-6 lg:px-10">
          <BrandMark />
          <nav aria-label="Landing page navigation" className="hidden items-center gap-7 lg:flex">
            {[
              ["Platform", "#platform"],
              ["Forecasting", "#forecasting"],
              ["Risk", "#risk"],
              ["AI", "#ai"],
            ].map(([label, href]) => (
              <a className="interface-label text-[var(--text-secondary)] no-underline transition-colors hover:text-[var(--signal-primary)]" href={href} key={href}>
                {label}
              </a>
            ))}
          </nav>
          <Button asChild size="sm">
            <Link to="/app/command-center">LAUNCH APP</Link>
          </Button>
        </div>
      </header>

      <section className="relative mx-auto grid min-h-[82vh] max-w-[1500px] items-center gap-12 px-4 py-20 sm:px-6 lg:grid-cols-[0.82fr_1.18fr] lg:px-10 lg:py-28">
        <div className="relative z-10">
          <div className="mb-6 flex items-center gap-3">
            <span className="h-px w-10 bg-[var(--signal-primary)]" />
            <p className="interface-label m-0 text-[var(--signal-primary)]">FINANCE INTELLIGENCE // NEXT HORIZON</p>
          </div>
          <h1 className="m-0 max-w-4xl font-display text-[clamp(3.4rem,7vw,7.7rem)] font-semibold uppercase leading-[0.82] tracking-[-0.065em]">
            See the future <span className="text-[var(--signal-primary)]">of finance.</span>
          </h1>
          <p className="mt-8 max-w-xl text-base leading-7 text-[var(--text-secondary)] sm:text-lg">
            One command layer for forecasting, performance, liquidity, risk, capital allocation and governed AI insight.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link to="/app/command-center">LAUNCH COMMAND CENTER</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="#platform">EXPLORE PLATFORM</a>
            </Button>
          </div>
          <div className="mt-10 grid max-w-xl gap-px bg-[var(--frame-muted)] sm:grid-cols-3">
            {[
              ["MODE", "TACTICAL"],
              ["CONTRACT", "OPENAPI"],
              ["DATA", "PREVIEW"],
            ].map(([label, value]) => (
              <div className="bg-[var(--surface-panel)] p-3" key={label}>
                <p className="interface-label m-0 text-[var(--text-muted)]">{label}</p>
                <p className="data-value m-0 mt-1 text-xs text-[var(--signal-primary)]">{value}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="relative lg:-mr-28">
          <ProductPreview />
        </div>
      </section>

      <section aria-label="Simulated product metrics" className="border-y border-[var(--frame-muted)] bg-[var(--surface-panel)]">
        <div className="mx-auto grid max-w-[1500px] divide-y divide-[var(--frame-muted)] sm:grid-cols-2 sm:divide-x sm:divide-y-0 lg:grid-cols-4 lg:px-10">
          {previewMetrics.map((metric) => (
            <div className="p-5 lg:p-7" key={metric.label}>
              <p className="interface-label m-0 text-[var(--text-muted)]">{metric.label}</p>
              <div className="mt-3 flex items-end justify-between gap-4">
                <p className="data-value m-0 text-2xl text-[var(--signal-primary)] sm:text-3xl">{metric.value}</p>
                <span className="data-value text-[0.65rem] text-[var(--signal-positive)]">{metric.detail}</span>
              </div>
              <p className="data-value m-0 mt-3 text-[0.58rem] text-[var(--text-muted)]">SIMULATED UI PREVIEW // NOT LIVE DATA</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-[1500px] px-4 py-24 sm:px-6 lg:px-10 lg:py-32" id="platform">
        <div className="grid gap-12 lg:grid-cols-[0.7fr_1.3fr]">
          <div>
            <p className="interface-label m-0 text-[var(--signal-primary)]">PLATFORM // 04 MODULES</p>
            <h2 className="mt-4 max-w-md font-display text-4xl font-semibold uppercase leading-[0.94] tracking-[-0.045em] sm:text-5xl">
              Built for decisions under uncertainty.
            </h2>
            <p className="mt-6 max-w-md text-sm leading-6 text-[var(--text-secondary)]">
              The visual system stays cinematic. The underlying product stays disciplined: governed models, explicit scenarios, traceable outputs and clear action paths.
            </p>
          </div>
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2">
            {features.map((feature) => (
              <article className="group min-h-64 bg-[var(--surface-panel)] p-6 transition-colors hover:bg-[var(--surface-panel-raised)]" id={feature.code === "01" ? "forecasting" : feature.code === "02" ? "risk" : feature.code === "04" ? "ai" : undefined} key={feature.code}>
                <div className="flex items-start justify-between gap-4">
                  <span className="data-value text-xs text-[var(--signal-primary)]">{feature.code}</span>
                  <span className="interface-label border border-[var(--frame-muted)] px-2 py-1 text-[var(--text-muted)] group-hover:border-[var(--frame-active)] group-hover:text-[var(--signal-primary)]">
                    {feature.signal}
                  </span>
                </div>
                <h3 className="mt-14 font-display text-2xl font-semibold uppercase tracking-[-0.03em]">{feature.title}</h3>
                <p className="mt-4 max-w-sm text-sm leading-6 text-[var(--text-secondary)]">{feature.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-[var(--frame-muted)] bg-[var(--surface-panel)]">
        <div className="mx-auto grid max-w-[1500px] gap-8 px-4 py-20 sm:px-6 lg:grid-cols-[1fr_1fr] lg:px-10 lg:py-24">
          <div>
            <p className="interface-label m-0 text-[var(--signal-primary)]">CONTROL SURFACE // GOVERNED BY DESIGN</p>
            <h2 className="mt-4 max-w-2xl font-display text-4xl font-semibold uppercase leading-[0.95] tracking-[-0.045em] sm:text-5xl">
              Retro-future interface. Enterprise finance discipline.
            </h2>
          </div>
          <div className="grid gap-px bg-[var(--frame-muted)] sm:grid-cols-2">
            {[
              ["01", "OPENAPI CONTRACT", "Frontend types follow backend Pydantic models instead of duplicating them."],
              ["02", "RUN LINEAGE", "Finance outcomes remain attributable to scenarios, models, snapshots and governed runs."],
              ["03", "MOCK / LIVE", "Frontend development continues in parallel without pretending mock data is production data."],
              ["04", "ACCESSIBLE UI", "Technical density remains keyboard-operable, readable and responsive."],
            ].map(([code, title, description]) => (
              <div className="bg-[var(--surface-canvas)] p-5" key={code}>
                <p className="data-value m-0 text-[0.65rem] text-[var(--signal-primary)]">{code}</p>
                <p className="interface-label m-0 mt-8 text-[var(--text-primary)]">{title}</p>
                <p className="mt-3 text-xs leading-5 text-[var(--text-secondary)]">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-[1500px] px-4 py-24 sm:px-6 lg:px-10 lg:py-36">
        <TacticalFrame label="NEXT COMMAND" tone="active">
          <div className="relative overflow-hidden p-7 sm:p-10 lg:p-14">
            <div className="pointer-events-none absolute right-[-8rem] top-[-12rem] h-96 w-96 rounded-full border border-[var(--frame-active)] opacity-25 shadow-[0_0_100px_var(--glow-primary)]" />
            <p className="interface-label m-0 text-[var(--signal-primary)]">CFO COMMAND CENTER // READY</p>
            <div className="relative mt-6 grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
              <h2 className="m-0 max-w-4xl font-display text-4xl font-semibold uppercase leading-[0.92] tracking-[-0.05em] sm:text-6xl">
                Move from reporting the past to steering the next outcome.
              </h2>
              <Button asChild size="lg">
                <Link to="/app/command-center">ENTER COMMAND CENTER</Link>
              </Button>
            </div>
          </div>
        </TacticalFrame>
      </section>

      <footer className="border-t border-[var(--frame-muted)]">
        <div className="mx-auto flex max-w-[1500px] flex-col gap-4 px-4 py-6 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-10">
          <BrandMark />
          <p className="data-value m-0 text-[0.6rem] text-[var(--text-muted)]">PUBLIC LANDING // NO BUSINESS API DEPENDENCY // FE-04</p>
        </div>
      </footer>
    </main>
  );
}
