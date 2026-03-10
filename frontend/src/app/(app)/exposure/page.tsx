"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { assetsApi, cveApi } from "@/lib/api";
import { Asset, AssetRiskSummary } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { EmptyState } from "@/components/shared/EmptyState";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SkeletonTable, SkeletonCard } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Shield,
  AlertTriangle,
  Activity,
  ChevronRight,
  Server,
} from "lucide-react";
import Link from "next/link";

interface AssetWithRisk {
  asset: Asset;
  risk: AssetRiskSummary | null;
}

export default function ExposurePage() {
  const { token } = useAuthStore();
  const [items, setItems] = useState<AssetWithRisk[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    loadData();
  }, [token]);

  async function loadData() {
    setLoading(true);
    try {
      const assets = await assetsApi.list(token!, {
        limit: 100,
        offset: 0,
        status: "authorized",
      });

      const withRisk = await Promise.all(
        assets.items.map(async (asset) => {
          const risk = await cveApi
            .riskSummary(token!, asset.id)
            .catch(() => null);
          return { asset, risk };
        })
      );

      // Ordenar: más riesgo primero
      withRisk.sort((a, b) => {
        const scoreA = riskScore(a.risk);
        const scoreB = riskScore(b.risk);
        return scoreB - scoreA;
      });

      setItems(withRisk);
    } finally {
      setLoading(false);
    }
  }

  const totalCritical = items.reduce(
    (acc, i) => acc + (i.risk?.critical_count ?? 0),
    0
  );
  const totalHigh = items.reduce(
    (acc, i) => acc + (i.risk?.high_count ?? 0),
    0
  );
  const assetsWithCritical = items.filter(
    (i) => (i.risk?.critical_count ?? 0) > 0
  ).length;

  return (
    <div className="p-6 space-y-6">
      <Breadcrumb items={[{ label: "Exposure Analysis" }]} />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">
            Exposure Analysis
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            Superficie de ataque y correlación CVE por activo autorizado
          </p>
        </div>
        <Link href="/exposure/scans">
          <Button variant="outline" size="sm">
            <Activity className="h-4 w-4 mr-2" />
            Ver escaneos
          </Button>
        </Link>
      </div>

      {/* KPIs */}
      {loading ? (
        <div className="grid grid-cols-3 gap-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <ExposureKpi
            label="CVEs Críticas"
            value={totalCritical}
            icon={AlertTriangle}
            color="text-critical"
            bg="bg-critical/10"
          />
          <ExposureKpi
            label="CVEs Altas"
            value={totalHigh}
            icon={AlertTriangle}
            color="text-high"
            bg="bg-high/10"
          />
          <ExposureKpi
            label="Activos con riesgo crítico"
            value={assetsWithCritical}
            icon={Server}
            color="text-medium"
            bg="bg-medium/10"
          />
        </div>
      )}

      {/* Tabla de activos con riesgo */}
      <div>
        <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-3">
          Activos autorizados — resumen de exposición
        </h2>

        {loading ? (
          <SkeletonTable rows={8} cols={6} />
        ) : items.length === 0 ? (
          <EmptyState
            icon={Shield}
            title="Sin activos autorizados"
            description="Autoriza activos en el Asset Registry para comenzar el análisis de exposición."
            action={{ label: "Ir a Assets", onClick: () => {} }}
          />
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>Activo</Th>
                  <Th center>Critical</Th>
                  <Th center>High</Th>
                  <Th center>Medium</Th>
                  <Th center>Low</Th>
                  <Th>Riesgo</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {items.map(({ asset, risk }) => (
                  <AssetRiskRow key={asset.id} asset={asset} risk={risk} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Sub-componentes ─────────────────────────────────────────────────────────

function AssetRiskRow({
  asset,
  risk,
}: {
  asset: Asset;
  risk: AssetRiskSummary | null;
}) {
  const level = riskLevel(risk);

  return (
    <tr className="h-row hover:bg-surface/60 transition-colors group">
      <td className="px-4">
        <div>
          <span className="text-sm font-medium text-text-primary font-technical">
            {asset.hostname ?? asset.ip_address}
          </span>
          {asset.hostname && (
            <span className="block text-xs text-text-muted font-technical">
              {asset.ip_address}
            </span>
          )}
        </div>
      </td>
      <td className="px-4 text-center">
        <CveCount count={risk?.critical_count ?? 0} severity="critical" />
      </td>
      <td className="px-4 text-center">
        <CveCount count={risk?.high_count ?? 0} severity="high" />
      </td>
      <td className="px-4 text-center">
        <CveCount count={risk?.medium_count ?? 0} severity="medium" />
      </td>
      <td className="px-4 text-center">
        <CveCount count={risk?.low_count ?? 0} severity="low" />
      </td>
      <td className="px-4">
        {level ? (
          <SeverityBadge severity={level} label={RISK_LABEL[level]} />
        ) : (
          <span className="text-xs text-text-muted">Sin datos</span>
        )}
      </td>
      <td className="px-4 text-right">
        <Link href={`/assets/${asset.id}?tab=exposure`}>
          <Button
            variant="ghost"
            size="icon-sm"
            className="opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </Link>
      </td>
    </tr>
  );
}

function CveCount({
  count,
  severity,
}: {
  count: number;
  severity: "critical" | "high" | "medium" | "low";
}) {
  if (count === 0)
    return <span className="text-xs text-text-muted font-technical">—</span>;
  const colors: Record<string, string> = {
    critical: "text-critical",
    high: "text-high",
    medium: "text-medium",
    low: "text-low",
  };
  return (
    <span className={cn("text-sm font-technical font-semibold", colors[severity])}>
      {count}
    </span>
  );
}

function ExposureKpi({
  label,
  value,
  icon: Icon,
  color,
  bg,
}: {
  label: string;
  value: number;
  icon: React.ElementType;
  color: string;
  bg: string;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-2">
              {label}
            </p>
            <p className={cn("text-3xl font-bold", color)}>{value}</p>
          </div>
          <div className={cn("p-2 rounded-lg", bg)}>
            <Icon className={cn("h-5 w-5", color)} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function Th({
  children,
  center,
}: {
  children?: React.ReactNode;
  center?: boolean;
}) {
  return (
    <th
      className={cn(
        "px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider",
        center ? "text-center" : "text-left"
      )}
    >
      {children}
    </th>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const RISK_LABEL: Record<string, string> = {
  critical: "Crítico",
  high: "Alto",
  medium: "Medio",
  low: "Bajo",
  pass: "Sin riesgo",
};

function riskScore(risk: AssetRiskSummary | null): number {
  if (!risk) return 0;
  return (
    (risk.critical_count ?? 0) * 1000 +
    (risk.high_count ?? 0) * 100 +
    (risk.medium_count ?? 0) * 10 +
    (risk.low_count ?? 0)
  );
}

function riskLevel(
  risk: AssetRiskSummary | null
): "critical" | "high" | "medium" | "low" | "pass" | null {
  if (!risk) return null;
  if ((risk.critical_count ?? 0) > 0) return "critical";
  if ((risk.high_count ?? 0) > 0) return "high";
  if ((risk.medium_count ?? 0) > 0) return "medium";
  if ((risk.low_count ?? 0) > 0) return "low";
  return "pass";
}
