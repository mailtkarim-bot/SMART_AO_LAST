from uuid import UUID

from pydantic import Field, SerializerFunctionWrapHandler, model_serializer

from app.platform.events.command_contracts import ApplicationCommand


class RequestSubmissionSignatureCommand(ApplicationCommand):
    """Request an external electronic signature for one immutable submission manifest."""

    command_type = "RequestSubmissionSignature"

    signature_id: UUID
    submission_package_id: UUID
    expected_package_version: int = Field(ge=1)
    expected_manifest_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    rationale: str | None = Field(default=None, min_length=1, max_length=2000)
    signer_membership_id: UUID
    provider: str = Field(min_length=2, max_length=64, pattern=r"^[A-Z][A-Z0-9_.-]+$")

    @model_serializer(mode="wrap")
    def preserve_legacy_intent_hash(self, handler: SerializerFunctionWrapHandler) -> dict:
        data = handler(self)
        for field in ("expected_manifest_sha256", "rationale"):
            if getattr(self, field) is None:
                data.pop(field, None)
        return data


class RecordSubmissionSignatureCommand(ApplicationCommand):
    """Record a provider callback as a hash-only signature proof."""

    command_type = "RecordSubmissionSignature"

    signature_id: UUID
    submission_package_id: UUID
    provider: str = Field(min_length=2, max_length=64, pattern=r"^[A-Z][A-Z0-9_.-]+$")
    provider_reference_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    signature_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    outcome: str = Field(pattern=r"^(SIGNED|REJECTED)$")
