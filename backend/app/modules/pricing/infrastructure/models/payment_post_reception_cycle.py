# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PaymentPostReceptionCycleRecord(TenantScopedRecord, Base):
    __tablename__ = "payment_post_reception_cycles"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_payment_post_reception_cycles__tenant_id"),
        sa.CheckConstraint("status IN ('SOURCE_SIGNAL_ONLY', 'REVIEW_REQUIRED', 'UNKNOWN')", name="payment_cycle_status_closed"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    trigger_event: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    cash_assumption: Mapped[str | None] = mapped_column(sa.Text)
    post_reception_cost_note: Mapped[str | None] = mapped_column(sa.Text)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

