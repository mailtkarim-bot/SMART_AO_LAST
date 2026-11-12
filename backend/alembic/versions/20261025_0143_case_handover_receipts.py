"""Append-only operational handover receipts, distinct from contract acceptance."""

import sqlalchemy as sa
from alembic import op

revision = "20261025_0143"
down_revision = "20261023_0142"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
CREATE TABLE case_handover_receipts (
	tenant_id UUID NOT NULL,

	id UUID NOT NULL,

	case_id UUID NOT NULL,

	snapshot_id UUID NOT NULL,

	snapshot_revision INTEGER NOT NULL,

	view_sha256 CHAR(64) NOT NULL,

	receipt_kind VARCHAR(32) NOT NULL,

	note TEXT NOT NULL,

	actor_id UUID NOT NULL,

	membership_id UUID NOT NULL,

	command_id UUID NOT NULL,

	idempotency_key UUID NOT NULL,

	correlation_id UUID,

	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,

	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,

	CONSTRAINT pk_case_handover_receipts PRIMARY KEY (tenant_id,
id),

	CONSTRAINT fk_case_handover_receipts__case_handover_snapshots__tenant_id FOREIGN KEY(tenant_id,
case_id,
snapshot_id)
REFERENCES case_handover_snapshots (tenant_id,
case_id,
id)
ON DELETE RESTRICT,

	CONSTRAINT fk_case_handover_receipts__cases__tenant_id FOREIGN KEY(tenant_id,
case_id)
REFERENCES cases (tenant_id,
id)
ON DELETE RESTRICT,

	CONSTRAINT fk_case_handover_receipts__tenant_memberships__tenant_id FOREIGN KEY(tenant_id,
membership_id)
REFERENCES tenant_memberships (tenant_id,
id)
ON DELETE RESTRICT,

	CONSTRAINT uq_handover_receipt__tenant_id UNIQUE (tenant_id,
id),

	CONSTRAINT uq_handover_receipt__command UNIQUE (tenant_id,
command_id),

	CONSTRAINT uq_handover_receipt__idempotency UNIQUE (tenant_id,
idempotency_key),

	CONSTRAINT ck_case_handover_receipts__snapshot_revision_positive CHECK (snapshot_revision > 0),

	CONSTRAINT ck_case_handover_receipts__view_sha256 CHECK (view_sha256 ~ '^[a-f0-9]{64}$'),

	CONSTRAINT ck_case_handover_receipts__receipt_kind
        CHECK (receipt_kind IN ('RECEIVED','RECEIVED_WITH_GAPS')),

	CONSTRAINT ck_case_handover_receipts__note_required CHECK (length(trim(note)) > 0)
)


""")
    op.execute("""CREATE INDEX ix_handover_receipts__case_snapshot
ON case_handover_receipts (tenant_id,
case_id,
snapshot_id,
created_at)
""")
    op.execute("""
        CREATE FUNCTION guard_case_handover_receipt() RETURNS trigger AS $$
        BEGIN
            IF TG_OP <> 'INSERT' THEN
                RAISE EXCEPTION 'handover receipts are append-only';
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM case_handover_snapshots
                WHERE tenant_id = NEW.tenant_id AND case_id = NEW.case_id
                  AND id = NEW.snapshot_id AND revision = NEW.snapshot_revision
            ) THEN
                RAISE EXCEPTION 'handover receipt snapshot revision mismatch';
            END IF;
            RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_case_handover_receipts_guard
        BEFORE INSERT OR UPDATE OR DELETE ON case_handover_receipts
        FOR EACH ROW EXECUTE FUNCTION guard_case_handover_receipt();
    """)


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT EXISTS (SELECT 1 FROM case_handover_receipts)")):
        raise RuntimeError("cannot downgrade with operational handover receipts")
    op.execute("DROP TRIGGER trg_case_handover_receipts_guard ON case_handover_receipts")
    op.execute("DROP FUNCTION guard_case_handover_receipt()")
    op.drop_table("case_handover_receipts")
