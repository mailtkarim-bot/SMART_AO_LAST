# ruff: noqa: E501, E701
from __future__ import annotations

import sqlalchemy as sa

from app.modules.dce.infrastructure.models.contract_query_export import ContractQueryExportRecord
from app.modules.dce.infrastructure.models.contract_query_export_transition import (
    ContractQueryExportTransitionRecord,
)


class ExportOperationalHandoffReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def get_for_export(self, *, actor, export_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            export = session.scalar(sa.select(ContractQueryExportRecord).where(ContractQueryExportRecord.tenant_id == actor.tenant_id, ContractQueryExportRecord.id == export_id))
            if export is None: return None
            transitions = tuple(session.scalars(sa.select(ContractQueryExportTransitionRecord).where(ContractQueryExportTransitionRecord.tenant_id == actor.tenant_id, ContractQueryExportTransitionRecord.export_id == export_id).order_by(ContractQueryExportTransitionRecord.created_at.asc())).all())
            return export, transitions
