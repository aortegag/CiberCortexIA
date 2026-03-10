"use client";

import { cn } from "@/lib/utils";

export type Severity = "critical" | "high" | "medium" | "low" | "pass" | "info";

const SEVERITY_CONFIG: Record<
  Severity,
  { label: string; bg: string; text: string; dot: string }
> = {
  critical: {
    label: "Critical",
    bg: "bg-critical/10",
    text: "text-critical",
    dot: "bg-critical",
  },
  high: {
    label: "High",
    bg: "bg-high/10",
    text: "text-high",
    dot: "bg-high",
  },
  medium: {
    label: "Medium",
    bg: "bg-medium/10",
    text: "text-medium",
    dot: "bg-medium",
  },
  low: {
    label: "Low",
    bg: "bg-low/10",
    text: "text-low",
    dot: "bg-low",
  },
  pass: {
    label: "Pass",
    bg: "bg-pass/10",
    text: "text-pass",
    dot: "bg-pass",
  },
  info: {
    label: "Info",
    bg: "bg-white/5",
    text: "text-text-secondary",
    dot: "bg-text-secondary",
  },
};

interface SeverityBadgeProps {
  severity: Severity;
  /** Muestra una etiqueta personalizada en lugar del nombre de severidad */
  label?: string;
  /** Tamaño: sm (por defecto) o md */
  size?: "sm" | "md";
  /** Muestra el punto de color */
  dot?: boolean;
  className?: string;
}

export function SeverityBadge({
  severity,
  label,
  size = "sm",
  dot = true,
  className,
}: SeverityBadgeProps) {
  const cfg = SEVERITY_CONFIG[severity];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded font-medium",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm",
        cfg.bg,
        cfg.text,
        className
      )}
    >
      {dot && (
        <span
          className={cn("rounded-full shrink-0", cfg.dot, size === "sm" ? "h-1.5 w-1.5" : "h-2 w-2")}
        />
      )}
      {label ?? cfg.label}
    </span>
  );
}

/** Mapea string de la API a tipo Severity seguro */
export function parseSeverity(s: string): Severity {
  const valid: Severity[] = ["critical", "high", "medium", "low", "pass", "info"];
  return valid.includes(s as Severity) ? (s as Severity) : "info";
}
