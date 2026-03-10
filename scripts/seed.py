#!/usr/bin/env python3
"""
CiberCortex IA — Seed script
Crea el usuario admin inicial y datos de ejemplo opcionales.

Uso:
  python scripts/seed.py                          # desde la raíz del proyecto
  docker compose --profile seed run --rm seed     # vía Docker
"""
import asyncio
import os
import sys

# Añadir backend/app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import select

ADMIN_EMAIL    = os.getenv("SEED_ADMIN_EMAIL",    "admin@cibercortex.local")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "CiberCortex2024!")
ADMIN_NAME     = os.getenv("SEED_ADMIN_NAME",     "Admin CiberCortex")


async def seed() -> None:
    print("🌱  CiberCortex IA — Seed")
    print(f"   Admin email   : {ADMIN_EMAIL}")
    print(f"   Admin password: {ADMIN_PASSWORD}")
    print()

    async with async_session_factory() as session:
        # ── Comprobar si ya existe el admin ──────────────────────────────────
        result = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"✓  El usuario admin ya existe: {ADMIN_EMAIL}")
        else:
            admin = User(
                email=ADMIN_EMAIL,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                full_name=ADMIN_NAME,
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            print(f"✅  Usuario admin creado:")
            print(f"   ID    : {admin.id}")
            print(f"   Email : {admin.email}")
            print(f"   Rol   : {admin.role}")

    print()
    print("Seed completado.")
    print()
    print("Próximos pasos:")
    print("  1. Abre http://localhost:3000 (o http://localhost/)")
    print(f"  2. Inicia sesión con {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print("  3. Cambia la contraseña desde el perfil")
    print("  4. Agrega activos en Assets → Nuevo activo")


if __name__ == "__main__":
    asyncio.run(seed())
