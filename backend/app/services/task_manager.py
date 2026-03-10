"""
Celery application + task definitions.

Tasks use synchronous SQLAlchemy (psycopg2) — the standard approach
for Celery workers. FastAPI uses async SQLAlchemy (asyncpg).

Safety invariant enforced in run_nmap_scan:
  asset.status must be 'authorized' — checked again inside the task,
  never relying only on the API-level check.
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from celery import Celery

from app.core.config import settings
from app.core.sync_database import get_sync_db

logger = logging.getLogger(__name__)

celery_app = Celery(
    "cybercortex",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,  # Only ack after task completes (safer for long-running tasks)
    worker_prefetch_multiplier=1,  # One task at a time per worker slot
)


@celery_app.task(bind=True, max_retries=2, name="tasks.run_nmap_scan")
def run_nmap_scan(self, scan_job_id: str) -> dict:
    """
    Execute Nmap TCP scan on the asset linked to scan_job_id.

    Steps:
    1. Load scan_job + asset, validate asset is still authorized.
    2. Update status → running.
    3. Run nmap, save DiscoveredService records.
    4. Update status → completed.
    5. Dispatch correlate_cves task.
    """
    from app.models.asset import AssetStatus
    from app.models.scan_job import ScanJob, ScanJobStatus
    from app.models.discovered_service import DiscoveredService
    from app.modules.exposure import scanner

    job_id = uuid.UUID(scan_job_id)

    with get_sync_db() as db:
        job: ScanJob | None = db.get(ScanJob, job_id)
        if not job:
            logger.error("ScanJob %s not found", scan_job_id)
            return {"error": "scan_job not found"}

        from app.models.asset import Asset
        asset: Asset | None = db.get(Asset, job.asset_id)
        if not asset or asset.status != AssetStatus.AUTHORIZED.value:
            job.status = ScanJobStatus.FAILED.value
            job.error_message = "Asset is not authorized for scanning"
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
            logger.warning("Scan %s aborted: asset not authorized", scan_job_id)
            return {"error": "asset not authorized"}

        # Mark as running
        job.status = ScanJobStatus.RUNNING.value
        job.started_at = datetime.now(timezone.utc)
        db.commit()

    # Run nmap OUTSIDE the DB transaction (can take minutes)
    target = asset.ip_address or asset.hostname
    try:
        services = asyncio.run(
            scanner.run_nmap(target, timeout=settings.NMAP_SCAN_TIMEOUT_SECONDS)
        )
    except RuntimeError as exc:
        with get_sync_db() as db:
            job = db.get(ScanJob, job_id)
            job.status = ScanJobStatus.FAILED.value
            job.error_message = str(exc)[:500]
            job.finished_at = datetime.now(timezone.utc)
        logger.error("Nmap scan %s failed: %s", scan_job_id, exc)
        return {"error": str(exc)}

    # Save results
    with get_sync_db() as db:
        for svc in services:
            db.add(
                DiscoveredService(
                    scan_job_id=job_id,
                    port=svc["port"],
                    protocol=svc["protocol"],
                    service=svc["service"],
                    version=svc["version"],
                    banner=svc["banner"],
                    cpe=svc["cpe"],
                )
            )

        job = db.get(ScanJob, job_id)
        job.status = ScanJobStatus.COMPLETED.value
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

    logger.info("Scan %s completed: %d services found", scan_job_id, len(services))

    # Dispatch CVE correlation
    correlate_cves.delay(scan_job_id)

    return {"scan_job_id": scan_job_id, "services_found": len(services)}


@celery_app.task(bind=True, max_retries=2, name="tasks.correlate_cves")
def correlate_cves(self, scan_job_id: str) -> dict:
    """
    For each DiscoveredService in the scan, query NVD API and store CVECorrelations.

    Confidence levels:
    - HIGH   → CPE match (nmap detected a CPE)
    - MEDIUM → version string keyword search
    - LOW    → service name only keyword search
    """
    from sqlalchemy import select
    from app.models.discovered_service import DiscoveredService
    from app.models.scan_job import ScanJob
    from app.models.cve_correlation import CVECorrelation, CVEConfidence, CVEEvidenceSource
    from app.modules.exposure import nvd_client

    job_id = uuid.UUID(scan_job_id)

    with get_sync_db() as db:
        job: ScanJob | None = db.get(ScanJob, job_id)
        if not job:
            return {"error": "scan_job not found"}
        asset_id = job.asset_id

        services = db.execute(
            select(DiscoveredService).where(DiscoveredService.scan_job_id == job_id)
        ).scalars().all()

    total_cves = 0

    for svc in services:
        # Determine query strategy by available data
        if svc.cpe:
            confidence = CVEConfidence.HIGH.value
            evidence_source = CVEEvidenceSource.NMAP_CPE.value
            evidence_data = svc.cpe
            cves = asyncio.run(nvd_client.fetch_cves_by_cpe(svc.cpe))
        elif svc.version:
            confidence = CVEConfidence.MEDIUM.value
            evidence_source = CVEEvidenceSource.NMAP_VERSION_STRING.value
            evidence_data = svc.version
            keyword = f"{svc.service} {svc.version}".strip()
            cves = asyncio.run(nvd_client.fetch_cves_by_keyword(keyword))
        else:
            # Only skip service-name queries for truly unknown services
            if svc.service in ("unknown", "tcpwrapped"):
                continue
            confidence = CVEConfidence.LOW.value
            evidence_source = CVEEvidenceSource.SERVICE_NAME.value
            evidence_data = svc.service
            cves = asyncio.run(nvd_client.fetch_cves_by_keyword(svc.service))

        if not cves:
            continue

        with get_sync_db() as db:
            for cve_data in cves:
                # Upsert: if CVE already exists for this asset, update confidence if higher
                from sqlalchemy import select as sa_select
                existing = db.execute(
                    sa_select(CVECorrelation).where(
                        CVECorrelation.asset_id == asset_id,
                        CVECorrelation.cve_id == cve_data["cve_id"],
                    )
                ).scalar_one_or_none()

                if existing:
                    # Upgrade confidence if new detection is more confident
                    confidence_rank = {
                        CVEConfidence.HIGH.value: 3,
                        CVEConfidence.MEDIUM.value: 2,
                        CVEConfidence.LOW.value: 1,
                    }
                    if confidence_rank.get(confidence, 0) > confidence_rank.get(existing.confidence, 0):
                        existing.confidence = confidence
                        existing.evidence_source = evidence_source
                        existing.evidence_data = evidence_data
                        existing.scan_job_id = job_id
                        existing.discovered_service_id = svc.id
                else:
                    db.add(
                        CVECorrelation(
                            asset_id=asset_id,
                            scan_job_id=job_id,
                            discovered_service_id=svc.id,
                            cve_id=cve_data["cve_id"],
                            cvss_score=cve_data.get("cvss_score"),
                            cvss_vector=cve_data.get("cvss_vector"),
                            cvss_version=cve_data.get("cvss_version"),
                            software=svc.service,
                            version=svc.version,
                            confidence=confidence,
                            evidence_source=evidence_source,
                            evidence_data=evidence_data,
                        )
                    )
                    total_cves += 1

    logger.info("CVE correlation for scan %s: %d new CVEs stored", scan_job_id, total_cves)
    return {"scan_job_id": scan_job_id, "cves_stored": total_cves}
