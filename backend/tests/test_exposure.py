"""
Tests for Exposure: discovery endpoints + CVE endpoints.
Nmap and NVD API are mocked — no real network calls.
"""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.asset import Asset
from app.models.cve_correlation import CVEConfidence, CVECorrelation, CVEEvidenceSource
from app.models.discovered_service import DiscoveredService
from app.models.scan_job import ScanJob, ScanJobStatus
from app.models.user import User


# ── Scanner unit tests (pure function, no DB) ─────────────────────────────────


def test_parse_nmap_xml_empty():
    from app.modules.exposure.scanner import parse_nmap_xml

    result = parse_nmap_xml("<nmaprun></nmaprun>")
    assert result == []


def test_parse_nmap_xml_with_services():
    from app.modules.exposure.scanner import parse_nmap_xml

    xml = """
    <nmaprun>
      <host>
        <ports>
          <port protocol="tcp" portid="22">
            <state state="open"/>
            <service name="ssh" product="OpenSSH" version="8.9" extrainfo="Ubuntu">
              <cpe>cpe:/a:openbsd:openssh:8.9</cpe>
            </service>
          </port>
          <port protocol="tcp" portid="80">
            <state state="open"/>
            <service name="http" product="nginx" version="1.24.0"/>
          </port>
          <port protocol="tcp" portid="9999">
            <state state="closed"/>
            <service name="unknown"/>
          </port>
        </ports>
      </host>
    </nmaprun>
    """
    services = parse_nmap_xml(xml)
    assert len(services) == 2  # only open ports
    assert services[0]["port"] == 22
    assert services[0]["service"] == "ssh"
    assert services[0]["cpe"] == "cpe:/a:openbsd:openssh:8.9"
    assert services[1]["port"] == 80
    assert services[1]["service"] == "http"
    assert services[1]["cpe"] is None


def test_parse_nmap_xml_invalid():
    from app.modules.exposure.scanner import parse_nmap_xml

    result = parse_nmap_xml("not xml at all")
    assert result == []


# ── API endpoint tests ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
@patch("app.api.v1.exposure.discovery.run_nmap_scan")
async def test_trigger_scan_authorized_asset(
    mock_task,
    client: AsyncClient,
    analyst_token: str,
    authorized_asset: Asset,
):
    mock_task.delay.return_value = MagicMock(id="mock-celery-task-id")

    response = await client.post(
        f"/api/v1/exposure/assets/{authorized_asset.id}/scans",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert data["asset_id"] == str(authorized_asset.id)
    mock_task.delay.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_scan_pending_asset_forbidden(
    client: AsyncClient,
    analyst_token: str,
    pending_asset: Asset,
):
    """Scanning a non-authorized asset must be rejected — safety gate."""
    response = await client.post(
        f"/api/v1/exposure/assets/{pending_asset.id}/scans",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_trigger_scan_readonly_forbidden(
    client: AsyncClient,
    readonly_token: str,
    authorized_asset: Asset,
):
    response = await client.post(
        f"/api/v1/exposure/assets/{authorized_asset.id}/scans",
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_scans_for_asset(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset: Asset,
    db_session,
):
    job = ScanJob(
        asset_id=authorized_asset.id,
        status=ScanJobStatus.COMPLETED.value,
    )
    db_session.add(job)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/exposure/assets/{authorized_asset.id}/scans",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_scan_by_id(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset: Asset,
    db_session,
):
    job = ScanJob(asset_id=authorized_asset.id, status=ScanJobStatus.RUNNING.value)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    response = await client.get(
        f"/api/v1/exposure/scans/{job.id}",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "running"


@pytest.mark.asyncio
async def test_list_services_empty_when_no_completed_scan(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset: Asset,
):
    response = await client.get(
        f"/api/v1/exposure/assets/{authorized_asset.id}/services",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_cves_for_asset(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset: Asset,
    db_session,
):
    cve = CVECorrelation(
        asset_id=authorized_asset.id,
        cve_id="CVE-2023-12345",
        cvss_score=9.8,
        software="OpenSSH",
        version="8.0",
        confidence=CVEConfidence.HIGH.value,
        evidence_source=CVEEvidenceSource.NMAP_CPE.value,
        evidence_data="cpe:/a:openbsd:openssh:8.0",
    )
    db_session.add(cve)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/exposure/assets/{authorized_asset.id}/cves",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["cve_id"] == "CVE-2023-12345"
    assert data[0]["confidence"] == "high"


@pytest.mark.asyncio
async def test_cve_summary(
    client: AsyncClient,
    analyst_token: str,
    authorized_asset: Asset,
    db_session,
):
    # Add a mix of CVEs
    cves = [
        CVECorrelation(
            asset_id=authorized_asset.id, cve_id="CVE-2023-0001",
            cvss_score=9.8, software="svc", confidence=CVEConfidence.HIGH.value,
            evidence_source=CVEEvidenceSource.NMAP_CPE.value, evidence_data="cpe:/x",
        ),
        CVECorrelation(
            asset_id=authorized_asset.id, cve_id="CVE-2023-0002",
            cvss_score=6.5, software="svc", confidence=CVEConfidence.MEDIUM.value,
            evidence_source=CVEEvidenceSource.NMAP_VERSION_STRING.value, evidence_data="svc 1.0",
        ),
    ]
    db_session.add_all(cves)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/exposure/assets/{authorized_asset.id}/cves/summary",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "by_severity" in data
    assert "by_confidence" in data
    assert data["total"] >= 2
