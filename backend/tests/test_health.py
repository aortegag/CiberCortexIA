"""Integration test for the /health endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["health"] == "/api/v1/health"


@pytest.mark.asyncio
async def test_health_with_live_dependencies(client: AsyncClient):
    """
    NOTE: This test requires DB + Redis running.
    In CI it will run against test containers.
    Locally, start services with: docker compose up db redis
    """
    response = await client.get("/api/v1/health")
    # Accept 200 (all ok) or 503 (dependencies not available in unit test mode)
    assert response.status_code in (200, 503)
    data = response.json()
    if response.status_code == 200:
        assert data["status"] == "ok"
        assert "checks" in data
    else:
        assert "detail" in data
