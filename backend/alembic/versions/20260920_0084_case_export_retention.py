"""Persist separate Case export requests and retention facts."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260920_0084"
down_revision = "20260920_0083"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_export_requests",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("artifact_kind", sa.String(24), nullable=False),
        sa.Column("recipient_label", sa.String(240)),
        sa.Column("purpose", sa.String(2000), nullable=False),
        sa.Column("source_locator", sa.String(500)),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_export_requests__tenant_id_id"),
        sa.CheckConstraint(
            "artifact_kind IN ('CASE_DOSSIER', 'P7_RESULT', 'REX', 'AUDIT_TRAIL')",
            name="artifact_kind",
        ),
    )
    op.create_table(
        "case_retentions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("evidence_locator", sa.String(500), nullable=False),
        sa.Column("retention_basis", sa.String(24), nullable=False),
        sa.Column("retain_until", sa.Date(), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_retentions__tenant_id_id"),
        sa.CheckConstraint(
            "retention_basis IN ('MARKET_RECORD', 'OPEN_LITIGATION', 'INTERNAL_POLICY')",
            name="retention_basis",
        ),
    )


def downgrade() -> None:
    op.drop_table("case_retentions")
    op.drop_table("case_export_requests")
