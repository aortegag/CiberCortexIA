import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.cve_correlation import CVEConfidence, CVEEvidenceSource
from app.models.scan_job import ScanJobStatus, ScanJobType


class ScanJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    scan_type: ScanJobType
    status: ScanJobStatus
    celery_task_id: str | None
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
    created_by_id: uuid.UUID | None
    created_at: datetime


class DiscoveredServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_job_id: uuid.UUID
    port: int
    protocol: str
    service: str
    version: str | None
    banner: str | None
    cpe: str | None
    created_at: datetime


class CVECorrelationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    cve_id: str
    cvss_score: float | None
    cvss_vector: str | None
    cvss_version: str | None
    software: str
    version: str | None
    confidence: CVEConfidence
    evidence_source: CVEEvidenceSource
    evidence_data: str
    scan_job_id: uuid.UUID | None
    discovered_service_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
