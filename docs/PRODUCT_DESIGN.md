# CiberCortex IA — Product Design Document

**Version:** 0.3.0
**Date:** 2026-03-10
**Cambios respecto a v0.2.0:** MVP reducido a 8 bloques; ciclo de valor extendido a 5 pasos; principio evidence-first; AI Lite en MVP; CISO con drill-down controlado; secciones nuevas: Product Guardrails, Definition of Done, Failure Modes, Open Questions.

---

## Executive Summary

CiberCortex IA es una plataforma defensiva de gestión de postura de seguridad. Su propósito es dar a los equipos de seguridad **visibilidad sobre lo que tienen expuesto, evaluación de cómo está configurado, y un camino claro para mejorar** — todo sobre activos explícitamente autorizados, con evidencia obligatoria y trazabilidad total.

**Cambios clave en esta versión:**

| Aspecto | v0.2.0 | v0.3.0 |
|---|---|---|
| MVP | 13 módulos | **8 bloques funcionales** |
| Ciclo de valor | 4 pasos | **5 pasos (añade Remediate + Validate)** |
| Evidencia | Opcional | **Obligatoria para todo hallazgo** |
| IA en MVP | No | **AI Lite: sólo explicación, sin autonomía** |
| CISO | Read-only puro | **Abstracto por defecto, drill-down controlado** |
| Verbos del producto | 4 | **5 (Discover, Evaluate, Prioritize, Remediate, Validate)** |

**Lo que el producto NO es y NUNCA será:** pentesting automatizado, escáner ofensivo, plataforma de explotación, herramienta de evasión, ni sistema de auto-remediación sin aprobación humana explícita.

---

## 1. Posicionamiento

### Frase canónica

> **"CiberCortex IA convierte datos de exposición y configuración en remediación priorizada y validada, sobre activos autorizados, con evidencia trazable en cada paso."**

### Categoría y diferenciación

| Categoría | Herramienta de referencia | Cómo se diferencia CiberCortex IA |
|---|---|---|
| Vulnerability Management | Tenable, Qualys | Sin agente, sin licencias por activo, UX orientada a decisiones no a listas |
| Config Compliance | Chef InSpec, OpenSCAP runner | Con contexto de negocio, roles, reporting y AI advisory |
| CSPM | Wiz, Prisma | Agnóstico de cloud, orientado a on-premise y entornos mixtos |

**Propuesta de valor en una línea por rol:**

- **Analyst:** "Sé exactamente qué tienes expuesto, qué tan mal está configurado, y qué corregir primero."
- **Admin:** "Gobierna qué se evalúa, quién lo evalúa, y que cada acción quede registrada."
- **CISO:** "¿Estamos mejorando? Aquí está la evidencia."

---

## 2. Ciclo de Valor del Producto

El producto estructura su funcionamiento en **5 pasos secuenciales**. Todo módulo y toda feature debe pertenecer a uno de estos pasos o ser infraestructura que los sostiene. No hay excepciones.

```
  ┌────────────────────────────────────────────────────────────────────┐
  │                                                                    │
  │  [1] DISCOVER → [2] EVALUATE → [3] PRIORITIZE → [4] REMEDIATE → [5] VALIDATE
  │      │               │               │               │              │
  │   Assets +        CIS checks      Score +        Track fix       Re-assess
  │   Services +      + Evidence      Queue          progress        + Delta
  │   CVEs                            ordered
  │                                                                    │
  └────────────────────────────────────────────────────────────────────┘
                    REPORTING disponible en cualquier paso
                    AI LITE disponible en cualquier paso (sólo explicar)
                    AUDIT TRAIL registra todo en tiempo real
```

### Por qué 5 pasos y no 4

La versión anterior terminaba en **Report**. El problema: reportar no es el objetivo, **mejorar la postura es el objetivo**. Sin los pasos Remediate y Validate, el producto genera visibilidad pero no cierra el loop. Un analista que genera un reporte sin seguimiento de remediación ni re-evaluación está en la misma posición 6 meses después.

---

## 3. Tabla de Módulos Refinada (MVP = 8 bloques)

### Consolidación respecto a v0.2.0

La versión anterior tenía 13 módulos en MVP. La reducción a 8 se logra consolidando:
- Asset Management + Asset Inventory → **Asset Registry** (eran el mismo concepto en dos capas)
- User Management + Audit Trail → **Platform Core** (infraestructura, no feature de usuario)
- Service Discovery + CVE Correlation → **Exposure Analysis** (un solo workflow en la UI)
- Hardening Score + Remediation Advisor → **Scoring & Remediation** (output único del assessment)
- Reporting Engine + Exposure Reports + Hardening Reports → **Report Engine** (un motor, múltiples templates)

### Tabla canónica de módulos

