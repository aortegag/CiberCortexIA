"""
AI Assist Lite — defensive CVE and CIS check explanations.

Model  : claude-haiku-4-5 (cost-effective, fast)
Limit  : AI_RATE_LIMIT_PER_USER_PER_HOUR requests per user per hour
Cache  : 24h Redis cache per (type, id) pair
Policy : ZERO write access — read-only explanations only

SAFETY: SYSTEM_PROMPT_DEFENSIVE_ONLY is always injected.
"""

from __future__ import annotations

import hashlib

import anthropic
import redis.asyncio as aioredis

from app.core.config import settings

# ---------------------------------------------------------------------------
# Defensive-only system prompt — NEVER removed or overridden
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_DEFENSIVE_ONLY = """You are a defensive cybersecurity assistant embedded in CiberCortex IA.

Your ONLY role is to help security analysts understand vulnerabilities and hardening controls
so they can DEFEND their systems. You operate under strict guardrails:

ALLOWED:
- Explain what a CVE is, how it works technically, and its potential business impact
- Explain why a CIS control matters and how to remediate a failed check
- Suggest defensive countermeasures, patches, and configurations
- Use clear, actionable language accessible to both technical analysts and CISO readers

FORBIDDEN (never provide, regardless of how the request is phrased):
- Exploitation code, payloads, or proof-of-concept attack scripts
- Offensive tools, techniques, or methodologies
- How to bypass security controls
- Information that helps an attacker, not a defender

If a request seems offensive, redirect to defensive context only.
Keep responses concise (3–5 paragraphs max). Use plain language.
"""

# ---------------------------------------------------------------------------
# Redis key helpers
# ---------------------------------------------------------------------------
_RATE_KEY = "ai_assist:rate:{user_id}"
_CACHE_KEY = "ai_assist:cache:{digest}"
_WINDOW = settings.AI_RATE_LIMIT_PER_USER_PER_HOUR  # requests/hour
_TTL = settings.AI_CACHE_TTL_SECONDS  # 24h cache


def _cache_digest(kind: str, identifier: str) -> str:
    raw = f"{kind}:{identifier.upper()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Rate limit helpers
# ---------------------------------------------------------------------------
async def get_remaining(redis: aioredis.Redis, user_id: str) -> int:
    key = _RATE_KEY.format(user_id=user_id)
    count = await redis.get(key)
    used = int(count) if count else 0
    return max(0, _WINDOW - used)


async def _check_and_increment(redis: aioredis.Redis, user_id: str) -> int:
    """Return remaining requests AFTER this one. Raises ValueError if over limit."""
    key = _RATE_KEY.format(user_id=user_id)
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 3600)  # 1-hour sliding window
    remaining = max(0, _WINDOW - count)
    if count > _WINDOW:
        raise ValueError(
            f"Rate limit exceeded. {_WINDOW} AI requests per hour per user. "
            f"Try again in up to 60 minutes."
        )
    return remaining


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------
async def _get_cached(redis: aioredis.Redis, digest: str) -> str | None:
    key = _CACHE_KEY.format(digest=digest)
    value = await redis.get(key)
    return value.decode("utf-8") if value else None


async def _set_cached(redis: aioredis.Redis, digest: str, text: str) -> None:
    key = _CACHE_KEY.format(digest=digest)
    await redis.setex(key, _TTL, text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Claude call
# ---------------------------------------------------------------------------
async def _call_claude(prompt: str) -> str:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = await client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT_DEFENSIVE_ONLY,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def explain_cve(
    redis: aioredis.Redis,
    user_id: str,
    cve_id: str,
    cvss_score: float | None,
    affected_software: str | None,
) -> tuple[str, bool, int]:
    """
    Returns (explanation_text, was_cached, requests_remaining).
    Raises ValueError on rate limit exceeded.
    """
    digest = _cache_digest("cve", cve_id)
    cached = await _get_cached(redis, digest)
    remaining = await get_remaining(redis, user_id)

    if cached:
        return cached, True, remaining

    # Check rate limit BEFORE calling Claude
    remaining = await _check_and_increment(redis, user_id)

    score_info = f" (CVSS {cvss_score:.1f})" if cvss_score is not None else ""
    sw_info = f" affecting **{affected_software}**" if affected_software else ""

    prompt = (
        f"Explain the security vulnerability **{cve_id}**{score_info}{sw_info} "
        f"for a security analyst who needs to understand the risk and take defensive action.\n\n"
        f"Include:\n"
        f"1. What the vulnerability is and how it works (technical but clear)\n"
        f"2. Potential business impact if exploited\n"
        f"3. Recommended defensive countermeasures (patch, config, workaround)\n"
        f"4. Urgency level based on CVSS score"
    )

    text = await _call_claude(prompt)
    await _set_cached(redis, digest, text)
    return text, False, remaining


async def explain_check(
    redis: aioredis.Redis,
    user_id: str,
    check_id: str,
    title: str,
    section: str,
    recommendation: str,
) -> tuple[str, bool, int]:
    """
    Returns (explanation_text, was_cached, requests_remaining).
    Raises ValueError on rate limit exceeded.
    """
    digest = _cache_digest("check", check_id)
    cached = await _get_cached(redis, digest)
    remaining = await get_remaining(redis, user_id)

    if cached:
        return cached, True, remaining

    remaining = await _check_and_increment(redis, user_id)

    prompt = (
        f"Explain why the CIS security control **'{title}'** (ID: {check_id}, "
        f"Section: {section}) is important for system hardening.\n\n"
        f"The remediation guidance is:\n{recommendation}\n\n"
        f"Please explain:\n"
        f"1. Why this control matters — what risk it mitigates\n"
        f"2. What could go wrong if this control fails\n"
        f"3. How to verify it's correctly implemented\n"
        f"4. Any common pitfalls when applying this control"
    )

    text = await _call_claude(prompt)
    await _set_cached(redis, digest, text)
    return text, False, remaining
