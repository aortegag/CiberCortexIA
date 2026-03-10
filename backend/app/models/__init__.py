# Import all models so Base.metadata is fully populated for Alembic and tests
from app.models.user import User, UserRole  # noqa: F401
from app.models.asset import Asset, AssetStatus, AssetType  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
