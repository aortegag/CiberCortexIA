# CiberCortex IA — UX Design System

**Version:** 1.0.0
**Date:** 2026-03-10
**Role:** Principal UX / Product Designer reference document
**Scope:** MVP complete — 10 pantallas, componentes, sistema de diseño, reglas y riesgos

---

## Filosofía de Diseño

Antes de cualquier componente o pantalla, cuatro decisiones irrevocables que guían cada elección visual:

> **1. Claridad antes que exhaustividad.** Mostrar lo que el usuario necesita para tomar una decisión, no todo lo que el sistema sabe.
>
> **2. Estructura sobre decoración.** La UI organiza datos, no los decora. Cada elemento visual gana su espacio.
>
> **3. Estado siempre visible.** El usuario nunca se pregunta "¿qué está pasando?". Cada entidad muestra su estado de forma inequívoca.
>
> **4. El analista trabaja, el CISO decide.** La misma plataforma, dos niveles de abstracción distintos activados por el rol.

---

## 1. Sitemap Completo

```
/login
│
├── /exposure
│   │
│   ├── /assets                         ← Asset Inventory [Analyst, Admin, CISO*]
│   │   ├── /new                        ← Register Asset [Analyst, Admin]
│   │   └── /:id                        ← Asset Detail
│   │       ├── /overview               ← Asset Overview [todos los roles]
│   │       ├── /services               ← Discovery Results [Analyst, Admin]
│   │       ├── /cves                   ← Exposure Findings [Analyst, Admin]
│   │       └── /reports                ← Asset Reports [Analyst, Admin]
│   │
│   └── /surface                        ← Attack Surface [V2]
│
├── /hardening
│   │
│   ├── /assessments                    ← Assessment List [Analyst, Admin]
│   │   ├── /new                        ← New Assessment [Analyst, Admin]
│   │   └── /:id
│   │       ├── /checks                 ← Hardening Assessment [Analyst, Admin]
│   │       ├── /score                  ← Score Detail [Analyst, Admin]
│   │       └── /remediation            ← Remediation Items [Analyst, Admin]
│   │
│   ├── /scores                         ← Scores Overview [Analyst, Admin]
│   │
│   └── /remediation                    ← Global Remediation Queue [Analyst, Admin]
│
├── /reports                            ← Report Center [Analyst, Admin, CISO]
│   ├── /new                            ← Generate Report
│   └── /history                        ← Report History
│
└── /settings                           ← Settings [Admin only]
    ├── /users                          ← User Management
    ├── /audit-log                      ← Audit Log
    └── /system                         ← System Config

* CISO ve /assets con datos abstractos: nombres, estados, scores. Sin IPs ni versiones.
```

---

## 2. Sistema de Diseño Enterprise — Design Tokens

### Paleta de colores (Dark Mode nativo)

```
── BACKGROUNDS ─────────────────────────────────────────────
bg-canvas:   #080C15    ← Fondo más profundo (página base)
bg-surface:  #0F1623    ← Sidebar, cards, contenedores
bg-raised:   #1A2233    ← Hover de filas, inputs, bloques
bg-elevated: #202C42    ← Modales, dropdowns, tooltips

── BORDERS ──────────────────────────────────────────────────
border-faint:   #1A2438   ← Separadores sutiles
border-default: #273452   ← Cards, inputs en estado normal
border-strong:  #3D5580   ← Foco, estados activos

── TEXT ─────────────────────────────────────────────────────
text-primary:   #E8EEF9   ← Títulos, datos principales
text-secondary: #8A9BBF   ← Labels, metadatos, placeholders activos
text-tertiary:  #4D5F80   ← Placeholders vacíos, disabled
text-on-color:  #080C15   ← Texto sobre fondos coloreados

── SEMÁNTICOS (SEVERIDAD — inmutables en toda la app) ───────
critical-fg: #FF4545   critical-bg: #FF454512   critical-border: #FF454530
high-fg:     #FF8C00   high-bg:     #FF8C0012   high-border:     #FF8C0030
medium-fg:   #F0B429   medium-bg:   #F0B42912   medium-border:   #F0B42930
low-fg:      #4B8BFF   low-bg:      #4B8BFF12   low-border:      #4B8BFF30
pass-fg:     #22C55E   pass-bg:     #22C55E12   pass-border:     #22C55E30
info-fg:     #5B6B8A   info-bg:     #5B6B8A10   info-border:     #5B6B8A20

── CONFIANZA DE EVIDENCIA ───────────────────────────────────
conf-high:   #22C55E   ← Verificado (CPE match)
conf-med:    #F0B429   ← No verificado (version string)
conf-low:    #5B6B8A   ← Sin confirmar (service name only)

── MARCA ────────────────────────────────────────────────────
brand:       #3B7EFF   ← Azul principal de acciones
brand-hover: #2D6FEE
brand-muted: #3B7EFF20
```

### Tipografía

```
── FUENTES ──────────────────────────────────────────────────
sans:  'Inter', 'Geist', system-ui, sans-serif
mono:  'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace

── ESCALA ───────────────────────────────────────────────────
display:    24px / 700 / sans / text-primary    ← Títulos de página
heading:    18px / 600 / sans / text-primary    ← Títulos de sección
subheading: 14px / 600 / sans / text-secondary  ← Labels de sección (uppercase, tracking-wide)
body:       14px / 400 / sans / text-primary    ← Contenido general
small:      12px / 400 / sans / text-secondary  ← Metadatos, timestamps
caption:    11px / 400 / sans / text-tertiary   ← Labels de inputs, hints
data:       13px / 400 / mono / text-primary    ← IPs, CVE IDs, puertos, hashes, versiones
data-small: 12px / 400 / mono / text-secondary  ← Datos técnicos secundarios

── REGLA CRÍTICA ────────────────────────────────────────────
Todo dato técnico (IP, hostname, CVE ID, puerto, versión, hash, banner)
usa fuente 'mono'. No hay excepciones.
```

### Espaciado (Base = 4px)

```
xs:  4px   ← Gap entre icon + label
sm:  8px   ← Padding de badge, gap entre meta items
md:  12px  ← Padding de inputs, gap de form fields
lg:  16px  ← Padding de celdas de tabla
xl:  20px  ← Padding de cards
2xl: 24px  ← Page padding horizontal
3xl: 32px  ← Section gap
4xl: 48px  ← Between major sections
```

### Elevación (sin sombras — usa border + bg shift)

```
Nivel 0 — bg-canvas:   página, fondo
Nivel 1 — bg-surface:  sidebar, main content background
Nivel 2 — bg-raised:   cards, table row hover, input focus
Nivel 3 — bg-elevated: modales, dropdowns, popovers
Nivel 4 — border-strong: sólo para outline de estados activos/focus
```

### Iconografía

```
Biblioteca:   Lucide React (consistencia, tree-shakeable, outline style)
Tamaño base:  16px (inline), 20px (standalone acciones)
Color:        Hereda text-secondary por defecto; text-primary en hover
Severidad:    Usar los caracteres textuales para badges, NO iconos de Lucide
              para que sean legibles en export a PDF
```

---

## 3. Layout Global — Authenticated Shell

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░ bg-canvas ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ┌─────────────┐ ┌──────────────────────────────────────────────────────┐ │
│ │             │ │                  MAIN CONTENT                        │ │
│ │   SIDEBAR   │ │  bg-canvas · overflow-y-auto · padding: 24px         │ │
│ │   bg-surface│ │                                                       │ │
│ │   220px     │ │  [Breadcrumb]                                         │ │
│ │   fixed     │ │  EXPOSURE  ›  Assets  ›  web-prod-01                 │ │
│ │             │ │                                                       │ │
│ │             │ │  [Page Header]                                        │ │
│ │             │ │  ┌─────────────────────────────────────────────────┐ │ │
│ │             │ │  │  web-prod-01                     [+ Action]     │ │ │
│ │             │ │  │  192.168.1.10  ·  Linux Server  · Production    │ │ │
│ │             │ │  │  ● Authorized                                   │ │ │
│ │             │ │  └─────────────────────────────────────────────────┘ │ │
│ │             │ │                                                       │ │
│ │             │ │  [Content]                                            │ │
│ │             │ │                                                       │ │
│ │             │ │                                                       │ │
│ └─────────────┘ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### Sidebar — Estructura detallada

```
┌─────────────────────┐
│  ◈ CiberCortex IA   │  ← Logo + nombre, 20px, color brand
│  ─────────────────  │  ← border-faint
│                     │
│  EXPOSURE           │  ← 11px uppercase tracking-widest text-tertiary
│                     │     NON-CLICKABLE section label
│  ◱ Assets           │  ← Nav item activo: bg-raised + border-l-2 brand
│  ◳ Reports          │  ← Nav item inactivo: hover bg-raised
│                     │
│  HARDENING          │  ← Section label
│                     │
│  ✓ Assessments      │
│  ◈ Scores           │
│  ⊞ Remediation      │
│                     │
│  PLATFORM           │  ← Section label
│                     │
│  ⊟ All Reports      │
│                     │
│  ─────────────────  │
│  ⚙ Settings         │  ← Solo Admin. Si no es Admin: visible pero
│                     │     disabled con tooltip "Requires Admin role"
│  ─────────────────  │
│  ● J.García         │  ← Avatar inicial + nombre + role badge
│    Analyst          │
└─────────────────────┘

Reglas del sidebar:
- Ancho fijo: 220px. No colapsable en MVP.
- Active state: bg-raised + border-l-2 solid brand + text-primary
- Hover state: bg-raised + text-primary (transición 100ms)
- Section labels: nunca clicables, visualmente separados
- Settings: siempre visible, bloqueado con tooltip si no es Admin
- User area: al fondo, sempre visible, click → logout menu
```

