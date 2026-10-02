from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecordCaseHandoverRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    snapshot_id: UUID
    outcome_id: UUID
    submission_package_id: UUID


class CaseHandoverOfferOptionResponse(BaseModel):
    outcome_id: UUID
    lot_reference: str
    submission_package_id: UUID
    package_version: int
    manifest_sha256: str
    dce_version_id: UUID
    technical_document_id: UUID
    technical_document_version: int
    technical_document_kind: str
    technical_document_sha256: str


class CaseHandoverOfferOptionsResponse(BaseModel):
    case_id: UUID
    items: list[CaseHandoverOfferOptionResponse]


class CaseHandoverSnapshotResponse(BaseModel):
    snapshot_id: UUID
    outcome_id: UUID
    lot_reference: str
    submission_package_id: UUID
    package_version: int
    manifest_sha256: str
    revision: int
    created_at: str
    snapshot: dict[str, object]


class CaseHandoverSnapshotsResponse(BaseModel):
    case_id: UUID
    items: list[CaseHandoverSnapshotResponse] = Field(default_factory=list)


class RecordCaseHandoverResponse(BaseModel):
    status: str
    result_code: str
    replayed: bool
