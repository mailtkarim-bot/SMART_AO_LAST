"""Append-only sourced cash declarations per Case, with protected downgrade."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "20261102_0147"
down_revision = "20261027_0146"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cash_schedule_revisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("declaration_json", JSONB, nullable=False),
        sa.Column("source_snapshot_json", JSONB, nullable=False),
        sa.Column("justification", sa.String(2000), nullable=False),
        sa.Column("human_confirmed", sa.Boolean, nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "case_id", "revision", name="uq_cash_schedule_revision"),
        sa.CheckConstraint("revision>0", name="cash_schedule_revision_positive"),
        sa.CheckConstraint(
            "jsonb_typeof(declaration_json)='object' AND "
            "jsonb_typeof(source_snapshot_json)='object'",
            name="cash_schedule_objects",
        ),
        sa.CheckConstraint(
            "length(trim(justification))>0 AND human_confirmed", name="cash_schedule_consent"
        ),
    )
    op.create_index(
        "ix_cash_schedule_revisions_tenant_id", "cash_schedule_revisions", ["tenant_id"]
    )
    op.execute("""CREATE FUNCTION guard_cash_schedule() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'cash schedule history is append-only'; END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_cash_schedule_history BEFORE UPDATE OR DELETE ON cash_schedule_revisions
        FOR EACH ROW EXECUTE FUNCTION guard_cash_schedule();""")


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT EXISTS(SELECT 1 FROM cash_schedule_revisions)")):
        raise RuntimeError("CASH_SCHEDULE_HISTORY_DOWNGRADE_REFUSED")
    op.execute("DROP TRIGGER trg_cash_schedule_history ON cash_schedule_revisions")
    op.execute("DROP FUNCTION guard_cash_schedule()")
    op.drop_table("cash_schedule_revisions")
