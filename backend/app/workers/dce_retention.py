"""Deterministic DCE/C5 worker for private quarantine retention and cleanup."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid5

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.dce.application.commands import ExpireDceStagedObjectCommand
from app.modules.dce.application.handlers import ExpireDceStagedObjectHandler
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.modules.pricing.application.case_contract_change import case_contract_change_handlers
from app.modules.pricing.application.case_contract_change_commands import (
    CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC,
    ExpireCaseContractChangeEvidenceUploadCommand,
)
from app.modules.pricing.infrastructure.models.case_contract_change import (
    CaseContractChangeEvidenceObjectRecord,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.events.retry_policy import (
    DEFAULT_MAX_OUTBOX_ATTEMPTS,
    MAX_OUTBOX_ATTEMPTS_LIMIT,
    decide_retry,
)
from app.platform.persistence.models import OutboxMessageRecord

RETENTION_TOPIC = "dce_staging_retention"
SYSTEM_RETENTION_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000012")
_DELETABLE_STATES = frozenset({"REJECTED", "EXPIRED"})


@dataclass(frozen=True, slots=True)
class RetentionRunResult:
    """Counters intentionally free of storage keys, content, hashes and scanner facts."""

    expired: int = 0
    published: int = 0
    retried: int = 0
    failed: int = 0
    skipped: int = 0

    def merged(self, other: RetentionRunResult) -> RetentionRunResult:
        return RetentionRunResult(
            expired=self.expired + other.expired,
            published=self.published + other.published,
            retried=self.retried + other.retried,
            failed=self.failed + other.failed,
            skipped=self.skipped + other.skipped,
        )


class DceRetentionWorker:
    """Expires abandoned DCE/C5 uploads then consumes cleanup outbox messages safely."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        dispatcher: CommandDispatcher,
        storage: LocalQuarantineStorageAdapter,
        batch_size: int = 50,
        lease_seconds: int = 120,
        max_attempts: int = DEFAULT_MAX_OUTBOX_ATTEMPTS,
    ) -> None:
        self._session_factory = session_factory
        self._dispatcher = dispatcher
        self._storage = storage
        self._batch_size = batch_size
        self._lease_seconds = lease_seconds
        if not 1 <= max_attempts <= MAX_OUTBOX_ATTEMPTS_LIMIT:
            raise ValueError("max_attempts must be between 1 and 100")
        self._max_attempts = max_attempts

    async def run_once(self, *, now: datetime | None = None) -> RetentionRunResult:
        """Expire DCE/C5 uploads and consume their private-storage cleanup outboxes."""

        effective_now = now or datetime.now(tz=UTC)
        expired = self._expire_due_objects(now=effective_now)
        expired += self._expire_due_c5_uploads(now=effective_now)
        claimed_message_ids = self._claim_due_messages(now=effective_now)
        result = RetentionRunResult(expired=expired)
        for message_id in claimed_message_ids:
            processed = await self._process_message(message_id=message_id, now=effective_now)
            result = result.merged(processed)
        return result

    def _expire_due_objects(self, *, now: datetime) -> int:
        with self._session_factory.begin() as session:
            object_ids = list(
                session.scalars(
                    sa.select(DceStagedObjectRecord.id)
                    .where(
                        DceStagedObjectRecord.state.not_in(("CONSUMED", "EXPIRED")),
                        DceStagedObjectRecord.expires_at <= now,
                    )
                    .order_by(DceStagedObjectRecord.expires_at, DceStagedObjectRecord.id)
                    .limit(self._batch_size)
                    .with_for_update(skip_locked=True)
                )
            )
            records = [
                (record.id, record.tenant_id)
                for record in session.scalars(
                    sa.select(DceStagedObjectRecord).where(DceStagedObjectRecord.id.in_(object_ids))
                )
            ]
        expired = 0
        for storage_object_id, tenant_id in records:
            try:
                self._dispatcher.dispatch(
                    command=ExpireDceStagedObjectCommand(
                        command_id=_command_id(storage_object_id, "expire"),
                        idempotency_key=_command_id(storage_object_id, "expire-receipt"),
                        correlation_id=storage_object_id,
                        storage_object_id=storage_object_id,
                    ),
                    context=_system_context(tenant_id=tenant_id, now=now),
                )
            except CommandExecutionError:
                continue
            expired += 1
        return expired

    def _expire_due_c5_uploads(self, *, now: datetime) -> int:
        with self._session_factory.begin() as session:
            candidates = list(
                session.execute(
                    sa.select(
                        CaseContractChangeEvidenceObjectRecord.id,
                        CaseContractChangeEvidenceObjectRecord.tenant_id,
                        CaseContractChangeEvidenceObjectRecord.case_id,
                        CaseContractChangeEvidenceObjectRecord.event_id,
                        CaseContractChangeEvidenceObjectRecord.action_id,
                    )
                    .where(
                        CaseContractChangeEvidenceObjectRecord.state.in_(
                            ("AWAITING_UPLOAD", "UPLOADING")
                        ),
                        CaseContractChangeEvidenceObjectRecord.expires_at <= now,
                    )
                    .order_by(
                        CaseContractChangeEvidenceObjectRecord.expires_at,
                        CaseContractChangeEvidenceObjectRecord.id,
                    )
                    .limit(self._batch_size)
                    .with_for_update(skip_locked=True)
                ).all()
            )

        expired = 0
        for evidence_id, tenant_id, case_id, event_id, action_id in candidates:
            try:
                result = self._dispatcher.dispatch(
                    command=ExpireCaseContractChangeEvidenceUploadCommand(
                        command_id=_command_id(evidence_id, "c5-expire"),
                        idempotency_key=_command_id(evidence_id, "c5-expire-receipt"),
                        correlation_id=evidence_id,
                        case_id=case_id,
                        event_id=event_id,
                        action_id=action_id,
                        evidence_object_id=evidence_id,
                    ),
                    context=_system_context(tenant_id=tenant_id, now=now),
                )
            except CommandExecutionError:
                continue
            if not result.replayed and result.result_code == "C5_EVIDENCE_UPLOAD_EXPIRED":
                expired += 1
        return expired

    def _claim_due_messages(self, *, now: datetime) -> list[UUID]:
        lease_until = now + timedelta(seconds=self._lease_seconds)
        with self._session_factory.begin() as session:
            messages = list(
                session.scalars(
                    sa.select(OutboxMessageRecord)
                    .where(
                        OutboxMessageRecord.topic.in_(
                            (RETENTION_TOPIC, CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC)
                        ),
                        OutboxMessageRecord.status.in_(("PENDING", "RETRY")),
                        sa.or_(
                            OutboxMessageRecord.next_attempt_at.is_(None),
                            OutboxMessageRecord.next_attempt_at <= now,
                        ),
                    )
                    .order_by(OutboxMessageRecord.created_at, OutboxMessageRecord.id)
                    .limit(self._batch_size)
                    .with_for_update(skip_locked=True)
                )
            )
            for message in messages:
                message.status = "RETRY"
                message.next_attempt_at = lease_until
            return [message.id for message in messages]

    async def _process_message(self, *, message_id: UUID, now: datetime) -> RetentionRunResult:
        with self._session_factory() as session:
            message = session.get(OutboxMessageRecord, message_id)
            if message is None or message.topic not in {
                RETENTION_TOPIC,
                CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC,
            }:
                return RetentionRunResult(skipped=1)
            payload_data = message.payload_json.get("data", {})
            tenant_id = _uuid_payload(payload_data, "tenant_id")
            c5_evidence_id = (
                _uuid_payload(payload_data, "evidence_object_id")
                if message.topic == CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC
                else None
            )
            storage_object_id = (
                _uuid_payload(payload_data, "storage_object_id")
                if message.topic == RETENTION_TOPIC
                else None
            )
            if tenant_id is None or (c5_evidence_id is None and storage_object_id is None):
                return self._retry_message(
                    message_id=message_id,
                    now=now,
                    error_code="INVALID_RETENTION_PAYLOAD",
                )
            with self._session_factory() as object_session:
                if c5_evidence_id is not None:
                    object_record = object_session.scalar(
                        sa.select(CaseContractChangeEvidenceObjectRecord).where(
                            CaseContractChangeEvidenceObjectRecord.id == c5_evidence_id,
                            CaseContractChangeEvidenceObjectRecord.tenant_id == tenant_id,
                        )
                    )
                    if object_record is None:
                        return self._publish_message(message_id=message_id, now=now)
                    if object_record.state != "REJECTED":
                        return self._publish_message(message_id=message_id, now=now, skipped=True)
                    storage_key = object_record.storage_key
                else:
                    staged_object = object_session.scalar(
                        sa.select(DceStagedObjectRecord).where(
                            DceStagedObjectRecord.id == storage_object_id,
                            DceStagedObjectRecord.tenant_id == tenant_id,
                        )
                    )
                    if staged_object is None:
                        return self._publish_message(message_id=message_id, now=now)
                    state = staged_object.state
                    storage_key = staged_object.storage_key

        if c5_evidence_id is None and state not in _DELETABLE_STATES:
            return self._publish_message(message_id=message_id, now=now, skipped=True)
        try:
            await self._storage.delete(storage_key=storage_key)
            if c5_evidence_id is not None:
                await self._storage.delete_partials(storage_key=storage_key)
        except Exception:
            return self._retry_message(
                message_id=message_id,
                now=now,
                error_code="PRIVATE_DELETE_FAILED",
            )
        return self._publish_message(message_id=message_id, now=now)

    def _publish_message(
        self,
        *,
        message_id: UUID,
        now: datetime,
        skipped: bool = False,
    ) -> RetentionRunResult:
        with self._session_factory.begin() as session:
            message = session.get(OutboxMessageRecord, message_id, with_for_update=True)
            if message is None or message.status == "PUBLISHED":
                return RetentionRunResult(skipped=1)
            message.status = "PUBLISHED"
            message.published_at = now
            message.next_attempt_at = None
            message.last_error_code = None
        return RetentionRunResult(skipped=1) if skipped else RetentionRunResult(published=1)

    def _retry_message(
        self,
        *,
        message_id: UUID,
        now: datetime,
        error_code: str,
    ) -> RetentionRunResult:
        with self._session_factory.begin() as session:
            message = session.get(OutboxMessageRecord, message_id, with_for_update=True)
            if message is None or message.status == "PUBLISHED":
                return RetentionRunResult(skipped=1)
            decision = decide_retry(
                attempt_count=message.attempt_count,
                now=now,
                max_attempts=self._max_attempts,
            )
            message.status = decision.status
            message.attempt_count = decision.attempt_count
            message.next_attempt_at = decision.next_attempt_at
            message.last_error_code = error_code
        return RetentionRunResult(
            retried=1 if decision.status == "RETRY" else 0,
            failed=1 if decision.status == "FAILED" else 0,
        )


