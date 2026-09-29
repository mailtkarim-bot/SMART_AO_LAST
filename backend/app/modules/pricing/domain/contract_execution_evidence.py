from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID


class ContractExecutionActKind(StrEnum):
    WORK_RECEPTION = "WORK_RECEPTION"
    RIGHTS_PRESERVATION = "RIGHTS_PRESERVATION"
    CONTRACT_EXIT = "CONTRACT_EXIT"


class ContractReceptionOutcome(StrEnum):
    WITH_RESERVATIONS = "WITH_RESERVATIONS"
    UNDER_RESERVATIONS = "UNDER_RESERVATIONS"
    WITHOUT_RESERVATIONS = "WITHOUT_RESERVATIONS"


@dataclass(frozen=True, slots=True)
class ContractExecutionEvidence:
    case_id: UUID
    case_dce_version_id_at_recording: UUID | None
    contract_instrument_version_id: UUID | None
    act_kind: ContractExecutionActKind
    reception_outcome: ContractReceptionOutcome | None
    summary: str
    source_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    declared_event_date: date | None = None

    def validate(self) -> None:
        if not self.summary.strip():
            raise ValueError("CONTRACT_EXECUTION_SUMMARY_REQUIRED")
        if not self.source_refs or any(
            not ref.strip() or len(ref) > 1000 for ref in self.source_refs
        ):
            raise ValueError("CONTRACT_EXECUTION_SOURCE_REQUIRED")
        if not self.evidence_refs or any(
            not ref.strip() or len(ref) > 1000 for ref in self.evidence_refs
        ):
            raise ValueError("CONTRACT_EXECUTION_EVIDENCE_REQUIRED")
        if self.act_kind is ContractExecutionActKind.WORK_RECEPTION:
            if self.reception_outcome is None:
                raise ValueError("CONTRACT_RECEPTION_OUTCOME_REQUIRED")
        elif self.reception_outcome is not None:
            raise ValueError("CONTRACT_RECEPTION_OUTCOME_NOT_APPLICABLE")


def build_contract_execution_evidence(
    *,
    case_id: UUID,
    act_kind: ContractExecutionActKind,
    summary: str,
    source_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    declared_event_date: date | None = None,
    case_dce_version_id_at_recording: UUID | None = None,
    contract_instrument_version_id: UUID | None = None,
    reception_outcome: ContractReceptionOutcome | None = None,
) -> ContractExecutionEvidence:
    evidence = ContractExecutionEvidence(
        case_id=case_id,
        case_dce_version_id_at_recording=case_dce_version_id_at_recording,
        contract_instrument_version_id=contract_instrument_version_id,
        act_kind=act_kind,
        reception_outcome=reception_outcome,
        summary=summary,
        source_refs=source_refs,
        evidence_refs=evidence_refs,
        declared_event_date=declared_event_date,
    )
    evidence.validate()
    return evidence