| ID | Módulo | Objetivo | Usuario principal | MVP / V2 / V3 | Depende de |
|---|---|---|---|---|---|
| **SHARED** | | | | | |
| S-01 | Platform Core | Auth, RBAC, Audit Trail inmutable. Infraestructura del sistema. | Admin | **MVP** | — |
| S-02 | Asset Registry | Registrar, autorizar y gestionar activos. Pivote central del sistema. | Admin + Analyst | **MVP** | S-01 |
| S-03 | Report Engine | Generar reportes PDF/DOCX/XLSX con múltiples templates. | Analyst + Admin + CISO | **MVP** (técnico) / V2 (ejecutivo) | S-02 |
| **EXPOSURE** | | | | | |
| E-01 | Exposure Analysis | Descubrir servicios (Nmap) y correlacionar CVEs (NVD) en activos autorizados. | Analyst | **MVP** | S-02 |
| E-02 | Attack Surface View | Vista agregada de riesgo por tipo de exposición (no por puerto). | Analyst + CISO | V2 | E-01 (necesita histórico) |
| E-03 | Web Posture | Evaluar TLS, HTTP headers, configuración web básica. | Analyst | V2 | S-02 |
| **HARDENING** | | | | | |
| H-01 | CIS Assessment | Crear y completar evaluaciones CIS con evidencia obligatoria por check. | Analyst | **MVP** | S-02 |
| H-02 | Scoring & Remediation | Calcular score ponderado y generar cola priorizada de remediación. | Analyst | **MVP** | H-01 |
| H-03 | Validation Tracker | Registrar re-evaluaciones y calcular delta de mejora respecto al anterior. | Analyst | **MVP** | H-01 + H-02 |
| H-04 | OpenSCAP Import | Importar resultados XCCDF/ARF de escaneos externos como assessments. | Analyst | V2 | H-01 |
| **TRANSVERSAL** | | | | | |
| T-01 | AI Assist Lite | Explicar CVEs y checks fallidos en lenguaje natural. Sin autonomía. Sin acciones. | Analyst | **MVP** (lite) / V2 (completo) | E-01 + H-01 |
| T-02 | Dashboard Overview | Vista ejecutiva: posture score, tendencias, top riesgos. | CISO + Admin | V2 | Requiere datos acumulados |
| T-03 | Multi-tenancy | Organizaciones separadas, datos aislados por tenant. | Admin | V3 | Toda la plataforma |
| T-04 | SSO / SAML | Autenticación federada con IdP corporativo. | Admin | V3 | S-01 |
| T-05 | Integration Hub | Conectores a Jira, Slack, SIEM. | Admin | V3 | S-01 |

### Módulos que nunca existirán

| Capacidad | Razón |
|---|---|
| Exploit execution | Fuera del propósito ético y legal del producto |
| Offensive payloads / weaponization | Prohibido por diseño |
| C2 / reverse shells / persistence | Prohibido por diseño |
| Auto-remediation sin aprobación humana | Riesgo operacional inaceptable |
| Credential dumping / brute force | Prohibido por diseño |
| Scanning de activos no autorizados | Violación del contrato de uso |

---

## 4. Definición del MVP — 8 Bloques Funcionales

### Objetivo del MVP

> Validar que el ciclo completo funciona: **registrar asset → descubrir servicios → correlacionar CVEs → evaluar CIS con evidencia → obtener score → priorizar remediación → validar mejora → generar reporte técnico.**

### Los 8 bloques del MVP

```
S-01  Platform Core          Auth JWT + RBAC 3 roles + Audit Trail
S-02  Asset Registry         CRUD + autorización admin + metadatos
S-03  Report Engine          PDF técnico por asset (Exposure + Hardening)
E-01  Exposure Analysis      Nmap TCP + CVE NVD (con niveles de confianza)
H-01  CIS Assessment         10 checks L1 Linux + evidencia obligatoria
H-02  Scoring & Remediation  Score ponderado + cola priorizada de correcciones
H-03  Validation Tracker     Re-evaluación + delta vs assessment anterior
T-01  AI Assist Lite         Explicar CVE / Explicar check fallido (read-only)
```

### Decisión: AI Lite en MVP (justificación)

La v0.2.0 excluía la IA del MVP argumentando que "requiere datos acumulados". Esa razón es incorrecta para el caso de uso de explicación:

- Explicar `CVE-2024-12345` en el contexto de "un servidor web Linux de producción" es **stateless**. No requiere histórico.
- El costo de implementación es bajo: un endpoint `POST /ai/explain`, un prompt template, rate limiting.
- El valor es inmediato: el analista entiende el riesgo en segundos en lugar de buscar en NIST.
- El riesgo es cero si las constraints son correctas (read-only, sin autonomía, sin triggers).

**Constraints del AI Lite MVP:**

```
Modelo:       claude-haiku-4-5 (bajo costo, respuesta rápida)
Casos de uso: 2 únicos → explain_cve | explain_check_failure
Rate limit:   5 requests / usuario / hora
Caching:      Respuestas cacheadas 24h por (cve_id | check_id + benchmark)
Autonomía:    CERO. El AI no puede crear, modificar, trigger, ni recomendar acciones
              fuera de los pasos de remediación documentados.
System prompt: SYSTEM_PROMPT_DEFENSIVE_ONLY hardcoded, no configurable por usuario
Input sanitization: El contexto del asset se incluye estructuradamente, no como texto libre del usuario
```

### UX del MVP

La UX del MVP puede ser **funcional, no bella**. No se requieren:
- Charts o gráficos animados
- Dashboard overview
- Executive report templates
- Dark mode perfecto

Se requieren: tablas limpias, formularios que funcionan, badges de estado claros, y PDF con datos correctos.

---

## 5. Scope V2

V2 convierte el MVP en un producto que los analistas y CISOs eligen usar de forma recurrente.

### Qué añade V2

| Módulo | Qué añade |
|---|---|
| E-02 Attack Surface View | Vista de riesgo agregada (no por puerto, por impacto real) |
| E-03 Web Posture | TLS grade, HTTP headers: HSTS, CSP, X-Frame-Options |
| H-04 OpenSCAP Import | Importar XCCDF/ARF; los checks se mapean a CIS automáticamente |
| H-03 Validation Tracker upgrade | Gráfico de tendencia de score histórico por asset |
| T-01 AI Assist upgrade | CVE explain mejorado + Remediation steps contextualizados + modelo claude-sonnet-4-6 |
| T-02 Dashboard Overview | Posture score, top CVEs, hardening trend, activos en riesgo |
| S-03 Report Engine upgrade | Template ejecutivo, multi-asset, XLSX export |
| Roles upgrade | Consultant role con scope asignado (AssetGroup) |

