from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Check result input (submitted by analyst)
# ---------------------------------------------------------------------------

class CheckResultInput(BaseModel):
    check_id: str = Field(..., max_length=30)
    result: Literal["pass", "fail", "not_applicable", "not_tested"]
    notes: str | None = Field(default=None, max_length=2000)

    # Evidence — required when result is pass or fail
    evidence_type: Literal[
        "command_output", "config_excerpt", "file_content", "manual_note"
    ] | None = None
    evidence_text: str | None = None

    @model_validator(mode="after")
    def evidence_required_for_decisive_results(self) -> "CheckResultInput":
        if self.result in ("pass", "fail"):
            if not self.evidence_type or not self.evidence_text:
                raise ValueError(
                    "evidence_type and evidence_text are required when result is 'pass' or 'fail'"
                )
        return self


# ---------------------------------------------------------------------------
# Assessment creation
# ---------------------------------------------------------------------------

class AssessmentCreate(BaseModel):
    asset_id: uuid.UUID
    date: date
    benchmark: str = Field(default="CIS Linux Level 1", max_length=100)
    benchmark_version: str = Field(default="2.0", max_length=20)
    notes: str | None = Field(default=None, max_length=4000)
    results: list[CheckResultInput] = Field(
        ..., min_length=1, description="One entry per CIS check evaluated"
    )


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class CheckResultResponse(BaseModel):
    id: uuid.UUID
    check_id: str
    title: str
    severity: str
    section: str
    result: str
    notes: str | None
    evidence_type: str | None
    evidence_text: str | None
    evidence_at: datetime | None

    model_config = {"from_attributes": True}


class AssessmentResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    analyst_id: uuid.UUID | None
    benchmark: str
    benchmark_version: str
    date: date
    raw_score: float
    weighted_score: float
    total_checks: int
    passed_checks: int
    failed_checks: int
    not_applicable_checks: int
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssessmentDetailResponse(AssessmentResponse):
    check_results: list[CheckResultResponse] = []


class RemediationItemResponse(BaseModel):
    id: uuid.UUID
    check_result_id: uuid.UUID
    assessment_id: uuid.UUID
    asset_id: uuid.UUID
    check_id: str
    title: str
    severity: str
    priority: int
    recommendation: str
    effort_minutes: int | None
    resolved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssetScoreResponse(BaseModel):
    asset_id: uuid.UUID
    latest_assessment_id: uuid.UUID | None
    latest_date: date | None
    weighted_score: float | None
    raw_score: float | None
    passed_checks: int
    failed_checks: int
    total_checks: int
    trend: list[dict]  # [{date, weighted_score}] last 5 assessments
