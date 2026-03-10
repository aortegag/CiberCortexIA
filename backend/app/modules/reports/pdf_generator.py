"""
PDF report generator — WeasyPrint-based HTML → PDF.

Three report types:
  - exposure_technical  : services + CVEs for analysts
  - hardening_technical : CIS assessment + remediation for analysts
  - executive_summary   : abstract scores + trends (NO IPs / CVE IDs / versions)

Call generate_pdf(report_type, data) → bytes (PDF content)
The 'data' dict is built by the endpoint from DB query results.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Severity palette (matches UX_DESIGN.md canonical colors)
# ---------------------------------------------------------------------------
SEVERITY_COLOR: dict[str, str] = {
    "critical": "#FF4545",
    "high": "#FF8C00",
    "medium": "#F0B429",
    "low": "#4B8BFF",
    "pass": "#22C55E",
    "info": "#6B7280",
}

CONFIDENCE_BADGE: dict[str, str] = {
    "high": "◉ Verified (CPE)",
    "medium": "◎ Unverified",
    "low": "○ Unconfirmed",
}

# ---------------------------------------------------------------------------
# Shared CSS
# ---------------------------------------------------------------------------
_BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 10pt;
    color: #1A2233;
    background: #fff;
    padding: 0;
}
header {
    background: #0F1623;
    color: #E2E8F0;
    padding: 24px 32px;
    margin-bottom: 24px;
}
header h1 { font-size: 16pt; letter-spacing: 0.5px; }
header .meta { font-size: 8pt; color: #94A3B8; margin-top: 6px; }
.content { padding: 0 32px 32px; }
h2 {
    font-size: 12pt;
    color: #0F1623;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 6px;
    margin: 20px 0 12px;
}
h3 { font-size: 10pt; color: #334155; margin: 14px 0 8px; }
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 8pt;
    font-weight: 600;
    color: #fff;
}
.badge-critical { background: #FF4545; }
.badge-high     { background: #FF8C00; }
.badge-medium   { background: #F0B429; color: #1A2233; }
.badge-low      { background: #4B8BFF; }
.badge-pass     { background: #22C55E; }
.badge-fail     { background: #FF4545; }
.badge-na       { background: #6B7280; }
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;
    font-size: 9pt;
}
th {
    background: #F1F5F9;
    text-align: left;
    padding: 7px 10px;
    font-weight: 600;
    color: #334155;
    border-bottom: 1px solid #CBD5E1;
}
td {
    padding: 6px 10px;
    border-bottom: 1px solid #E2E8F0;
    vertical-align: top;
}
tr:nth-child(even) td { background: #F8FAFC; }
.score-box {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 14pt;
    font-weight: 700;
    color: #fff;
    margin-right: 8px;
}
.kv { display: flex; gap: 24px; margin-bottom: 12px; flex-wrap: wrap; }
.kv-item label { font-size: 8pt; color: #6B7280; display: block; }
.kv-item span  { font-size: 10pt; font-weight: 600; }
footer {
    margin-top: 32px;
    font-size: 7.5pt;
    color: #94A3B8;
    border-top: 1px solid #E2E8F0;
    padding-top: 10px;
    text-align: center;
}
@page { margin: 1.5cm; }
"""


# ---------------------------------------------------------------------------
# Score → color helper
# ---------------------------------------------------------------------------
def _score_color(score: float | None) -> str:
    if score is None:
        return "#6B7280"
    pct = score * 100
    if pct >= 80:
        return "#22C55E"
    if pct >= 60:
        return "#F0B429"
    return "#FF4545"


# ---------------------------------------------------------------------------
# Exposure technical report
# ---------------------------------------------------------------------------
def _render_exposure(data: dict) -> str:
    asset = data["asset"]
    services = data.get("services", [])
    cves = data.get("cves", [])
    last_scan = data.get("last_scan")

    # Split CVEs by severity
    critical_high = [c for c in cves if c.get("cvss_score", 0) >= 7.0]
    medium_low = [c for c in cves if c.get("cvss_score", 0) < 7.0]

    scan_info = (
        f"{last_scan['started_at'][:10]}  ·  status: {last_scan['status']}"
        if last_scan
        else "No scans yet"
    )

    svc_rows = "".join(
        f"<tr><td><code>{s['port']}/{s['protocol']}</code></td>"
        f"<td>{s.get('service','—')}</td>"
        f"<td>{s.get('version','—')}</td>"
        f"<td>{s.get('cpe','—')}</td></tr>"
        for s in services
    )

    def cve_row(c: dict) -> str:
        score = c.get("cvss_score") or 0.0
        if score >= 9.0:
            sev = "critical"
        elif score >= 7.0:
            sev = "high"
        elif score >= 4.0:
            sev = "medium"
        else:
            sev = "low"
        conf = c.get("confidence", "low")
        badge = CONFIDENCE_BADGE.get(conf, conf)
        return (
            f"<tr><td><code>{c['cve_id']}</code></td>"
            f"<td><span class='badge badge-{sev}'>{score:.1f}</span></td>"
            f"<td>{badge}</td>"
            f"<td>{c.get('software','—')} {c.get('version','')}</td></tr>"
        )

    cve_ch_rows = "".join(cve_row(c) for c in critical_high)
    cve_ml_rows = "".join(cve_row(c) for c in medium_low)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{_BASE_CSS}</style></head><body>
