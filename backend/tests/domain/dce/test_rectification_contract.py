from uuid import uuid4

import pytest
from app.modules.dce.application.commands import RegisterDceVersionCommand
from pydantic import ValidationError

from tests.application.test_register_dce_version import _command


@pytest.mark.parametrize(
    "replacement",
    [
        {"predecessor_dce_version_id": str(uuid4())},
        {"expected_predecessor_revision": 0},
        {"replacement_reason": "Motif isolé"},
        {"predecessor_dce_version_id": str(uuid4()), "expected_predecessor_revision": 0},
        {
            "predecessor_dce_version_id": str(uuid4()),
            "expected_predecessor_revision": -1,
            "replacement_reason": "Motif",
        },
        {
            "predecessor_dce_version_id": str(uuid4()),
            "expected_predecessor_revision": 0,
            "replacement_reason": "  ",
        },
    ],
)
def test_rectification_requires_complete_and_bounded_human_intent(replacement):
    payload = _command(consultation_id=uuid4()).model_dump(mode="json")
    with pytest.raises(ValidationError):
        RegisterDceVersionCommand.model_validate(
            {**payload, "provenance_channel": "RECTIFICATION", **replacement}
        )


def test_replacement_cannot_target_itself_or_claim_a_non_rectification_channel():
    command = _command(consultation_id=uuid4())
    fields = {
        "predecessor_dce_version_id": str(uuid4()),
        "expected_predecessor_revision": 0,
        "replacement_reason": "Source synthétique exacte.",
    }
    with pytest.raises(ValidationError):
        RegisterDceVersionCommand.model_validate({**command.model_dump(), **fields})
    with pytest.raises(ValidationError):
        RegisterDceVersionCommand.model_validate(
            {
                **command.model_dump(),
                **fields,
                "provenance_channel": "RECTIFICATION",
                "predecessor_dce_version_id": command.dce_version_id,
            }
        )
