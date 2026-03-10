"""
Integration tests for hardening endpoints.
Uses in-memory SQLite via conftest fixtures.
"""

import pytest
from httpx import AsyncClient

from app.modules.hardening.cis_checks import CIS_L1_LINUX

# Use a subset of the catalog so tests stay fast
_PASS_CHECK = CIS_L1_LINUX[0]["check_id"]   # e.g. "1.1.1" — low severity
_FAIL_CHECK = CIS_L1_LINUX[8]["check_id"]   # e.g. "5.2.7" — critical severity
_NA_CHECK = CIS_L1_LINUX[2]["check_id"]     # e.g. "1.3.2" — medium severity


def _assessment_payload(asset_id: str) -> dict:
    return {
        "asset_id": asset_id,
        "date": "2026-03-10",
        "results": [
            {
                "check_id": _PASS_CHECK,
                "result": "pass",
                "evidence_type": "command_output",
                "evidence_text": "modprobe cramfs returned exit 1",
            },
            {
                "check_id": _FAIL_CHECK,
                "result": "fail",
                "evidence_type": "config_excerpt",
                "evidence_text": "PermitRootLogin yes",
            },
            {
                "check_id": _NA_CHECK,
                "result": "not_applicable",
            },
        ],
    }


# ---------------------------------------------------------------------------
# POST /hardening/assessments
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_assessment_analyst(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    payload = _assessment_payload(str(authorized_asset.id))
    resp = await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["asset_id"] == str(authorized_asset.id)
    assert data["passed_checks"] == 1
    assert data["failed_checks"] == 1
    assert data["not_applicable_checks"] == 1
    assert data["total_checks"] == 3
    assert data["weighted_score"] > 0


@pytest.mark.asyncio
async def test_create_assessment_read_only_forbidden(
    client: AsyncClient,
    readonly_token: str,
    authorized_asset,
) -> None:
    payload = _assessment_payload(str(authorized_asset.id))
    resp = await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_assessment_pending_asset_forbidden(
    client: AsyncClient,
    analyst_token: str,
    pending_asset,
) -> None:
    payload = _assessment_payload(str(pending_asset.id))
    resp = await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_assessment_unknown_check_id(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    payload = {
        "asset_id": str(authorized_asset.id),
        "date": "2026-03-10",
        "results": [
            {
                "check_id": "99.99.99",
                "result": "pass",
                "evidence_type": "command_output",
                "evidence_text": "something",
            }
        ],
    }
    resp = await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_assessment_missing_evidence_for_pass(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    """Pydantic should reject pass/fail without evidence."""
    payload = {
        "asset_id": str(authorized_asset.id),
        "date": "2026-03-10",
        "results": [
            {
                "check_id": _PASS_CHECK,
                "result": "pass",
                # No evidence_type or evidence_text
            }
        ],
    }
    resp = await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /hardening/assessments/{id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_assessment_detail(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    payload = _assessment_payload(str(authorized_asset.id))
    create_resp = await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert create_resp.status_code == 201
    assessment_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/hardening/assessments/{assessment_id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["check_results"]) == 3


# ---------------------------------------------------------------------------
# GET /hardening/assets/{id}/assessments
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_asset_assessments(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    payload = _assessment_payload(str(authorized_asset.id))
    await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )

    resp = await client.get(
        f"/api/v1/hardening/assets/{authorized_asset.id}/assessments",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ---------------------------------------------------------------------------
# GET /hardening/assets/{id}/score
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_asset_score_no_assessments(
    client: AsyncClient,
    readonly_token: str,
    authorized_asset,
) -> None:
    resp = await client.get(
        f"/api/v1/hardening/assets/{authorized_asset.id}/score",
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["latest_assessment_id"] is None
    assert data["trend"] == []


@pytest.mark.asyncio
async def test_asset_score_after_assessment(
    client: AsyncClient,
    analyst_token: str,
    readonly_token: str,
    authorized_asset,
) -> None:
    payload = _assessment_payload(str(authorized_asset.id))
    await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )

    resp = await client.get(
        f"/api/v1/hardening/assets/{authorized_asset.id}/score",
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["latest_assessment_id"] is not None
    assert data["weighted_score"] is not None
    assert len(data["trend"]) == 1


# ---------------------------------------------------------------------------
# GET /hardening/assessments/{id}/remediation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_remediation_list_contains_failed_check(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    payload = _assessment_payload(str(authorized_asset.id))
    create_resp = await client.post(
        "/api/v1/hardening/assessments",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assessment_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/hardening/assessments/{assessment_id}/remediation",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    # Only the failed check generates a remediation item
    assert len(items) == 1
    assert items[0]["check_id"] == _FAIL_CHECK
    assert items[0]["priority"] == 1  # critical → priority 1


# ---------------------------------------------------------------------------
# GET /hardening/catalog
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_catalog_returns_all_checks(
    client: AsyncClient,
    readonly_token: str,
) -> None:
    resp = await client.get(
        "/api/v1/hardening/catalog",
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == len(CIS_L1_LINUX)
