from uuid import uuid4

import pytest
from app.modules.optimization.application.dated_commands import RecordDatedCapacityRequest
from pydantic import ValidationError


def request(**changes):
    return dict(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        run_id=uuid4(),
        expected_revision=0,
        context_sha256="a" * 64,
        demands=None,
        supplies=None,
        justification="Planning déclaré pour cette Affaire",
        human_confirmed=True,
        **changes,
    )


def test_missing_inputs_are_explicit_and_human_confirmation_required():
    parsed = RecordDatedCapacityRequest.model_validate(request())
    assert parsed.demands is None and parsed.supplies is None
    data = request()
    data["human_confirmed"] = False
    with pytest.raises(ValidationError):
        RecordDatedCapacityRequest.model_validate(data)


def test_duplicate_resources_and_partial_dates_are_refused():
    row = dict(
        id=str(uuid4()),
        label="Équipe A",
        resource_type="compagnons",
        units=2,
        start="2026-11-01",
        end="2026-11-03",
        source=dict(reference="Planning", revision="1", locator="L2"),
    )
    data = request()
    data["supplies"] = [row, row]
    with pytest.raises(ValidationError):
        RecordDatedCapacityRequest.model_validate(data)
    data["supplies"] = [{**row, "end": None}]
    with pytest.raises(ValidationError):
        RecordDatedCapacityRequest.model_validate(data)


def test_supplied_invalid_units_are_not_coerced():
    data = request()
    data["demands"] = [
        dict(
            id=str(uuid4()),
            label="Pose",
            resource_type=None,
            units=True,
            start=None,
            end=None,
            source=None,
            named_supply_id=None,
        )
    ]
    with pytest.raises(ValidationError):
        RecordDatedCapacityRequest.model_validate(data)
