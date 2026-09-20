"""Read BOAMP unknowns attached to an opportunity-origin Case."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.application.queries import CaseResolutionUnknownProjection
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.opportunity.application.boamp_qualification import (
    _deadline_state,
    _unknowns,
)
from app.modules.opportunity.infrastructure.observation_models import (
    BoampOpportunityObservationRecord,
)


class SqlAlchemyBoampCaseUnknownReader:
    """Project deterministic BOAMP unknowns without creating a second registry."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_case(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        limit: int,
    ) -> tuple[CaseResolutionUnknownProjection, ...]:
        page_limit = min(max(limit, 1), 100)
        with self._session_factory() as session:
            observation_id = session.scalar(
                sa.select(CaseRecord.origin_reference_id).where(
                    CaseRecord.tenant_id == tenant_id,
                    CaseRecord.id == case_id,
                    CaseRecord.business_origin == "OPPORTUNITY",
                )
            )
            if observation_id is None:
                return ()
            observation = session.scalar(
                sa.select(BoampOpportunityObservationRecord).where(
                    BoampOpportunityObservationRecord.tenant_id == tenant_id,
                    BoampOpportunityObservationRecord.id == observation_id,
                )
            )
            if observation is None:
                return ()
            deadline_state = _deadline_state(
                observation.response_deadline,
                now=datetime.now(tz=UTC),
            )
            unknowns = _unknowns(
                observation,
                deadline_state=deadline_state,
                opened=True,
            )

        source_notice_ref = f"BOAMP:{observation.source_notice_id}"
        return tuple(
            CaseResolutionUnknownProjection(
                unknown_id=uuid5(
                    NAMESPACE_URL,
                    f"smart-ao:case-resolution-unknown:{tenant_id}:{case_id}:{unknown['code']}",
                ),
                native_state="UNKNOWN",
                source_refs=(
                    f"observation:{observation.id}",
                    source_notice_ref,
                    f"unknown:{unknown['code']}",
                    f"unknown-state:{unknown['state']}",
                ),
                next_action=str(unknown["next_action"]),
                due_at=None,
                impact=str(unknown["possible_impact"]),
            )
            for unknown in unknowns[:page_limit]
        )
