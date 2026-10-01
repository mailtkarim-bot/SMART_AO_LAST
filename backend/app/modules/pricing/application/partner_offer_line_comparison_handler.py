from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.modules.pricing.application.partner_offer_line_comparison_commands import (
    RecordPartnerOfferLineComparisonCommand,
)
from app.modules.pricing.domain.partner_offer_line_comparison import (
    PartnerOfferLineGroup,
    PartnerOfferLineMember,
    build_partner_offer_line_comparison,
)
from app.modules.pricing.infrastructure.models.partner_offer_line_comparison import (
    PartnerOfferLineComparisonRecord,
    PartnerOfferLineGroupRecord,
    PartnerOfferLineMemberRecord,
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


class RecordPartnerOfferLineComparisonHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordPartnerOfferLineComparisonCommand,
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
        if session.scalar(
            sa.select(PartnerOfferLineComparisonRecord.id).where(
                PartnerOfferLineComparisonRecord.id == command.record_id
            )
        ) is not None:
            raise CommandExecutionError("PARTNER_OFFER_LINE_COMPARISON_ID_REUSED")

        scope_review = session.scalar(
            sa.select(PartnerOfferScopeReviewRecord).where(
                PartnerOfferScopeReviewRecord.tenant_id == tenant_id,
                PartnerOfferScopeReviewRecord.case_id == command.case_id,
                PartnerOfferScopeReviewRecord.id == command.scope_review_id,
            )
        )
        if scope_review is None:
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_NOT_FOUND_OR_FORBIDDEN")
        latest_scope_revision = session.scalar(
            sa.select(sa.func.max(PartnerOfferScopeReviewRecord.revision)).where(
                PartnerOfferScopeReviewRecord.tenant_id == tenant_id,
                PartnerOfferScopeReviewRecord.case_id == command.case_id,
                PartnerOfferScopeReviewRecord.comparison_id == scope_review.comparison_id,
            )
        )
        if scope_review.revision != latest_scope_revision:
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_VERSION_CONFLICT")
        if scope_review.decision != "SAME_SCOPE_CONFIRMED":
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_NOT_CONFIRMED")

        parent_receipt_ids = set(
            session.scalars(
                sa.select(PartnerOfferScopeReviewOfferRecord.receipt_event_id).where(
                    PartnerOfferScopeReviewOfferRecord.tenant_id == tenant_id,
                    PartnerOfferScopeReviewOfferRecord.case_id == command.case_id,
                    PartnerOfferScopeReviewOfferRecord.review_id == command.scope_review_id,
                )
            ).all()
        )
        if not parent_receipt_ids:
            raise CommandExecutionError("PARTNER_SCOPE_REVIEW_NOT_FOUND_OR_FORBIDDEN")

        current_revision = session.scalar(
            sa.select(sa.func.coalesce(sa.func.max(PartnerOfferLineComparisonRecord.revision), 0))
            .where(
                PartnerOfferLineComparisonRecord.tenant_id == tenant_id,
                PartnerOfferLineComparisonRecord.case_id == command.case_id,
                PartnerOfferLineComparisonRecord.comparison_id == command.comparison_id,
            )
        )
        if current_revision != command.expected_revision:
            raise CommandExecutionError("PARTNER_OFFER_LINE_COMPARISON_VERSION_CONFLICT")

        domain_groups = tuple(
            PartnerOfferLineGroup(
                group_id=group.group_id,
                disposition=group.disposition,
                rationale=group.rationale,
                members=tuple(
                    PartnerOfferLineMember(
                        receipt_event_id=member.receipt_event_id,
                        line_locator_state=member.line_locator_state,
                        line_locator=member.line_locator,
                        item_reference_state=member.item_reference_state,
                        item_reference=member.item_reference,
                        designation_state=member.designation_state,
                        designation=member.designation,
                        unit_state=member.unit_state,
                        unit=member.unit,
                        quantity_state=member.quantity_state,
                        quantity=member.quantity,
                    )
                    for member in group.members
                ),
            )
            for group in command.groups
        )
        try:
            comparison = build_partner_offer_line_comparison(
                comparison_id=command.comparison_id,
                scope_review_id=command.scope_review_id,
                groups=domain_groups,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error

        for group in comparison.groups:
            if {member.receipt_event_id for member in group.members} != parent_receipt_ids:
                raise CommandExecutionError("PARTNER_OFFER_LINE_SCOPE_MEMBER_SET_CONFLICT")

        if current_revision:
            prior = session.scalar(
                sa.select(PartnerOfferLineComparisonRecord).where(
                    PartnerOfferLineComparisonRecord.tenant_id == tenant_id,
                    PartnerOfferLineComparisonRecord.case_id == command.case_id,
                    PartnerOfferLineComparisonRecord.comparison_id == command.comparison_id,
                    PartnerOfferLineComparisonRecord.revision == current_revision,
                )
            )
            if prior is None or prior.scope_review_id != command.scope_review_id:
                raise CommandExecutionError("PARTNER_OFFER_LINE_SCOPE_REVIEW_CONFLICT")
            previous_members = session.execute(
                sa.select(
                    PartnerOfferLineGroupRecord.group_id,
                    PartnerOfferLineMemberRecord.receipt_event_id,
                )
                .join(
                    PartnerOfferLineMemberRecord,
                    sa.and_(
                        PartnerOfferLineMemberRecord.tenant_id
                        == PartnerOfferLineGroupRecord.tenant_id,
                        PartnerOfferLineMemberRecord.case_id == PartnerOfferLineGroupRecord.case_id,
                        PartnerOfferLineMemberRecord.group_record_id == PartnerOfferLineGroupRecord.id,
                    ),
                )
                .where(
                    PartnerOfferLineGroupRecord.tenant_id == tenant_id,
                    PartnerOfferLineGroupRecord.case_id == command.case_id,
                    PartnerOfferLineGroupRecord.comparison_record_id == prior.id,
                )
            ).all()
            previous_sets: dict[UUID, set[UUID]] = {}
            for group_id, receipt_id in previous_members:
                previous_sets.setdefault(group_id, set()).add(receipt_id)
            requested_sets = {
                group.group_id: {member.receipt_event_id for member in group.members}
                for group in comparison.groups
            }
            if previous_sets != requested_sets:
                raise CommandExecutionError("PARTNER_OFFER_LINE_MEMBER_SET_CONFLICT")

        receipt_ids = tuple(
            {member.receipt_event_id for group in comparison.groups for member in group.members}
        )
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
        latest_receipt_rows = session.execute(
            sa.select(
                CasePartnerEventRecord.partner_id,
                sa.func.max(CasePartnerEventRecord.revision),
            )
            .where(
                CasePartnerEventRecord.tenant_id == tenant_id,
                CasePartnerEventRecord.case_id == command.case_id,
                CasePartnerEventRecord.partner_id.in_(tuple(row.partner_id for row in receipt_rows)),
                CasePartnerEventRecord.event_type == "RECEIVED",
            )
            .group_by(CasePartnerEventRecord.partner_id)
        ).all()
        latest_revisions = {partner_id: revision for partner_id, revision in latest_receipt_rows}
        if any(row.revision != latest_revisions.get(row.partner_id) for row in receipt_rows):
            raise CommandExecutionError("PARTNER_RECEIPT_VERSION_CONFLICT")

        revision = current_revision + 1
        root = PartnerOfferLineComparisonRecord(
            id=command.record_id,
            tenant_id=tenant_id,
            case_id=command.case_id,
            comparison_id=command.comparison_id,
            revision=revision,
            scope_review_id=command.scope_review_id,
            actor_id=UUID(str(context.actor_id)),
            membership_id=UUID(str(context.membership_id)),
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(root)
        session.flush()

        for group in comparison.groups:
            group_record = PartnerOfferLineGroupRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                case_id=command.case_id,
                comparison_record_id=root.id,
                group_id=group.group_id,
                disposition=group.disposition,
                rationale=group.rationale.strip(),
            )
            session.add(group_record)
            session.flush()
            session.add_all(
                PartnerOfferLineMemberRecord(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    case_id=command.case_id,
                    group_record_id=group_record.id,
                    receipt_event_id=member.receipt_event_id,
                    line_locator_state=member.line_locator_state,
                    line_locator=member.line_locator,
                    item_reference_state=member.item_reference_state,
                    item_reference=member.item_reference,
                    designation_state=member.designation_state,
                    designation=member.designation,
                    unit_state=member.unit_state,
                    unit=member.unit,
                    quantity_state=member.quantity_state,
                    quantity=member.quantity,
                )
                for member in group.members
            )

        return HandlerOutcome(
            result_code="PARTNER_OFFER_LINE_COMPARISON_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "PARTNER_OFFER_LINE_COMPARISON",
                    "aggregate_id": str(command.comparison_id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="PARTNER_OFFER_LINE_COMPARISON",
                    aggregate_id=command.comparison_id,
                    aggregate_revision=revision,
                    event_type="PARTNER_OFFER_LINE_COMPARISON_RECORDED",
                    payload={"case_id": str(command.case_id), "record_id": str(root.id)},
                ),
            ),
        )


def partner_offer_line_comparison_handlers() -> dict[str, CommandHandler]:
    return {
        RecordPartnerOfferLineComparisonCommand.command_type:
            RecordPartnerOfferLineComparisonHandler(),
    }


@dataclass(frozen=True, slots=True)
class PartnerOfferLineMemberView:
    receipt_event_id: UUID
    partner_id: UUID
    partner_kind: str
    partner_label: str
    source_locator: str
    receipt_is_current: bool
    line_locator_state: str
    line_locator: str | None
    item_reference_state: str
    item_reference: str | None
    designation_state: str
    designation: str | None
    unit_state: str
    unit: str | None
    quantity_state: str
    quantity: str | None


@dataclass(frozen=True, slots=True)
class PartnerOfferLineGroupView:
    group_id: UUID
    disposition: str
    rationale: str
    members: tuple[PartnerOfferLineMemberView, ...]


@dataclass(frozen=True, slots=True)
class PartnerOfferLineComparisonView:
    record_id: UUID
    comparison_id: UUID
    revision: int
    scope_review_id: UUID
    scope_review_revision: int
    scope_review_decision: str
    requires_reassessment: bool
    actor_id: UUID
    created_at: datetime
    groups: tuple[PartnerOfferLineGroupView, ...]


@dataclass(frozen=True, slots=True)
class PartnerOfferLineComparisonList:
    case_id: UUID
    comparisons: tuple[PartnerOfferLineComparisonView, ...]


class PartnerOfferLineComparisonService:
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
    ) -> PartnerOfferLineComparisonList:
        self._authorize(actor=actor, case_id=case_id, action=Capability.PRICING_READ, now=now)
        with self._session_factory() as session:
            records = session.scalars(
                sa.select(PartnerOfferLineComparisonRecord)
                .where(
                    PartnerOfferLineComparisonRecord.tenant_id == actor.tenant_id,
                    PartnerOfferLineComparisonRecord.case_id == case_id,
                )
                .order_by(
                    PartnerOfferLineComparisonRecord.created_at.asc(),
                    PartnerOfferLineComparisonRecord.comparison_id.asc(),
                    PartnerOfferLineComparisonRecord.revision.asc(),
                )
            ).all()
            record_ids = [record.id for record in records]
            group_rows = (
                session.scalars(
                    sa.select(PartnerOfferLineGroupRecord)
                    .where(
                        PartnerOfferLineGroupRecord.tenant_id == actor.tenant_id,
                        PartnerOfferLineGroupRecord.case_id == case_id,
                        PartnerOfferLineGroupRecord.comparison_record_id.in_(record_ids),
                    )
                    .order_by(
                        PartnerOfferLineGroupRecord.comparison_record_id,
                        PartnerOfferLineGroupRecord.group_id,
                    )
                ).all()
                if record_ids
                else []
            )
            group_ids = [group.id for group in group_rows]
            member_rows = (
                session.scalars(
                    sa.select(PartnerOfferLineMemberRecord)
                    .where(
                        PartnerOfferLineMemberRecord.tenant_id == actor.tenant_id,
                        PartnerOfferLineMemberRecord.case_id == case_id,
                        PartnerOfferLineMemberRecord.group_record_id.in_(group_ids),
                    )
                    .order_by(
                        PartnerOfferLineMemberRecord.group_record_id,
                        PartnerOfferLineMemberRecord.receipt_event_id,
                    )
                ).all()
                if group_ids
                else []
            )
            receipt_ids = tuple({member.receipt_event_id for member in member_rows})
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
            receipt_by_id = {receipt.event_id: receipt for receipt in receipts}
            partner_ids = tuple({receipt.partner_id for receipt in receipts})
            latest_receipts = (
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
            latest_receipt_revision = {
                partner_id: revision for partner_id, revision in latest_receipts
            }
            scope_reviews = session.scalars(
                sa.select(PartnerOfferScopeReviewRecord).where(
                    PartnerOfferScopeReviewRecord.tenant_id == actor.tenant_id,
                    PartnerOfferScopeReviewRecord.case_id == case_id,
                )
            ).all()
            scope_review_by_id = {review.id: review for review in scope_reviews}
            latest_scope_review = {
                comparison_id: review
                for comparison_id, review in _latest_by_comparison(scope_reviews).items()
            }

            members_by_group: dict[UUID, list[PartnerOfferLineMemberView]] = {}
            for member in member_rows:
                receipt = receipt_by_id[member.receipt_event_id]
                members_by_group.setdefault(member.group_record_id, []).append(
                    PartnerOfferLineMemberView(
                        receipt_event_id=receipt.event_id,
                        partner_id=receipt.partner_id,
                        partner_kind=receipt.partner_kind,
                        partner_label=receipt.partner_label,
                        source_locator=receipt.source_locator,
                        receipt_is_current=(
                            receipt.revision == latest_receipt_revision.get(receipt.partner_id)
                        ),
                        line_locator_state=member.line_locator_state,
                        line_locator=member.line_locator,
                        item_reference_state=member.item_reference_state,
                        item_reference=member.item_reference,
                        designation_state=member.designation_state,
                        designation=member.designation,
                        unit_state=member.unit_state,
                        unit=member.unit,
                        quantity_state=member.quantity_state,
                        quantity=member.quantity,
                    )
                )
            groups_by_record: dict[UUID, list[PartnerOfferLineGroupView]] = {}
            for group in group_rows:
                groups_by_record.setdefault(group.comparison_record_id, []).append(
                    PartnerOfferLineGroupView(
                        group_id=group.group_id,
                        disposition=group.disposition,
                        rationale=group.rationale,
                        members=tuple(members_by_group.get(group.id, ())),
                    )
                )

            comparisons = []
            for record in records:
                scope_review = scope_review_by_id[record.scope_review_id]
                current_scope = latest_scope_review[scope_review.comparison_id]
                groups = tuple(groups_by_record.get(record.id, ()))
                comparisons.append(
                    PartnerOfferLineComparisonView(
                        record_id=record.id,
                        comparison_id=record.comparison_id,
                        revision=record.revision,
                        scope_review_id=scope_review.id,
                        scope_review_revision=scope_review.revision,
                        scope_review_decision=scope_review.decision,
                        requires_reassessment=(
                            current_scope.id != scope_review.id
                            or current_scope.decision != "SAME_SCOPE_CONFIRMED"
                            or any(
                                not member.receipt_is_current
                                for group in groups
                                for member in group.members
                            )
                        ),
                        actor_id=record.actor_id,
                        created_at=record.created_at,
                        groups=groups,
                    )
                )
            return PartnerOfferLineComparisonList(case_id=case_id, comparisons=tuple(comparisons))

    def record(
        self,
        *,
        actor: ActorContext,
        command: RecordPartnerOfferLineComparisonCommand,
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
                    resource_type="PARTNER_OFFER_LINE_COMPARISON",
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


def _latest_by_comparison(
    scope_reviews: list[PartnerOfferScopeReviewRecord],
) -> dict[UUID, PartnerOfferScopeReviewRecord]:
    latest: dict[UUID, PartnerOfferScopeReviewRecord] = {}
    for review in scope_reviews:
        previous = latest.get(review.comparison_id)
        if previous is None or review.revision > previous.revision:
            latest[review.comparison_id] = review
    return latest
