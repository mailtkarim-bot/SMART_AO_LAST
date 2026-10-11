"""Closed C10 references and compatibility of durable legacy retry hashes."""

import hashlib
import json
from uuid import uuid4

import pytest
from app.modules.submission.application.commands import (
    AuthorizeSubmissionPackageCommand,
    PrepareSubmissionPackageCommand,
)
from app.modules.submission.public.contracts import (
    AuthorizeSubmissionPackageRequest,
    PrepareSubmissionPackageRequest,
)
from app.platform.events.dispatcher import canonical_request_hash
from pydantic import ValidationError


def _body():
    return {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "expected_preparation_revision": 9,
        "submission_mode": "CANDIDATURE_ONLY",
        "candidature_only_reason": "Synthetic proof.",
    }


def _source():
    return {"snapshot_id": str(uuid4()), "snapshot_version": 1, "manifest_sha256": "a" * 64}


@pytest.mark.parametrize(
    "change",
    [
        {"snapshot_id": "invalid"},
        {"snapshot_version": 0},
        {"snapshot_version": True},
        {"snapshot_version": "1"},
        {"manifest_sha256": "a" * 63},
        {"manifest_sha256": "A" * 64},
        {"manifest_sha256": "a" * 64 + "\n"},
        {"storage_key": "private"},
    ],
)
def test_c10_source_reference_is_closed(change):
    with pytest.raises(ValidationError):
        PrepareSubmissionPackageRequest.model_validate(
            {**_body(), "preparation_snapshot_source": {**_source(), **change}}
        )


def test_legacy_canonical_hash_remains_byte_compatible():
    body = _body()
    preparation_id = uuid4()
    command = PrepareSubmissionPackageRequest.model_validate(body).to_command(
        preparation_package_id=preparation_id
    )
    payload = {
        "preparation_package_id": str(preparation_id),
        "expected_preparation_revision": 9,
        "submission_mode": "CANDIDATURE_ONLY",
        "candidature_only_reason": body["candidature_only_reason"],
    }
    old_canonical = json.dumps(
        {"command_type": "PrepareSubmissionPackage", "payload": payload},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    assert canonical_request_hash(command) == hashlib.sha256(old_canonical).hexdigest()
    assert "preparation_snapshot_source" not in command.model_dump(mode="json")
    explicit_null = PrepareSubmissionPackageCommand.model_validate(
        {**command.model_dump(), "preparation_snapshot_source": None}
    )
    assert canonical_request_hash(explicit_null) == canonical_request_hash(command)


def test_c10_source_is_part_of_the_retry_intent():
    source = _source()
    command = PrepareSubmissionPackageRequest.model_validate(
        {**_body(), "preparation_snapshot_source": source}
    ).to_command(preparation_package_id=uuid4())
    assert command.model_dump(mode="json")["preparation_snapshot_source"] == source
    changed = command.model_copy(
        update={
            "preparation_snapshot_source": command.preparation_snapshot_source.model_copy(
                update={"manifest_sha256": "b" * 64}
            )
        }
    )
    assert canonical_request_hash(command) != canonical_request_hash(changed)


def test_legacy_p5_hash_remains_byte_compatible():
    body = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "authorization_id": str(uuid4()),
        "expected_package_version": 3,
        "rationale": "Revue P5 effectuée.",
    }
    package_id = uuid4()
    command = AuthorizeSubmissionPackageRequest.model_validate(body).to_command(
        submission_package_id=package_id
    )
    payload = {
        "authorization_id": body["authorization_id"],
        "submission_package_id": str(package_id),
        "expected_package_version": 3,
        "rationale": body["rationale"],
    }
    old_canonical = json.dumps(
        {"command_type": "AuthorizeSubmissionPackage", "payload": payload},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    assert canonical_request_hash(command) == hashlib.sha256(old_canonical).hexdigest()
    assert "expected_manifest_sha256" not in command.model_dump(mode="json")
    explicit_null = AuthorizeSubmissionPackageCommand.model_validate(
        {**command.model_dump(), "expected_manifest_sha256": None}
    )
    assert canonical_request_hash(explicit_null) == canonical_request_hash(command)


@pytest.mark.parametrize("manifest_sha256", ["0" * 63, "A" * 64, "g" * 64, "0" * 64 + "\n"])
def test_expected_p5_manifest_hash_requires_lowercase_sha256(manifest_sha256):
    with pytest.raises(ValidationError):
        AuthorizeSubmissionPackageRequest.model_validate(
            {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "authorization_id": str(uuid4()),
                "expected_package_version": 1,
                "expected_manifest_sha256": manifest_sha256,
                "rationale": "Revue P5 effectuée.",
            }
        )
