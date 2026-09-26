# ruff: noqa: E501, E701
from __future__ import annotations

import sqlalchemy as sa

from app.modules.dce.infrastructure.models.human_resumption_act import HumanResumptionActRecord


class HumanResumptionReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def get_for_export(self, *, actor, export_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return session.scalar(sa.select(HumanResumptionActRecord).where(HumanResumptionActRecord.tenant_id == actor.tenant_id, HumanResumptionActRecord.export_id == export_id).order_by(HumanResumptionActRecord.created_at.desc()))
