"""Transactional P7 handover command handler."""

from __future__ import annotations

import hashlib
import json

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.decision.infrastructure.models.decision import (
    DecisionConditionContractEvidenceLinkRecord,
    DecisionConditionRecord,
    DecisionContextRecord,
    DecisionRecord,
)
from app.modules.patron_action.application.handover_commands import (
    RecordCaseHandoverSnapshotCommand,
)
from app.modules.patron_action.application.handover_queries import technical_document_source
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.patron_action.infrastructure.models.outcome import CaseOutcomeRecord
from app.modules.submission.infrastructure.models.submission import (
    SubmissionPackageAuthorizationRecord,
    SubmissionPackageRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


def _technical_document_source(manifest: dict[str, object], package) -> dict[str, str] | None:
    return technical_document_source(
        manifest,
        document_id=package.technical_document_id,
        version=package.technical_document_version,
    )


class CaseHandoverHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordCaseHandoverSnapshotCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == context.tenant_id, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        outcome = session.scalar(
            sa.select(CaseOutcomeRecord).where(
                CaseOutcomeRecord.tenant_id == context.tenant_id,
                CaseOutcomeRecord.case_id == command.case_id,
                CaseOutcomeRecord.id == command.outcome_id,
            )
        )
        package = session.scalar(
            sa.select(SubmissionPackageRecord).where(
                SubmissionPackageRecord.tenant_id == context.tenant_id,
                SubmissionPackageRecord.case_id == command.case_id,
                SubmissionPackageRecord.id == command.submission_package_id,
            )
        )
        if case is None or outcome is None or package is None:
            raise CommandExecutionError("HANDOVER_SOURCE_NOT_FOUND_OR_FORBIDDEN")
        if outcome.outcome != "WON":
            raise CommandExecutionError("HANDOVER_REQUIRES_WON_OUTCOME")
        manifest_bytes = json.dumps(
            package.manifest_json, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        if hashlib.sha256(manifest_bytes).hexdigest() != package.manifest_sha256:
            raise CommandExecutionError("HANDOVER_OFFER_MANIFEST_INTEGRITY_FAILED")
        technical_source = _technical_document_source(package.manifest_json, package)
        if technical_source is None:
            raise CommandExecutionError("HANDOVER_OFFER_DOCUMENT_SOURCE_MISSING")
        authorization = session.scalar(
            sa.select(SubmissionPackageAuthorizationRecord).where(
                SubmissionPackageAuthorizationRecord.tenant_id == context.tenant_id,
                SubmissionPackageAuthorizationRecord.submission_package_id == package.id,
                SubmissionPackageAuthorizationRecord.package_version == package.version,
                SubmissionPackageAuthorizationRecord.manifest_sha256 == package.manifest_sha256,
                SubmissionPackageAuthorizationRecord.state == "AUTHORIZED",
            )
        )
        if authorization is None:
            raise CommandExecutionError("HANDOVER_OFFER_NOT_P5_AUTHORIZED")
        manifest_scope = package.manifest_json.get("scope")
        lot_numbers = (
            manifest_scope.get("lot_numbers", []) if isinstance(manifest_scope, dict) else []
        )
        if outcome.lot_reference not in {str(lot).strip() for lot in lot_numbers}:
            raise CommandExecutionError("HANDOVER_OFFER_LOT_MISMATCH")

        decision = session.scalar(
            sa.select(DecisionRecord)
            .where(
                DecisionRecord.tenant_id == context.tenant_id,
                DecisionRecord.case_id == command.case_id,
                DecisionRecord.validity == "CURRENT",
            )
            .order_by(DecisionRecord.cycle_number.desc(), DecisionRecord.updated_at.desc())
            .limit(1)
        )
        decision_context = None
        open_conditions: list[DecisionConditionRecord] = []
        conditions_state = "UNKNOWN"
        sources: list[dict[str, object]] = []
        if decision is not None and decision.selected_final_context_id is not None:
            decision_context = session.scalar(
                sa.select(DecisionContextRecord)
                .where(
                    DecisionContextRecord.tenant_id == context.tenant_id,
                    DecisionContextRecord.decision_id == decision.id,
                    DecisionContextRecord.id == decision.selected_final_context_id,
                )
                .order_by(DecisionContextRecord.sequence_number.desc())
                .limit(1)
            )
            if decision_context is not None:
                conditions_state = "KNOWN"
                open_conditions = list(
                    session.scalars(
                        sa.select(DecisionConditionRecord)
                        .where(
                            DecisionConditionRecord.tenant_id == context.tenant_id,
                            DecisionConditionRecord.decision_id == decision.id,
                            DecisionConditionRecord.status == "OPEN",
                        )
                        .order_by(DecisionConditionRecord.id)
                    ).all()
                )
                if open_conditions:
                    links = session.scalars(
                        sa.select(DecisionConditionContractEvidenceLinkRecord)
                        .where(
                            DecisionConditionContractEvidenceLinkRecord.tenant_id
                            == context.tenant_id,
                            DecisionConditionContractEvidenceLinkRecord.decision_id == decision.id,
                            DecisionConditionContractEvidenceLinkRecord.context_id
                            == decision_context.id,
                            DecisionConditionContractEvidenceLinkRecord.condition_id.in_(
                                [condition.id for condition in open_conditions]
                            ),
                        )
                        .order_by(
                            DecisionConditionContractEvidenceLinkRecord.created_at,
                            DecisionConditionContractEvidenceLinkRecord.id,
                        )
                    ).all()
                    sources = [
                        {
                            "condition_id": str(link.condition_id),
                            "requirement_id": str(link.dce_requirement_id),
                            "requirement_revision": link.dce_requirement_revision,
                            "impact_id": str(link.contract_impact_id),
                            "impact_revision": link.proof_revision,
                            "profile_version_id": str(link.profile_version_id),
                            "profile_version": link.profile_version,
                            "profile_sha256": link.profile_content_sha256,
                        }
                        for link in links
                    ]

        latest_revision = session.scalar(
            sa.select(sa.func.coalesce(sa.func.max(CaseHandoverSnapshotRecord.revision), 0)).where(
                CaseHandoverSnapshotRecord.tenant_id == context.tenant_id,
                CaseHandoverSnapshotRecord.outcome_id == outcome.id,
            )
        )
        revision = int(latest_revision or 0) + 1
        snapshot: dict[str, object] = {
            "schema_version": 1,
            "kind": "P7_HANDOVER_SNAPSHOT",
            "p7_is_order_service": False,
            "award": {
                "outcome_id": str(outcome.id),
                "lot_reference": outcome.lot_reference,
                "source_locator": outcome.source_locator,
                "recorded_at": outcome.created_at.isoformat(),
            },
            "offer": {
                "submission_package_id": str(package.id),
                "package_version": package.version,
                "manifest_sha256": package.manifest_sha256,
                "dce_version_id": str(package.dce_version_id),
                "technical_document_id": str(package.technical_document_id),
                "technical_document_version": package.technical_document_version,
                "technical_document_kind": technical_source["kind"],
                "technical_document_sha256": technical_source["sha256"],
                "financial_content": "NOT_INCLUDED",
            },
            "decision": {
                "state": "KNOWN"
                if decision is not None and decision_context is not None
                else "UNKNOWN",
                "decision_id": str(decision.id) if decision is not None else None,
                "revision": decision.aggregate_revision if decision is not None else None,
                "outcome": decision.outcome if decision is not None else "UNKNOWN",
                "context_id": str(decision_context.id) if decision_context is not None else None,
                "context_fingerprint": decision_context.context_fingerprint
                if decision_context
                else None,
                "conditions_state": conditions_state,
                "open_conditions": [
                    {
                        "condition_id": str(condition.id),
                        "label": condition.label,
                        "status": condition.status,
                        "due_at": condition.due_at.isoformat() if condition.due_at else None,
                    }
                    for condition in open_conditions
                ],
                "condition_sources": sources,
            },
            "contract_comparison": {
                "state": "UNKNOWN",
                "reason": (
                    "Aucune liaison humaine entre l'offre attribuée et une version du contrat "
                    "signé ou de mise au point n'est enregistrée ; aucun écart n'a été évalué."
                ),
            },
            "excluded": ["DONNEES_FINANCIERES_PRIVEES", "TEXTES_LIBRES_PATRON"],
        }
        record = CaseHandoverSnapshotRecord(
            id=command.snapshot_id,
            tenant_id=context.tenant_id,
            case_id=case.id,
            outcome_id=outcome.id,
            lot_reference=outcome.lot_reference,
            submission_package_id=package.id,
            package_version=package.version,
            manifest_sha256=package.manifest_sha256,
            revision=revision,
            snapshot_json=snapshot,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_HANDOVER_SNAPSHOT_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseHandoverSnapshot",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseHandoverSnapshot",
                    aggregate_id=record.id,
                    aggregate_revision=revision,
                    event_type="CaseHandoverSnapshotRecorded",
                    payload={
                        "case_id": str(case.id),
                        "outcome_id": str(outcome.id),
                        "lot_reference": outcome.lot_reference,
                        "package_id": str(package.id),
                        "revision": revision,
                    },
                ),
            ),
        )
