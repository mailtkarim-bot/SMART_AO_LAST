from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import NAMESPACE_URL, UUID, uuid5

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.application.commands import CreateCaseCommand
from app.modules.case.application.handlers import _SCOPE_KIND_MAP, CreateCaseHandler, _scope_json
from app.modules.case.domain.case import CaseScope
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.opportunity.application.boamp_qualification import PatronBoampObservationService
from app.modules.opportunity.infrastructure.boamp_qualification_repository import lock_boamp_notice
from app.modules.opportunity.infrastructure.observation_models import (
    BoampOpportunityObservationRecord,
    BoampOpportunityQualificationRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandExecutionError,
    DispatchResult,
    canonical_request_hash,
)
from app.platform.persistence.models import CommandReceiptRecord


@dataclass(frozen=True, slots=True)
class BoampCaseCreationCommand:
    observation_id: UUID
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None


class BoampCaseCreationService:
    """Turns a human-qualified public signal into one normal Case command."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        dispatcher: CommandDispatcher,
    ) -> None:
        self._session_factory = session_factory
        self._dispatcher = dispatcher

    def create(
        self,
        *,
        context: CommandContext,
        command: BoampCaseCreationCommand,
        now: datetime,
    ) -> DispatchResult:
        if context.actor_kind != "PATRON_ADMIN":
            raise PermissionError("BOAMP_CASE_CREATION_PATRON_REQUIRED")
        with self._session_factory() as session:
            observation = session.scalar(
                sa.select(BoampOpportunityObservationRecord).where(
                    BoampOpportunityObservationRecord.tenant_id == context.tenant_id,
                    BoampOpportunityObservationRecord.id == command.observation_id,
                )
            )
            receipt = session.scalar(
                sa.select(CommandReceiptRecord).where(
                    CommandReceiptRecord.tenant_id == context.tenant_id,
                    CommandReceiptRecord.actor_id == context.actor_id,
                    CommandReceiptRecord.command_type == "CreateCase",
                    CommandReceiptRecord.idempotency_key == command.idempotency_key,
                )
            )
        if observation is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        with self._session_factory() as session:
            PatronBoampObservationService._require_patron_membership(
                session=session,
                tenant_id=UUID(str(context.tenant_id)),
                actor_id=UUID(str(context.actor_id)),
                actor_kind=context.actor_kind,
            )
        case_id = uuid5(
            NAMESPACE_URL,
            f"smart-ao:case:{context.tenant_id}:{context.actor_id}:{command.idempotency_key}",
        )
        title = (observation.title or f"Avis BOAMP {observation.source_notice_id}").strip()[:240]
        description = _description(observation)
        origin_rationale = (
            f"Signal BOAMP {observation.source_notice_id} qualifié par décision humaine; "
            f"score public figé {observation.score}/100 ({observation.score_version})."
        )[:2_000]
        creation = CreateCaseCommand(
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
            case_id=case_id,
            title=title,
            object_description=description,
            scope_kind="CUSTOM",
            scope_justification=(
                "Périmètre issu d’un signal public : confirmer les lots et pièces du DCE "
                "avant chiffrage ou décision."
            ),
            origin_kind="OPPORTUNITY",
            origin_rationale=origin_rationale,
            origin_reference_id=observation.id,
        )
        # Preserve receipts created before tenant/actor scoped Case identities.
        legacy = creation.model_copy(
            update={"case_id": uuid5(NAMESPACE_URL, f"smart-ao:case:{command.idempotency_key}")}
        )
        if receipt is not None and receipt.request_hash == canonical_request_hash(legacy):
            creation = legacy
        try:
            return self._dispatcher.dispatch(command=creation, context=context)
        except CommandExecutionError as error:
            if (
                isinstance(error.__cause__, ValueError)
                and str(error.__cause__) == "BOAMP_QUALIFICATION_REQUIRED"
            ):
                raise ValueError("BOAMP_QUALIFICATION_REQUIRED") from error
            raise


class BoampAwareCreateCaseHandler(CreateCaseHandler):
    """Keep the generic Case command/receipt contract; guard BOAMP origins atomically."""

    @staticmethod
    def _observation(session, command, context):
        if command.origin_kind != "OPPORTUNITY":
            return None
        return session.scalar(
            sa.select(BoampOpportunityObservationRecord).where(
                BoampOpportunityObservationRecord.tenant_id == context.tenant_id,
                BoampOpportunityObservationRecord.id == command.origin_reference_id,
            )
        )

    def authorize_context(self, *, session, command, context):
        if self._observation(session, command, context) is not None:
            PatronBoampObservationService._require_patron_membership(
                session=session,
                tenant_id=UUID(str(context.tenant_id)),
                actor_id=UUID(str(context.actor_id)),
                actor_kind=context.actor_kind,
            )

    def execute(self, *, session, command, context):
        observation = self._observation(session, command, context)
        if observation is not None:
            lock_boamp_notice(session, observation)
            qualification = session.scalar(
                sa.select(BoampOpportunityQualificationRecord)
                .where(
                    BoampOpportunityQualificationRecord.tenant_id == context.tenant_id,
                    BoampOpportunityQualificationRecord.observation_id == observation.id,
                )
                .order_by(
                    BoampOpportunityQualificationRecord.created_at.desc(),
                    BoampOpportunityQualificationRecord.id.desc(),
                )
                .limit(1)
            )
            if qualification is None or qualification.decision != "QUALIFIED":
                raise ValueError("BOAMP_QUALIFICATION_REQUIRED")
            scope = _scope_json(
                CaseScope(
                    kind=_SCOPE_KIND_MAP[command.scope_kind],
                    lot_numbers=command.lot_numbers,
                    tranche_reference=command.tranche_reference,
                    variant_reference=command.variant_reference,
                    source_justification=command.scope_justification,
                )
            )
            prior = session.scalars(
                sa.select(CaseRecord)
                .join(
                    BoampOpportunityObservationRecord,
                    sa.and_(
                        BoampOpportunityObservationRecord.tenant_id == CaseRecord.tenant_id,
                        BoampOpportunityObservationRecord.id == CaseRecord.origin_reference_id,
                    ),
                )
                .where(
                    CaseRecord.tenant_id == context.tenant_id,
                    CaseRecord.business_origin == "OPPORTUNITY",
                    CaseRecord.lifecycle != "ARCHIVED",
                    BoampOpportunityObservationRecord.source == observation.source,
                    BoampOpportunityObservationRecord.source_notice_id
                    == observation.source_notice_id,
                )
            ).all()
            keys = ("kind", "lot_numbers", "tranche_reference", "variant_reference")
            unknown_scope = command.scope_kind == "CUSTOM" and not (
                command.lot_numbers or command.tranche_reference or command.variant_reference
            )
            if any(
                unknown_scope
                or (
                    row.scope_json.get("kind") == "CUSTOM_SOURCED_SCOPE"
                    and not any(row.scope_json.get(k) for k in keys[1:])
                )
                or all(row.scope_json.get(k) == scope.get(k) for k in keys)
                for row in prior
            ):
                raise ValueError("DUPLICATE_FUNCTIONAL_IDENTITY")
            audit = (
                f" Qualification {qualification.id} : "
                f"{qualification.decision}/{qualification.reason_code}. "
                f"Observation {observation.id}; empreinte {observation.fingerprint_sha256}."
            )
            command = command.model_copy(
                update={
                    "origin_rationale": (command.origin_rationale or "")[: 2000 - len(audit)]
                    + audit
                }
            )

        return super().execute(session=session, command=command, context=context)


def _description(observation: BoampOpportunityObservationRecord) -> str:
    departments = ", ".join(observation.department_codes) or "non précisés"
    market_types = ", ".join(observation.market_types) or "non précisés"
    deadline = (
        observation.response_deadline.isoformat()
        if observation.response_deadline
        else "non précisée"
    )
    return (
        f"Observation publique BOAMP {observation.source_notice_id}. "
        f"Départements : {departments}. Types de marché : {market_types}. "
        f"Date limite publiée : {deadline}. "
        "Description contractuelle à compléter après réception et contrôle du DCE."
    )[:10_000]
