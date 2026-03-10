"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user: User):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "adminpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user: User):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@test.com", "password": "somepass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client: AsyncClient, admin_user: User, admin_token: str):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_returns_new_tokens(client: AsyncClient, admin_user: User):
    # First login to get refresh token
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "adminpass123"},
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not.a.valid.token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_admin_only(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "newuser@test.com",
            "password": "securepass123",
            "full_name": "New User",
            "role": "analyst",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@test.com"


@pytest.mark.asyncio
async def test_create_user_analyst_forbidden(client: AsyncClient, analyst_token: str):
    response = await client.post(
        "/api/v1/auth/users",
        json={
            "email": "another@test.com",
            "password": "securepass123",
            "full_name": "Another",
            "role": "analyst",
        },
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 403