def _retry_delay(attempt_count: int) -> timedelta:
    return timedelta(seconds=min(30 * (2 ** max(attempt_count - 1, 0)), 3600))


def _system_context(*, tenant_id: UUID, now: datetime) -> CommandContext:
    return CommandContext(
        tenant_id=tenant_id,
        actor_id=SYSTEM_RETENTION_ACTOR_ID,
        actor_kind="SYSTEM",
        received_at=now,
    )


def _command_id(storage_object_id: UUID, action: str) -> UUID:
    return uuid5(storage_object_id, f"dce-retention:{action}")


def _uuid_payload(payload: object, key: str) -> UUID | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get(key)
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def build_default_worker() -> DceRetentionWorker:
    """Build the private-storage retention worker; no HTTP listener or exposed port."""

    database_url = os.environ["SMART_AO_DATABASE_URL"]
    engine = sa.create_engine(database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "ExpireDceStagedObject": ExpireDceStagedObjectHandler(),
            **case_contract_change_handlers(),
        },
    )
    storage = LocalQuarantineStorageAdapter(root=Path(os.environ["SMART_AO_DCE_QUARANTINE_ROOT"]))
    return DceRetentionWorker(
        session_factory=session_factory,
        dispatcher=dispatcher,
        storage=storage,
        batch_size=int(os.getenv("SMART_AO_RETENTION_BATCH_SIZE", "50")),
        lease_seconds=int(os.getenv("SMART_AO_RETENTION_LEASE_SECONDS", "120")),
        max_attempts=int(
            os.getenv("SMART_AO_OUTBOX_MAX_ATTEMPTS", str(DEFAULT_MAX_OUTBOX_ATTEMPTS))
        ),
    )


def main() -> None:
    worker = build_default_worker()
    poll_seconds = float(os.getenv("SMART_AO_RETENTION_POLL_SECONDS", "30"))
    while True:
        import asyncio

        asyncio.run(worker.run_once())
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
