"""Refusals and exact recovery on the repriced packet-to-closure native chain."""

from tests.db.test_l11_repriced_closure import (
    test_repriced_actions_reach_closure_without_transferring_prior_consents as _closure,
)
from tests.db.test_transversal_rectified_closure_recovery import (
    test_refusals_and_exact_recovery_after_rectification_and_closure as _recovery,
)


def _repriced_closure(session_factory, tmp_path, monkeypatch, technical_docx, continuity_qualifier):
    assert technical_docx is False
    _closure(session_factory, tmp_path, monkeypatch, continuity_qualifier=continuity_qualifier)


def test_repriced_packet_chain_refusals_and_recovery_before_and_after_commit(
    session_factory, tmp_path, monkeypatch
):
    monkeypatch.setenv("SMART_AO_TRANSVERSAL_RECOVERY_PROOF_DIR", str(tmp_path / "recovery"))
    _recovery(session_factory, tmp_path, monkeypatch, closure_runner=_repriced_closure)
