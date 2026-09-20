"""Transactional Case/DCE applicability handler."""

from __future__ import annotations

from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.application.commands import LinkCaseDceVersionCommand
from app.modules.case.infrastructure.models.case import (
    CaseDceApplicabilityHistoryRecord,
    CaseRecord,
)
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.platform.events.dispatcher import CommandContext, HandlerOutcome, PendingDomainEvent


class LinkCaseDceVersionHandler:
    """Link an admitted DCE version while preserving prior applicability history."""

    def execute(
        self,
        *,
        session: Session,
        command: LinkCaseDceVersionCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        case = session.scalar(
            sa.select(CaseRecord)
            .where(
                CaseRecord.tenant_id == context.tenant_id,
                CaseRecord.id == command.case_id,
            )
            .with_for_update()
        )
        version = session.scalar(
            sa.select(DceVersionRecord)
            .where(
                DceVersionRecord.tenant_id == context.tenant_id,
                DceVersionRecord.id == command.dce_version_id,
            )
            .with_for_update()
        )
        if case is None or case.lifecycle == "ARCHIVED":
            raise ValueError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if (
            command.expected_case_revision is not None
            and case.aggregate_revision != command.expected_case_revision
        ):
            raise ValueError("VERSION_CONFLICT")
        if version is None:
            raise ValueError("DCE_VERSION_NOT_FOUND_OR_FORBIDDEN")
        if case.consultation_id is None or version.consultation_id != case.consultation_id:
            raise ValueError("DCE_CONSULTATION_MISMATCH")
        if version.lifecycle != "ADMITTED" or version.integrity != "VERIFIED":
            raise ValueError("DCE_VERSION_NOT_ADMISSIBLE")
        if case.applicable_dce_version_id == version.id:
            raise ValueError("DCE_VERSION_ALREADY_APPLICABLE")

        session.execute(
            sa.update(CaseDceApplicabilityHistoryRecord)
            .where(
                CaseDceApplicabilityHistoryRecord.tenant_id == context.tenant_id,
                CaseDceApplicabilityHistoryRecord.case_id == case.id,
                CaseDceApplicabilityHistoryRecord.is_current.is_(True),
            )
            .values(is_current=False)
        )
        case.applicable_dce_version_id = version.id
        case.dce_freshness = "CURRENT"
        case.aggregate_revision += 1
        case.updated_by_actor_id = context.actor_id
        session.add(
            CaseDceApplicabilityHistoryRecord(
                id=uuid4(),
                tenant_id=context.tenant_id,
                case_id=case.id,
                dce_version_id=version.id,
                reason=command.reason,
                is_current=True,
                set_by_actor_id=context.actor_id,
                set_at=context.received_at,
            )
        )
        event = PendingDomainEvent(
            aggregate_type="CASE",
            aggregate_id=case.id,
            aggregate_revision=case.aggregate_revision,
            event_type="CASE_DCE_APPLICABILITY_SET",
            payload={
                "case_id": str(case.id),
                "dce_version_id": str(version.id),
                "tenant_id": str(context.tenant_id),
            },
        )
        return HandlerOutcome(
            result_code="CASE_DCE_APPLICABILITY_SET",
            aggregate_refs=(
                {
                    "aggregate_type": "AFF",
                    "aggregate_id": str(case.id),
                    "aggregate_revision": case.aggregate_revision,
                },
            ),
            events=(event,),
        )
