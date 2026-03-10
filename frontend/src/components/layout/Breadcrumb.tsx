import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav
      aria-label="Breadcrumb"
      className={cn("flex items-center gap-1 text-xs text-text-muted", className)}
    >
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <ChevronRight className="w-3 h-3 text-text-muted/50 shrink-0" />}
          {item.href && i < items.length - 1 ? (
            <Link
              href={item.href}
              className="hover:text-text-secondary transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className={cn(i === items.length - 1 && "text-text-secondary font-medium")}>
              {item.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}
