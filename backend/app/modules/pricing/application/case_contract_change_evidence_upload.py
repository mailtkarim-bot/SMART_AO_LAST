"""C5 private upload orchestration and source-byte verification."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterable
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Protocol
from uuid import UUID

from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification
from app.platform.storage.quarantine import (
    ContentInspectionPort,
    MalwareScanPort,
    QuarantineStoragePort,
)

logger = logging.getLogger(__name__)

MAX_EVIDENCE_BYTES = 150_000_000
EVIDENCE_MEDIA_TYPES = frozenset(
    {
        "application/pdf",
        "application/msword",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/zip",
        "image/jpeg",
        "image/png",
        "image/tiff",
    }
)


class ReadableQuarantineStorage(QuarantineStoragePort, Protocol):
    async def read_bytes(self, *, storage_key: str, max_bytes: int) -> bytes: ...


@dataclass(frozen=True, slots=True)
class EvidenceUploadResult:
    evidence_object_id: UUID
    version: int
    state: str
    sha256: str
    actual_byte_size: int
    media_type: str


@dataclass(frozen=True, slots=True)
class EvidenceUploadIntent:
    evidence_object_id: UUID
    state: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class EvidenceObjectSnapshot:
    evidence_object_id: UUID
    idempotency_key: UUID
    storage_key: str
    expected_byte_size: int
    actual_byte_size: int | None
    sha256: str | None
    media_type: str | None
    state: str
    expires_at: datetime
    version: int


class CaseContractChangeEvidenceRepositoryPort(Protocol):
    def get_target(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        evidence_object_id: UUID,
    ) -> EvidenceObjectSnapshot | None: ...

    def list_clean_sources(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        c4_relation_id: UUID,
        evidence_object_ids: tuple[UUID, ...],
        evidence_kind: str,
    ) -> tuple[EvidenceObjectSnapshot, ...]: ...

    def claim(self, *, evidence_object_id: UUID) -> bool: ...

    def admit_clean(
        self,
        *,
        evidence_object_id: UUID,
        actual_byte_size: int,
        digest: str,
        media_type: str,
        scan_verdict: str,
        scanner_name: str,
        scanner_signature_version: str,
        scanned_at: datetime,
    ) -> bool: ...

    def reject(self, *, evidence_object_id: UUID) -> None: ...


class EvidenceUploadRejectedError(RuntimeError):
    def __init__(self, *, status_code: int = 422) -> None:
        super().__init__("C5_EVIDENCE_UPLOAD_REJECTED")
        self.status_code = status_code


class EvidenceUploadAlreadyClaimedError(RuntimeError):
    pass


class CaseContractChangeEvidenceUploadService:
    """Store clean C5 evidence privately; source keys never leave this adapter."""

    def __init__(
        self,
        *,
        repository: CaseContractChangeEvidenceRepositoryPort,
        policy: AuthorizationPolicyPort,
        storage: ReadableQuarantineStorage,
        inspector: ContentInspectionPort,
        scanner: MalwareScanPort,
        allowed_media_types: frozenset[str] = EVIDENCE_MEDIA_TYPES,
        max_bytes: int = MAX_EVIDENCE_BYTES,
    ) -> None:
        self._repository = repository
        self._policy = policy
        self._storage = storage
        self._inspector = inspector
        self._scanner = scanner
        self._allowed_media_types = allowed_media_types
        self._max_bytes = min(max_bytes, MAX_EVIDENCE_BYTES)

    async def upload(
        self,
        *,
        actor: ActorContext,
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        evidence_object_id: UUID,
        idempotency_key: UUID,
        stream: AsyncIterable[bytes],
        content_length: int | None,
        now: datetime,
    ) -> EvidenceUploadResult:
        self._authorize(actor=actor, case_id=case_id, now=now)
        target = self._repository.get_target(
            tenant_id=actor.tenant_id,
            case_id=case_id,
            event_id=event_id,
            action_id=action_id,
            evidence_object_id=evidence_object_id,
        )
        if target is None or target.idempotency_key != idempotency_key:
            raise PermissionError("C5_EVIDENCE_UPLOAD_NOT_FOUND_OR_FORBIDDEN")
        if target.state == "CLEAN":
            await self._verify_retry_stream(
                stream=stream,
                expected_byte_size=target.actual_byte_size,
                expected_sha256=target.sha256,
            )
            return self._clean_result(target)
        if target.state != "AWAITING_UPLOAD":
            raise EvidenceUploadAlreadyClaimedError()
        if now >= target.expires_at:
            self._repository.reject(evidence_object_id=evidence_object_id)
            raise EvidenceUploadRejectedError()
        if content_length is not None and (
            content_length <= 0
            or content_length > self._max_bytes
            or content_length != target.expected_byte_size
        ):
            self._repository.reject(evidence_object_id=evidence_object_id)
            raise EvidenceUploadRejectedError(
                status_code=413 if content_length > self._max_bytes else 422
            )

        if not self._repository.claim(evidence_object_id=evidence_object_id):
            raise EvidenceUploadAlreadyClaimedError()
        try:
            write_result = await self._storage.write(
                storage_key=target.storage_key,
                stream=stream,
                max_bytes=self._max_bytes,
            )
            if write_result.byte_size != target.expected_byte_size or write_result.byte_size <= 0:
                raise EvidenceUploadRejectedError()
            media_type = (
                await self._inspector.detect_media_type(storage_key=target.storage_key)
            ).casefold()
            if media_type not in self._allowed_media_types:
                raise EvidenceUploadRejectedError()
            scan_result = await self._scanner.scan(storage_key=target.storage_key)
            if scan_result.verdict != "CLEAN" or not _valid_sha256(write_result.sha256):
                raise EvidenceUploadRejectedError()
            admitted = self._repository.admit_clean(
                evidence_object_id=evidence_object_id,
                actual_byte_size=write_result.byte_size,
                digest=write_result.sha256,
                media_type=media_type,
                scan_verdict=scan_result.verdict,
                scanner_name=scan_result.scanner_name,
                scanner_signature_version=scan_result.scanner_signature_version,
                scanned_at=scan_result.scanned_at,
            )
            if not admitted:
                raise EvidenceUploadAlreadyClaimedError()
        except asyncio.CancelledError:
            try:
                await asyncio.shield(self._delete_quarantine(storage_key=target.storage_key))
            finally:
                self._repository.reject(evidence_object_id=evidence_object_id)
            raise
        except Exception as error:
            await self._delete_quarantine(storage_key=target.storage_key)
            self._repository.reject(evidence_object_id=evidence_object_id)
            if isinstance(error, EvidenceUploadRejectedError):
                raise
            logger.warning(
                "case_contract_change_evidence_upload_failed",
                extra={"error_type": type(error).__name__},
            )
            raise EvidenceUploadRejectedError() from error

        return EvidenceUploadResult(
            evidence_object_id=evidence_object_id,
            version=1,
            state="CLEAN",
            sha256=write_result.sha256,
            actual_byte_size=write_result.byte_size,
            media_type=media_type,
        )

    def get_intent(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        evidence_object_id: UUID,
    ) -> EvidenceUploadIntent | None:
        record = self._repository.get_target(
            tenant_id=tenant_id,
            case_id=case_id,
            event_id=event_id,
            action_id=action_id,
            evidence_object_id=evidence_object_id,
        )
        if record is None:
            return None
        return EvidenceUploadIntent(
            evidence_object_id=record.evidence_object_id,
            state=record.state,
            expires_at=record.expires_at,
        )

    async def verify_sources(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        c4_relation_id: UUID,
        evidence_object_ids: tuple[UUID, ...],
        evidence_kind: str,
    ) -> tuple[UUID, ...]:
        if not evidence_object_ids:
            return ()
        rows = self._repository.list_clean_sources(
            tenant_id=tenant_id,
            case_id=case_id,
            event_id=event_id,
            action_id=action_id,
            c4_relation_id=c4_relation_id,
            evidence_object_ids=evidence_object_ids,
            evidence_kind=evidence_kind,
        )
        by_id = {row.evidence_object_id: row for row in rows}
        if len(by_id) != len(evidence_object_ids):
            raise PermissionError("C5_EVIDENCE_OBJECT_NOT_FOUND_OR_FORBIDDEN")
        for evidence_id in evidence_object_ids:
            source = by_id[evidence_id]
            try:
                content = await self._storage.read_bytes(
                    storage_key=source.storage_key,
                    max_bytes=self._max_bytes,
                )
            except Exception as error:
                raise EvidenceUploadRejectedError() from error
            if (
                len(content) != source.actual_byte_size
                or sha256(content).hexdigest() != source.sha256
            ):
                raise EvidenceUploadRejectedError()
        return evidence_object_ids

    def _authorize(self, *, actor: ActorContext, case_id: UUID, now: datetime) -> None:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PATRON_ACTION_WRITE,
                resource=AuthorizationResource(
                    resource_type="CASE_CONTRACT_CHANGE",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.FINANCIAL_PRIVATE,
                    case_id=case_id,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)

    @staticmethod
    def _clean_result(record: EvidenceObjectSnapshot) -> EvidenceUploadResult:
        if record.actual_byte_size is None or record.sha256 is None or record.media_type is None:
            raise EvidenceUploadRejectedError()
        return EvidenceUploadResult(
            evidence_object_id=record.evidence_object_id,
            version=record.version,
            state=record.state,
            sha256=record.sha256,
            actual_byte_size=record.actual_byte_size,
            media_type=record.media_type,
        )

    async def _delete_quarantine(self, *, storage_key: str) -> None:
        try:
            await self._storage.delete(storage_key=storage_key)
        except Exception as error:
            logger.warning(
                "case_contract_change_evidence_delete_failed",
                extra={"error_type": type(error).__name__},
            )

    async def _verify_retry_stream(
        self,
        *,
        stream: AsyncIterable[bytes],
        expected_byte_size: int | None,
        expected_sha256: str | None,
    ) -> None:
        digest = sha256()
        byte_size = 0
        async for chunk in stream:
            if not isinstance(chunk, bytes):
                raise EvidenceUploadAlreadyClaimedError()
            byte_size += len(chunk)
            if byte_size > self._max_bytes:
                raise EvidenceUploadAlreadyClaimedError()
            digest.update(chunk)
        if byte_size != expected_byte_size or digest.hexdigest() != expected_sha256:
            raise EvidenceUploadAlreadyClaimedError()


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)
