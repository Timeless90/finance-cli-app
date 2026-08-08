import { TacticalFrame } from "@/components/finance/tactical-frame";

export interface MetricPanelProps {
  label: string;
  value: string;
  delta?: string;
  deltaTone?: "positive" | "negative" | "neutral";
  meta?: string;
}

const deltaClasses = {
  positive: "text-[var(--signal-positive)]",
  negative: "text-[var(--signal-negative)]",
  neutral: "text-[var(--text-secondary)]",
} as const;

export function MetricPanel({
  delta,
  deltaTone = "neutral",
  label,
  meta,
  value,
}: MetricPanelProps) {
  return (
    <TacticalFrame label={label} className="min-h-36">
      <div className="flex h-full flex-col justify-between gap-4 p-4">
        <div>
          <div className="data-value text-3xl tracking-[-0.04em] text-[var(--signal-primary)]">
            {value}
          </div>
          {delta ? (
            <div className={`data-value mt-2 text-xs ${deltaClasses[deltaTone]}`}>{delta}</div>
          ) : null}
        </div>
        {meta ? (
          <div className="interface-label border-t border-[var(--frame-muted)] pt-3 text-[var(--text-muted)]">
            {meta}
          </div>
        ) : null}
      </div>
    </TacticalFrame>
  );
}