### Criterio de entrada a V2

V2 empieza cuando:
1. El MVP está en producción con al menos 1 organización real usándolo
2. Al menos 20 assessments completados en el sistema
3. Al menos 10 reportes PDF generados y validados
4. La tasa de falsos positivos de CVEs está medida y < 10%

---

## 6. Roles de Usuario (v0.3.0)

### Admin
**Quién:** Security Manager, IT Director, responsable de la instancia.
**Preocupación:** Gobernanza del sistema y del scope de autorización.
**Capacidades exclusivas:** Autorizar activos, gestionar usuarios, ver audit log completo, borrar datos (con confirmación).

### Analyst
**Quién:** Security Engineer, el que hace el trabajo técnico.
**Preocupación:** Datos correctos, evaluaciones rápidas, entender qué corregir.
**No puede:** Autorizar activos, gestionar usuarios, ver audit log.

### Consultant (V2)
**Quién:** Asesor externo con contrato.
**Preocupación:** Trabajar sólo en su scope, sin ver información de otros.
**Implementación:** Analyst con `scope_id` FK a AssetGroup. Todos los queries filtran por scope.
**En MVP:** Tratar como Analyst hasta que el concepto de AssetGroup esté implementado.

### CISO — Vista Revisada

**Quién:** Ejecutivo de seguridad. No ejecuta trabajo técnico.
**Preocupación:** ¿Mejoramos? ¿Cuál es el riesgo mayor? ¿Tengo evidencia para el board?

#### Vista abstracta por defecto (siempre disponible)
- Posture score global: número único (e.g., 62/100) con color semántico
- Tendencia: gráfico de score últimos 6 meses
- Riesgos top: "3 activos de producción con CVEs críticos sin acción"
- Remediación: "12 items resueltos este mes / 8 pendientes"

#### Drill-down controlado (disponible bajo demanda)
- Click en categoría de riesgo → ver **nombres** de activos afectados (sin IPs, sin versiones)
- Click en activo → ver **descripción del riesgo** (sin banners, sin raw CVE data)
- "Ver detalle técnico" → genera notificación al Analyst para que comparta el reporte técnico completo

#### Export del CISO
- **Executive PDF:** siempre generado por el CISO (resumen ejecutivo, sin raw data)
- **Technical PDF compartido:** el Analyst genera y lo comparte explícitamente con el CISO (acción con AuditEntry)

> El CISO nunca accede a: IPs, banners de servicio, versiones de software, vectores CVSS, CVE IDs técnicos. Esos datos son del Analyst. El CISO trabaja con riesgo en lenguaje de negocio.

### Matriz de permisos

| Acción | Admin | Analyst | Consultant | CISO |
|---|---|---|---|---|
| Registrar asset | ✅ | ✅ | ❌ | ❌ |
| Autorizar asset | ✅ | ❌ | ❌ | ❌ |
| Ejecutar scan | ✅ | ✅ | ✅ (scope) | ❌ |
| Ver servicios / CVEs raw | ✅ | ✅ | ✅ (scope) | ❌ |
| Ver resumen de riesgo | ✅ | ✅ | ✅ (scope) | ✅ (abstracto) |
| Crear assessment | ✅ | ✅ | ✅ (scope) | ❌ |
| Ver score + remediation | ✅ | ✅ | ✅ (scope) | agregado |
| Usar AI Lite | ✅ | ✅ | ✅ (scope) | ❌ |
| Generar reporte técnico | ✅ | ✅ | ✅ (scope) | ❌ (sólo via Analyst) |
| Generar reporte ejecutivo | ✅ | ✅ | ✅ (scope) | ✅ |
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ |
| Ver audit log | ✅ | ❌ | ❌ | ❌ |
| Borrar datos | ✅ (confirm) | ❌ | ❌ | ❌ |

---

## 7. Principio Evidence-First

### Definición

> **Ningún hallazgo existe sin evidencia. Todo resultado tiene fuente, timestamp, método y nivel de confianza.**

Esto no es una recomendación de UX. Es un requisito de datos. La plataforma rechaza hallazgos sin evidencia asociada.

### Aplicación por entidad

#### CVECorrelation — niveles de confianza

| Nivel | Condición | Ejemplo |
|---|---|---|
| `high` | CPE exacto del servicio hace match en NVD | Nmap devuelve `cpe:/a:openssh:openssh:8.2p1` |
| `medium` | Nombre + versión del servicio hace match | Nmap devuelve `OpenSSH 8.2p1` sin CPE |
| `low` | Sólo nombre del servicio, sin versión | Nmap devuelve `ssh`, sin versión detectable |

Los CVEs con confianza `low` se muestran **separados** en la UI con un aviso: "Correlación sin versión confirmada — verificación manual recomendada."

**Campos añadidos a CVECorrelation:**
```
confidence        ENUM(high, medium, low) NOT NULL
evidence_source   ENUM(nmap_cpe, nmap_version_string, manual_entry) NOT NULL
evidence_data     TEXT NOT NULL       — el string/CPE que generó la correlación
scan_job_id       UUID FK → ScanJob   — trazabilidad al scan origen
```

#### CheckResult — evidencia obligatoria

Regla: **no se puede marcar un check como `pass` o `fail` sin evidencia.**

- Estado `not_applicable` puede completarse sin evidencia, pero requiere justificación en `notes`.
- Estado `manual_review` puede completarse sin evidencia (pending).
- El backend rechaza `Complete Assessment` si algún check pass/fail tiene `evidence_text = NULL`.

