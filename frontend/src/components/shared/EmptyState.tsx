"use client";

import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  /** Botón de acción principal */
  action?: {
    label: string;
    onClick: () => void;
  };
  /** Botón de acción secundaria */
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  /** Variante visual */
  variant?: "default" | "compact";
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  secondaryAction,
  variant = "default",
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center",
        variant === "default" ? "py-16 px-8" : "py-8 px-4",
        className
      )}
    >
      {/* Icono */}
      {Icon && (
        <div
          className={cn(
            "flex items-center justify-center rounded-xl bg-white/5 mb-4",
            variant === "default" ? "h-14 w-14" : "h-10 w-10"
          )}
        >
          <Icon
            className={cn(
              "text-text-muted",
              variant === "default" ? "h-7 w-7" : "h-5 w-5"
            )}
          />
        </div>
      )}

      {/* Título */}
      <h3
        className={cn(
          "font-semibold text-text-primary mb-1",
          variant === "default" ? "text-base" : "text-sm"
        )}
      >
        {title}
      </h3>

      {/* Descripción */}
      {description && (
        <p
          className={cn(
            "text-text-secondary max-w-sm",
            variant === "default" ? "text-sm mb-6" : "text-xs mb-4"
          )}
        >
          {description}
        </p>
      )}

      {/* Acciones */}
      {(action || secondaryAction) && (
        <div className="flex items-center gap-3">
          {action && (
            <Button
              onClick={action.onClick}
              size={variant === "default" ? "default" : "sm"}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              variant="outline"
              onClick={secondaryAction.onClick}
              size={variant === "default" ? "default" : "sm"}
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
