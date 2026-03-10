"""
AI Assist Lite endpoints — explain CVEs and CIS checks.

POST  /ai/explain-cve    — plain-English CVE explanation
POST  /ai/explain-check  — plain-English CIS check explanation
GET   /ai/usage          — remaining requests this hour

Safety:   SYSTEM_PROMPT_DEFENSIVE_ONLY always included
Model:    claude-haiku-4-5 (per product design)
Rate:     5 requests / user / hour
Cache:    24 hours per (type, id)
Write:    ZERO — AI never touches the database
"""

from __future__ import annotations

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.modules.ai_assist import assistant as ai
from app.modules.hardening.cis_checks import CIS_BY_ID
from app.schemas.ai_assist import AIExplanationResponse, ExplainCVERequest, ExplainCheckRequest

router = APIRouter(prefix="/ai", tags=["ai-assist"])


# ---------------------------------------------------------------------------
# Redis dependency (simple — same URL as NVD cache)
# ---------------------------------------------------------------------------
async def get_redis() -> aioredis.Redis:  # type: ignore[return]
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=False)
    try:
        yield client
    finally:
        await client.aclose()


# ---------------------------------------------------------------------------
# POST /ai/explain-cve
# ---------------------------------------------------------------------------
@router.post(
    "/explain-cve",
    response_model=AIExplanationResponse,
    summary="Explain a CVE in plain language (cached 24h, rate limited)",
)
async def explain_cve(
    body: ExplainCVERequest,
    redis: aioredis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> AIExplanationResponse:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Assist is not configured (ANTHROPIC_API_KEY missing)",
        )

    try:
        text, was_cached, remaining = await ai.explain_cve(
            redis=redis,
            user_id=str(current_user.id),
            cve_id=body.cve_id,
            cvss_score=body.cvss_score,
            affected_software=body.affected_software,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        )

    return AIExplanationResponse(
        explanation=text,
        cached=was_cached,
        requests_remaining=remaining,
    )


# ---------------------------------------------------------------------------
# POST /ai/explain-check
# ---------------------------------------------------------------------------
@router.post(
    "/explain-check",
    response_model=AIExplanationResponse,
    summary="Explain a CIS check in plain language (cached 24h, rate limited)",
)
async def explain_check(
    body: ExplainCheckRequest,
    redis: aioredis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> AIExplanationResponse:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Assist is not configured (ANTHROPIC_API_KEY missing)",
        )

    check = CIS_BY_ID.get(body.check_id)
    if not check:
        raise HTTPException(
            status_code=404,
            detail=f"Check '{body.check_id}' not found in catalog. See GET /api/v1/hardening/catalog",
        )

    try:
        text, was_cached, remaining = await ai.explain_check(
            redis=redis,
            user_id=str(current_user.id),
            check_id=body.check_id,
            title=check["title"],
            section=check["section"],
            recommendation=check["recommendation"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        )

    return AIExplanationResponse(
        explanation=text,
        cached=was_cached,
        requests_remaining=remaining,
    )


# ---------------------------------------------------------------------------
# GET /ai/usage
# ---------------------------------------------------------------------------
@router.get(
    "/usage",
    summary="Remaining AI Assist requests this hour",
)
async def get_usage(
    redis: aioredis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> dict:
    remaining = await ai.get_remaining(redis, str(current_user.id))
    return {
        "requests_remaining": remaining,
        "limit_per_hour": settings.AI_RATE_LIMIT_PER_USER_PER_HOUR,
        "cache_ttl_hours": settings.AI_CACHE_TTL_SECONDS // 3600,
    }
