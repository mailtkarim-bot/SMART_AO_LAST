"""Append-only adoption of an exact enterprise method-profile version by an Affaire."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseBusinessMethodProfileAdoptionRecord(TenantScopedRecord, Base):
    __tablename__ = "case_business_method_profile_adoptions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_case_business_method_adoption__case",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_version_id", "profile_version", "profile_content_sha256"],
            [
                "enterprise_business_method_profile_versions.tenant_id",
                "enterprise_business_method_profile_versions.id",
                "enterprise_business_method_profile_versions.version_number",
                "enterprise_business_method_profile_versions.content_sha256",
            ],
            name="fk_case_business_method_adoption__profile_hash",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "created_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_case_business_method_adoption__membership",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_business_method_adoption__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_business_method_adoption__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "adoption_revision",
            name="uq_case_business_method_adoption__revision",
        ),
        sa.CheckConstraint("adoption_revision > 0", name="arev"),
        sa.CheckConstraint("profile_version > 0", name="pver"),
        sa.CheckConstraint("profile_content_sha256 ~ '^[0-9a-f]{64}$'", name="hash"),
        sa.Index(
            "ix_case_business_method_adoptions__tenant_case_revision",
            "tenant_id",
            "case_id",
            "adoption_revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    profile_version_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    profile_version: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    profile_content_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    adoption_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    created_by_actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_by_membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