---

## 4. Navegación y Jerarquía Visual por Rol

### Analyst — Acceso pleno a datos técnicos

```
SideNav:    Todos los items visibles y activos
PageHeader: Título técnico (hostname/IP), actions (scan, assess, report)
Tables:     Columnas técnicas completas (IP, version, CVE ID, CVSS vector)
Badges:     SeverityBadge + ConfidenceBadge visibles
Actions:    Scan trigger, Assessment create, Evidence input, AI Explain
Data:       Fuente monospace para todos los datos técnicos
```

### CISO — Vista abstracta, drill-down controlado

```
SideNav:    Mismo sidebar, pero /hardening/assessments/:id/checks → blocked
PageHeader: Nombre del activo (sin IP), score prominente
Tables:     Columnas abstraídas: Name | Environment | Risk Level | Status
            SIN columnas: IP, Version, CVE ID, Port, Banner
Badges:     RiskBadge (Critical Risk / High Risk / Low Risk) en lugar de SeverityBadge
Scores:     Prominentes, numéricos, con tendencia
Drill-down: Click en "3 activos críticos" → lista de nombres, no IPs
            Click en activo → descripción de riesgo en lenguaje de negocio
            Sin acceso a /services, /cves (raw), /checks
Actions:    Solo: Generate Executive Report, View Posture Summary
Data:       Sin fuente mono. Todo en sans-serif. Sin raw data.
```

### Principio de implementación para roles

La misma ruta `/exposure/assets` existe para ambos roles. El backend devuelve:
- Para Analyst/Admin: campo `ip`, `hostname`, `service_version`, `cve_id` incluidos
- Para CISO: campos `ip`, `hostname`, `service_version`, `cve_id`, `banner` omitidos en la respuesta

El frontend renderiza el componente correcto según `user.role` recibido en el JWT.
No hay rutas distintas para CISO — hay respuestas distintas y componentes distintos.

---

## 5. Componentes Reutilizables

### 5.1 SeverityBadge

```
Uso: CVEs, check severity, remediation priority
Estructura: [icon  label]  → pill, border-radius 4px, padding 4px 8px

Variantes:
  ⬤ CRITICAL  bg: critical-bg, text: critical-fg, border: critical-border
  ▲ HIGH      bg: high-bg,     text: high-fg,     border: high-border
  ◆ MEDIUM    bg: medium-bg,   text: medium-fg,   border: medium-border
  ▼ LOW       bg: low-bg,      text: low-fg,      border: low-border
  ✓ PASS      bg: pass-bg,     text: pass-fg,     border: pass-border
  ℹ INFO      bg: info-bg,     text: info-fg,     border: info-border

Tamaño: 11px / 500 / sans / uppercase
Regla: Una sola paleta de severidad en TODA la app. No hay variantes de color para
       el mismo concepto en pantallas distintas.
```

### 5.2 ConfidenceBadge

```
Uso: CVECorrelation.confidence — siempre visible junto al CVE ID
Estructura: [◉ Verified] → más pequeño que SeverityBadge, más sutil

Variantes:
  ◉ Verified      text: conf-high,   12px, mono font hint
  ◎ Unverified    text: conf-med,    12px
  ○ Unconfirmed   text: conf-low,    12px

Regla: ConfidenceBadge LOW nunca aparece en la misma línea que datos técnicos sin
       un tooltip que explique "Version not confirmed. Manual verification recommended."
```

### 5.3 StatusBadge

```
Uso: Asset status, ScanJob status, Assessment status, RemediationItem status
Estructura: [● Estado] → dot + text, sin border, más ligero que SeverityBadge

Assets:
  ● Authorized      dot: pass-fg
  ◌ Pending Auth    dot: medium-fg (parpadeo lento 2s)
  — Decommissioned  dot: text-tertiary
  ⊘ Suspended       dot: critical-fg

Scans:
  ● Queued          dot: text-tertiary (estático)
  ⟳ Running         dot: brand (spin animation 1s)  + "Started X min ago"
  ✓ Completed       dot: pass-fg
  ✗ Failed          dot: critical-fg  + "Retry" link
  ⊘ Cancelled       dot: text-tertiary

Assessments:
  ✎ Draft           dot: medium-fg
  ⟳ In Progress     dot: brand
  ✓ Completed       dot: pass-fg
  ◻ Archived        dot: text-tertiary

Remediation items:
  ● Open            dot: critical-fg o high-fg (según priority)
  ⟳ In Progress     dot: brand
  ✓ Resolved        dot: pass-fg
  ⊘ Accepted Risk   dot: text-tertiary
  ✕ Won't Fix       dot: text-tertiary
```

### 5.4 ScoreDisplay

```
Uso: Hardening score, posture score
Estructuras disponibles:

  [LARGE] — Pantalla de score principal
  ┌──────────┐
  │    74    │  ← 48px / 700 / sans
  │  /100    │  ← 14px / text-secondary
  └──────────┘
  Color del número según valor:
    < 50:  critical-fg
    50-74: high-fg
    75-89: medium-fg (naranja-amarillo — "bueno pero mejorable")
    ≥ 90:  pass-fg

  [INLINE] — En tablas y listas
  74/100  ← con color del número según valor, mono font

  [DELTA] — En re-evaluaciones
  ↑ +19   ← pass-fg si positivo; critical-fg si negativo
  74 → 93 ← inline comparación

  [WEIGHTED] — Siempre mostrar los dos: raw y ponderado
  74.0% raw  ·  68.4% weighted  ← en layout de score detail
```

### 5.5 DataTable

```
Estructura base:
┌─────────────────────────────────────────────────────────────┐
│ [🔍 Search...]  [Filter ▾]  [Severity ▾]  ...  [Export ↓]  │  ← FilterBar
├──────────┬───────────────┬───────────┬───────────┬──────────┤
│ NAME ↕   │ IP/HOSTNAME ↕ │ TYPE      │ STATUS    │ ACTIONS  │  ← Header
├──────────┼───────────────┼───────────┼───────────┼──────────┤
│ web-p-01 │ 192.168.1.10  │ Server    │ ● Auth    │ [···]    │  ← Row
│ db-main  │ 10.0.0.5      │ Server    │ ◌ Pending │ [···]    │
├──────────┴───────────────┴───────────┴───────────┴──────────┤
│ Showing 1–25 of 43                    [< 1 2 >] [25 ▾]      │  ← Pagination
└─────────────────────────────────────────────────────────────┘

Reglas de tabla:
- Header: 11px uppercase tracking-widest text-tertiary. Click para sort.
- Row height: 44px (no compactar — enterprise necesita respirar)
- Hover row: bg-raised transition 80ms
- Selected row: bg-raised + border-l-2 brand (si hay selección múltiple)
- Sort indicator: ↕ (sin sort), ↑ (asc), ↓ (desc) — siempre visible en header
- La columna de acciones [···] nunca tiene label, sólo el icono
- Zebra striping: NO. Usar hover para feedback visual.
- Columnas técnicas (IP, CVE ID, versión): fuente mono
- Columnas semánticas (nombre, tipo, estado): fuente sans
- Paginación: server-side para > 100 filas; client-side ≤ 100
```

### 5.6 ScanStatusBar

```
Uso: Fijo en el Asset Detail header cuando hay un scan activo
Aparece entre el PageHeader y las tabs del asset

MIENTRAS CORRE:
┌─────────────────────────────────────────────────────────────┐
│ ⟳ Discovery scan running  ·  Started 2 min ago  [Cancel]   │
│ ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Progress          │
└─────────────────────────────────────────────────────────────┘
bg: brand-muted, border: border-default, text: text-secondary

AL COMPLETAR (visible 5 segundos, luego desaparece):
┌─────────────────────────────────────────────────────────────┐
│ ✓ Scan completed  ·  12 services found  ·  Just now         │
└─────────────────────────────────────────────────────────────┘
bg: pass-bg, border: pass-border, text: pass-fg

EN ERROR:
┌─────────────────────────────────────────────────────────────┐
│ ✗ Scan failed: Connection timeout (192.168.1.10:443)  [Retry]│
└─────────────────────────────────────────────────────────────┘
bg: critical-bg, border: critical-border, text: critical-fg

Regla: Polling cada 3s. No bloquear la UI. El usuario puede navegar
       mientras el scan corre. El StatusBar sigue visible en todas
       las sub-vistas del mismo asset.
```

### 5.7 EvidenceInput

