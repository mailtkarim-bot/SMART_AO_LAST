from uuid import uuid4

import pytest
from app.modules.dce.application.contract_baseline_commands import (
    RecordContractBaselineImpactCommand,
)


def test_revision_command_keeps_revision_identity_explicit() -> None:
    command = RecordContractBaselineImpactCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        proof_id=uuid4(),
        case_id=uuid4(),
        baseline_observation_id=uuid4(),
        proof_revision=2,
        baseline_source_refs=("dce://ccap/page-4",),
        baseline_statement="Baseline",
        status="HUMAN_REVIEW_REQUIRED",
    )
    assert command.proof_revision == 2
    assert command.baseline_observation_id is not None


def test_superseded_revision_is_an_explicit_non_success_state() -> None:
    command = RecordContractBaselineImpactCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        proof_id=uuid4(),
        case_id=uuid4(),
        baseline_observation_id=uuid4(),
        proof_revision=2,
        baseline_source_refs=("rectificatif://p1",),
        baseline_statement="Ancienne baseline",
        status="SUPERSEDED",
    )
    assert command.status == "SUPERSEDED"


@pytest.mark.parametrize("revision", [0, -1])
def test_revision_must_be_positive(revision: int) -> None:
    with pytest.raises(ValueError):
        RecordContractBaselineImpactCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            proof_id=uuid4(),
            case_id=uuid4(),
            baseline_observation_id=uuid4(),
            proof_revision=revision,
            baseline_source_refs=("source",),
            baseline_statement="Baseline",
            status="UNKNOWN",
        )
