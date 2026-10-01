import pytest
from app.modules.decision.application.lifecycle_commands import DecisionContextReferenceInput
from pydantic import ValidationError


def test_profile_context_reference_requires_exact_version_hash() -> None:
    reference = DecisionContextReferenceInput(
        aggregate_type="BUSINESS_METHOD_PROFILE",
        aggregate_id="b6adff4a-fb98-4f0e-8dd6-ff719ec93ead",
        aggregate_revision=1,
        content_hash="a" * 64,
        reference_role="CONFIGURATION_USED",
    )
    assert reference.aggregate_revision == 1

    with pytest.raises(ValidationError):
        DecisionContextReferenceInput(
            aggregate_type="BUSINESS_METHOD_PROFILE",
            aggregate_id="b6adff4a-fb98-4f0e-8dd6-ff719ec93ead",
            aggregate_revision=0,
            reference_role="CONFIGURATION_USED",
        )
