"""Immutable source-bound human declarations, never gate decisions."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class AnalysisAssessmentRecord(TenantScopedRecord, Base):
    __tablename__ = "case_analysis_assessments"
    __table_args__ = (
        sa.UniqueConstraint("tenant_id", "case_id", "id", name="uq_assessments_tenant_case_id"),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], name="fk_analysis_assessments_0", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_analysis_assessments_1",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "risk_id"],
            ["decision_risks.tenant_id", "decision_risks.id"],
            name="fk_analysis_assessments_2",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "requirement_id"],
            ["dce_requirements.tenant_id", "dce_requirements.id"],
            name="fk_analysis_assessments_3",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "dce_version_id"],
            ["dce_versions.tenant_id", "dce_versions.id"],
            name="fk_analysis_assessments_4",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "source_fragment_id"],
            ["dce_document_extraction_fragments.tenant_id", "dce_document_extraction_fragments.id"],
            name="fk_analysis_assessments_5",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "previous_assessment_id"],
            ["case_analysis_assessments.tenant_id", "case_analysis_assessments.id"],
            name="fk_analysis_assessments_6",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "id", name="pk_case_analysis_assessments"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "point_kind",
            "point_id",
            "revision",
            name="uq_analysis_assessments_1",
        ),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_analysis_assessments_2"),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_analysis_assessments_3"),
        sa.CheckConstraint(
            (
                "(point_kind='RISK' AND risk_id IS NOT NULL AND risk_id=point_id AND "
                "requirement_id IS NULL) OR (point_kind='REQUIREMENT' AND "
                "requirement_id IS NOT NULL AND requirement_id=point_id AND risk_id IS "
                "NULL)"
            ),
            name="analysis_point_identity",
        ),
        sa.CheckConstraint(
            (
                "native_revision>=0 AND ((revision=1 AND previous_assessment_id IS "
                "NULL) OR (revision>1 AND previous_assessment_id IS NOT NULL))"
            ),
            name="analysis_revisions",
        ),
        sa.CheckConstraint(
            "source_context_sha256 ~ '^[0-9a-f]{64}$' AND scope_fingerprint ~ '^[0-9a-f]{64}$'",
            name="analysis_source_hash",
        ),
        sa.CheckConstraint("jsonb_typeof(source_manifest_json)='object'", name="analysis_manifest"),
        sa.CheckConstraint(
            "char_length(btrim(justification)) BETWEEN 1 AND 2000", name="analysis_justification"
        ),
        sa.CheckConstraint(
            (
                "(expected_evidence_state<>'UNKNOWN' AND "
                "residual_risk_state<>'UNKNOWN') OR (unknown_reason IS NOT NULL AND "
                "char_length(btrim(unknown_reason)) BETWEEN 1 AND 2000)"
            ),
            name="analysis_unknown_reason",
        ),
        sa.CheckConstraint(
            (
                "(expected_evidence_state='DECLARED' AND expected_evidence IS NOT NULL "
                "AND char_length(btrim(expected_evidence)) BETWEEN 1 AND 2000) OR "
                "(expected_evidence_state='UNKNOWN' AND expected_evidence IS NULL)"
            ),
            name="analysis_expected_evidence",
        ),
        sa.CheckConstraint(
            (
                "(residual_risk_state='DECLARED' AND residual_risk IS NOT NULL AND "
                "char_length(btrim(residual_risk)) BETWEEN 1 AND 2000) OR "
                "(residual_risk_state='UNKNOWN' AND residual_risk IS NULL)"
            ),
            name="analysis_residual_risk",
        ),
    )
    id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    case_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    point_kind: Mapped[str] = mapped_column(sa.String(16), nullable=False, primary_key=False)
    point_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    risk_id: Mapped[UUID | None] = mapped_column(sa.Uuid(), nullable=True, primary_key=False)
    requirement_id: Mapped[UUID | None] = mapped_column(sa.Uuid(), nullable=True, primary_key=False)
    dce_version_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    source_fragment_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    scope_fingerprint: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False, primary_key=False)
    native_revision: Mapped[int] = mapped_column(sa.Integer(), nullable=False, primary_key=False)
    source_context_sha256: Mapped[str] = mapped_column(
        sa.CHAR(64), nullable=False, primary_key=False
    )
    source_manifest_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, primary_key=False
    )
    revision: Mapped[int] = mapped_column(sa.Integer(), nullable=False, primary_key=False)
    previous_assessment_id: Mapped[UUID | None] = mapped_column(
        sa.Uuid(), nullable=True, primary_key=False
    )
    expected_evidence_state: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, primary_key=False
    )
    expected_evidence: Mapped[str | None] = mapped_column(
        sa.Text(), nullable=True, primary_key=False
    )
    residual_risk_state: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, primary_key=False
    )
    residual_risk: Mapped[str | None] = mapped_column(sa.Text(), nullable=True, primary_key=False)
    unknown_reason: Mapped[str | None] = mapped_column(sa.Text(), nullable=True, primary_key=False)
    justification: Mapped[str] = mapped_column(sa.Text(), nullable=False, primary_key=False)
    actor_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    membership_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    command_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    idempotency_key: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, primary_key=False)
    correlation_id: Mapped[UUID | None] = mapped_column(sa.Uuid(), nullable=True, primary_key=False)

    treatment_json: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True), nullable=True)