**Campos de evidencia en CheckResult:**
```
evidence_type     ENUM(command_output, config_excerpt, file_content, screenshot_ref, manual_note) NOT NULL
evidence_text     TEXT NOT NULL (required for pass/fail)
evidence_at       TIMESTAMPTZ NOT NULL   — timestamp de cuando se recopiló
```

#### DiscoveredService — fuente siempre registrada

```
detection_method  ENUM(nmap_syn, nmap_version, nmap_script, manual_entry) NOT NULL
detection_at      TIMESTAMPTZ NOT NULL
```

### Por qué evidence-first importa

1. **Reportes defendibles:** Un auditor externo puede rastrear cada hallazgo hasta su fuente.
2. **Menos falsos positivos:** Un CVE `low` confidence se identifica antes de que genere ruido.
3. **Re-evaluación honesta:** No se puede marcar un check como "pass" si no hay evidencia del fix.
4. **Responsabilidad del analista:** Cada hallazgo tiene un `user_id` y un timestamp. No hay hallazgos anónimos.

---

## 8. Modelo de Entidades (actualizado)

Los cambios respecto a v0.2.0 son los campos de evidencia. El resto es estable.

### Diagrama de relaciones

```
User ──────────────────────────────── AuditEntry (append-only)
 │                                         │ references all
 │                                         ▼
 └─────► Asset ◄──────────────────── ScanJob
             │                           │
             │                           └──► DiscoveredService
             │                                    │
             │                                    └──► CVECorrelation (+ confidence, evidence)
             │
             └──► Assessment
                      │
                      └──► CheckResult (+ evidence_type, evidence_text, evidence_at)
                               │
                               └──► RemediationItem

 Asset ──► Report  (scope: single | group | org)
 T-01 ──► AIExplanation (cached, read-only, linked to CVE or CheckResult)
```

### Entidades nuevas o modificadas en v0.3.0

#### CVECorrelation (modificada)
```sql
-- Campos añadidos respecto a v0.2.0:
confidence        ENUM('high','medium','low')        NOT NULL DEFAULT 'medium'
evidence_source   ENUM('nmap_cpe','nmap_version_string','manual_entry') NOT NULL
evidence_data     TEXT                               NOT NULL
scan_job_id       UUID REFERENCES scan_jobs(id)
```

#### CheckResult (modificada)
```sql
-- Campos añadidos:
evidence_type     ENUM('command_output','config_excerpt','file_content',
                       'screenshot_ref','manual_note')    -- required for pass/fail
evidence_text     TEXT                                     -- required for pass/fail
evidence_at       TIMESTAMPTZ                              -- when evidence was collected
```

#### AIExplanation (nueva — MVP)
```sql
id                UUID PRIMARY KEY
context_type      ENUM('cve','cis_check')   NOT NULL
context_id        VARCHAR(100)              NOT NULL   -- CVE ID or check_id
asset_type        VARCHAR(50)               NOT NULL   -- contexto del asset (server/workstation/etc)
prompt_hash       VARCHAR(64)               NOT NULL   -- SHA-256 del prompt para cache lookup
response_text     TEXT                      NOT NULL
model_used        VARCHAR(50)               NOT NULL   -- e.g. 'claude-haiku-4-5-20251001'
cached            BOOLEAN                   DEFAULT false
created_at        TIMESTAMPTZ               NOT NULL
requested_by      UUID REFERENCES users(id) NOT NULL
```

---

## 9. Flujos de Usuario Clave (v0.3.0)

### Flujo 1: Discover — Primer scan con evidencia de confianza

```
Analyst → registra asset (IP, type, env, owner, auth_document)
        → Admin autoriza (status: authorized)
        → Analyst dispara Nmap TCP scan sobre asset autorizado
        → Scan completa → servicios guardados con detection_method + detection_at
        → "Correlate CVEs" → NVD lookup por CPE/versión
        → CVEs guardados CON nivel de confianza:
            · CVE-2023-38408  OpenSSH 8.2p1  [HIGH confidence — CPE match]
            · CVE-2021-41617  ssh service    [LOW confidence — no version]
        → UI distingue visualmente: HIGH en tabla principal, LOW en sección colapsada "Sin versión confirmada"
        → Analyst puede marcar LOW como false_positive o investigar manualmente

Evidencia mínima para Discover: scan_job con timestamps + detection_method por servicio
```

### Flujo 2: Evaluate — CIS Assessment con evidencia obligatoria

```
Analyst → nuevo Assessment (asset + benchmark)
        → Check "1.1.1 — Ensure /tmp is a separate partition"
          · Comando de auditoría: mount | grep /tmp
          · Analyst ejecuta en terminal del sistema auditado
          · Copia output → evidence_text: "tmpfs on /tmp type tmpfs (rw,nosuid,nodev,noexec)"
          · evidence_type: command_output
          → Marca: PASS

        → Check "1.4.1 — Ensure permissions on bootloader config are configured"
          · Analyst ejecuta: stat /boot/grub2/grub.cfg
          · Output: "-rw-------. 1 root root 6714 Jan 15 2026 /boot/grub2/grub.cfg"
          → Marca: PASS (evidence guardada)

        → Check "3.5.1 — Ensure DCCP is disabled"
          · No hay GRUB en este sistema → Check "N/A"
          · notes obligatorio: "Sistema sin GRUB tradicional, kernel hardening aplicado vía otro método"

        → "Complete Assessment" → backend valida que todos los pass/fail tienen evidence_text
        → Si algún check pass/fail sin evidencia → error: "Check 2.3.1 requiere evidencia antes de completar"
```

### Flujo 3: Prioritize — Score y cola de remediación

