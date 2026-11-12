from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.modules.pricing.application.case_contract_change_evidence_upload import (
    CaseContractChangeEvidenceUploadService,
    EvidenceObjectSnapshot,
)
from app.platform.security.authorization import AuthorizationDecision
from app.platform.security.context import ActorContext, ActorKind

CONTENT = b"%PDF-1.7\nC5 cancellation proof\n"
NOW = datetime(2026, 10, 4, tzinfo=UTC)


class _Repository:
    def __init__(self, *, target: EvidenceObjectSnapshot) -> None:
        self.target = target
        self.state = target.state

    def get_target(self, **_kwargs) -> EvidenceObjectSnapshot:
        return replace(self.target, state=self.state)

    def claim(self, *, evidence_object_id) -> bool:
        if self.state != "AWAITING_UPLOAD":
            return False
        self.state = "UPLOADING"
        return True

    def list_clean_sources(self, **_kwargs) -> tuple[EvidenceObjectSnapshot, ...]:
        raise AssertionError("cancelled upload must not list CLEAN sources")

    def admit_clean(self, **_kwargs) -> bool:
        raise AssertionError("cancelled upload must not be admitted CLEAN")

    def reject(self, *, evidence_object_id) -> None:
        if self.state in {"AWAITING_UPLOAD", "UPLOADING"}:
            self.state = "REJECTED"


class _Inspector:
    async def detect_media_type(self, *, storage_key: str) -> str:
        return "application/pdf"


class _CancelledScanner:
    async def scan(self, *, storage_key: str):
        raise asyncio.CancelledError()


class _AllowPolicy:
    def authorize(self, **_kwargs) -> AuthorizationDecision:
        return AuthorizationDecision.allow()


async def _stream():
    yield CONTENT


def test_cancelled_c5_scan_rejects_intent_and_removes_quarantined_object(
    tmp_path: Path,
) -> None:
    evidence_object_id = uuid4()
    idempotency_key = uuid4()
    storage_key = f"c5/{evidence_object_id}"
    repository = _Repository(
        target=EvidenceObjectSnapshot(
            evidence_object_id=evidence_object_id,
            idempotency_key=idempotency_key,
            storage_key=storage_key,
            expected_byte_size=len(CONTENT),
            actual_byte_size=None,
            sha256=None,
            media_type=None,
            state="AWAITING_UPLOAD",
            expires_at=NOW + timedelta(minutes=30),
            version=1,
        )
    )
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    service = CaseContractChangeEvidenceUploadService(
        repository=repository,
        policy=_AllowPolicy(),
        storage=storage,
        inspector=_Inspector(),
        scanner=_CancelledScanner(),
    )
    actor = SimpleNamespace(
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_id=uuid4(),
        tenant_id=uuid4(),
    )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(
            service.upload(
                actor=cast(ActorContext, actor),
                case_id=uuid4(),
                event_id=uuid4(),
                action_id=uuid4(),
                evidence_object_id=evidence_object_id,
                idempotency_key=idempotency_key,
                stream=_stream(),
                content_length=len(CONTENT),
                now=NOW,
            )
        )

    assert repository.state == "REJECTED"
    assert not (tmp_path / storage_key).exists()