```
Uso: CheckResult — campos evidence_type + evidence_text + evidence_at
Regla: NO es un campo opcional. Aparece prominente, no colapsado.

┌──────────────────────────────────────────────────────────────┐
│ Evidence                                    REQUIRED for Pass/Fail │
│ ┌─────────────────┐                                          │
│ │ Type ▾          │  ← dropdown: Command Output / Config     │
│ │ Command Output  │    Excerpt / File Content / Manual Note  │
│ └─────────────────┘                                          │
│ ┌────────────────────────────────────────────────────────────┐│
│ │ Paste command output or write your observation...          │ │
│ │                                                            │ │
│ │                                                            │ │
│ └────────────────────────────────────────────────────────────┘│
│ Collected at: [Mar 10, 2026  14:23]  (auto-filled on paste)  │
└──────────────────────────────────────────────────────────────┘

Estados:
- Empty (antes de marcar Pass/Fail): bg-raised, border-default
- Required (marcado Pass/Fail sin evidencia): border-critical-border + mensaje
- Filled: border-pass-border sutil
- Read-only (assessment completado): bg-canvas, texto en mono, no editable

Regla UX: El timestamp `evidence_at` se rellena automáticamente cuando el
usuario pega o empieza a escribir. No pedirle que lo introduzca manualmente.
```

### 5.8 AIExplainPanel

```
Uso: CVE detail, CheckResult detail — botón "Explain" que expande panel
Regla: Read-only. Sin acciones. Sin formularios.

Estado inicial (cerrado):
  [ ✦ Explain with AI ]  ← botón secundario, outline

Estado cargando (tras click):
  ┌──────────────────────────────────────────────────────────┐
  │ ✦ AI Explanation                                   [✕]   │
  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (skeleton 3 lines) │
  └──────────────────────────────────────────────────────────┘

Estado con contenido:
  ┌──────────────────────────────────────────────────────────┐
  │ ✦ AI Explanation  ·  claude-haiku-4-5  ·  Cached  [✕]   │
  │ ─────────────────────────────────────────────────────── │
  │ What this means:                                         │
  │ CVE-2023-38408 affects OpenSSH's ssh-agent forwarding... │
  │                                                          │
  │ Why it matters for production servers:                   │
  │ An attacker with access to the network path could...     │
  │                                                          │
  │ Suggested remediation:                                   │
  │ 1. Update OpenSSH to version ≥ 9.3p2                     │
  │ 2. Disable ssh-agent forwarding if not required          │
  │ 3. Verify: ssh -V                                        │
  │ ─────────────────────────────────────────────────────── │
  │ ⚠ AI explanations are advisory. Verify before applying.  │
  └──────────────────────────────────────────────────────────┘

Reglas:
- El panel siempre muestra "claude-haiku-4-5" o el modelo usado (transparencia)
- "Cached" badge si viene de caché. Permite saber que es determinista.
- El footer de disclaimer es obligatorio y no ocultable
- Sin markdown avanzado en el output — sólo párrafos y listas numeradas
- Nunca botones de acción dentro del panel
```

### 5.9 ConfirmationModal

```
Uso: Scans, borrados, autorizaciones — cualquier acción no reversible

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Run Discovery Scan                                         │
│  ─────────────────────────────────────────────────────────  │
│  This will execute a TCP SYN scan (Nmap) against:           │
│                                                             │
│  Target:   192.168.1.10  (web-prod-01)                      │
│  Type:     TCP Discovery (ports 1–1024 + common)            │
│  Initiated by: j.garcia@example.com                         │
│                                                             │
│  This action will be logged to the Audit Trail.             │
│                                                             │
│  [Cancel]                    [Run Scan →]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Reglas:
- Siempre muestra: qué va a pasar, sobre qué target, quién lo inicia
- "Logged to Audit Trail" siempre visible — no opcional
- Botón de confirmación: primario, alineado a la derecha
- Botón de cancelar: ghost, alineado a la izquierda
- No usar "Are you sure?" — describir la acción concretamente
- Para borrado: el modal lleva el nombre del item a borrar explícitamente
```

### 5.10 EmptyState

```
Uso: Tablas vacías, primeros accesos, resultados sin datos

Estructura:
  ┌──────────────────────────────────────────┐
  │                                          │
  │          [icono Lucide, 40px]            │
  │                                          │
  │          No assets registered            │  ← 16px / 500 / text-primary
  │                                          │
  │    Register your first authorized asset  │  ← 14px / text-secondary
  │    to begin exposure analysis.           │
  │                                          │
  │          [+ Register Asset]              │  ← botón primario
  │                                          │
  └──────────────────────────────────────────┘

Variantes por pantalla:
  Assets vacíos:     "No assets registered" + CTA "Register Asset"
  CVEs vacíos:       "No CVEs found for detected services. Run a scan first."
  Sin scan:          "No scan data yet" + CTA "Run Discovery Scan"
  Assessments vacíos: "No assessments yet" + CTA "Start Assessment"
  Audit log vacío:   "No actions recorded yet" — sin CTA (es sólo informativo)
  Reports vacíos:    "No reports generated" + CTA "Generate Report"

Regla: Nunca mostrar una tabla vacía sin contexto. Siempre un EmptyState
       con icono relevante, texto descriptivo y CTA si aplica.
       El CTA respeta permisos: si el usuario no puede hacer la acción,
       el CTA no aparece.
```

### 5.11 PageHeader

```
Estructura:
┌─────────────────────────────────────────────────────────────┐
│  [Título principal]                    [Action 2] [Action 1]│
│  [Subtítulo: metadatos clave]                               │
│  [StatusBadge]  ·  [metadato 2]  ·  [metadato 3]           │
└─────────────────────────────────────────────────────────────┘

Reglas:
- Título: 24px / 700
- Subtítulo (si hay): 14px / text-secondary
- Metadatos en una línea, separados por ·
- Acciones: máximo 2 en el header. Si hay más, ir a menú [···]
- Action 1 (primaria): botón primario brand
- Action 2 (secundaria): botón outline

Ejemplos:
  Página Assets:     "Assets (43)"  +  [+ New Asset]
  Página Asset/id:   "web-prod-01"  +  [Run Scan] [···]
                     192.168.1.10 · Linux Server · Production · ● Authorized
  Página Assessment: "CIS Linux L1 — web-prod-01"  +  [Complete Assessment]
                     In Progress · Started Mar 10, 2026 · 7/10 checks done
```

### 5.12 InlineAlert

```
Uso: Mensajes contextuales de error, warning, info — dentro de la página
Regla: NO usar toast/snackbar para errores que bloquean una acción.
       Usar InlineAlert dentro del contexto donde ocurre el error.

Variantes:
  [ℹ] Info:    bg-info-bg,     border-l-4 info-fg
  [⚠] Warning: bg-medium-bg,  border-l-4 medium-fg
  [✗] Error:   bg-critical-bg, border-l-4 critical-fg

Ejemplo de error de evidencia:
  ┌──────────────────────────────────────────────────────────┐
  │ ✗  Cannot complete assessment                            │
  │    3 checks marked as Pass/Fail require evidence:        │
  │    · 1.1.1 — Ensure /tmp is a separate partition         │
  │    · 1.4.2 — Ensure permissions on bootloader...         │
  │    · 3.3.2 — Ensure IPv6 is not accepted                 │
  └──────────────────────────────────────────────────────────┘

Toast (snackbar): SOLO para confirmaciones de acciones exitosas no críticas.
  Ejemplo: "Scan started for web-prod-01" — aparece 3s, esquina inferior derecha.
  No para errores. No para acciones críticas.
```

---

## 6. Wireframes por Pantalla

---

### SCREEN 01 — Login

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: todos — pre-autenticación]                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  bg-canvas — pantalla completa, sin sidebar                  ║
║                                                              ║
║          ┌──────────────────────────────────┐               ║
║          │                                  │               ║
║          │  ◈  CiberCortex IA               │  ← 20px brand ║
║          │                                  │               ║
║          │  ──────────────────────────────  │               ║
║          │                                  │               ║
║          │  Email address                   │               ║
║          │  ┌──────────────────────────┐    │               ║
║          │  │ user@organization.com    │    │               ║
║          │  └──────────────────────────┘    │               ║
║          │                                  │               ║
║          │  Password                        │               ║
║          │  ┌──────────────────────────┐    │               ║
║          │  │ ••••••••••••••••      👁 │    │               ║
║          │  └──────────────────────────┘    │               ║
║          │                                  │               ║
║          │  [  Sign In  ───────────────]    │  ← full width ║
║          │                                  │               ║
║          │  ──────────────────────────────  │               ║
║          │  Version 1.0.0-mvp               │  ← 11px gray  ║
║          └──────────────────────────────────┘               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

ESTADOS:
- Loading: botón "Sign In" → spinner + "Signing in..." — deshabilitado
- Error:   InlineAlert ✗ bajo el formulario: "Invalid credentials"
- Success: redirect a /exposure/assets

