from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from types import SimpleNamespace
from typing import Protocol, cast
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.enterprise.infrastructure.models import (
    EnterpriseCapabilityRecord,
    EnterpriseCapabilityVersionRecord,
    EnterpriseDocumentRecord,
    EnterpriseDocumentUploadRecord,
)
from app.modules.membership.infrastructure.records import CaseAssignmentRecord
from app.modules.membership.public.text_safety import contains_forbidden_text
from app.modules.preparation.application.document_content import (
    ResponsePlanDraftItem,
    build_response_plan_draft,
)
from app.modules.preparation.application.plan_commands import (
    CreatePreparationResponsePlanCommand,
)
from app.modules.preparation.application.ports import (
    PreparationPrivateSourceDigestReader,
    PreparationResponsePlanFact,
    PreparationResponsePlanSourceReader,
)
from app.modules.preparation.application.review_commands import (
    AddPreparationCorrectionCommand,
    CreateTechnicalResponseDraftCommand,
    DecidePreparationReviewCommand,
    RequestPreparationReviewCommand,
)
from app.modules.preparation.infrastructure.models import (
    GeneratedTechnicalDocumentRecord,
    PreparationPackageRecord,
    PreparationResponsePlanRecord,
    PreparationReviewCorrectionRecord,
    PreparationReviewRecord,
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
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification
from app.platform.storage.ports import GeneratedDocumentStorage

_MAX_RESPONSE_PLAN_SOURCE_BYTES = 150_000_000
_MAX_RESPONSE_DRAFT_BYTES = 100_000
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

_REVIEW_COMMANDS = frozenset(
    {
        "RequestPreparationReview",
        "DecidePreparationReview",
        "AddPreparationCorrection",
        "CreatePreparationResponsePlan",
        "CreateTechnicalResponseDraft",
    }
)
_ALLOWED_SECTION_CODES = frozenset(
    {"COVER", "UNDERSTANDING", "METHOD", "RESOURCES", "SCHEDULE", "RISKS", "SOURCES"}
)


class _ResponsePlanFields(Protocol):
    section_codes: list[str]
    source_refs: list[UUID]


class PreparationReviewService:
    """Facade that separates collaborator requests from patron review authority."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        dispatcher: CommandDispatcher,
        policy: AuthorizationPolicyPort,
        storage: GeneratedDocumentStorage,
    ) -> None:
        self._session_factory = session_factory
        self._dispatcher = dispatcher
        self._policy = policy
        self._storage = storage

    def execute(self, *, actor: ActorContext, command, now: datetime) -> DispatchResult:
        c10_review_request = (
            command.command_type == "RequestPreparationReview"
            and getattr(command, "target_draft_id", None) is not None
        )
        is_collaborator_write = command.command_type in {
            "CreatePreparationResponsePlan",
            "CreateTechnicalResponseDraft",
        } or (command.command_type == "RequestPreparationReview" and not c10_review_request)
        is_patron_review = (
            command.command_type
            in {
                "DecidePreparationReview",
                "AddPreparationCorrection",
            }
            or c10_review_request
        )
        if c10_review_request and actor.actor_kind not in {
            ActorKind.COLLABORATEUR,
            ActorKind.PATRON_ADMIN,
        }:
            raise PermissionError("PATRON_OR_COLLABORATOR_REQUIRED")
        if is_collaborator_write and actor.actor_kind is not ActorKind.COLLABORATEUR:
            raise PermissionError("COLLABORATOR_REQUIRED")
        if (
            is_patron_review
            and not c10_review_request
            and actor.actor_kind is not ActorKind.PATRON_ADMIN
        ):
            raise PermissionError("PATRON_REQUIRED")
        package = self._resolve_package(actor=actor, command=command)
        if package is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        capability = (
            Capability.PREPARATION_REVIEW_REQUEST
            if command.command_type == "RequestPreparationReview"
            and actor.actor_kind is ActorKind.COLLABORATEUR
            else Capability.PREPARATION_REVIEW_DECIDE
            if command.command_type == "RequestPreparationReview"
            else Capability.PREPARATION_DOCUMENT_WRITE
            if command.command_type
            in {"CreateTechnicalResponseDraft", "CreatePreparationResponsePlan"}
            else Capability.PREPARATION_REVIEW_DECIDE
        )
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=capability,
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

    def read_reviews(
        self, *, actor: ActorContext, package_id: UUID, now: datetime
    ) -> tuple[tuple[PreparationReviewRecord, tuple[PreparationReviewCorrectionRecord, ...]], ...]:
        """Read latest review revisions for a patron-owned preparation package."""
        if actor.actor_kind not in {ActorKind.PATRON_ADMIN, ActorKind.PATRON_DELEGATE}:
            raise PermissionError("PATRON_REQUIRED")
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
            records = list(
                session.scalars(
                    sa.select(PreparationReviewRecord)
                    .where(
                        PreparationReviewRecord.tenant_id == actor.tenant_id,
                        PreparationReviewRecord.package_id == package.id,
                    )
                    .order_by(PreparationReviewRecord.review_id, PreparationReviewRecord.revision)
                ).all()
            )
            latest: dict[UUID, PreparationReviewRecord] = {}
            for record in records:
                latest[record.review_id] = record
            if not latest:
                return ()
            corrections = list(
                session.scalars(
                    sa.select(PreparationReviewCorrectionRecord).where(
                        PreparationReviewCorrectionRecord.tenant_id == actor.tenant_id,
                        PreparationReviewCorrectionRecord.review_id.in_(latest),
                    )
                ).all()
            )
            corrections_by_review: dict[UUID, list[PreparationReviewCorrectionRecord]] = {}
            for correction in corrections:
                if correction.review_id in latest:
                    corrections_by_review.setdefault(correction.review_id, []).append(correction)
            return tuple(
                (record, tuple(corrections_by_review.get(review_id, [])))
                for review_id, record in latest.items()
            )

    def read_response_drafts(
        self, *, actor: ActorContext, package_id: UUID, now: datetime
    ) -> tuple[TechnicalResponseDraftRecord, ...]:
        """Read versioned non-financial drafts for a patron review."""
        if actor.actor_kind not in {ActorKind.PATRON_ADMIN, ActorKind.PATRON_DELEGATE}:
            raise PermissionError("PATRON_REQUIRED")
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
            return tuple(
                session.scalars(
                    sa.select(TechnicalResponseDraftRecord)
                    .where(
                        TechnicalResponseDraftRecord.tenant_id == actor.tenant_id,
                        TechnicalResponseDraftRecord.package_id == package.id,
                    )
                    .order_by(
                        TechnicalResponseDraftRecord.draft_id,
                        TechnicalResponseDraftRecord.version,
                    )
                ).all()
            )

    def read_response_drafts_package_revision(
        self, *, actor: ActorContext, package_id: UUID, now: datetime
    ) -> int:
        self.read_response_drafts(actor=actor, package_id=package_id, now=now)
        with self._session_factory() as session:
            package = session.scalar(
                sa.select(PreparationPackageRecord).where(
                    PreparationPackageRecord.tenant_id == actor.tenant_id,
                    PreparationPackageRecord.id == package_id,
                )
            )
            if package is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            return package.aggregate_revision

    def read_verified_response_drafts(
        self, *, actor: ActorContext, package_id: UUID, now: datetime
    ) -> tuple[tuple[TechnicalResponseDraftRecord, str], ...]:
        result = []
        for draft in self.read_response_drafts(actor=actor, package_id=package_id, now=now):
            try:
                content = self._storage.read(storage_key=draft.storage_key)
                text = content.decode("utf-8")
            except Exception as error:
                raise PermissionError("RESPONSE_DRAFT_UNKNOWN") from error
            if (
                len(content) > _MAX_RESPONSE_DRAFT_BYTES
                or hashlib.sha256(content).hexdigest() != draft.content_sha256
                or contains_forbidden_text(text)
            ):
                raise PermissionError("RESPONSE_DRAFT_UNKNOWN")
            result.append((draft, text))
        return tuple(result)

    def read_response_plans(
        self, *, actor: ActorContext, package_id: UUID, now: datetime
    ) -> tuple[PreparationResponsePlanRecord, ...]:
        if actor.actor_kind is not ActorKind.COLLABORATEUR or actor.membership_id is None:
            raise PermissionError("COLLABORATOR_REQUIRED")
        with self._session_factory() as session:
            package = session.scalar(
                sa.select(PreparationPackageRecord).where(
                    PreparationPackageRecord.tenant_id == actor.tenant_id,
                    PreparationPackageRecord.id == package_id,
                )
            )
            if package is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            assignment = session.scalar(
                sa.select(CaseAssignmentRecord).where(
                    CaseAssignmentRecord.tenant_id == actor.tenant_id,
                    CaseAssignmentRecord.id == package.assignment_id,
                    CaseAssignmentRecord.case_id == package.case_id,
                    CaseAssignmentRecord.membership_id == actor.membership_id,
                    CaseAssignmentRecord.state == "ACTIVE",
                    CaseAssignmentRecord.starts_at <= now,
                    sa.or_(
                        CaseAssignmentRecord.ends_at.is_(None), CaseAssignmentRecord.ends_at > now
                    ),
                )
            )
            if (
                assignment is None
                or Capability.PREPARATION_DOCUMENT_WRITE.value not in assignment.scope_actions_json
            ):
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            decision = self._policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=Capability.PREPARATION_DOCUMENT_WRITE,
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
            return tuple(
                session.scalars(
                    sa.select(PreparationResponsePlanRecord)
                    .where(
                        PreparationResponsePlanRecord.tenant_id == actor.tenant_id,
                        PreparationResponsePlanRecord.package_id == package.id,
                    )
                    .order_by(
                        PreparationResponsePlanRecord.plan_id,
                        PreparationResponsePlanRecord.version,
                    )
                ).all()
            )

    def _resolve_package(self, *, actor: ActorContext, command) -> PreparationPackageRecord | None:
        with self._session_factory() as session:
            package = session.scalar(
                sa.select(PreparationPackageRecord).where(
                    PreparationPackageRecord.tenant_id == actor.tenant_id,
                    PreparationPackageRecord.id == command.package_id,
                )
            )
            if package is None:
                return None
            if actor.actor_kind is ActorKind.PATRON_ADMIN:
                return package
            assignment = session.scalar(
                sa.select(CaseAssignmentRecord).where(
                    CaseAssignmentRecord.tenant_id == actor.tenant_id,
                    CaseAssignmentRecord.id == package.assignment_id,
                    CaseAssignmentRecord.case_id == package.case_id,
                    CaseAssignmentRecord.membership_id == actor.membership_id,
                    CaseAssignmentRecord.state == "ACTIVE",
                )
            )
            if (
                assignment is None
                or Capability.WORK_TASK_WRITE.value not in assignment.scope_actions_json
            ):
                return None
            return package


class PreparationReviewHandler:
    """Own immutable review transitions, corrections and draft versions."""

    def __init__(
        self,
        *,
        storage: GeneratedDocumentStorage,
        source_reader: PreparationResponsePlanSourceReader | None = None,
        source_storage: PreparationPrivateSourceDigestReader | None = None,
    ) -> None:
        self._storage = storage
        self._source_reader = source_reader
        self._source_storage = source_storage

    def execute(self, *, session: Session, command, context: CommandContext) -> HandlerOutcome:
        if command.command_type == "RequestPreparationReview":
            return self._request(session=session, command=command, context=context)
        if command.command_type == "DecidePreparationReview":
            return self._decide(session=session, command=command, context=context)
        if command.command_type == "AddPreparationCorrection":
            return self._correction(session=session, command=command, context=context)
        if command.command_type == "CreatePreparationResponsePlan":
            return self._response_plan(session=session, command=command, context=context)
        if command.command_type == "CreateTechnicalResponseDraft":
            return self._draft(session=session, command=command, context=context)
        raise CommandExecutionError(
            f"unsupported preparation review command: {command.command_type}"
        )

    def _response_plan(
        self,
        *,
        session: Session,
        command: CreatePreparationResponsePlanCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.COLLABORATEUR.value or context.membership_id is None:
            raise CommandExecutionError("COLLABORATOR_REQUIRED")
        package = self._package(session=session, context=context, package_id=command.package_id)
        if package.aggregate_revision != command.expected_package_revision:
            raise CommandExecutionError("VERSION_CONFLICT")
        existing_plan_id = session.scalar(
            sa.select(PreparationResponsePlanRecord.plan_id)
            .where(
                PreparationResponsePlanRecord.tenant_id == context.tenant_id,
                PreparationResponsePlanRecord.package_id == package.id,
            )
            .limit(1)
        )
        if existing_plan_id is not None and existing_plan_id != command.plan_id:
            raise CommandExecutionError("VERSION_CONFLICT")
        assignment = session.scalar(
            sa.select(CaseAssignmentRecord).where(
                CaseAssignmentRecord.tenant_id == context.tenant_id,
                CaseAssignmentRecord.id == package.assignment_id,
                CaseAssignmentRecord.case_id == package.case_id,
                CaseAssignmentRecord.membership_id == context.membership_id,
                CaseAssignmentRecord.state == "ACTIVE",
                CaseAssignmentRecord.starts_at <= context.received_at,
                sa.or_(
                    CaseAssignmentRecord.ends_at.is_(None),
                    CaseAssignmentRecord.ends_at > context.received_at,
                ),
            )
        )
        if (
            assignment is None
            or Capability.PREPARATION_DOCUMENT_WRITE.value not in assignment.scope_actions_json
        ):
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        requirement_ids = {item.requirement_id for item in command.items}
        proposal_ids = {
            item.source_proposal_id for item in command.items if item.source_proposal_id is not None
        }
        if self._source_reader is None:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        sources = self._source_reader.read(
            session=session,
            tenant_id=package.tenant_id,
            case_id=package.case_id,
            assignment_id=package.assignment_id,
            dce_version_id=package.dce_version_id,
            requirement_ids=requirement_ids,
            proposal_ids=proposal_ids,
            evaluated_at=context.received_at,
        )
        if not sources.dce_current:
            raise CommandExecutionError("VERSION_CONFLICT")
        if len(sources.requirement_states) != len(requirement_ids):
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        if len(sources.facts) != len(proposal_ids):
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")

        items: list[dict[str, object]] = []
        source_manifest_by_proposal: dict[UUID, dict[str, object]] = {}
        for item in command.items:
            requirement_state = sources.requirement_states[item.requirement_id]
            fact = (
                sources.facts.get(item.source_proposal_id)
                if item.source_proposal_id is not None
                else None
            )
            source_version_id = None
            source_validity_state = "UNKNOWN"
            source_state = "UNKNOWN"
            if item.source_proposal_id is not None:
                if fact is None:
                    raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
                if fact.requirement_id != item.requirement_id or fact.task_id is not None:
                    raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
                if fact.validity_state == "EXPIRED" or fact.evidence_state == "EXPIRED":
                    raise CommandExecutionError("REUSABLE_FACT_EXPIRED")
                source_validity_state = fact.validity_state
                source_state = fact.evidence_state
                source_version_id = fact.capability_version_id
                source_manifest_by_proposal[fact.proposal_id] = {
                    "source_proposal_id": str(fact.proposal_id),
                    "source_capability_version_id": str(fact.capability_version_id),
                    "source_evidence_state": fact.evidence_state,
                    "proofs": [
                        {"document_id": str(document_id), "sha256": sha256}
                        for document_id, sha256 in fact.proof_refs
                    ],
                }
            items.append(
                {
                    "requirement_id": str(item.requirement_id),
                    "requirement_state": requirement_state,
                    "section_code": item.section_code,
                    "source_proposal_id": (str(fact.proposal_id) if fact is not None else None),
                    "source_capability_version_id": (
                        str(source_version_id) if source_version_id is not None else None
                    ),
                    "source_validity_state": source_validity_state,
                    "source_evidence_state": source_state,
                }
            )
        items.sort(key=lambda item: (item["requirement_id"], item["section_code"]))
        content = {
            "schema_version": 1,
            "case_id": str(package.case_id),
            "package_id": str(package.id),
            "dce_version_id": str(package.dce_version_id),
            "items": items,
        }
        serialized = json.dumps(
            content, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        source_evidence_json = [
            source_manifest_by_proposal[proposal_id]
            for proposal_id in sorted(source_manifest_by_proposal, key=str)
        ]
        source_evidence_serialized = json.dumps(
            source_evidence_json, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        plan_sha256 = hashlib.sha256(serialized).hexdigest()
        source_evidence_sha256 = hashlib.sha256(source_evidence_serialized).hexdigest()
        state = (
            "SOURCES_CURRENT"
            if all(
                item["requirement_state"] == "CONFIRMED"
                and item["source_validity_state"] == "CURRENT"
                and item["source_evidence_state"] == "CURRENT"
                for item in items
            )
            else "UNKNOWN"
        )
        version = (
            session.scalar(
                sa.select(
                    sa.func.coalesce(sa.func.max(PreparationResponsePlanRecord.version), 0)
                ).where(
                    PreparationResponsePlanRecord.tenant_id == context.tenant_id,
                    PreparationResponsePlanRecord.package_id == package.id,
                    PreparationResponsePlanRecord.plan_id == command.plan_id,
                )
            )
            + 1
        )
        session.add(
            PreparationResponsePlanRecord(
                id=command.command_id,
                tenant_id=context.tenant_id,
                plan_id=command.plan_id,
                package_id=package.id,
                dce_version_id=package.dce_version_id,
                version=version,
                state=state,
                content_json=content,
                plan_sha256=plan_sha256,
                source_evidence_json=source_evidence_json,
                source_evidence_sha256=source_evidence_sha256,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        package.aggregate_revision += 1
        return self._outcome(
            aggregate_type="PreparationResponsePlan",
            aggregate_id=command.plan_id,
            revision=version,
            event_type="PreparationResponsePlanCreated",
            payload={
                "plan_id": str(command.plan_id),
                "package_id": str(package.id),
                "dce_version_id": str(package.dce_version_id),
                "version": version,
                "state": state,
                "plan_sha256": plan_sha256,
            },
            result_code="PREPARATION_RESPONSE_PLAN_CREATED",
        )

    def _package(
        self, *, session: Session, context: CommandContext, package_id: UUID
    ) -> PreparationPackageRecord:
        package = session.scalar(
            sa.select(PreparationPackageRecord)
            .where(
                PreparationPackageRecord.tenant_id == context.tenant_id,
                PreparationPackageRecord.id == package_id,
            )
            .with_for_update()
        )
        if package is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        return package

    def _document(
        self,
        *,
        session: Session,
        context: CommandContext,
        package: PreparationPackageRecord,
        document_id: UUID,
        version: int,
    ) -> GeneratedTechnicalDocumentRecord:
        document = session.scalar(
            sa.select(GeneratedTechnicalDocumentRecord).where(
                GeneratedTechnicalDocumentRecord.tenant_id == context.tenant_id,
                GeneratedTechnicalDocumentRecord.id == document_id,
                GeneratedTechnicalDocumentRecord.package_id == package.id,
                GeneratedTechnicalDocumentRecord.version == version,
            )
        )
        if document is None:
            raise CommandExecutionError("TARGET_VERSION_NOT_FOUND")
        return document

    def _latest_review(
        self, *, session: Session, context: CommandContext, review_id: UUID
    ) -> PreparationReviewRecord | None:
        return session.scalar(
            sa.select(PreparationReviewRecord)
            .where(
                PreparationReviewRecord.tenant_id == context.tenant_id,
                PreparationReviewRecord.review_id == review_id,
            )
            .order_by(PreparationReviewRecord.revision.desc())
            .limit(1)
            .with_for_update()
        )

    def _request(
        self, *, session: Session, command: RequestPreparationReviewCommand, context: CommandContext
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.COLLABORATEUR.value and not (
            command.target_draft_id is not None
            and context.actor_kind == ActorKind.PATRON_ADMIN.value
        ):
            raise CommandExecutionError("COLLABORATOR_REQUIRED")
        package = self._package(session=session, context=context, package_id=command.package_id)
        if package.aggregate_revision != command.expected_package_revision:
            raise CommandExecutionError("VERSION_CONFLICT")
        target_draft = None
        if command.target_draft_id is not None:
            target_draft = self._exact_response_draft(
                session=session,
                context=context,
                package=package,
                draft_id=command.target_draft_id,
                version=command.target_draft_version,
                expected_sha256=command.target_content_sha256,
            )
            target_document_id = target_draft.source_document_id
            target_document = session.scalar(
                sa.select(GeneratedTechnicalDocumentRecord).where(
                    GeneratedTechnicalDocumentRecord.tenant_id == context.tenant_id,
                    GeneratedTechnicalDocumentRecord.package_id == package.id,
                    GeneratedTechnicalDocumentRecord.id == target_document_id,
                )
            )
            if target_document is None:
                raise CommandExecutionError("TARGET_VERSION_NOT_FOUND")
            target_version = target_document.version
        else:
            if command.target_document_id is None or command.target_version is None:
                raise CommandExecutionError("REVIEW_TARGET_INCOMPLETE")
            target_document = self._document(
                session=session,
                context=context,
                package=package,
                document_id=command.target_document_id,
                version=command.target_version,
            )
            target_document_id = target_document.id
            target_version = target_document.version
        if target_draft is not None:
            existing_target_review = session.scalar(
                sa.select(PreparationReviewRecord.review_id)
                .where(
                    PreparationReviewRecord.tenant_id == context.tenant_id,
                    PreparationReviewRecord.package_id == package.id,
                    PreparationReviewRecord.target_draft_id == target_draft.draft_id,
                    PreparationReviewRecord.target_draft_version == target_draft.version,
                    PreparationReviewRecord.target_content_sha256 == target_draft.content_sha256,
                )
                .limit(1)
            )
            if existing_target_review is not None:
                raise CommandExecutionError("REVIEW_ALREADY_EXISTS")
        if (
            self._latest_review(session=session, context=context, review_id=command.review_id)
            is not None
        ):
            raise CommandExecutionError("REVIEW_ALREADY_EXISTS")
        review = PreparationReviewRecord(
            id=command.command_id,
            tenant_id=context.tenant_id,
            review_id=command.review_id,
            package_id=package.id,
            target_document_id=target_document_id,
            target_version=target_version,
            target_draft_id=target_draft.draft_id if target_draft else None,
            target_draft_version=target_draft.version if target_draft else None,
            target_content_sha256=target_draft.content_sha256 if target_draft else None,
            revision=1,
            state="REQUESTED",
            decision_code=None,
            decision_note=None,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(review)
        package.aggregate_revision += 1
        package.state = "A_REVIEW"
        return self._outcome(
            aggregate_type="PreparationReview",
            aggregate_id=command.review_id,
            revision=1,
            event_type="PreparationReviewRequested",
            payload={
                "review_id": str(command.review_id),
                "target_document_id": str(target_document_id),
                "target_version": target_version,
                "target_draft_id": str(target_draft.draft_id) if target_draft else None,
                "target_draft_version": target_draft.version if target_draft else None,
                "target_content_sha256": target_draft.content_sha256 if target_draft else None,
                "state": "REQUESTED",
            },
            result_code="PREPARATION_REVIEW_REQUESTED",
        )

    def _exact_response_draft(
        self,
        *,
        session: Session,
        context: CommandContext,
        package: PreparationPackageRecord,
        draft_id: UUID,
        version: int | None,
        expected_sha256: str | None,
    ) -> TechnicalResponseDraftRecord:
        if version is None or expected_sha256 is None or not _SHA256_RE.fullmatch(expected_sha256):
            raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN")
        draft = session.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == context.tenant_id,
                TechnicalResponseDraftRecord.package_id == package.id,
                TechnicalResponseDraftRecord.draft_id == draft_id,
                TechnicalResponseDraftRecord.version == version,
            )
        )
        latest_version = session.scalar(
            sa.select(sa.func.max(TechnicalResponseDraftRecord.version)).where(
                TechnicalResponseDraftRecord.tenant_id == context.tenant_id,
                TechnicalResponseDraftRecord.package_id == package.id,
                TechnicalResponseDraftRecord.draft_id == draft_id,
            )
        )
        if (
            draft is None
            or latest_version != version
            or draft.response_plan_id is None
            or draft.content_sha256 != expected_sha256
        ):
            raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN")
        plan = session.scalar(
            sa.select(PreparationResponsePlanRecord).where(
                PreparationResponsePlanRecord.tenant_id == context.tenant_id,
                PreparationResponsePlanRecord.package_id == package.id,
                PreparationResponsePlanRecord.plan_id == draft.response_plan_id,
                PreparationResponsePlanRecord.version == draft.response_plan_version,
                PreparationResponsePlanRecord.state == "SOURCES_CURRENT",
                PreparationResponsePlanRecord.dce_version_id == package.dce_version_id,
            )
        )
        latest_plan_version = session.scalar(
            sa.select(sa.func.max(PreparationResponsePlanRecord.version)).where(
                PreparationResponsePlanRecord.tenant_id == context.tenant_id,
                PreparationResponsePlanRecord.package_id == package.id,
            )
        )
        if plan is None or latest_plan_version != plan.version:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        try:
            content = self._storage.read(storage_key=draft.storage_key)
            decoded = content.decode("utf-8")
        except Exception as error:
            raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN") from error
        if (
            len(content) > _MAX_RESPONSE_DRAFT_BYTES
            or hashlib.sha256(content).hexdigest() != expected_sha256
            or contains_forbidden_text(decoded)
        ):
            raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN")
        return draft

    def _decide(
        self, *, session: Session, command: DecidePreparationReviewCommand, context: CommandContext
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value:
            raise CommandExecutionError("PATRON_REQUIRED")
        package = self._package(session=session, context=context, package_id=command.package_id)
        latest = self._latest_review(session=session, context=context, review_id=command.review_id)
        if (
            latest is None
            or latest.package_id != package.id
            or (
                command.target_document_id is not None
                and latest.target_document_id != command.target_document_id
            )
            or (
                latest.target_draft_id is not None
                and (
                    latest.target_draft_id != command.target_draft_id
                    or latest.target_draft_version != command.target_draft_version
                    or latest.target_content_sha256 != command.target_content_sha256
                )
            )
        ):
            raise CommandExecutionError("REVIEW_NOT_FOUND")
        if latest.target_draft_id is not None:
            self._exact_response_draft(
                session=session,
                context=context,
                package=package,
                draft_id=latest.target_draft_id,
                version=latest.target_draft_version,
                expected_sha256=latest.target_content_sha256,
            )
        if latest.revision != command.expected_review_revision:
            raise CommandExecutionError("VERSION_CONFLICT")
        if latest.state not in {"REQUESTED", "RETURNED_WITH_CORRECTIONS"}:
            raise CommandExecutionError("REVIEW_STATE_INVALID")
        state = {
            "ACCEPTED": "ACCEPTED",
            "CORRECTIONS_REQUIRED": "RETURNED_WITH_CORRECTIONS",
            "REJECTED": "REJECTED",
        }[command.decision_code]
        revision = latest.revision + 1
        session.add(
            PreparationReviewRecord(
                id=command.command_id,
                tenant_id=context.tenant_id,
                review_id=latest.review_id,
                package_id=package.id,
                target_document_id=latest.target_document_id,
                target_version=latest.target_version,
                target_draft_id=latest.target_draft_id,
                target_draft_version=latest.target_draft_version,
                target_content_sha256=latest.target_content_sha256,
                revision=revision,
                state=state,
                decision_code=command.decision_code,
                decision_note=command.decision_note,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        package.aggregate_revision += 1
        package.state = (
            "READY"
            if state == "ACCEPTED"
            else "A_REVIEW"
            if state == "RETURNED_WITH_CORRECTIONS"
            else "BLOCKED"
        )
        return self._outcome(
            aggregate_type="PreparationReview",
            aggregate_id=latest.review_id,
            revision=revision,
            event_type="PreparationReviewDecided",
            payload={
                "review_id": str(latest.review_id),
                "revision": revision,
                "decision_code": command.decision_code,
                "state": state,
            },
            result_code="PREPARATION_REVIEW_DECIDED",
        )

    def _correction(
        self, *, session: Session, command: AddPreparationCorrectionCommand, context: CommandContext
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value:
            raise CommandExecutionError("PATRON_REQUIRED")
        package = self._package(session=session, context=context, package_id=command.package_id)
        latest = self._latest_review(session=session, context=context, review_id=command.review_id)
        if (
            latest is None
            or latest.package_id != package.id
            or (
                command.target_document_id is not None
                and latest.target_document_id != command.target_document_id
            )
            or (
                latest.target_draft_id is not None
                and (
                    latest.target_draft_id != command.target_draft_id
                    or latest.target_draft_version != command.target_draft_version
                    or latest.target_content_sha256 != command.target_content_sha256
                )
            )
        ):
            raise CommandExecutionError("REVIEW_NOT_FOUND")
        if latest.state != "RETURNED_WITH_CORRECTIONS":
            raise CommandExecutionError("CORRECTIONS_NOT_REQUESTED")
        source_draft = None
        corrected_sha256 = None
        corrected_version = None
        if latest.target_draft_id is not None:
            if not command.corrected_content:
                raise CommandExecutionError("CORRECTED_RESPONSE_DRAFT_REQUIRED")
            source_draft = self._exact_response_draft(
                session=session,
                context=context,
                package=package,
                draft_id=latest.target_draft_id,
                version=latest.target_draft_version,
                expected_sha256=latest.target_content_sha256,
            )
            sections = list(source_draft.section_codes_json)
            refs = [UUID(item) for item in source_draft.source_refs_json]
            plan, source_facts = self._current_response_plan(
                session=session,
                package=package,
                command=cast(
                    _ResponsePlanFields,
                    SimpleNamespace(section_codes=sections, source_refs=refs),
                ),
                context=context,
            )
            if (plan.plan_id, plan.version) != (
                source_draft.response_plan_id,
                source_draft.response_plan_version,
            ):
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            self._reread_response_plan_sources(
                session=session,
                plan=plan,
                source_facts=source_facts,
                tenant_id=package.tenant_id,
            )
            if contains_forbidden_text(command.corrected_content):
                raise CommandExecutionError("FINANCIAL_DATA_FORBIDDEN")
            corrected_version = source_draft.version + 1
            corrected_bytes = command.corrected_content.encode("utf-8")
            if len(corrected_bytes) > _MAX_RESPONSE_DRAFT_BYTES:
                raise CommandExecutionError("RESPONSE_DRAFT_TOO_LARGE")
            storage_key = (
                f"technical-response-drafts/{context.tenant_id}/{package.id}/"
                f"{source_draft.draft_id}/{corrected_version}.md"
            )
            try:
                corrected_sha256 = self._storage.write(
                    storage_key=storage_key, content=corrected_bytes
                )
            except Exception as error:
                raise CommandExecutionError("RESPONSE_DRAFT_STORAGE_FAILED") from error
            if corrected_sha256 != hashlib.sha256(corrected_bytes).hexdigest():
                raise CommandExecutionError("RESPONSE_DRAFT_STORAGE_FAILED")
        revision = (
            session.scalar(
                sa.select(
                    sa.func.coalesce(sa.func.max(PreparationReviewCorrectionRecord.revision), 0)
                ).where(
                    PreparationReviewCorrectionRecord.tenant_id == context.tenant_id,
                    PreparationReviewCorrectionRecord.review_id == latest.review_id,
                )
            )
            + 1
        )
        session.add(
            PreparationReviewCorrectionRecord(
                id=command.command_id,
                tenant_id=context.tenant_id,
                review_id=latest.review_id,
                review_revision=latest.revision,
                target_document_id=latest.target_document_id,
                target_draft_id=latest.target_draft_id,
                target_draft_version=latest.target_draft_version,
                target_content_sha256=latest.target_content_sha256,
                revision=revision,
                correction_code=command.correction_code,
                instruction=command.instruction,
                source_locator=command.source_locator,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        if (
            source_draft is not None
            and corrected_sha256 is not None
            and corrected_version is not None
        ):
            session.add(
                TechnicalResponseDraftRecord(
                    id=command.command_id,
                    tenant_id=context.tenant_id,
                    draft_id=source_draft.draft_id,
                    package_id=package.id,
                    source_document_id=source_draft.source_document_id,
                    response_plan_id=source_draft.response_plan_id,
                    response_plan_version=source_draft.response_plan_version,
                    version=corrected_version,
                    state="DRAFT",
                    section_codes_json=list(source_draft.section_codes_json),
                    source_refs_json=list(source_draft.source_refs_json),
                    responsible_role="PATRON_REVIEWER",
                    content_sha256=corrected_sha256,
                    storage_key=storage_key,
                    actor_id=context.actor_id,
                    membership_id=context.membership_id,
                    command_id=command.command_id,
                    idempotency_key=command.idempotency_key,
                    correlation_id=command.correlation_id,
                )
            )
            session.flush()
            session.add(
                PreparationReviewRecord(
                    id=uuid4(),
                    tenant_id=context.tenant_id,
                    review_id=latest.review_id,
                    package_id=package.id,
                    target_document_id=latest.target_document_id,
                    target_version=latest.target_version,
                    target_draft_id=source_draft.draft_id,
                    target_draft_version=corrected_version,
                    target_content_sha256=corrected_sha256,
                    revision=latest.revision + 1,
                    state="REQUESTED",
                    decision_code=None,
                    decision_note=None,
                    actor_id=context.actor_id,
                    membership_id=context.membership_id,
                    command_id=uuid4(),
                    idempotency_key=uuid4(),
                    correlation_id=context.correlation_id,
                )
            )
        package.aggregate_revision += 1
        package.state = "A_REVIEW"
        if source_draft is not None and corrected_version is not None:
            return HandlerOutcome(
                result_code="PREPARATION_CORRECTION_ADDED",
                aggregate_refs=(
                    {
                        "aggregate_type": "PreparationReview",
                        "aggregate_id": str(latest.review_id),
                        "aggregate_revision": latest.revision + 1,
                    },
                    {
                        "aggregate_type": "TechnicalResponseDraft",
                        "aggregate_id": str(source_draft.draft_id),
                        "aggregate_revision": corrected_version,
                    },
                ),
                events=(
                    PendingDomainEvent(
                        aggregate_type="TechnicalResponseDraft",
                        aggregate_id=source_draft.draft_id,
                        aggregate_revision=corrected_version,
                        event_type="TechnicalResponseDraftCorrected",
                        payload={
                            "draft_id": str(source_draft.draft_id),
                            "version": corrected_version,
                            "response_plan_id": str(source_draft.response_plan_id),
                            "response_plan_version": source_draft.response_plan_version,
                        },
                    ),
                    PendingDomainEvent(
                        aggregate_type="PreparationReview",
                        aggregate_id=latest.review_id,
                        aggregate_revision=latest.revision + 1,
                        event_type="PreparationReviewRequested",
                        payload={
                            "review_id": str(latest.review_id),
                            "revision": latest.revision + 1,
                            "target_draft_version": corrected_version,
                            "state": "REQUESTED",
                        },
                    ),
                    PendingDomainEvent(
                        aggregate_type="PreparationReview",
                        aggregate_id=latest.review_id,
                        aggregate_revision=revision,
                        event_type="PreparationCorrectionAdded",
                        payload={
                            "review_id": str(latest.review_id),
                            "correction_revision": revision,
                            "correction_code": command.correction_code,
                            "draft_version": corrected_version,
                        },
                    ),
                ),
            )
        return self._outcome(
            aggregate_type="PreparationReview",
            aggregate_id=latest.review_id,
            revision=revision,
            event_type="PreparationCorrectionAdded",
            payload={
                "review_id": str(latest.review_id),
                "correction_revision": revision,
                "correction_code": command.correction_code,
                "draft_version": corrected_version,
            },
            result_code="PREPARATION_CORRECTION_ADDED",
        )

    def _current_response_plan(
        self,
        *,
        session: Session,
        package: PreparationPackageRecord,
        command: _ResponsePlanFields,
        context: CommandContext,
    ) -> tuple[PreparationResponsePlanRecord, dict[UUID, PreparationResponsePlanFact]]:
        plan = session.scalar(
            sa.select(PreparationResponsePlanRecord)
            .where(
                PreparationResponsePlanRecord.tenant_id == context.tenant_id,
                PreparationResponsePlanRecord.package_id == package.id,
            )
            .order_by(PreparationResponsePlanRecord.version.desc())
            .limit(1)
        )
        if plan is None:
            raise CommandExecutionError("RESPONSE_PLAN_REQUIRED")
        if plan.state != "SOURCES_CURRENT" or plan.dce_version_id != package.dce_version_id:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        if self._source_reader is None:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        plan_items = plan.content_json.get("items")
        if not isinstance(plan_items, list):
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        requirement_ids = {UUID(item["requirement_id"]) for item in plan_items}
        proposal_ids = {
            UUID(item["source_proposal_id"])
            for item in plan_items
            if item.get("source_proposal_id") is not None
        }
        sections = {item["section_code"] for item in plan_items}
        if set(command.section_codes) != sections or {str(ref) for ref in command.source_refs} != {
            str(proposal_id) for proposal_id in proposal_ids
        }:
            raise CommandExecutionError("RESPONSE_PLAN_MISMATCH")
        sources = self._source_reader.read(
            session=session,
            tenant_id=package.tenant_id,
            case_id=package.case_id,
            assignment_id=package.assignment_id,
            dce_version_id=package.dce_version_id,
            requirement_ids=requirement_ids,
            proposal_ids=proposal_ids,
            evaluated_at=context.received_at,
        )
        if not sources.dce_current:
            raise CommandExecutionError("VERSION_CONFLICT")
        if len(sources.requirement_states) != len(requirement_ids):
            raise CommandExecutionError("VERSION_CONFLICT")
        if len(sources.facts) != len(proposal_ids):
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        if any(state != "CONFIRMED" for state in sources.requirement_states.values()):
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        evidence_manifest = {
            source["source_proposal_id"]: source for source in plan.source_evidence_json
        }
        for item in plan_items:
            if item.get("source_proposal_id") is None:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            proposal_id = UUID(item["source_proposal_id"])
            fact = sources.facts.get(proposal_id)
            if fact is None:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            if fact.requirement_id != UUID(item["requirement_id"]) or fact.task_id is not None:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            if fact.validity_state == "EXPIRED" or fact.evidence_state == "EXPIRED":
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            if (
                fact.validity_state != "CURRENT"
                or fact.evidence_state != "CURRENT"
                or item.get("source_validity_state") != "CURRENT"
                or item.get("source_evidence_state") != "CURRENT"
            ):
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            if item.get("source_capability_version_id") != str(fact.capability_version_id):
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            stored = evidence_manifest.get(str(proposal_id))
            if stored is None:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            current_proofs = [
                {"document_id": str(document_id), "sha256": sha256}
                for document_id, sha256 in fact.proof_refs
            ]
            if stored["proofs"] != current_proofs:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        try:
            content_bytes = json.dumps(
                plan.content_json, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            evidence_bytes = json.dumps(
                plan.source_evidence_json,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError) as error:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN") from error
        if (
            not _SHA256_RE.fullmatch(plan.plan_sha256)
            or hashlib.sha256(content_bytes).hexdigest() != plan.plan_sha256
            or not _SHA256_RE.fullmatch(plan.source_evidence_sha256)
            or hashlib.sha256(evidence_bytes).hexdigest() != plan.source_evidence_sha256
        ):
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        return plan, sources.facts

    def _draft(
        self,
        *,
        session: Session,
        command: CreateTechnicalResponseDraftCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.COLLABORATEUR.value:
            raise CommandExecutionError("COLLABORATOR_REQUIRED")
        package = self._package(session=session, context=context, package_id=command.package_id)
        if package.aggregate_revision != command.expected_package_revision:
            raise CommandExecutionError("VERSION_CONFLICT")
        if any(code not in _ALLOWED_SECTION_CODES for code in command.section_codes):
            raise CommandExecutionError("SECTION_CODE_INVALID")
        document = session.scalar(
            sa.select(GeneratedTechnicalDocumentRecord).where(
                GeneratedTechnicalDocumentRecord.tenant_id == context.tenant_id,
                GeneratedTechnicalDocumentRecord.id == command.source_document_id,
                GeneratedTechnicalDocumentRecord.package_id == package.id,
            )
        )
        if document is None:
            raise CommandExecutionError("SOURCE_DOCUMENT_NOT_FOUND")
        if document.document_kind != "TECHNICAL_RESPONSE" or document.state != "GENERATED":
            raise CommandExecutionError("SOURCE_DOCUMENT_NOT_FOUND")
        version = (
            session.scalar(
                sa.select(
                    sa.func.coalesce(sa.func.max(TechnicalResponseDraftRecord.version), 0)
                ).where(
                    TechnicalResponseDraftRecord.tenant_id == context.tenant_id,
                    TechnicalResponseDraftRecord.draft_id == command.draft_id,
                )
            )
            + 1
        )
        refs = sorted({str(ref) for ref in command.source_refs})
        sections = sorted(set(command.section_codes))
        response_plan, source_facts = self._current_response_plan(
            session=session,
            package=package,
            command=command,
            context=context,
        )
        proof_counts = self._reread_response_plan_sources(
            session=session,
            plan=response_plan,
            source_facts=source_facts,
            tenant_id=package.tenant_id,
        )
        content = self._build_response_plan_content(
            session=session,
            plan=response_plan,
            source_facts=source_facts,
            proof_counts=proof_counts,
            tenant_id=package.tenant_id,
            draft_version=version,
        ).encode("utf-8")
        if len(content) > _MAX_RESPONSE_DRAFT_BYTES:
            raise CommandExecutionError("RESPONSE_DRAFT_TOO_LARGE")
        if contains_forbidden_text(content.decode("utf-8")):
            raise CommandExecutionError("FINANCIAL_DATA_FORBIDDEN")
        storage_key = (
            f"technical-response-drafts/{context.tenant_id}/{package.id}/"
            f"{command.draft_id}/{version}.md"
        )
        content_sha256 = self._storage.write(storage_key=storage_key, content=content)
        session.add(
            TechnicalResponseDraftRecord(
                id=command.command_id,
                tenant_id=context.tenant_id,
                draft_id=command.draft_id,
                package_id=package.id,
                source_document_id=document.id,
                response_plan_id=response_plan.plan_id,
                response_plan_version=response_plan.version,
                version=version,
                state="DRAFT",
                section_codes_json=sections,
                source_refs_json=refs,
                responsible_role=command.responsible_role,
                content_sha256=content_sha256,
                storage_key=storage_key,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        package.aggregate_revision += 1
        package.state = "IN_PREPARATION"
        return self._outcome(
            aggregate_type="TechnicalResponseDraft",
            aggregate_id=command.draft_id,
            revision=version,
            event_type="TechnicalResponseDraftCreated",
            payload={
                "draft_id": str(command.draft_id),
                "version": version,
                "package_id": str(package.id),
                "state": "DRAFT",
            },
            result_code="TECHNICAL_RESPONSE_DRAFT_CREATED",
        )

    def _reread_response_plan_sources(
        self,
        *,
        session: Session,
        plan: PreparationResponsePlanRecord,
        source_facts: dict[UUID, PreparationResponsePlanFact],
        tenant_id: UUID,
    ) -> dict[UUID, int]:
        if self._source_storage is None:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        proof_hashes: dict[UUID, str] = {}
        proof_counts: dict[UUID, int] = {}
        try:
            for item in plan.content_json["items"]:
                proposal_id = UUID(item["source_proposal_id"])
                fact = source_facts.get(proposal_id)
                stored = next(
                    source
                    for source in plan.source_evidence_json
                    if source.get("source_proposal_id") == str(proposal_id)
                )
                if fact is None or not stored["proofs"]:
                    raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
                proof_counts[proposal_id] = len(stored["proofs"])
                current_refs = {
                    str(document_id): source_sha256
                    for document_id, source_sha256 in fact.proof_refs
                }
                stored_refs = {proof["document_id"]: proof["sha256"] for proof in stored["proofs"]}
                if current_refs != stored_refs:
                    raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
                for proof in stored["proofs"]:
                    document_id = UUID(proof["document_id"])
                    source_sha256 = proof["sha256"]
                    if not _SHA256_RE.fullmatch(source_sha256):
                        raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
                    if document_id in proof_hashes and proof_hashes[document_id] != source_sha256:
                        raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
                    proof_hashes[document_id] = source_sha256
        except CommandExecutionError:
            raise
        except (KeyError, TypeError, ValueError, StopIteration) as error:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN") from error

        if not proof_hashes:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        rows = session.execute(
            sa.select(EnterpriseDocumentRecord, EnterpriseDocumentUploadRecord)
            .join(
                EnterpriseDocumentUploadRecord,
                sa.and_(
                    EnterpriseDocumentUploadRecord.tenant_id == tenant_id,
                    EnterpriseDocumentUploadRecord.id == EnterpriseDocumentRecord.storage_object_id,
                    EnterpriseDocumentUploadRecord.document_id == EnterpriseDocumentRecord.id,
                    EnterpriseDocumentUploadRecord.company_id
                    == EnterpriseDocumentRecord.company_id,
                    EnterpriseDocumentUploadRecord.document_kind
                    == EnterpriseDocumentRecord.document_kind,
                    EnterpriseDocumentUploadRecord.sha256 == EnterpriseDocumentRecord.sha256,
                    EnterpriseDocumentUploadRecord.state == "CLEAN",
                    EnterpriseDocumentUploadRecord.scan_verdict == "CLEAN",
                ),
            )
            .where(
                EnterpriseDocumentRecord.tenant_id == tenant_id,
                EnterpriseDocumentRecord.id.in_(proof_hashes),
                EnterpriseDocumentRecord.verification_status == "VALIDATED",
            )
        ).all()
        if len(rows) != len(proof_hashes):
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        total_bytes = 0
        for document, upload in rows:
            source_sha256 = proof_hashes[document.id]
            byte_size = upload.actual_byte_size
            if (
                byte_size is None
                or byte_size <= 0
                or byte_size > _MAX_RESPONSE_PLAN_SOURCE_BYTES - total_bytes
                or upload.sha256 != source_sha256
                or document.sha256 != source_sha256
            ):
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            try:
                reread_size, reread_sha256 = self._source_storage.read_digest(
                    storage_key=upload.storage_key,
                    max_bytes=_MAX_RESPONSE_PLAN_SOURCE_BYTES - total_bytes,
                )
            except Exception as error:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN") from error
            if reread_size != byte_size or reread_sha256 != source_sha256:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            total_bytes += reread_size
        return proof_counts

    @staticmethod
    def _build_response_plan_content(
        *,
        session: Session,
        plan: PreparationResponsePlanRecord,
        source_facts: dict[UUID, PreparationResponsePlanFact],
        proof_counts: dict[UUID, int],
        tenant_id: UUID,
        draft_version: int,
    ) -> str:
        capability_version_ids = {fact.capability_version_id for fact in source_facts.values()}
        rows = session.execute(
            sa.select(
                EnterpriseCapabilityVersionRecord.id,
                EnterpriseCapabilityRecord.name,
                EnterpriseCapabilityVersionRecord.title,
                EnterpriseCapabilityVersionRecord.version_number,
            )
            .join(
                EnterpriseCapabilityRecord,
                sa.and_(
                    EnterpriseCapabilityRecord.tenant_id == tenant_id,
                    EnterpriseCapabilityRecord.id
                    == EnterpriseCapabilityVersionRecord.capability_id,
                ),
            )
            .where(
                EnterpriseCapabilityVersionRecord.tenant_id == tenant_id,
                EnterpriseCapabilityVersionRecord.id.in_(capability_version_ids),
            )
        ).all()
        capabilities = {row.id: row for row in rows}
        if len(capabilities) != len(capability_version_ids):
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
        items: list[ResponsePlanDraftItem] = []
        for item in plan.content_json["items"]:
            proposal_id = UUID(item["source_proposal_id"])
            fact = source_facts.get(proposal_id)
            capability = capabilities.get(fact.capability_version_id) if fact is not None else None
            if capability is None or proposal_id not in proof_counts:
                raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
            items.append(
                ResponsePlanDraftItem(
                    requirement_id=UUID(item["requirement_id"]),
                    section_code=item["section_code"],
                    capability_name=capability.name,
                    capability_title=capability.title,
                    capability_version_number=capability.version_number,
                    verified_source_count=proof_counts[proposal_id],
                )
            )
        try:
            return build_response_plan_draft(
                plan_version=plan.version,
                draft_version=draft_version,
                items=tuple(items),
            )
        except ValueError as error:
            raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN") from error

    @staticmethod
    def _outcome(
        *,
        aggregate_type: str,
        aggregate_id: UUID,
        revision: int,
        event_type: str,
        payload: dict[str, object],
        result_code: str,
    ) -> HandlerOutcome:
        return HandlerOutcome(
            result_code=result_code,
            aggregate_refs=(
                {
                    "aggregate_type": aggregate_type,
                    "aggregate_id": str(aggregate_id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type=aggregate_type,
                    aggregate_id=aggregate_id,
                    aggregate_revision=revision,
                    event_type=event_type,
                    payload=payload,
                ),
            ),
        )


def preparation_review_handlers(
    *,
    storage: GeneratedDocumentStorage,
    source_reader: PreparationResponsePlanSourceReader | None = None,
    source_storage: PreparationPrivateSourceDigestReader | None = None,
) -> dict[str, PreparationReviewHandler]:
    handler = PreparationReviewHandler(
        storage=storage,
        source_reader=source_reader,
        source_storage=source_storage,
    )
    return {command_type: handler for command_type in _REVIEW_COMMANDS}
