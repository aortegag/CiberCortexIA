"""Exposure schema: scan_jobs, discovered_services, cve_correlations

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-10 01:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── scan_jobs ──────────────────────────────────────────────────────────
    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("scan_type", sa.String(30), nullable=False, server_default="nmap_tcp"),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scan_jobs_asset_id", "scan_jobs", ["asset_id"])
    op.create_index("ix_scan_jobs_status", "scan_jobs", ["status"])

    # ── discovered_services ────────────────────────────────────────────────
    op.create_table(
        "discovered_services",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scan_job_id", sa.Uuid(), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("protocol", sa.String(10), nullable=False, server_default="tcp"),
        sa.Column("service", sa.String(100), nullable=False),
        sa.Column("version", sa.String(255), nullable=True),
        sa.Column("banner", sa.Text(), nullable=True),
        sa.Column("cpe", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["scan_job_id"], ["scan_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_discovered_services_scan_job_id", "discovered_services", ["scan_job_id"])

    # ── cve_correlations ───────────────────────────────────────────────────
    op.create_table(
        "cve_correlations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("scan_job_id", sa.Uuid(), nullable=True),
        sa.Column("discovered_service_id", sa.Uuid(), nullable=True),
        sa.Column("cve_id", sa.String(30), nullable=False),
        sa.Column("cvss_score", sa.Float(), nullable=True),
        sa.Column("cvss_vector", sa.String(100), nullable=True),
        sa.Column("cvss_version", sa.String(10), nullable=True),
        sa.Column("software", sa.String(255), nullable=False),
        sa.Column("version", sa.String(100), nullable=True),
        sa.Column("confidence", sa.String(10), nullable=False, server_default="medium"),
        sa.Column("evidence_source", sa.String(30), nullable=False),
        sa.Column("evidence_data", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scan_job_id"], ["scan_jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["discovered_service_id"], ["discovered_services.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("asset_id", "cve_id", name="uq_cve_per_asset"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cve_correlations_asset_id", "cve_correlations", ["asset_id"])
    op.create_index("ix_cve_correlations_cve_id", "cve_correlations", ["cve_id"])


def downgrade() -> None:
    op.drop_table("cve_correlations")
    op.drop_table("discovered_services")
    op.drop_table("scan_jobs")
