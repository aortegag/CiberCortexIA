# CiberCortex IA — Architecture

**Version:** 0.1.0
**Date:** 2026-03-10

---

## 1. Visión General

CiberCortex IA sigue una arquitectura **API-first, modular y event-driven** para tareas de larga duración (scans). El frontend y el backend están completamente desacoplados. Los módulos de Exposure y Hardening son independientes entre sí, compartiendo únicamente el modelo de Asset.

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│              Next.js + TypeScript + shadcn/ui               │
│  ┌──────────────────┐        ┌──────────────────────────┐   │
│  │  Workspace:       │        │  Workspace:              │   │
│  │  Exposure         │        │  Hardening               │   │
│  └──────────────────┘        └──────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS / REST API
┌───────────────────────▼─────────────────────────────────────┐
│                     BACKEND API                             │
│                   FastAPI (Python)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Auth /  │  │ Exposure │  │Hardening │  │  Reports │   │
│  │  RBAC    │  │  Module  │  │  Module  │  │  Module  │   │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│                     │             │              │          │
│  ┌──────────────────▼─────────────▼──────────────▼──────┐  │
│  │              Shared Services Layer                    │  │
│  │  Assets DB  │  Audit Log  │  Task Manager  │  AI Svc  │  │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌──────────┐ ┌──────────────────┐
│  PostgreSQL   │ │  Redis   │ │  External APIs   │
│  (main store) │ │(cache +  │ │  NVD / OpenSCAP  │
│               │ │  queue)  │ │  Claude API      │
└───────────────┘ └──────────┘ └──────────────────┘
        ▲
        │
┌───────────────┐
│ Celery Worker │  ← Executes Nmap, OpenSCAP, NVD queries
│ (async tasks) │
└───────────────┘
```

---

## 2. Capas de la Arquitectura

### 2.1 Frontend — Next.js App

- **Routing**: App Router (Next.js 14+)
- **Estado**: React Query para server state; Zustand para UI state
- **UI**: shadcn/ui + Tailwind CSS
- **Auth**: Token JWT almacenado en httpOnly cookie
- **Estructura por workspace** (no por tipo de componente):

```
frontend/src/
├── app/
│   ├── (auth)/login/
│   ├── (dashboard)/
│   │   ├── exposure/
│   │   │   ├── assets/
│   │   │   ├── discovery/
│   │   │   └── reports/
│   │   └── hardening/
│   │       ├── assessments/
│   │       ├── scores/
│   │       └── remediation/
├── components/
│   ├── ui/           ← shadcn primitives
│   ├── shared/       ← Componentes comunes (DataTable, StatusBadge)
│   └── charts/       ← Recharts wrappers
└── lib/
    ├── api/          ← Typed API client (fetch wrappers)
    └── auth/         ← Auth helpers
```

### 2.2 Backend API — FastAPI

- **Estructura por módulo** (domain-driven):

```
backend/app/
├── api/v1/
│   ├── auth.py
│   ├── assets.py
│   ├── exposure/
│   │   ├── discovery.py
│   │   ├── cve.py
│   │   └── reports.py
│   └── hardening/
│       ├── assessments.py
│       ├── scores.py
│       └── remediation.py
├── core/
│   ├── config.py        ← Settings (pydantic-settings)
│   ├── security.py      ← JWT, password hashing
│   ├── audit.py         ← Audit log service
│   └── database.py      ← SQLAlchemy engine + session
├── modules/
│   ├── exposure/
│   │   ├── scanner.py   ← Nmap wrapper (async, task-based)
│   │   ├── nvd_client.py← NVD API client
│   │   └── surface.py   ← Attack surface analysis logic
│   └── hardening/
│       ├── cis_checks.py← CIS check definitions + evaluator
│       ├── scap.py      ← OpenSCAP integration (Fase 2)
│       └── scorer.py    ← Score calculation engine
├── models/              ← SQLAlchemy ORM models
├── schemas/             ← Pydantic request/response schemas
└── services/
    ├── ai_advisor.py    ← Claude API integration
    ├── report_gen.py    ← PDF/DOCX report generation
    └── task_manager.py  ← Celery task definitions
```

### 2.3 Base de Datos — PostgreSQL

**Tablas principales:**

```sql
-- Core
assets (id, name, ip, hostname, type, os, status, owner, auth_scope, created_at)
users (id, email, hashed_password, role, is_active, created_at)
audit_log (id, timestamp, user_id, action, resource_type, resource_id, details)