```
Assessment completado →
        Score calculado:
          Raw: 6/10 = 60%
          Weighted: (4 passed: 2 critical + 1 high + 1 medium) / (6 total applicable)
                    = (2×4 + 1×3 + 1×2) / (2×4 + 2×3 + 1×2 + 1×1) = 13/19 = 68.4%

        RemediationItems generados automáticamente para checks FAIL:
          ┌──────────────────────────────────────────────────────────────────┐
          │ [CRITICAL] 3.3.2 Ensure IPv6 router advertisements not accepted  │
          │ effort: minutes  status: open                                    │
          │ "Añadir net.ipv6.conf.all.accept_ra=0 en /etc/sysctl.d/99-cis..." │
          │ [AI Explain ▶]                                                   │
          ├──────────────────────────────────────────────────────────────────┤
          │ [HIGH]     1.6.1 Ensure core dumps are restricted                │
          │ effort: hours   status: open                                     │
          └──────────────────────────────────────────────────────────────────┘

        "AI Explain" en un item → llama AI Lite:
          Respuesta: "Este check asegura que el kernel no acepte anuncios de enrutadores IPv6...
                     El riesgo en un servidor de producción es [X]. El fix es [pasos concretos]."
          (Respuesta cacheada 24h por check_id + benchmark)
```

### Flujo 4: Remediate — Seguimiento de correcciones

```
SysAdmin recibe la lista de remediación (fuera de plataforma, via PDF o enlace)
        → Implementa correcciones

Analyst → Hardening > Remediation > actualiza items:
          · item "3.3.2" → status: in_progress, assigned_to: sysadmin@org
          · item "1.6.1" → status: resolved, resolution_notes: "sysctl config actualizado"

(Remediación NO se ejecuta desde la plataforma. La plataforma sólo registra el estado.)
```

### Flujo 5: Validate — Re-evaluación y delta

```
Analyst → Hardening > Assessments > Assessment anterior > "New Re-evaluation"
        → Pre-cargado con checks del assessment anterior (estados vacíos)
        → Re-evalúa únicamente los checks que fallaron (o todos, a su criterio)
        → Complete Assessment

Resultado:
        Score anterior: 60% / 68.4% (raw/weighted)
        Score actual:   80% / 85.2%
        Delta:          +20% / +16.8% ↑
        Checks newly passed: 3
        Checks still failing: 1
        ──────────────────────────
        AuditEntry: assessment.validation_completed
        RemediationItems de checks pasados → status: auto-resolved
```

### Flujo 6: CISO — Postura y drill-down controlado (V2)

```
CISO → Dashboard
     → "Posture Score: 74/100 ↑ +12 este mes" (número grande, verde)
     → Widgets: CVEs críticos abiertos (3), Assets en riesgo (2), Remediación (85% completado)
     → Trend chart: score de los últimos 6 assessments

     → Click en "CVEs críticos abiertos (3)"
       → Drill-down: "3 activos de producción" (nombres, sin IPs)
       → Descripción: "Vulnerabilidades en servicios de autenticación remota (riesgo: acceso no autorizado)"
       → [Solicitar reporte técnico] → notificación al Analyst responsable

     → "Generate Executive Report" → PDF sin raw data:
       · Resumen: postura actual + tendencia
       · Top 3 riesgos en lenguaje de negocio
       · Estado de remediación (% completado, MTTR)
       · Recomendaciones estratégicas
```

---

## 10. Métricas Clave

### Métricas de producto (¿se usa correctamente?)

| Métrica | Qué mide | Target MVP | Target V2 |
|---|---|---|---|
| Evidence completion rate | % assessments completados con 100% de checks con evidencia | 100% (enforced) | 100% |
| CVE confidence distribution | % CVEs HIGH vs MEDIUM vs LOW confidence | LOW < 20% | LOW < 10% |
| Scans/semana | Actividad de discovery | ≥ 5 | ≥ 20 |
| Assessments completados/semana | Actividad de evaluación | ≥ 2 | ≥ 10 |
| Re-evaluation rate | % assessments con al menos 1 re-evaluación | ≥ 30% (en 90 días) | ≥ 60% |
| Reports generados/semana | Actividad de reporting | ≥ 2 | ≥ 8 |

### Métricas de postura de seguridad (¿mejora el cliente?)

| Métrica | Descripción | Meta |
|---|---|---|
| MTTA | Tiempo desde registro de asset hasta primer assessment completado | < 7 días |
| MTTR Critical | Tiempo desde `status=open` (critical) hasta `resolved` | < 7 días |
| MTTR High | Tiempo desde `status=open` (high) hasta `resolved` | < 30 días |
| Hardening score trend | Score promedio trimestral por organización | ≥ +5% / trimestre |
| CVE backlog | CVEs open con severity ≥ high | Tendencia decreciente |
| % Critical CVEs acknowledged < 48h | Reconocimiento en menos de 48h | ≥ 80% |

### Métricas de plataforma (¿funciona bien?)

| Métrica | Target |
|---|---|
| Scan success rate | ≥ 95% |
| CVE false positive rate (user-reported) | < 5% |
| Report generation success rate | ≥ 99% |
| AI Lite response time (con cache hit) | < 500ms |
| AI Lite response time (sin cache) | < 5 segundos |
| API p95 latency (non-scan endpoints) | < 500ms |

---

## 11. Anti-Scope-Creep — Los 5 Filtros (actualizado)

Todo feature propuesto pasa por los 5 filtros en orden. Falla en cualquiera → rechazado.

