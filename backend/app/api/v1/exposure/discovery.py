"""
Exposure — Discovery endpoints.

POST /exposure/assets/{id}/scans  → trigger nmap scan (asset must be authorized)
GET  /exposure/assets/{id}/scans  → list scans for asset
GET  /exposure/scans/{id}         → scan job detail + status
GET  /exposure/assets/{id}/services → discovered services from latest completed scan
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.asset import Asset, AssetStatus
from app.models.discovered_service import DiscoveredService
from app.models.scan_job import ScanJob, ScanJobStatus, ScanJobType
from app.models.user import User, UserRole
from app.schemas.exposure import DiscoveredServiceResponse, ScanJobResponse

router = APIRouter(tags=["exposure / discovery"])


def _assert_authorized(asset: Asset) -> None:
    """Safety gate: asset must be authorized before any active operation."""
    if asset.status != AssetStatus.AUTHORIZED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Asset '{asset.name}' must be authorized before scanning (current status: {asset.status})",
        )


@router.post(
    "/exposure/assets/{asset_id}/scans",
    response_model=ScanJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Nmap TCP scan — asset must be authorized",
)
async def trigger_scan(
    asset_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> ScanJob:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    _assert_authorized(asset)

    # Check no scan is already running for this asset
    running = await db.execute(
        select(ScanJob).where(
            ScanJob.asset_id == asset_id,
            ScanJob.status == ScanJobStatus.RUNNING.value,
        )
    )
    if running.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A scan is already running for this asset",
        )

    job = ScanJob(
        asset_id=asset_id,
        scan_type=ScanJobType.NMAP_TCP.value,
        status=ScanJobStatus.QUEUED.value,
        created_by_id=current_user.id,
    )
    db.add(job)

    await audit.record(
        db,
        action="scan.queued",
        user_id=current_user.id,
        resource_type="scan_job",
        resource_id=str(job.id),
        details={"asset_id": str(asset_id), "asset_name": asset.name, "target": asset.ip_address or asset.hostname},
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(job)

    # Dispatch Celery task (import here to avoid circular imports at startup)
    from app.services.task_manager import run_nmap_scan
    task = run_nmap_scan.delay(str(job.id))

    # Store Celery task ID for status polling
    job.celery_task_id = task.id
    await db.commit()
    await db.refresh(job)

    return job


@router.get(
    "/exposure/assets/{asset_id}/scans",
    response_model=list[ScanJobResponse],
    summary="List scans for an asset",
)
async def list_scans(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ScanJob]:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    result = await db.execute(
        select(ScanJob)
        .where(ScanJob.asset_id == asset_id)
        .order_by(ScanJob.created_at.desc())
    )
    return list(result.scalars().all())


@router.get(
    "/exposure/scans/{scan_id}",
    response_model=ScanJobResponse,
    summary="Get scan job status and detail",
)
async def get_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ScanJob:
    job = await db.get(ScanJob, scan_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan job not found")
    return job


@router.get(
    "/exposure/assets/{asset_id}/services",
    response_model=list[DiscoveredServiceResponse],
    summary="List discovered services for an asset (latest completed scan)",
)
async def list_services(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[DiscoveredService]:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    # Get the latest completed scan
    latest_scan = await db.execute(
        select(ScanJob)
        .where(ScanJob.asset_id == asset_id, ScanJob.status == ScanJobStatus.COMPLETED.value)
        .order_by(ScanJob.finished_at.desc())
        .limit(1)
    )
    job = latest_scan.scalar_one_or_none()
    if not job:
        return []

    result = await db.execute(
        select(DiscoveredService)
        .where(DiscoveredService.scan_job_id == job.id)
        .order_by(DiscoveredService.port)
    )
    return list(result.scalars().all())
