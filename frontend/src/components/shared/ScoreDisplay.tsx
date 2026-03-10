"use client";

import { cn, scoreColor } from "@/lib/utils";

interface ScoreDisplayProps {
  /** Puntuación raw (0-100) */
  raw: number;
  /** Puntuación ponderada (0-100). Si se omite, sólo se muestra la raw */
  weighted?: number;
  /** Tamaño del número principal */
  size?: "sm" | "md" | "lg" | "xl";
  /** Muestra una barra de progreso debajo */
  showBar?: boolean;
  /** Etiqueta encima del score */
  label?: string;
  className?: string;
}

const SIZE_CLASSES = {
  sm: "text-lg font-semibold",
  md: "text-2xl font-bold",
  lg: "text-4xl font-bold",
  xl: "text-5xl font-extrabold",
};

export function ScoreDisplay({
  raw,
  weighted,
  size = "md",
  showBar = false,
  label,
  className,
}: ScoreDisplayProps) {
  const rawColor = scoreColor(raw);
  const weightedColor = weighted !== undefined ? scoreColor(weighted) : null;

  return (
    <div className={cn("flex flex-col gap-1", className)}>
      {label && (
        <span className="text-xs text-text-muted uppercase tracking-wider">
          {label}
        </span>
      )}

      <div className="flex items-baseline gap-3">
        {/* Score raw — número principal */}
        <span className={cn(SIZE_CLASSES[size], rawColor)}>
          {raw.toFixed(1)}
        </span>

        {/* Score ponderado — secundario */}
        {weighted !== undefined && (
          <span className="text-sm text-text-secondary">
            <span className="text-text-muted text-xs mr-1">weighted</span>
            <span className={cn("font-semibold", weightedColor)}>
              {weighted.toFixed(1)}
            </span>
          </span>
        )}

        {/* Escala */}
        <span className="text-text-muted text-xs self-end mb-0.5">/100</span>
      </div>

      {/* Barra de progreso */}
      {showBar && (
        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all duration-500", barColor(raw))}
            style={{ width: `${Math.min(100, Math.max(0, raw))}%` }}
          />
        </div>
      )}
    </div>
  );
}

function barColor(score: number): string {
  if (score >= 80) return "bg-pass";
  if (score >= 60) return "bg-medium";
  if (score >= 40) return "bg-high";
  return "bg-critical";
}

/** Score compacto inline para tablas */
export function ScoreInline({
  score,
  className,
}: {
  score: number;
  className?: string;
}) {
  return (
    <span className={cn("font-mono font-semibold tabular-nums", scoreColor(score), className)}>
      {score.toFixed(1)}
    </span>
  );
}
