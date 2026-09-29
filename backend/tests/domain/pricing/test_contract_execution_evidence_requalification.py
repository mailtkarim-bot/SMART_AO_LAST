from uuid import uuid4

import pytest
from app.modules.pricing.domain.contract_execution_evidence_requalification import (
    ContractExecutionEvidenceRequalification,
    ContractExecutionEvidenceRequalificationDecision,
)


def test_human_requalification_keeps_its_decision_separate_from_legal_conclusion() -> None:
    requalification = ContractExecutionEvidenceRequalification(
        case_id=uuid4(),
        act_id=uuid4(),
        supersession_id=uuid4(),
        revision=1,
        decision=ContractExecutionEvidenceRequalificationDecision.RELINKED_TO_DECLARED_VERSION,
        resulting_contract_instrument_version_id=uuid4(),
        rationale="Le Patron rattache la déclaration à une autre version sourcée.",
    )

    requalification.validate()
    assert requalification.revision == 1
    assert not hasattr(requalification, "legal_conclusion")
    assert not hasattr(requalification, "applicability_status")


@pytest.mark.parametrize(
    ("decision", "result_version_id", "revision", "rationale", "error"),
    [
        ("RELINKED_TO_DECLARED_VERSION", None, 1, "Revue", "RESULT_VERSION_REQUIRED"),
        ("NEEDS_CLARIFICATION", uuid4(), 1, "Revue", "RESULT_VERSION_NOT_ALLOWED"),
        ("RETAINED_AS_DECLARED", None, 1, "Revue", "RESULT_VERSION_REQUIRED"),
        ("RETAINED_AS_DECLARED", uuid4(), 0, "Revue", "REVISION_REQUIRED"),
        ("RETAINED_AS_DECLARED", uuid4(), 1, "  ", "RATIONALE_REQUIRED"),
    ],
)
def test_rejects_inconsistent_requalification_facts(
    decision, result_version_id, revision, rationale, error
) -> None:
    item = ContractExecutionEvidenceRequalification(
        case_id=uuid4(),
        act_id=uuid4(),
        supersession_id=uuid4(),
        revision=revision,
        decision=ContractExecutionEvidenceRequalificationDecision(decision),
        resulting_contract_instrument_version_id=result_version_id,
        rationale=rationale,
    )
    with pytest.raises(ValueError, match=error):
        item.validate()
