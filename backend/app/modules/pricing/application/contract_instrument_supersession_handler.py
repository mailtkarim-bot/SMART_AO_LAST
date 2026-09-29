from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.contract_execution_evidence_commands import (
    DeclareContractInstrumentSupersessionCommand,
)
from app.modules.pricing.domain.contract_instrument_supersession import (
    ContractInstrumentSupersession,
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


class DeclareContractInstrumentSupersessionHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: DeclareContractInstrumentSupersessionCommand,
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
        if (
            command.replacing_contract_instrument_version_id
            == command.replaced_contract_instrument_version_id
        ):
            raise CommandExecutionError(
                "CONTRACT_INSTRUMENT_SUPERSESSION_DISTINCT_VERSIONS_REQUIRED"
            )

        replacing = session.scalar(
            sa.select(ContractInstrumentVersionRecord).where(
                ContractInstrumentVersionRecord.tenant_id == tenant_id,
                ContractInstrumentVersionRecord.case_id == command.case_id,
                ContractInstrumentVersionRecord.id
                == command.replacing_contract_instrument_version_id,
            )
        )
        replaced = session.scalar(
            sa.select(ContractInstrumentVersionRecord).where(
                ContractInstrumentVersionRecord.tenant_id == tenant_id,
                ContractInstrumentVersionRecord.case_id == command.case_id,
                ContractInstrumentVersionRecord.id
                == command.replaced_contract_instrument_version_id,
            )
        )
        if replacing is None or replaced is None:
            raise CommandExecutionError("CONTRACT_INSTRUMENT_VERSION_NOT_FOUND_OR_FORBIDDEN")
        if replacing.instrument_kind != "AMENDMENT":
            raise CommandExecutionError("CONTRACT_INSTRUMENT_REPLACING_VERSION_MUST_BE_AMENDMENT")
        if session.scalar(
            sa.select(ContractInstrumentSupersessionRecord.id).where(
                ContractInstrumentSupersessionRecord.tenant_id == tenant_id,
                ContractInstrumentSupersessionRecord.case_id == command.case_id,
                ContractInstrumentSupersessionRecord.replacing_contract_instrument_version_id
                == command.replacing_contract_instrument_version_id,
                ContractInstrumentSupersessionRecord.replaced_contract_instrument_version_id
                == command.replaced_contract_instrument_version_id,
            )
        ) is not None:
            raise CommandExecutionError("CONTRACT_INSTRUMENT_SUPERSESSION_ALREADY_RECORDED")
        try:
            declaration = ContractInstrumentSupersession(
                case_id=command.case_id,
                replacing_contract_instrument_version_id=(
                    command.replacing_contract_instrument_version_id
                ),
                replaced_contract_instrument_version_id=(
                    command.replaced_contract_instrument_version_id
                ),
                rationale=command.rationale,
            )
            declaration.validate()
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error

        session.add(
            ContractInstrumentSupersessionRecord(
                id=command.supersession_id,
                tenant_id=tenant_id,
                case_id=declaration.case_id,
                replacing_contract_instrument_version_id=(
                    declaration.replacing_contract_instrument_version_id
                ),
                replaced_contract_instrument_version_id=(
                    declaration.replaced_contract_instrument_version_id
                ),
                rationale=declaration.rationale.strip(),
                actor_id=UUID(str(context.actor_id)),
            )
        )
        return HandlerOutcome(
            result_code="CONTRACT_INSTRUMENT_SUPERSESSION_DECLARED",
            aggregate_refs=(
                {
                    "aggregate_type": "CONTRACT_INSTRUMENT_SUPERSESSION",
                    "aggregate_id": str(command.supersession_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CONTRACT_INSTRUMENT_SUPERSESSION",
                    aggregate_id=command.supersession_id,
                    aggregate_revision=1,
                    event_type="CONTRACT_INSTRUMENT_SUPERSESSION_DECLARED",
                    payload={
                        "case_id": str(command.case_id),
                        "replacing_contract_instrument_version_id": str(
                            command.replacing_contract_instrument_version_id
                        ),
                        "replaced_contract_instrument_version_id": str(
                            command.replaced_contract_instrument_version_id
                        ),
                    },
                ),
            ),
        )


def contract_instrument_supersession_handlers() -> dict[
    str, DeclareContractInstrumentSupersessionHandler
]:
    handler = DeclareContractInstrumentSupersessionHandler()
    return {DeclareContractInstrumentSupersessionCommand.command_type: handler}
