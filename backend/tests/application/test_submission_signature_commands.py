from uuid import uuid4

import pytest
from app.modules.submission.application.signature_commands import (
    RecordSubmissionSignatureCommand,
    RequestSubmissionSignatureCommand,
)
from pydantic import ValidationError


def test_signature_request_contract_is_closed_and_provider_normalized() -> None:
    command = RequestSubmissionSignatureCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        signature_id=uuid4(),
        submission_package_id=uuid4(),
        expected_package_version=1,
        signer_membership_id=uuid4(),
        provider="DOCUSIGN",
    )
    assert command.provider == "DOCUSIGN"
    assert command.expected_package_version == 1


def test_signature_callback_requires_hashes_and_closed_outcome() -> None:
    command = RecordSubmissionSignatureCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        signature_id=uuid4(),
        submission_package_id=uuid4(),
        provider="DOCUSIGN",
        provider_reference_hash="a" * 64,
        signature_sha256="b" * 64,
        outcome="SIGNED",
    )
    assert command.outcome == "SIGNED"


@pytest.mark.parametrize(
    "field,value",
    [("provider_reference_hash", "not-a-hash"), ("signature_sha256", "not-a-hash")],
)
def test_signature_callback_rejects_unhashed_provider_facts(field: str, value: str) -> None:
    payload = {
        "command_id": uuid4(),
        "idempotency_key": uuid4(),
        "correlation_id": uuid4(),
        "signature_id": uuid4(),
        "submission_package_id": uuid4(),
        "provider": "DOCUSIGN",
        "provider_reference_hash": "a" * 64,
        "signature_sha256": "b" * 64,
        "outcome": "SIGNED",
    }
    payload[field] = value
    with pytest.raises(ValidationError):
        RecordSubmissionSignatureCommand(**payload)


def test_signature_request_preserves_legacy_idempotence_and_binds_new_hash_and_rationale():
    import json
    from hashlib import sha256

    from app.platform.events.dispatcher import canonical_request_hash

    ids = dict(signature_id=uuid4(), submission_package_id=uuid4(), signer_membership_id=uuid4())
    legacy = RequestSubmissionSignatureCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        expected_package_version=1,
        provider="TEST_PROVIDER",
        **ids,
    )
    payload = {
        **{key: str(value) for key, value in ids.items()},
        "expected_package_version": 1,
        "provider": "TEST_PROVIDER",
    }
    expected = sha256(
        json.dumps(
            {"command_type": "RequestSubmissionSignature", "payload": payload},
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    assert canonical_request_hash(legacy) == expected
    exact = RequestSubmissionSignatureCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        expected_package_version=1,
        expected_manifest_sha256="a" * 64,
        rationale="Demande humaine synthétique relue.",
        provider="TEST_PROVIDER",
        **ids,
    )
    assert canonical_request_hash(exact) != expected
    assert exact.model_dump()["rationale"] == "Demande humaine synthétique relue."


def test_signature_request_rejects_blank_human_rationale_at_the_http_boundary():
    from app.modules.submission.public.signature_contracts import RequestSubmissionSignatureRequest

    with pytest.raises(ValidationError):
        RequestSubmissionSignatureRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            signature_id=uuid4(),
            expected_package_version=1,
            rationale="   ",
        )
