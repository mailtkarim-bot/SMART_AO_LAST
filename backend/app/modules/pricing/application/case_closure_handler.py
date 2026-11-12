from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.case_closure_commands import RecordPaymentFactCommand
from app.modules.pricing.infrastructure.case_closure_reader import (
    _json_value,
    _record,
    closure_dossier,
    fingerprint,
    source_context_state,
)
from app.modules.pricing.infrastructure.models.payment_cycle_fact import PaymentCycleFactRecord
from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
    PaymentPostReceptionCycleRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordPaymentFactHandler(CommandHandler):
    def execute(self, *, session, command: RecordPaymentFactCommand, context: CommandContext):
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        tenant = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        cycle = session.scalar(
            sa.select(PaymentPostReceptionCycleRecord)
            .where(
                PaymentPostReceptionCycleRecord.tenant_id == tenant,
                PaymentPostReceptionCycleRecord.case_id == command.case_id,
                PaymentPostReceptionCycleRecord.id == command.cycle_id,
            )
            .with_for_update()
        )
        if cycle is None:
            raise CommandExecutionError("PAYMENT_CYCLE_NOT_FOUND_OR_FORBIDDEN")
        dossier = closure_dossier(session, tenant, command.case_id)
        if dossier["dossier_sha256"] != command.expected_dossier_sha256:
            raise CommandExecutionError("CLOSURE_VIEW_CONFLICT")
        if (
            session.scalar(
                sa.select(PaymentCycleFactRecord.id).where(
                    PaymentCycleFactRecord.tenant_id == tenant,
                    PaymentCycleFactRecord.id == command.fact_id,
                )
            )
            is not None
        ):
            raise CommandExecutionError("PAYMENT_FACT_NOT_AVAILABLE")
        if command.compared_to_fact_id is not None:
            parent = session.scalar(
                sa.select(PaymentCycleFactRecord).where(
                    PaymentCycleFactRecord.tenant_id == tenant,
                    PaymentCycleFactRecord.case_id == command.case_id,
                    PaymentCycleFactRecord.cycle_id == command.cycle_id,
                    PaymentCycleFactRecord.id == command.compared_to_fact_id,
                )
            )
            if parent is None:
                raise CommandExecutionError("PAYMENT_COMPARISON_NOT_FOUND_OR_FORBIDDEN")
            if parent.currency_code != command.currency_code or (command.kind, parent.kind) not in {
                ("PAYMENT_EXPECTED", "INVOICE_DECLARED"),
                ("COLLECTION_RECORDED", "PAYMENT_EXPECTED"),
            }:
                raise CommandExecutionError("PAYMENT_COMPARISON_INCOMPATIBLE")
            if source_context_state(
                parent.source_snapshot_json.get("case_source"), dossier["case_source"]
            ) == "REVIEW_REQUIRED" or parent.source_snapshot_json.get("cycle") != _record(cycle):
                raise CommandExecutionError("PAYMENT_COMPARISON_SOURCE_CHANGED")
        session.add(
            PaymentCycleFactRecord(
                id=command.fact_id,
                tenant_id=tenant,
                case_id=command.case_id,
                cycle_id=command.cycle_id,
                kind=command.kind,
                amount_minor=command.amount_minor,
                currency_code=command.currency_code,
                declared_date=command.declared_date,
                compared_to_fact_id=command.compared_to_fact_id,
                source_refs_json=list(command.source_refs),
                evidence_refs_json=list(command.evidence_refs),
                justification=command.justification,
                actor_id=UUID(str(context.actor_id)),
                source_snapshot_json={
                    "case_source": dossier["case_source"],
                    "dce_version_id": _json_value(case.applicable_dce_version_id),
                    "cycle": _record(cycle),
                    "dossier_sha256": dossier["dossier_sha256"],
                    "human_confirmed": True,
                },
            )
        )
        return HandlerOutcome(
            result_code="PAYMENT_FACT_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "PAYMENT_CYCLE_FACT",
                    "aggregate_id": str(command.fact_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="PAYMENT_CYCLE_FACT",
                    aggregate_id=command.fact_id,
                    aggregate_revision=1,
                    event_type="PAYMENT_FACT_RECORDED",
                    payload={"case_id": str(command.case_id), "kind": command.kind},
                ),
            ),
        )


def validate_closure_review(session, tenant_id, command):
    dossier = closure_dossier(session, tenant_id, command.case_id)
    review = command.closure_review
    if dossier is None or review.expected_dossier_sha256 != dossier["dossier_sha256"]:
        raise CommandExecutionError("CLOSURE_VIEW_CONFLICT")
    origin_id = getattr(command, "origin_reception_act_id", None)
    if origin_id is not None:
        origin = next((act for act in dossier["acts"] if act["id"] == str(origin_id)), None)
        if origin is None or origin.get("context_state") == "REVIEW_REQUIRED":
            raise CommandExecutionError("CLOSURE_COMPARISON_SOURCE_CHANGED_OR_FORBIDDEN")
    if getattr(command, "act_kind", None) == "CONTRACT_EXIT":
        if set(map(str, review.acknowledged_open_obligation_ids)) != set(
            dossier["open_obligation_ids"]
        ):
            raise CommandExecutionError("OPEN_OBLIGATIONS_REQUIRE_ACKNOWLEDGEMENT")
    elif review.acknowledged_open_obligation_ids:
        raise CommandExecutionError("OPEN_ACKNOWLEDGEMENT_ONLY_FOR_EXIT")
    references = {
        (kind, entry["id"] if kind != "PAYMENT_FACT" else entry["fact_id"]): entry
        for kind, entries in (
            ("ACT", dossier["acts"]),
            ("OBLIGATION", dossier["obligations"]),
            ("PAYMENT_FACT", dossier["facts"]),
            ("CHANGE_ACTION", dossier["change_actions"]),
        )
        for entry in entries
    }
    comparisons = []
    for comparison in review.comparisons:
        snapshots = {}
        for side in ("expected", "actual"):
            ref = getattr(comparison, side)
            value = references.get((ref.kind, str(ref.record_id)))
            if value is None or fingerprint(value) != ref.sha256:
                raise CommandExecutionError("CLOSURE_COMPARISON_SOURCE_CHANGED_OR_FORBIDDEN")
            if value.get("context_state") == "REVIEW_REQUIRED":
                raise CommandExecutionError("CLOSURE_COMPARISON_SOURCE_CHANGED_OR_FORBIDDEN")
            snapshots[side] = value
        comparisons.append({**comparison.model_dump(mode="json"), "source_snapshots": snapshots})
    return {
        **review.model_dump(mode="json"),
        "dce_version_id": dossier["dce_version_id"],
        "case_source": dossier["case_source"],
        "comparisons": comparisons,
        "comparison_state": "HUMAN_DECLARED" if comparisons else "UNKNOWN",
        "legal_effect_state": "UNKNOWN",
    }
