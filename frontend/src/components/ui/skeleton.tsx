import { cn } from "@/lib/utils";

// Design system: skeleton loaders, NOT spinners
interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Height in Tailwind classes, e.g. "h-4" */
  h?: string;
  /** Width in Tailwind classes, e.g. "w-32" */
  w?: string;
}

export function Skeleton({ className, h = "h-4", w = "w-full", ...props }: SkeletonProps) {
  return (
    <div
      className={cn("skeleton rounded", h, w, className)}
      {...props}
    />
  );
}

export function SkeletonRow({ cols = 4 }: { cols?: number }) {
  return (
    <div className="flex items-center gap-4 h-row px-4">
      {Array.from({ length: cols }).map((_, i) => (
        <Skeleton key={i} h="h-3" w={i === 0 ? "w-32" : i === 1 ? "w-24" : "w-20"} />
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="divide-y divide-border">
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonRow key={i} cols={cols} />
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-lg bg-surface border border-border p-5 space-y-3">
      <Skeleton h="h-3" w="w-20" />
      <Skeleton h="h-8" w="w-28" />
      <Skeleton h="h-3" w="w-40" />
    </div>
  );
}
