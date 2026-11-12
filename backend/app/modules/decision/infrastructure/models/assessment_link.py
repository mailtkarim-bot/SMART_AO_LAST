from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class DecisionConditionAssessmentLinkRecord(TenantScopedRecord, Base):
    __tablename__ = "decision_condition_assessment_links"
    __table_args__ = (
        sa.PrimaryKeyConstraint("tenant_id", "id"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"]),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "decision_id"],
            ["decisions.tenant_id", "decisions.case_id", "decisions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "decision_id", "condition_id"],
            [
                "decision_conditions.tenant_id",
                "decision_conditions.decision_id",
                "decision_conditions.id",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "decision_id", "context_id"],
            [
                "decision_contexts.tenant_id",
                "decision_contexts.decision_id",
                "decision_contexts.id",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "assessment_id"],
            [
                "case_analysis_assessments.tenant_id",
                "case_analysis_assessments.case_id",
                "case_analysis_assessments.id",
            ],
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "condition_id",
            "assessment_id",
            "assessment_revision",
            name="uq_condition_assessment_exact",
        ),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_condition_assessment_command"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_condition_assessment_idempotency"
        ),
        sa.CheckConstraint("assessment_revision>0", name="assessment_revision"),
        sa.CheckConstraint("source_context_sha256 ~ '^[a-f0-9]{64}$'", name="source_hash"),
        sa.CheckConstraint("length(btrim(justification)) BETWEEN 1 AND 2000", name="justification"),
        sa.Index("ix_condition_assessment_case", "tenant_id", "case_id", "decision_id"),
    )
    id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    case_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    decision_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    context_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    condition_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    assessment_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    assessment_revision: Mapped[int] = mapped_column(nullable=False)
    source_context_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    justification: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    command_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
