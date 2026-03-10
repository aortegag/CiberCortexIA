import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CheckResultStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"
    NOT_TESTED = "not_tested"


class EvidenceType(str, Enum):
    COMMAND_OUTPUT = "command_output"
    CONFIG_EXCERPT = "config_excerpt"
    FILE_CONTENT = "file_content"
    MANUAL_NOTE = "manual_note"


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Denormalized from CIS catalog for query independence
    check_id: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    section: Mapped[str] = mapped_column(String(100), nullable=False)

    result: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CheckResultStatus.NOT_TESTED.value
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Evidence — mandatory for pass/fail (enforced at schema level)
    evidence_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<CheckResult {self.check_id} [{self.result}]>"
