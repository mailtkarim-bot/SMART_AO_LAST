# ruff: noqa: E501, E701, I001
from __future__ import annotations
import sqlalchemy as sa
from app.modules.pricing.infrastructure.models.payment_unknown_audit_owner_act import PaymentUnknownAuditOwnerActRecord
class PaymentUnknownAuditOwnerActReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def get_for_case(self, *, actor, case_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return session.scalar(sa.select(PaymentUnknownAuditOwnerActRecord).where(PaymentUnknownAuditOwnerActRecord.tenant_id == actor.tenant_id, PaymentUnknownAuditOwnerActRecord.case_id == case_id).order_by(PaymentUnknownAuditOwnerActRecord.created_at.desc()))
