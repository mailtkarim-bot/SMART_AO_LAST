from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractExecutionEvidenceRequalificationRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_execution_evidence_requalifications"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "act_id"],
            [
                "contract_execution_evidence.tenant_id",
                "contract_execution_evidence.case_id",
                "contract_execution_evidence.id",
            ],
            ondelete="RESTRICT",
            name="fk_cer_act_same_case",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "supersession_id"],
            [
                "contract_instrument_supersessions.tenant_id",
                "contract_instrument_supersessions.case_id",
                "contract_instrument_supersessions.id",
            ],
            ondelete="RESTRICT",
            name="fk_cer_supersession_same_case",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "resulting_contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
            name="fk_cer_result_version_same_case",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_exec_requal__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "act_id", "supersession_id", "revision",
            name="uq_contract_exec_requal__trigger_revision",
        ),
        sa.CheckConstraint("revision > 0", name="contract_exec_requal_revision_positive"),
        sa.CheckConstraint(
            "decision IN ("
            "'RETAINED_AS_DECLARED', 'RELINKED_TO_DECLARED_VERSION', 'NEEDS_CLARIFICATION')",
            name="contract_exec_requal_decision_closed",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0",
            name="contract_exec_requal_rationale_required",
        ),
        sa.CheckConstraint(
            "(decision = 'NEEDS_CLARIFICATION' "
            "AND resulting_contract_instrument_version_id IS NULL) "
            "OR (decision IN ('RETAINED_AS_DECLARED', 'RELINKED_TO_DECLARED_VERSION') "
            "AND resulting_contract_instrument_version_id IS NOT NULL)",
            name="contract_exec_requal_result_matches_decision",
        ),
        sa.Index(
            "ix_contract_exec_requal_tenant_case_act",
            "tenant_id",
            "case_id",
            "act_id",
            "created_at",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    act_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    supersession_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(40), nullable=False)
    resulting_contract_instrument_version_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    rationale: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
