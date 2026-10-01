from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PartnerOfferScopeReviewRecord(TenantScopedRecord, Base):
    __tablename__ = "partner_offer_scope_reviews"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
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
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint(
            "decision IN ('SAME_SCOPE_CONFIRMED', 'DIFFERENT_SCOPE', 'NEEDS_CLARIFICATION')",
            name="decision_closed",
        ),
        sa.CheckConstraint("length(trim(rationale)) > 0", name="rationale_required"),
        sa.Index(
            "ix_partner_scope_reviews__tenant_case_comparison_revision",
            "tenant_id",
            "case_id",
            "comparison_id",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    comparison_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class PartnerOfferScopeReviewOfferRecord(TenantScopedRecord, Base):
    __tablename__ = "partner_offer_scope_review_offers"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "review_id"],
            [
                "partner_offer_scope_reviews.tenant_id",
                "partner_offer_scope_reviews.case_id",
                "partner_offer_scope_reviews.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "receipt_event_id"],
            [
                "case_partner_events.tenant_id",
                "case_partner_events.case_id",
                "case_partner_events.event_id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_scope_review_offers__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "review_id",
            "receipt_event_id",
            name="uq_partner_scope_review_offer_receipt",
        ),
        sa.CheckConstraint(
            "inclusion_state IN ('UNKNOWN', 'DECLARED')", name="inclusion_state_closed"
        ),
        sa.CheckConstraint(
            "inclusion_state <> 'DECLARED' OR "
            "(included_scope_note IS NOT NULL AND length(trim(included_scope_note)) > 0)",
            name="declared_inclusion_note_required",
        ),
        sa.CheckConstraint(
            "exclusions_review_state IN ('UNKNOWN', 'REVIEWED')",
            name="exclusions_review_state_closed",
        ),
        sa.CheckConstraint(
            "transport_state IN ('UNKNOWN', 'INCLUDED', 'EXCLUDED', 'SEPARATE')",
            name="transport_state_closed",
        ),
        sa.CheckConstraint(
            "transport_state = 'UNKNOWN' OR "
            "(transport_note IS NOT NULL AND length(trim(transport_note)) > 0)",
            name="known_transport_note_required",
        ),
        sa.Index(
            "ix_partner_scope_review_offers__tenant_case_review",
            "tenant_id",
            "case_id",
            "review_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    review_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    receipt_event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    inclusion_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    included_scope_note: Mapped[str | None] = mapped_column(sa.String(2000))
    exclusions_review_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    transport_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    transport_note: Mapped[str | None] = mapped_column(sa.String(1000))
