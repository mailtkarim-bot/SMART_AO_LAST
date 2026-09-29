from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ContractInstrumentKind(StrEnum):
    SIGNED_CONTRACT = "SIGNED_CONTRACT"
    AMENDMENT = "AMENDMENT"


@dataclass(frozen=True, slots=True)
class ContractInstrumentVersion:
    case_id: UUID
    instrument_kind: ContractInstrumentKind
    version_reference: str
    source_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def validate(self) -> None:
        if not self.version_reference.strip() or len(self.version_reference) > 500:
            raise ValueError("CONTRACT_INSTRUMENT_REFERENCE_REQUIRED")
        if (
            not self.source_refs
            or len(self.source_refs) > 32
            or any(not ref.strip() or len(ref) > 1000 for ref in self.source_refs)
        ):
            raise ValueError("CONTRACT_INSTRUMENT_SOURCE_REQUIRED")
        if (
            not self.evidence_refs
            or len(self.evidence_refs) > 32
            or any(not ref.strip() or len(ref) > 1000 for ref in self.evidence_refs)
        ):
            raise ValueError("CONTRACT_INSTRUMENT_PROOF_REQUIRED")


def build_contract_instrument_version(
    *,
    case_id: UUID,
    instrument_kind: ContractInstrumentKind,
    version_reference: str,
    source_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
) -> ContractInstrumentVersion:
    version = ContractInstrumentVersion(
        case_id=case_id,
        instrument_kind=instrument_kind,
        version_reference=version_reference.strip(),
        source_refs=source_refs,
        evidence_refs=evidence_refs,
    )
    version.validate()
    return version
