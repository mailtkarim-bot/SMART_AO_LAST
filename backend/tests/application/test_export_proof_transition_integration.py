from hashlib import sha256

from app.modules.dce.domain.export_proof_verification import ExportProofVerificationStatus, verify_export_proof


def test_match_can_supply_ready_proof_reference() -> None:
    content = b"local export"
    result = verify_export_proof(content=content, expected_sha256=sha256(content).hexdigest())
    assert result.status is ExportProofVerificationStatus.MATCH
    assert result.calculated_sha256 is not None


def test_mismatch_cannot_supply_ready_proof() -> None:
    result = verify_export_proof(content=b"local export", expected_sha256="f" * 64)
    assert result.status is ExportProofVerificationStatus.MISMATCH


def test_unavailable_keeps_export_unknown() -> None:
    result = verify_export_proof(content=None, expected_sha256="a" * 64)
    assert result.status is ExportProofVerificationStatus.UNAVAILABLE
