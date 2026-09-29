from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ContractExecutionEvidenceRequalificationDecision(StrEnum):
    RETAINED_AS_DECLARED = "RETAINED_AS_DECLARED"
    RELINKED_TO_DECLARED_VERSION = "RELINKED_TO_DECLARED_VERSION"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"


@dataclass(frozen=True, slots=True)
class ContractExecutionEvidenceRequalification:
    case_id: UUID
    act_id: UUID
    supersession_id: UUID
    revision: int
    decision: ContractExecutionEvidenceRequalificationDecision
    resulting_contract_instrument_version_id: UUID | None
    rationale: str

    def validate(self) -> None:
        if self.revision < 1:
            raise ValueError("CONTRACT_EXECUTION_REQUALIFICATION_REVISION_REQUIRED")
        if not self.rationale.strip() or len(self.rationale) > 2000:
            raise ValueError("CONTRACT_EXECUTION_REQUALIFICATION_RATIONALE_REQUIRED")
        has_result = self.resulting_contract_instrument_version_id is not None
        if self.decision is ContractExecutionEvidenceRequalificationDecision.NEEDS_CLARIFICATION:
            if has_result:
                raise ValueError("CONTRACT_EXECUTION_REQUALIFICATION_RESULT_VERSION_NOT_ALLOWED")
        elif not has_result:
            raise ValueError("CONTRACT_EXECUTION_REQUALIFICATION_RESULT_VERSION_REQUIRED")
