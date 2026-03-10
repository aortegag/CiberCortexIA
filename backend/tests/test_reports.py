"""
Integration tests for report generation endpoints.

WeasyPrint (PDF generation) is mocked to avoid system dependencies in tests.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


# Minimal fake PDF bytes
_FAKE_PDF = b"%PDF-1.4 fake"


# ---------------------------------------------------------------------------
# POST /reports/generate — exposure_technical
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_generate_exposure_report_analyst(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    with patch(
        "app.api.v1.reports.reports.generate_pdf",
        new=AsyncMock(return_value=_FAKE_PDF),
    ):
        resp = await client.post(
            "/api/v1/reports/generate",
            json={
                "asset_id": str(authorized_asset.id),
                "report_type": "exposure_technical",
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["report_type"] == "exposure_technical"
    assert data["status"] == "ready"
    assert data["asset_id"] == str(authorized_asset.id)


@pytest.mark.asyncio
async def test_generate_hardening_report_analyst(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    with patch(
        "app.api.v1.reports.reports.generate_pdf",
        new=AsyncMock(return_value=_FAKE_PDF),
    ):
        resp = await client.post(
            "/api/v1/reports/generate",
            json={
                "asset_id": str(authorized_asset.id),
                "report_type": "hardening_technical",
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )

    assert resp.status_code == 201, resp.text
    assert resp.json()["report_type"] == "hardening_technical"


@pytest.mark.asyncio
async def test_generate_executive_report_readonly(
    client: AsyncClient,
    readonly_token: str,
    authorized_asset,
) -> None:
    """Read-Only users CAN generate executive summaries."""
    with patch(
        "app.api.v1.reports.reports.generate_pdf",
        new=AsyncMock(return_value=_FAKE_PDF),
    ):
        resp = await client.post(
            "/api/v1/reports/generate",
            json={
                "asset_id": str(authorized_asset.id),
                "report_type": "executive_summary",
            },
            headers={"Authorization": f"Bearer {readonly_token}"},
        )

    assert resp.status_code == 201, resp.text


@pytest.mark.asyncio
async def test_generate_technical_report_readonly_forbidden(
    client: AsyncClient,
    readonly_token: str,
    authorized_asset,
) -> None:
    """Read-Only users CANNOT generate technical reports."""
    resp = await client.post(
        "/api/v1/reports/generate",
        json={
            "asset_id": str(authorized_asset.id),
            "report_type": "exposure_technical",
        },
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_generate_report_asset_not_found(
    client: AsyncClient,
    analyst_token: str,
) -> None:
    import uuid
    resp = await client.post(
        "/api/v1/reports/generate",
        json={
            "asset_id": str(uuid.uuid4()),
            "report_type": "exposure_technical",
        },
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /reports/
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_reports(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    with patch(
        "app.api.v1.reports.reports.generate_pdf",
        new=AsyncMock(return_value=_FAKE_PDF),
    ):
        await client.post(
            "/api/v1/reports/generate",
            json={
                "asset_id": str(authorized_asset.id),
                "report_type": "executive_summary",
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )

    resp = await client.get(
        "/api/v1/reports/",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


# ---------------------------------------------------------------------------
# GET /reports/{id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_report_metadata(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    with patch(
        "app.api.v1.reports.reports.generate_pdf",
        new=AsyncMock(return_value=_FAKE_PDF),
    ):
        create_resp = await client.post(
            "/api/v1/reports/generate",
            json={
                "asset_id": str(authorized_asset.id),
                "report_type": "hardening_technical",
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
    report_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == report_id


# ---------------------------------------------------------------------------
# GET /reports/{id}/download
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_download_report_pdf(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset,
) -> None:
    with patch(
        "app.api.v1.reports.reports.generate_pdf",
        new=AsyncMock(return_value=_FAKE_PDF),
    ):
        create_resp = await client.post(
            "/api/v1/reports/generate",
            json={
                "asset_id": str(authorized_asset.id),
                "report_type": "executive_summary",
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
    report_id = create_resp.json()["id"]

    dl_resp = await client.get(
        f"/api/v1/reports/{report_id}/download",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"
    assert dl_resp.content == _FAKE_PDF