REGLAS:
- Card centered: max-width 360px, bg-surface, border-default, padding 32px
- Sin imagen de fondo, sin gradientes, sin partículas
- Sin "Forgot password" en MVP — se configura en Settings
- Sin "Sign up" — acceso sólo por Admin invitation
```

---

### SCREEN 02 — Asset Inventory

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Analyst, Admin, CISO (vista abstracta)]               ║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Exposure  ›  Assets                          │║
║ │          │ │                                              │║
║ │ EXPOSURE │ │ Assets (43)                    [+ New Asset] │║
║ │ ◱ Assets │ │ 38 authorized · 4 pending · 1 suspended      │║
║ │ ◳ Reports│ │                                              │║
║ │          │ │ ┌──────────────────────────────────────────┐ │║
║ │ HARDENING│ │ │🔍 Search assets...  [Status ▾] [Type ▾]  │ │║
║ │ ✓ Assess │ │ │                          [Environment ▾] │ │║
║ │ ◈ Scores │ │ └──────────────────────────────────────────┘ │║
║ │ ⊞ Remed. │ │                                              │║
║ │          │ │ NAME↕    IP/HOST↕   TYPE   ENV     STATUS    │║
║ │ PLATFORM │ │ ─────────────────────────────────────────    │║
║ │ ⊟ Reports│ │ web-p-01 192.168.. Server  Prod  ● Auth      │║
║ │          │ │ db-main  10.0.0.5  Server  Prod  ● Auth      │║
║ │─────────│ │ smtp-01  10.0.1.3  Server  Prod  ● Auth      │║
║ │⚙ Settings│ │ fw-edge  172.16.0. Device  Prod  ◌ Pending   │║
║ │          │ │ dev-box  10.0.2.15 Workst. Dev   ● Auth      │║
║ │● J.García│ │                                              │║
║ │  Analyst │ │ Showing 1–25 of 43         [< 1 2 >] [25 ▾]  │║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

COLUMNAS COMPLETAS (Analyst/Admin):
  NAME · IP/HOSTNAME · TYPE · OS · ENVIRONMENT · STATUS · LAST SCAN · CVE COUNT

COLUMNAS CISO:
  NAME · TYPE · ENVIRONMENT · RISK LEVEL · REMEDIATION STATUS
  (Sin IP, sin OS, sin CVE count numérico — sólo "3 Critical Issues")

ACCIONES POR FILA (menú [···]):
  - View Detail (siempre)
  - Run Scan (si Authorized + Analyst/Admin)
  - Edit (Analyst/Admin)
  - Authorize (Admin only, si Pending)
  - Decommission (Admin only)

EMPTY STATE:
  [icono Shield] "No assets registered"
  "Register your first authorized asset to begin exposure analysis."
  [+ Register Asset]

ADMIN DIFERENCIA: columna adicional "Owner" y badge de pending auth con CTA
```

---

### SCREEN 03 — Asset Detail: Overview

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Analyst, Admin — vista técnica completa]              ║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Exposure  ›  Assets  ›  web-prod-01          │║
║ │          │ │                                              │║
║ │          │ │ web-prod-01              [Run Scan] [···]    │║
║ │          │ │ 192.168.1.10  ·  Linux Server  ·  Production │║
║ │          │ │ ● Authorized  ·  owner: infra-team           │║
║ │          │ │ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (ScanStatusBar)    │║
║ │          │ │                                              │║
║ │          │ │ [Overview] [Services] [CVEs] [Reports]       │║
║ │          │ │ ─────────                                    │║
║ │          │ │                                              │║
║ │          │ │ ┌──────────────┐  ┌──────────────┐          │║
║ │          │ │ │ Last Scan    │  │ Hardening    │          │║
║ │          │ │ │ Mar 9, 14:32 │  │ Score        │          │║
║ │          │ │ │ ✓ Completed  │  │   74/100     │          │║
║ │          │ │ │ 12 services  │  │              │          │║
║ │          │ │ └──────────────┘  └──────────────┘          │║
║ │          │ │                                              │║
║ │          │ │ ┌──────────────┐  ┌──────────────┐          │║
║ │          │ │ │ CVEs         │  │ Remediation  │          │║
║ │          │ │ │ 2 ⬤ CRIT    │  │ 3 Open       │          │║
║ │          │ │ │ 4 ▲ HIGH     │  │ 1 In Progress│          │║
║ │          │ │ │ 7 ◆ MED      │  │ 2 Resolved   │          │║
║ │          │ │ └──────────────┘  └──────────────┘          │║
║ │          │ │                                              │║
║ │          │ │ Asset Metadata                               │║
║ │          │ │ ┌────────────────────────────────────────┐  │║
║ │          │ │ │ IP Address    192.168.1.10              │  │║
║ │          │ │ │ Hostname      web-prod-01.example.com   │  │║
║ │          │ │ │ OS            Ubuntu 22.04 LTS          │  │║
║ │          │ │ │ Type          Server                    │  │║
║ │          │ │ │ Environment   Production                │  │║
║ │          │ │ │ Department    Infrastructure            │  │║
║ │          │ │ │ Auth Doc      NDA-2024-SEC-0042         │  │║
║ │          │ │ │ Registered    Feb 15, 2026 · j.garcia   │  │║
║ │          │ │ └────────────────────────────────────────┘  │║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

TABS del Asset Detail:
  Overview  → este wireframe
  Services  → tabla de servicios descubiertos (Screen 04)
  CVEs      → tabla de CVEs correlacionados (Screen 05)
  Reports   → lista de reportes del asset

STATS CARDS (4 cards en 2x2 grid):
  - Last Scan: fecha + status + count de servicios
  - Hardening Score: número + /100
  - CVEs: count por severidad (sólo Critical y High visibles)
  - Remediation: conteos por estado

REGLA: Los 4 stat cards tienen el mismo tamaño. Sin gráficos circulares ni barras.
       Números y texto únicamente. La densidad visual viene de los datos, no de adornos.

CISO VARIANT (mismo URL, distinto render):
  - IP Address → [REDACTED — contact your security analyst]
  - Hostname   → web-prod-01 (sin dominio)
  - No tabs Services ni CVEs
  - Stats: "Critical Risk: 2 issues" en lugar de CVE counts
  - [Request Technical Detail] button → notificación al Analyst asignado
```

---

### SCREEN 04 — Discovery Results (Services)

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Analyst, Admin]  · Tab: Services dentro de Asset Detail║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Exposure › Assets › web-prod-01 › Services   │║
║ │          │ │                                              │║
║ │          │ │ web-prod-01   [Run Scan] [Correlate CVEs] […]│║
║ │          │ │ ● Authorized  ·  Last scan: Mar 9, 14:32     │║
║ │          │ │                                              │║
║ │          │ │ [Overview] [Services ─] [CVEs] [Reports]     │║
║ │          │ │                                              │║
║ │          │ │ 12 services discovered  ·  Scan: TCP SYN     │║
║ │          │ │ ┌────────────────────────────────────────────┐║
║ │          │ │ │PORT↕  PROTO SERVICE↕  VERSION↕    CONFIDENCE│║
║ │          │ │ │─────────────────────────────────────────   │║
║ │          │ │ │22    TCP   ssh       OpenSSH 8.2p1 ◉ Verif.│║
║ │          │ │ │80    TCP   http      Apache 2.4.52  ◉ Verif.│║
║ │          │ │ │443   TCP   https     Apache 2.4.52  ◉ Verif.│║
║ │          │ │ │3306  TCP   mysql     MySQL 8.0.32   ◉ Verif.│║
║ │          │ │ │8080  TCP   http-alt  Jetty 9.4.51   ◎ Unver.│║
║ │          │ │ │5432  TCP   postgresql PostgreSQL 14 ◉ Verif.│║
║ │          │ │ │─────────────────────────────────────────   │║
║ │          │ │ │▼  6 more services (medium/no version)       │║
║ │          │ │ └────────────────────────────────────────────┘║
║ │          │ │                                              │║
║ │          │ │ ┌───────────────────────────────────────────┐│║
║ │          │ │ │ⓘ CVEs not yet correlated for this scan.   ││║
║ │          │ │ │  [Correlate CVEs →]                        ││║
║ │          │ │ └───────────────────────────────────────────┘│║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

COLUMNAS: PORT · PROTOCOL · SERVICE · VERSION · DETECTION METHOD · CONFIDENCE · LAST SEEN
Todos los datos en fuente mono.

AGRUPACIÓN:
  Bloque 1: Servicios con versión confirmada (Verified/Unverified) — siempre visibles
  Bloque 2: "▼ N more services (no version detected)" — colapsado, expandible con click

REGLA DE CONFIANZA:
  ◉ Verified   → CPE match exacto → CVE correlation alta fidelidad
  ◎ Unverified → Version string match → CVE correlation posible
  ○ Unconfirmed → Solo nombre servicio → CVE correlation no recomendada

SCAN TRIGGER MODAL: (al hacer click en "Run Scan")
  ConfirmationModal con:
  - Target: IP + hostname
  - Scan type: TCP Discovery
  - Initiated by: user email
  - "This will be logged to Audit Trail"
  - [Cancel] [Run Scan →]

ESTADO SIN SCAN PREVIO:
  EmptyState con:
  "No discovery scan has been run yet."
  "Run a scan to discover services and correlate vulnerabilities."
  [Run Discovery Scan]
```

---

