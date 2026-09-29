from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.contract_execution_evidence_commands import (
    RecordContractExecutionEvidenceRequalificationCommand,
)
from app.modules.pricing.domain.contract_execution_evidence_requalification import (
    ContractExecutionEvidenceRequalification,
    ContractExecutionEvidenceRequalificationDecision,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence_requalification import (
    ContractExecutionEvidenceRequalificationRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
    ContractInstrumentSupersessionRecord,
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


class RecordContractExecutionEvidenceRequalificationHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordContractExecutionEvidenceRequalificationCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        if session.scalar(
            sa.select(CaseRecord.id).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == command.case_id,
            )
        ) is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(
            sa.select(ContractExecutionEvidenceRequalificationRecord.id).where(
                ContractExecutionEvidenceRequalificationRecord.tenant_id == tenant_id,
                ContractExecutionEvidenceRequalificationRecord.id == command.requalification_id,
            )
        ) is not None:
            raise CommandExecutionError("CONTRACT_EXECUTION_REQUALIFICATION_ID_REUSED")

        act = session.scalar(
            sa.select(ContractExecutionEvidenceRecord)
            .where(
                ContractExecutionEvidenceRecord.tenant_id == tenant_id,
                ContractExecutionEvidenceRecord.case_id == command.case_id,
                ContractExecutionEvidenceRecord.id == command.act_id,
            )
            .with_for_update()
        )
        if act is None:
            raise CommandExecutionError("CONTRACT_EXECUTION_EVIDENCE_NOT_FOUND_OR_FORBIDDEN")
        supersession = session.scalar(
            sa.select(ContractInstrumentSupersessionRecord).where(
                ContractInstrumentSupersessionRecord.tenant_id == tenant_id,
                ContractInstrumentSupersessionRecord.case_id == command.case_id,
                ContractInstrumentSupersessionRecord.id == command.supersession_id,
            )
        )
        if (
            supersession is None
            or act.contract_instrument_version_id
            != supersession.replaced_contract_instrument_version_id
        ):
            raise CommandExecutionError("CONTRACT_EXECUTION_EVIDENCE_NOT_REVIEW_REQUIRED")

        latest_revision = session.scalar(
            sa.select(sa.func.max(ContractExecutionEvidenceRequalificationRecord.revision)).where(
                ContractExecutionEvidenceRequalificationRecord.tenant_id == tenant_id,
                ContractExecutionEvidenceRequalificationRecord.case_id == command.case_id,
                ContractExecutionEvidenceRequalificationRecord.act_id == command.act_id,
                ContractExecutionEvidenceRequalificationRecord.supersession_id
                == command.supersession_id,
            )
        ) or 0
        if command.expected_revision != latest_revision:
            raise CommandExecutionError("CONTRACT_EXECUTION_REQUALIFICATION_REVISION_CONFLICT")

        decision = ContractExecutionEvidenceRequalificationDecision(command.decision)
        resulting_version_id = command.resulting_contract_instrument_version_id
        if decision is ContractExecutionEvidenceRequalificationDecision.RETAINED_AS_DECLARED:
            if resulting_version_id is not None:
                raise CommandExecutionError(
                    "CONTRACT_EXECUTION_REQUALIFICATION_RESULT_VERSION_NOT_ALLOWED"
                )
            resulting_version_id = act.contract_instrument_version_id
        elif decision is ContractExecutionEvidenceRequalificationDecision.NEEDS_CLARIFICATION:
            if resulting_version_id is not None:
                raise CommandExecutionError(
                    "CONTRACT_EXECUTION_REQUALIFICATION_RESULT_VERSION_NOT_ALLOWED"
                )
        else:
            if resulting_version_id is None:
                raise CommandExecutionError(
                    "CONTRACT_EXECUTION_REQUALIFICATION_RESULT_VERSION_REQUIRED"
                )
            if session.scalar(
                sa.select(ContractInstrumentVersionRecord.id).where(
                    ContractInstrumentVersionRecord.tenant_id == tenant_id,
                    ContractInstrumentVersionRecord.case_id == command.case_id,
                    ContractInstrumentVersionRecord.id == resulting_version_id,
                )
            ) is None:
                raise CommandExecutionError("CONTRACT_INSTRUMENT_VERSION_NOT_FOUND_OR_FORBIDDEN")

        requalification = ContractExecutionEvidenceRequalification(
            case_id=command.case_id,
            act_id=command.act_id,
            supersession_id=command.supersession_id,
            revision=latest_revision + 1,
            decision=decision,
            resulting_contract_instrument_version_id=resulting_version_id,
            rationale=command.rationale,
        )
        try:
            requalification.validate()
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error

        session.add(
            ContractExecutionEvidenceRequalificationRecord(
                id=command.requalification_id,
                tenant_id=tenant_id,
                case_id=command.case_id,
                act_id=command.act_id,
                supersession_id=command.supersession_id,
                revision=requalification.revision,
                decision=requalification.decision.value,
                resulting_contract_instrument_version_id=(
                    requalification.resulting_contract_instrument_version_id
                ),
                rationale=requalification.rationale.strip(),
                actor_id=UUID(str(context.actor_id)),
            )
        )
        return HandlerOutcome(
            result_code="CONTRACT_EXECUTION_EVIDENCE_REQUALIFICATION_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CONTRACT_EXECUTION_EVIDENCE_REQUALIFICATION",
                    "aggregate_id": str(command.requalification_id),
                    "aggregate_revision": requalification.revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CONTRACT_EXECUTION_EVIDENCE_REQUALIFICATION",
                    aggregate_id=command.requalification_id,
                    aggregate_revision=requalification.revision,
                    event_type="CONTRACT_EXECUTION_EVIDENCE_REQUALIFICATION_RECORDED",
                    payload={
                        "case_id": str(command.case_id),
                        "act_id": str(command.act_id),
                        "supersession_id": str(command.supersession_id),
                        "decision": requalification.decision.value,
                    },
                ),
            ),
        )


def contract_execution_evidence_requalification_handlers() -> dict[
    str, RecordContractExecutionEvidenceRequalificationHandler
]:
    handler = RecordContractExecutionEvidenceRequalificationHandler()
    return {RecordContractExecutionEvidenceRequalificationCommand.command_type: handler}
