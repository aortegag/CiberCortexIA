import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CVEConfidence(str, Enum):
    HIGH = "high"      # CPE exact match
    MEDIUM = "medium"  # version string keyword search
    LOW = "low"        # service name only


class CVEEvidenceSource(str, Enum):
    NMAP_CPE = "nmap_cpe"
    NMAP_VERSION_STRING = "nmap_version_string"
    SERVICE_NAME = "service_name"


class CVECorrelation(Base):
    __tablename__ = "cve_correlations"
    __table_args__ = (
        UniqueConstraint("asset_id", "cve_id", name="uq_cve_per_asset"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scan_job_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scan_jobs.id", ondelete="SET NULL"), nullable=True
    )
    discovered_service_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discovered_services.id", ondelete="SET NULL"),
        nullable=True,
    )
    cve_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cvss_vector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cvss_version: Mapped[str | None] = mapped_column(String(10), nullable=True)
    software: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[str] = mapped_column(String(10), nullable=False, default=CVEConfidence.MEDIUM.value)
    evidence_source: Mapped[str] = mapped_column(String(30), nullable=False)
    evidence_data: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<CVECorrelation {self.cve_id} asset={self.asset_id} [{self.confidence}]>"
