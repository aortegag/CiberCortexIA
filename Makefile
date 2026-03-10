# CiberCortex IA — Makefile
# Uso: make <target>
# Requiere: docker compose v2, python 3.12+, node 20+

.PHONY: help up down build logs \
        migrate seed shell-api shell-db \
        dev-backend dev-frontend \
        test lint format \
        prod-up prod-build \
        clean nuke

COMPOSE        = docker compose
COMPOSE_PROD   = docker compose -f docker-compose.yml -f docker-compose.prod.yml
BACKEND_DIR    = ./backend
FRONTEND_DIR   = ./frontend

# ── Ayuda ─────────────────────────────────────────────────────────────────────
help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS=":.*## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Desarrollo (stack completo) ───────────────────────────────────────────────
up: ## Levantar stack completo (db + redis + api + frontend)
	$(COMPOSE) up

up-worker: ## Levantar stack con Celery worker
	$(COMPOSE) --profile worker up

up-nginx: ## Levantar stack con nginx (puerto 80)
	$(COMPOSE) --profile nginx up

down: ## Detener todos los servicios
	$(COMPOSE) down

build: ## Reconstruir todas las imágenes
	$(COMPOSE) build --no-cache

build-api: ## Reconstruir solo la imagen del backend
	$(COMPOSE) build --no-cache api

build-frontend: ## Reconstruir solo la imagen del frontend
	$(COMPOSE) build --no-cache frontend

logs: ## Ver logs de todos los servicios (follow)
	$(COMPOSE) logs -f

logs-api: ## Ver logs solo del backend
	$(COMPOSE) logs -f api

logs-worker: ## Ver logs del Celery worker
	$(COMPOSE) logs -f worker

# ── Base de datos ─────────────────────────────────────────────────────────────
migrate: ## Ejecutar migraciones Alembic (alembic upgrade head)
	$(COMPOSE) --profile migrate run --rm migrate

migrate-new: ## Crear nueva migración (NAME=nombre_de_la_migracion)
	@cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(NAME)"

migrate-history: ## Ver historial de migraciones
	@cd $(BACKEND_DIR) && alembic history --verbose

migrate-downgrade: ## Revertir última migración
	@cd $(BACKEND_DIR) && alembic downgrade -1

seed: ## Crear usuario admin inicial (requiere DB activa)
	$(COMPOSE) --profile seed run --rm seed

shell-api: ## Shell interactivo en el contenedor del backend
	$(COMPOSE) exec api /bin/sh

shell-db: ## psql interactivo en la base de datos
	$(COMPOSE) exec db psql -U $${DB_USER:-cybercortex} -d $${DB_NAME:-cybercortex}

shell-redis: ## redis-cli interactivo
	$(COMPOSE) exec redis redis-cli

# ── Desarrollo local (sin Docker) ────────────────────────────────────────────
dev-backend: ## Levantar backend FastAPI en modo desarrollo (sin Docker)
	@cd $(BACKEND_DIR) && \
	  pip install -r requirements.txt -r requirements-dev.txt -q && \
	  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Levantar frontend Next.js en modo desarrollo (sin Docker)
	@cd $(FRONTEND_DIR) && \
	  npm install && \
	  npm run dev

dev-worker: ## Levantar Celery worker en modo desarrollo (sin Docker)
	@cd $(BACKEND_DIR) && \
	  celery -A app.services.task_manager worker --loglevel=info --concurrency=2

# ── Tests ─────────────────────────────────────────────────────────────────────
test: ## Ejecutar suite de tests del backend
	@cd $(BACKEND_DIR) && pytest -v --tb=short

test-cov: ## Tests con cobertura HTML
	@cd $(BACKEND_DIR) && pytest --cov=app --cov-report=html --cov-report=term-missing

test-frontend: ## Tests del frontend
	@cd $(FRONTEND_DIR) && npm test

# ── Calidad de código ─────────────────────────────────────────────────────────
lint: ## Linting Python (ruff) + TypeScript (next lint)
	@cd $(BACKEND_DIR) && ruff check app/ tests/
	@cd $(FRONTEND_DIR) && npm run lint

format: ## Formatear código Python (ruff format) + TypeScript (prettier)
	@cd $(BACKEND_DIR) && ruff format app/ tests/
	@cd $(FRONTEND_DIR) && npm run format 2>/dev/null || true

typecheck: ## Type checking TypeScript
	@cd $(FRONTEND_DIR) && npm run build -- --no-lint

# ── Producción ────────────────────────────────────────────────────────────────
prod-build: ## Build de imágenes para producción
	$(COMPOSE_PROD) build

prod-up: ## Levantar stack en modo producción
	$(COMPOSE_PROD) up -d

prod-migrate: ## Migraciones en producción
	$(COMPOSE_PROD) --profile migrate run --rm migrate

# ── Limpieza ──────────────────────────────────────────────────────────────────
clean: ## Eliminar contenedores y redes (preserva volúmenes)
	$(COMPOSE) down --remove-orphans

nuke: ## ⚠️  Eliminar TODO incluyendo volúmenes (DESTRUYE DATOS)
	@echo "ADVERTENCIA: Esto elimina todos los datos de la BD. Escribe 'SI' para confirmar:"
	@read confirm && [ "$$confirm" = "SI" ] || (echo "Cancelado." && exit 1)
	$(COMPOSE) down --volumes --remove-orphans

# ── Entorno ───────────────────────────────────────────────────────────────────
env: ## Copiar .env.example a .env (si no existe)
	@test -f .env && echo ".env ya existe, no se sobrescribe." || \
	  (cp .env.example .env && echo ".env creado desde .env.example — edítalo antes de levantar.")

status: ## Estado de todos los contenedores
	$(COMPOSE) ps

health: ## Verificar health del backend
	@curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