### SCREEN 05 — Exposure Findings (CVEs)

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Analyst, Admin]  · Tab: CVEs dentro de Asset Detail   ║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Exposure  ›  Assets  ›  web-prod-01  ›  CVEs │║
║ │          │ │                                              │║
║ │          │ │ web-prod-01                    [+ Correlate] │║
║ │          │ │                                              │║
║ │          │ │ [Overview] [Services] [CVEs ─] [Reports]     │║
║ │          │ │                                              │║
║ │          │ │ ─ CONFIRMED VULNERABILITIES (13) ─────────── │║
║ │          │ │ Correlated from version-matched services      │║
║ │          │ │                                              │║
║ │          │ │ [Status ▾] [Severity ▾]           [Export ↓] │║
║ │          │ │ ─────────────────────────────────────────    │║
║ │          │ │ CVE-2023-38408 ⬤CRIT 9.8  OpenSSH 8.2  Open  │║
║ │          │ │                            [✦ Explain] [···] │║
║ │          │ │ CVE-2021-41617 ▲HIGH 7.0  OpenSSH 8.2  Open  │║
║ │          │ │ CVE-2022-22719 ▲HIGH 7.5  Apache 2.4.52 Open │║
║ │          │ │ CVE-2023-25690 ▲HIGH 9.8  Apache 2.4.52 Ackd │║
║ │          │ │ CVE-2023-27522 ◆MED  7.5  Apache 2.4.52 Open │║
║ │          │ │ [▼ Show 8 more Medium/Low]                   │║
║ │          │ │                                              │║
║ │          │ │ ─ UNCONFIRMED (service name only) (6) ─────── │║
║ │          │ │ ⚠ Version not confirmed for these services.   │║
║ │          │ │   Manual verification recommended.            │║
║ │          │ │ [▼ Show 6 unconfirmed correlations]          │║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

SECCIÓN 1 — CONFIRMED VULNERABILITIES:
  Correlaciones con confidence HIGH o MEDIUM
  Columnas: CVE ID | CVSS Score | Severity | Software | Version | Status | Actions

  Inline actions por CVE (menú [···]):
    - Acknowledge (→ status: acknowledged)
    - Mark as False Positive
    - View CVE Details (expand row)
    - Explain with AI

  Expand row (click en CVE ID o ▶):
  ┌──────────────────────────────────────────────────────────┐
  │ CVE-2023-38408                                           │
  │ CVSS v3.1: 9.8 CRITICAL · Vector: AV:N/AC:L/PR:N/UI:N   │
  │ Published: 2023-07-20 · Modified: 2023-08-10             │
  │                                                          │
  │ OpenSSH's ssh-agent remote code execution via forwarded  │
  │ agent connections when PKCS#11 shared libraries are...   │
  │                                                          │
  │ Evidence source: Nmap CPE match cpe:/a:openbsd:openssh   │
  │ Confidence: ◉ Verified · Detected: Mar 9, 2026 14:35     │
  │                                                          │
  │ Status: ○ Open  ·  [Acknowledge] [Mark False Positive]   │
  │                                                          │
  │ [ ✦ Explain with AI ]                                    │
  └──────────────────────────────────────────────────────────┘

SECCIÓN 2 — UNCONFIRMED:
  Colapsada por defecto. Aviso prominente de que son no verificadas.
  Mismo formato de tabla pero con ○ Unconfirmed badge en cada fila.

REGLA ANTI-FLOODING:
  Critical y High: siempre visibles en sección 1
  Medium/Low: colapsados bajo "▼ Show N more Medium/Low"
  Un analista nunca ve 200 CVEs a la vez. La vista default es siempre Critical+High.
```

---

### SCREEN 06 — Hardening Assessment (Checklist)

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Analyst, Admin]  · La pantalla más compleja del MVP   ║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Hardening  ›  Assessments  ›  #A-042  ›  Checks│
║ │          │ │                                              │║
║ │          │ │ CIS Linux L1 — web-prod-01     [Complete ▶]  │║
║ │          │ │ In Progress · Mar 10, 2026 · j.garcia        │║
║ │          │ │                                              │║
║ │          │ │ [Checks ─] [Score] [Remediation]             │║
║ │          │ │                                              │║
║ │          │ │ Progress: 7 / 10 checks evaluated            │║
║ │          │ │ ████████████████████░░░░░░░░░░  70%          │║
║ │          │ │                                              │║
║ │          │ │ ┌──────────────────────────────────────────┐ │║
║ │          │ │ │SECTION: Filesystem Configuration (3/3)   │ │║
║ │          │ │ ├─────────────────────────────────────────  │║
║ │          │ │ │ 1.1.1 ▼LOW  Ensure /tmp partition         │ │║
║ │          │ │ │             ✓ PASS  ·  Evidence provided  │ │║
║ │          │ │ │                          [▶ View evidence] │ │║
║ │          │ │ ├─────────────────────────────────────────  │║
║ │          │ │ │ 1.4.1 ▲HIGH Ensure bootloader permissions │ │║
║ │          │ │ │                                           │ │║
║ │          │ │ │  ○ Pass  ●Fail  ○ N/A  ○ Manual Review   │ │║
║ │          │ │ │                                           │ │║
║ │          │ │ │  ▼ Command to verify:                     │ │║
║ │          │ │ │  stat /boot/grub2/grub.cfg                │ │║ ← mono
║ │          │ │ │                                           │ │║
║ │          │ │ │  Evidence  ★ REQUIRED                     │ │║
║ │          │ │ │  Type: [Command Output  ▾]                │ │║
║ │          │ │ │  ┌──────────────────────────────────────┐ │ │║
║ │          │ │ │  │ Paste output here...                 │ │ │║
║ │          │ │ │  └──────────────────────────────────────┘ │ │║
║ │          │ │ │                           [Save ✓]        │ │║
║ │          │ │ ├─────────────────────────────────────────  │║
║ │          │ │ │ 3.5.1 ◆MED  Ensure DCCP disabled          │ │║
║ │          │ │ │             ⊘ N/A  ·  Note: No GRUB       │ │║
║ │          │ │ └──────────────────────────────────────────┘ │║
║ │          │ │                                              │║
║ │          │ │ ┌──────────────────────────────────────────┐ │║
║ │          │ │ │SECTION: Network Configuration (1/3)      │ │║
║ │          │ │ │  [3 checks, 1 evaluated, 2 pending]      │ │║
║ │          │ │ │  [▶ Expand section]                      │ │║
║ │          │ │ └──────────────────────────────────────────┘ │║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

ESTRUCTURA DEL CHECK ITEM:
  Estado collapsed (ya evaluado):
    [check_id] [SeverityBadge] [título]     ← 44px altura
    [StatusBadge: Pass/Fail/N-A]  · [Evidence indicator]

  Estado expanded (en evaluación — el check activo):
    [check_id] [SeverityBadge] [título]     ← siempre visible
    Descripción breve del check (14px, text-secondary)
    [▼ Rationale: por qué importa este check] ← colapsable
    [▼ Audit command: comando para verificar] ← texto mono, read-only

    RADIO BUTTONS: ○ Pass  ○ Fail  ○ Not Applicable  ○ Manual Review

    EVIDENCE INPUT (visible tras seleccionar Pass o Fail):
    [EvidenceInput component completo]

    [Save check  ✓]  ← guarda este check y colapsa

REGLAS DE EVIDENCIA EN EL CHECKLIST:
  - El EvidenceInput NO aparece si se selecciona N/A o Manual Review
  - Si se selecciona N/A: aparece campo "Justification" (1 línea, obligatorio)
  - Si se selecciona Manual Review: aparece nota "Needs review" (opcional)
  - NO se puede guardar un check Pass/Fail sin evidence_text
  - El botón [Complete Assessment] valida TODOS los checks antes de submitir

PROGRESS BAR:
  No es decorativa — muestra checks completados / total
  Color: brand mientras in_progress; pass-fg cuando todo completo

SECCIONES AGRUPADAS:
  Los checks se agrupan por sección CIS (Filesystem, Network, etc.)
  Las secciones completas se muestran colapsadas con un summary
  La sección activa está expandida

"Complete Assessment" button:
  - Disabled (gris) mientras haya checks sin evaluar
  - Enabled cuando todos marcados
  - Click → validación backend → si pasa: assessment.status = completed → redirect a /score
  - Si falla validación → InlineAlert con lista de checks sin evidencia
```

---

### SCREEN 07 — Remediation Items

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Analyst, Admin]  · Tab: Remediation dentro de Assessment║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Hardening  ›  Assessments  ›  #A-042  ›  Rem.│║
║ │          │ │                                              │║
║ │          │ │ CIS Linux L1 — web-prod-01                   │║
║ │          │ │ Completed · Score: 74/100 · 3 items open     │║
║ │          │ │                                              │║
║ │          │ │ [Checks] [Score] [Remediation ─]             │║
║ │          │ │                                              │║
║ │          │ │ ┌────────────────────────────────────────────┐║
║ │          │ │ │⬤ CRITICAL (1)                              │║
║ │          │ │ ├────────────────────────────────────────────┤║
║ │          │ │ │ 3.3.2 Ensure IPv6 router advert. disabled  │║
║ │          │ │ │ ● Open  ·  Effort: minutes  ·  [Explain ✦]│║
║ │          │ │ │                                            │║
║ │          │ │ │ Fix: Add net.ipv6.conf.all.accept_ra=0     │║
║ │          │ │ │      to /etc/sysctl.d/99-cis-hardening.conf│║
║ │          │ │ │      Then run: sysctl --system             │║
║ │          │ │ │                                            │║
║ │          │ │ │ [Mark In Progress]  [Mark Resolved]        │║
║ │          │ │ └────────────────────────────────────────────┘║
║ │          │ │                                              │║
║ │          │ │ ┌────────────────────────────────────────────┐║
║ │          │ │ │▲ HIGH (2)                                  │║
║ │          │ │ ├────────────────────────────────────────────┤║
║ │          │ │ │ 1.6.1 Ensure core dumps restricted     ⟳IP │║
║ │          │ │ │ 4.2.4 Ensure SSH X11 forwarding disabled ● │║
║ │          │ │ └────────────────────────────────────────────┘║
║ │          │ │                                              │║
║ │          │ │ ┌────────────────────────────────────────────┐║
║ │          │ │ │◆ MEDIUM (0)  ✓ All resolved                │║
║ │          │ │ └────────────────────────────────────────────┘║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

