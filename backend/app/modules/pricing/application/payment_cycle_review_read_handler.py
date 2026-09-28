# ruff: noqa: E501, E701
from __future__ import annotations

import sqlalchemy as sa

from app.modules.pricing.infrastructure.models.payment_cycle_review import PaymentCycleReviewRecord


class PaymentCycleReviewReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def list_for_cycle(self, *, actor, cycle_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return tuple(session.scalars(sa.select(PaymentCycleReviewRecord).where(PaymentCycleReviewRecord.tenant_id == actor.tenant_id, PaymentCycleReviewRecord.cycle_id == cycle_id).order_by(PaymentCycleReviewRecord.created_at.asc())).all())
