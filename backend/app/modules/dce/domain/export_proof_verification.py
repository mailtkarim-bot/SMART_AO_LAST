# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class ExportProofVerificationStatus(StrEnum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNAVAILABLE = "UNAVAILABLE"

@dataclass(frozen=True, slots=True)
class ExportProofVerification:
    status: ExportProofVerificationStatus
    calculated_sha256: str | None

def verify_export_proof(*, content: bytes | None, expected_sha256: str | None) -> ExportProofVerification:
    if content is None or expected_sha256 is None:
        return ExportProofVerification(ExportProofVerificationStatus.UNAVAILABLE, None)
    calculated = sha256(content).hexdigest()
    return ExportProofVerification(ExportProofVerificationStatus.MATCH if calculated == expected_sha256.lower() else ExportProofVerificationStatus.MISMATCH, calculated)
