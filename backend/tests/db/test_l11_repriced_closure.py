"""Repriced packet -> handover -> changes/actions -> sourced closure and requalification."""

from tests.db.test_l10_repriced_execution import (
    test_changes_follow_the_repriced_handover_without_reusing_prior_acts as _changes,
)
from tests.db.test_l11_v2_closure import (
    test_v2_changes_remain_explicit_in_closure_without_presuming_payment as _closure,
)


def _repriced_changes(session_factory, tmp_path, monkeypatch, technical_docx, closure_qualifier):
    assert technical_docx is False
    _changes(session_factory, tmp_path, monkeypatch, closure_qualifier=closure_qualifier)


def test_repriced_actions_reach_closure_without_transferring_prior_consents(
    session_factory, tmp_path, monkeypatch, continuity_qualifier=None
):
    monkeypatch.setenv("SMART_AO_L11_V2_PROOF_DIR", str(tmp_path / "l11-proof"))
    _closure(
        session_factory,
        tmp_path,
        monkeypatch,
        False,
        continuity_qualifier=continuity_qualifier,
        changes_runner=_repriced_changes,
    )
