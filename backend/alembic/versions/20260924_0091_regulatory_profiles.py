"""Persist sourced, versioned regulatory applicability profiles."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260924_0091"
down_revision = "20260920_0090"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "regulatory_profiles",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("profile_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("facts_json", JSONB(), nullable=False),
        sa.Column("source_refs_json", JSONB(), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_actor_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_regulatory_profiles__tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_regulatory_profiles__case",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_regulatory_profiles__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "profile_version", name="uq_regulatory_profiles__case_version"
        ),
        sa.CheckConstraint("profile_version > 0", name="profile_version_positive"),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'FUTURE', 'EXPIRED', 'UNKNOWN_APPLICABILITY', 'REVIEW_REQUIRED')",
            name="status_closed",
        ),
        sa.CheckConstraint("jsonb_typeof(facts_json) = 'object'", name="facts_object"),
        sa.CheckConstraint(
            "jsonb_typeof(source_refs_json) = 'array' AND jsonb_array_length(source_refs_json) > 0",
            name="source_refs_nonempty",
        ),
        sa.Index(
            "ix_regulatory_profiles__tenant_case_version",
            "tenant_id",
            "case_id",
            "profile_version",
        ),
    )


def downgrade() -> None:
    op.drop_table("regulatory_profiles")
