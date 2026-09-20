from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class PrepareSubmissionPackageRequest(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    expected_preparation_revision: int = Field(ge=0)
    submission_mode: Literal["FULL", "CANDIDATURE_ONLY"] = "FULL"
    candidature_only_reason: str | None = Field(default=None, min_length=1, max_length=1_000)

    def to_command(self, *, preparation_package_id: UUID):
        from app.modules.submission.application.commands import PrepareSubmissionPackageCommand

        return PrepareSubmissionPackageCommand(
            command_id=self.command_id,
            idempotency_key=self.idempotency_key,
            preparation_package_id=preparation_package_id,
            expected_preparation_revision=self.expected_preparation_revision,
            submission_mode=self.submission_mode,
            candidature_only_reason=self.candidature_only_reason,
        )


class AuthorizeSubmissionPackageRequest(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    authorization_id: UUID
    expected_package_version: int = Field(ge=1)
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
    authorization_status: Literal["AUTHORIZED", "NOT_AUTHORIZED"]
    external_submission: Literal["NOT_PERFORMED"]
