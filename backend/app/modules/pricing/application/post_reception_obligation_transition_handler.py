# ruff: noqa: E501, I001
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.pricing.application.post_reception_obligation_transition_commands import TransitionPostReceptionObligationCommand
from app.modules.pricing.domain.post_reception_obligation_transition import (
    PostReceptionObligationStatus,
    build_post_reception_obligation_transition,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation import PostReceptionObligationRecord
from app.modules.pricing.infrastructure.models.post_reception_obligation_transition import PostReceptionObligationTransitionRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class TransitionPostReceptionObligationHandler(CommandHandler):
    def execute(self, *, session: Session, command: TransitionPostReceptionObligationCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        obligation = session.scalar(
            sa.select(PostReceptionObligationRecord)
            .where(
                PostReceptionObligationRecord.tenant_id == tenant_id,
                PostReceptionObligationRecord.case_id == command.case_id,
                PostReceptionObligationRecord.id == command.obligation_id,
            )
            .with_for_update()
        )
        if obligation is None:
            raise CommandExecutionError("POST_RECEPTION_OBLIGATION_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(
            sa.select(PostReceptionObligationTransitionRecord.id).where(
                PostReceptionObligationTransitionRecord.tenant_id == tenant_id,
                PostReceptionObligationTransitionRecord.id == command.transition_id,
            )
        ) is not None:
            raise CommandExecutionError("POST_RECEPTION_OBLIGATION_TRANSITION_ID_REUSED")
        latest = session.scalar(
            sa.select(PostReceptionObligationTransitionRecord)
            .where(
                PostReceptionObligationTransitionRecord.tenant_id == tenant_id,
                PostReceptionObligationTransitionRecord.obligation_id == command.obligation_id,
            )
            .order_by(PostReceptionObligationTransitionRecord.revision.desc())
            .limit(1)
        )
        current_status = PostReceptionObligationStatus(latest.resulting_status if latest else obligation.status)
        current_revision = latest.revision if latest else 0
        if command.expected_revision != current_revision:
            raise CommandExecutionError("POST_RECEPTION_OBLIGATION_REVISION_CONFLICT")
        try:
            transition = build_post_reception_obligation_transition(
                current_status=current_status,
                resulting_status=PostReceptionObligationStatus(command.resulting_status),
                rationale=command.rationale,
                evidence_refs=command.evidence_refs,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        revision = current_revision + 1
        session.add(
            PostReceptionObligationTransitionRecord(
                id=command.transition_id,
                tenant_id=tenant_id,
                obligation_id=command.obligation_id,
                revision=revision,
                previous_status=transition.previous_status.value,
                resulting_status=transition.resulting_status.value,
                evidence_refs_json=list(transition.evidence_refs),
                rationale=transition.rationale,
                actor_id=UUID(str(context.actor_id)),
            )
        )
        return HandlerOutcome(
            result_code="POST_RECEPTION_OBLIGATION_TRANSITION_RECORDED",
            aggregate_refs=({"aggregate_type": "POST_RECEPTION_OBLIGATION", "aggregate_id": str(command.obligation_id), "aggregate_revision": revision},),
            events=(PendingDomainEvent(
                aggregate_type="POST_RECEPTION_OBLIGATION",
                aggregate_id=command.obligation_id,
                aggregate_revision=revision,
                event_type="POST_RECEPTION_OBLIGATION_TRANSITION_RECORDED",
                payload={"case_id": str(command.case_id), "previous_status": transition.previous_status.value, "resulting_status": transition.resulting_status.value, "evidence_refs": list(transition.evidence_refs)},
            ),),
        )


def post_reception_obligation_transition_handlers() -> dict[str, TransitionPostReceptionObligationHandler]:
    return {TransitionPostReceptionObligationCommand.command_type: TransitionPostReceptionObligationHandler()}
