# ruff: noqa: E501, I001
from __future__ import annotations
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.platform.persistence.base import Base, TenantScopedRecord

class PaymentCollectionRejectionReviewRecord(TenantScopedRecord, Base):
    __tablename__ = "payment_collection_rejection_reviews"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_payment_collection_rejection_reviews__tenant_id"),
        sa.CheckConstraint("decision IN ('ACKNOWLEDGED', 'FOLLOW_UP_REQUIRED')", name="payment_collection_rejection_review_decision_closed"),
        sa.CheckConstraint("rejected_count > 0", name="payment_collection_rejection_review_count_positive"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reviewer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    rejected_count: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
