"""
Pure unit tests for the CIS scoring engine.
No DB, no fixtures needed.
"""

import pytest

from app.modules.hardening.scorer import ScoreResult, compute_score


def _r(result: str, severity: str = "high") -> dict:
    return {"result": result, "severity": severity}


# ---------------------------------------------------------------------------
# Basic score correctness
# ---------------------------------------------------------------------------

def test_all_pass():
    results = [_r("pass", "high"), _r("pass", "medium"), _r("pass", "low")]
    score = compute_score(results)
    assert score.raw_score == 1.0
    assert score.weighted_score == 1.0
    assert score.passed_checks == 3
    assert score.failed_checks == 0


def test_all_fail():
    results = [_r("fail", "critical"), _r("fail", "high")]
    score = compute_score(results)
    assert score.raw_score == 0.0
    assert score.weighted_score == 0.0
    assert score.failed_checks == 2


def test_mixed_results():
    results = [
        _r("pass", "critical"),   # weight 4 → counts
        _r("fail", "high"),       # weight 3 → counts
        _r("not_applicable", "medium"),
        _r("not_tested", "low"),
    ]
    score = compute_score(results)
    # raw: 1 pass / (1 pass + 1 fail) = 0.5
    assert score.raw_score == 0.5
    # weighted: 4 / (4 + 3) ≈ 0.5714
    assert abs(score.weighted_score - round(4 / 7, 4)) < 1e-4
    assert score.total_checks == 4
    assert score.not_applicable_checks == 1
    assert score.not_tested_checks == 1


def test_only_not_applicable():
    results = [_r("not_applicable", "high"), _r("not_applicable", "low")]
    score = compute_score(results)
    assert score.raw_score == 0.0
    assert score.weighted_score == 0.0
    assert score.passed_checks == 0
    assert score.failed_checks == 0


def test_empty_results():
    score = compute_score([])
    assert score.raw_score == 0.0
    assert score.total_checks == 0


# ---------------------------------------------------------------------------
# Weighted score respects severity ordering
# ---------------------------------------------------------------------------

def test_critical_failure_weights_more_than_low():
    # Same raw score (1 pass, 1 fail) but different severities
    critical_fail = compute_score([_r("pass", "low"), _r("fail", "critical")])
    low_fail = compute_score([_r("pass", "critical"), _r("fail", "low")])

    # critical_fail: 1/(1+4) = 0.2
    # low_fail: 4/(4+1) = 0.8
    assert critical_fail.weighted_score < low_fail.weighted_score


def test_unknown_severity_defaults_to_weight_1():
    results = [_r("pass", "unknown_sev"), _r("fail", "unknown_sev")]
    score = compute_score(results)
    # Both weight=1 → 1/(1+1) = 0.5
    assert score.weighted_score == 0.5


# ---------------------------------------------------------------------------
# ScoreResult helper properties
# ---------------------------------------------------------------------------

def test_pass_rate_pct():
    score = ScoreResult(
        raw_score=0.75,
        weighted_score=0.80,
        total_checks=4,
        passed_checks=3,
        failed_checks=1,
        not_applicable_checks=0,
    )
    assert score.pass_rate_pct == 75.0
    assert score.weighted_pct == 80.0
