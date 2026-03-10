# Import all models so Base.metadata is fully populated for Alembic and tests
from app.models.user import User, UserRole  # noqa: F401
from app.models.asset import Asset, AssetStatus, AssetType  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.scan_job import ScanJob, ScanJobStatus, ScanJobType  # noqa: F401
from app.models.discovered_service import DiscoveredService  # noqa: F401
from app.models.cve_correlation import CVECorrelation, CVEConfidence, CVEEvidenceSource  # noqa: F401
from app.models.assessment import Assessment, AssessmentStatus  # noqa: F401
from app.models.check_result import CheckResult, CheckResultStatus, EvidenceType  # noqa: F401
from app.models.remediation_item import RemediationItem  # noqa: F401
