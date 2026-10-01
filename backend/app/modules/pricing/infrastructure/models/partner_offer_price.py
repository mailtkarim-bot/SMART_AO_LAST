from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PartnerOfferPriceDeclarationRecord(TenantScopedRecord, Base):
    __tablename__ = "partner_offer_price_declarations"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
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
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_prices__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "receipt_event_id",
            "revision",
            name="uq_partner_offer_price_receipt_revision",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint(
            "amount_as_declared ~ '^[0-9]+([,.][0-9]{1,6})?$'",
            name="amount_format",
        ),
        sa.CheckConstraint("currency_code ~ '^[A-Z]{3}$'", name="currency_code_format"),
        sa.Index(
            "ix_partner_offer_prices__tenant_case_receipt_revision",
            "tenant_id",
            "case_id",
            "receipt_event_id",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    receipt_event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    amount_as_declared: Mapped[str] = mapped_column(sa.String(80), nullable=False)
    currency_code: Mapped[str] = mapped_column(sa.CHAR(3), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
