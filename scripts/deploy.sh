#!/usr/bin/env bash
# CiberCortex IA — Script de deploy en VPS/servidor Linux
# Uso: ./scripts/deploy.sh [--skip-build] [--env-file /ruta/.env]
#
# Requisitos:
#   - Docker + Docker Compose v2
#   - Archivo .env configurado en la raíz del proyecto
#   - Usuario con permisos de docker (grupo docker o sudo)

set -euo pipefail

# ── Colores ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; exit 1; }

# ── Parámetros ────────────────────────────────────────────────────────────────
SKIP_BUILD=false
ENV_FILE=".env"
COMPOSE_CMD="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-build) SKIP_BUILD=true; shift ;;
    --env-file)   ENV_FILE="$2"; shift 2 ;;
    *) error "Argumento desconocido: $1" ;;
  esac
done

# ── Verificaciones previas ────────────────────────────────────────────────────
info "CiberCortex IA — Deploy"
echo

command -v docker  >/dev/null 2>&1 || error "Docker no está instalado."
docker compose version >/dev/null 2>&1 || error "Docker Compose v2 no está disponible."

[[ -f "$ENV_FILE" ]] || error "Archivo de entorno no encontrado: $ENV_FILE"

# Verificar variables críticas
# shellcheck source=/dev/null
source "$ENV_FILE"
[[ "${SECRET_KEY:-}" == "change-me"* ]] && error "SECRET_KEY no ha sido cambiado. Genera uno seguro."
[[ "${DB_PASSWORD:-}" == "cybercortex-dev"* ]] && warn "DB_PASSWORD parece ser el valor de desarrollo."
[[ -z "${ANTHROPIC_API_KEY:-}" ]] && warn "ANTHROPIC_API_KEY vacío — AI Assist no funcionará."

# ── Build ─────────────────────────────────────────────────────────────────────
if [[ "$SKIP_BUILD" == false ]]; then
  info "Construyendo imágenes Docker..."
  $COMPOSE_CMD build --no-cache
  success "Imágenes construidas."
fi

# ── Migraciones ───────────────────────────────────────────────────────────────
info "Levantando base de datos y Redis..."
$COMPOSE_CMD up -d db redis
sleep 5

info "Ejecutando migraciones Alembic..."
$COMPOSE_CMD --profile migrate run --rm migrate
success "Migraciones aplicadas."

# ── Deploy ────────────────────────────────────────────────────────────────────
info "Reiniciando servicios con zero-downtime (recreate)..."
$COMPOSE_CMD up -d --remove-orphans
success "Servicios actualizados."

# ── Health check ──────────────────────────────────────────────────────────────
info "Esperando que el backend esté listo..."
MAX_RETRIES=15
COUNT=0
until curl -sf http://localhost:8000/api/v1/health >/dev/null 2>&1; do
  COUNT=$((COUNT + 1))
  [[ $COUNT -ge $MAX_RETRIES ]] && error "Backend no responde tras $MAX_RETRIES intentos."
  echo -n "."
  sleep 2
done
echo
success "Backend responde en http://localhost:8000/api/v1/health"

# ── Estado final ──────────────────────────────────────────────────────────────
echo
$COMPOSE_CMD ps
echo
success "Deploy completado. Frontend disponible en http://localhost (nginx)."