```
FILTRO 1 — ¿Pertenece a uno de los 5 verbos del ciclo?
           Discover | Evaluate | Prioritize | Remediate | Validate
           ¿O es infraestructura que sostiene el ciclo?
           Si NO → rechazado.

FILTRO 2 — ¿Opera sobre activos autorizados?
           ¿Requiere registro previo del activo en la plataforma?
           ¿Introduce alguna capacidad ofensiva, aunque sea opcional?
           Si NO (activo) o SI (ofensiva) → rechazado.

FILTRO 3 — ¿Tiene un usuario nombrado con necesidad real?
           "El [rol] necesita [X] para poder [Y] en el paso [Z] del ciclo."
           "Podría ser útil" no es suficiente.
           Si no hay usuario nombrado → rechazado.

FILTRO 4 — ¿Es coherente con la fase actual?
           ¿Existen los datos que necesita?
           ¿Cabe en el sprint sin romper lo existente?
           Si NO → pasa a la fase correcta, no al sprint actual.

FILTRO 5 — ¿Respeta la taxonomía de módulos?
           ¿Cabe en un módulo existente o justifica uno nuevo?
           ¿Crea un tercer workspace?
           Si no cabe y no justifica → rechazado.
```

---

## 12. Product Guardrails

> Estos límites no son negociables. No los ajusta el cliente, no los sobreescribe un sprint, no los elimina la presión de tiempo.

### G-1: Activos Autorizados Únicamente
Todo escaneo activo, evaluación o acción sobre un sistema requiere que el activo esté registrado con `status = 'authorized'` en la base de datos. Este check ocurre en el backend, no en el frontend.

```python
# Invariante que NUNCA se omite — en toda función que opere sobre un asset
def require_authorized(asset: Asset) -> None:
    if asset.status != AssetStatus.AUTHORIZED:
        raise ForbiddenError(f"Asset {asset.id} is not authorized for active operations")
    audit.record(action="authorization_check.passed", asset_id=asset.id)
```

### G-2: Sin Explotación
La plataforma no implementa, no integra, no llama, ni orquesta ninguna técnica de explotación de vulnerabilidades. Correlacionar un CVE ≠ explotar ese CVE.

### G-3: Sin Movimiento Lateral
No hay features de descubrimiento de redes adyacentes, relays, enumeración de trusts, o cualquier técnica que atraviese el perímetro del asset registrado.

### G-4: Sin Autopwn
No existe modo de "ataque automático", "verificación de explotabilidad activa", ni encadenamiento de técnicas. La plataforma observa y evalúa. No ataca.

### G-5: Sin Auto-Remediación sin Validación Humana
La plataforma puede sugerir pasos de remediación. **No ejecuta ningún cambio en sistemas remotos.** Ninguna acción de corrección se dispara sin que un humano la apruebe explícitamente en su propio sistema.

### G-6: Evidencia Obligatoria
Ningún hallazgo se guarda sin evidencia asociada. Los campos `evidence_text` y `evidence_source` son `NOT NULL` para estados operacionales (pass/fail en checks; high/medium/low en CVEs).

### G-7: Audit Trail Inmutable
La tabla `audit_log` tiene:
- Política de BD: `REVOKE DELETE, UPDATE ON audit_log FROM ALL`
- Esquema de base de datos separado con permisos más restrictivos
- El Admin puede **leer** el audit log pero no modificarlo

### G-8: IA Read-Only
El módulo AI Assist no puede:
- Crear entidades en la base de datos
- Disparar scans ni assessments
- Modificar el estado de cualquier hallazgo
- Acceder a internet o llamar APIs externas

La IA recibe contexto estructurado de la plataforma y devuelve texto explicativo. Nada más.

### G-9: Datos Sensibles no se Exportan Implícitamente
Los reportes del CISO no incluyen IPs, versiones de software, banners de servicio, ni CVE IDs. Un reporte técnico requiere acción explícita de un Analyst, con AuditEntry generado.

---

## 13. Definition of Done — MVP

El MVP se declara completo cuando **todos** los criterios siguientes son verificables:

### Funcionales

| # | Criterio | Cómo se verifica |
|---|---|---|
| F-1 | Un nuevo usuario puede registrarse, autenticarse y recibir un rol en < 5 minutos | Test de onboarding manual + test de integración |
| F-2 | Un Analyst puede registrar un asset y que un Admin lo autorice en < 2 clics | Test de flujo manual |
| F-3 | Un scan TCP sobre un asset autorizado completa en < 60 segundos para un host único | Test funcional con host controlado |
| F-4 | La correlación de CVEs retorna resultados con nivel de confianza correcto | Test con CPE conocido + servicio sin versión |
| F-5 | Un assessment CIS de 10 checks rechaza la finalización si algún pass/fail carece de evidencia | Test unitario del endpoint `POST /assessments/:id/complete` |
| F-6 | El score ponderado se calcula correctamente (fórmula: suma(passed × weight) / suma(applicable × weight)) | Test unitario del scoring engine con casos conocidos |
| F-7 | Un reporte PDF técnico genera en < 30 segundos con datos correctos | Test funcional + validación del contenido del PDF |
| F-8 | Una re-evaluación calcula el delta correcto respecto al assessment anterior | Test de integración con 2 assessments del mismo asset |
| F-9 | AI Lite responde a `explain_cve` y `explain_check` con texto coherente y defensivo | Test manual + verificación de system prompt restrictivo |
| F-10 | El rate limit de AI Lite rechaza la 6ª solicitud en la misma hora del mismo usuario | Test automatizado |

### Seguridad y Gobernanza

