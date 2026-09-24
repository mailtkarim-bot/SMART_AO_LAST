"""Tenant-scoped persistence for sourced regulatory applicability facts."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class RegulatoryProfileRecord(TenantScopedRecord, Base):
    __tablename__ = "regulatory_profiles"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_regulatory_profiles__tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_regulatory_profiles__case",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_regulatory_profiles__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "profile_version", name="uq_regulatory_profiles__case_version"
        ),
        sa.CheckConstraint("profile_version > 0", name="profile_version_positive"),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'FUTURE', 'EXPIRED', 'UNKNOWN_APPLICABILITY', 'REVIEW_REQUIRED')",
            name="status_closed",
        ),
        sa.CheckConstraint("jsonb_typeof(facts_json) = 'object'", name="facts_object"),
        sa.CheckConstraint(
            "jsonb_typeof(source_refs_json) = 'array' AND jsonb_array_length(source_refs_json) > 0",
            name="source_refs_nonempty",
        ),
        sa.Index(
            "ix_regulatory_profiles__tenant_case_version",
            "tenant_id",
            "case_id",
            "profile_version",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    profile_version: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    facts_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    effective_from: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    effective_until: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    created_by_actor_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
