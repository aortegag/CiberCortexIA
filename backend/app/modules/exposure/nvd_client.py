"""
NVD API v2 client.

Features:
- Rate limiting: 5 req/30s without API key, 50 req/30s with key (NVD policy).
- Redis cache: 24h TTL per unique query.
- Retry with exponential backoff on transient errors.
- Returns normalized CVE dicts ready to store in CVECorrelation.
"""
import asyncio
import hashlib
import json
import logging

import httpx
import redis.asyncio as aioredis
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)

# NVD rate limit: sleep between requests
# Without key: 1 req / 6s → 10/min (conservative)
# With key: 1 req / 0.6s → 100/min (conservative)
_RATE_LIMIT_SLEEP = 0.6 if settings.NVD_API_KEY else 6.0


def _cache_key(query_type: str, value: str) -> str:
    h = hashlib.sha256(value.encode()).hexdigest()[:16]
    return f"nvd:{query_type}:{h}"


def _extract_cvss(cve: dict) -> tuple[float | None, str | None, str | None]:
    """Extract best available CVSS score, vector, and version from a CVE object."""
    metrics = cve.get("metrics", {})
    for metric_key, version_label in [
        ("cvssMetricV31", "3.1"),
        ("cvssMetricV30", "3.0"),
        ("cvssMetricV2", "2.0"),
    ]:
        entries = metrics.get(metric_key, [])
        if entries:
            data = entries[0].get("cvssData", {})
            return data.get("baseScore"), data.get("vectorString"), version_label
    return None, None, None


def _parse_vulnerabilities(data: dict) -> list[dict]:
    results = []
    for vuln in data.get("vulnerabilities", []):
        cve = vuln.get("cve", {})
        cve_id = cve.get("id", "")
        if not cve_id:
            continue
        score, vector, version = _extract_cvss(cve)
        results.append(
            {
                "cve_id": cve_id,
                "cvss_score": score,
                "cvss_vector": vector,
                "cvss_version": version,
            }
        )
    return results


@retry(
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=30),
)
async def _query_nvd(params: dict) -> list[dict]:
    headers = {}
    if settings.NVD_API_KEY:
        headers["apiKey"] = settings.NVD_API_KEY

    await asyncio.sleep(_RATE_LIMIT_SLEEP)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(settings.NVD_API_BASE_URL, params=params, headers=headers)
        response.raise_for_status()
        return _parse_vulnerabilities(response.json())


async def _cached_query(cache_key: str, params: dict) -> list[dict]:
    r = aioredis.from_url(settings.REDIS_URL)
    try:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

        results = await _query_nvd(params)
        await r.setex(cache_key, settings.NVD_CACHE_TTL_SECONDS, json.dumps(results))
        return results
    except Exception as exc:
        logger.warning("NVD query failed: %s", exc)
        return []
    finally:
        await r.aclose()


async def fetch_cves_by_cpe(cpe: str) -> list[dict]:
    """Query NVD by CPE string. High-confidence results."""
    key = _cache_key("cpe", cpe)
    return await _cached_query(key, {"cpeName": cpe, "resultsPerPage": 50})


async def fetch_cves_by_keyword(keyword: str) -> list[dict]:
    """Query NVD by keyword (e.g. 'OpenSSH 7.4'). Medium-confidence results."""
    key = _cache_key("kw", keyword)
    return await _cached_query(key, {"keywordSearch": keyword, "resultsPerPage": 20})