ESTRUCTURA DE ITEM DE REMEDIACIÓN:
  Header (siempre visible):
    [SeverityBadge] [check_id] [título] [StatusBadge] [effort] [✦ Explain]

  Body expandido:
    Recomendación: texto descriptivo (sans, 14px)
    Pasos: lista numerada con comandos en mono

    Actions row:
      [Mark In Progress] [Mark Resolved ✓] [Accept Risk] [Won't Fix]

    Si Resolved: "Resolved by [user] on [date]" + campo para resolution_notes

AGRUPACIÓN POR SEVERIDAD:
  Las secciones se muestran en orden: Critical → High → Medium → Low
  Secciones con 0 open items se colapsan: "◆ MEDIUM (0) ✓ All resolved"

QUICK WINS VISUAL:
  El esfuerzo estimado (Effort: minutes/hours/days/weeks) es prominente
  Los items de "minutes" effort + alta severidad tienen un sutil destacado:
  border-l-4 brand (sugiere "haz esto primero" sin decirlo explícitamente)

REGLA: NO hay "prioritize" button. La priorización ya está hecha por el order:
  Critical + minutes effort > Critical + days effort > High + minutes effort...
  El analista simplemente trabaja de arriba hacia abajo.
```

---

### SCREEN 08 — Technical Report View

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Analyst, Admin]  · Report Generation Interface        ║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Platform  ›  Reports  ›  New Report          │║
║ │          │ │                                              │║
║ │          │ │ Generate Technical Report     [← Back]       │║
║ │          │ │                                              │║
║ │          │ │ ┌────────────────────────────────────────┐   │║
║ │          │ │ │ SCOPE                                  │   │║
║ │          │ │ │ Asset:    [web-prod-01           ▾]    │   │║
║ │          │ │ │ Template: [● Technical Exposure      ] │   │║
║ │          │ │ │           [○ Technical Hardening     ] │   │║
║ │          │ │ │           [○ Full Assessment (both)  ] │   │║
║ │          │ │ │ Format:   [● PDF] [○ DOCX]             │   │║
║ │          │ │ └────────────────────────────────────────┘   │║
║ │          │ │                                              │║
║ │          │ │ ┌────────────────────────────────────────┐   │║
║ │          │ │ │ REPORT INCLUDES                        │   │║
║ │          │ │ │ ✓ Asset metadata & authorization info  │   │║
║ │          │ │ │ ✓ Discovery scan results (Mar 9, 14:32)│   │║
║ │          │ │ │ ✓ 13 CVEs (2 Critical, 4 High, 7 Med.) │   │║
║ │          │ │ │ ✗ Hardening assessment (none complete) │   │║
║ │          │ │ │ ✓ Analyst disclaimer                   │   │║
║ │          │ │ │ ✓ Audit trail for this asset           │   │║
║ │          │ │ └────────────────────────────────────────┘   │║
║ │          │ │                                              │║
║ │          │ │          [Generate Report →]                 │║
║ │          │ │                                              │║
║ │          │ │ ─── REPORT HISTORY ────────────────────────  │║
║ │          │ │ web-prod-01_technical_20260309.pdf           │║
║ │          │ │ Technical Exposure · Mar 9 · j.garcia [↓]   │║
║ │          │ │ web-prod-01_technical_20260220.pdf           │║
║ │          │ │ Technical Exposure · Feb 20 · j.garcia [↓]  │║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

SECCIÓN "REPORT INCLUDES" (crítica para UX):
  El usuario sabe QUÉ va a estar en el reporte ANTES de generarlo.
  Items con ✓: incluidos con datos actuales
  Items con ✗: no incluibles (con razón: "none complete", "no scan data")

  NUNCA generar un reporte sorpresa. El usuario tiene pleno control del contenido.

GENERACIÓN (tras click):
  - Modal de confirmación: "Report will be generated for web-prod-01.
    This action will be logged."
  - Redirect a /reports/history con status "Generating..."
  - Polling hasta "Ready" → botón [↓ Download PDF]

REPORT HISTORY:
  Columnas: Filename · Template · Date · Generated by · Hash (primeros 8 chars)
  [↓] botón de descarga por fila

REGLA: El hash SHA-256 (truncado a 8 chars) siempre visible. Permite verificar integridad.
       "web-prod-01_technical_20260309.pdf  ·  Hash: a4f3b2c1..."
```

---

### SCREEN 09 — Audit Log

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Admin ONLY]                                           ║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Settings  ›  Audit Log                       │║
║ │          │ │                                              │║
║ │          │ │ Audit Trail                      [Export CSV]│║
║ │          │ │ Read-only · All actions since system start    │║
║ │          │ │                                              │║
║ │          │ │ [🔍 Search user, action, resource...]        │║
║ │          │ │ [Date range ▾]  [Action type ▾]  [User ▾]   │║
║ │          │ │                                              │║
║ │          │ │ TIMESTAMP ↕  USER        ACTION    RESOURCE  │║
║ │          │ │ ─────────────────────────────────────────── │║
║ │          │ │ Mar 10 14:23 j.garcia    scan.start web-p-01 │║
║ │          │ │ Mar 10 14:21 j.garcia    cve.ack    CVE-2023- │║
║ │          │ │ Mar 10 09:15 a.admin     asset.auth web-p-01 │║
║ │          │ │ Mar  9 16:45 j.garcia    report.gen web-p-01 │║
║ │          │ │ Mar  9 14:32 j.garcia    scan.comp  web-p-01 │║
║ │          │ │ Mar  9 14:30 j.garcia    scan.start web-p-01 │║
║ │          │ │ ─────────────────────────────────────────── │║
║ │          │ │ Showing 1–50 of 1,247      [< 1 2 3 ... >]   │║
║ │          │ │                                              │║
║ │          │ │ ⓘ This log is append-only. No entries can    │║
║ │          │ │   be deleted or modified.                    │║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

COLUMNAS:
  TIMESTAMP (mono, texto completo) · USER (email) · ACTION (mono, formato "entity.verb")
  · RESOURCE TYPE · RESOURCE ID (truncado) · DETAILS [▶]

EXPAND ROW (click en fila):
  ┌──────────────────────────────────────────────────────────┐
  │ action:       scan.started                               │
  │ resource:     asset / 3f4a-b2c1...                       │
  │ user:         j.garcia@example.com                       │
  │ timestamp:    2026-03-10T14:23:41.284Z                   │
  │ ip_address:   10.0.2.105                                 │
  │ details:      {"scan_type": "tcp_discovery",             │
  │               "port_range": "1-1024",                    │
  │               "asset_ip": "192.168.1.10"}               │
  └──────────────────────────────────────────────────────────┘
  Todo el JSON en mono. Fondo bg-raised. Sin botones.

REGLAS:
- Sin botones de edición o borrado en ninguna fila. La UI es 100% read.
- Aviso de "append-only" siempre visible al pie de la tabla
- Export CSV: todos los campos, sin truncar
- Density: 36px por fila (más compacto que otras tablas — son logs, no entidades)
- Acciones: solo Export CSV. Sin "Clear Log", sin "Delete", sin "Archive".
```

---

### SCREEN 10 — Settings (limitado)

```
╔══════════════════════════════════════════════════════════════╗
║  [Rol: Admin ONLY]  · Vista limitada para MVP                ║
╠══════════════════════════════════════════════════════════════╣
║ ┌──────────┐ ┌──────────────────────────────────────────────┐║
║ │ SIDEBAR  │ │ Settings  ›  Users                           │║
║ │          │ │                                              │║
║ │ SETTINGS │ │ ┌─────────────────────────────┐             │║
║ │ > Users  │ │ │ Users              Audit Log│ ← sub-tabs  │║
║ │ ·AuditLog│ │ └─────────────────────────────┘             │║
║ │          │ │                                              │║
║ │          │ │ Users (5)                    [+ Invite User] │║
║ │          │ │                                              │║
║ │          │ │ NAME          EMAIL          ROLE    STATUS  │║
║ │          │ │ ─────────────────────────────────────────── │║
║ │          │ │ Ana García    a@org.com   Admin   ● Active   │║
║ │          │ │ Juan Pérez    j@org.com   Analyst ● Active   │║
║ │          │ │ María López   m@org.com   Analyst ● Active   │║
║ │          │ │ Carlos R.     c@org.com   CISO    ● Active   │║
║ │          │ │ Pedro S.      p@org.com   Analyst ◌ Invited  │║
║ │          │ │                                              │║
║ │          │ │ ─────────────────────────────────────────── │║
║ │          │ │                                              │║
║ │          │ │ ⓘ User management. Only Admins can create,  │║
║ │          │ │   edit, or deactivate users.                 │║
║ └──────────┘ └──────────────────────────────────────────────┘║
╚══════════════════════════════════════════════════════════════╝

