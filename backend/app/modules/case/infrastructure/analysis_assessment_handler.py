"""Persist and project source-bound human declarations under native command receipts."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa

from app.modules.case.application.analysis_assessment import source_context_digest
from app.modules.case.infrastructure.models.analysis_assessment import (
    AnalysisAssessmentRecord as Act,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.platform.events.dispatcher import CommandExecutionError, HandlerOutcome


def attach_assessments(session, *, tenant_id, case_id, version, requirements, risks):
    case = session.scalar(
        sa.select(CaseRecord).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
    )
    scope = dict(
        scope_kind=case.scope_kind,
        scope_json=case.scope_json,
        scope_fingerprint=case.scope_fingerprint,
    )
    for item in (*requirements, *risks):
        current = item["source_state"] == "CURRENT_SOURCE"
        digest = (
            source_context_digest(
                point=item, tenant_id=tenant_id, case_id=case_id, version_id=version, scope=scope
            )
            if current
            else None
        )
        item["source_context_sha256"] = digest
        item["human_assessment"] = None
        act = session.scalar(
            sa.select(Act)
            .where(
                Act.tenant_id == tenant_id,
                Act.case_id == case_id,
                Act.point_kind == item["kind"],
                Act.point_id == item["item_id"],
            )
            .order_by(Act.revision.desc())
            .limit(1)
        )
        if act is None:
            continue
        valid = current and act.source_context_sha256 == digest
        item["human_assessment"] = dict(
            assessment_id=act.id,
            revision=act.revision,
            previous_assessment_id=act.previous_assessment_id,
            state="CURRENT" if valid else "REVIEW_REQUIRED",
            source_context_sha256=act.source_context_sha256,
            actor_id=act.actor_id if valid else None,
            created_at=act.created_at,
            expected_evidence_state=act.expected_evidence_state if valid else "UNKNOWN",
            expected_evidence=act.expected_evidence if valid else None,
            residual_risk_state=act.residual_risk_state if valid else "UNKNOWN",
            residual_risk=act.residual_risk if valid else None,
            unknown_reason=act.unknown_reason if valid else None,
            justification=act.justification if valid else None,
            treatment=act.treatment_json if valid else None,
        )


class RecordAnalysisAssessmentHandler:
    def execute(self, *, session, command, context):
        from app.modules.case.infrastructure.analysis_summary_reader import (
            SqlAlchemyCaseAnalysisSummaryReader,
        )

        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        tenant = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        reader = SqlAlchemyCaseAnalysisSummaryReader(session)

        def current_point():
            try:
                summary = reader.get(tenant_id=tenant, case_id=case.id)
            except ValueError as error:
                raise CommandExecutionError("STALE_SOURCE_CONTEXT") from error
            return (
                next(
                    (
                        i
                        for a in summary["axes"]
                        for i in a["items"]
                        if i["kind"] == command.point_kind and i["item_id"] == command.point_id
                    ),
                    None,
                )
                if summary
                else None
            )

        item = current_point()
        if item is None:
            raise CommandExecutionError("STALE_SOURCE_CONTEXT")
        if item["source_state"] != "CURRENT_SOURCE":
            raise CommandExecutionError("STALE_SOURCE_CONTEXT")
        from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
        from app.modules.decision.infrastructure.models.risk import DecisionRiskRecord

        native_model = DecisionRiskRecord if command.point_kind == "RISK" else DceRequirementRecord
        native = session.scalar(
            sa.select(native_model)
            .where(native_model.tenant_id == tenant, native_model.id == command.point_id)
            .with_for_update()
        )
        if native is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        anchor = item["source_anchor"]
        session.scalar(
            sa.select(DceDocumentRecord)
            .where(
                DceDocumentRecord.tenant_id == tenant,
                DceDocumentRecord.id == anchor["dce_document_id"],
            )
            .with_for_update()
        )
        session.scalar(
            sa.select(DceVersionRecord)
            .where(
                DceVersionRecord.tenant_id == tenant,
                DceVersionRecord.id == anchor["dce_version_id"],
            )
            .with_for_update()
        )
        item = current_point()
        if (
            item is None
            or item["source_state"] != "CURRENT_SOURCE"
            or item["source_context_sha256"] != command.source_context_sha256
        ):
            raise CommandExecutionError("STALE_SOURCE_CONTEXT")
        previous = session.scalar(
            sa.select(Act)
            .where(
                Act.tenant_id == tenant,
                Act.case_id == case.id,
                Act.point_kind == command.point_kind,
                Act.point_id == command.point_id,
            )
            .order_by(Act.revision.desc())
            .limit(1)
        )
        revision = previous.revision if previous else 0
        if revision != command.expected_revision:
            raise CommandExecutionError("STALE_ASSESSMENT_REVISION")
        row = Act(
            id=command.assessment_id,
            tenant_id=tenant,
            case_id=case.id,
            point_kind=command.point_kind,
            point_id=command.point_id,
            risk_id=command.point_id if command.point_kind == "RISK" else None,
            requirement_id=command.point_id if command.point_kind == "REQUIREMENT" else None,
            dce_version_id=anchor["dce_version_id"],
            source_fragment_id=anchor["source_anchor_id"],
            scope_fingerprint=case.scope_fingerprint,
            native_revision=item["native_revision"],
            source_context_sha256=command.source_context_sha256,
            source_manifest_json=dict(
                source_anchor={k: str(v) if isinstance(v, UUID) else v for k, v in anchor.items()},
                start_byte_offset=item["start_byte_offset"],
                end_byte_offset=item["end_byte_offset"],
                scope=dict(
                    kind=case.scope_kind, facts=case.scope_json, fingerprint=case.scope_fingerprint
                ),
                native_revision=item["native_revision"],
            ),
            revision=revision + 1,
            previous_assessment_id=previous.id if previous else None,
            expected_evidence_state=command.expected_evidence_state,
            expected_evidence=command.expected_evidence,
            residual_risk_state=command.residual_risk_state,
            residual_risk=command.residual_risk,
            unknown_reason=command.unknown_reason,
            justification=command.justification,
            treatment_json=command.treatment.model_dump(mode="json") if command.treatment else None,
            actor_id=UUID(str(context.actor_id)),
            membership_id=UUID(str(context.membership_id)),
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=UUID(str(context.correlation_id)) if context.correlation_id else None,
        )
        session.add(row)
        session.flush()
        return HandlerOutcome(
            result_code="ANALYSIS_ASSESSMENT_RECORDED",
            aggregate_refs=(
                dict(
                    aggregate_type="CASE_ANALYSIS_ASSESSMENT",
                    aggregate_id=str(row.id),
                    aggregate_revision=row.revision,
                ),
            ),
            events=(),
        )