-- Exposure
scan_jobs (id, asset_id, type, status, started_at, finished_at, celery_task_id)
discovered_services (id, scan_job_id, port, protocol, service, version, banner)
cve_correlations (id, asset_id, cve_id, cvss_score, cvss_vector, software, version)

-- Hardening
assessments (id, asset_id, analyst_id, benchmark, version, date, score, status)
check_results (id, assessment_id, check_id, title, status, notes)
remediation_items (id, check_result_id, priority, recommendation, resolved_at)

-- Reporting
reports (id, asset_id, type, generated_by, generated_at, file_path, hash)
```

### 2.4 Task Queue — Celery + Redis

Tasks asíncronas para operaciones de larga duración:

| Task | Tiempo estimado | Prioridad |
|---|---|---|
| `run_nmap_scan` | 30s – 5min | alta |
| `correlate_cves` | 5s – 30s | media |
| `generate_report` | 5s – 30s | media |
| `run_oscap_scan` | 2min – 15min | baja (Fase 2) |

### 2.5 AI Service — Claude API

- **Uso**: Sólo en endpoints de `/hardening/remediation/explain` y `/exposure/cve/explain`
- **Patrón**: El servicio construye el prompt con contexto estructurado del asset y el CVE/check, llama a Claude API, y retorna explicación + pasos.
- **Rate limiting**: Máximo 10 llamadas/minuto por usuario para evitar costos descontrolados.
- **No streaming en MVP**: Respuesta completa, sin streaming.

```python
# Patrón del servicio AI
async def explain_cve(asset: Asset, cve: CVECorrelation) -> AIExplanation:
    prompt = build_cve_prompt(asset, cve)  # Structured, sanitized
    response = await claude_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT_DEFENSIVE_ONLY,  # Restricciones hard-coded
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_ai_response(response)
```

---

## 3. Flujos Principales

### 3.1 Flujo: Exposure Discovery

```
Analyst → [Register Asset] → Asset DB (status: authorized)
       → [Trigger Scan]    → API validates auth → Celery task queued
       → [Task executes]   → Nmap runs → Results saved to discovered_services
       → [CVE Correlation] → NVD API queried per service/version
       → [View Results]    → Frontend fetches asset detail with services + CVEs
```

### 3.2 Flujo: Hardening Assessment

```
Analyst → [New Assessment] → Select asset + benchmark (CIS L1)
       → [Fill Checks]    → Pass/Fail per check item
       → [Calculate Score]→ Backend calculates % + priority list
       → [View Report]    → Score + failed checks + remediation list
       → [AI Explain]     → Per check: AI explains risk + correction steps
       → [Re-evaluate]    → New assessment logged, trend visible
```

### 3.3 Flujo: Report Generation

```
Analyst → [Generate Report] → Select asset(s) + template (technical/executive)
       → [Task queued]     → Report service fetches all relevant data
       → [PDF generated]   → Stored with hash, metadata in DB
       → [Download]        → Signed URL or direct download
```

---

## 4. Decisiones Arquitectónicas (ADRs)

| # | Decisión | Alternativa considerada | Razón |
|---|---|---|---|
| 1 | FastAPI sobre Django | Flask, Django REST | Async nativo, tipado con Pydantic, performance |
| 2 | PostgreSQL sobre MongoDB | MongoDB | ACID crítico para audit log; relaciones entre assets |
| 3 | Celery+Redis para tasks | Dramatiq, RQ | Ecosistema maduro, integración con FastAPI probada |
| 4 | Next.js sobre Vue/SvelteKit | Astro, Remix | Ecosistema enterprise, shadcn/ui, TypeScript nativo |
| 5 | Claude API para IA | GPT-4, Mistral | Capacidades de seguimiento de instrucciones, restricciones de seguridad |
| 6 | Módulos por dominio | Capas horizontales | Cohesión de negocio, independencia de deployment futuro |

---

## 5. Consideraciones de Seguridad de la Plataforma

- **CORS**: Origen explícito, no wildcard
- **Input validation**: Pydantic en todos los endpoints
- **SQL injection**: ORM siempre, queries raw prohibidas salvo casos documentados
- **Rate limiting**: FastAPI-Limiter en endpoints de scan y auth
- **Dependency scanning**: pip-audit y npm audit en CI
- **Secrets management**: Variables de entorno, nunca hardcoded. .env.example documentado.
- **Container security**: Non-root user en Dockerfiles, imágenes slim

---

*Arquitectura sujeta a revisión al inicio de cada fase.*
