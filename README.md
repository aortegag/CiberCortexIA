# CiberCortex IA

**Defensive cybersecurity platform — Exposure & Hardening workspaces.**

> Discover → Evaluate → Prioritize → Remediate → Validate

---

## Quick Start (Phase 0)

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env with your values

# 2. Start services
docker compose up

# 3. Verify
curl http://localhost:8000/api/v1/health
# → {"status": "ok", "version": "0.1.0", "checks": {"database": "ok", "redis": "ok"}}
```

## Stack

| Layer | Technology |
|---|---|
| API | Python 3.12 + FastAPI (async) |
| Database | PostgreSQL 16 + SQLAlchemy async + Alembic |
| Queue | Celery + Redis 7 |
| Frontend | Next.js 14 + TypeScript + shadcn/ui (Sprint 4) |
| AI | Anthropic claude-haiku-4-5 (Phase 2 MVP, read-only) |

## Documentation

- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) — Product definition
- [`docs/MVP_SCOPE.md`](docs/MVP_SCOPE.md) — What's in/out of MVP
- [`docs/SAFETY_GUARDRAILS.md`](docs/SAFETY_GUARDRAILS.md) — Hard limits
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — System design + ADRs
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — 4-phase roadmap
- [`docs/PRODUCT_DESIGN.md`](docs/PRODUCT_DESIGN.md) — Product design v0.3.0
- [`docs/UX_DESIGN.md`](docs/UX_DESIGN.md) — UX system + wireframes

## Development

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt

# Linting
ruff check app/ && ruff format app/

# Tests
pytest

# Migrations
alembic upgrade head
```

## Safety Contract

This platform is **defensive only**. No exploit generation, no C2, no offensive payloads.
See [`docs/SAFETY_GUARDRAILS.md`](docs/SAFETY_GUARDRAILS.md).
