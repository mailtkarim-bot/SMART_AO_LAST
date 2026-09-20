"""Append-only DCE contribution conflict register."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260920_0090"
down_revision = "20260920_0089"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dce_requirement_contributions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("requirement_id", sa.UUID(), nullable=False),
        sa.Column("observed_revision", sa.Integer(), nullable=False),
        sa.Column("current_revision_at_submission", sa.Integer(), nullable=False),
        sa.Column("author_actor_id", sa.UUID(), nullable=False),
        sa.Column("source_locator", sa.String(500), nullable=False),
        sa.Column("basis_fingerprint", sa.CHAR(64), nullable=False),
        sa.Column("proposed_outcome", sa.String(32), nullable=False),
        sa.Column("proposed_reason_code", sa.String(64), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("contributed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], name="fk_dce_contrib__tenant", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "requirement_id"],
            ["dce_requirements.tenant_id", "dce_requirements.id"],
            name="fk_dce_contrib__requirement",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_dce_contrib__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "author_actor_id", "idempotency_key", name="uq_dce_contrib__idempotency"
        ),
        sa.CheckConstraint("observed_revision >= 0", name="observed_revision_nonnegative"),
        sa.CheckConstraint(
            "proposed_outcome IN ('CONFIRMED', 'REVIEW_REQUIRED', 'NOT_APPLICABLE')",
            name="proposed_outcome",
        ),
        sa.Index(
            "ix_dce_contrib__tenant_requirement_revision",
            "tenant_id",
            "requirement_id",
            "observed_revision",
        ),
    )
    op.create_table(
        "dce_requirement_conflicts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("requirement_id", sa.UUID(), nullable=False),
        sa.Column("observed_revision", sa.Integer(), nullable=False),
        sa.Column("first_contribution_id", sa.UUID(), nullable=False),
        sa.Column("second_contribution_id", sa.UUID(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "requirement_id"],
            ["dce_requirements.tenant_id", "dce_requirements.id"],
            name="fk_dce_conflict__requirement",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "first_contribution_id"],
            ["dce_requirement_contributions.tenant_id", "dce_requirement_contributions.id"],
            name="fk_dce_conflict__first_contribution",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "second_contribution_id"],
            ["dce_requirement_contributions.tenant_id", "dce_requirement_contributions.id"],
            name="fk_dce_conflict__second_contribution",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_dce_conflict__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "requirement_id",
            "observed_revision",
            name="uq_dce_conflict__requirement_revision",
        ),
        sa.CheckConstraint("observed_revision >= 0", name="observed_revision_nonnegative"),
    )
    op.create_table(
        "dce_requirement_conflict_resolutions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("conflict_id", sa.UUID(), nullable=False),
        sa.Column("selected_contribution_id", sa.UUID(), nullable=False),
        sa.Column("resolved_by_actor_id", sa.UUID(), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "conflict_id"],
            ["dce_requirement_conflicts.tenant_id", "dce_requirement_conflicts.id"],
            name="fk_dce_resolution__conflict",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "selected_contribution_id"],
            ["dce_requirement_contributions.tenant_id", "dce_requirement_contributions.id"],
            name="fk_dce_resolution__selected_contribution",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_dce_resolution__tenant_id"),
        sa.UniqueConstraint("tenant_id", "conflict_id", name="uq_dce_resolution__conflict"),
        sa.UniqueConstraint(
            "tenant_id", "conflict_id", "idempotency_key", name="uq_dce_resolution__idempotency"
        ),
    )


def downgrade() -> None:
    op.drop_table("dce_requirement_conflict_resolutions")
    op.drop_table("dce_requirement_conflicts")
    op.drop_table("dce_requirement_contributions")
