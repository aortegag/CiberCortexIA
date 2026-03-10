"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuthStore } from "@/stores/authStore";
import { discoveryApi, assetsApi } from "@/lib/api";
import { ScanJob, Asset } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { EmptyState } from "@/components/shared/EmptyState";
import { SkeletonTable } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { fmtDatetime, fmtRelative, cn } from "@/lib/utils";
import {
  Activity,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Clock,
} from "lucide-react";

const PAGE_SIZE = 20;

const STATUS_CONFIG: Record<
  string,
  { label: string; color: string; pulse?: boolean }
> = {
  pending:   { label: "Pendiente",   color: "text-text-muted" },
  running:   { label: "En curso",    color: "text-medium", pulse: true },
  completed: { label: "Completado",  color: "text-pass" },
  failed:    { label: "Error",       color: "text-critical" },
};

export default function ScansPage() {
  const { token } = useAuthStore();
  const [scans, setScans] = useState<ScanJob[]>([]);
  const [assetsMap, setAssetsMap] = useState<Record<string, Asset>>({});
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(
    async (pg: number, quiet = false) => {
      if (!token) return;
      if (!quiet) setLoading(true);
      else setRefreshing(true);
      try {
        const res = await discoveryApi.listScans(token, {
          limit: PAGE_SIZE,
          offset: pg * PAGE_SIZE,
        });
        setScans(res.items);
        setTotal(res.total);

        // Cargar datos de activos únicos
        const uniqueAssetIds = [...new Set(res.items.map((s) => s.asset_id))];
        const missing = uniqueAssetIds.filter((id) => !assetsMap[id]);
        if (missing.length > 0) {
          const fetched = await Promise.all(
            missing.map((id) => assetsApi.get(token, id).catch(() => null))
          );
          setAssetsMap((prev) => {
            const next = { ...prev };
            fetched.forEach((a) => {
              if (a) next[a.id] = a;
            });
            return next;
          });
        }
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [token]
  );

  useEffect(() => {
    load(0);
  }, []);

  useEffect(() => {
    load(page);
  }, [page]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="p-6 space-y-5">
      <Breadcrumb
        items={[
          { label: "Exposure", href: "/exposure" },
          { label: "Escaneos" },
        ]}
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">
            Historial de escaneos
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            {total} escaneo{total !== 1 ? "s" : ""} registrado
            {total !== 1 ? "s" : ""}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => load(page, true)}
          disabled={refreshing}
        >
          <RefreshCw
            className={cn("h-4 w-4 mr-2", refreshing && "animate-spin")}
          />
          Actualizar
        </Button>
      </div>

      {loading ? (
        <SkeletonTable rows={8} cols={5} />
      ) : scans.length === 0 ? (
        <EmptyState
          icon={Activity}
          title="Sin escaneos registrados"
          description="Inicia un escaneo desde la página de detalle de un activo autorizado."
        />
      ) : (
        <>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>Activo</Th>
                  <Th>Tipo</Th>
                  <Th>Estado</Th>
                  <Th>Iniciado</Th>
                  <Th>Finalizado</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {scans.map((scan) => (
                  <ScanRow
                    key={scan.id}
                    scan={scan}
                    asset={assetsMap[scan.asset_id]}
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
                <Button
                  variant="outline"
                  size="icon-sm"
                  disabled={page === 0}
                  onClick={() => setPage((p) => p - 1)}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="font-medium text-text-primary px-1">
                  {page + 1} / {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="icon-sm"
                  disabled={page >= totalPages - 1}
                  onClick={() => setPage((p) => p + 1)}
                >
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

function ScanRow({ scan, asset }: { scan: ScanJob; asset?: Asset }) {
  const cfg = STATUS_CONFIG[scan.status] ?? STATUS_CONFIG.pending;
  return (
    <tr className="h-row hover:bg-surface/60 transition-colors">
      <td className="px-4">
        {asset ? (
          <span className="text-sm font-technical text-text-primary">
            {asset.hostname ?? asset.ip_address}
          </span>
        ) : (
          <span className="text-sm font-technical text-text-muted">
            {scan.asset_id.slice(0, 8)}…
          </span>
        )}
      </td>
      <td className="px-4">
        <span className="text-sm font-technical text-text-secondary uppercase">
          {scan.scan_type}
        </span>
      </td>
      <td className="px-4">
        <span className={cn("text-sm font-medium flex items-center gap-1.5", cfg.color)}>
          {cfg.pulse && (
            <span className="h-1.5 w-1.5 rounded-full bg-medium animate-pulse" />
          )}
          {cfg.label}
        </span>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary flex items-center gap-1">
          <Clock className="h-3 w-3 text-text-muted" />
          {fmtRelative(scan.created_at)}
        </span>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary">
          {scan.completed_at ? fmtDatetime(scan.completed_at) : "—"}
        </span>
      </td>
    </tr>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
      {children}
    </th>
  );
}