| # | Criterio | Cómo se verifica |
|---|---|---|
| S-1 | Todos los endpoints de la API retornan 401 sin token válido | Test automatizado de seguridad (pytest + httpx) |
| S-2 | El endpoint de scan retorna 403 si el asset tiene `status != authorized` | Test unitario del guardrail G-1 |
| S-3 | El 100% de las acciones de scan, assessment, autorización y reporte generan AuditEntry | Test de integración: verificar audit_log tras cada acción |
| S-4 | La tabla `audit_log` no puede recibir UPDATE ni DELETE desde la aplicación | Test de permisos de BD (pgTest o equivalente) |
| S-5 | El AI Assist no puede modificar ninguna entidad de la BD | Revisión de código del servicio AI + test de surface attack |
| S-6 | Zero vulnerabilidades críticas o altas en dependencias Python y Node.js | `pip-audit` + `npm audit` en CI con umbral de fallo |

### Calidad

| # | Criterio | Cómo se verifica |
|---|---|---|
| Q-1 | Cobertura de tests del backend ≥ 70% en módulos core (no en main.py ni config) | `pytest --cov` en CI |
| Q-2 | Todos los endpoints tienen schema de validación Pydantic y retornan 422 en input inválido | Test automatizado de validación |
| Q-3 | El Docker Compose levanta todos los servicios con un único `docker compose up` en un entorno limpio | Test de smoke en CI |
| Q-4 | El OpenAPI (Swagger) en `/docs` documenta correctamente todos los endpoints | Revisión manual |

---

## 14. Failure Modes

Cómo el producto puede degenerar y cómo evitarlo.

### FM-1: Deriva Ofensiva ("sólo un módulo más")

**Cómo ocurre:** Alguien propone añadir "verificación de explotabilidad" para distinguir CVEs teóricos de CVEs reales. Parece razonable. Es el primer paso.

**Consecuencia:** La plataforma se convierte en una herramienta de explotación con capa defensiva encima.

**Prevención:**
- Filtro 2 del anti-scope-creep es obligatorio y binario
- Cualquier feature que "verifica" algo en el sistema remoto (más allá de leer puertos abiertos) requiere aprobación del responsable de seguridad con justificación escrita
- El Product Guardrail G-2 es no negociable

---

### FM-2: Evidence Theater ("marcar sin revisar")

**Cómo ocurre:** Los analistas, bajo presión de tiempo, copian outputs genéricos en el campo de evidencia sin verificar realmente el check. Los scores suenan bien, la realidad es distinta.

**Consecuencia:** Los reportes generan falsa confianza. El CISO cree que el hardening está en 85%. Está en 40%.

**Prevención:**
- Evidence es obligatoria pero no garantiza que sea correcta; la responsabilidad es del analista
- Los assessments deben mostrar `completed_by` + `completed_at` de forma prominente
- Los re-assessments permiten detectar inconsistencias (check pasa en assessment A, falla en B sin cambio conocido)
- El Audit Log registra quién marcó qué y cuándo

---

### FM-3: CVE Flooding ("demasiados hallazgos, cero remediación")

**Cómo ocurre:** El sistema encuentra 200 CVEs por host. El analista no puede priorizar. Todo queda "open". El backlog crece.

**Consecuencia:** La plataforma genera ansiedad, no claridad. Los usuarios dejan de usarla.

**Prevención:**
- Los CVEs con confianza `low` se colapsan por defecto en la UI
- La vista principal muestra sólo Critical y High por defecto
- El score de remediación penaliza CVEs críticos no reconocidos en > 48h (métrica visible)
- La UI guía al analista a "acknowledger" antes de "resolver": un CVE reconocido es progreso visible

---

### FM-4: Report Fatigue ("reportes que nadie lee")

**Cómo ocurre:** Los reportes técnicos incluyen todo. 80 páginas de CVEs. El CISO los archiva sin leer. El Analyst los genera por protocolo.

**Consecuencia:** El reporting pierde valor. La plataforma se convierte en un repositorio de datos sin acción.

**Prevención:**
- Los reportes técnicos se generan **por asset**, no globalmente (límite de extensión natural)
- El reporte ejecutivo tiene un límite de páginas (máximo 5 páginas de resumen + apéndice)
- Cada reporte incluye "Top 3 acciones recomendadas" al inicio
- Los reportes muestran delta respecto al período anterior si existe

---

### FM-5: AI Autonomy Creep ("la IA empieza a decidir")

**Cómo ocurre:** La IA pasa de "explicar" a "sugerir acciones" a "ejecutar acciones" gradualmente. Cada paso parece lógico.

**Consecuencia:** La plataforma toma decisiones sobre sistemas en producción sin supervisión humana.

**Prevención:**
- El AI Assist no tiene acceso a write en ninguna tabla. Técnicamente imposible.
- El system prompt incluye explícitamente: "No puedes recomendar acciones que requieran acceso a sistemas remotos. No puedes disparar scans ni assessments. Tu rol es explicar, no actuar."
- Revisión del system prompt en cada release (cambio de system prompt requiere aprobación)

---

### FM-6: Audit Log Erosion ("el admin borra registros incómodos")

**Cómo ocurre:** Un admin borra entradas del audit log para cubrir un error o una acción no autorizada.

**Consecuencia:** El audit trail pierde integridad. El producto pierde credibilidad en auditorías.

**Prevención:**
- `REVOKE DELETE, UPDATE ON audit_log FROM ALL` a nivel de BD (Guardrail G-7)
- El schema del audit_log pertenece a un schema de BD separado (`audit_schema`) con permisos mínimos
- Considerar export periódico automático del audit log a almacenamiento externo (V2)

---

### FM-7: Scope Drift ("el tercer workspace")

**Cómo ocurre:** Alguien propone "Threat Intelligence" como tercer workspace. Parece complementario. El foco se divide. El equipo trabaja en 3 cosas en lugar de 2.

