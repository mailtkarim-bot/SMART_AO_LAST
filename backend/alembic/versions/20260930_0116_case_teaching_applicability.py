"""Persist human, source-bound teaching applicability assessments."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260930_0116"
down_revision = "20260930_0115"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_teaching_applicabilities",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("target_case_id", sa.UUID(), nullable=False),
        sa.Column("source_interview_id", sa.UUID(), nullable=False),
        sa.Column("source_rex_id", sa.UUID(), nullable=False),
        sa.Column("decision", sa.String(length=24), nullable=False),
        sa.Column("rationale", sa.String(length=2000), nullable=False),
        sa.Column("target_source_locator", sa.String(length=500), nullable=False),
        sa.Column("source_expires_on", sa.Date(), nullable=False),
        sa.Column("source_validity_at_recording", sa.String(length=8), nullable=False),
        sa.Column("source_snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "target_case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_case_teaching_applicabilities__target_case_same_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "source_interview_id"],
            ["case_interviews.tenant_id", "case_interviews.id"],
            name="fk_case_teaching_applicabilities__source_interview_same_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "source_rex_id"],
            ["case_rex.tenant_id", "case_rex.id"],
            name="fk_case_teaching_applicabilities__source_rex_same_tenant",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_teaching_applicabilities__tenant_id_id"
        ),
        sa.CheckConstraint(
            "decision IN ('APPLICABLE', 'NOT_APPLICABLE', 'REVIEW_REQUIRED')",
            name="case_teaching_applicability_decision",
        ),
        sa.CheckConstraint(
            "source_validity_at_recording IN ('USABLE', 'EXPIRED')",
            name="case_teaching_applicability_source_validity",
        ),
    )
    op.create_index(
        "ix_case_teaching_applicabilities__target_created",
        "case_teaching_applicabilities",
        ["tenant_id", "target_case_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_case_teaching_applicabilities__target_created",
        table_name="case_teaching_applicabilities",
    )
    op.drop_table("case_teaching_applicabilities")
