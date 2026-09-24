# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractProofReviewRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_proof_reviews"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "proof_id"], ["contract_baseline_deviation_impacts.tenant_id", "contract_baseline_deviation_impacts.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_proof_reviews__tenant_id"),
        sa.UniqueConstraint("tenant_id", "proof_id", "reviewed_revision", name="uq_contract_proof_reviews__functional"),
        sa.CheckConstraint("reviewed_revision > 0", name="contract_review_revision_positive"),
        sa.CheckConstraint("decision IN ('ACCEPTED', 'REJECTED', 'NEEDS_CLARIFICATION')", name="contract_review_decision_closed"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    proof_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reviewer_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reviewed_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
