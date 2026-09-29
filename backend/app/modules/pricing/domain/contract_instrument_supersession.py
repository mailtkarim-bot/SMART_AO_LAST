from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ContractInstrumentSupersession:
    case_id: UUID
    replacing_contract_instrument_version_id: UUID
    replaced_contract_instrument_version_id: UUID
    rationale: str

    def validate(self) -> None:
        if (
            self.replacing_contract_instrument_version_id
            == self.replaced_contract_instrument_version_id
        ):
            raise ValueError("CONTRACT_INSTRUMENT_SUPERSESSION_DISTINCT_VERSIONS_REQUIRED")
        if not self.rationale.strip() or len(self.rationale) > 2000:
            raise ValueError("CONTRACT_INSTRUMENT_SUPERSESSION_RATIONALE_REQUIRED")
