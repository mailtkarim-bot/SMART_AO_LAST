"""Private human position reviews using existing authorization and command receipts."""

import sqlalchemy as sa

from app.modules.pricing.infrastructure.models.financial import PricingImportRowRecord as Row
from app.modules.pricing.infrastructure.models.position_review import (
    PricingPositionReviewRecord as Review,
)
from app.modules.pricing.infrastructure.position_reader import (
    case_batch,
    digest,
    public_snapshot,
    read_positions,
)
from app.platform.events.dispatcher import CommandContext
from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorKind, DataClassification


class PricingPositionService:
    def __init__(self, *, session_factory, dispatcher, policy):
        self._factory = session_factory
        self._dispatcher = dispatcher
        self._policy = policy

    def _authorize(self, *, actor, case_id, now, write=False):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("FORBIDDEN")
        rights = [
            (Capability.CASE_DCE_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.DECISION_RISK_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.PRICING_READ, DataClassification.FINANCIAL_PRIVATE),
        ]
        if write:
            rights.append(
                (Capability.FINANCIAL_REPORT_LINE_WRITE, DataClassification.FINANCIAL_PRIVATE)
            )
        for action, classification in rights:
            result = self._policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=action,
                    resource=AuthorizationResource(
                        resource_type="PRICING_POSITION",
                        resource_id=case_id,
                        case_id=case_id,
                        tenant_id=actor.tenant_id,
                        classification=classification,
                    ),
                    evaluated_at=now,
                    mfa_required=write,
                ),
            )
            if not result.allowed:
                raise PermissionError("FORBIDDEN")

    def read(self, *, actor, case_id, batch_id, now, offset=0, search="", position_id=None):
        self._authorize(actor=actor, case_id=case_id, now=now)
        with self._factory() as session:
            session.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            if position_id is not None:
                case_batch(session, tenant=actor.tenant_id, case_id=case_id, batch_id=batch_id)
                row = session.scalar(
                    sa.select(Row).where(
                        Row.tenant_id == actor.tenant_id,
                        Row.batch_id == batch_id,
                        Row.id == position_id,
                    )
                )
                if row is None:
                    raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
                offset = session.scalar(
                    sa.select(sa.func.count())
                    .select_from(Row)
                    .where(
                        Row.tenant_id == actor.tenant_id,
                        Row.batch_id == batch_id,
                        Row.row_number < row.row_number,
                    )
                )
            return read_positions(
                session,
                tenant=actor.tenant_id,
                case_id=case_id,
                batch_id=batch_id,
                offset=offset,
                search=search,
                today=now.date(),
            )

    def record(self, *, actor, command, now):
        self._authorize(actor=actor, case_id=command.case_id, now=now, write=True)
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                case_id=command.case_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                membership_id=actor.membership_id,
                identity_id=actor.identity_id,
                session_id=actor.session_id,
                received_at=now,
                correlation_id=actor.correlation_id,
            ),
        )

    def history(self, *, actor, case_id, batch_id, position_id, now, before_revision=None):
        self._authorize(actor=actor, case_id=case_id, now=now)
        with self._factory() as session:
            session.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            case_batch(session, tenant=actor.tenant_id, case_id=case_id, batch_id=batch_id)
            row = session.scalar(
                sa.select(Row.id).where(
                    Row.tenant_id == actor.tenant_id,
                    Row.batch_id == batch_id,
                    Row.id == position_id,
                )
            )
            if row is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            query = sa.select(Review).where(
                Review.tenant_id == actor.tenant_id,
                Review.case_id == case_id,
                Review.position_id == position_id,
            )
            if before_revision is not None:
                query = query.where(Review.revision < before_revision)
            records = list(session.scalars(query.order_by(Review.revision.desc()).limit(21)))
            result = []
            for r in records[:20]:
                valid = digest(r.source_snapshot_json) == r.basis_sha256
                result.append(
                    dict(
                        record_id=r.id,
                        revision=r.revision,
                        previous_id=r.previous_id,
                        state="HISTORICAL" if valid else "UNPROVEN",
                        created_at=r.created_at,
                        actor_id=r.actor_id if valid else None,
                        justification=r.justification if valid else None,
                        snapshot=public_snapshot(r.source_snapshot_json) if valid else None,
                    )
                )
            return dict(
                case_id=case_id,
                batch_id=batch_id,
                position_id=position_id,
                entries=result,
                next_before_revision=records[19].revision if len(records) > 20 else None,
            )
