from uuid import uuid4

import pytest
from app.modules.decision.application.lifecycle_commands import DecisionContextReferenceInput
from pydantic import ValidationError


def test_capacity_source_requires_exact_revision_and_hash():
    data = dict(
        aggregate_type="CAPACITY_RUN",
        aggregate_id=uuid4(),
        aggregate_revision=1,
        content_hash="a" * 64,
        reference_role="CAPACITY_HYPOTHESIS",
    )
    assert DecisionContextReferenceInput.model_validate(data).aggregate_type == "CAPACITY_RUN"
    for change in ({"content_hash": None}, {"aggregate_revision": 0}):
        with pytest.raises(ValidationError):
            DecisionContextReferenceInput.model_validate({**data, **change})
