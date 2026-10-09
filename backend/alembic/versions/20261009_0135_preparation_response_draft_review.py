"""Bind preparation reviews and corrections to exact response draft versions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261009_0135"
down_revision = "20261008_0134"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    for table in ("preparation_reviews", "preparation_review_corrections"):
        op.add_column(table, sa.Column("target_draft_id", postgresql.UUID(as_uuid=True)))
        op.add_column(table, sa.Column("target_draft_version", sa.Integer()))
        op.add_column(table, sa.Column("target_content_sha256", sa.CHAR(length=64)))
        op.create_check_constraint(
            f"ck_{table}__target_draft_exact",
            table,
            "(target_draft_id IS NULL AND target_draft_version IS NULL AND "
            "target_content_sha256 IS NULL) OR "
            "(target_draft_id IS NOT NULL AND target_draft_version IS NOT NULL AND "
            "target_content_sha256 IS NOT NULL AND target_content_sha256 ~ '^[0-9a-f]{64}$')",
        )
        op.create_foreign_key(
            f"fk_{table}__draft",
            table,
            "technical_response_drafts",
            ["tenant_id", "target_draft_id", "target_draft_version"],
            ["tenant_id", "draft_id", "version"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    for table in ("preparation_review_corrections", "preparation_reviews"):
        op.drop_constraint(f"fk_{table}__draft", table, type_="foreignkey")
        op.drop_constraint(f"ck_{table}__target_draft_exact", table, type_="check")
        op.drop_column(table, "target_content_sha256")
        op.drop_column(table, "target_draft_version")
        op.drop_column(table, "target_draft_id")
