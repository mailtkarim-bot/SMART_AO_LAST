from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.contract_execution_evidence_commands import (
    RecordContractExecutionEvidenceCommand,
)
from app.modules.pricing.domain.contract_execution_evidence import (
    ContractExecutionActKind,
    ContractReceptionOutcome,
    build_contract_execution_evidence,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordContractExecutionEvidenceHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordContractExecutionEvidenceCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        case = session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == command.case_id,
            )
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if (
            command.contract_instrument_version_id is not None
            and session.scalar(
                sa.select(ContractInstrumentVersionRecord.id).where(
                    ContractInstrumentVersionRecord.tenant_id == tenant_id,
                    ContractInstrumentVersionRecord.case_id == command.case_id,
                    ContractInstrumentVersionRecord.id == command.contract_instrument_version_id,
                )
            )
            is None
        ):
            raise CommandExecutionError("CONTRACT_INSTRUMENT_VERSION_NOT_FOUND_OR_FORBIDDEN")
        if (
            session.scalar(
                sa.select(ContractExecutionEvidenceRecord.id).where(
                    ContractExecutionEvidenceRecord.tenant_id == tenant_id,
                    ContractExecutionEvidenceRecord.id == command.act_id,
                )
            )
            is not None
        ):
            raise CommandExecutionError("CONTRACT_EXECUTION_ACT_ID_REUSED")
        try:
            evidence = build_contract_execution_evidence(
                case_id=command.case_id,
                case_dce_version_id_at_recording=case.applicable_dce_version_id,
                act_kind=ContractExecutionActKind(command.act_kind),
                summary=command.summary,
                source_refs=command.source_refs,
                evidence_refs=command.evidence_refs,
                declared_event_date=command.declared_event_date,
                contract_instrument_version_id=command.contract_instrument_version_id,
                reception_outcome=(
                    ContractReceptionOutcome(command.reception_outcome)
                    if command.reception_outcome is not None
                    else None
                ),
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error

        session.add(
            ContractExecutionEvidenceRecord(
                id=command.act_id,
                tenant_id=tenant_id,
                case_id=evidence.case_id,
                case_dce_version_id_at_recording=evidence.case_dce_version_id_at_recording,
                contract_instrument_version_id=evidence.contract_instrument_version_id,
                act_kind=evidence.act_kind.value,
                reception_outcome=(
                    evidence.reception_outcome.value if evidence.reception_outcome else None
                ),
                summary=evidence.summary,
                source_refs_json=list(evidence.source_refs),
                evidence_refs_json=list(evidence.evidence_refs),
                declared_event_date=evidence.declared_event_date,
                actor_id=UUID(str(context.actor_id)),
            )
        )
        event_date = (
            evidence.declared_event_date.isoformat() if evidence.declared_event_date else None
        )
        return HandlerOutcome(
            result_code="CONTRACT_EXECUTION_EVIDENCE_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CONTRACT_EXECUTION_EVIDENCE",
                    "aggregate_id": str(command.act_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CONTRACT_EXECUTION_EVIDENCE",
                    aggregate_id=command.act_id,
                    aggregate_revision=1,
                    event_type="CONTRACT_EXECUTION_EVIDENCE_RECORDED",
                    payload={
                        "case_id": str(command.case_id),
                        "act_kind": evidence.act_kind.value,
                        "reception_outcome": (
                            evidence.reception_outcome.value if evidence.reception_outcome else None
                        ),
                        "declared_event_date": event_date,
                        "case_dce_version_id_at_recording": (
                            str(evidence.case_dce_version_id_at_recording)
                            if evidence.case_dce_version_id_at_recording
                            else None
                        ),
                        "contract_instrument_version_id": (
                            str(evidence.contract_instrument_version_id)
                            if evidence.contract_instrument_version_id
                            else None
                        ),
                    },
                ),
            ),
        )


def contract_execution_evidence_handlers() -> dict[str, RecordContractExecutionEvidenceHandler]:
    handler = RecordContractExecutionEvidenceHandler()
    return {RecordContractExecutionEvidenceCommand.command_type: handler}
