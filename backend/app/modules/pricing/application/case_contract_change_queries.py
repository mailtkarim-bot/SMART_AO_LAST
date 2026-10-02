"""Read-side port for the Patron contract-change timeline."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID


class CaseContractChangeReader(Protocol):
    def list_for_case(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[dict[str, object], ...]: ...
