"""Explicitly published execution learning, without a fabricated commercial P7."""

from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.infrastructure.models.rex import CaseRexRecord
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordExecutionRexHandler(CommandHandler):
    def execute(self, *, session, command, context):
        from app.modules.pricing.infrastructure.case_closure_reader import (
            closure_dossier,
            fingerprint,
            source_context_state,
        )

        tenant = UUID(str(context.tenant_id))
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        lots = {str(v).strip() for v in case.scope_json.get("lot_numbers", []) if str(v).strip()}
        if (lots and command.lot_reference not in lots) or (
            not lots and command.lot_reference != "UNKNOWN"
        ):
            raise CommandExecutionError("LOT_NOT_IN_CASE_SCOPE")
        dossier = closure_dossier(session, tenant, command.case_id)
        if dossier["dossier_sha256"] != command.expected_dossier_sha256:
            raise CommandExecutionError("CLOSURE_VIEW_CONFLICT")
        exit_act = session.scalar(
            sa.select(ContractExecutionEvidenceRecord).where(
                ContractExecutionEvidenceRecord.tenant_id == tenant,
                ContractExecutionEvidenceRecord.case_id == command.case_id,
                ContractExecutionEvidenceRecord.id == command.exit_act_id,
                ContractExecutionEvidenceRecord.act_kind == "CONTRACT_EXIT",
            )
        )
        if exit_act is None or exit_act.closure_review_json is None:
            raise CommandExecutionError("REVIEWED_EXIT_NOT_FOUND_OR_FORBIDDEN")
        dce = str(case.applicable_dce_version_id) if case.applicable_dce_version_id else None
        if (
            source_context_state(
                exit_act.closure_review_json.get("case_source"), dossier["case_source"]
            )
            == "REVIEW_REQUIRED"
        ):
            raise CommandExecutionError("EXECUTION_REX_SOURCE_CHANGED")
        if exit_act.contract_instrument_version_id and any(
            r["replaced_contract_instrument_version_id"]
            == str(exit_act.contract_instrument_version_id)
            for r in dossier["contract_replacements"]
        ):
            raise CommandExecutionError("EXECUTION_REX_SOURCE_CHANGED")
        session.add(
            CaseRexRecord(
                id=command.rex_id,
                tenant_id=tenant,
                case_id=command.case_id,
                p7_result_id=None,
                execution_exit_act_id=exit_act.id,
                execution_source_json={
                    "exit_act_id": str(exit_act.id),
                    "dce_version_id": dce,
                    "exit_record_sha256": fingerprint(
                        next(a for a in dossier["acts"] if a["id"] == str(exit_act.id))
                    ),
                    "published_by_human": True,
                    "case_source": dossier["case_source"],
                    "human_justification": command.justification,
                },
                lot_reference=command.lot_reference,
                motif="KNOWN",
                scope=command.scope,
                validation=command.validation,
                observation=command.observation,
                consequence=command.consequence,
                follow_up=command.follow_up,
                source_locator=command.source_locator,
                actor_id=UUID(str(context.actor_id)),
                membership_id=UUID(str(context.membership_id)),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return HandlerOutcome(
            result_code="EXECUTION_REX_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseRex",
                    "aggregate_id": str(command.rex_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseRex",
                    aggregate_id=command.rex_id,
                    aggregate_revision=1,
                    event_type="ExecutionRexRecorded",
                    payload={"case_id": str(command.case_id), "exit_act_id": str(exit_act.id)},
                ),
            ),
        )
