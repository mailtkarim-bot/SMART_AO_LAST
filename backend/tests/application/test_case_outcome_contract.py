from uuid import uuid4

import pytest
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from pydantic import ValidationError


def base() -> dict[str, object]:
    return {
        "command_id": uuid4(),
        "idempotency_key": uuid4(),
        "correlation_id": uuid4(),
        "outcome_id": uuid4(),
        "case_id": uuid4(),
        "lot_reference": "01",
    }


def test_outcome_contract_distinguishes_won_and_unknown_evidence():
    won = RecordCaseOutcomeCommand(
        **base(),
        outcome="WON",
        source_locator="portal:receipt:1",
        reservations=["Sous réserve de validation du planning"],
    )
    unknown = RecordCaseOutcomeCommand(
        **base(), outcome="UNKNOWN", unknown_reason="Aucun retour contrôlé"
    )
    assert won.outcome == "WON" and won.reservations
    assert unknown.outcome == "UNKNOWN" and unknown.unknown_reason


def test_outcome_contract_is_closed():
    with pytest.raises(ValidationError):
        RecordCaseOutcomeCommand(**base(), outcome="WON", source_locator="x", invented_field=True)
