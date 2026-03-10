"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuthStore } from "@/stores/authStore";
import { assetsApi } from "@/lib/api";
import { Asset, AssetCreate, AssetStatus } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { EmptyState } from "@/components/shared/EmptyState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { SkeletonTable } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Server,
  Plus,
  Search,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";
import Link from "next/link";
import { fmtDate, cn } from "@/lib/utils";

const PAGE_SIZE = 20;

const STATUS_CONFIG: Record<AssetStatus, { label: string; color: string; bg: string }> = {
  authorized: {
    label: "Autorizado",
    color: "text-pass",
    bg: "bg-pass/10",
  },
  pending_review: {
    label: "Pendiente",
    color: "text-medium",
    bg: "bg-medium/10",
  },
  decommissioned: {
    label: "Dado de baja",
    color: "text-text-muted",
    bg: "bg-white/5",
  },
};

export default function AssetsPage() {
  const { token, isAnalyst } = useAuthStore();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const load = useCallback(
    async (pg: number) => {
      if (!token) return;
      setLoading(true);
      try {
        const res = await assetsApi.list(token, {
          limit: PAGE_SIZE,
          offset: pg * PAGE_SIZE,
          search: search || undefined,
        });
        setAssets(res.items);
        setTotal(res.total);
      } finally {
        setLoading(false);
      }
    },
    [token, search]
  );

  useEffect(() => {
    setPage(0);
    load(0);
  }, [search]);

  useEffect(() => {
    load(page);
  }, [page]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="p-6 space-y-5">
      <Breadcrumb items={[{ label: "Asset Registry" }]} />

      {/* Cabecera */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">
            Asset Registry
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            {total} activo{total !== 1 ? "s" : ""} registrado
            {total !== 1 ? "s" : ""}
          </p>
        </div>
        {isAnalyst() && (
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Nuevo activo
          </Button>
        )}
      </div>

      {/* Barra de búsqueda */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted pointer-events-none" />
        <Input
          placeholder="Buscar por IP, hostname, etiqueta…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Tabla */}
      {loading ? (
        <SkeletonTable rows={8} cols={5} />
      ) : assets.length === 0 ? (
        <EmptyState
          icon={Server}
          title={
            search ? "Sin resultados para esa búsqueda" : "No hay activos aún"
          }
          description={
            search
              ? "Prueba con otra IP, hostname o etiqueta."
              : "Agrega el primer activo para comenzar a descubrir exposiciones."
          }
          action={
            isAnalyst() && !search
              ? { label: "Agregar activo", onClick: () => setShowCreate(true) }
              : undefined
          }
        />
      ) : (
        <>
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Activo
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    OS
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Agregado
                  </th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {assets.map((asset) => (
                  <AssetRow key={asset.id} asset={asset} />
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginación */}
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

      {/* Modal crear activo */}
      <CreateAssetDialog
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreated={() => {
          setShowCreate(false);
          load(page);
        }}
        token={token!}
      />
    </div>
  );
}

// ─── Fila de activo ──────────────────────────────────────────────────────────

function AssetRow({ asset }: { asset: Asset }) {
  const cfg = STATUS_CONFIG[asset.status] ?? STATUS_CONFIG.pending_review;

  return (
    <tr className="h-row hover:bg-surface/60 transition-colors group">
      <td className="px-4">
        <div>
          <span className="text-sm font-medium text-text-primary font-technical">
            {asset.ip_address}
          </span>
          {asset.hostname && (
            <span className="block text-xs text-text-muted font-technical">
              {asset.hostname}
            </span>
          )}
        </div>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary capitalize">
          {asset.asset_type ?? "—"}
        </span>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary font-technical">
          {asset.os_hint ?? "—"}
        </span>
      </td>
      <td className="px-4">
        <span
          className={cn(
            "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
            cfg.bg,
            cfg.color
          )}
        >
          {cfg.label}
        </span>
      </td>
      <td className="px-4">
        <span className="text-sm text-text-secondary">
          {fmtDate(asset.created_at)}
        </span>
      </td>
      <td className="px-4 text-right">
        <Link href={`/assets/${asset.id}`}>
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

// ─── Modal crear activo ──────────────────────────────────────────────────────

interface CreateAssetDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
  token: string;
}

function CreateAssetDialog({
  open,
  onClose,
  onCreated,
  token,
}: CreateAssetDialogProps) {
  const [form, setForm] = useState<AssetCreate>({
    ip_address: "",
    hostname: "",
    asset_type: "server",
    os_hint: "",
    tags: [],
    notes: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update(field: keyof AssetCreate, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.ip_address.trim()) {
      setError("La dirección IP es obligatoria.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await assetsApi.create(token, form);
      onCreated();
      setForm({
        ip_address: "",
        hostname: "",
        asset_type: "server",
        os_hint: "",
        tags: [],
        notes: "",
      });
    } catch (err: unknown) {
      const e = err as { detail?: string };
      setError(e?.detail ?? "Error al crear el activo.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Nuevo activo</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="ip">Dirección IP *</Label>
            <Input
              id="ip"
              placeholder="192.168.1.100"
              value={form.ip_address}
              onChange={(e) => update("ip_address", e.target.value)}
              className="font-technical"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="hostname">Hostname</Label>
            <Input
              id="hostname"
              placeholder="web-server-01.corp"
              value={form.hostname}
              onChange={(e) => update("hostname", e.target.value)}
              className="font-technical"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="os">Sistema operativo (hint)</Label>
            <Input
              id="os"
              placeholder="Ubuntu 22.04 LTS"
              value={form.os_hint}
              onChange={(e) => update("os_hint", e.target.value)}
              className="font-technical"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="notes">Notas</Label>
            <Input
              id="notes"
              placeholder="Contexto adicional sobre este activo…"
              value={form.notes}
              onChange={(e) => update("notes", e.target.value)}
            />
          </div>

          {error && (
            <p className="text-sm text-critical bg-critical/10 rounded px-3 py-2">
              {error}
            </p>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creando…" : "Crear activo"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
