from copy import deepcopy
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.modules.pricing.application import case_closure_handler as handler
from app.modules.pricing.public.case_closure_contracts import ClosureActReview
from app.platform.events.dispatcher import CommandExecutionError
from pydantic import ValidationError


def test_requalification_cannot_reuse_a_stale_view_or_omit_new_consent(monkeypatch):
    with pytest.raises(ValidationError, match="HUMAN_CONFIRMATION_REQUIRED"):
        ClosureActReview(
            expected_dossier_sha256="a" * 64,
            human_confirmed=False,
            justification="La confirmation précédente ne suffit pas.",
        )
    monkeypatch.setattr(handler, "closure_dossier", lambda *args: {"dossier_sha256": "b" * 64})
    command = SimpleNamespace(
        case_id=uuid4(),
        closure_review=ClosureActReview(
            expected_dossier_sha256="a" * 64,
            human_confirmed=True,
            justification="Nouvel acte sur une vue devenue obsolète.",
        ),
    )
    with pytest.raises(CommandExecutionError, match="CLOSURE_VIEW_CONFLICT"):
        handler.validate_closure_review(None, uuid4(), command)


@pytest.mark.parametrize("state", ["REVIEW_REQUIRED", "MISSING", "CURRENT", "UNKNOWN"])
def test_new_reserve_requires_a_non_invalidated_origin_and_keeps_history(monkeypatch, state):
    origin = uuid4()
    historical = {
        "id": str(uuid4()),
        "context_state": "REVIEW_REQUIRED",
        "closure_review_json": {"human_confirmed": True, "justification": "Ancien accord."},
    }
    dossier = dict(
        dossier_sha256="a" * 64,
        dce_version_id=str(uuid4()),
        case_source={"source": "synthetic-v2"},
        open_obligation_ids=[],
        acts=[historical]
        + ([] if state == "MISSING" else [{"id": str(origin), "context_state": state}]),
        obligations=[],
        facts=[],
        change_actions=[],
    )
    before = deepcopy(dossier)
    monkeypatch.setattr(handler, "closure_dossier", lambda *args: dossier)
    command = SimpleNamespace(
        case_id=uuid4(),
        origin_reception_act_id=origin,
        closure_review=ClosureActReview(
            expected_dossier_sha256="a" * 64,
            human_confirmed=True,
            justification="Nouvelle relecture explicite sur source V2.",
        ),
    )
    if state in {"REVIEW_REQUIRED", "MISSING"}:
        with pytest.raises(
            CommandExecutionError, match="CLOSURE_COMPARISON_SOURCE_CHANGED_OR_FORBIDDEN"
        ):
            handler.validate_closure_review(None, uuid4(), command)
    else:
        result = handler.validate_closure_review(None, uuid4(), command)
        assert result["human_confirmed"] is True
        assert result["justification"] == command.closure_review.justification
        assert result["case_source"] == dossier["case_source"]
        assert result["legal_effect_state"] == "UNKNOWN"
    assert dossier == before
