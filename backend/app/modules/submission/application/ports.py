from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.modules.decision.domain.submission_gate import DecisionSubmissionGateSnapshot
from app.platform.events.dispatcher import CommandContext


class SubmissionDecisionGateReader(Protocol):
    """Reads only non-financial Decision facts inside the caller transaction."""

    def read(
        self, *, session: object, tenant_id: UUID, case_id: UUID
    ) -> DecisionSubmissionGateSnapshot | None: ...


class SubmissionPreparationSourceReader(Protocol):
    """Preparation owns verification; Submission receives only frozen source references."""

    def read(
        self,
        *,
        session: object,
        preparation_package_id: UUID,
        source: dict[str, object] | None,
        context: CommandContext,
    ) -> dict[str, object] | None: ...
