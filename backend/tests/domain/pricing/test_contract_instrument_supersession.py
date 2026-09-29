from uuid import uuid4

import pytest
from app.modules.pricing.domain.contract_instrument_supersession import (
    ContractInstrumentSupersession,
)


def test_supersession_is_a_human_declaration_between_two_distinct_versions() -> None:
    replacing_id, replaced_id = uuid4(), uuid4()
    declaration = ContractInstrumentSupersession(
        case_id=uuid4(),
        replacing_contract_instrument_version_id=replacing_id,
        replaced_contract_instrument_version_id=replaced_id,
        rationale="Le Patron rattache l’avenant à la version contractuelle antérieure.",
    )

    declaration.validate()
    assert declaration.replacing_contract_instrument_version_id == replacing_id
    assert declaration.replaced_contract_instrument_version_id == replaced_id
    assert not hasattr(declaration, "legal_conclusion")


@pytest.mark.parametrize(
    ("replacing_id", "replaced_id", "rationale", "error"),
    [
        ("same", "same", "Déclaration humaine", "DISTINCT_VERSIONS_REQUIRED"),
        ("new", "old", "  ", "RATIONALE_REQUIRED"),
        ("new", "old", "r" * 2001, "RATIONALE_REQUIRED"),
    ],
)
def test_rejects_invalid_supersession_declaration(
    replacing_id, replaced_id, rationale, error
) -> None:
    same_id = uuid4()
    declaration = ContractInstrumentSupersession(
        case_id=uuid4(),
        replacing_contract_instrument_version_id=same_id if replacing_id == "same" else uuid4(),
        replaced_contract_instrument_version_id=same_id if replaced_id == "same" else uuid4(),
        rationale=rationale,
    )
    with pytest.raises(ValueError, match=error):
        declaration.validate()
