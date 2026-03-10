"""
Hardening endpoints — CIS assessment lifecycle and remediation.

POST  /hardening/assessments                — create assessment + compute score
GET   /hardening/assessments/{id}           — assessment detail with check results
GET   /hardening/assets/{asset_id}/assessments — list assessments for an asset
GET   /hardening/assets/{asset_id}/score    — latest score + 5-entry trend
GET   /hardening/assessments/{id}/remediation — prioritised remediation list
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record as audit_record
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.assessment import Assessment, AssessmentStatus
from app.models.asset import Asset, AssetStatus
from app.models.check_result import CheckResult, CheckResultStatus
from app.models.remediation_item import RemediationItem
from app.models.user import User, UserRole
from app.modules.hardening.cis_checks import CIS_BY_ID, CIS_L1_LINUX
from app.modules.hardening.scorer import compute_score
from app.schemas.hardening import (
    AssessmentCreate,
    AssessmentDetailResponse,
    AssessmentResponse,
    AssetScoreResponse,
    RemediationItemResponse,
)

router = APIRouter(prefix="/hardening", tags=["hardening"])

# Severity → priority integer (1=critical, …4=low)
_PRIORITY: dict[str, int] = {"critical": 1, "high": 2, "medium": 3, "low": 4}


def _require_asset_authorized(asset: Asset) -> None:
    if asset.status != AssetStatus.AUTHORIZED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Asset must be in 'authorized' state before running an assessment",
        )


# ---------------------------------------------------------------------------
# POST /hardening/assessments
# ---------------------------------------------------------------------------

@router.post(
    "/assessments",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create CIS assessment",
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.ANALYST))],
)
async def create_assessment(
    body: AssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentResponse:
    # Validate asset exists and is authorized
    asset = await db.get(Asset, body.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    _require_asset_authorized(asset)

    # Validate all check_ids belong to the catalog
    unknown = [r.check_id for r in body.results if r.check_id not in CIS_BY_ID]
    if unknown:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown check IDs: {unknown}. See GET /hardening/catalog",
        )

    # Score
    result_dicts = []
    for r in body.results:
        meta = CIS_BY_ID[r.check_id]
        result_dicts.append({"result": r.result, "severity": meta["severity"]})

    score = compute_score(result_dicts)

    # Persist Assessment
    assessment = Assessment(
        asset_id=body.asset_id,
        analyst_id=current_user.id,
        benchmark=body.benchmark,
        benchmark_version=body.benchmark_version,
        date=body.date,
        raw_score=score.raw_score,
        weighted_score=score.weighted_score,
        total_checks=score.total_checks,
        passed_checks=score.passed_checks,
        failed_checks=score.failed_checks,
        not_applicable_checks=score.not_applicable_checks,
        status=AssessmentStatus.COMPLETED.value,
        notes=body.notes,
    )
    db.add(assessment)
    await db.flush()  # get assessment.id before adding children

    # Persist CheckResult + remediation items for failures
    for r in body.results:
        meta = CIS_BY_ID[r.check_id]
        cr = CheckResult(
            assessment_id=assessment.id,
            check_id=r.check_id,
            title=meta["title"],
            severity=meta["severity"],
            section=meta["section"],
            result=r.result,
            notes=r.notes,
            evidence_type=r.evidence_type,
            evidence_text=r.evidence_text,
            evidence_at=datetime.now(timezone.utc) if r.evidence_text else None,
        )
        db.add(cr)
        await db.flush()  # get cr.id

        if r.result == CheckResultStatus.FAIL.value:
            db.add(
                RemediationItem(
                    check_result_id=cr.id,
                    assessment_id=assessment.id,
                    asset_id=body.asset_id,
                    check_id=r.check_id,
                    title=meta["title"],
                    severity=meta["severity"],
                    priority=_PRIORITY.get(meta["severity"], 4),
                    recommendation=meta["recommendation"],
                    effort_minutes=meta["effort_minutes"],
                )
            )

    await audit_record(
        db,
        action="assessment_created",
        user_id=current_user.id,
        resource_type="assessment",
        resource_id=str(assessment.id),
        details={
            "asset_id": str(body.asset_id),
            "weighted_score": score.weighted_score,
            "failed_checks": score.failed_checks,
        },
    )
    await db.commit()
    await db.refresh(assessment)
    return AssessmentResponse.model_validate(assessment)


# ---------------------------------------------------------------------------
# GET /hardening/assessments/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/assessments/{assessment_id}",
    response_model=AssessmentDetailResponse,
    summary="Get assessment detail with check results",
)
async def get_assessment(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AssessmentDetailResponse:
    assessment = await db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    stmt = (
        select(CheckResult)
        .where(CheckResult.assessment_id == assessment_id)
        .order_by(CheckResult.check_id)
    )
    check_results = (await db.execute(stmt)).scalars().all()

    data = AssessmentDetailResponse.model_validate(assessment)
    data.check_results = [
        dict(
            id=cr.id,
            check_id=cr.check_id,
            title=cr.title,
            severity=cr.severity,
            section=cr.section,
            result=cr.result,
            notes=cr.notes,
            evidence_type=cr.evidence_type,
            evidence_text=cr.evidence_text,
            evidence_at=cr.evidence_at,
        )
        for cr in check_results
    ]
    return data


# ---------------------------------------------------------------------------
# GET /hardening/assets/{asset_id}/assessments
# ---------------------------------------------------------------------------

@router.get(
    "/assets/{asset_id}/assessments",
    response_model=list[AssessmentResponse],
    summary="List assessments for an asset",
)
async def list_asset_assessments(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[AssessmentResponse]:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    stmt = (
        select(Assessment)
        .where(Assessment.asset_id == asset_id)
        .order_by(Assessment.date.desc())
    )
    assessments = (await db.execute(stmt)).scalars().all()
    return [AssessmentResponse.model_validate(a) for a in assessments]


# ---------------------------------------------------------------------------
# GET /hardening/assets/{asset_id}/score
# ---------------------------------------------------------------------------

@router.get(
    "/assets/{asset_id}/score",
    response_model=AssetScoreResponse,
    summary="Latest CIS score and 5-entry trend for an asset",
)
async def get_asset_score(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AssetScoreResponse:
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    stmt = (
        select(Assessment)
        .where(Assessment.asset_id == asset_id)
        .order_by(Assessment.date.desc())
        .limit(5)
    )
    rows = (await db.execute(stmt)).scalars().all()

    if not rows:
        return AssetScoreResponse(
            asset_id=asset_id,
            latest_assessment_id=None,
            latest_date=None,
            weighted_score=None,
            raw_score=None,
            passed_checks=0,
            failed_checks=0,
            total_checks=0,
            trend=[],
        )

    latest = rows[0]
    trend = [
        {"date": str(r.date), "weighted_score": r.weighted_score}
        for r in reversed(rows)
    ]
    return AssetScoreResponse(
        asset_id=asset_id,
        latest_assessment_id=latest.id,
        latest_date=latest.date,
        weighted_score=latest.weighted_score,
        raw_score=latest.raw_score,
        passed_checks=latest.passed_checks,
        failed_checks=latest.failed_checks,
        total_checks=latest.total_checks,
        trend=trend,
    )


# ---------------------------------------------------------------------------
# GET /hardening/assessments/{id}/remediation
# ---------------------------------------------------------------------------

@router.get(
    "/assessments/{assessment_id}/remediation",
    response_model=list[RemediationItemResponse],
    summary="Prioritised remediation list for an assessment",
)
async def get_remediation(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[RemediationItemResponse]:
    assessment = await db.get(Assessment, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    stmt = (
        select(RemediationItem)
        .where(RemediationItem.assessment_id == assessment_id)
        .order_by(RemediationItem.priority.asc(), RemediationItem.check_id.asc())
    )
    items = (await db.execute(stmt)).scalars().all()
    return [RemediationItemResponse.model_validate(i) for i in items]


# ---------------------------------------------------------------------------
# GET /hardening/catalog — helper so clients know valid check IDs
# ---------------------------------------------------------------------------

@router.get(
    "/catalog",
    summary="List all CIS L1 checks in the catalog",
    response_model=list[dict],
)
async def list_catalog(_: User = Depends(get_current_user)) -> list[dict]:
    return list(CIS_L1_LINUX)