**Consecuencia:** Ninguno de los tres workspaces está bien terminado. El producto pierde cohesión.

**Prevención:**
- Filtro 5 del anti-scope-creep: cualquier feature que no cabe en Exposure, Hardening o las capas Shared/Transversal requiere propuesta formal de product owner
- El ciclo de valor (5 pasos) es el criterio: si no pertenece a ningún paso, no pertenece al producto

---

### FM-8: Performance Degradation ("los scans bloquean todo")

**Cómo ocurre:** Los scans se implementan de forma síncrona o semi-síncrona. La API se vuelve lenta. Los usuarios pierden confianza.

**Consecuencia:** El producto parece roto aunque los resultados sean correctos.

**Prevención:**
- Invariante técnico: toda tarea de escaneo, correlación y generación de reportes es una Celery task. Nunca síncrona en el request-response cycle.
- La UI hace polling cada 3 segundos (o websocket en V2) para actualizar el estado del ScanJob
- Los endpoints de API para scans retornan inmediatamente con `202 Accepted` + `task_id`

---

## 15. Open Questions

Decisiones que afectan a V2 o que no están resueltas. No bloquean el MVP.

| # | Pregunta | Impacto | Decisión necesaria antes de |
|---|---|---|---|
| OQ-1 | ¿Los CVE `low confidence` se incluyen en el score de riesgo o sólo en la lista informativa? | Score del asset, severidad percibida | V2 |
| OQ-2 | ¿Cómo se gestiona el conflicto entre CVSS NVD y CVSS del vendor (e.g., RedHat Score)? | Confianza en el dato de severidad | V2 |
| OQ-3 | ¿Una re-evaluación puede ser parcial (sólo checks fallidos) o siempre requiere todos los checks? | UX del validation tracker | V2 |
| OQ-4 | ¿Las explicaciones del AI Lite se almacenan permanentemente o se purgan a los 30 días? | Storage, privacidad del contexto del asset | Antes de go-live MVP |
| OQ-5 | ¿El CISO puede solicitar un reporte técnico completo "con un click"? ¿O siempre requiere mediación del Analyst? | Flujo del rol CISO | V2 |
| OQ-6 | ¿Qué ocurre si el scan de Nmap falla parcialmente (timeout en algunos puertos)? ¿Se guarda el resultado parcial? | Completitud de datos, UI de resultados | MVP (antes de shipping) |
| OQ-7 | ¿El campo `auth_document` es una referencia libre (string URL) o debe existir en la plataforma como entidad? | Trazabilidad de autorización | V2 (en MVP: string libre) |
| OQ-8 | ¿Los assessments se pueden archivar o sólo se desactivan? ¿Cuánto tiempo se retienen los checks con evidencia? | Storage, compliance, retención | V3 o política de despliegue |

---

## Apéndice: Navegación del Producto

```
/login

/dashboard              [V2] → [MVP: redirige a /exposure/assets]

├── /exposure
│   ├── /assets                  Lista de activos (filtros: estado, tipo, env, owner)
│   │   ├── /new                 Registrar activo
│   │   └── /:id
│   │       ├── /overview        Info + último scan + score + estado
│   │       ├── /services        Servicios descubiertos | trigger scan
│   │       │                    [HIGH confidence CVEs inline] [LOW confidence colapsados]
│   │       ├── /cves            CVEs correlacionados | filtro por severidad + confianza
│   │       └── /reports         Reportes de este activo
│   └── /surface                 [V2] Vista de riesgo agregada
│
├── /hardening
│   ├── /assessments             Lista (filtro: asset, benchmark, estado)
│   │   ├── /new
│   │   └── /:id
│   │       ├── /checks          Checklist + evidence input obligatorio
│   │       ├── /score           Score raw + weighted + breakdown
│   │       └── /remediation     Cola priorizada | AI Explain por item
│   ├── /scores                  Score por asset + [V2: tendencia]
│   └── /remediation             Cola global todos los assets
│
├── /reports
│   └── /history                 Historial con descarga + hash
│
└── /settings                    [Admin only]
    ├── /users
    ├── /audit-log               Read-only, no delete
    └── /integrations            [V3]
```

## Apéndice: Sistema de Color y UX

```
Severidades — paleta fija, nunca varía entre pantallas:
  Critical  #DC2626 (red-600)    ⬤ crítico
  High      #EA580C (orange-600) ▲ alto
  Medium    #CA8A04 (yellow-600) ◆ medio
  Low       #2563EB (blue-600)   ▼ bajo
  Pass      #16A34A (green-600)  ✓ correcto
  Info      #6B7280 (gray-500)   ℹ informativo

Confidence badges (nuevo en v0.3.0):
  High conf   #16A34A + "Verified"      → CPE match
  Med conf    #CA8A04 + "Unverified"    → version string match
  Low conf    #6B7280 + "Unconfirmed"   → service name only

Tipografía:
  Datos técnicos (IPs, CVE IDs, puertos, hashes): JetBrains Mono / Fira Code
  UI general: Inter / Geist
  Dark mode: desde el primer día, CSS variables, no afterthought

Tablas: siempre con ordenación, filtro, búsqueda, export CSV, paginación server-side
Scans: feedback async con polling 3s (MVP) o websocket (V2)
Empty states: siempre con CTA accionable
Acciones destructivas: siempre con modal de confirmación que describe lo que ocurrirá
```

---

*Documento canónico del diseño de producto. Toda decisión de arquitectura, UX o features debe ser coherente con este documento. Versión 0.3.0 — revisión prevista al inicio de Fase 1 (MVP development).*
