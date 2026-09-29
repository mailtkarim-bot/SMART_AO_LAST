# ruff: noqa: E501, I001
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PostReceptionObligationTransitionRecord(TenantScopedRecord, Base):
    __tablename__ = "post_reception_obligation_transitions"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "obligation_id"], ["post_reception_obligations.tenant_id", "post_reception_obligations.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_post_reception_obligation_transitions__tenant_id"),
        sa.UniqueConstraint("tenant_id", "obligation_id", "revision", name="uq_post_reception_obligation_transitions__revision"),
        sa.CheckConstraint("revision > 0", name="post_reception_obligation_transition_revision_positive"),
        sa.CheckConstraint("previous_status IN ('REVIEW_REQUIRED', 'IN_PROGRESS', 'FOLLOW_UP_REQUIRED', 'UNKNOWN')", name="post_reception_obligation_transition_previous_closed"),
        sa.CheckConstraint("resulting_status IN ('IN_PROGRESS', 'FOLLOW_UP_REQUIRED', 'UNKNOWN', 'COMPLETED')", name="post_reception_obligation_transition_result_closed"),
        sa.CheckConstraint("resulting_status != 'COMPLETED' OR jsonb_array_length(evidence_refs_json) > 0", name="post_reception_obligation_completion_requires_proof"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    obligation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    previous_status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    resulting_status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
