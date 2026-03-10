"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { aiApi } from "@/lib/api";
import { AIUsage } from "@/types/api";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Sparkles,
  Loader2,
  AlertTriangle,
  ShieldCheck,
  Info,
  Clock,
} from "lucide-react";

type Mode = "cve" | "check";

interface ExplainResult {
  query: string;
  explanation: string;
  mode: Mode;
  cached: boolean;
  timestamp: Date;
}

export default function AIAssistPage() {
  const { token } = useAuthStore();
  const [mode, setMode] = useState<Mode>("cve");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<ExplainResult[]>([]);
  const [usage, setUsage] = useState<AIUsage | null>(null);
  const [usageLoading, setUsageLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    aiApi
      .usage(token)
      .then(setUsage)
      .catch(() => setUsage(null))
      .finally(() => setUsageLoading(false));
  }, [token]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q || !token) return;

    setError(null);
    setLoading(true);
    try {
      let res;
      if (mode === "cve") {
        res = await aiApi.explainCVE(token, q);
      } else {
        res = await aiApi.explainCheck(token, q);
      }

      setHistory((prev) => [
        {
          query: q,
          explanation: res.explanation,
          mode,
          cached: res.cached ?? false,
          timestamp: new Date(),
        },
        ...prev,
      ]);
      setQuery("");

      // Actualizar uso
      aiApi.usage(token).then(setUsage).catch(() => {});
    } catch (err: unknown) {
      const e = err as { detail?: string; status?: number };
      if (e.status === 429) {
        setError(
          "Has alcanzado el límite de 5 consultas por hora. Inténtalo más tarde."
        );
      } else {
        setError(e?.detail ?? "Error al consultar la IA. Inténtalo de nuevo.");
      }
    } finally {
      setLoading(false);
    }
  }

  const remaining = usage ? Math.max(0, 5 - (usage.requests_this_hour ?? 0)) : null;

  return (
    <div className="p-6 space-y-6">
      <Breadcrumb items={[{ label: "AI Assist" }]} />

      {/* Cabecera */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-text-primary flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-brand" />
            AI Assist Lite
          </h1>
          <p className="text-sm text-text-secondary mt-0.5">
            Explicaciones defensivas de CVEs y controles CIS — solo lectura
          </p>
        </div>
        {/* Rate limit indicator */}
        <div className="flex items-center gap-2 text-sm text-text-secondary">
          <Clock className="h-4 w-4 text-text-muted" />
          {usageLoading ? (
            <Skeleton className="h-4 w-20" />
          ) : remaining !== null ? (
            <span>
              <span className={cn("font-semibold", remaining === 0 ? "text-critical" : "text-text-primary")}>
                {remaining}
              </span>
              <span className="text-text-muted"> / 5 consultas restantes esta hora</span>
            </span>
          ) : null}
        </div>
      </div>

      {/* Aviso defensivo */}
      <div className="flex items-start gap-3 bg-brand/5 border border-brand/20 rounded-lg px-4 py-3">
        <Info className="h-4 w-4 text-brand shrink-0 mt-0.5" />
        <p className="text-sm text-text-secondary">
          <span className="font-medium text-text-primary">Uso exclusivamente defensivo.</span>{" "}
          AI Assist explica vulnerabilidades y controles para ayudarte a remediarlos.
          No genera exploits, payloads ni instrucciones ofensivas.
          Las respuestas se cachean 24h por consulta idéntica.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Panel de consulta */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm text-text-secondary uppercase tracking-wider">
                Nueva consulta
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Selector de modo */}
                <div className="space-y-1.5">
                  <Label>Tipo de consulta</Label>
                  <div className="grid grid-cols-2 gap-2">
                    <ModeButton
                      active={mode === "cve"}
                      onClick={() => setMode("cve")}
                      icon={AlertTriangle}
                      label="CVE"
                      sublabel="Explica una vulnerabilidad"
                    />
                    <ModeButton
                      active={mode === "check"}
                      onClick={() => setMode("check")}
                      icon={ShieldCheck}
                      label="Check CIS"
                      sublabel="Explica un control"
                    />
                  </div>
                </div>

                {/* Input */}
                <div className="space-y-1.5">
                  <Label htmlFor="query">
                    {mode === "cve" ? "CVE ID" : "Check ID"}
                  </Label>
                  <Input
                    id="query"
                    placeholder={
                      mode === "cve" ? "CVE-2024-12345" : "CIS-RHEL8-1.1.1"
                    }
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="font-technical"
                    disabled={loading || remaining === 0}
                  />
                </div>

                {/* Error */}
                {error && (
                  <p className="text-sm text-critical bg-critical/10 rounded px-3 py-2">
                    {error}
                  </p>
                )}

                <Button
                  type="submit"
                  className="w-full"
                  disabled={loading || !query.trim() || remaining === 0}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Consultando IA…
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Explicar
                    </>
                  )}
                </Button>

                {remaining === 0 && (
                  <p className="text-xs text-text-muted text-center">
                    Límite alcanzado. Se reinicia cada hora.
                  </p>
                )}
              </form>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card>
            <CardContent className="p-4">
              <p className="text-xs font-medium text-text-secondary uppercase tracking-wider mb-3">
                Ejemplos de consulta
              </p>
              <div className="space-y-2">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex.query}
                    onClick={() => { setMode(ex.mode); setQuery(ex.query); }}
                    className="w-full text-left px-3 py-2 rounded bg-surface hover:bg-raised transition-colors"
                  >
                    <span className="block text-xs font-technical text-brand">{ex.query}</span>
                    <span className="block text-xs text-text-muted mt-0.5">{ex.desc}</span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Historial de respuestas */}
        <div className="lg:col-span-2 space-y-4">
          {history.length === 0 && !loading ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="h-14 w-14 rounded-xl bg-brand/10 flex items-center justify-center mb-4">
                <Sparkles className="h-7 w-7 text-brand" />
              </div>
              <p className="text-sm font-medium text-text-primary">Listo para consultar</p>
              <p className="text-sm text-text-secondary mt-1 max-w-sm">
                Introduce un CVE ID o Check CIS para obtener una explicación defensiva.
              </p>
            </div>
          ) : (
            <>
              {loading && (
                <Card className="border-brand/30 bg-brand/5">
                  <CardContent className="p-4 flex items-center gap-3">
                    <Loader2 className="h-5 w-5 text-brand animate-spin shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-text-primary">
                        Consultando AI Assist…
                      </p>
                      <p className="text-xs text-text-muted font-technical">{query}</p>
                    </div>
                  </CardContent>
                </Card>
              )}
              {history.map((item, i) => (
                <ExplainCard key={i} item={item} />
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Sub-componentes ─────────────────────────────────────────────────────────

function ExplainCard({ item }: { item: ExplainResult }) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {item.mode === "cve" ? (
              <AlertTriangle className="h-4 w-4 text-high shrink-0" />
            ) : (
              <ShieldCheck className="h-4 w-4 text-brand shrink-0" />
            )}
            <span className="text-sm font-technical font-semibold text-text-primary">
              {item.query}
            </span>
            {item.cached && (
              <span className="text-xs text-text-muted bg-white/5 px-1.5 py-0.5 rounded">
                cached
              </span>
            )}
          </div>
          <span className="text-xs text-text-muted shrink-0 ml-4">
            {item.timestamp.toLocaleTimeString("es-ES", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>
        <div className="prose-sm prose-invert max-w-none">
          <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
            {item.explanation}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function ModeButton({
  active,
  onClick,
  icon: Icon,
  label,
  sublabel,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ElementType;
  label: string;
  sublabel: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex flex-col items-start gap-1 px-3 py-2.5 rounded-lg border text-left transition-colors",
        active
          ? "border-brand bg-brand/10 text-text-primary"
          : "border-border bg-surface text-text-secondary hover:bg-raised"
      )}
    >
      <div className="flex items-center gap-1.5">
        <Icon className={cn("h-3.5 w-3.5", active ? "text-brand" : "text-text-muted")} />
        <span className="text-xs font-semibold">{label}</span>
      </div>
      <span className="text-xs text-text-muted leading-snug">{sublabel}</span>
    </button>
  );
}

// ─── Datos estáticos ─────────────────────────────────────────────────────────

const EXAMPLES: { query: string; mode: Mode; desc: string }[] = [
  {
    query: "CVE-2021-44228",
    mode: "cve",
    desc: "Log4Shell — RCE crítico en Log4j",
  },
  {
    query: "CVE-2023-44487",
    mode: "cve",
    desc: "HTTP/2 Rapid Reset — DoS masivo",
  },
  {
    query: "CIS-RHEL8-1.1.1",
    mode: "check",
    desc: "Partición /tmp separada",
  },
  {
    query: "CIS-DEBIAN-5.2.4",
    mode: "check",
    desc: "Configuración de SSH",
  },
];
