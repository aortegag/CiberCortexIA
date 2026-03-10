#!/usr/bin/env python3
"""
CiberCortex IA — Seed script (runs inside the Docker container)
Crea el usuario admin inicial.

Uso:
  docker compose --profile seed run --rm seed
  docker compose exec api python scripts/seed.py
"""
import asyncio
import os

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import select

ADMIN_EMAIL    = os.getenv("SEED_ADMIN_EMAIL",    "admin@cibercortex.local")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "CiberCortex2024!")
ADMIN_NAME     = os.getenv("SEED_ADMIN_NAME",     "Admin CiberCortex")


async def seed() -> None:
    print("\U0001f331  CiberCortex IA — Seed")
    print(f"   Admin email   : {ADMIN_EMAIL}")
    print()

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"\u2713  El usuario admin ya existe: {ADMIN_EMAIL}")
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
            print(f"\u2705  Usuario admin creado:")
            print(f"   ID    : {admin.id}")
            print(f"   Email : {admin.email}")
            print(f"   Rol   : {admin.role}")

    print()
    print("Seed completado.")
    print()
    print("Proximos pasos:")
    print("  1. Abre http://localhost:3000")
    print(f"  2. Inicia sesion con {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print("  3. Cambia la contrasena desde el perfil")


if __name__ == "__main__":
    asyncio.run(seed())
