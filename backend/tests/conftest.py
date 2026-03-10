"""
Shared test fixtures. Uses SQLite in-memory for fast, isolated tests.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401 — registers all models with Base.metadata
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.asset import Asset, AssetStatus, AssetType
from app.models.user import User, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncClient:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── User fixtures ──────────────────────────────────────────────────────────────


@pytest_asyncio.fixture()
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("adminpass123"),
        full_name="Test Admin",
        role=UserRole.ADMIN.value,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def analyst_user(db_session: AsyncSession) -> User:
    user = User(
        email="analyst@test.com",
        hashed_password=hash_password("analystpass123"),
        full_name="Test Analyst",
        role=UserRole.ANALYST.value,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture()
async def readonly_user(db_session: AsyncSession) -> User:
    user = User(
        email="readonly@test.com",
        hashed_password=hash_password("readonlypass123"),
        full_name="Test ReadOnly",
        role=UserRole.READ_ONLY.value,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ── Token fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture()
def admin_token(admin_user: User) -> str:
    return create_access_token(str(admin_user.id), admin_user.role)


@pytest.fixture()
def analyst_token(analyst_user: User) -> str:
    return create_access_token(str(analyst_user.id), analyst_user.role)


@pytest.fixture()
def readonly_token(readonly_user: User) -> str:
    return create_access_token(str(readonly_user.id), readonly_user.role)


# ── Asset fixtures ─────────────────────────────────────────────────────────────


@pytest_asyncio.fixture()
async def pending_asset(db_session: AsyncSession, analyst_user: User) -> Asset:
    asset = Asset(
        name="Test Server",
        ip_address="192.168.1.10",
        hostname="test-server.local",
        asset_type=AssetType.SERVER.value,
        owner="IT Team",
        status=AssetStatus.PENDING.value,
        created_by_id=analyst_user.id,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset


@pytest_asyncio.fixture()
async def authorized_asset(db_session: AsyncSession, admin_user: User) -> Asset:
    asset = Asset(
        name="Authorized Server",
        ip_address="10.0.0.1",
        hostname="authorized.local",
        asset_type=AssetType.SERVER.value,
        owner="Security Team",
        status=AssetStatus.AUTHORIZED.value,
        created_by_id=admin_user.id,
        authorized_by_id=admin_user.id,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset
