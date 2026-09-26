# ruff: noqa: E501, E701
from __future__ import annotations

import sqlalchemy as sa

from app.modules.dce.infrastructure.models.contract_query_export_transition import (
    ContractQueryExportTransitionRecord,
)
from app.modules.dce.infrastructure.models.human_resumption_act import HumanResumptionActRecord


class HumanResumptionTimelineReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def get_for_export(self, *, actor, export_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            rows = []
            for row in session.scalars(sa.select(ContractQueryExportTransitionRecord).where(ContractQueryExportTransitionRecord.tenant_id == actor.tenant_id, ContractQueryExportTransitionRecord.export_id == export_id)).all(): rows.append({"event_type": "TRANSITION", "event_id": row.id, "status": row.to_status, "created_at": row.created_at})
            for row in session.scalars(sa.select(HumanResumptionActRecord).where(HumanResumptionActRecord.tenant_id == actor.tenant_id, HumanResumptionActRecord.export_id == export_id)).all(): rows.append({"event_type": "HUMAN_RESUMPTION", "event_id": row.id, "status": row.state, "created_at": row.created_at})
            return tuple(sorted(rows, key=lambda item: item["created_at"]))