FUNCIONES EN MVP:
  Users tab:
    - Lista de usuarios con rol y estado
    - [+ Invite User]: modal con email + role dropdown
    - Acciones por fila [···]: Edit role, Deactivate
    - NO: delete (sólo deactivate para preservar audit trail references)

  Audit Log tab:
    - Redirige a /settings/audit-log (Screen 09)

FUERA DEL MVP:
  - Integrations tab (V3)
  - System Configuration (V3)
  - SAML/SSO (V3)

REGLA: Settings está intencionalmente limitado. No es un panel de control.
       Es gestión de usuarios y acceso al audit log. Nada más en MVP.
```

---

## 7. Estado Vacíos, Loading y Error

### Empty States por entidad

```
Asset Inventory vacío:
  Icono: Shield (Lucide, 48px, text-tertiary)
  Título: "No assets registered"
  Body: "Register your first authorized asset to begin exposure analysis."
  CTA: [+ Register Asset]  (sólo si Analyst/Admin)

Discovery vacío (sin scan):
  Icono: Radar (48px)
  Título: "No scan data yet"
  Body: "Run a discovery scan to detect services on this asset."
  CTA: [Run Discovery Scan]  (sólo si Authorized)

Discovery vacío (scan completado sin resultados):
  Icono: Search (48px)
  Título: "No services detected"
  Body: "The scan completed but no open ports were found on 192.168.1.10."
       "Verify the target is reachable and the scan options are correct."
  CTA: [Run Scan Again]

CVEs vacíos (sin correlación):
  Icono: ShieldCheck (48px)
  Título: "No CVEs correlated yet"
  Body: "Run CVE correlation after a service discovery scan."
  CTA: [Correlate CVEs]

CVEs vacíos (correlación sin CVEs):
  Icono: ShieldCheck (48px, pass-fg)
  Título: "No CVEs found"
  Body: "No known vulnerabilities found for the detected service versions."
       "Keep software updated to maintain this status."
  CTA: ninguno (es un resultado positivo)

Assessments vacíos:
  Icono: ClipboardCheck (48px)
  Título: "No assessments yet"
  Body: "Start a CIS assessment to evaluate the hardening of this asset."
  CTA: [Start Assessment]

Remediation vacía (todo resuelto):
  Icono: CheckCircle (48px, pass-fg)
  Título: "All remediation items resolved"
  Body: "This assessment has no open remediation items."
  CTA: [Start Re-evaluation]

Audit log vacío:
  Icono: List (48px)
  Título: "No actions recorded yet"
  Body: "All platform actions will appear here once users begin working."
  CTA: ninguno
```

### Loading States

```
SKELETON LOADERS (preferido sobre spinner genérico):

Tabla en carga:
  ┌──────────────────────────────────────────────────────────┐
  │ ░░░░░░░░░░░░  ░░░░░░░░░░░░  ░░░░░░  ░░░░░░░░░          │  ← fila skeleton
  │ ░░░░░░░░░░░   ░░░░░░░░░░░   ░░░░░   ░░░░░░░            │
  │ ░░░░░░░░░░░░░ ░░░░░░░░░░░░░ ░░░░░░░ ░░░░               │
  └──────────────────────────────────────────────────────────┘
  Los bloques ░ son bg-raised animados (shimmer, 1.5s, ease-in-out)

Stat card en carga:
  ┌──────────────┐
  │ ░░░░░░░░░░░  │  ← título skeleton
  │              │
  │   ░░░░░░░   │  ← número skeleton grande
  └──────────────┘

AIExplainPanel cargando:
  ┌──────────────────────────────────────────────────────────┐
  │ ✦ Generating explanation...                              │
  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │
  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │
  │ ░░░░░░░░░░░░░░░░░░░░░░░                                 │
  └──────────────────────────────────────────────────────────┘
  Texto "Generating explanation..." visible — no sólo shimmer

Spinner: SÓLO para botones de acción mientras procesan.
  [Generating...  ⟳]  ← spinner inline en el botón, botón deshabilitado
  NO para carga de páginas. NO para tablas.
```

### Error States

```
Error de red / API down:
  InlineAlert ✗ en la zona de contenido:
  "Unable to load assets. Check your network connection."
  [Retry]

Error de scan fallido:
  ScanStatusBar en rojo:
  "✗ Scan failed: Connection refused (192.168.1.10:80)"
  [Retry Scan]

Error de validación en formulario:
  Field-level: borde critical-border + texto de error 12px bajo el campo
  Form-level (si hay múltiples): InlineAlert ✗ al tope del formulario

Error de AI rate limit:
  "✦ AI explanation unavailable — Rate limit reached (5/hour)."
  "Try again in 47 minutes."
  Sin CTA. Sin alternativa sugerida de forma automática.

Error 403 (acceso no autorizado):
  Pantalla completa centrada:
  Icono Lock (48px, text-tertiary)
  "You don't have permission to access this page."
  "Contact your administrator if you need access."
  [← Go Back]

Error 404:
  Icono SearchX (48px)
  "Page not found"
  "This asset may have been removed or you may have an incorrect link."
  [← Go to Assets]
```

---

## 8. Reglas de Diseño

### Tablas: reglas obligatorias

```
1. Row height:        44px (standard), 36px (audit log — alta densidad)
2. Header:            11px / 600 / uppercase / tracking-wide / text-tertiary
3. Cell text:         14px / 400 / sans para semántico; 13px / 400 / mono para técnico
4. Hover row:         background bg-raised, transición 80ms
5. Active/selected:   border-l-2 brand + bg-raised
6. Sort indicators:   ↕ (none), ↑ (asc), ↓ (desc) — siempre visible en header clickeable
7. Column actions:    última columna, siempre [···] nunca con label
8. Densidad:          generous padding (16px horizontal) — no compactar datos
9. Zebra:             NO. El hover proporciona el feedback visual necesario.
10. Líneas:           border-faint entre filas, NO grid lines entre columnas
11. Números en celdas: alineados a la derecha con font-mono
12. Badges en celdas: centrados verticalmente, no más de 2 por celda
13. Truncate largo:   máximo 1 línea, tooltip en hover para el valor completo
14. Paginación:       server-side para > 100 filas; client-side para ≤ 100
```

### Severity Badges: reglas inmutables

```
1. UN SOLO sistema de colores para severidad en TODA la app.
   Critical = red. High = orange. Medium = yellow. Low = blue. Pass = green.
   Esta asignación no cambia en ninguna pantalla, ningún contexto.

2. El icono de texto (⬤ ▲ ◆ ▼ ✓) SIEMPRE acompaña al badge.
   Es necesario para accesibilidad (no depender sólo del color) y para PDF export.

3. SeverityBadge vs RiskBadge:
   Analyst/Admin: SeverityBadge con texto técnico (CRITICAL, HIGH, etc.)
   CISO: RiskBadge con texto de negocio ("Critical Risk", "High Risk")
   Son componentes distintos que se renderizan según user.role.

4. Nunca usar colores de severidad para otro concepto.
   Si necesitas un badge de "Production", NO uses green (podría confundirse con Pass).
   Usar un badge neutro: bg-raised, border-default, text-primary.

5. No combinar múltiples SeverityBadges en la misma celda de tabla.
   Si un asset tiene CVEs de múltiples severidades: mostrar sólo el más alto.
   "⬤ CRITICAL (2)" — no "⬤ CRIT ▲ HIGH ◆ MED".
```

### Scores: reglas de presentación

```
1. Siempre mostrar Raw Y Weighted:
   "74.0% raw  ·  68.4% weighted"
   Nunca sólo uno. El usuario debe entender que son métricas distintas.

2. Color del número según valor:
   < 50:  critical-fg
   50–74: high-fg
   75–89: medium-fg  ← "naranja-amarillo": indica progreso pero no excelencia
   ≥ 90:  pass-fg

3. Delta en re-evaluación: siempre con dirección y color
   ↑ +19  (pass-fg si positivo)
   ↓ −5   (critical-fg si negativo)

4. NO usar gauge charts o donut charts para el score.
   El número es suficiente. Si se necesita contexto visual: una barra horizontal simple.
   ████████████████░░░░  74/100
   No más. No animado. No 3D.

5. En tablas multi-asset: score como número inline en mono, con color del número.
   74  ← directamente en la celda, color según valor, sin badge adicional
```

### Evidencia: reglas de presentación

```
1. El campo de evidencia NUNCA es un campo pequeño o de baja jerarquía.
   En el checklist de assessment, la evidencia es el elemento central.

2. Evidencia guardada (read-only) se muestra en:
   - Fondo bg-raised (distinguible del resto)
   - Fuente mono para el contenido (es output técnico)
   - Prefijo "Evidence [tipo] · Collected [fecha]" como label

3. La fecha de evidencia (evidence_at) siempre visible junto al contenido.
   No hay evidencia sin timestamp.

