"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { assetsApi, discoveryApi } from "@/lib/api";
import { Asset, ScanJob } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { ScoreInline } from "@/components/shared/ScoreDisplay";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SkeletonCard } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { fmtDatetime, fmtRelative } from "@/lib/utils";
import {
  Shield,
  Server,
  AlertTriangle,
  CheckCircle2,
  Activity,
  ChevronRight,
  Clock,
} from "lucide-react";
import Link from "next/link";

interface DashboardStats {
  totalAssets: number;
  authorizedAssets: number;
  activeScans: number;
  recentAssets: Asset[];
  recentScans: ScanJob[];
}

export default function DashboardPage() {
  const { user, token } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    loadStats();
  }, [token]);

  async function loadStats() {
    try {
      const [assets, scans] = await Promise.all([
        assetsApi.list(token!, { limit: 100, offset: 0 }),
        discoveryApi.listScans(token!, { limit: 5 }),
      ]);

      const authorized = assets.items.filter((a) => a.status === "authorized");
      const active = scans.items.filter(
        (s) => s.status === "running" || s.status === "pending"
      );

      setStats({
        totalAssets: assets.total,
        authorizedAssets: authorized.length,
        activeScans: active.length,
        recentAssets: assets.items.slice(0, 5),
        recentScans: scans.items,
      });
    } catch {
      // Si falla la carga, mostramos estado vacío
      setStats({
        totalAssets: 0,
        authorizedAssets: 0,
        activeScans: 0,
        recentAssets: [],
        recentScans: [],
      });
    } finally {
      setLoading(false);
    }
  }

  const greeting = getGreeting();

  return (
    <div className="p-6 space-y-6">
      {/* Breadcrumb */}
      <Breadcrumb items={[{ label: "Dashboard" }]} />

      {/* Cabecera */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">
            {greeting}, {user?.full_name?.split(" ")[0] ?? user?.email}
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            Plataforma de ciberseguridad defensiva — visión general
          </p>
        </div>
        <Link href="/assets">
          <Button variant="outline" size="sm">
            Ver activos
            <ChevronRight className="h-3.5 w-3.5 ml-1" />
          </Button>
        </Link>
      </div>

      {/* KPIs */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard
            icon={Server}
            label="Activos registrados"
            value={stats!.totalAssets}
            sub={`${stats!.authorizedAssets} autorizados`}
            color="text-brand"
          />
          <KpiCard
            icon={Activity}
            label="Escaneos activos"
            value={stats!.activeScans}
            sub="en curso ahora"
            color={stats!.activeScans > 0 ? "text-medium" : "text-pass"}
          />
          <KpiCard
            icon={Shield}
            label="Workspace"
            value="Activo"
            sub="Exposure + Hardening"
            color="text-pass"
            isText
          />
        </div>
      )}

      {/* Fila inferior: Activos recientes + Escaneos recientes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activos recientes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-sm font-medium text-text-secondary uppercase tracking-wider">
              Activos recientes
            </CardTitle>
            <Link
              href="/assets"
              className="text-xs text-brand hover:text-brand-hover transition-colors"
            >
              Ver todos
            </Link>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="px-4 pb-4 space-y-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-row flex items-center gap-3 animate-pulse">
                    <div className="h-4 w-32 bg-white/5 rounded" />
                    <div className="h-4 w-16 bg-white/5 rounded ml-auto" />
                  </div>
                ))}
              </div>
            ) : stats!.recentAssets.length === 0 ? (
              <div className="py-10 text-center text-text-muted text-sm">
                No hay activos registrados aún.{" "}
                <Link href="/assets" className="text-brand hover:underline">
                  Agregar activo
                </Link>
              </div>
            ) : (
              <table className="w-full">
                <tbody>
                  {stats!.recentAssets.map((asset) => (
                    <tr
                      key={asset.id}
                      className="h-row border-b border-border/50 last:border-0 hover:bg-surface/60 transition-colors"
                    >
                      <td className="px-4">
                        <Link
                          href={`/assets/${asset.id}`}
                          className="text-sm font-medium text-text-primary hover:text-brand transition-colors font-technical"
                        >
                          {asset.hostname ?? asset.ip_address}
                        </Link>
                        {asset.hostname && (
                          <span className="text-xs text-text-muted ml-2 font-technical">
                            {asset.ip_address}
                          </span>
                        )}
                      </td>
                      <td className="px-4 text-right">
                        <AssetStatusBadge status={asset.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>

        {/* Escaneos recientes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="text-sm font-medium text-text-secondary uppercase tracking-wider">
              Escaneos recientes
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="px-4 pb-4 space-y-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-row flex items-center gap-3 animate-pulse">
                    <div className="h-4 w-40 bg-white/5 rounded" />
                    <div className="h-4 w-14 bg-white/5 rounded ml-auto" />
                  </div>
                ))}
              </div>
            ) : stats!.recentScans.length === 0 ? (
              <div className="py-10 text-center text-text-muted text-sm">
                Ningún escaneo ejecutado aún.
              </div>
            ) : (
              <table className="w-full">
                <tbody>
                  {stats!.recentScans.map((scan) => (
                    <tr
                      key={scan.id}
                      className="h-row border-b border-border/50 last:border-0 hover:bg-surface/60 transition-colors"
                    >
                      <td className="px-4">
                        <span className="text-sm text-text-primary font-technical">
                          {scan.scan_type}
                        </span>
                        <span className="text-xs text-text-muted ml-2 flex items-center gap-1 inline-flex">
                          <Clock className="h-3 w-3" />
                          {fmtRelative(scan.created_at)}
                        </span>
                      </td>
                      <td className="px-4 text-right">
                        <ScanStatusBadge status={scan.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ─── Sub-componentes locales ─────────────────────────────────────────────────

function KpiCard({
  icon: Icon,
  label,
  value,
  sub,
  color,
  isText = false,
}: {
  icon: React.ElementType;
  label: string;
  value: number | string;
  sub: string;
  color: string;
  isText?: boolean;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-2">
              {label}
            </p>
            <p className={`text-3xl font-bold ${isText ? "text-lg pt-1" : ""} ${color}`}>
              {value}
            </p>
            <p className="text-xs text-text-secondary mt-1">{sub}</p>
          </div>
          <div className="p-2 rounded-lg bg-white/5">
            <Icon className={`h-5 w-5 ${color}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function AssetStatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; variant: "default" | "outline" | "muted" }> = {
    authorized: { label: "Autorizado", variant: "default" },
    pending_review: { label: "Pendiente", variant: "muted" },
    decommissioned: { label: "Dado de baja", variant: "outline" },
  };
  const cfg = map[status] ?? { label: status, variant: "muted" };
  return <Badge variant={cfg.variant}>{cfg.label}</Badge>;
}

function ScanStatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    pending: "text-text-muted",
    running: "text-medium",
    completed: "text-pass",
    failed: "text-critical",
  };
  const labels: Record<string, string> = {
    pending: "Pendiente",
    running: "En curso",
    completed: "Completado",
    failed: "Error",
  };
  return (
    <span className={`text-xs font-medium ${map[status] ?? "text-text-muted"}`}>
      {labels[status] ?? status}
    </span>
  );
}

function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Buenos días";
  if (h < 20) return "Buenas tardes";
  return "Buenas noches";
}
