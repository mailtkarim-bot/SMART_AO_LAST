from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseP6ControlRecord(TenantScopedRecord, Base):
    __tablename__ = "case_p6_controls"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "order_id"],
            ["case_orders.tenant_id", "case_orders.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_p6_controls__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "order_id", name="uq_case_p6_controls__tenant_id_order_id"
        ),
        sa.CheckConstraint("decision IN ('APPROVED', 'REJECTED')", name="decision"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    order_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    lot_reference: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    reservations_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    rationale: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
