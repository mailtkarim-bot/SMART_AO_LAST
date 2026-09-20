"""Append-only human contributions and resolutions for one DCE requirement."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class DceRequirementContributionRecord(TenantScopedRecord, Base):
    """One author's proposal, retained even when another proposal wins."""

    __tablename__ = "dce_requirement_contributions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], name="fk_dce_contrib__tenant", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "requirement_id"],
            ["dce_requirements.tenant_id", "dce_requirements.id"],
            name="fk_dce_contrib__requirement",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_dce_contrib__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "author_actor_id", "idempotency_key", name="uq_dce_contrib__idempotency"
        ),
        sa.CheckConstraint("observed_revision >= 0", name="observed_revision_nonnegative"),
        sa.CheckConstraint(
            "proposed_outcome IN ('CONFIRMED', 'REVIEW_REQUIRED', 'NOT_APPLICABLE')",
            name="proposed_outcome",
        ),
        sa.Index(
            "ix_dce_contrib__tenant_requirement_revision",
            "tenant_id",
            "requirement_id",
            "observed_revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    requirement_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    observed_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    current_revision_at_submission: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    author_actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    source_locator: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    basis_fingerprint: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    proposed_outcome: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    proposed_reason_code: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    contributed_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)


class DceRequirementConflictRecord(TenantScopedRecord, Base):
    """A pair of different proposals for the same observed revision."""

    __tablename__ = "dce_requirement_conflicts"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "requirement_id"],
            ["dce_requirements.tenant_id", "dce_requirements.id"],
            name="fk_dce_conflict__requirement",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "first_contribution_id"],
            ["dce_requirement_contributions.tenant_id", "dce_requirement_contributions.id"],
            name="fk_dce_conflict__first_contribution",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "second_contribution_id"],
            ["dce_requirement_contributions.tenant_id", "dce_requirement_contributions.id"],
            name="fk_dce_conflict__second_contribution",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_dce_conflict__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "requirement_id",
            "observed_revision",
            name="uq_dce_conflict__requirement_revision",
        ),
        sa.CheckConstraint("observed_revision >= 0", name="observed_revision_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    requirement_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    observed_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    first_contribution_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    second_contribution_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)


class DceRequirementConflictResolutionRecord(TenantScopedRecord, Base):
    """Immutable human resolution; its existence closes the conflict."""

    __tablename__ = "dce_requirement_conflict_resolutions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "conflict_id"],
            ["dce_requirement_conflicts.tenant_id", "dce_requirement_conflicts.id"],
            name="fk_dce_resolution__conflict",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "selected_contribution_id"],
            ["dce_requirement_contributions.tenant_id", "dce_requirement_contributions.id"],
            name="fk_dce_resolution__selected_contribution",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_dce_resolution__tenant_id"),
        sa.UniqueConstraint("tenant_id", "conflict_id", name="uq_dce_resolution__conflict"),
        sa.UniqueConstraint(
            "tenant_id", "conflict_id", "idempotency_key", name="uq_dce_resolution__idempotency"
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    conflict_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    selected_contribution_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    resolved_by_actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reason: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
