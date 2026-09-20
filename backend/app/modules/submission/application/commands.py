from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class PrepareSubmissionPackageCommand(ApplicationCommand):
    """Freeze the latest admissible technical and official-price references for human submission."""

    command_type = "PrepareSubmissionPackage"

    preparation_package_id: UUID
    expected_preparation_revision: int = Field(ge=0)
    submission_mode: Literal["FULL", "CANDIDATURE_ONLY"] = "FULL"
    candidature_only_reason: str | None = Field(default=None, min_length=1, max_length=1_000)


class AuthorizeSubmissionPackageCommand(ApplicationCommand):
    """Record Patron authorization for one exact immutable package version."""

    command_type = "AuthorizeSubmissionPackage"

    authorization_id: UUID
    submission_package_id: UUID
    expected_package_version: int = Field(ge=1)
    rationale: str = Field(min_length=1, max_length=2_000)
