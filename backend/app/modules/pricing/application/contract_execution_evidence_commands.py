from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from app.modules.pricing.domain.contract_execution_evidence import ContractReceptionOutcome
from app.platform.events.command_contracts import ApplicationCommand


class RecordContractExecutionEvidenceCommand(ApplicationCommand):
    command_type = "RecordContractExecutionEvidence"
    act_id: UUID
    case_id: UUID
    act_kind: Literal["WORK_RECEPTION", "RIGHTS_PRESERVATION", "CONTRACT_EXIT"]
    reception_outcome: ContractReceptionOutcome | None = None
    summary: str = Field(min_length=1, max_length=2000)
    source_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )
    declared_event_date: date | None = None
    contract_instrument_version_id: UUID | None = None


class RecordContractInstrumentVersionCommand(ApplicationCommand):
    command_type = "RecordContractInstrumentVersion"
    contract_instrument_version_id: UUID
    case_id: UUID
    instrument_kind: Literal["SIGNED_CONTRACT", "AMENDMENT"]
    version_reference: str = Field(min_length=1, max_length=500)
    source_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )


class DeclareContractInstrumentSupersessionCommand(ApplicationCommand):
    command_type = "DeclareContractInstrumentSupersession"
    supersession_id: UUID
    case_id: UUID
    replacing_contract_instrument_version_id: UUID
    replaced_contract_instrument_version_id: UUID
    rationale: str = Field(min_length=1, max_length=2000)


class RecordContractExecutionEvidenceRequalificationCommand(ApplicationCommand):
    command_type = "RecordContractExecutionEvidenceRequalification"
    requalification_id: UUID
    case_id: UUID
    act_id: UUID
    supersession_id: UUID
    expected_revision: int = Field(ge=0)
    decision: Literal["RETAINED_AS_DECLARED", "RELINKED_TO_DECLARED_VERSION", "NEEDS_CLARIFICATION"]
    resulting_contract_instrument_version_id: UUID | None = None
    rationale: str = Field(min_length=1, max_length=2000)
