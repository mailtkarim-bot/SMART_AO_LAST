from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractExecutionEvidenceRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_execution_evidence"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_dce_version_id_at_recording"],
            ["dce_versions.tenant_id", "dce_versions.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_execution_evidence__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_contract_execution_evidence__tenant_case_id"
        ),
        sa.CheckConstraint(
            "act_kind IN ('WORK_RECEPTION', 'RIGHTS_PRESERVATION', 'CONTRACT_EXIT')",
            name="contract_execution_evidence_kind_closed",
        ),
        sa.CheckConstraint(
            "reception_outcome IS NULL OR (act_kind = 'WORK_RECEPTION' AND reception_outcome IN ("
            "'WITH_RESERVATIONS', 'UNDER_RESERVATIONS', 'WITHOUT_RESERVATIONS'))",
            name="contract_execution_evidence_reception_outcome_closed",
        ),
        sa.CheckConstraint(
            "length(trim(summary)) > 0", name="contract_execution_evidence_summary_required"
        ),
        sa.CheckConstraint(
            "jsonb_array_length(source_refs_json) > 0",
            name="contract_execution_evidence_source_required",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(evidence_refs_json) > 0",
            name="contract_execution_evidence_proof_required",
        ),
        sa.Index(
            "ix_contract_exec_evidence_tenant_case_created",
            "tenant_id",
            "case_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_dce_version_id_at_recording: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    contract_instrument_version_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    act_kind: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    reception_outcome: Mapped[str | None] = mapped_column(sa.String(32))
    summary: Mapped[str] = mapped_column(sa.Text, nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    declared_event_date: Mapped[date | None] = mapped_column(sa.Date)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
