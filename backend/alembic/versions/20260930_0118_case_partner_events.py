"""Record case partner requests, receipts and Patron-declared engagement."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260930_0118"
down_revision = "20260930_0116"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_partner_events",
        sa.Column("event_id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("partner_id", sa.UUID(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(24), nullable=False),
        sa.Column("partner_kind", sa.String(24), nullable=False),
        sa.Column("partner_label", sa.String(240), nullable=False),
        sa.Column("related_event_id", sa.UUID(), nullable=True),
        sa.Column("source_locator", sa.String(500), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("validity_at_recording", sa.String(8), nullable=False),
        sa.Column("exclusions_state", sa.String(16), nullable=False),
        sa.Column("exclusions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("mandate_state", sa.String(24), nullable=False),
        sa.Column("mandate_source_locator", sa.String(500), nullable=True),
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
            name="fk_case_partner_events__case_same_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "related_event_id"],
            ["case_partner_events.tenant_id", "case_partner_events.event_id"],
            name="fk_case_partner_events__related_same_tenant",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "event_id", name="uq_case_partner_events__tenant_event"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "partner_id",
            "revision",
            name="uq_case_partner_events__partner_revision",
        ),
        sa.CheckConstraint("revision >= 1", name="case_partner_revision_positive"),
        sa.CheckConstraint(
            "event_type IN ('REQUESTED', 'RECEIVED', 'ENGAGEMENT_DECLARED')",
            name="case_partner_event_type",
        ),
        sa.CheckConstraint(
            "partner_kind IN ('SUPPLIER', 'SUBCONTRACTOR', 'CO_CONTRACTOR')",
            name="case_partner_kind",
        ),
        sa.CheckConstraint(
            "validity_at_recording IN ('UNKNOWN', 'VALID', 'EXPIRED')",
            name="case_partner_validity_at_recording",
        ),
        sa.CheckConstraint(
            "exclusions_state IN ('UNKNOWN', 'DECLARED')",
            name="case_partner_exclusions_state",
        ),
        sa.CheckConstraint(
            "mandate_state IN ("
            "'NOT_APPLICABLE', 'UNKNOWN', 'REQUESTED', 'RECEIVED', 'REVIEW_REQUIRED')",
            name="case_partner_mandate_state",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(exclusions_json) = 'array'",
            name="case_partner_exclusions_array",
        ),
        sa.CheckConstraint(
            "exclusions_state <> 'UNKNOWN' OR jsonb_array_length(exclusions_json) = 0",
            name="case_partner_unknown_exclusions_empty",
        ),
        sa.CheckConstraint(
            "mandate_state <> 'RECEIVED' OR mandate_source_locator IS NOT NULL",
            name="case_partner_received_mandate_source",
        ),
        sa.CheckConstraint(
            "event_type <> 'REQUESTED' OR (related_event_id IS NULL AND valid_until IS NULL "
            "AND validity_at_recording = 'UNKNOWN' AND exclusions_state = 'UNKNOWN' "
            "AND jsonb_array_length(exclusions_json) = 0)",
            name="case_partner_request_state_unknown",
        ),
        sa.CheckConstraint(
            "event_type <> 'ENGAGEMENT_DECLARED' OR related_event_id IS NOT NULL",
            name="case_partner_engagement_receipt_required",
        ),
    )
    op.create_index(
        "ix_case_partner_events__tenant_case_created",
        "case_partner_events",
        ["tenant_id", "case_id", "created_at", "event_id"],
    )
    op.create_index(
        "uq_case_partner_events__receipt_engagement",
        "case_partner_events",
        ["tenant_id", "related_event_id"],
        unique=True,
        postgresql_where=sa.text("event_type = 'ENGAGEMENT_DECLARED'"),
    )
    op.execute("""
        CREATE FUNCTION reject_case_partner_event_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'case partner events are append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_partner_events_append_only
        BEFORE UPDATE OR DELETE ON case_partner_events
        FOR EACH ROW EXECUTE FUNCTION reject_case_partner_event_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS case_partner_events_append_only ON case_partner_events")
    op.execute("DROP FUNCTION IF EXISTS reject_case_partner_event_mutation()")
    op.drop_index("uq_case_partner_events__receipt_engagement", table_name="case_partner_events")
    op.drop_index("ix_case_partner_events__tenant_case_created", table_name="case_partner_events")
    op.drop_table("case_partner_events")
