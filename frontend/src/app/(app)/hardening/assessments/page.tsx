"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuthStore } from "@/stores/authStore";
import { hardeningApi, assetsApi } from "@/lib/api";
import { Assessment, Asset } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { ScoreInline } from "@/components/shared/ScoreDisplay";
import { EmptyState } from "@/components/shared/EmptyState";
import { SkeletonTable } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { fmtDate, fmtRelative, cn } from "@/lib/utils";
import {
  ShieldCheck,
  ChevronRight,
  ChevronLeft,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";

const PAGE_SIZE = 20;

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft:      { label: "Borrador",    color: "text-text-muted" },
  in_progress:{ label: "En progreso", color: "text-medium" },
  completed:  { label: "Completada",  color: "text-pass" },
};

export default function AssessmentsPage() {
  const { token } = useAuthStore();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [assetsMap, setAssetsMap] = useState<Record<string, Asset>>({});
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);

  const load = useCallback(
    async (pg: number) => {
      if (!token) return;
      setLoading(true);
      try {
        const res = await hardeningApi.listAssessments(token, {
          limit: PAGE_SIZE,
          offset: pg * PAGE_SIZE,
        });
        setAssessments(res.items);
        setTotal(res.total);

        // Cargar activos faltantes
        const missing = [...new Set(res.items.map((a) => a.asset_id))].filter(
          (id) => !assetsMap[id]
        );
        if (missing.length) {
          const fetched = await Promise.all(
            missing.map((id) => assetsApi.get(token, id).catch(() => null))
          );
          setAssetsMap((prev) => {
            const next = { ...prev };
            fetched.forEach((a) => { if (a) next[a.id] = a; });
            return next;
          });
        }
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  useEffect(() => { load(0); }, []);
  useEffect(() => { load(page); }, [page]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="p-6 space-y-5">
      <Breadcrumb
        items={[
          { label: "Hardening", href: "/hardening" },
          { label: "Assessments" },
        ]}
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">Assessments CIS</h1>
          <p className="text-sm text-text-secondary mt-0.5">
            {total} assessment{total !== 1 ? "s" : ""} registrada{total !== 1 ? "s" : ""}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => load(page)} disabled={loading}>
          <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
          Actualizar
        </Button>
      </div>

      {loading ? (
        <SkeletonTable rows={8} cols={5} />
      ) : assessments.length === 0 ? (
        <EmptyState
          icon={ShieldCheck}
          title="Sin assessments"
          description="Crea una assessment CIS desde la página de detalle de un activo."
        />
      ) : (
        <>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>Activo</Th>
                  <Th>Catálogo</Th>
                  <Th center>Score</Th>
                  <Th>Estado</Th>
                  <Th>Fecha</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {assessments.map((a) => (
                  <AssessmentRow
                    key={a.id}
                    assessment={a}
                    asset={assetsMap[a.asset_id]}
                  />
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between text-sm text-text-secondary">
              <span>
                Mostrando {page * PAGE_SIZE + 1}–
                {Math.min((page + 1) * PAGE_SIZE, total)} de {total}
              </span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="icon-sm" disabled={page === 0}
                  onClick={() => setPage((p) => p - 1)}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="font-medium text-text-primary px-1">
                  {page + 1} / {totalPages}
                </span>
                <Button variant="outline" size="icon-sm" disabled={page >= totalPages - 1}
                  onClick={() => setPage((p) => p + 1)}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function AssessmentRow({
  assessment,
  asset,
}: {
  assessment: Assessment;
  asset?: Asset;
}) {
  const cfg = STATUS_CONFIG[assessment.status] ?? STATUS_CONFIG.draft;
  return (
    <tr className="h-row hover:bg-surface/60 transition-colors group">
      <td className="px-4">
        <span className="text-sm font-technical text-text-primary">
          {asset?.hostname ?? asset?.ip_address ?? assessment.asset_id.slice(0, 8) + "…"}
        </span>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary font-technical">
          {assessment.catalog_id ?? "—"}
        </span>
      </td>
      <td className="px-4 text-center">
        {assessment.score != null ? (
          <ScoreInline score={assessment.score} />
        ) : (
          <span className="text-xs text-text-muted">—</span>
        )}
      </td>
      <td className="px-4">
        <span className={cn("text-sm font-medium", cfg.color)}>
          {cfg.label}
        </span>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary">
          {fmtRelative(assessment.created_at)}
        </span>
      </td>
      <td className="px-4 text-right">
        <Link href={`/hardening/assessments/${assessment.id}`}>
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

function Th({ children, center }: { children?: React.ReactNode; center?: boolean }) {
  return (
    <th className={cn("px-4 py-3 text-xs font-medium text-text-muted uppercase tracking-wider",
      center ? "text-center" : "text-left")}>
      {children}
    </th>
  );
}
