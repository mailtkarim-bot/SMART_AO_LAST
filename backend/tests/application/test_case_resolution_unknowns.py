from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from app.modules.opportunity.application.boamp_case_creation import BoampCaseCreationService
from app.modules.opportunity.infrastructure.case_unknown_reader import (
    SqlAlchemyBoampCaseUnknownReader,
)

sys.path.insert(0, str(Path(__file__).parents[1] / "process"))
from test_boamp_case_creation_persistence import (  # noqa: E402
    NOW,
    _command,
    _context,
    _dispatcher,
    _seed_signal,
)


@pytest.mark.db
@pytest.mark.security
def test_opportunity_case_unknowns_keep_source_and_deterministic_identity(
    database_engine,
    session_factory,
) -> None:
    tenant_id, identity_id, membership_id, observation_id = _seed_signal(database_engine)
    result = BoampCaseCreationService(
        session_factory=session_factory,
        dispatcher=_dispatcher(session_factory),
    ).create(
        context=_context(
            tenant_id=tenant_id,
            identity_id=identity_id,
            membership_id=membership_id,
        ),
        command=_command(
            observation_id=observation_id,
            idempotency_key=uuid4(),
        ),
        now=NOW,
    )
    case_id = UUID(str(result.aggregate_refs[0]["aggregate_id"]))
    reader = SqlAlchemyBoampCaseUnknownReader(session_factory)

    first = reader.list_for_case(tenant_id=tenant_id, case_id=case_id, limit=100)
    replay = reader.list_for_case(tenant_id=tenant_id, case_id=case_id, limit=100)

    assert {ref for item in first for ref in item.source_refs} >= {
        f"observation:{observation_id}",
        "BOAMP:A-" + observation_id.hex[:12],
    }
    assert len(first) == 2
    assert all(
        item.unknown_id == replay_item.unknown_id
        for item, replay_item in zip(first, replay, strict=True)
    )
    assert all(item.native_state == "UNKNOWN" for item in first)
    assert {item.impact for item in first} == {
        "Périmètre d’étude et de prix non démontré.",
        "Éligibilité et exigences non vérifiables.",
    }
    assert {"unknown:LOT_SCOPE", "unknown:DCE_NOT_RECEIVED"} <= {
        ref
        for item in first
        for ref in item.source_refs
        if ref.startswith("unknown:")
    }
