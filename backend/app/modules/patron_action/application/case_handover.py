"""Owner-issued, finance-redacted P7 handover snapshot and assigned Conducteur read."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime
from uuid import UUID

from app.modules.patron_action.application.handover_commands import (
    RecordCaseHandoverSnapshotCommand,
)
from app.modules.patron_action.application.handover_queries import (
    CaseHandoverReader,
    CaseHandoverSnapshotProjection,
    technical_document_source,
)
from app.modules.patron_action.application.operational_handover import public_handover_snapshot
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandExecutionError,
    CommandHandler,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    DataClassification,
    OperationalProfile,
)
from app.platform.storage.ports import GeneratedDocumentStorage


class CaseHandoverService:
    def __init__(
        self,
        *,
        dispatcher: CommandDispatcher,
        reader: CaseHandoverReader,
        policy: AuthorizationPolicyPort,
        storage: GeneratedDocumentStorage | None = None,
    ) -> None:
        self._dispatcher = dispatcher
        self._reader = reader
        self._policy = policy
        self._storage = storage

    def record(
        self, *, actor: ActorContext, command: RecordCaseHandoverSnapshotCommand, now: datetime
    ):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(
            actor=actor, case_id=command.case_id, action=Capability.PATRON_ACTION_WRITE, now=now
        )
        if command.operational_review is not None:
            self._authorize(
                actor=actor,
                case_id=command.case_id,
                action=Capability.PRICING_READ,
                now=now,
                classification=DataClassification.FINANCIAL_PRIVATE,
                mfa_required=True,
            )
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                received_at=now,
                identity_id=actor.identity_id,
                membership_id=actor.membership_id,
                session_id=actor.session_id,
                case_id=command.case_id,
                correlation_id=command.correlation_id,
            ),
        )

    def read(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> tuple[CaseHandoverSnapshotProjection, ...]:
        if actor.actor_kind is ActorKind.COLLABORATEUR:
            if actor.operational_profile is not OperationalProfile.RESPONSABLE:
                raise PermissionError("RESPONSABLE_PROFILE_REQUIRED")
            action = Capability.CASE_DCE_READ
        elif actor.actor_kind is ActorKind.PATRON_ADMIN:
            action = Capability.PATRON_ACTION_READ
        else:
            raise PermissionError("FORBIDDEN")
        self._authorize(actor=actor, case_id=case_id, action=action, now=now)
        return tuple(
            replace(item, snapshot_json=public_handover_snapshot(item.snapshot_json))
            for item in self._reader.list_for_case(tenant_id=actor.tenant_id, case_id=case_id)
        )

    def download_offer_document(
        self, *, actor: ActorContext, case_id: UUID, snapshot_id: UUID, now: datetime
    ) -> tuple[bytes, str, str]:
        if self._storage is None:
            raise RuntimeError("HANDOVER_DOCUMENT_STORAGE_UNAVAILABLE")
        if actor.actor_kind is ActorKind.COLLABORATEUR:
            if actor.operational_profile is not OperationalProfile.RESPONSABLE:
                raise PermissionError("RESPONSABLE_PROFILE_REQUIRED")
            action = Capability.CASE_DCE_READ
        elif actor.actor_kind is ActorKind.PATRON_ADMIN:
            action = Capability.PATRON_ACTION_READ
        else:
            raise PermissionError("FORBIDDEN")
        self._authorize(actor=actor, case_id=case_id, action=action, now=now)
        candidate = self._reader.offer_document_candidate(
            tenant_id=actor.tenant_id, case_id=case_id, snapshot_id=snapshot_id
        )
        if candidate is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        manifest_bytes = json.dumps(
            candidate.manifest_json,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if (
            hashlib.sha256(manifest_bytes).hexdigest() != candidate.snapshot_manifest_sha256
            or candidate.manifest_sha256 != candidate.snapshot_manifest_sha256
        ):
            raise CommandExecutionError("HANDOVER_OFFER_MANIFEST_INTEGRITY_FAILED")
        if (
            not candidate.authorization_present
            or candidate.technical_source_sha256 is None
            or candidate.technical_document_sha256 is None
            or candidate.technical_document_storage_key is None
            or candidate.technical_source_sha256 != candidate.technical_document_sha256
            or candidate.snapshot_offer.get("technical_document_sha256")
            != candidate.technical_document_sha256
            or candidate.snapshot_offer.get("technical_document_kind") != "TECHNICAL_RESPONSE"
        ):
            raise CommandExecutionError("HANDOVER_OFFER_DOCUMENT_NOT_VERIFIED")
        content = self._storage.read(storage_key=candidate.technical_document_storage_key)
        if hashlib.sha256(content).hexdigest() != candidate.technical_document_sha256:
            raise CommandExecutionError("HANDOVER_OFFER_DOCUMENT_HASH_MISMATCH")
        source = technical_document_source(
            candidate.manifest_json,
            document_id=UUID(str(candidate.snapshot_offer["technical_document_id"])),
            version=int(str(candidate.snapshot_offer["technical_document_version"])),
        )
        if (
            source is None
            or candidate.technical_document_format not in {"MARKDOWN", "DOCX"}
            or source.get("content_format", "MARKDOWN") != candidate.technical_document_format
        ):
            raise CommandExecutionError("HANDOVER_OFFER_DOCUMENT_NOT_VERIFIED")
        return content, candidate.technical_document_sha256, candidate.technical_document_format

    def list_offer_options(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> tuple[dict[str, object], ...]:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(actor=actor, case_id=case_id, action=Capability.PATRON_ACTION_READ, now=now)
        return self._reader.list_offer_options(tenant_id=actor.tenant_id, case_id=case_id)

    def contract_options(self, *, actor, case_id, now):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(
            actor=actor,
            case_id=case_id,
            action=Capability.PRICING_READ,
            now=now,
            classification=DataClassification.FINANCIAL_PRIVATE,
        )
        return self._reader.list_contract_options(tenant_id=actor.tenant_id, case_id=case_id)

    def condition_options(self, *, actor, case_id, now):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(
            actor=actor,
            case_id=case_id,
            action=Capability.PRICING_READ,
            now=now,
            classification=DataClassification.FINANCIAL_PRIVATE,
        )
        return self._reader.condition_options(tenant_id=actor.tenant_id, case_id=case_id)

    def read_exact(self, *, actor, case_id, snapshot_id, now):
        if actor.actor_kind is ActorKind.COLLABORATEUR:
            if actor.operational_profile is not OperationalProfile.RESPONSABLE:
                raise PermissionError("RESPONSABLE_PROFILE_REQUIRED")
            action = Capability.CASE_DCE_READ
        elif actor.actor_kind is ActorKind.PATRON_ADMIN:
            action = Capability.PATRON_ACTION_READ
        else:
            raise PermissionError("FORBIDDEN")
        self._authorize(actor=actor, case_id=case_id, action=action, now=now)
        row = self._reader.snapshot_for_case(
            tenant_id=actor.tenant_id, case_id=case_id, snapshot_id=snapshot_id
        )
        if row is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        return row

    def history(self, *, actor, case_id, before_snapshot_id, now):
        if actor.actor_kind is ActorKind.COLLABORATEUR:
            if actor.operational_profile is not OperationalProfile.RESPONSABLE:
                raise PermissionError("RESPONSABLE_PROFILE_REQUIRED")
            action = Capability.CASE_DCE_READ
        elif actor.actor_kind is ActorKind.PATRON_ADMIN:
            action = Capability.PATRON_ACTION_READ
        else:
            raise PermissionError("FORBIDDEN")
        self._authorize(actor=actor, case_id=case_id, action=action, now=now)
        return self._reader.history_for_case(
            tenant_id=actor.tenant_id, case_id=case_id, before_snapshot_id=before_snapshot_id
        )

    def acknowledge(self, *, actor, command, now):
        if (
            actor.actor_kind is not ActorKind.COLLABORATEUR
            or actor.operational_profile is not OperationalProfile.RESPONSABLE
            or actor.membership_id is None
        ):
            raise PermissionError("RESPONSABLE_PROFILE_REQUIRED")
        self._authorize(
            actor=actor,
            case_id=command.case_id,
            action=Capability.CASE_HANDOVER_RECEIPT_WRITE,
            now=now,
        )
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                received_at=now,
                identity_id=actor.identity_id,
                membership_id=actor.membership_id,
                session_id=actor.session_id,
                case_id=command.case_id,
                correlation_id=command.correlation_id,
            ),
        )

    def _authorize(
        self,
        *,
        actor: ActorContext,
        case_id: UUID,
        action: Capability,
        now: datetime,
        classification=DataClassification.INTERNAL_OPERATIONAL,
        mfa_required=False,
    ) -> None:
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=action,
                resource=AuthorizationResource(
                    resource_type="CASE_HANDOVER",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=classification,
                    case_id=case_id,
                ),
                evaluated_at=now,
                mfa_required=mfa_required,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)


def case_handover_handlers(*, storage=None) -> dict[str, CommandHandler]:
    from app.modules.patron_action.application.case_handover_handler import (
        CaseHandoverHandler,
    )
    from app.modules.patron_action.application.handover_commands import AcknowledgeHandoverCommand
    from app.modules.patron_action.application.handover_receipt_handler import (
        AcknowledgeHandoverHandler,
    )

    return {
        RecordCaseHandoverSnapshotCommand.command_type: CaseHandoverHandler(storage=storage),
        AcknowledgeHandoverCommand.command_type: AcknowledgeHandoverHandler(storage=storage),
    }
