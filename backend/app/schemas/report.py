from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ReportCreate(BaseModel):
    asset_id: uuid.UUID
    report_type: Literal[
        "exposure_technical", "hardening_technical", "executive_summary"
    ]


class ReportResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID | None
    created_by_id: uuid.UUID | None
    report_type: str
    status: str
    title: str
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
