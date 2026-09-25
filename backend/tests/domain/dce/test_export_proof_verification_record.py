# ruff: noqa: E501
from uuid import uuid4

import pytest
from app.modules.dce.domain.export_proof_verification_record import (
    ExportProofVerificationRecord,
    ExportVerificationOutcome,
)


def test_match_record_requires_hash() -> None:
    ExportProofVerificationRecord(uuid4(), ExportVerificationOutcome.MATCH, "a" * 64, uuid4()).validate()

@pytest.mark.parametrize("outcome, digest, error", [(ExportVerificationOutcome.MATCH, None, "MATCH_HASH_REQUIRED"), (ExportVerificationOutcome.UNAVAILABLE, "a" * 64, "UNAVAILABLE_HASH_FORBIDDEN")])
def test_verification_record_rejects_incoherent_hash(outcome, digest, error) -> None:
    with pytest.raises(ValueError, match=error):
        ExportProofVerificationRecord(uuid4(), outcome, digest, uuid4()).validate()
