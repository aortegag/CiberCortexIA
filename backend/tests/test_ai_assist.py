"""
Tests for AI Assist Lite endpoints.

Claude API and Redis are mocked — no real network calls.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_redis(remaining: int = 5, cached: str | None = None):
    """Return a mock Redis client that mimics rate limit + cache behaviour."""
    redis_mock = AsyncMock()

    # get_remaining: return remaining
    count_used = 5 - remaining
    redis_mock.get = AsyncMock(
        side_effect=lambda key: (
            str(count_used).encode() if "rate:" in key else
            cached.encode() if (cached and "cache:" in key) else None
        )
    )
    redis_mock.incr = AsyncMock(return_value=count_used + 1)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.aclose = AsyncMock()
    return redis_mock


# ---------------------------------------------------------------------------
# POST /ai/explain-cve
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_explain_cve_success(
    client: AsyncClient,
    analyst_token: str,
) -> None:
    redis_mock = _mock_redis(remaining=4)

    with (
        patch("app.api.v1.ai_assist.explain.get_redis", return_value=_async_gen(redis_mock)),
        patch("app.modules.ai_assist.assistant._call_claude", new=AsyncMock(
            return_value="This CVE is a critical remote code execution vulnerability..."
        )),
        patch("app.core.config.settings.ANTHROPIC_API_KEY", "test-key"),
    ):
        resp = await client.post(
            "/api/v1/ai/explain-cve",
            json={"cve_id": "CVE-2021-44228", "cvss_score": 10.0,
                  "affected_software": "Apache Log4j"},
            headers={"Authorization": f"Bearer {analyst_token}"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "explanation" in data
    assert isinstance(data["cached"], bool)
    assert "requests_remaining" in data


@pytest.mark.asyncio
async def test_explain_cve_invalid_format(
    client: AsyncClient,
    analyst_token: str,
) -> None:
    resp = await client.post(
        "/api/v1/ai/explain-cve",
        json={"cve_id": "NOT-A-CVE"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_explain_cve_no_api_key(
    client: AsyncClient,
    analyst_token: str,
) -> None:
    with patch("app.core.config.settings.ANTHROPIC_API_KEY", ""):
        resp = await client.post(
            "/api/v1/ai/explain-cve",
            json={"cve_id": "CVE-2021-44228"},
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_explain_cve_rate_limited(
    client: AsyncClient,
    analyst_token: str,
) -> None:
    redis_mock = _mock_redis(remaining=0)
    redis_mock.incr = AsyncMock(return_value=6)  # over limit

    with (
        patch("app.api.v1.ai_assist.explain.get_redis", return_value=_async_gen(redis_mock)),
        patch("app.core.config.settings.ANTHROPIC_API_KEY", "test-key"),
    ):
        resp = await client.post(
            "/api/v1/ai/explain-cve",
            json={"cve_id": "CVE-2021-44228"},
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
    assert resp.status_code == 429


# ---------------------------------------------------------------------------
# POST /ai/explain-check
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_explain_check_success(
    client: AsyncClient,
    readonly_token: str,
) -> None:
    redis_mock = _mock_redis(remaining=3)

    with (
        patch("app.api.v1.ai_assist.explain.get_redis", return_value=_async_gen(redis_mock)),
        patch("app.modules.ai_assist.assistant._call_claude", new=AsyncMock(
            return_value="SSH root login should be disabled because..."
        )),
        patch("app.core.config.settings.ANTHROPIC_API_KEY", "test-key"),
    ):
        resp = await client.post(
            "/api/v1/ai/explain-check",
            json={"check_id": "5.2.7"},
            headers={"Authorization": f"Bearer {readonly_token}"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "SSH" in data["explanation"]


@pytest.mark.asyncio
async def test_explain_check_unknown_id(
    client: AsyncClient,
    analyst_token: str,
) -> None:
    resp = await client.post(
        "/api/v1/ai/explain-check",
        json={"check_id": "99.99.99"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_explain_check_cached(
    client: AsyncClient,
    analyst_token: str,
) -> None:
    redis_mock = _mock_redis(remaining=5, cached="Cached explanation text")

    with (
        patch("app.api.v1.ai_assist.explain.get_redis", return_value=_async_gen(redis_mock)),
        patch("app.core.config.settings.ANTHROPIC_API_KEY", "test-key"),
    ):
        resp = await client.post(
            "/api/v1/ai/explain-check",
            json={"check_id": "5.2.7"},
            headers={"Authorization": f"Bearer {analyst_token}"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["cached"] is True
    assert data["explanation"] == "Cached explanation text"


# ---------------------------------------------------------------------------
# GET /ai/usage
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_usage(
    client: AsyncClient,
    readonly_token: str,
) -> None:
    redis_mock = _mock_redis(remaining=3)

    with patch("app.api.v1.ai_assist.explain.get_redis", return_value=_async_gen(redis_mock)):
        resp = await client.get(
            "/api/v1/ai/usage",
            headers={"Authorization": f"Bearer {readonly_token}"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "requests_remaining" in data
    assert data["limit_per_hour"] == 5


# ---------------------------------------------------------------------------
# Helpers for async generator mocking
# ---------------------------------------------------------------------------

async def _async_gen(value):
    """Create an async generator that yields a single value — simulates FastAPI Depends."""
    yield value
