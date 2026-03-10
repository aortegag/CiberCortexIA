# CiberCortex IA

**Plataforma de ciberseguridad defensiva — workspaces Exposure & Hardening.**

> Discover → Evaluate → Prioritize → Remediate → Validate

---

## Inicio rápido

```bash
# 1. Copiar variables de entorno
make env
# Edita .env antes de continuar (SECRET_KEY, ANTHROPIC_API_KEY, etc.)

# 2. Levantar stack completo (db + redis + api + frontend)
make up

# 3. Ejecutar migraciones
make migrate

# 4. Crear usuario admin inicial
make seed

# 5. Abrir la plataforma
open http://localhost:3000
# Usuario: admin@cibercortex.local  |  Contraseña: CiberCortex2024!
```

---

## Stack

| Capa | Tecnología |
|------|-----------|
| API | Python 3.12 + FastAPI (async) |
| Base de datos | PostgreSQL 16 + SQLAlchemy async + Alembic |
| Cola de tareas | Celery + Redis 7 |
| Frontend | Next.js 14 + TypeScript + Tailwind + shadcn/ui |
| AI Assist | Anthropic claude-haiku-4-5 (solo lectura, defensivo) |
| Proxy | Nginx 1.25 |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx (:80)                         │
│          /api/v1/* → backend:8000                           │
│          /*         → frontend:3000                         │
└────────────────────┬────────────────┬───────────────────────┘
                     │                │
          ┌──────────▼──────┐  ┌──────▼───────────┐
          │  FastAPI :8000  │  │  Next.js :3000   │
          │  Python 3.12    │  │  TypeScript      │
          └────────┬────────┘  └──────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
  ┌─────▼────┐  ┌──▼───┐  ┌──▼──────────┐
  │ Postgres │  │Redis │  │Celery Worker│
  │    :5432 │  │:6379 │  │  (scans/PDF)│
  └──────────┘  └──────┘  └─────────────┘
```

---

## Comandos Makefile

```bash
make help          # Ver todos los comandos disponibles

# Desarrollo
make up            # Stack completo
make up-worker     # Stack + Celery worker
make up-nginx      # Stack + Nginx en puerto 80
make down          # Detener todo
make logs          # Logs en tiempo real
make logs-api      # Logs solo del backend

# Base de datos
make migrate       # Ejecutar migraciones pendientes
make migrate-new NAME=nombre    # Nueva migración Alembic
make seed          # Crear usuario admin
make shell-db      # psql interactivo
make shell-api     # Shell en contenedor backend

# Calidad de código
make lint          # Python (ruff) + TypeScript (next lint)
make format        # Formatear código
make test          # Tests del backend
make test-cov      # Tests con cobertura HTML

# Producción
make prod-build    # Build optimizado
make prod-up       # Levantar en producción
```

---

## Estructura del proyecto

```
CiberCortexIA/
├── backend/                    # FastAPI + Python
│   ├── app/
│   │   ├── api/v1/             # Endpoints REST
│   │   ├── core/               # Config, DB, seguridad, deps
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── modules/            # Lógica de dominio (exposure, hardening, ai)
│   │   └── main.py             # Punto de entrada FastAPI
│   ├── migrations/             # Alembic migrations
│   ├── tests/                  # pytest
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Next.js 14 + TypeScript
│   ├── src/
│   │   ├── app/                # App Router (rutas)
│   │   │   ├── (auth)/login/   # Login
│   │   │   └── (app)/          # Rutas autenticadas
│   │   │       ├── dashboard/
│   │   │       ├── assets/
│   │   │       ├── exposure/
│   │   │       ├── hardening/
│   │   │       ├── reports/
│   │   │       └── ai/
│   │   ├── components/         # UI components
│   │   ├── lib/                # API client, utils
│   │   ├── stores/             # Zustand (auth)
│   │   ├── hooks/              # useAuth
│   │   └── types/              # TypeScript types
│   └── Dockerfile
│
├── infrastructure/
│   └── nginx/nginx.conf        # Reverse proxy config
│
├── scripts/
│   └── seed.py                 # Seed usuario admin
│
├── docs/                       # Documentación del producto
├── docker-compose.yml          # Stack completo
├── Makefile                    # Comandos de desarrollo
└── .env.example                # Template de variables
```

---

## Módulos MVP

| ID | Módulo | Ruta |
|----|--------|------|
| S-01 | Platform Core (Auth + RBAC) | `/login` |
| S-02 | Asset Registry | `/assets` |
| E-01 | Exposure Analysis | `/exposure` |
| E-02 | CVE Correlation | `/exposure` + `/assets/[id]` |
| H-01 | CIS Assessment | `/hardening/assessments` |
| H-02 | Scoring & Remediation | `/hardening` |
| T-01 | Report Engine (PDF) | `/reports` |
| T-02 | AI Assist Lite | `/ai` |

---

## Roles

| Rol | Permisos |
|-----|---------|
| `admin` | Todo: gestión de usuarios + todas las acciones |
| `analyst` | Crear activos, ejecutar escaneos, crear assessments, generar reportes |
| `readonly` | Solo lectura de todos los datos |

---

## Contrato de seguridad

Esta plataforma es **exclusivamente defensiva**.

- ✅ Análisis de vulnerabilidades y compliance
- ✅ Correlación CVE y priorización de remediación
- ✅ AI Assist explicativo (solo lectura)
- ❌ Sin generación de exploits
- ❌ Sin payloads ofensivos ni C2
- ❌ Sin auto-remediación
- ❌ Solo activos con `status=authorized` pueden ser escaneados

Ver [`docs/SAFETY_GUARDRAILS.md`](docs/SAFETY_GUARDRAILS.md) para el detalle normativo.

---

## Documentación

- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) — Definición del producto
- [`docs/MVP_SCOPE.md`](docs/MVP_SCOPE.md) — Alcance del MVP
- [`docs/SAFETY_GUARDRAILS.md`](docs/SAFETY_GUARDRAILS.md) — Límites de seguridad
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura + ADRs
- [`docs/PRODUCT_DESIGN.md`](docs/PRODUCT_DESIGN.md) — Diseño de producto v0.3.0
- [`docs/UX_DESIGN.md`](docs/UX_DESIGN.md) — Sistema de diseño UX
