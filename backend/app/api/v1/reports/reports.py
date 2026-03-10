"""
Report generation endpoints.

POST  /reports/generate          — generate PDF report (returns metadata)
GET   /reports/                  — list reports (current user)
GET   /reports/{id}              — report metadata + status
GET   /reports/{id}/download     — download PDF bytes

Report types:
  exposure_technical   → Analyst only
  hardening_technical  → Analyst only
  executive_summary    → All authenticated roles
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record as audit_record
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.assessment import Assessment
from app.models.asset import Asset
from app.models.check_result import CheckResult
from app.models.cve_correlation import CVECorrelation
from app.models.discovered_service import DiscoveredService
from app.models.remediation_item import RemediationItem
from app.models.report import Report, ReportStatus, ReportType
from app.models.scan_job import ScanJob, ScanJobStatus
from app.models.user import User, UserRole
from app.modules.reports.pdf_generator import generate_pdf
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


# ---------------------------------------------------------------------------
# Data builders — fetch from DB and build dicts for the PDF renderer
# ---------------------------------------------------------------------------
async def _build_exposure_data(asset: Asset, db: AsyncSession) -> dict:
    # Latest completed scan
    scan_stmt = (
        select(ScanJob)
        .where(
            ScanJob.asset_id == asset.id,
            ScanJob.status == ScanJobStatus.COMPLETED.value,
        )
        .order_by(ScanJob.finished_at.desc())
        .limit(1)
    )
    scans = (await db.execute(scan_stmt)).scalars().all()
    last_scan = None
    services = []
    if scans:
        last_scan = scans[0]
        svc_stmt = select(DiscoveredService).where(
            DiscoveredService.scan_job_id == last_scan.id
        )
        services = (await db.execute(svc_stmt)).scalars().all()

    # CVEs for this asset
    cve_stmt = (
        select(CVECorrelation)
        .where(CVECorrelation.asset_id == asset.id)
        .order_by(CVECorrelation.cvss_score.desc().nullslast())
    )
    cves = (await db.execute(cve_stmt)).scalars().all()

    return {
        "asset": {
            "name": asset.name,
            "ip_address": asset.ip_address,
            "asset_type": asset.asset_type,
        },
        "last_scan": (
            {
                "started_at": str(last_scan.started_at),
                "status": last_scan.status,
            }
            if last_scan
            else None
        ),
        "services": [
            {
                "port": s.port,
                "protocol": s.protocol,
                "service": s.service,
                "version": s.version,
                "cpe": s.cpe,
            }
            for s in services
        ],
        "cves": [
            {
                "cve_id": c.cve_id,
                "cvss_score": c.cvss_score,
                "confidence": c.confidence,
                "software": c.software,
                "version": c.version,
            }
            for c in cves
        ],
    }


async def _build_hardening_data(asset: Asset, db: AsyncSession) -> dict:
    # Latest assessment
    stmt = (
        select(Assessment)
        .where(Assessment.asset_id == asset.id)
        .order_by(Assessment.date.desc())
        .limit(1)
    )
    assessments = (await db.execute(stmt)).scalars().all()

    if not assessments:
        return {
            "asset": {"name": asset.name, "ip_address": asset.ip_address},
            "assessment": None,
            "checks": [],
            "remediation": [],
        }

    latest = assessments[0]

    checks_stmt = (
        select(CheckResult)
        .where(CheckResult.assessment_id == latest.id)
        .order_by(CheckResult.check_id)
    )
    checks = (await db.execute(checks_stmt)).scalars().all()

    rem_stmt = (
        select(RemediationItem)
        .where(RemediationItem.assessment_id == latest.id)
        .order_by(RemediationItem.priority, RemediationItem.check_id)
    )
    remediation = (await db.execute(rem_stmt)).scalars().all()

    return {
        "asset": {"name": asset.name, "ip_address": asset.ip_address},
        "assessment": {
            "date": str(latest.date),
            "benchmark": latest.benchmark,
            "benchmark_version": latest.benchmark_version,
            "weighted_score": latest.weighted_score,
            "raw_score": latest.raw_score,
            "passed_checks": latest.passed_checks,
            "failed_checks": latest.failed_checks,
            "not_applicable_checks": latest.not_applicable_checks,
        },
        "checks": [
            {
                "check_id": c.check_id,
                "title": c.title,
                "severity": c.severity,
                "result": c.result,
            }
            for c in checks
        ],
        "remediation": [
            {
                "check_id": r.check_id,
                "title": r.title,
                "severity": r.severity,
                "priority": r.priority,
                "effort_minutes": r.effort_minutes,
            }
            for r in remediation
        ],
    }


async def _build_executive_data(asset: Asset, db: AsyncSession) -> dict:
    # CVE counts by severity (no IDs)
    cve_stmt = select(CVECorrelation).where(CVECorrelation.asset_id == asset.id)
    cves = (await db.execute(cve_stmt)).scalars().all()
    critical = sum(1 for c in cves if (c.cvss_score or 0) >= 9.0)
    high = sum(1 for c in cves if 7.0 <= (c.cvss_score or 0) < 9.0)
    medium = sum(1 for c in cves if 4.0 <= (c.cvss_score or 0) < 7.0)
    low = sum(1 for c in cves if (c.cvss_score or 0) < 4.0)

    # Latest assessment (abstract)
    assess_stmt = (
        select(Assessment)
        .where(Assessment.asset_id == asset.id)
        .order_by(Assessment.date.desc())
        .limit(5)
    )
    assessments = (await db.execute(assess_stmt)).scalars().all()

    hardening: dict = {}
    trend: list = []
    top_actions: list = []
    if assessments:
        latest = assessments[0]
        hardening = {
            "weighted_score": latest.weighted_score,
            "failed_checks": latest.failed_checks,
        }
        trend = [
            {"date": str(a.date), "weighted_score": a.weighted_score or 0}
            for a in reversed(assessments)
        ]
        # Top remediation items (title + priority only — no technical details)
        rem_stmt = (
            select(RemediationItem)
            .where(RemediationItem.assessment_id == latest.id)
            .order_by(RemediationItem.priority, RemediationItem.check_id)
            .limit(5)
        )
        rem_items = (await db.execute(rem_stmt)).scalars().all()
        top_actions = [
            {
                "priority": r.priority,
                "title": r.title,
                "severity": r.severity,
            }
            for r in rem_items
        ]

    return {
        "asset_name": asset.name,  # NO IP address in executive report
        "exposure": {
            "critical_cves": critical,
            "high_cves": high,
            "medium_cves": medium,
            "low_cves": low,
        },
        "hardening": hardening,
        "trend": trend,
        "top_actions": top_actions,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a PDF report for an asset",
)
async def generate_report(
    body: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    # Technical reports: Analyst + Admin only
    if body.report_type in (
        ReportType.EXPOSURE_TECHNICAL.value,
        ReportType.HARDENING_TECHNICAL.value,
    ):
        if current_user.role not in (UserRole.ADMIN.value, UserRole.ANALYST.value):
            raise HTTPException(
                status_code=403,
                detail="Technical reports require Analyst or Admin role",
            )

    asset = await db.get(Asset, body.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Build title
    type_labels = {
        "exposure_technical": "Exposure Technical Report",
        "hardening_technical": "Hardening Technical Report",
        "executive_summary": "Executive Security Summary",
    }
    title = f"{type_labels.get(body.report_type, 'Report')} — {asset.name}"

    # Create report record
    report = Report(
        asset_id=body.asset_id,
        created_by_id=current_user.id,
        report_type=body.report_type,
        status=ReportStatus.GENERATING.value,
        title=title,
    )
    db.add(report)
    await db.flush()

    # Build data and generate PDF
    try:
        if body.report_type == ReportType.EXPOSURE_TECHNICAL.value:
            data = await _build_exposure_data(asset, db)
        elif body.report_type == ReportType.HARDENING_TECHNICAL.value:
            data = await _build_hardening_data(asset, db)
        else:
            data = await _build_executive_data(asset, db)

        pdf_bytes = await generate_pdf(body.report_type, data)

        report.pdf_data = pdf_bytes
        report.status = ReportStatus.READY.value
        report.completed_at = datetime.now(timezone.utc)
    except Exception as exc:
        report.status = ReportStatus.FAILED.value
        report.error_message = str(exc)[:500]
        await db.commit()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")

    await audit_record(
        db,
        action="report_generated",
        user_id=current_user.id,
        resource_type="report",
        resource_id=str(report.id),
        details={"report_type": body.report_type, "asset_id": str(body.asset_id)},
    )
    await db.commit()
    await db.refresh(report)
    return ReportResponse.model_validate(report)


@router.get(
    "/",
    response_model=list[ReportResponse],
    summary="List reports (current user)",
)
async def list_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReportResponse]:
    stmt = (
        select(Report)
        .where(Report.created_by_id == current_user.id)
        .order_by(Report.created_at.desc())
        .limit(50)
    )
    reports = (await db.execute(stmt)).scalars().all()
    return [ReportResponse.model_validate(r) for r in reports]


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report metadata",
)
async def get_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    # Analysts can only see their own reports; Admins see all
    if current_user.role != UserRole.ADMIN.value:
        if report.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    return ReportResponse.model_validate(report)


@router.get(
    "/{report_id}/download",
    summary="Download PDF report",
    response_class=Response,
)
async def download_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if current_user.role != UserRole.ADMIN.value:
        if report.created_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    if report.status != ReportStatus.READY.value or not report.pdf_data:
        raise HTTPException(status_code=409, detail="Report is not ready yet")

    safe_title = report.title.replace(" ", "_").replace("/", "-")[:80]
    return Response(
        content=report.pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}.pdf"'
        },
    )