<header>
  <h1>CiberCortex IA — Exposure Technical Report</h1>
  <div class="meta">CONFIDENTIAL · Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div>
</header>
<div class="content">
  <h2>Asset Information</h2>
  <div class="kv">
    <div class="kv-item"><label>Name</label><span>{asset.get('name','—')}</span></div>
    <div class="kv-item"><label>IP / Target</label><span><code>{asset.get('ip_address','—')}</code></span></div>
    <div class="kv-item"><label>Type</label><span>{asset.get('asset_type','—')}</span></div>
    <div class="kv-item"><label>Last Scan</label><span>{scan_info}</span></div>
  </div>

  <h2>Discovered Services ({len(services)})</h2>
  <table>
    <thead><tr><th>Port / Protocol</th><th>Service</th><th>Version</th><th>CPE</th></tr></thead>
    <tbody>{svc_rows if svc_rows else "<tr><td colspan='4'>No services discovered</td></tr>"}</tbody>
  </table>

  <h2>CVE Correlations — Critical &amp; High ({len(critical_high)})</h2>
  <table>
    <thead><tr><th>CVE ID</th><th>CVSS</th><th>Confidence</th><th>Software</th></tr></thead>
    <tbody>{cve_ch_rows if cve_ch_rows else "<tr><td colspan='4'>None</td></tr>"}</tbody>
  </table>

  <h2>CVE Correlations — Medium &amp; Low ({len(medium_low)})</h2>
  <table>
    <thead><tr><th>CVE ID</th><th>CVSS</th><th>Confidence</th><th>Software</th></tr></thead>
    <tbody>{cve_ml_rows if cve_ml_rows else "<tr><td colspan='4'>None</td></tr>"}</tbody>
  </table>

  <footer>CiberCortex IA · Exposure Technical Report · {asset.get('name','Asset')} · CONFIDENTIAL</footer>
