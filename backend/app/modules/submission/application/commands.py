from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import Field, SerializerFunctionWrapHandler, model_serializer

from app.modules.submission.public.contracts import PreparationSnapshotSource
from app.platform.events.command_contracts import ApplicationCommand


class PrepareSubmissionPackageCommand(ApplicationCommand):
    """Freeze the latest admissible technical and official-price references for human submission."""

    command_type = "PrepareSubmissionPackage"

    preparation_package_id: UUID
    expected_preparation_revision: int = Field(ge=0)
    submission_mode: Literal["FULL", "CANDIDATURE_ONLY"] = "FULL"
    candidature_only_reason: str | None = Field(default=None, min_length=1, max_length=1_000)

    preparation_snapshot_source: PreparationSnapshotSource | None = None

    @model_serializer(mode="wrap")
    def preserve_legacy_intent_hash(self, handler: SerializerFunctionWrapHandler) -> dict:
        serialized = handler(self)
        if self.preparation_snapshot_source is None:
            serialized.pop("preparation_snapshot_source", None)
        return serialized


class AuthorizeSubmissionPackageCommand(ApplicationCommand):
    """Record Patron authorization for one exact immutable package version."""

    command_type = "AuthorizeSubmissionPackage"

    authorization_id: UUID
    submission_package_id: UUID
    expected_package_version: int = Field(ge=1)
    rationale: str = Field(min_length=1, max_length=2_000)
