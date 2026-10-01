from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.modules.pricing.application.partner_offer_scope_review_commands import (
    RecordPartnerOfferScopeReviewCommand,
)
from app.modules.pricing.domain.partner_offer_scope_review import (
    PartnerOfferScopeFact,
    build_partner_offer_scope_review,
)
from app.modules.pricing.infrastructure.models.partner_offer_scope_review import (
    PartnerOfferScopeReviewOfferRecord,
    PartnerOfferScopeReviewRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandExecutionError,
    CommandHandler,
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


class RecordPartnerOfferScopeReviewHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordPartnerOfferScopeReviewCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value or context.membership_id is None:
            raise CommandExecutionError("FINANCIAL_PRIVATE_FORBIDDEN")
        tenant_id = UUID(str(context.tenant_id))
        if (
            session.scalar(
                sa.select(CaseRecord.id)
                .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)
                .with_for_update()
            )
            is None
        ):
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if (
            session.scalar(
                sa.select(PartnerOfferScopeReviewRecord.id).where(
                    PartnerOfferScopeReviewRecord.id == command.review_id
                )
            )
            is not None
        ):
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_ID_REUSED")
        receipt_ids = tuple(item.receipt_event_id for item in command.offers)
        if len(set(receipt_ids)) != len(receipt_ids):
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_DUPLICATE_RECEIPT")
        if (
            session.scalar(
                sa.select(PartnerOfferScopeReviewRecord.id).where(
                    PartnerOfferScopeReviewRecord.id == command.review_id
                )
            )
            is not None
        ):
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_ID_REUSED")

        current_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(PartnerOfferScopeReviewRecord.revision), 0)
            ).where(
                PartnerOfferScopeReviewRecord.tenant_id == tenant_id,
                PartnerOfferScopeReviewRecord.case_id == command.case_id,
                PartnerOfferScopeReviewRecord.comparison_id == command.comparison_id,
            )
        )
        if current_revision != command.expected_revision:
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_VERSION_CONFLICT")

        receipt_rows = session.scalars(
            sa.select(CasePartnerEventRecord).where(
                CasePartnerEventRecord.tenant_id == tenant_id,
                CasePartnerEventRecord.case_id == command.case_id,
                CasePartnerEventRecord.event_id.in_(receipt_ids),
                CasePartnerEventRecord.event_type == "RECEIVED",
            )
        ).all()
        if len(receipt_rows) != len(receipt_ids):
            raise CommandExecutionError("PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN")
        receipt_by_id = {row.event_id: row for row in receipt_rows}
        if len({row.partner_id for row in receipt_rows}) != len(receipt_rows):
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_DUPLICATE_PARTNER")

        latest_receipt_rows = session.execute(
            sa.select(
                CasePartnerEventRecord.partner_id,
                sa.func.max(CasePartnerEventRecord.revision),
            )
            .where(
                CasePartnerEventRecord.tenant_id == tenant_id,
                CasePartnerEventRecord.case_id == command.case_id,
                CasePartnerEventRecord.partner_id.in_(
                    tuple(row.partner_id for row in receipt_rows)
                ),
                CasePartnerEventRecord.event_type == "RECEIVED",
            )
            .group_by(CasePartnerEventRecord.partner_id)
        ).all()
        latest_revisions = {partner_id: revision for partner_id, revision in latest_receipt_rows}
        if any(row.revision != latest_revisions.get(row.partner_id) for row in receipt_rows):
            raise CommandExecutionError("PARTNER_RECEIPT_VERSION_CONFLICT")

        if current_revision:
            current_review_id = session.scalar(
                sa.select(PartnerOfferScopeReviewRecord.id).where(
                    PartnerOfferScopeReviewRecord.tenant_id == tenant_id,
                    PartnerOfferScopeReviewRecord.case_id == command.case_id,
                    PartnerOfferScopeReviewRecord.comparison_id == command.comparison_id,
                    PartnerOfferScopeReviewRecord.revision == current_revision,
                )
            )
            prior_receipt_ids = set(
                session.scalars(
                    sa.select(PartnerOfferScopeReviewOfferRecord.receipt_event_id).where(
                        PartnerOfferScopeReviewOfferRecord.tenant_id == tenant_id,
                        PartnerOfferScopeReviewOfferRecord.case_id == command.case_id,
                        PartnerOfferScopeReviewOfferRecord.review_id == current_review_id,
                    )
                ).all()
            )
            if prior_receipt_ids != set(receipt_ids):
                raise CommandExecutionError("PARTNER_SCOPE_REVIEW_MEMBER_SET_CONFLICT")

        facts = tuple(
            PartnerOfferScopeFact(
                receipt_event_id=item.receipt_event_id,
                inclusion_state=item.inclusion_state,
                included_scope_note=item.included_scope_note,
                exclusions_review_state=item.exclusions_review_state,
                transport_state=item.transport_state,
                transport_note=item.transport_note,
            )
            for item in command.offers
        )
        try:
            review = build_partner_offer_scope_review(
                comparison_id=command.comparison_id,
                decision=command.decision,
                rationale=command.rationale,
                offers=facts,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error

        if review.decision == "SAME_SCOPE_CONFIRMED" and any(
            receipt_by_id[item.receipt_event_id].exclusions_state != "DECLARED"
            for item in review.offers
        ):
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_EXCLUSIONS_UNKNOWN")
        if any(
            item.exclusions_review_state == "REVIEWED"
            and receipt_by_id[item.receipt_event_id].exclusions_state != "DECLARED"
            for item in review.offers
        ):
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_EXCLUSIONS_UNKNOWN")

        revision = current_revision + 1
        session.add(
            PartnerOfferScopeReviewRecord(
                id=command.review_id,
                tenant_id=tenant_id,
                case_id=command.case_id,
                comparison_id=command.comparison_id,
                revision=revision,
                decision=review.decision,
                rationale=review.rationale,
                actor_id=UUID(str(context.actor_id)),
                membership_id=UUID(str(context.membership_id)),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        session.flush()
        session.add_all(
            PartnerOfferScopeReviewOfferRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                case_id=command.case_id,
                review_id=command.review_id,
                receipt_event_id=offer.receipt_event_id,
                inclusion_state=offer.inclusion_state,
                included_scope_note=offer.included_scope_note,
                exclusions_review_state=offer.exclusions_review_state,
                transport_state=offer.transport_state,
                transport_note=offer.transport_note,
            )
            for offer in review.offers
        )
        return HandlerOutcome(
            result_code="PARTNER_SCOPE_REVIEW_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "PARTNER_OFFER_SCOPE_REVIEW",
                    "aggregate_id": str(command.comparison_id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="PARTNER_OFFER_SCOPE_REVIEW",
                    aggregate_id=command.comparison_id,
                    aggregate_revision=revision,
                    event_type="PARTNER_OFFER_SCOPE_REVIEW_RECORDED",
                    payload={"case_id": str(command.case_id), "review_id": str(command.review_id)},
                ),
            ),
        )


def partner_offer_scope_review_handlers() -> dict[str, CommandHandler]:
    return {
        RecordPartnerOfferScopeReviewCommand.command_type: RecordPartnerOfferScopeReviewHandler(),
    }


@dataclass(frozen=True, slots=True)
class PartnerOfferScopeReviewOfferView:
    receipt_event_id: UUID
    partner_id: UUID
    partner_kind: str
    partner_label: str
    source_locator: str
    source_rationale: str
    validity_current: str
    exclusions_state: str
    exclusions: tuple[str, ...]
    inclusion_state: str
    included_scope_note: str | None
    exclusions_review_state: str
    transport_state: str
    transport_note: str | None
    receipt_is_current: bool


@dataclass(frozen=True, slots=True)
class PartnerOfferScopeReviewView:
    review_id: UUID
    comparison_id: UUID
    revision: int
    decision: str
    rationale: str
    actor_id: UUID
    created_at: datetime
    offers: tuple[PartnerOfferScopeReviewOfferView, ...]


@dataclass(frozen=True, slots=True)
class PartnerOfferScopeReviewList:
    case_id: UUID
    reviews: tuple[PartnerOfferScopeReviewView, ...]


class PartnerOfferScopeReviewService:
    def __init__(
        self,
        *,
        dispatcher: CommandDispatcher,
        session_factory: sessionmaker[Session],
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._policy = policy

    def list_for_case(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> PartnerOfferScopeReviewList:
        self._authorize(actor=actor, case_id=case_id, action=Capability.PRICING_READ, now=now)
        with self._session_factory() as session:
            reviews = session.scalars(
                sa.select(PartnerOfferScopeReviewRecord)
                .where(
                    PartnerOfferScopeReviewRecord.tenant_id == actor.tenant_id,
                    PartnerOfferScopeReviewRecord.case_id == case_id,
                )
                .order_by(
                    PartnerOfferScopeReviewRecord.created_at.asc(),
                    PartnerOfferScopeReviewRecord.comparison_id.asc(),
                    PartnerOfferScopeReviewRecord.revision.asc(),
                )
            ).all()
            review_ids = [row.id for row in reviews]
            offer_rows = (
                session.scalars(
                    sa.select(PartnerOfferScopeReviewOfferRecord)
                    .where(
                        PartnerOfferScopeReviewOfferRecord.tenant_id == actor.tenant_id,
                        PartnerOfferScopeReviewOfferRecord.case_id == case_id,
                        PartnerOfferScopeReviewOfferRecord.review_id.in_(review_ids),
                    )
                    .order_by(PartnerOfferScopeReviewOfferRecord.receipt_event_id.asc())
                ).all()
                if review_ids
                else []
            )
            receipt_ids = [row.receipt_event_id for row in offer_rows]
            receipts = (
                session.scalars(
                    sa.select(CasePartnerEventRecord).where(
                        CasePartnerEventRecord.tenant_id == actor.tenant_id,
                        CasePartnerEventRecord.case_id == case_id,
                        CasePartnerEventRecord.event_id.in_(receipt_ids),
                    )
                ).all()
                if receipt_ids
                else []
            )
            receipt_by_id = {row.event_id: row for row in receipts}
            partner_ids = tuple({row.partner_id for row in receipts})
            latest_receipt_rows = (
                session.execute(
                    sa.select(
                        CasePartnerEventRecord.partner_id,
                        sa.func.max(CasePartnerEventRecord.revision),
                    )
                    .where(
                        CasePartnerEventRecord.tenant_id == actor.tenant_id,
                        CasePartnerEventRecord.case_id == case_id,
                        CasePartnerEventRecord.partner_id.in_(partner_ids),
                        CasePartnerEventRecord.event_type == "RECEIVED",
                    )
                    .group_by(CasePartnerEventRecord.partner_id)
                ).all()
                if partner_ids
                else []
            )
            latest_revisions = {
                partner_id: revision for partner_id, revision in latest_receipt_rows
            }
            offers_by_review: dict[UUID, list[PartnerOfferScopeReviewOfferView]] = {}
            for row in offer_rows:
                receipt = receipt_by_id[row.receipt_event_id]
                offers_by_review.setdefault(row.review_id, []).append(
                    PartnerOfferScopeReviewOfferView(
                        receipt_event_id=receipt.event_id,
                        partner_id=receipt.partner_id,
                        partner_kind=receipt.partner_kind,
                        partner_label=receipt.partner_label,
                        source_locator=receipt.source_locator,
                        source_rationale=receipt.rationale,
                        validity_current=(
                            "UNKNOWN"
                            if receipt.valid_until is None
                            else "VALID"
                            if receipt.valid_until >= now.date()
                            else "EXPIRED"
                        ),
                        exclusions_state=receipt.exclusions_state,
                        exclusions=tuple(receipt.exclusions_json),
                        inclusion_state=row.inclusion_state,
                        included_scope_note=row.included_scope_note,
                        exclusions_review_state=row.exclusions_review_state,
                        transport_state=row.transport_state,
                        transport_note=row.transport_note,
                        receipt_is_current=(
                            receipt.revision == latest_revisions.get(receipt.partner_id)
                        ),
                    )
                )
            return PartnerOfferScopeReviewList(
                case_id=case_id,
                reviews=tuple(
                    PartnerOfferScopeReviewView(
                        review_id=row.id,
                        comparison_id=row.comparison_id,
                        revision=row.revision,
                        decision=row.decision,
                        rationale=row.rationale,
                        actor_id=row.actor_id,
                        created_at=row.created_at,
                        offers=tuple(offers_by_review.get(row.id, ())),
                    )
                    for row in reviews
                ),
            )

    def record(
        self,
        *,
        actor: ActorContext,
        command: RecordPartnerOfferScopeReviewCommand,
        now: datetime,
    ) -> DispatchResult:
        self._authorize(
            actor=actor, case_id=command.case_id, action=Capability.PRICING_WRITE, now=now
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
                correlation_id=actor.correlation_id,
            ),
        )

    def _authorize(self, *, actor: ActorContext, case_id: UUID, action: str, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("FINANCIAL_PRIVATE_FORBIDDEN")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=action,
                resource=AuthorizationResource(
                    resource_type="PARTNER_OFFER_SCOPE_REVIEW",
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
