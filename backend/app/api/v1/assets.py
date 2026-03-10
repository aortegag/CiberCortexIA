import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.asset import Asset, AssetStatus
from app.models.user import User, UserRole
from app.schemas.asset import AssetCreate, AssetListResponse, AssetResponse, AssetUpdate

router = APIRouter(prefix="/assets", tags=["assets"])


def _require_authorized(asset: Asset) -> None:
    """Safety gate: raises 403 if asset is not authorized for active operations."""
    if asset.status != AssetStatus.AUTHORIZED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Asset '{asset.name}' is not authorized for active operations (status: {asset.status})",
        )


@router.get("", response_model=AssetListResponse, summary="List assets")
async def list_assets(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    asset_status: AssetStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AssetListResponse:
    q = select(Asset)
    if asset_status:
        q = q.where(Asset.status == asset_status.value)

    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar_one()

    q = q.offset((page - 1) * size).limit(size).order_by(Asset.created_at.desc())
    result = await db.execute(q)
    items = result.scalars().all()

    return AssetListResponse(items=list(items), total=total, page=page, size=size)


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED, summary="Register asset")
async def create_asset(
    body: AssetCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> Asset:
    asset = Asset(
        name=body.name,
        ip_address=body.ip_address,
        hostname=body.hostname,
        asset_type=body.asset_type.value,
        os=body.os,
        owner=body.owner,
        notes=body.notes,
        created_by_id=current_user.id,
        status=AssetStatus.PENDING.value,
    )
    db.add(asset)

    await audit.record(
        db,
        action="asset.created",
        user_id=current_user.id,
        resource_type="asset",
        details={"name": body.name, "ip": body.ip_address, "hostname": body.hostname},
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/{asset_id}", response_model=AssetResponse, summary="Get asset detail")
async def get_asset(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Asset:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetResponse, summary="Update asset")
async def update_asset(
    asset_id: uuid.UUID,
    body: AssetUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST)),
) -> Asset:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    updated_fields: dict = {}
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(asset, field, value)
        updated_fields[field] = str(value)

    if not updated_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    await audit.record(
        db,
        action="asset.updated",
        user_id=current_user.id,
        resource_type="asset",
        resource_id=str(asset_id),
        details={"updated_fields": updated_fields},
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(asset)
    return asset


@router.post(
    "/{asset_id}/authorize",
    response_model=AssetResponse,
    summary="Authorize asset for active operations — Admin only",
)
async def authorize_asset(
    asset_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> Asset:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if asset.status == AssetStatus.AUTHORIZED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset is already authorized")

    if asset.status == AssetStatus.DECOMMISSIONED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot authorize a decommissioned asset")

    asset.status = AssetStatus.AUTHORIZED.value
    asset.authorized_by_id = current_user.id
    asset.authorized_at = datetime.now(timezone.utc)

    await audit.record(
        db,
        action="asset.authorized",
        user_id=current_user.id,
        resource_type="asset",
        resource_id=str(asset_id),
        details={"asset_name": asset.name},
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Decommission asset — Admin only",
)
async def decommission_asset(
    asset_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> None:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    asset.status = AssetStatus.DECOMMISSIONED.value

    await audit.record(
        db,
        action="asset.decommissioned",
        user_id=current_user.id,
        resource_type="asset",
        resource_id=str(asset_id),
        details={"asset_name": asset.name},
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
