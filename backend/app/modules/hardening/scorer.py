"""
Scoring engine for CIS hardening assessments.

Raw score  = passed / (passed + failed)   [0.0 – 1.0]
Weighted score uses severity weights so critical/high failures cost more.

SEVERITY_WEIGHT maps severity → integer weight used in both numerator and denominator.
not_applicable and not_tested checks are excluded from both numerators and denominators.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SEVERITY_WEIGHT: dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


@dataclass
class ScoreResult:
    raw_score: float           # 0.0 – 1.0
    weighted_score: float      # 0.0 – 1.0
    total_checks: int
    passed_checks: int
    failed_checks: int
    not_applicable_checks: int
    not_tested_checks: int = field(default=0)

    @property
    def pass_rate_pct(self) -> float:
        return round(self.raw_score * 100, 1)

    @property
    def weighted_pct(self) -> float:
        return round(self.weighted_score * 100, 1)


def compute_score(results: list[dict]) -> ScoreResult:
    """
    Compute raw and weighted scores from a list of check result dicts.

    Each dict must have:
        result   : str  — "pass" | "fail" | "not_applicable" | "not_tested"
        severity : str  — "critical" | "high" | "medium" | "low"

    Returns a ScoreResult dataclass.
    """
    passed = 0
    failed = 0
    not_applicable = 0
    not_tested = 0

    weighted_passed = 0
    weighted_total = 0

    for r in results:
        result = r["result"]
        weight = SEVERITY_WEIGHT.get(r.get("severity", "low"), 1)

        if result == "pass":
            passed += 1
            weighted_passed += weight
            weighted_total += weight
        elif result == "fail":
            failed += 1
            weighted_total += weight
        elif result == "not_applicable":
            not_applicable += 1
        else:
            not_tested += 1

    scored = passed + failed
    raw_score = (passed / scored) if scored > 0 else 0.0
    weighted_score = (weighted_passed / weighted_total) if weighted_total > 0 else 0.0

    return ScoreResult(
        raw_score=round(raw_score, 4),
        weighted_score=round(weighted_score, 4),
        total_checks=len(results),
        passed_checks=passed,
        failed_checks=failed,
        not_applicable_checks=not_applicable,
        not_tested_checks=not_tested,
    )
