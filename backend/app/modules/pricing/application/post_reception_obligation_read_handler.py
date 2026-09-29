# ruff: noqa: E501, I001
from dataclasses import dataclass
from uuid import UUID
import sqlalchemy as sa

from app.modules.pricing.infrastructure.models.post_reception_obligation import (
    PostReceptionObligationRecord,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation_transition import (
    PostReceptionObligationTransitionRecord,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)


@dataclass(frozen=True, slots=True)
class PostReceptionObligationProjection:
    record: PostReceptionObligationRecord
    status: str
    revision: int
    latest_transition: PostReceptionObligationTransitionRecord | None
    origin_reception_summary: str | None
    origin_reception_outcome: str


class PostReceptionObligationReadService:
    def __init__(self, *, session_factory):
        self._session_factory = session_factory

    def list_for_case(self, *, actor, case_id):
        from app.platform.security.context import ActorKind

        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            obligations = tuple(
                session.scalars(
                    sa.select(PostReceptionObligationRecord)
                    .where(
                        PostReceptionObligationRecord.tenant_id == actor.tenant_id,
                        PostReceptionObligationRecord.case_id == case_id,
                    )
                    .order_by(
                        PostReceptionObligationRecord.created_at.asc(),
                        PostReceptionObligationRecord.id.asc(),
                    )
                ).all()
            )
            if not obligations:
                return ()
            reception_ids = [
                row.origin_reception_act_id for row in obligations if row.origin_reception_act_id
            ]
            receptions = (
                {
                    row.id: row
                    for row in session.scalars(
                        sa.select(ContractExecutionEvidenceRecord).where(
                            ContractExecutionEvidenceRecord.tenant_id == actor.tenant_id,
                            ContractExecutionEvidenceRecord.case_id == case_id,
                            ContractExecutionEvidenceRecord.id.in_(reception_ids),
                            ContractExecutionEvidenceRecord.act_kind == "WORK_RECEPTION",
                        )
                    ).all()
                }
                if reception_ids
                else {}
            )
            ids = [row.id for row in obligations]
            transitions = session.scalars(
                sa.select(PostReceptionObligationTransitionRecord)
                .where(
                    PostReceptionObligationTransitionRecord.tenant_id == actor.tenant_id,
                    PostReceptionObligationTransitionRecord.obligation_id.in_(ids),
                )
                .order_by(
                    PostReceptionObligationTransitionRecord.obligation_id,
                    PostReceptionObligationTransitionRecord.revision.desc(),
                )
            ).all()
            latest_by_id: dict[UUID, PostReceptionObligationTransitionRecord] = {}
            for transition in transitions:
                latest_by_id.setdefault(transition.obligation_id, transition)
            return tuple(
                PostReceptionObligationProjection(
                    record=row,
                    status=latest_by_id[row.id].resulting_status
                    if row.id in latest_by_id
                    else row.status,
                    revision=latest_by_id[row.id].revision if row.id in latest_by_id else 0,
                    latest_transition=latest_by_id.get(row.id),
                    origin_reception_summary=(
                        receptions[row.origin_reception_act_id].summary
                        if row.origin_reception_act_id in receptions
                        else None
                    ),
                    origin_reception_outcome=(
                        receptions[row.origin_reception_act_id].reception_outcome or "UNKNOWN"
                        if row.origin_reception_act_id in receptions
                        else "UNKNOWN"
                    ),
                )
                for row in obligations
            )
