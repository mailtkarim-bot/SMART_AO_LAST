# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractQueryExportTransitionRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_query_export_transitions"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_query_export_transitions__tenant_id"),
        sa.CheckConstraint("from_status IN ('REQUESTED', 'READY', 'UNKNOWN', 'REFUSED')", name="contract_export_transition_from_closed"),
        sa.CheckConstraint("to_status IN ('REQUESTED', 'READY', 'UNKNOWN', 'REFUSED')", name="contract_export_transition_to_closed"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    export_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    from_status: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    to_status: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    local_proof_ref: Mapped[str | None] = mapped_column(sa.String(255))
    local_proof_sha256: Mapped[str | None] = mapped_column(sa.String(64))
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
