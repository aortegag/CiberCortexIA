from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.assets import router as assets_router
from app.api.v1.exposure.discovery import router as discovery_router
from app.api.v1.exposure.cve import router as cve_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "CiberCortex IA — Defensive cybersecurity platform. "
        "Exposure & Hardening workspaces. No offensive capabilities."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Routers — v1
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(discovery_router, prefix="/api/v1")
app.include_router(cve_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root() -> dict:
    """Root redirect hint."""
    return {"message": "CiberCortex IA API", "docs": "/docs", "health": "/api/v1/health"}