4. Estado visual de evidencia por check:
   ✓ Evidence provided  → texto pass-fg pequeño, click para ver
   ⚠ Evidence required  → texto critical-fg, campo expandido forzado
   — Not required (N/A) → no indicator

5. En el reporte PDF: la evidencia se incluye en el apéndice, no en el cuerpo.
   El cuerpo muestra: check, resultado, recomendación.
   El apéndice muestra: evidencia completa por check (para auditoría).
```

### Remediación: reglas de priorización visual

```
1. Las items de remediación se ordenan por: severidad → effort (menor primero)
   Critical/minutes > Critical/hours > Critical/days > High/minutes > ...
   El UI no tiene botón "sort". Este es el orden siempre.

2. Quick wins (effort = minutes + severity ≥ high):
   Highlight sutil: border-l-4 brand
   No texto extra. El analista lee el orden y lo entiende.

3. Effort badge: siempre visible junto al status
   "minutes"  → text-pass-fg (positivo, es rápido)
   "hours"    → text-secondary
   "days"     → text-medium-fg
   "weeks"    → text-high-fg (señal de que requerirá planning)

4. Status de remediación en tabla:
   ● Open       → dot color según severity
   ⟳ In Progress → dot brand
   ✓ Resolved   → dot pass-fg + texto tachado (visual closure)
   ⊘ Accepted   → dot text-tertiary + tooltip "Accepted risk — see notes"
   ✕ Won't Fix  → dot text-tertiary

5. Progress counter en el header del assessment:
   "3 open · 1 in progress · 6 resolved"
   Siempre los tres números. Sin barra de progreso adicional.
```

---

## 9. Principios de Diseño (10 reglas absolutas)

### P-01: Un color, un significado
La paleta de severidad (Critical/High/Medium/Low/Pass) es inmutable y exclusiva para severidades. Ningún color de este sistema se reutiliza para otro concepto. Violarlo rompe la lectura rápida que los analistas desarrollan con el tiempo.

### P-02: Los datos técnicos hablan en monospace
IP, hostname, CVE ID, puerto, versión de software, hash, banner, timestamp ISO — todo en `JetBrains Mono`. Sin excepciones. La diferencia visual entre `data` y `narrative` es parte del lenguaje de la interfaz.

### P-03: El estado siempre es visible
Ningún activo, scan, assessment, o item de remediación existe en la UI sin un StatusBadge visible. El usuario nunca tiene que preguntarse "¿está corriendo el scan?", "¿fue aprobado el activo?", "¿está resuelto el item?".

### P-04: No hay acción sin confirmación
Scans, autorizaciones, borrados, completación de assessments — cualquier acción que modifica estado muestra un ConfirmationModal que describe qué va a ocurrir, sobre qué target, y que quedará en el audit trail. Sin excepciones.

### P-05: Los charts deben justificar su existencia
Un chart sólo existe si ayuda a tomar una decisión que no se tomaría igualmente con un número o una tabla. En MVP: cero charts. Los números y las tablas son la visualización. Un gráfico de barras de la tendencia de score existe en V2 porque muestra mejora a lo largo del tiempo — eso no se lee igual en una tabla. Un donut chart del porcentaje de checks pasados no existe porque "74%" ya lo dice todo.

### P-06: Los empty states son invitaciones, no errores
Una tabla vacía sin contexto es un bug de UX. Todo estado vacío tiene icono, explicación de por qué está vacío, y una acción clara si el usuario puede hacer algo al respecto. El tono es instructivo, no de error.

### P-07: La IA es un asistente, no un protagonista
El AI Assist Lite es un panel secundario que se abre bajo demanda. No ocupa espacio en la UI base. "✦ Explain with AI" es un botón de tercera jerarquía — visible pero no dominante. El protagonista de la pantalla siempre son los datos del activo.

### P-08: El CISO y el Analyst ven la misma plataforma, no plataformas distintas
No hay una "vista CISO" separada. Hay componentes que renderizan con distintos niveles de abstracción según `user.role`. Las rutas son las mismas. Lo que cambia es la profundidad de los datos y los componentes renderizados. Esto simplifica el desarrollo y evita que haya un producto de segunda clase para ejecutivos.

### P-09: Cero estética hacker, cero ruido visual
Sin terminales falsos, sin código animado en fondos, sin gradientes de neón, sin efectos de partículas, sin iconografía de "hacker" (calaveras, matrices, candados con rayos). La plataforma parece una herramienta de gestión enterprise seria. Los que la usan son profesionales de seguridad, no personajes de película.

### P-10: El espaciado transmite seriedad
Las plataformas enterprise tienen aire. Las tablas tienen 44px de altura de fila. Las cards tienen 20px de padding. Las páginas tienen 24px de padding lateral. No se compacta para meter más información — se filtra para mostrar menos pero más relevante. La densidad viene de los datos, no del layout.

---

## 10. Riesgos de UX

### UXRISK-01: Evidence fatigue (evidencia omitida sistemáticamente)
**Descripción:** Los analistas, bajo presión de tiempo, marcan checks como Pass/Fail con evidencia mínima o copiada de otro check. Los assessments se vuelven "checkbox theater".

**Señales de alerta:**
- Múltiples checks con evidencia idéntica
- Evidencia de 3 caracteres ("ok", "yes", "✓")

**Mitigación:**
- El campo de evidencia es prominente, no pequeño
- El sistema registra `evidence_at` — si múltiples checks tienen el mismo timestamp exacto, es sospechoso
- En re-evaluaciones, el sistema puede alertar si la evidencia no cambió entre assessments

---

### UXRISK-02: CVE flooding (demasiados hallazgos, parálisis del analista)
**Descripción:** La pantalla de CVEs muestra 200 filas. El analista no sabe por dónde empezar. Deja la pantalla abierta sin tomar acciones.

**Mitigación:**
- Critical + High siempre visibles, Medium/Low colapsados por defecto
- Unconfirmed CVEs siempre colapsados con aviso
- El primer CTA visible en la pantalla es "Acknowledge" el top CVE, no "view all"

---

### UXRISK-03: Scan anxiety (el analista no sabe si el scan sigue corriendo)
**Descripción:** El scan tardó 3 minutos. El analista cerró la pestaña y volvió. ¿Sigue corriendo? ¿Falló?

**Mitigación:**
- ScanStatusBar visible en el Asset Detail independientemente de la sub-tab activa
- Polling cada 3s con actualización visual del estado
- Si el usuario vuelve a la página mientras hay un scan activo: el ScanStatusBar se muestra inmediatamente con el estado actual

---

### UXRISK-04: Assessment overwhelm (el analista no completa el assessment)
**Descripción:** El analista abre un assessment de 10 checks, hace 3, y lo deja en "Draft" porque la evidencia es tediosa.

**Mitigación:**
- Secciones colapsadas (sólo la sección activa expandida)
- Progress bar visible: "7/10 checks evaluated" — el progreso visible motiva la finalización
- El assessment guarda automáticamente cada check (sin "guardar todo")
- El historial de assessments muestra claramente cuántos están "In Progress" como deuda

---

### UXRISK-05: Report irrelevance (los reportes no se leen)
**Descripción:** El analista genera reportes de 40 páginas con todos los CVEs. El CISO los archiva sin leer. Los reportes pierden su función comunicativa.

**Mitigación:**
- "Report Includes" preview antes de generar — el analista sabe qué va a estar
- El reporte técnico está estructurado por secciones con índice
- Los primeros 2 párrafos siempre son el "Executive Summary" del reporte técnico
- El reporte ejecutivo tiene un máximo de 5 páginas de contenido + apéndice

---

### UXRISK-06: Role confusion (el CISO como Analyst frustrado)
**Descripción:** El CISO intenta navegar a los CVEs del activo y no ve IPs ni versiones. Cree que la plataforma está rota.

**Mitigación:**
- En las páginas donde el CISO tiene vista abstracta: un banner sutil:
  "You're viewing a summarized view. Technical detail is available to Analyst users."
- El botón [Request Technical Detail] es visible y tiene un tooltip descriptivo
- La vista del CISO tiene sus propios empty states orientados a su rol

---

### UXRISK-07: Navigation disorientation (el usuario no sabe dónde está)
**Descripción:** El usuario está en el tercer nivel de navegación y no recuerda cómo llegó ahí.

**Mitigación:**
- Breadcrumb siempre visible: "Exposure › Assets › web-prod-01 › CVEs"
- La sidebar muestra el item activo con highlight (bg-raised + border-l-2)
- Los tabs del Asset Detail persisten cuando se navega entre sub-secciones
- El botón ← Back siempre presente en las páginas de formularios (New Asset, New Assessment)

---

### UXRISK-08: Settings como zona de peligro
**Descripción:** El Admin entra en Settings y puede borrar usuarios o hacer cambios que afectan a todos. Sin confirmación adecuada, puede romper el acceso de otros.

**Mitigación:**
- Deactivate User (no Delete) — los usuarios desactivados siguen en la BD para el audit trail
- Cambio de rol: ConfirmationModal con "This will change [user]'s access level immediately"
- Invite User: el link de invitación expira en 48h — no hay cuenta hasta que el usuario acepta

---

*Documento de diseño UX. Versión 1.0.0 — Actualizar al inicio de cada fase de desarrollo.*
