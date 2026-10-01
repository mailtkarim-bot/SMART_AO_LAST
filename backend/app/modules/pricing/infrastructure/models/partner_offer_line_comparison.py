from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


def _source_field_constraints(name: str, _max_length: int) -> tuple[sa.CheckConstraint, ...]:
    field_key = {
        "line_locator": "loc",
        "item_reference": "ref",
        "designation": "label",
        "unit": "unit",
        "quantity": "qty",
    }[name]
    return (
        sa.CheckConstraint(
            f"{name}_state IN ('UNKNOWN', 'DECLARED')",
            name=f"{field_key}_state",
        ),
        sa.CheckConstraint(
            f"({name}_state = 'UNKNOWN' AND {name} IS NULL) OR "
            f"({name}_state = 'DECLARED' AND {name} IS NOT NULL AND length(trim({name})) > 0)",
            name=f"{field_key}_value",
        ),
    )


class PartnerOfferLineComparisonRecord(TenantScopedRecord, Base):
    __tablename__ = "partner_offer_line_comparisons"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_partner_offer_line_comparisons__case",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "scope_review_id"],
            [
                "partner_offer_scope_reviews.tenant_id",
                "partner_offer_scope_reviews.case_id",
                "partner_offer_scope_reviews.id",
            ],
            name="fk_partner_offer_line_comparisons__scope_review",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_line_comparisons__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_partner_offer_line_comparisons__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "comparison_id",
            "revision",
            name="uq_partner_offer_line_comparison_revision",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.Index(
            "ix_partner_offer_line_cmp__tenant_case_revision",
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
    scope_review_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class PartnerOfferLineGroupRecord(TenantScopedRecord, Base):
    __tablename__ = "partner_offer_line_groups"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "comparison_record_id"],
            [
                "partner_offer_line_comparisons.tenant_id",
                "partner_offer_line_comparisons.case_id",
                "partner_offer_line_comparisons.id",
            ],
            name="fk_partner_offer_line_groups__comparison",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_line_groups__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_partner_offer_line_groups__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "comparison_record_id",
            "group_id",
            name="uq_partner_offer_line_group_revision_id",
        ),
        sa.CheckConstraint(
            "disposition IN ('LINKED_BY_PATRON', 'DISTINCT_POSITIONS', 'NEEDS_CLARIFICATION')",
            name="disposition_closed",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0", name="group_rationale_required"
        ),
        sa.Index(
            "ix_partner_offer_line_groups__tenant_case_comparison",
            "tenant_id",
            "case_id",
            "comparison_record_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    comparison_record_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    group_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    disposition: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.String(2000), nullable=False)


class PartnerOfferLineMemberRecord(TenantScopedRecord, Base):
    __tablename__ = "partner_offer_line_members"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "group_record_id"],
            [
                "partner_offer_line_groups.tenant_id",
                "partner_offer_line_groups.case_id",
                "partner_offer_line_groups.id",
            ],
            name="fk_partner_offer_line_members__group",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "receipt_event_id"],
            [
                "case_partner_events.tenant_id",
                "case_partner_events.case_id",
                "case_partner_events.event_id",
            ],
            name="fk_partner_offer_line_members__receipt",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_line_members__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "group_record_id",
            "receipt_event_id",
            name="uq_partner_offer_line_member_receipt",
        ),
        *_source_field_constraints("line_locator", 500),
        *_source_field_constraints("item_reference", 120),
        *_source_field_constraints("designation", 500),
        *_source_field_constraints("unit", 32),
        *_source_field_constraints("quantity", 80),
        sa.Index(
            "ix_partner_offer_line_members__tenant_case_group",
            "tenant_id",
            "case_id",
            "group_record_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    group_record_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    receipt_event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    line_locator_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    line_locator: Mapped[str | None] = mapped_column(sa.String(500))
    item_reference_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    item_reference: Mapped[str | None] = mapped_column(sa.String(120))
    designation_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    designation: Mapped[str | None] = mapped_column(sa.String(500))
    unit_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    unit: Mapped[str | None] = mapped_column(sa.String(32))
    quantity_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    quantity: Mapped[str | None] = mapped_column(sa.String(80))
