"""Store Patron-private, source-referenced partner offer price declarations."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260930_0119"
down_revision = "20260930_0118"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_case_partner_events__tenant_case_event",
        "case_partner_events",
        ["tenant_id", "case_id", "event_id"],
    )
    op.create_table(
        "partner_offer_price_declarations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("receipt_event_id", sa.UUID(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("amount_as_declared", sa.String(80), nullable=False),
        sa.Column("currency_code", sa.CHAR(3), nullable=False),
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
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_partner_offer_price__case_same_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "receipt_event_id"],
            [
                "case_partner_events.tenant_id",
                "case_partner_events.case_id",
                "case_partner_events.event_id",
            ],
            name="fk_partner_offer_price__receipt_same_case",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_prices__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "receipt_event_id",
            "revision",
            name="uq_partner_offer_price_receipt_revision",
        ),
        sa.CheckConstraint("revision > 0", name="partner_offer_price_revision_positive"),
        sa.CheckConstraint(
            "amount_as_declared ~ '^[0-9]+([,.][0-9]{1,6})?$'",
            name="partner_offer_price_amount_format",
        ),
        sa.CheckConstraint(
            "currency_code ~ '^[A-Z]{3}$'",
            name="partner_offer_price_currency_format",
        ),
    )
    op.create_index(
        "ix_partner_offer_prices__tenant_case_receipt_revision",
        "partner_offer_price_declarations",
        ["tenant_id", "case_id", "receipt_event_id", "revision"],
    )
    op.execute("""
        CREATE FUNCTION validate_partner_offer_price_receipt() RETURNS trigger AS $$
        DECLARE
            receipt_partner_id uuid;
            latest_receipt_event_id uuid;
        BEGIN
            SELECT partner_id INTO receipt_partner_id
            FROM case_partner_events
            WHERE tenant_id = NEW.tenant_id
              AND case_id = NEW.case_id
              AND event_id = NEW.receipt_event_id
              AND event_type = 'RECEIVED';
            IF receipt_partner_id IS NULL THEN
                RAISE EXCEPTION 'partner offer price requires a received partner event';
            END IF;
            SELECT event_id INTO latest_receipt_event_id
            FROM case_partner_events
            WHERE tenant_id = NEW.tenant_id
              AND case_id = NEW.case_id
              AND partner_id = receipt_partner_id
              AND event_type = 'RECEIVED'
            ORDER BY revision DESC
            LIMIT 1;
            IF latest_receipt_event_id IS DISTINCT FROM NEW.receipt_event_id THEN
                RAISE EXCEPTION 'partner offer price requires the latest received version';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER partner_offer_price_receipt_required
        BEFORE INSERT ON partner_offer_price_declarations
        FOR EACH ROW EXECUTE FUNCTION validate_partner_offer_price_receipt();
    """)
    op.execute("""
        CREATE FUNCTION reject_partner_offer_price_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'partner offer price declarations are append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER partner_offer_price_declarations_append_only
        BEFORE UPDATE OR DELETE ON partner_offer_price_declarations
        FOR EACH ROW EXECUTE FUNCTION reject_partner_offer_price_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS partner_offer_price_declarations_append_only "
        "ON partner_offer_price_declarations"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_partner_offer_price_mutation()")
    op.execute(
        "DROP TRIGGER IF EXISTS partner_offer_price_receipt_required "
        "ON partner_offer_price_declarations"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_partner_offer_price_receipt()")
    op.drop_index(
        "ix_partner_offer_prices__tenant_case_receipt_revision",
        table_name="partner_offer_price_declarations",
    )
    op.drop_table("partner_offer_price_declarations")
    op.drop_constraint(
        "uq_case_partner_events__tenant_case_event",
        "case_partner_events",
        type_="unique",
    )
