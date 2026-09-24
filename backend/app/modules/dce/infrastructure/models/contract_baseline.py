"""Tenant-scoped append-only contract baseline/deviation/impact proof."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractBaselineDeviationImpactRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_baseline_deviation_impacts"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_baseline_impacts__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "baseline_observation_id",
            "proof_revision",
            name="uq_contract_baseline_impacts__functional",
        ),
        sa.CheckConstraint("proof_revision > 0", name="contract_proof_revision_positive"),
        sa.CheckConstraint(
            "status IN ('SOURCE_SIGNAL_ONLY', 'HUMAN_REVIEW_REQUIRED', 'CONFIRMED', 'UNKNOWN')",
            name="contract_assessment_status_closed",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(baseline_source_refs_json) > 0",
            name="contract_baseline_sources_nonempty",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    baseline_observation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    proof_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    baseline_source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    baseline_statement: Mapped[str] = mapped_column(sa.Text, nullable=False)
    deviation_statement: Mapped[str | None] = mapped_column(sa.Text)
    impact_statement: Mapped[str | None] = mapped_column(sa.Text)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    created_by_actor_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
