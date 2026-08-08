import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";

const frameVariants = cva(
  "relative border bg-[var(--surface-panel)] text-[var(--text-primary)] transition-[border-color,box-shadow,background] duration-200",
  {
    variants: {
      tone: {
        default: "border-[var(--frame-default)]",
        active:
          "border-[var(--frame-active)] text-[var(--signal-primary)] shadow-[0_0_26px_var(--glow-primary)]",
        positive:
          "border-[var(--frame-positive)] text-[var(--signal-positive)] shadow-[0_0_22px_var(--glow-positive)]",
        negative: "border-[var(--frame-negative)] text-[var(--signal-negative)]",
        muted: "border-[var(--frame-muted)] text-[var(--text-secondary)]",
      },
    },
    defaultVariants: {
      tone: "default",
    },
  },
);

export interface TacticalFrameProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof frameVariants> {
  label?: string;
  labelAction?: ReactNode;
}

export function TacticalFrame({
  children,
  className,
  label,
  labelAction,
  tone,
  ...props
}: TacticalFrameProps) {
  return (
    <section className={cn(frameVariants({ tone }), className)} {...props}>
      <span aria-hidden="true" className="tactical-corner tactical-corner--tl" />
      <span aria-hidden="true" className="tactical-corner tactical-corner--tr" />
      <span aria-hidden="true" className="tactical-corner tactical-corner--bl" />
      <span aria-hidden="true" className="tactical-corner tactical-corner--br" />
      {(label || labelAction) && (
        <header className="flex min-h-9 items-center justify-between gap-4 border-b border-[var(--frame-muted)] px-3 py-2 text-[var(--text-secondary)]">
          {label ? <span className="interface-label">{label}</span> : <span />}
          {labelAction}
        </header>
      )}
      {children}
    </section>
  );
}
