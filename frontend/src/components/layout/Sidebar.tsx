"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Server,
  ShieldAlert,
  ShieldCheck,
  FileText,
  Sparkles,
  LogOut,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  /** If true, only shown to Analyst/Admin */
  analystOnly?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard",  href: "/dashboard",  icon: LayoutDashboard },
  { label: "Assets",     href: "/assets",     icon: Server },
  { label: "Exposure",   href: "/exposure",   icon: ShieldAlert, analystOnly: true },
  { label: "Hardening",  href: "/hardening",  icon: ShieldCheck, analystOnly: true },
  { label: "Reports",    href: "/reports",    icon: FileText },
  { label: "AI Assist",  href: "/ai",         icon: Sparkles },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout, isAnalyst } = useAuth();

  return (
    <aside className="fixed left-0 top-0 h-full w-sidebar bg-surface border-r border-border flex flex-col z-40">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 h-14 border-b border-border shrink-0">
        <div className="w-7 h-7 rounded-md bg-brand/20 border border-brand/30 flex items-center justify-center">
          <Activity className="w-3.5 h-3.5 text-brand" />
        </div>
        <div className="leading-none">
          <p className="text-xs font-semibold text-text-primary tracking-tight">CiberCortex</p>
          <p className="text-[10px] text-text-muted mt-0.5 font-mono">IA v0.1</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        <ul className="space-y-0.5">
          {NAV_ITEMS.map((item) => {
            if (item.analystOnly && !isAnalyst()) return null;

            const isActive =
              item.href === "/dashboard"
                ? pathname === "/dashboard"
                : pathname.startsWith(item.href);

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2.5 px-3 py-2 rounded text-sm transition-colors",
                    isActive
                      ? "bg-brand/10 text-brand font-medium"
                      : "text-text-secondary hover:bg-raised hover:text-text-primary"
                  )}
                >
                  <item.icon
                    className={cn("w-4 h-4 shrink-0", isActive ? "text-brand" : "text-text-secondary")}
                  />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User footer */}
      <div className="border-t border-border px-3 py-3 shrink-0">
        {user && (
          <div className="flex items-center gap-2.5 px-2 py-1.5 mb-1">
            <div className="w-6 h-6 rounded-full bg-brand/20 border border-brand/30 flex items-center justify-center shrink-0">
              <span className="text-[10px] font-semibold text-brand uppercase">
                {user.full_name?.[0] ?? user.email[0]}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-text-primary truncate">
                {user.full_name ?? user.email}
              </p>
              <p className="text-[10px] text-text-muted capitalize">{user.role}</p>
            </div>
          </div>
        )}
        <button
          onClick={logout}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded text-sm text-text-secondary hover:bg-raised hover:text-text-primary transition-colors"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
