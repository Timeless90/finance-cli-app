import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

const buttonVariants = cva(
  "interface-label inline-flex min-h-10 items-center justify-center gap-2 border px-4 py-2 transition-[background,border-color,color,box-shadow] duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--signal-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)] disabled:pointer-events-none disabled:opacity-40",
  {
    variants: {
      variant: {
        primary:
          "border-[var(--signal-primary)] bg-[var(--signal-primary)] text-[var(--text-inverse)] hover:bg-[var(--signal-primary-strong)] hover:shadow-[0_0_24px_var(--glow-primary)]",
        outline:
          "border-[var(--frame-active)] bg-transparent text-[var(--signal-primary)] hover:bg-[var(--signal-primary)]/10",
        ghost:
          "border-transparent bg-transparent text-[var(--text-secondary)] hover:border-[var(--frame-muted)] hover:text-[var(--text-primary)]",
      },
      size: {
        sm: "min-h-8 px-3 text-[0.625rem]",
        md: "min-h-10 px-4",
        lg: "min-h-12 px-6 text-xs",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export function Button({ asChild = false, className, size, variant, ...props }: ButtonProps) {
  const Component = asChild ? Slot : "button";

  return <Component className={cn(buttonVariants({ size, variant }), className)} {...props} />;
}
