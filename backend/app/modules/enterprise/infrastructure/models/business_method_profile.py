"""Immutable published business-method profile versions."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from app.platform.persistence.base import Base, TenantScopedRecord
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class EnterpriseBusinessMethodProfileVersionRecord(TenantScopedRecord, Base):
    __tablename__ = "enterprise_business_method_profile_versions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "company_id"],
            ["enterprise_companies.tenant_id", "enterprise_companies.id"],
            name="fk_business_method_profile_version__company",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "created_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_business_method_profile_version__membership",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_business_method_profile_version__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "company_id",
            "version_number",
            name="uq_business_method_profile_version__number",
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_business_method_profile_version__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", "content_sha256", name="uq_business_method_profile_version__hash"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "id",
            "version_number",
            "content_sha256",
            name="uq_business_method_profile_version__snapshot",
        ),
        sa.CheckConstraint("version_number > 0", name="vnum"),
        sa.CheckConstraint("schema_version = 1", name="schema"),
        sa.CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$'", name="hash"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(profile_json) = 'object' "
            "AND profile_json ? 'schema_version' "
            "AND profile_json ->> 'schema_version' = '1' "
            "AND jsonb_typeof(profile_json -> 'terminology') = 'object' "
            "AND jsonb_typeof(profile_json -> 'additional_checks') = 'array' "
            "AND jsonb_array_length(profile_json -> 'additional_checks') <= 40 "
            "AND octet_length(profile_json::text) <= 16000",
            name="shape",
        ),
        sa.Index(
            "ix_business_method_profile_versions__tenant_company_version",
            "tenant_id",
            "company_id",
            "version_number",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    version_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    schema_version: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    profile_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    content_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    created_by_actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_by_membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