</div></body></html>"""


# ---------------------------------------------------------------------------
# Hardening technical report
# ---------------------------------------------------------------------------
def _render_hardening(data: dict) -> str:
    asset = data["asset"]
    assessment = data.get("assessment")
    checks = data.get("checks", [])
    remediation = data.get("remediation", [])

    if not assessment:
        body = "<p>No assessment found for this asset.</p>"
        return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>{_BASE_CSS}</style></head><body>
<header><h1>CiberCortex IA — Hardening Technical Report</h1>
<div class='meta'>CONFIDENTIAL · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div></header>
<div class='content'>{body}<footer>CiberCortex IA · Hardening · {asset.get('name','Asset')}</footer>
</div></body></html>"""

    ws = assessment.get("weighted_score", 0) or 0
    rs = assessment.get("raw_score", 0) or 0
    sc = _score_color(ws)

    check_rows = "".join(
        f"<tr><td>{c['check_id']}</td>"
        f"<td>{c['title']}</td>"
        f"<td><span class='badge badge-{c.get(\"severity\",\"low\")}'>{c.get('severity','—')}</span></td>"
        f"<td><span class='badge badge-{c[\"result\"]}'>{c['result'].upper()}</span></td></tr>"
        for c in checks
    )

    rem_rows = "".join(
        f"<tr><td>{r['check_id']}</td>"
        f"<td>{r['title']}</td>"
        f"<td><span class='badge badge-{r.get(\"severity\",\"low\")}'>{r.get('severity','—')}</span></td>"
        f"<td>{r.get('effort_minutes','—')} min</td></tr>"
        for r in remediation
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{_BASE_CSS}</style></head><body>
<header>
  <h1>CiberCortex IA — Hardening Technical Report</h1>
  <div class="meta">CONFIDENTIAL · Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div>
</header>
<div class="content">
  <h2>Asset</h2>
  <div class="kv">
    <div class="kv-item"><label>Name</label><span>{asset.get('name','—')}</span></div>
    <div class="kv-item"><label>IP</label><span><code>{asset.get('ip_address','—')}</code></span></div>
  </div>

  <h2>Assessment Summary — {assessment.get('date','—')}</h2>
  <div class="kv">
    <div class="kv-item"><label>Benchmark</label>
      <span>{assessment.get('benchmark','—')} v{assessment.get('benchmark_version','')}</span></div>
    <div class="kv-item"><label>Weighted Score</label>
      <span class='score-box' style='background:{sc}'>{ws*100:.1f}%</span></div>
    <div class="kv-item"><label>Raw Score</label><span>{rs*100:.1f}%</span></div>
    <div class="kv-item"><label>Passed</label><span>{assessment.get('passed_checks',0)}</span></div>
    <div class="kv-item"><label>Failed</label><span>{assessment.get('failed_checks',0)}</span></div>
    <div class="kv-item"><label>N/A</label><span>{assessment.get('not_applicable_checks',0)}</span></div>
  </div>

  <h2>Check Results ({len(checks)})</h2>
  <table>
    <thead><tr><th>Check ID</th><th>Title</th><th>Severity</th><th>Result</th></tr></thead>
    <tbody>{check_rows if check_rows else "<tr><td colspan='4'>No check results</td></tr>"}</tbody>
  </table>

  <h2>Remediation Items ({len(remediation)})</h2>
  <table>
    <thead><tr><th>Check ID</th><th>Title</th><th>Severity</th><th>Effort</th></tr></thead>
    <tbody>{rem_rows if rem_rows else "<tr><td colspan='4'>None</td></tr>"}</tbody>
  </table>

  <footer>CiberCortex IA · Hardening Technical Report · {asset.get('name','Asset')} · CONFIDENTIAL</footer>
</div></body></html>"""


# ---------------------------------------------------------------------------
# Executive summary (abstract — no IPs, no CVE IDs, no versions)
# ---------------------------------------------------------------------------
def _render_executive(data: dict) -> str:
    asset_name = data.get("asset_name", "Asset")
    exposure = data.get("exposure", {})
    hardening = data.get("hardening", {})
    trend = data.get("trend", [])

    ws = hardening.get("weighted_score")
    sc = _score_color(ws)
    ws_display = f"{ws*100:.1f}%" if ws is not None else "N/A"

    cve_critical = exposure.get("critical_cves", 0)
    cve_high = exposure.get("high_cves", 0)
    cve_medium = exposure.get("medium_cves", 0)
    cve_low = exposure.get("low_cves", 0)

    trend_rows = "".join(
        f"<tr><td>{t['date']}</td><td>{t['weighted_score']*100:.1f}%</td></tr>"
        for t in trend
    )

    top_actions = data.get("top_actions", [])
    action_rows = "".join(
        f"<tr><td>P{a['priority']}</td><td>{a['title']}</td>"
        f"<td><span class='badge badge-{a[\"severity\"]}'>{a['severity']}</span></td></tr>"
        for a in top_actions
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{_BASE_CSS}</style></head><body>
<header>
  <h1>CiberCortex IA — Executive Security Summary</h1>
  <div class="meta">CONFIDENTIAL · {asset_name} ·
    Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div>
</header>
<div class="content">
  <h2>Security Posture</h2>
  <div class="kv">
    <div class="kv-item"><label>Asset</label><span>{asset_name}</span></div>
    <div class="kv-item"><label>Hardening Score</label>
      <span class='score-box' style='background:{sc}'>{ws_display}</span></div>
    <div class="kv-item"><label>Failed Controls</label>
      <span>{hardening.get('failed_checks', 0)}</span></div>
    <div class="kv-item"><label>Exposure: Critical / High</label>
      <span style='color:#FF4545;font-weight:700'>{cve_critical}</span>
      &nbsp;/&nbsp;
      <span style='color:#FF8C00;font-weight:700'>{cve_high}</span></div>
    <div class="kv-item"><label>Exposure: Medium / Low</label>
      <span>{cve_medium} / {cve_low}</span></div>
  </div>

  <h2>Hardening Score Trend</h2>
  <table>
    <thead><tr><th>Date</th><th>Score</th></tr></thead>
    <tbody>{trend_rows if trend_rows else "<tr><td colspan='2'>No history</td></tr>"}</tbody>
  </table>

  <h2>Priority Actions (Top {len(top_actions)})</h2>
  <table>
    <thead><tr><th>Priority</th><th>Action</th><th>Severity</th></tr></thead>
    <tbody>{action_rows if action_rows else "<tr><td colspan='3'>None</td></tr>"}</tbody>
  </table>

  <h3>Risk Note</h3>
  <p style="font-size:9pt;color:#475569;margin-top:8px;">
    Scores are weighted by severity (Critical×4 / High×3 / Medium×2 / Low×1).
    Technical details are available in the Analyst Technical Report.
    This document does not contain IP addresses, CVE identifiers, or software versions.
  </p>

  <footer>CiberCortex IA · Executive Summary · {asset_name} · CONFIDENTIAL</footer>
</div></body></html>"""


# ---------------------------------------------------------------------------
# Main entry point — called from API endpoint
# ---------------------------------------------------------------------------
_RENDERERS = {
    "exposure_technical": _render_exposure,
    "hardening_technical": _render_hardening,
    "executive_summary": _render_executive,
}


def _html_to_pdf(html: str) -> bytes:
    """Convert HTML string to PDF bytes using WeasyPrint (sync, CPU-bound)."""
    from weasyprint import HTML as WeasyHTML  # import here to allow mocking in tests

    return WeasyHTML(string=html).write_pdf()


async def generate_pdf(report_type: str, data: dict[str, Any]) -> bytes:
    """Async wrapper: render HTML then convert to PDF in thread pool."""
    renderer = _RENDERERS.get(report_type)
    if not renderer:
        raise ValueError(f"Unknown report type: {report_type}")

    html = renderer(data)
    loop = asyncio.get_event_loop()
    pdf_bytes: bytes = await loop.run_in_executor(None, _html_to_pdf, html)
    return pdf_bytes
