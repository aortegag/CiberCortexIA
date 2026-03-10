import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.asset import AssetStatus, AssetType


class AssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    ip_address: str | None = Field(default=None, max_length=45)
    hostname: str | None = Field(default=None, max_length=255)
    asset_type: AssetType = AssetType.OTHER
    os: str | None = Field(default=None, max_length=100)
    owner: str = Field(min_length=1, max_length=255)
    notes: str | None = None

    @model_validator(mode="after")
    def require_ip_or_hostname(self) -> "AssetCreate":
        if not self.ip_address and not self.hostname:
            raise ValueError("At least one of ip_address or hostname is required")
        return self


class AssetUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    ip_address: str | None = Field(default=None, max_length=45)
    hostname: str | None = Field(default=None, max_length=255)
    asset_type: AssetType | None = None
    os: str | None = Field(default=None, max_length=100)
    owner: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    ip_address: str | None
    hostname: str | None
    asset_type: AssetType
    os: str | None
    status: AssetStatus
    owner: str
    notes: str | None
    created_by_id: uuid.UUID | None
    authorized_by_id: uuid.UUID | None
    authorized_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    size: int
