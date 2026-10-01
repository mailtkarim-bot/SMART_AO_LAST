"""Persist append-only human reviews of partner-offer scope comparability."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260930_0120"
down_revision = "20260930_0119"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "partner_offer_scope_reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("comparison_id", sa.UUID(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
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
            name="fk_partner_scope_review__case_same_tenant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_scope_review__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_partner_scope_review__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "comparison_id",
            "revision",
            name="uq_partner_scope_review__comparison_revision",
        ),
        sa.CheckConstraint("revision > 0", name="partner_scope_review_revision_positive"),
        sa.CheckConstraint(
            "decision IN ('SAME_SCOPE_CONFIRMED', 'DIFFERENT_SCOPE', 'NEEDS_CLARIFICATION')",
            name="partner_scope_review_decision_closed",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0",
            name="partner_scope_review_rationale_required",
        ),
    )
    op.create_index(
        "ix_partner_scope_reviews__tenant_case_comparison_revision",
        "partner_offer_scope_reviews",
        ["tenant_id", "case_id", "comparison_id", "revision"],
    )
    op.create_table(
        "partner_offer_scope_review_offers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("review_id", sa.UUID(), nullable=False),
        sa.Column("receipt_event_id", sa.UUID(), nullable=False),
        sa.Column("inclusion_state", sa.String(16), nullable=False),
        sa.Column("included_scope_note", sa.String(2000), nullable=True),
        sa.Column("exclusions_review_state", sa.String(16), nullable=False),
        sa.Column("transport_state", sa.String(16), nullable=False),
        sa.Column("transport_note", sa.String(1000), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "review_id"],
            [
                "partner_offer_scope_reviews.tenant_id",
                "partner_offer_scope_reviews.case_id",
                "partner_offer_scope_reviews.id",
            ],
            name="fk_partner_scope_review_offer__review_same_case",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "receipt_event_id"],
            [
                "case_partner_events.tenant_id",
                "case_partner_events.case_id",
                "case_partner_events.event_id",
            ],
            name="fk_partner_scope_review_offer__receipt_same_case",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_scope_review_offers__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "review_id",
            "receipt_event_id",
            name="uq_partner_scope_review_offer_receipt",
        ),
        sa.CheckConstraint(
            "inclusion_state IN ('UNKNOWN', 'DECLARED')",
            name="partner_scope_review_inclusion_state_closed",
        ),
        sa.CheckConstraint(
            "inclusion_state <> 'DECLARED' OR "
            "(included_scope_note IS NOT NULL AND length(trim(included_scope_note)) > 0)",
            name="partner_scope_review_declared_inclusion_note_required",
        ),
        sa.CheckConstraint(
            "exclusions_review_state IN ('UNKNOWN', 'REVIEWED')",
            name="partner_scope_review_exclusions_review_state_closed",
        ),
        sa.CheckConstraint(
            "transport_state IN ('UNKNOWN', 'INCLUDED', 'EXCLUDED', 'SEPARATE')",
            name="partner_scope_review_transport_state_closed",
        ),
        sa.CheckConstraint(
            "transport_state = 'UNKNOWN' OR "
            "(transport_note IS NOT NULL AND length(trim(transport_note)) > 0)",
            name="partner_scope_review_known_transport_note_required",
        ),
    )
    op.create_index(
        "ix_partner_scope_review_offers__tenant_case_review",
        "partner_offer_scope_review_offers",
        ["tenant_id", "case_id", "review_id"],
    )
    _install_append_only("partner_offer_scope_reviews", "partner_scope_reviews")
    _install_append_only("partner_offer_scope_review_offers", "partner_scope_review_offers")
    op.execute("""
        CREATE FUNCTION validate_partner_offer_scope_review() RETURNS trigger AS $$
        DECLARE
            offer_count integer;
            distinct_partner_count integer;
        BEGIN
            SELECT count(*), count(DISTINCT receipt.partner_id)
              INTO offer_count, distinct_partner_count
            FROM partner_offer_scope_review_offers review_offer
            JOIN case_partner_events receipt
              ON receipt.tenant_id = review_offer.tenant_id
             AND receipt.case_id = review_offer.case_id
             AND receipt.event_id = review_offer.receipt_event_id
            WHERE review_offer.tenant_id = NEW.tenant_id
              AND review_offer.case_id = NEW.case_id
              AND review_offer.review_id = NEW.id;

            IF offer_count < 2 OR offer_count > 20 OR distinct_partner_count <> offer_count THEN
                RAISE EXCEPTION 'partner scope review offer set invalid';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM partner_offer_scope_review_offers review_offer
                JOIN case_partner_events receipt
                  ON receipt.tenant_id = review_offer.tenant_id
                 AND receipt.case_id = review_offer.case_id
                 AND receipt.event_id = review_offer.receipt_event_id
                WHERE review_offer.tenant_id = NEW.tenant_id
                  AND review_offer.case_id = NEW.case_id
                  AND review_offer.review_id = NEW.id
                  AND (
                    receipt.event_type <> 'RECEIVED'
                    OR receipt.event_id IS DISTINCT FROM (
                        SELECT latest.event_id
                        FROM case_partner_events latest
                        WHERE latest.tenant_id = receipt.tenant_id
                          AND latest.case_id = receipt.case_id
                          AND latest.partner_id = receipt.partner_id
                          AND latest.event_type = 'RECEIVED'
                        ORDER BY latest.revision DESC
                        LIMIT 1
                    )
                  )
            ) THEN
                RAISE EXCEPTION 'partner scope review requires each latest received version';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM partner_offer_scope_review_offers review_offer
                JOIN case_partner_events receipt
                  ON receipt.tenant_id = review_offer.tenant_id
                 AND receipt.case_id = review_offer.case_id
                 AND receipt.event_id = review_offer.receipt_event_id
                WHERE review_offer.tenant_id = NEW.tenant_id
                  AND review_offer.case_id = NEW.case_id
                  AND review_offer.review_id = NEW.id
                  AND review_offer.exclusions_review_state = 'REVIEWED'
                  AND receipt.exclusions_state <> 'DECLARED'
            ) THEN
                RAISE EXCEPTION 'reviewed exclusions require a declared source';
            END IF;

            IF NEW.decision = 'SAME_SCOPE_CONFIRMED' AND EXISTS (
                SELECT 1
                FROM partner_offer_scope_review_offers review_offer
                JOIN case_partner_events receipt
                  ON receipt.tenant_id = review_offer.tenant_id
                 AND receipt.case_id = review_offer.case_id
                 AND receipt.event_id = review_offer.receipt_event_id
                WHERE review_offer.tenant_id = NEW.tenant_id
                  AND review_offer.case_id = NEW.case_id
                  AND review_offer.review_id = NEW.id
                  AND (
                    review_offer.inclusion_state <> 'DECLARED'
                    OR review_offer.exclusions_review_state <> 'REVIEWED'
                    OR review_offer.transport_state = 'UNKNOWN'
                    OR receipt.exclusions_state <> 'DECLARED'
                  )
            ) THEN
                RAISE EXCEPTION 'same-scope requires reviewed exclusions, inclusion and transport';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE CONSTRAINT TRIGGER partner_offer_scope_review_complete
        AFTER INSERT ON partner_offer_scope_reviews
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION validate_partner_offer_scope_review();
    """)


def _install_append_only(table_name: str, function_suffix: str) -> None:
    function_name = f"reject_{function_suffix}_mutation"
    trigger_name = f"{table_name}_append_only"
    op.execute(f"""
        CREATE FUNCTION {function_name}() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION '{table_name} is append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute(f"""
        CREATE TRIGGER {trigger_name}
        BEFORE UPDATE OR DELETE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION {function_name}();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS partner_offer_scope_review_complete ON partner_offer_scope_reviews"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_partner_offer_scope_review()")
    for table_name, function_suffix in (
        ("partner_offer_scope_review_offers", "partner_scope_review_offers"),
        ("partner_offer_scope_reviews", "partner_scope_reviews"),
    ):
        op.execute(f"DROP TRIGGER IF EXISTS {table_name}_append_only ON {table_name}")
        op.execute(f"DROP FUNCTION IF EXISTS reject_{function_suffix}_mutation()")
    op.drop_index(
        "ix_partner_scope_review_offers__tenant_case_review",
        table_name="partner_offer_scope_review_offers",
    )
    op.drop_table("partner_offer_scope_review_offers")
    op.drop_index(
        "ix_partner_scope_reviews__tenant_case_comparison_revision",
        table_name="partner_offer_scope_reviews",
    )
    op.drop_table("partner_offer_scope_reviews")
