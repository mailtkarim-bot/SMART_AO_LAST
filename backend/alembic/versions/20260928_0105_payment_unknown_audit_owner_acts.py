"""Persist Patron validation of payment unknown audit."""
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op
revision = "20260928_0105"
down_revision = "20260927_0104"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None
def upgrade() -> None:
    op.create_table("payment_unknown_audit_owner_acts", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("case_id", sa.UUID(), nullable=False), sa.Column("owner_id", sa.UUID(), nullable=False), sa.Column("approved", sa.Boolean(), nullable=False), sa.Column("rationale", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_payment_unknown_audit_owner_acts__tenant_id"))
def downgrade() -> None:
    op.drop_table("payment_unknown_audit_owner_acts")
