"""Tests for asset management endpoints."""
import pytest
from httpx import AsyncClient

from app.models.asset import Asset, AssetStatus
from app.models.user import User


@pytest.mark.asyncio
async def test_create_asset_analyst(client: AsyncClient, analyst_token: str):
    response = await client.post(
        "/api/v1/assets",
        json={
            "name": "Web Server",
            "ip_address": "192.168.1.100",
            "hostname": "web01.local",
            "asset_type": "server",
            "owner": "Web Team",
        },
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Web Server"
    assert data["status"] == "pending"  # Always starts as pending


@pytest.mark.asyncio
async def test_create_asset_requires_ip_or_hostname(client: AsyncClient, analyst_token: str):
    response = await client.post(
        "/api/v1/assets",
        json={"name": "Bad Asset", "asset_type": "server", "owner": "Team"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_asset_readonly_forbidden(client: AsyncClient, readonly_token: str):
    response = await client.post(
        "/api/v1/assets",
        json={"name": "DB Server", "ip_address": "10.0.0.5", "owner": "DBA"},
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_assets(client: AsyncClient, analyst_token: str, pending_asset: Asset):
    response = await client.get(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_asset_by_id(client: AsyncClient, analyst_token: str, pending_asset: Asset):
    response = await client.get(
        f"/api/v1/assets/{pending_asset.id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(pending_asset.id)


@pytest.mark.asyncio
async def test_get_asset_not_found(client: AsyncClient, analyst_token: str):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/api/v1/assets/{fake_id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_asset(client: AsyncClient, analyst_token: str, pending_asset: Asset):
    response = await client.patch(
        f"/api/v1/assets/{pending_asset.id}",
        json={"os": "Ubuntu 24.04 LTS"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    assert response.json()["os"] == "Ubuntu 24.04 LTS"


@pytest.mark.asyncio
async def test_authorize_asset_admin_only(
    client: AsyncClient,
    admin_token: str,
    analyst_token: str,
    pending_asset: Asset,
):
    # Analyst cannot authorize
    response = await client.post(
        f"/api/v1/assets/{pending_asset.id}/authorize",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 403

    # Admin can authorize
    response = await client.post(
        f"/api/v1/assets/{pending_asset.id}/authorize",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == AssetStatus.AUTHORIZED.value
    assert data["authorized_by_id"] is not None
    assert data["authorized_at"] is not None


@pytest.mark.asyncio
async def test_authorize_already_authorized(
    client: AsyncClient, admin_token: str, authorized_asset: Asset
):
    response = await client.post(
        f"/api/v1/assets/{authorized_asset.id}/authorize",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_decommission_asset_admin_only(
    client: AsyncClient,
    admin_token: str,
    analyst_token: str,
    pending_asset: Asset,
):
    # Analyst cannot decommission
    response = await client.delete(
        f"/api/v1/assets/{pending_asset.id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 403

    # Admin can decommission
    response = await client.delete(
        f"/api/v1/assets/{pending_asset.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_unauthenticated_request(client: AsyncClient):
    response = await client.get("/api/v1/assets")
    assert response.status_code == 401
