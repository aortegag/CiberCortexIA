import uuid
from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssessmentStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analyst_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    benchmark: Mapped[str] = mapped_column(String(100), nullable=False, default="CIS Linux Level 1")
    benchmark_version: Mapped[str] = mapped_column(String(20), nullable=False, default="2.0")
    date: Mapped[date] = mapped_column(Date, nullable=False)
    raw_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    weighted_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    not_applicable_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AssessmentStatus.COMPLETED.value
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
        return f"<Assessment {self.id} asset={self.asset_id} score={self.weighted_score}>"
