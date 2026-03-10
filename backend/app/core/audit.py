"""
Audit log service — append-only, never update or delete.
All write operations in the platform should call audit.record().
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def record(
    db: AsyncSession,
    action: str,
    user_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """
    Append a new audit entry. Does NOT commit — caller is responsible for committing
    the enclosing transaction so the audit entry and the main operation are atomic.
    """
    entry = AuditLog(
        action=action,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
