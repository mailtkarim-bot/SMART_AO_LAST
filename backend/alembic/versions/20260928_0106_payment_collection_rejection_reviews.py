"""Persist human reviews of partial payment collection rejections."""
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op
revision = "20260928_0106"
down_revision = "20260928_0105"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None
def upgrade() -> None:
    op.create_table("payment_collection_rejection_reviews", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("case_id", sa.UUID(), nullable=False), sa.Column("reviewer_id", sa.UUID(), nullable=False), sa.Column("rejected_count", sa.Integer(), nullable=False), sa.Column("decision", sa.String(32), nullable=False), sa.Column("rationale", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_payment_collection_rejection_reviews__tenant_id"), sa.CheckConstraint("decision IN ('ACKNOWLEDGED', 'FOLLOW_UP_REQUIRED')", name="payment_collection_rejection_review_decision_closed"), sa.CheckConstraint("rejected_count > 0", name="payment_collection_rejection_review_count_positive"))
def downgrade() -> None:
    op.drop_table("payment_collection_rejection_reviews")
