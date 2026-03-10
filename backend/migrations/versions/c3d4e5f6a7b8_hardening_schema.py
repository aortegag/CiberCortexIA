"""hardening_schema

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-10 00:00:00.000000

Creates:
  - assessments
  - check_results
  - remediation_items
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # assessments
    # ------------------------------------------------------------------
    op.create_table(
        "assessments",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "asset_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "analyst_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("benchmark", sa.String(100), nullable=False),
        sa.Column("benchmark_version", sa.String(20), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("raw_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("weighted_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_checks", sa.Integer, nullable=False, server_default="0"),
        sa.Column("passed_checks", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed_checks", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "not_applicable_checks", sa.Integer, nullable=False, server_default="0"
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_assessments_asset_id", "assessments", ["asset_id"])
    op.create_index("ix_assessments_date", "assessments", ["date"])

    # ------------------------------------------------------------------
    # check_results
    # ------------------------------------------------------------------
    op.create_table(
        "check_results",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "assessment_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("check_id", sa.String(30), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("section", sa.String(100), nullable=False),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("evidence_type", sa.String(30), nullable=True),
        sa.Column("evidence_text", sa.Text, nullable=True),
        sa.Column("evidence_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_check_results_assessment_id", "check_results", ["assessment_id"]
    )
    op.create_index("ix_check_results_check_id", "check_results", ["check_id"])

    # ------------------------------------------------------------------
    # remediation_items
    # ------------------------------------------------------------------
    op.create_table(
        "remediation_items",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "check_result_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("check_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "assessment_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("check_id", sa.String(30), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("priority", sa.Integer, nullable=False),
        sa.Column("recommendation", sa.Text, nullable=False),
        sa.Column("effort_minutes", sa.Integer, nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_remediation_items_assessment_id",
        "remediation_items",
        ["assessment_id"],
    )
    op.create_index(
        "ix_remediation_items_asset_id", "remediation_items", ["asset_id"]
    )
    op.create_index(
        "ix_remediation_items_priority", "remediation_items", ["priority"]
    )


def downgrade() -> None:
    op.drop_table("remediation_items")
    op.drop_table("check_results")
    op.drop_table("assessments")
