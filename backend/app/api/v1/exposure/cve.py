"""
Exposure — CVE correlation endpoints.

GET /exposure/assets/{id}/cves          → list CVE correlations for an asset
GET /exposure/assets/{id}/cves/summary  → counts by severity
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.asset import Asset
from app.models.cve_correlation import CVEConfidence, CVECorrelation
from app.models.user import User
from app.schemas.exposure import CVECorrelationResponse

router = APIRouter(tags=["exposure / cve"])


def _severity_from_score(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low"


@router.get(
    "/exposure/assets/{asset_id}/cves",
    response_model=list[CVECorrelationResponse],
    summary="List CVE correlations for an asset",
)
async def list_cves(
    asset_id: uuid.UUID,
    confidence: CVEConfidence | None = Query(default=None, description="Filter by confidence level"),
    min_cvss: float | None = Query(default=None, ge=0.0, le=10.0, description="Minimum CVSS score"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[CVECorrelation]:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    q = select(CVECorrelation).where(CVECorrelation.asset_id == asset_id)

    if confidence:
        q = q.where(CVECorrelation.confidence == confidence.value)
    if min_cvss is not None:
        q = q.where(CVECorrelation.cvss_score >= min_cvss)

    # Sort: by CVSS score descending (None scores last), then confidence
    result = await db.execute(q.order_by(CVECorrelation.cvss_score.desc().nulls_last()))
    return list(result.scalars().all())


@router.get(
    "/exposure/assets/{asset_id}/cves/summary",
    summary="CVE counts by severity for an asset",
)
async def cve_summary(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    result = await db.execute(
        select(CVECorrelation).where(CVECorrelation.asset_id == asset_id)
    )
    cves = result.scalars().all()

    summary: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    by_confidence: dict[str, int] = {"high": 0, "medium": 0, "low": 0}

    for cve in cves:
        sev = _severity_from_score(cve.cvss_score)
        summary[sev] = summary.get(sev, 0) + 1
        by_confidence[cve.confidence] = by_confidence.get(cve.confidence, 0) + 1

    return {
        "asset_id": str(asset_id),
        "total": len(cves),
        "by_severity": summary,
        "by_confidence": by_confidence,
    }
