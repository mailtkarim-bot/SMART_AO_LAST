from hashlib import sha256

from app.modules.dce.domain.export_proof_verification import (
    ExportProofVerificationStatus,
    verify_export_proof,
)


def test_export_proof_matches_local_content() -> None:
    content = b"export"
    result = verify_export_proof(content=content, expected_sha256=sha256(content).hexdigest())
    assert result.status is ExportProofVerificationStatus.MATCH

def test_export_proof_mismatch_is_explicit() -> None:
    result = verify_export_proof(content=b"export", expected_sha256="0" * 64)
    assert result.status is ExportProofVerificationStatus.MISMATCH

def test_export_proof_unavailable_does_not_become_success() -> None:
    result = verify_export_proof(content=None, expected_sha256=None)
    assert result.status is ExportProofVerificationStatus.UNAVAILABLE
