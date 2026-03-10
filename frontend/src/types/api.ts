/**
 * CiberCortex IA — API types
 * Mirror of backend Pydantic schemas.
 * Keep in sync with backend/app/schemas/
 */

// -----------------------------------------------------------------------
// Auth
// -----------------------------------------------------------------------
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface UserMe {
  id: string;
  email: string;
  full_name: string;
  role: "admin" | "analyst" | "readonly";
  is_active: boolean;
  created_at: string;
}

// -----------------------------------------------------------------------
// Assets
// -----------------------------------------------------------------------
export type AssetStatus = "pending" | "authorized" | "decommissioned";

export interface Asset {
  id: string;
  name: string;
  ip_address: string;
  asset_type: string;
  status: AssetStatus;
  owner: string | null;
  tags: string[];
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssetCreate {
  name: string;
  ip_address: string;
  asset_type: string;
  owner?: string;
  tags?: string[];
  notes?: string;
}

// -----------------------------------------------------------------------
// Exposure — Discovery
// -----------------------------------------------------------------------
export type ScanJobStatus = "pending" | "running" | "completed" | "failed";

export interface ScanJob {
  id: string;
  asset_id: string;
  status: ScanJobStatus;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface DiscoveredService {
  id: string;
  asset_id: string;
  port: number;
  protocol: "tcp" | "udp";
  service_name: string | null;
  product: string | null;
  version: string | null;
  state: string;
  scan_job_id: string;
  discovered_at: string;
}

// -----------------------------------------------------------------------
// Exposure — CVE
// -----------------------------------------------------------------------
export type CVEConfidence = "high" | "medium" | "low";
export type Severity = "critical" | "high" | "medium" | "low" | "info";

export interface CVECorrelation {
  id: string;
  asset_id: string;
  service_id: string;
  cve_id: string;
  cvss_score: number | null;
  severity: Severity;
  confidence: CVEConfidence;
  description: string | null;
  published_date: string | null;
  correlated_at: string;
}

export interface AssetRiskSummary {
  asset_id: string;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  total_count: number;
}

// -----------------------------------------------------------------------
// Hardening
// -----------------------------------------------------------------------
export type CheckStatus = "pass" | "fail" | "not_applicable" | "not_tested";

export interface CatalogCheck {
  check_id: string;
  title: string;
  severity: Severity;
  section: string;
  recommendation: string;
  effort_minutes: number;
}

export interface CheckResultInput {
  check_id: string;
  status: CheckStatus;
  evidence_type: string | null;
  evidence_text: string | null;
  notes: string | null;
}

export interface CheckResult {
  id: string;
  assessment_id: string;
  check_id: string;
  title: string;
  severity: Severity;
  section: string;
  status: CheckStatus;
  evidence_type: string | null;
  evidence_text: string | null;
  notes: string | null;
  evidence_at: string | null;
}

export interface AssessmentScore {
  raw_score: number;
  weighted_score: number;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  not_applicable_checks: number;
}

export interface Assessment {
  id: string;
  asset_id: string;
  created_by_id: string;
  raw_score: number;
  weighted_score: number;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  not_applicable_checks: number;
  created_at: string;
}

export interface AssessmentDetail extends Assessment {
  check_results: CheckResult[];
}

export interface RemediationItem {
  id: string;
  assessment_id: string;
  check_id: string;
  title: string;
  severity: Severity;
  effort_minutes: number;
  recommendation: string;
  status: "open" | "in_progress" | "resolved";
  resolved_at: string | null;
}

export interface AssetScoreResponse {
  asset_id: string;
  latest_score: AssessmentScore | null;
  trend: AssessmentScore[];
}

// -----------------------------------------------------------------------
// Reports
// -----------------------------------------------------------------------
export type ReportType =
  | "exposure_technical"
  | "hardening_technical"
  | "executive_summary";

export type ReportStatus = "generating" | "ready" | "failed";

export interface Report {
  id: string;
  asset_id: string | null;
  created_by_id: string | null;
  report_type: ReportType;
  status: ReportStatus;
  title: string;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

// -----------------------------------------------------------------------
// AI Assist
// -----------------------------------------------------------------------
export interface AIExplanationResponse {
  explanation: string;
  cached: boolean;
  requests_remaining: number;
}

export interface AIUsage {
  requests_remaining: number;
  limit_per_hour: number;
  cache_ttl_hours: number;
}

// -----------------------------------------------------------------------
// Pagination / common
// -----------------------------------------------------------------------
export interface ApiError {
  detail: string | { msg: string; type: string }[];
}
