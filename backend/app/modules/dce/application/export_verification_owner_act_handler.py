# ruff: noqa: E501
from __future__ import annotations

import sqlalchemy as sa

from app.modules.dce.infrastructure.models.export_verification_owner_act import (
    ExportVerificationOwnerActRecord,
)


class ExportVerificationOwnerActReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def get_for_export(self, *, actor, export_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return session.scalar(sa.select(ExportVerificationOwnerActRecord).where(ExportVerificationOwnerActRecord.tenant_id == actor.tenant_id, ExportVerificationOwnerActRecord.export_id == export_id).order_by(ExportVerificationOwnerActRecord.created_at.desc()))
