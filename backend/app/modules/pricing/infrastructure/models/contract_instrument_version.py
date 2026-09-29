from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractInstrumentVersionRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_instrument_versions"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_instrument_versions__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_contract_instrument_versions__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "instrument_kind",
            "version_reference",
            name="uq_contract_instrument_versions__declared_reference",
        ),
        sa.CheckConstraint(
            "instrument_kind IN ('SIGNED_CONTRACT', 'AMENDMENT')",
            name="contract_instrument_version_kind_closed",
        ),
        sa.CheckConstraint(
            "length(trim(version_reference)) > 0",
            name="contract_instrument_version_reference_required",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(source_refs_json) > 0",
            name="contract_instrument_version_sources_required",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(evidence_refs_json) > 0",
            name="contract_instrument_version_proofs_required",
        ),
        sa.Index(
            "ix_contract_instrument_versions_tenant_case_created",
            "tenant_id",
            "case_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    instrument_kind: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    version_reference: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
