# ruff: noqa: E501, E701
from __future__ import annotations

import sqlalchemy as sa

from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
    PaymentPostReceptionCycleRecord,
)


class PaymentCycleReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def list_for_case(self, *, actor, case_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return tuple(session.scalars(sa.select(PaymentPostReceptionCycleRecord).where(PaymentPostReceptionCycleRecord.tenant_id == actor.tenant_id, PaymentPostReceptionCycleRecord.case_id == case_id).order_by(PaymentPostReceptionCycleRecord.created_at.asc())).all())
