"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { hardeningApi, assetsApi, aiApi } from "@/lib/api";
import { AssessmentDetail, CheckResult, Asset } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { SeverityBadge, parseSeverity } from "@/components/shared/SeverityBadge";
import { ScoreDisplay } from "@/components/shared/ScoreDisplay";
import { EmptyState } from "@/components/shared/EmptyState";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SkeletonTable, Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { fmtRelative, fmtDatetime, cn } from "@/lib/utils";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Minus,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Loader2,
} from "lucide-react";

const RESULT_CONFIG: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  pass:    { icon: CheckCircle2, color: "text-pass",        label: "Pass" },
  fail:    { icon: XCircle,      color: "text-critical",    label: "Fail" },
  na:      { icon: Minus,        color: "text-text-muted",  label: "N/A" },
  unknown: { icon: Minus,        color: "text-text-muted",  label: "Pendiente" },
};

export default function AssessmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { token, isAnalyst } = useAuthStore();
  const [detail, setDetail] = useState<AssessmentDetail | null>(null);
  const [asset, setAsset] = useState<Asset | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token || !id) return;
    hardeningApi
      .getAssessment(token, id)
      .then(async (d) => {
        setDetail(d);
        const a = await assetsApi.get(token, d.asset_id).catch(() => null);
        setAsset(a);
      })
      .finally(() => setLoading(false));
  }, [token, id]);

  if (loading) return <AssessmentDetailSkeleton />;
  if (!detail) {
    return (
      <div className="p-6">
        <EmptyState
          icon={ShieldCheck}
          title="Assessment no encontrada"
          description="La assessment solicitada no existe o no tienes acceso."
        />
      </div>
    );
  }

  const pass = detail.results.filter((r) => r.result === "pass").length;
  const fail = detail.results.filter((r) => r.result === "fail").length;
  const na   = detail.results.filter((r) => r.result === "na").length;
  const total = detail.results.length;

  return (
    <div className="p-6 space-y-5">
      <Breadcrumb
        items={[
          { label: "Hardening",    href: "/hardening" },
          { label: "Assessments",  href: "/hardening/assessments" },
          { label: asset?.hostname ?? asset?.ip_address ?? id.slice(0, 8) },
        ]}
      />

      {/* Cabecera */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">
            Assessment CIS —{" "}
            <span className="font-technical">
              {asset?.hostname ?? asset?.ip_address ?? "…"}
            </span>
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            Catálogo: <span className="font-technical">{detail.catalog_id ?? "—"}</span>
            {" · "}
            Creada {fmtRelative(detail.created_at)}
          </p>
        </div>
      </div>

      {/* KPIs + Score */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <Card className="lg:col-span-1">
          <CardContent className="p-5">
            {detail.score != null ? (
              <ScoreDisplay
                raw={detail.score}
                size="xl"
                showBar
                label="Compliance Score"
              />
            ) : (
              <p className="text-text-muted text-sm">Score pendiente</p>
            )}
          </CardContent>
        </Card>
        <StatCard label="Pass" value={pass} color="text-pass" icon={CheckCircle2} />
        <StatCard label="Fail" value={fail} color="text-critical" icon={XCircle} />
        <StatCard label="N/A" value={na} color="text-text-muted" icon={Minus} />
      </div>

      {/* Tabla de check results */}
      <div>
        <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-3">
          Check results ({total})
        </h2>
        {total === 0 ? (
          <EmptyState
            icon={ShieldCheck}
            variant="compact"
            title="Sin checks registrados"
            description="Agrega resultados de checks a esta assessment."
          />
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>Check</Th>
                  <Th>Severidad</Th>
                  <Th center>Resultado</Th>
                  <Th>Evidencia</Th>
                  <Th>Evaluado</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {detail.results.map((r) => (
                  <CheckResultRow
                    key={r.id}
                    result={r}
                    token={token!}
                    analystOnly={isAnalyst()}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── CheckResultRow con expansión + AI explain ───────────────────────────────

function CheckResultRow({
  result,
  token,
  analystOnly,
}: {
  result: CheckResult;
  token: string;
  analystOnly: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const [aiExpl, setAiExpl] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const cfg = RESULT_CONFIG[result.result] ?? RESULT_CONFIG.unknown;
  const Icon = cfg.icon;

  async function explainCheck() {
    if (aiExpl || aiLoading) return;
    setAiLoading(true);
    try {
      const res = await aiApi.explainCheck(token, result.check_id);
      setAiExpl(res.explanation);
    } catch {
      setAiExpl("No se pudo obtener la explicación. Inténtalo de nuevo.");
    } finally {
      setAiLoading(false);
    }
  }

  return (
    <>
      <tr
        className="h-row hover:bg-surface/60 transition-colors cursor-pointer"
        onClick={() => setExpanded((v) => !v)}
      >
        <td className="px-4">
          <span className="text-sm font-technical text-text-primary">
            {result.check_id}
          </span>
        </td>
        <td className="px-4">
          <SeverityBadge severity={parseSeverity(result.severity ?? "info")} />
        </td>
        <td className="px-4 text-center">
          <span className={cn("inline-flex items-center gap-1 text-sm font-medium", cfg.color)}>
            <Icon className="h-4 w-4" />
            {cfg.label}
          </span>
        </td>
        <td className="px-4">
          <span className="text-xs text-text-secondary truncate max-w-xs block">
            {result.evidence ?? (
              <span className="text-text-muted italic">Sin evidencia</span>
            )}
          </span>
        </td>
        <td className="px-4">
          <span className="text-sm text-text-secondary">
            {result.evidence_at ? fmtRelative(result.evidence_at) : "—"}
          </span>
        </td>
        <td className="px-4 text-right">
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-text-muted inline" />
          ) : (
            <ChevronDown className="h-4 w-4 text-text-muted inline" />
          )}
        </td>
      </tr>

      {expanded && (
        <tr className="bg-surface/40">
          <td colSpan={6} className="px-4 py-4">
            <div className="space-y-3">
              {/* Descripción / notas */}
              {result.notes && (
                <p className="text-sm text-text-secondary">{result.notes}</p>
              )}

              {/* Evidencia completa */}
              {result.evidence && (
                <div className="bg-raised rounded px-3 py-2">
                  <p className="text-xs text-text-muted uppercase mb-1">Evidencia</p>
                  <p className="text-sm font-technical text-text-primary">
                    {result.evidence}
                  </p>
                  {result.evidence_method && (
                    <p className="text-xs text-text-muted mt-1">
                      Método: {result.evidence_method}
                    </p>
                  )}
                </div>
              )}

              {/* AI Explain */}
              <div className="border-t border-border/50 pt-3">
                {!aiExpl && !aiLoading && (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-brand hover:text-brand-hover"
                    onClick={(e) => { e.stopPropagation(); explainCheck(); }}
                  >
                    <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                    Explicar con IA
                  </Button>
                )}
                {aiLoading && (
                  <div className="flex items-center gap-2 text-sm text-text-muted">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Consultando IA…
                  </div>
                )}
                {aiExpl && (
                  <div className="bg-brand/5 border border-brand/20 rounded px-3 py-2">
                    <p className="text-xs text-brand uppercase mb-1 flex items-center gap-1">
                      <Sparkles className="h-3 w-3" /> AI Assist
                    </p>
                    <p className="text-sm text-text-primary leading-relaxed">{aiExpl}</p>
                  </div>
                )}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function StatCard({
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
      <CardContent className="p-5 flex items-start justify-between">
        <div>
          <p className="text-xs text-text-muted uppercase tracking-wider mb-2">{label}</p>
          <p className={cn("text-3xl font-bold", color)}>{value}</p>
        </div>
        <div className="p-2 rounded-lg bg-white/5">
          <Icon className={cn("h-5 w-5", color)} />
        </div>
      </CardContent>
    </Card>
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

function AssessmentDetailSkeleton() {
  return (
    <div className="p-6 space-y-5">
      <Skeleton className="h-4 w-64" />
      <Skeleton className="h-7 w-80" />
      <div className="grid grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-28 rounded-lg" />)}
      </div>
      <SkeletonTable rows={6} cols={5} />
    </div>
  );
}
