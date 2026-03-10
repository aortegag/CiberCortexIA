"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuthStore } from "@/stores/authStore";
import { reportsApi, assetsApi } from "@/lib/api";
import { Report, ReportType, ReportStatus, Asset } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { EmptyState } from "@/components/shared/EmptyState";
import { SkeletonTable } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { fmtDatetime, fmtRelative, cn } from "@/lib/utils";
import {
  FileText,
  Plus,
  Download,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from "lucide-react";

const PAGE_SIZE = 20;

const REPORT_TYPE_LABELS: Record<ReportType, string> = {
  executive_summary:  "Resumen ejecutivo",
  technical_exposure: "Exposición técnica",
  cis_compliance:     "Compliance CIS",
  full_audit:         "Auditoría completa",
};

const STATUS_CONFIG: Record<ReportStatus, { label: string; color: string }> = {
  pending:    { label: "Generando…", color: "text-medium" },
  completed:  { label: "Listo",      color: "text-pass" },
  failed:     { label: "Error",      color: "text-critical" },
};

export default function ReportsPage() {
  const { token, isAnalyst } = useAuthStore();
  const [reports, setReports] = useState<Report[]>([]);
  const [assetsMap, setAssetsMap] = useState<Record<string, Asset>>({});
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showGenerate, setShowGenerate] = useState(false);

  const load = useCallback(
    async (pg: number) => {
      if (!token) return;
      setLoading(true);
      try {
        const res = await reportsApi.list(token, {
          limit: PAGE_SIZE,
          offset: pg * PAGE_SIZE,
        });
        setReports(res.items);
        setTotal(res.total);

        const missing = [...new Set(res.items.map((r) => r.asset_id).filter(Boolean))].filter(
          (id) => id && !assetsMap[id]
        ) as string[];
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
      <Breadcrumb items={[{ label: "Reports" }]} />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">Report Engine</h1>
          <p className="text-sm text-text-secondary mt-0.5">
            {total} reporte{total !== 1 ? "s" : ""} generado{total !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => load(page)} disabled={loading}>
            <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
            Actualizar
          </Button>
          {isAnalyst() && (
            <Button size="sm" onClick={() => setShowGenerate(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Generar reporte
            </Button>
          )}
        </div>
      </div>

      {loading ? (
        <SkeletonTable rows={6} cols={5} />
      ) : reports.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="Sin reportes generados"
          description="Genera tu primer reporte de exposición o compliance CIS."
          action={
            isAnalyst()
              ? { label: "Generar reporte", onClick: () => setShowGenerate(true) }
              : undefined
          }
        />
      ) : (
        <>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>Tipo</Th>
                  <Th>Activo / Alcance</Th>
                  <Th>Estado</Th>
                  <Th>Generado</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {reports.map((r) => (
                  <ReportRow
                    key={r.id}
                    report={r}
                    asset={r.asset_id ? assetsMap[r.asset_id] : undefined}
                    token={token!}
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

      {/* Modal generar reporte */}
      <GenerateReportDialog
        open={showGenerate}
        onClose={() => setShowGenerate(false)}
        onGenerated={() => { setShowGenerate(false); load(0); }}
        token={token!}
      />
    </div>
  );
}

// ─── Fila de reporte ─────────────────────────────────────────────────────────

function ReportRow({
  report,
  asset,
  token,
}: {
  report: Report;
  asset?: Asset;
  token: string;
}) {
  const cfg = STATUS_CONFIG[report.status] ?? STATUS_CONFIG.pending;
  const typeLabel = REPORT_TYPE_LABELS[report.report_type] ?? report.report_type;

  function handleDownload() {
    const url = reportsApi.downloadUrl(token, report.id);
    window.open(url, "_blank");
  }

  return (
    <tr className="h-row hover:bg-surface/60 transition-colors">
      <td className="px-4">
        <span className="text-sm text-text-primary">{typeLabel}</span>
      </td>
      <td className="px-4">
        {asset ? (
          <span className="text-sm font-technical text-text-secondary">
            {asset.hostname ?? asset.ip_address}
          </span>
        ) : (
          <span className="text-sm text-text-muted">Global</span>
        )}
      </td>
      <td className="px-4">
        <span className={cn("text-sm font-medium flex items-center gap-1.5", cfg.color)}>
          {report.status === "pending" && (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          )}
          {cfg.label}
        </span>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary">
          {fmtRelative(report.created_at)}
        </span>
      </td>
      <td className="px-4 text-right">
        {report.status === "completed" && (
          <Button variant="ghost" size="sm" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-1.5" />
            PDF
          </Button>
        )}
      </td>
    </tr>
  );
}

// ─── Modal generar reporte ────────────────────────────────────────────────────

function GenerateReportDialog({
  open,
  onClose,
  onGenerated,
  token,
}: {
  open: boolean;
  onClose: () => void;
  onGenerated: () => void;
  token: string;
}) {
  const [reportType, setReportType] = useState<ReportType>("executive_summary");
  const [assetId, setAssetId] = useState<string>("");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    assetsApi.list(token, { limit: 100, offset: 0, status: "authorized" })
      .then((r) => setAssets(r.items))
      .catch(() => {});
  }, [open, token]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await reportsApi.generate(token, {
        report_type: reportType,
        asset_id: assetId || undefined,
      });
      onGenerated();
    } catch (err: unknown) {
      const e = err as { detail?: string };
      setError(e?.detail ?? "Error al iniciar la generación del reporte.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Generar reporte</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label>Tipo de reporte</Label>
            <Select value={reportType} onValueChange={(v) => setReportType(v as ReportType)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {(Object.entries(REPORT_TYPE_LABELS) as [ReportType, string][]).map(
                  ([value, label]) => (
                    <SelectItem key={value} value={value}>{label}</SelectItem>
                  )
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label>Activo (opcional — deja vacío para reporte global)</Label>
            <Select value={assetId} onValueChange={setAssetId}>
              <SelectTrigger>
                <SelectValue placeholder="Todos los activos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos los activos</SelectItem>
                {assets.map((a) => (
                  <SelectItem key={a.id} value={a.id}>
                    <span className="font-technical">{a.hostname ?? a.ip_address}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="bg-surface rounded-lg p-3 text-xs text-text-secondary">
            <p>El reporte se genera en segundo plano. Aparecerá en la lista cuando esté listo para descargar.</p>
          </div>

          {error && (
            <p className="text-sm text-critical bg-critical/10 rounded px-3 py-2">{error}</p>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Iniciando…</>
              ) : (
                "Generar PDF"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return (
    <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
      {children}
    </th>
  );
}
