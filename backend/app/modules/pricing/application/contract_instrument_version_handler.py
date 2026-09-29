from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.contract_execution_evidence_commands import (
    RecordContractInstrumentVersionCommand,
)
from app.modules.pricing.domain.contract_instrument_version import (
    ContractInstrumentKind,
    build_contract_instrument_version,
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


class RecordContractInstrumentVersionHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordContractInstrumentVersionCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        if (
            session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == tenant_id,
                    CaseRecord.id == command.case_id,
                )
            )
            is None
        ):
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if (
            session.scalar(
                sa.select(ContractInstrumentVersionRecord.id).where(
                    ContractInstrumentVersionRecord.tenant_id == tenant_id,
                    ContractInstrumentVersionRecord.id == command.contract_instrument_version_id,
                )
            )
            is not None
        ):
            raise CommandExecutionError("CONTRACT_INSTRUMENT_VERSION_ID_REUSED")
        if (
            session.scalar(
                sa.select(ContractInstrumentVersionRecord.id).where(
                    ContractInstrumentVersionRecord.tenant_id == tenant_id,
                    ContractInstrumentVersionRecord.case_id == command.case_id,
                    ContractInstrumentVersionRecord.instrument_kind == command.instrument_kind,
                    ContractInstrumentVersionRecord.version_reference
                    == command.version_reference.strip(),
                )
            )
            is not None
        ):
            raise CommandExecutionError("CONTRACT_INSTRUMENT_VERSION_REFERENCE_ALREADY_RECORDED")
        try:
            version = build_contract_instrument_version(
                case_id=command.case_id,
                instrument_kind=ContractInstrumentKind(command.instrument_kind),
                version_reference=command.version_reference,
                source_refs=command.source_refs,
                evidence_refs=command.evidence_refs,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        session.add(
            ContractInstrumentVersionRecord(
                id=command.contract_instrument_version_id,
                tenant_id=tenant_id,
                case_id=version.case_id,
                instrument_kind=version.instrument_kind.value,
                version_reference=version.version_reference,
                source_refs_json=list(version.source_refs),
                evidence_refs_json=list(version.evidence_refs),
                actor_id=UUID(str(context.actor_id)),
            )
        )
        return HandlerOutcome(
            result_code="CONTRACT_INSTRUMENT_VERSION_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CONTRACT_INSTRUMENT_VERSION",
                    "aggregate_id": str(command.contract_instrument_version_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CONTRACT_INSTRUMENT_VERSION",
                    aggregate_id=command.contract_instrument_version_id,
                    aggregate_revision=1,
                    event_type="CONTRACT_INSTRUMENT_VERSION_RECORDED",
                    payload={
                        "case_id": str(command.case_id),
                        "instrument_kind": version.instrument_kind.value,
                    },
                ),
            ),
        )


def contract_instrument_version_handlers() -> dict[str, RecordContractInstrumentVersionHandler]:
    handler = RecordContractInstrumentVersionHandler()
    return {RecordContractInstrumentVersionCommand.command_type: handler}
