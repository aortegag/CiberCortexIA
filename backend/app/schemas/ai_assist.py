from __future__ import annotations

from pydantic import BaseModel, Field


class ExplainCVERequest(BaseModel):
    cve_id: str = Field(..., pattern=r"^CVE-\d{4}-\d{4,}$")
    cvss_score: float | None = None
    affected_software: str | None = Field(default=None, max_length=200)


class ExplainCheckRequest(BaseModel):
    check_id: str = Field(..., max_length=30)


class AIExplanationResponse(BaseModel):
    explanation: str
    cached: bool = False
    requests_remaining: int
