"""SQLAlchemy adapter for C5 evidence-object persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.pricing.application.case_contract_change_evidence_upload import (
    EvidenceObjectSnapshot,
)
from app.modules.pricing.infrastructure.models.case_contract_change import (
    CaseContractChangeEvidenceObjectRecord,
)


class SqlAlchemyCaseContractChangeEvidenceRepository:
    def __init__(self, *, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_target(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        evidence_object_id: UUID,
    ) -> EvidenceObjectSnapshot | None:
        with self._session_factory() as session:
            record = session.scalar(
                sa.select(CaseContractChangeEvidenceObjectRecord).where(
                    CaseContractChangeEvidenceObjectRecord.tenant_id == tenant_id,
                    CaseContractChangeEvidenceObjectRecord.case_id == case_id,
                    CaseContractChangeEvidenceObjectRecord.event_id == event_id,
                    CaseContractChangeEvidenceObjectRecord.action_id == action_id,
                    CaseContractChangeEvidenceObjectRecord.id == evidence_object_id,
                )
            )
            return _snapshot(record) if record is not None else None

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
    ) -> tuple[EvidenceObjectSnapshot, ...]:
        with self._session_factory() as session:
            records = session.scalars(
                sa.select(CaseContractChangeEvidenceObjectRecord).where(
                    CaseContractChangeEvidenceObjectRecord.tenant_id == tenant_id,
                    CaseContractChangeEvidenceObjectRecord.case_id == case_id,
                    CaseContractChangeEvidenceObjectRecord.event_id == event_id,
                    CaseContractChangeEvidenceObjectRecord.action_id == action_id,
                    CaseContractChangeEvidenceObjectRecord.c4_relation_id == c4_relation_id,
                    CaseContractChangeEvidenceObjectRecord.id.in_(evidence_object_ids),
                    CaseContractChangeEvidenceObjectRecord.evidence_kind == evidence_kind,
                    CaseContractChangeEvidenceObjectRecord.state == "CLEAN",
                )
            ).all()
        return tuple(_snapshot(record) for record in records)

    def claim(self, *, evidence_object_id: UUID) -> bool:
        with self._session_factory.begin() as session:
            record = session.scalar(
                sa.select(CaseContractChangeEvidenceObjectRecord)
                .where(CaseContractChangeEvidenceObjectRecord.id == evidence_object_id)
                .with_for_update()
            )
            if record is None or record.state != "AWAITING_UPLOAD":
                return False
            record.state = "UPLOADING"
            return True

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
    ) -> bool:
        with self._session_factory.begin() as session:
            record = session.scalar(
                sa.select(CaseContractChangeEvidenceObjectRecord)
                .where(CaseContractChangeEvidenceObjectRecord.id == evidence_object_id)
                .with_for_update()
            )
            if record is None or record.state != "UPLOADING":
                return False
            record.actual_byte_size = actual_byte_size
            record.sha256 = digest
            record.media_type = media_type
            record.scan_verdict = scan_verdict
            record.scanner_name = scanner_name
            record.scanner_signature_version = scanner_signature_version
            record.scanned_at = scanned_at
            record.state = "CLEAN"
            return True

    def reject(self, *, evidence_object_id: UUID) -> None:
        with self._session_factory.begin() as session:
            record = session.scalar(
                sa.select(CaseContractChangeEvidenceObjectRecord)
                .where(CaseContractChangeEvidenceObjectRecord.id == evidence_object_id)
                .with_for_update()
            )
            if record is not None and record.state in {"AWAITING_UPLOAD", "UPLOADING"}:
                record.state = "REJECTED"


def _snapshot(record: CaseContractChangeEvidenceObjectRecord) -> EvidenceObjectSnapshot:
    return EvidenceObjectSnapshot(
        evidence_object_id=record.id,
        idempotency_key=record.idempotency_key,
        storage_key=record.storage_key,
        expected_byte_size=record.expected_byte_size,
        actual_byte_size=record.actual_byte_size,
        sha256=record.sha256,
        media_type=record.media_type,
        state=record.state,
        expires_at=record.expires_at,
        version=record.version,
    )
