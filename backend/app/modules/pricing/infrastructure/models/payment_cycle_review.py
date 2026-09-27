# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PaymentCycleReviewRecord(TenantScopedRecord, Base):
    __tablename__ = "payment_cycle_reviews"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "cycle_id"], ["payment_post_reception_cycles.tenant_id", "payment_post_reception_cycles.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_payment_cycle_reviews__tenant_id"),
        sa.CheckConstraint("decision IN ('ACCEPTED_FOR_PLANNING', 'REVIEW_REQUIRED', 'REJECTED')", name="payment_cycle_review_decision_closed"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    cycle_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reviewer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
