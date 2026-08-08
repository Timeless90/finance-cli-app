import { cn } from "@/lib/cn";

export type StatusTone = "neutral" | "active" | "positive" | "warning" | "negative";

const toneClasses: Record<StatusTone, string> = {
  neutral: "bg-[var(--text-muted)] shadow-[0_0_8px_oklch(0.58_0.025_52/0.2)]",
  active: "bg-[var(--signal-primary)] shadow-[0_0_10px_var(--glow-primary)]",
  positive: "bg-[var(--signal-positive)] shadow-[0_0_10px_var(--glow-positive)]",
  warning: "bg-[var(--signal-warning)]",
  negative: "bg-[var(--signal-negative)]",
};

export interface StatusIndicatorProps {
  label: string;
  tone?: StatusTone;
  detail?: string;
  className?: string;
}

export function StatusIndicator({
  className,
  detail,
  label,
  tone = "neutral",
}: StatusIndicatorProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span aria-hidden="true" className={cn("size-1.5 shrink-0 rounded-full", toneClasses[tone])} />
      <span className="interface-label text-[var(--text-secondary)]">{label}</span>
      {detail ? <span className="data-value text-xs text-[var(--text-primary)]">{detail}</span> : null}
    </div>
  );
}
