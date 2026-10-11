from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PreparationSnapshotSource(BaseModel):
    """Exact internal C10 origin read by the human caller; never an external receipt."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    snapshot_id: UUID
    snapshot_version: int = Field(ge=1, strict=True)
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class PrepareSubmissionPackageRequest(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    expected_preparation_revision: int = Field(ge=0)
    submission_mode: Literal["FULL", "CANDIDATURE_ONLY"] = "FULL"
    candidature_only_reason: str | None = Field(default=None, min_length=1, max_length=1_000)

    preparation_snapshot_source: PreparationSnapshotSource | None = None

    def to_command(self, *, preparation_package_id: UUID):
        from app.modules.submission.application.commands import PrepareSubmissionPackageCommand

        return PrepareSubmissionPackageCommand(
            command_id=self.command_id,
            idempotency_key=self.idempotency_key,
            preparation_package_id=preparation_package_id,
            expected_preparation_revision=self.expected_preparation_revision,
            submission_mode=self.submission_mode,
            candidature_only_reason=self.candidature_only_reason,
            preparation_snapshot_source=self.preparation_snapshot_source,
        )


class AuthorizeSubmissionPackageRequest(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    authorization_id: UUID
    expected_package_version: int = Field(ge=1)
    expected_manifest_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    rationale: str = Field(min_length=1, max_length=2_000)

    def to_command(self, *, submission_package_id: UUID):
        from app.modules.submission.application.commands import AuthorizeSubmissionPackageCommand

        return AuthorizeSubmissionPackageCommand(
            command_id=self.command_id,
            idempotency_key=self.idempotency_key,
            correlation_id=self.correlation_id,
            authorization_id=self.authorization_id,
            submission_package_id=submission_package_id,
            expected_package_version=self.expected_package_version,
            expected_manifest_sha256=self.expected_manifest_sha256,
            rationale=self.rationale,
        )


class SubmissionPackageCommandResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    result_code: str
    aggregate_refs: list[dict[str, object]]
    event_ids: list[UUID]
    replayed: bool


class SubmissionPackageManifestResponse(BaseModel):
    submission_package_id: UUID
    package_version: int
    state: Literal["PRET_CONTROLE", "AUTORISE_DEPOT"]
    manifest_sha256: str
    manifest: dict[str, object]
    source_origin_state: Literal["RECORDED", "UNKNOWN"] = "UNKNOWN"
    authorization_status: Literal["AUTHORIZED", "NOT_AUTHORIZED"]
    external_submission: Literal["NOT_PERFORMED"]
