"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { assetsApi, hardeningApi } from "@/lib/api";
import { Asset, AssetScoreResponse } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { ScoreDisplay, ScoreInline } from "@/components/shared/ScoreDisplay";
import { EmptyState } from "@/components/shared/EmptyState";
import { Card, CardContent } from "@/components/ui/card";
import { SkeletonTable, SkeletonCard } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  ShieldCheck,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import Link from "next/link";

interface AssetWithScore {
  asset: Asset;
  score: AssetScoreResponse | null;
}

export default function HardeningPage() {
  const { token } = useAuthStore();
  const [items, setItems] = useState<AssetWithScore[]>([]);
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
      const withScore = await Promise.all(
        assets.items.map(async (asset) => {
          const score = await hardeningApi
            .getScore(token!, asset.id)
            .catch(() => null);
          return { asset, score };
        })
      );
      // Ordenar: menor score primero (más urgente)
      withScore.sort((a, b) => {
        const sa = a.score?.weighted_score ?? 101;
        const sb = b.score?.weighted_score ?? 101;
        return sa - sb;
      });
      setItems(withScore);
    } finally {
      setLoading(false);
    }
  }

  // KPIs agregados
  const scoredItems = items.filter((i) => i.score !== null);
  const avgScore =
    scoredItems.length > 0
      ? scoredItems.reduce((acc, i) => acc + (i.score!.weighted_score ?? 0), 0) /
        scoredItems.length
      : null;
  const critical = items.filter((i) => (i.score?.weighted_score ?? 100) < 40).length;
  const compliant = items.filter((i) => (i.score?.weighted_score ?? 0) >= 80).length;

  return (
    <div className="p-6 space-y-6">
      <Breadcrumb items={[{ label: "Hardening" }]} />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">
            Hardening Dashboard
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            Compliance CIS y plan de remediación por activo
          </p>
        </div>
        <Link href="/hardening/assessments">
          <Button variant="outline" size="sm">
            Ver assessments
            <ChevronRight className="h-4 w-4 ml-1" />
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
          <Card>
            <CardContent className="p-5">
              <p className="text-xs text-text-muted uppercase tracking-wider mb-2">
                Score promedio
              </p>
              {avgScore !== null ? (
                <ScoreDisplay raw={avgScore} size="lg" showBar />
              ) : (
                <p className="text-2xl font-bold text-text-muted">—</p>
              )}
            </CardContent>
          </Card>
          <HardeningKpi
            label="Activos en riesgo crítico"
            value={critical}
            color={critical > 0 ? "text-critical" : "text-pass"}
            icon={critical > 0 ? TrendingDown : Minus}
          />
          <HardeningKpi
            label="Activos conformes (≥80)"
            value={compliant}
            color={compliant > 0 ? "text-pass" : "text-text-muted"}
            icon={compliant > 0 ? TrendingUp : Minus}
          />
        </div>
      )}

      {/* Tabla */}
      <div>
        <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-3">
          Scores por activo (ordenados por prioridad)
        </h2>

        {loading ? (
          <SkeletonTable rows={8} cols={5} />
        ) : items.length === 0 ? (
          <EmptyState
            icon={ShieldCheck}
            title="Sin activos autorizados"
            description="Autoriza activos y crea assessments CIS para ver scores de hardening."
          />
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>Activo</Th>
                  <Th center>Score raw</Th>
                  <Th center>Score ponderado</Th>
                  <Th>Nivel</Th>
                  <Th>Checks</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {items.map(({ asset, score }) => (
                  <HardeningRow key={asset.id} asset={asset} score={score} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function HardeningRow({
  asset,
  score,
}: {
  asset: Asset;
  score: AssetScoreResponse | null;
}) {
  const level = score ? complianceLevel(score.weighted_score) : null;
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
        {score ? (
          <ScoreInline score={score.raw_score} />
        ) : (
          <span className="text-xs text-text-muted">—</span>
        )}
      </td>
      <td className="px-4 text-center">
        {score ? (
          <ScoreInline score={score.weighted_score} />
        ) : (
          <span className="text-xs text-text-muted">—</span>
        )}
      </td>
      <td className="px-4">
        {level ? (
          <ComplianceLevelChip level={level} />
        ) : (
          <span className="text-xs text-text-muted">Sin assessment</span>
        )}
      </td>
      <td className="px-4">
        {score ? (
          <span className="text-xs text-text-secondary font-technical">
            <span className="text-pass">{score.passed_checks}</span>
            <span className="text-text-muted mx-1">/</span>
            {score.total_checks}
          </span>
        ) : (
          <span className="text-xs text-text-muted">—</span>
        )}
      </td>
      <td className="px-4 text-right">
        <Link href={`/assets/${asset.id}?tab=hardening`}>
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

function ComplianceLevelChip({ level }: { level: ReturnType<typeof complianceLevel> }) {
  const cfg = {
    critical: { label: "Crítico",   color: "text-critical", bg: "bg-critical/10" },
    low:      { label: "Bajo",      color: "text-high",     bg: "bg-high/10" },
    medium:   { label: "Medio",     color: "text-medium",   bg: "bg-medium/10" },
    good:     { label: "Bueno",     color: "text-pass",     bg: "bg-pass/10" },
  }[level];
  return (
    <span className={cn("inline-flex items-center px-2 py-0.5 rounded text-xs font-medium", cfg.bg, cfg.color)}>
      {cfg.label}
    </span>
  );
}

function HardeningKpi({
  label,
  value,
  color,
  icon: Icon,
}: {
  label: string;
  value: number;
  color: string;
  icon: React.ElementType;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-2">{label}</p>
            <p className={cn("text-3xl font-bold", color)}>{value}</p>
          </div>
          <div className="p-2 rounded-lg bg-white/5">
            <Icon className={cn("h-5 w-5", color)} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function Th({ children, center }: { children?: React.ReactNode; center?: boolean }) {
  return (
    <th className={cn("px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider", center ? "text-center" : "text-left")}>
      {children}
    </th>
  );
}

function complianceLevel(score: number): "critical" | "low" | "medium" | "good" {
  if (score < 40) return "critical";
  if (score < 60) return "low";
  if (score < 80) return "medium";
  return "good";
}
