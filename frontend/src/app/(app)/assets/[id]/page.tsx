"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { assetsApi, discoveryApi, cveApi, hardeningApi } from "@/lib/api";
import {
  Asset,
  ScanJob,
  DiscoveredService,
  CVECorrelation,
  AssetScoreResponse,
  AssetRiskSummary,
} from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { SeverityBadge, parseSeverity } from "@/components/shared/SeverityBadge";
import { ScoreDisplay } from "@/components/shared/ScoreDisplay";
import { EmptyState } from "@/components/shared/EmptyState";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { SkeletonTable, SkeletonCard, Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fmtDatetime, fmtRelative, cn } from "@/lib/utils";
import {
  Play,
  AlertTriangle,
  ShieldCheck,
  Server,
  Activity,
  Clock,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Eye,
  EyeOff,
} from "lucide-react";

const POLL_INTERVAL = 3000;

export default function AssetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { token, isAnalyst } = useAuthStore();

  const [asset, setAsset] = useState<Asset | null>(null);
  const [loadingAsset, setLoadingAsset] = useState(true);
  const [activeScan, setActiveScan] = useState<ScanJob | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  // Carga del activo
  useEffect(() => {
    if (!token || !id) return;
    assetsApi
      .get(token, id)
      .then(setAsset)
      .finally(() => setLoadingAsset(false));
    loadActiveScan();
  }, [token, id]);

  async function loadActiveScan() {
    if (!token) return;
    const scans = await discoveryApi.listScans(token, {
      asset_id: id,
      limit: 1,
    });
    const active = scans.items.find(
      (s) => s.status === "running" || s.status === "pending"
    );
    setActiveScan(active ?? null);
  }

  // Polling del escaneo activo
  useEffect(() => {
    if (!activeScan) {
      if (pollRef.current) clearInterval(pollRef.current);
      return;
    }
    pollRef.current = setInterval(async () => {
      if (!token) return;
      const updated = await discoveryApi.getScan(token, activeScan.id);
      if (updated.status !== "running" && updated.status !== "pending") {
        setActiveScan(null);
      } else {
        setActiveScan(updated);
      }
    }, POLL_INTERVAL);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [activeScan?.id]);

  async function startScan() {
    if (!token || !asset) return;
    const job = await discoveryApi.startScan(token, asset.id);
    setActiveScan(job);
  }

  async function authorizeAsset() {
    if (!token || !asset) return;
    const updated = await assetsApi.authorize(token, asset.id);
    setAsset(updated);
  }

  if (loadingAsset) return <AssetDetailSkeleton />;
  if (!asset) {
    return (
      <div className="p-6">
        <EmptyState
          icon={Server}
          title="Activo no encontrado"
          description="El activo solicitado no existe o no tienes acceso."
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-5">
      <Breadcrumb
        items={[
          { label: "Assets", href: "/assets" },
          { label: asset.hostname ?? asset.ip_address },
        ]}
      />

      {/* Cabecera del activo */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold text-text-primary font-technical">
              {asset.hostname ?? asset.ip_address}
            </h1>
            <AssetStatusChip status={asset.status} />
          </div>
          {asset.hostname && (
            <p className="text-sm text-text-muted font-technical mt-0.5">
              {asset.ip_address}
            </p>
          )}
          {asset.os_hint && (
            <p className="text-xs text-text-muted mt-1">{asset.os_hint}</p>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {asset.status === "pending_review" && isAnalyst() && (
            <Button variant="outline" size="sm" onClick={authorizeAsset}>
              <CheckCircle2 className="h-4 w-4 mr-1.5 text-pass" />
              Autorizar
            </Button>
          )}
          {asset.status === "authorized" && isAnalyst() && (
            <Button
              size="sm"
              disabled={!!activeScan}
              onClick={startScan}
            >
              <Play className="h-4 w-4 mr-1.5" />
              {activeScan ? "Escaneando…" : "Iniciar escaneo"}
            </Button>
          )}
        </div>
      </div>

      {/* ScanStatusBar — visible mientras hay escaneo activo */}
      {activeScan && (
        <ScanStatusBar scan={activeScan} />
      )}

      {/* Tabs: Overview / Exposure / Hardening */}
      <Tabs defaultValue="overview" className="space-y-5">
        <TabsList>
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="exposure">Exposure</TabsTrigger>
          <TabsTrigger value="hardening">Hardening</TabsTrigger>
        </TabsList>

        {/* ── Tab: Overview ── */}
        <TabsContent value="overview">
          <OverviewTab asset={asset} token={token!} />
        </TabsContent>

        {/* ── Tab: Exposure ── */}
        <TabsContent value="exposure">
          <ExposureTab assetId={asset.id} token={token!} />
        </TabsContent>

        {/* ── Tab: Hardening ── */}
        <TabsContent value="hardening">
          <HardeningTab assetId={asset.id} token={token!} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ─── ScanStatusBar ───────────────────────────────────────────────────────────

function ScanStatusBar({ scan }: { scan: ScanJob }) {
  const isRunning = scan.status === "running";
  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-lg border border-medium/30 bg-medium/5">
      <Activity
        className={cn(
          "h-4 w-4 text-medium",
          isRunning && "animate-pulse"
        )}
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary">
          {isRunning ? "Escaneo en curso" : "Escaneo pendiente"} —{" "}
          <span className="font-technical text-medium">{scan.scan_type}</span>
        </p>
        <p className="text-xs text-text-muted">
          Iniciado {fmtRelative(scan.created_at)}
        </p>
      </div>
      {/* Barra de progreso indeterminada */}
      {isRunning && (
        <div className="h-1 w-24 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full w-1/2 bg-medium rounded-full animate-[slide_1.5s_ease-in-out_infinite]" />
        </div>
      )}
    </div>
  );
}

// ─── Tab: Overview ───────────────────────────────────────────────────────────

function OverviewTab({ asset, token }: { asset: Asset; token: string }) {
  const [riskSummary, setRiskSummary] = useState<AssetRiskSummary | null>(null);
  const [score, setScore] = useState<AssetScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      cveApi.riskSummary(token, asset.id).catch(() => null),
      hardeningApi.getScore(token, asset.id).catch(() => null),
    ]).then(([risk, sc]) => {
      setRiskSummary(risk);
      setScore(sc);
      setLoading(false);
    });
  }, [asset.id, token]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Scores */}
      <div className="lg:col-span-1 space-y-4">
        {loading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            {score && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm text-text-secondary uppercase tracking-wider">
                    Hardening Score
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScoreDisplay
                    raw={score.raw_score}
                    weighted={score.weighted_score}
                    size="lg"
                    showBar
                    label="CIS Compliance"
                  />
                </CardContent>
              </Card>
            )}
            {riskSummary && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm text-text-secondary uppercase tracking-wider">
                    Exposición CVE
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {(["critical", "high", "medium", "low"] as const).map(
                    (sev) => (
                      <div key={sev} className="flex items-center justify-between">
                        <SeverityBadge severity={sev} />
                        <span className="font-technical text-sm font-medium text-text-primary">
                          {(riskSummary as Record<string, number>)[
                            `${sev}_count`
                          ] ?? 0}
                        </span>
                      </div>
                    )
                  )}
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>

      {/* Metadata del activo */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-sm text-text-secondary uppercase tracking-wider">
            Metadata
          </CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-4">
            <MetaField label="ID" value={asset.id} mono />
            <MetaField label="IP Address" value={asset.ip_address} mono />
            <MetaField label="Hostname" value={asset.hostname ?? "—"} mono />
            <MetaField label="Asset Type" value={asset.asset_type ?? "—"} />
            <MetaField label="OS Hint" value={asset.os_hint ?? "—"} mono />
            <MetaField label="Estado" value={asset.status} />
            <MetaField label="Creado" value={fmtDatetime(asset.created_at)} />
            <MetaField
              label="Actualizado"
              value={fmtDatetime(asset.updated_at)}
            />
          </dl>

          {asset.notes && (
            <div className="mt-4 pt-4 border-t border-border">
              <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
                Notas
              </p>
              <p className="text-sm text-text-secondary">{asset.notes}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ─── Tab: Exposure ───────────────────────────────────────────────────────────

function ExposureTab({
  assetId,
  token,
}: {
  assetId: string;
  token: string;
}) {
  const [services, setServices] = useState<DiscoveredService[]>([]);
  const [cves, setCves] = useState<CVECorrelation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLow, setShowLow] = useState(false);

  useEffect(() => {
    Promise.all([
      discoveryApi.listServices(token, assetId),
      cveApi.listCVEs(token, assetId),
    ])
      .then(([svcs, cvs]) => {
        setServices(svcs.items);
        setCves(cvs.items);
      })
      .finally(() => setLoading(false));
  }, [assetId, token]);

  const critical = cves.filter((c) => c.severity === "critical");
  const high = cves.filter((c) => c.severity === "high");
  const medium = cves.filter((c) => c.severity === "medium");
  const low = cves.filter((c) => c.severity === "low");
  const visibleCves = showLow
    ? cves
    : [...critical, ...high, ...medium];

  if (loading) return <SkeletonTable rows={6} cols={5} />;

  return (
    <div className="space-y-5">
      {/* Servicios descubiertos */}
      <div>
        <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-3">
          Servicios descubiertos ({services.length})
        </h3>
        {services.length === 0 ? (
          <EmptyState
            icon={Server}
            variant="compact"
            title="Sin servicios descubiertos"
            description="Inicia un escaneo de exposure para descubrir servicios expuestos."
          />
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>Puerto</Th>
                  <Th>Protocolo</Th>
                  <Th>Servicio</Th>
                  <Th>Banner / Versión</Th>
                  <Th>Descubierto</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {services.map((svc) => (
                  <tr key={svc.id} className="h-row hover:bg-surface/60 transition-colors">
                    <td className="px-4 font-technical text-sm text-text-primary">
                      {svc.port}
                    </td>
                    <td className="px-4 font-technical text-sm text-text-secondary uppercase">
                      {svc.protocol}
                    </td>
                    <td className="px-4 text-sm text-text-primary">
                      {svc.service_name ?? "—"}
                    </td>
                    <td className="px-4 font-technical text-xs text-text-muted truncate max-w-xs">
                      {svc.banner ?? svc.version ?? "—"}
                    </td>
                    <td className="px-4 text-sm text-text-secondary">
                      {fmtRelative(svc.discovered_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* CVEs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider">
            CVEs correlacionadas ({cves.length})
          </h3>
          {low.length > 0 && (
            <button
              onClick={() => setShowLow((v) => !v)}
              className="text-xs text-text-muted hover:text-text-secondary flex items-center gap-1 transition-colors"
            >
              {showLow ? (
                <>
                  <EyeOff className="h-3.5 w-3.5" /> Ocultar Low ({low.length})
                </>
              ) : (
                <>
                  <Eye className="h-3.5 w-3.5" /> Mostrar Low ({low.length})
                </>
              )}
            </button>
          )}
        </div>

        {cves.length === 0 ? (
          <EmptyState
            icon={ShieldCheck}
            variant="compact"
            title="Sin CVEs correlacionadas"
            description="Ejecuta una correlación de CVEs tras el escaneo de servicios."
          />
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <Th>CVE ID</Th>
                  <Th>Severidad</Th>
                  <Th>CVSS</Th>
                  <Th>Servicio</Th>
                  <Th>Confianza</Th>
                  <Th>Estado</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {visibleCves.map((cve) => (
                  <CVERow key={cve.id} cve={cve} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function CVERow({ cve }: { cve: CVECorrelation }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <tr
        className="h-row hover:bg-surface/60 transition-colors cursor-pointer"
        onClick={() => setExpanded((v) => !v)}
      >
        <td className="px-4 font-technical text-sm text-brand">{cve.cve_id}</td>
        <td className="px-4">
          <SeverityBadge severity={parseSeverity(cve.severity)} />
        </td>
        <td className="px-4 font-technical text-sm text-text-primary">
          {cve.cvss_score?.toFixed(1) ?? "—"}
        </td>
        <td className="px-4 font-technical text-xs text-text-muted">
          {cve.service_id ?? "—"}
        </td>
        <td className="px-4">
          <ConfidenceBadge confidence={cve.confidence} />
        </td>
        <td className="px-4 text-sm text-text-secondary capitalize">
          {cve.status}
        </td>
      </tr>
      {expanded && (
        <tr className="bg-surface/40">
          <td colSpan={6} className="px-4 py-3 text-sm text-text-secondary">
            {cve.description ?? (
              <span className="text-text-muted italic">Sin descripción disponible.</span>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

function ConfidenceBadge({ confidence }: { confidence: string }) {
  const map: Record<string, { icon: string; color: string; label: string }> = {
    high: { icon: "◉", color: "text-pass", label: "Verified (CPE)" },
    medium: { icon: "◎", color: "text-medium", label: "Unverified (version)" },
    low: { icon: "○", color: "text-text-muted", label: "Unconfirmed (service)" },
  };
  const cfg = map[confidence] ?? map.low;
  return (
    <span
      className={cn("text-xs font-technical", cfg.color)}
      title={cfg.label}
    >
      {cfg.icon} {confidence}
    </span>
  );
}

// ─── Tab: Hardening ──────────────────────────────────────────────────────────

function HardeningTab({
  assetId,
  token,
}: {
  assetId: string;
  token: string;
}) {
  const [score, setScore] = useState<AssetScoreResponse | null>(null);
  const [remediation, setRemediation] = useState<
    { id: string; title: string; severity: string; effort_minutes: number; status: string }[]
  >([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      hardeningApi.getScore(token, assetId).catch(() => null),
      hardeningApi.getRemediation(token, assetId).catch(() => ({ items: [] })),
    ])
      .then(([sc, rem]) => {
        setScore(sc);
        setRemediation(rem?.items ?? []);
      })
      .finally(() => setLoading(false));
  }, [assetId, token]);

  if (loading) return <SkeletonTable rows={5} cols={4} />;

  return (
    <div className="space-y-5">
      {/* Score */}
      {score && (
        <Card>
          <CardContent className="p-5">
            <ScoreDisplay
              raw={score.raw_score}
              weighted={score.weighted_score}
              size="xl"
              showBar
              label="CIS Compliance Score"
            />
          </CardContent>
        </Card>
      )}

      {/* Plan de remediación */}
      <div>
        <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-3">
          Plan de remediación
        </h3>
        {remediation.length === 0 ? (
          <EmptyState
            icon={ShieldCheck}
            variant="compact"
            title="Sin ítems de remediación"
            description="Completa una assessment CIS para generar el plan de remediación."
          />
        ) : (
          <div className="space-y-2">
            {remediation.map((item) => (
              <RemediationItem key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function RemediationItem({
  item,
}: {
  item: {
    id: string;
    title: string;
    severity: string;
    effort_minutes: number;
    status: string;
  };
}) {
  const isQuickWin = item.effort_minutes <= 30;
  return (
    <div
      className={cn(
        "flex items-center gap-4 px-4 py-3 rounded-lg bg-surface border border-border",
        isQuickWin && "border-l-4 border-l-brand"
      )}
    >
      <SeverityBadge severity={parseSeverity(item.severity)} />
      <span className="flex-1 text-sm text-text-primary">{item.title}</span>
      <span className="text-xs text-text-muted font-technical">
        {item.effort_minutes}min
      </span>
      {isQuickWin && (
        <span className="text-xs text-brand bg-brand/10 px-2 py-0.5 rounded">
          Quick win
        </span>
      )}
      <span
        className={cn(
          "text-xs capitalize",
          item.status === "resolved" ? "text-pass" : "text-text-muted"
        )}
      >
        {item.status}
      </span>
    </div>
  );
}

// ─── Helpers UI ──────────────────────────────────────────────────────────────

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
      {children}
    </th>
  );
}

function MetaField({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs text-text-muted uppercase tracking-wider mb-0.5">
        {label}
      </dt>
      <dd
        className={cn(
          "text-sm text-text-primary",
          mono && "font-technical"
        )}
      >
        {value}
      </dd>
    </div>
  );
}

function AssetStatusChip({ status }: { status: string }) {
  const map: Record<
    string,
    { label: string; color: string; bg: string }
  > = {
    authorized: { label: "Autorizado", color: "text-pass", bg: "bg-pass/10" },
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
  const cfg = map[status] ?? map.pending_review;
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
        cfg.bg,
        cfg.color
      )}
    >
      {cfg.label}
    </span>
  );
}

function AssetDetailSkeleton() {
  return (
    <div className="p-6 space-y-5">
      <Skeleton className="h-4 w-40" />
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <Skeleton className="h-7 w-56" />
          <Skeleton className="h-4 w-32" />
        </div>
        <Skeleton className="h-9 w-32" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <SkeletonCard />
        <div className="lg:col-span-2">
          <SkeletonCard />
        </div>
      </div>
    </div>
  );
}
