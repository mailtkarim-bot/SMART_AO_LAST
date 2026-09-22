from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.modules.patron_action.application.outcome import CaseOutcomeService
from app.platform.security.context import ActorKind


def test_outcome_reader_requires_patron():
    actor = SimpleNamespace(actor_kind=ActorKind.COLLABORATEUR, membership_id=uuid4())
    service = CaseOutcomeService(dispatcher=None, session_factory=None, policy=None)  # type: ignore[arg-type]
    try:
        service.list_for_case(actor=actor, case_id=uuid4(), now=datetime.now(tz=UTC))  # type: ignore[arg-type]
    except PermissionError as error:
        assert str(error) == "PATRON_REQUIRED"
    else:
        raise AssertionError("non-patron outcome read must be refused")
