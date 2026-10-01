from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseTeachingApplicabilityRecord(TenantScopedRecord, Base):
    __tablename__ = "case_teaching_applicabilities"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "target_case_id"],
            ["cases.tenant_id", "cases.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "source_interview_id"],
            ["case_interviews.tenant_id", "case_interviews.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "source_rex_id"],
            ["case_rex.tenant_id", "case_rex.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_teaching_applicabilities__tenant_id_id"
        ),
        sa.CheckConstraint(
            "decision IN ('APPLICABLE', 'NOT_APPLICABLE', 'REVIEW_REQUIRED')",
            name="case_teaching_applicability_decision",
        ),
        sa.CheckConstraint(
            "source_validity_at_recording IN ('USABLE', 'EXPIRED')",
            name="case_teaching_applicability_source_validity",
        ),
        sa.Index(
            "ix_case_teaching_applicabilities__target_created",
            "tenant_id",
            "target_case_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    target_case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    source_interview_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    source_rex_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    target_source_locator: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    source_expires_on: Mapped[date] = mapped_column(sa.Date, nullable=False)
    source_validity_at_recording: Mapped[str] = mapped_column(sa.String(8), nullable=False)
    source_snapshot_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
