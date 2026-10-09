from __future__ import annotations

import hashlib
import json
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.membership.infrastructure.records import CaseAssignmentRecord
from app.modules.patron_action.public.ports import PatronActionWriter
from app.modules.preparation.application.transmission_commands import (
    CreatePreparationSnapshotCommand,
    TransmitPreparationSnapshotCommand,
)
from app.modules.preparation.infrastructure.models import (
    GeneratedTechnicalDocumentRecord,
    PreparationPackageRecord,
    PreparationReadinessRecord,
    PreparationResponsePlanRecord,
    PreparationReviewRecord,
    PreparationSnapshotRecord,
    PreparationTransmissionRecord,
    TechnicalResponseDraftRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandExecutionError,
    DispatchResult,
    HandlerOutcome,
    PendingDomainEvent,
)
from app.platform.persistence.models import CommandReceiptRecord
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification
from app.platform.storage.ports import GeneratedDocumentStorage

_MAX_RESPONSE_DRAFT_BYTES = 100_000


class PreparationTransmissionService:
    """Own immutable preparation transmission writes and Patron receipt reads."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        dispatcher: CommandDispatcher,
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._session_factory = session_factory
        self._dispatcher = dispatcher
        self._policy = policy

    def execute(self, *, actor: ActorContext, command, now: datetime) -> DispatchResult:
        if actor.actor_kind is not ActorKind.COLLABORATEUR or actor.membership_id is None:
            raise PermissionError("COLLABORATOR_REQUIRED")
        package = self._package(actor.tenant_id, command.package_id)
        if package is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PREPARATION_TRANSMIT,
                resource=AuthorizationResource(
                    resource_type="PREPARATION_PACKAGE",
                    resource_id=package.id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                    case_id=package.case_id,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)
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
                case_id=package.case_id,
                correlation_id=actor.correlation_id,
            ),
        )

    def _package(self, tenant_id: UUID, package_id: UUID) -> PreparationPackageRecord | None:
        with self._session_factory() as session:
            return session.scalar(
                sa.select(PreparationPackageRecord).where(
                    PreparationPackageRecord.tenant_id == tenant_id,
                    PreparationPackageRecord.id == package_id,
                )
            )

    def read_transmissions(self, *, actor: ActorContext, package_id: UUID, now: datetime):
        if actor.actor_kind not in {ActorKind.PATRON_ADMIN, ActorKind.PATRON_DELEGATE}:
            raise PermissionError("PATRON_REQUIRED")
        if actor.membership_id is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        with self._session_factory() as session:
            package = session.scalar(
                sa.select(PreparationPackageRecord).where(
                    PreparationPackageRecord.tenant_id == actor.tenant_id,
                    PreparationPackageRecord.id == package_id,
                )
            )
            if package is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            decision = self._policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=Capability.PREPARATION_REVIEW_DECIDE,
                    resource=AuthorizationResource(
                        resource_type="PREPARATION_PACKAGE",
                        resource_id=package.id,
                        tenant_id=actor.tenant_id,
                        classification=DataClassification.INTERNAL_OPERATIONAL,
                        case_id=package.case_id,
                    ),
                    evaluated_at=now,
                ),
            )
            if not decision.allowed:
                raise PermissionError(decision.code)
            rows = session.execute(
                sa.select(PreparationSnapshotRecord, PreparationTransmissionRecord)
                .join(
                    PreparationTransmissionRecord,
                    sa.and_(
                        PreparationTransmissionRecord.tenant_id
                        == PreparationSnapshotRecord.tenant_id,
                        PreparationTransmissionRecord.package_id
                        == PreparationSnapshotRecord.package_id,
                        PreparationTransmissionRecord.snapshot_id == PreparationSnapshotRecord.id,
                    ),
                )
                .where(
                    PreparationSnapshotRecord.tenant_id == actor.tenant_id,
                    PreparationSnapshotRecord.package_id == package.id,
                    PreparationTransmissionRecord.state == "TRANSMITTED_TO_PATRON",
                )
                .order_by(PreparationSnapshotRecord.version)
            ).all()
            deliveries = []
            for snapshot, transmission in rows:
                manifest = snapshot.manifest_json
                try:
                    manifest_bytes = json.dumps(
                        manifest, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                except (TypeError, ValueError) as error:
                    raise CommandExecutionError("PREPARATION_RECEIPT_UNKNOWN") from error
                if (
                    not isinstance(manifest, dict)
                    or hashlib.sha256(manifest_bytes).hexdigest() != snapshot.manifest_sha256
                    or manifest.get("package_id") != str(package.id)
                    or manifest.get("case_id") != str(package.case_id)
                ):
                    raise CommandExecutionError("PREPARATION_RECEIPT_UNKNOWN")
                snapshot_receipt = self._read_command_receipt(
                    session=session,
                    tenant_id=actor.tenant_id,
                    command_id=snapshot.command_id,
                    expected_command_type=CreatePreparationSnapshotCommand.command_type,
                    expected_result_code="PREPARATION_SNAPSHOT_CREATED",
                    expected_aggregate_type="PreparationSnapshot",
                    expected_aggregate_id=snapshot.id,
                    expected_aggregate_revision=snapshot.version,
                )
                transmission_receipt = self._read_command_receipt(
                    session=session,
                    tenant_id=actor.tenant_id,
                    command_id=transmission.command_id,
                    expected_command_type=TransmitPreparationSnapshotCommand.command_type,
                    expected_result_code="PREPARATION_TRANSMITTED_TO_PATRON",
                    expected_aggregate_type="PreparationTransmission",
                    expected_aggregate_id=transmission.id,
                )
                deliveries.append((snapshot, transmission, snapshot_receipt, transmission_receipt))
            return tuple(deliveries)

    @staticmethod
    def _read_command_receipt(
        *,
        session: Session,
        tenant_id: UUID,
        command_id: UUID,
        expected_command_type: str,
        expected_result_code: str,
        expected_aggregate_type: str,
        expected_aggregate_id: UUID,
        expected_aggregate_revision: int | None = None,
    ) -> dict[str, object]:
        receipt = session.scalar(
            sa.select(CommandReceiptRecord).where(
                CommandReceiptRecord.tenant_id == tenant_id,
                CommandReceiptRecord.command_id == command_id,
            )
        )
        if (
            receipt is None
            or receipt.status != "SUCCEEDED"
            or receipt.command_type != expected_command_type
            or receipt.result_code != expected_result_code
            or receipt.response_body_json is None
            or receipt.aggregate_refs_json is None
        ):
            raise CommandExecutionError("PREPARATION_RECEIPT_UNKNOWN")
        body = receipt.response_body_json
        references = body.get("aggregate_refs")
        if (
            body.get("status") != "SUCCEEDED"
            or body.get("command_id") != str(command_id)
            or body.get("idempotency_key") != str(receipt.idempotency_key)
            or body.get("result_code") != expected_result_code
            or not isinstance(references, list)
            or len(references) != 1
            or receipt.aggregate_refs_json != {"aggregate_refs": references}
            or not isinstance(references[0], dict)
            or references[0].get("aggregate_type") != expected_aggregate_type
            or references[0].get("aggregate_id") != str(expected_aggregate_id)
            or (
                expected_aggregate_revision is not None
                and references[0].get("aggregate_revision") != expected_aggregate_revision
            )
            or body.get("event_ids") != receipt.event_ids_json
        ):
            raise CommandExecutionError("PREPARATION_RECEIPT_UNKNOWN")
        return body


class PreparationTransmissionHandler:
    """Own immutable snapshots and append-only patron transmissions."""

    def __init__(
        self,
        action_writer: PatronActionWriter | None = None,
        storage: GeneratedDocumentStorage | None = None,
    ) -> None:
        self._action_writer = action_writer
        self._storage = storage

    def execute(self, *, session: Session, command, context: CommandContext) -> HandlerOutcome:
        if context.actor_kind != ActorKind.COLLABORATEUR.value or context.membership_id is None:
            raise CommandExecutionError("COLLABORATOR_REQUIRED")
        package = session.scalar(
            sa.select(PreparationPackageRecord)
            .where(
                PreparationPackageRecord.tenant_id == context.tenant_id,
                PreparationPackageRecord.id == command.package_id,
            )
            .with_for_update()
        )
        if package is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        if package.aggregate_revision != command.expected_package_revision:
            raise CommandExecutionError("VERSION_CONFLICT")
        self._ensure_assignment(session=session, package=package, context=context)
        if command.command_type == CreatePreparationSnapshotCommand.command_type:
            return self._create_snapshot(
                session=session, package=package, command=command, context=context
            )
        if command.command_type == TransmitPreparationSnapshotCommand.command_type:
            return self._transmit_snapshot(
                session=session, package=package, command=command, context=context
            )
        raise CommandExecutionError(
            f"unsupported preparation transmission command: {command.command_type}"
        )

    def _ensure_assignment(
        self, *, session: Session, package: PreparationPackageRecord, context: CommandContext
    ) -> None:
        assignment = session.scalar(
            sa.select(CaseAssignmentRecord).where(
                CaseAssignmentRecord.tenant_id == context.tenant_id,
                CaseAssignmentRecord.id == package.assignment_id,
                CaseAssignmentRecord.case_id == package.case_id,
                CaseAssignmentRecord.membership_id == context.membership_id,
                CaseAssignmentRecord.state == "ACTIVE",
            )
        )
        if assignment is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        if Capability.WORK_TASK_WRITE.value not in assignment.scope_actions_json:
            raise CommandExecutionError("ASSIGNMENT_SCOPE_FORBIDDEN")

    def _current_c10_review_manifest(
        self, *, session: Session, package: PreparationPackageRecord, tenant_id: UUID
    ) -> list[dict[str, object]] | None:
        plan = session.scalar(
            sa.select(PreparationResponsePlanRecord)
            .where(
                PreparationResponsePlanRecord.tenant_id == tenant_id,
                PreparationResponsePlanRecord.package_id == package.id,
            )
            .order_by(PreparationResponsePlanRecord.version.desc())
            .limit(1)
        )
        if plan is None:
            return None
        if plan.state != "SOURCES_CURRENT" or plan.dce_version_id != package.dce_version_id:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        drafts = list(
            session.scalars(
                sa.select(TechnicalResponseDraftRecord)
                .where(
                    TechnicalResponseDraftRecord.tenant_id == tenant_id,
                    TechnicalResponseDraftRecord.package_id == package.id,
                )
                .order_by(
                    TechnicalResponseDraftRecord.draft_id,
                    TechnicalResponseDraftRecord.version.desc(),
                )
            ).all()
        )
        latest_drafts: dict[UUID, TechnicalResponseDraftRecord] = {}
        for draft in drafts:
            latest_drafts.setdefault(draft.draft_id, draft)
        current_drafts = [
            draft
            for draft in latest_drafts.values()
            if draft.response_plan_id == plan.plan_id
            and draft.response_plan_version == plan.version
        ]
        if not current_drafts:
            raise CommandExecutionError("RESPONSE_DRAFT_REQUIRED")
        review_rows = list(
            session.scalars(
                sa.select(PreparationReviewRecord).where(
                    PreparationReviewRecord.tenant_id == tenant_id,
                    PreparationReviewRecord.package_id == package.id,
                    PreparationReviewRecord.target_draft_id.is_not(None),
                )
            ).all()
        )
        latest_reviews: dict[UUID, PreparationReviewRecord] = {}
        for review in review_rows:
            current = latest_reviews.get(review.review_id)
            if current is None or review.revision > current.revision:
                latest_reviews[review.review_id] = review
        entries: list[dict[str, object]] = []
        for draft in sorted(current_drafts, key=lambda row: str(row.draft_id)):
            if self._storage is None:
                raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN")
            try:
                draft_content = self._storage.read(storage_key=draft.storage_key)
            except Exception as error:
                raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN") from error
            if (
                len(draft_content) > _MAX_RESPONSE_DRAFT_BYTES
                or hashlib.sha256(draft_content).hexdigest() != draft.content_sha256
            ):
                raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN")
            matching = [
                review
                for review in latest_reviews.values()
                if review.target_draft_id == draft.draft_id
                and review.target_draft_version == draft.version
                and review.target_content_sha256 == draft.content_sha256
            ]
            if len(matching) != 1 or matching[0].state != "ACCEPTED":
                raise CommandExecutionError("RESPONSE_DRAFT_REVIEW_REQUIRED")
            accepted = matching[0]
            entries.append(
                {
                    "draft_id": str(draft.draft_id),
                    "version": draft.version,
                    "content_sha256": draft.content_sha256,
                    "response_plan_id": str(draft.response_plan_id),
                    "response_plan_version": draft.response_plan_version,
                    "review_id": str(accepted.review_id),
                    "review_revision": accepted.revision,
                    "review_state": accepted.state,
                }
            )
        return entries

    def _create_snapshot(
        self,
        *,
        session: Session,
        package: PreparationPackageRecord,
        command,
        context: CommandContext,
    ) -> HandlerOutcome:
        if package.state not in {"GENERATED", "A_REVIEW", "READY"}:
            has_c10_plan = session.scalar(
                sa.select(PreparationResponsePlanRecord.id)
                .where(
                    PreparationResponsePlanRecord.tenant_id == context.tenant_id,
                    PreparationResponsePlanRecord.package_id == package.id,
                )
                .limit(1)
            )
            if has_c10_plan is None:
                raise CommandExecutionError("PREPARATION_NOT_GENERATED")
        readiness = session.scalar(
            sa.select(PreparationReadinessRecord)
            .where(
                PreparationReadinessRecord.tenant_id == context.tenant_id,
                PreparationReadinessRecord.package_id == package.id,
            )
            .order_by(PreparationReadinessRecord.revision.desc())
            .limit(1)
        )
        if readiness is None:
            raise CommandExecutionError("READINESS_NOT_FOUND")
        if readiness.state == "BLOCKED":
            raise CommandExecutionError("PREPARATION_BLOCKED")
        documents = list(
            session.scalars(
                sa.select(GeneratedTechnicalDocumentRecord)
                .where(
                    GeneratedTechnicalDocumentRecord.tenant_id == context.tenant_id,
                    GeneratedTechnicalDocumentRecord.package_id == package.id,
                    GeneratedTechnicalDocumentRecord.state == "GENERATED",
                )
                .order_by(
                    GeneratedTechnicalDocumentRecord.version.desc(),
                    GeneratedTechnicalDocumentRecord.id.desc(),
                )
            ).all()
        )
        if not documents:
            raise CommandExecutionError("TECHNICAL_DOCUMENT_REQUIRED")
        c10_review_manifest = self._current_c10_review_manifest(
            session=session, package=package, tenant_id=package.tenant_id
        )
        if package.state not in {"GENERATED", "A_REVIEW", "READY"}:
            raise CommandExecutionError("PREPARATION_NOT_GENERATED")
        drafts = list(
            session.scalars(
                sa.select(TechnicalResponseDraftRecord)
                .where(
                    TechnicalResponseDraftRecord.tenant_id == context.tenant_id,
                    TechnicalResponseDraftRecord.package_id == package.id,
                )
                .order_by(
                    TechnicalResponseDraftRecord.draft_id,
                    TechnicalResponseDraftRecord.version.desc(),
                )
            ).all()
        )
        latest_drafts: dict[UUID, TechnicalResponseDraftRecord] = {}
        for draft in drafts:
            latest_drafts.setdefault(draft.draft_id, draft)
        if c10_review_manifest is None:
            snapshot_drafts = list(latest_drafts.values())
        else:
            c10_ids = {entry["draft_id"] for entry in c10_review_manifest}
            snapshot_drafts = [
                draft for draft in latest_drafts.values() if str(draft.draft_id) in c10_ids
            ]
        version = (
            session.scalar(
                sa.select(
                    sa.func.coalesce(sa.func.max(PreparationSnapshotRecord.version), 0)
                ).where(
                    PreparationSnapshotRecord.tenant_id == context.tenant_id,
                    PreparationSnapshotRecord.package_id == package.id,
                )
            )
            + 1
        )
        manifest = {
            "schema_version": 1,
            "case_id": str(package.case_id),
            "package_id": str(package.id),
            "dce_version_id": str(package.dce_version_id),
            "readiness": {
                "revision": readiness.revision,
                "state": readiness.state,
                "blocker_codes": sorted(readiness.blocker_codes_json),
                "warning_codes": sorted(readiness.warning_codes_json),
            },
            "documents": [
                {
                    "document_id": str(document.id),
                    "version": document.version,
                    "kind": document.document_kind,
                    "sha256": document.content_sha256,
                }
                for document in documents[:1]
            ],
            "response_drafts": c10_review_manifest
            if c10_review_manifest is not None
            else [
                {
                    "draft_id": str(draft.draft_id),
                    "version": draft.version,
                    "state": draft.state,
                    "section_codes": sorted(draft.section_codes_json),
                    "source_refs": sorted(draft.source_refs_json),
                }
                for draft in snapshot_drafts
            ],
        }
        manifest_sha256 = hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        snapshot = PreparationSnapshotRecord(
            id=command.snapshot_id,
            tenant_id=context.tenant_id,
            package_id=package.id,
            case_id=package.case_id,
            dce_version_id=package.dce_version_id,
            readiness_id=readiness.id,
            technical_document_id=documents[0].id,
            technical_document_version=documents[0].version,
            version=version,
            state="READY_FOR_PATRON_REVIEW",
            manifest_sha256=manifest_sha256,
            manifest_json=manifest,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(snapshot)
        package.aggregate_revision += 1
        package.state = "READY"
        return HandlerOutcome(
            result_code="PREPARATION_SNAPSHOT_CREATED",
            aggregate_refs=(
                {
                    "aggregate_type": "PreparationSnapshot",
                    "aggregate_id": str(snapshot.id),
                    "aggregate_revision": snapshot.version,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="PreparationSnapshot",
                    aggregate_id=snapshot.id,
                    aggregate_revision=snapshot.version,
                    event_type="PreparationSnapshotCreated",
                    payload={
                        "snapshot_id": str(snapshot.id),
                        "package_id": str(package.id),
                        "version": snapshot.version,
                        "state": snapshot.state,
                        "manifest_sha256": manifest_sha256,
                    },
                ),
            ),
        )

    def _transmit_snapshot(
        self,
        *,
        session: Session,
        package: PreparationPackageRecord,
        command,
        context: CommandContext,
    ) -> HandlerOutcome:
        snapshot = session.scalar(
            sa.select(PreparationSnapshotRecord).where(
                PreparationSnapshotRecord.tenant_id == context.tenant_id,
                PreparationSnapshotRecord.id == command.snapshot_id,
                PreparationSnapshotRecord.package_id == package.id,
                PreparationSnapshotRecord.state == "READY_FOR_PATRON_REVIEW",
            )
        )
        if snapshot is None:
            raise CommandExecutionError("SNAPSHOT_NOT_FOUND_OR_FORBIDDEN")
        current_c10_review_manifest = self._current_c10_review_manifest(
            session=session, package=package, tenant_id=package.tenant_id
        )
        if (
            current_c10_review_manifest is not None
            and snapshot.manifest_json.get("response_drafts") != current_c10_review_manifest
        ):
            raise CommandExecutionError("RESPONSE_DRAFT_REVIEW_REQUIRED")
        existing = session.scalar(
            sa.select(PreparationTransmissionRecord).where(
                PreparationTransmissionRecord.tenant_id == context.tenant_id,
                PreparationTransmissionRecord.snapshot_id == snapshot.id,
            )
        )
        if existing is not None:
            raise CommandExecutionError("SNAPSHOT_ALREADY_TRANSMITTED")
        transmission = PreparationTransmissionRecord(
            id=command.transmission_id,
            tenant_id=context.tenant_id,
            package_id=package.id,
            snapshot_id=snapshot.id,
            state="TRANSMITTED_TO_PATRON",
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(transmission)
        action = None
        if self._action_writer is not None:
            action = self._action_writer.create_from_preparation_transmission(
                session=session,
                context=context,
                case_id=package.case_id,
                package_id=package.id,
                transmission_id=transmission.id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
            )
        package.aggregate_revision += 1
        package.state = "A_REVIEW"
        events = [
            PendingDomainEvent(
                aggregate_type="PreparationTransmission",
                aggregate_id=transmission.id,
                aggregate_revision=package.aggregate_revision,
                event_type="PreparationTransmittedToPatron",
                payload={
                    "transmission_id": str(transmission.id),
                    "snapshot_id": str(snapshot.id),
                    "package_id": str(package.id),
                    "state": transmission.state,
                },
            )
        ]
        if action is not None:
            events.append(
                PendingDomainEvent(
                    aggregate_type="PatronAction",
                    aggregate_id=action.id,
                    aggregate_revision=action.aggregate_revision,
                    event_type="PatronActionCreated",
                    payload={
                        "action_id": str(action.id),
                        "case_id": str(action.case_id),
                        "action_type": action.action_type,
                        "severity": action.severity,
                        "state": action.state,
                    },
                )
            )
        return HandlerOutcome(
            result_code="PREPARATION_TRANSMITTED_TO_PATRON",
            aggregate_refs=(
                {
                    "aggregate_type": "PreparationTransmission",
                    "aggregate_id": str(transmission.id),
                    "aggregate_revision": package.aggregate_revision,
                },
            ),
            events=tuple(events),
        )


def preparation_transmission_handlers(
    *,
    action_writer: PatronActionWriter | None = None,
    storage: GeneratedDocumentStorage | None = None,
) -> dict[str, PreparationTransmissionHandler]:
    handler = PreparationTransmissionHandler(action_writer=action_writer, storage=storage)
    return {
        CreatePreparationSnapshotCommand.command_type: handler,
        TransmitPreparationSnapshotCommand.command_type: handler,
    }
