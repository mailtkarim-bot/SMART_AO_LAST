"""Closure follows exact repriced changes while private cash remains protected."""

import json

from tests.db import test_l11_repriced_closure as closure
from tests.db.test_l10_private_cash_execution import (
    test_changes_do_not_expose_private_cash_after_repriced_handover as run_private_changes,
)


def test_repriced_changes_reach_closure_without_exposing_private_cash(
    session_factory, tmp_path, monkeypatch
):
    private_values = []
    checked = []

    def changes_runner(factory, root, patch, closure_qualifier=None):
        return run_private_changes(
            factory,
            root,
            patch,
            closure_qualifier=closure_qualifier,
            private_qualifier=lambda values: private_values.__setitem__(slice(None), values),
        )

    def inspect(factory, http, work, final):
        root = f"/api/v1/patron/cases/{work.case_id}/closure"
        denied = http.client.get(root, headers=http.driver_headers)
        assert denied.status_code == 403
        assert "314159265" not in denied.text
        text = json.dumps(final, ensure_ascii=False)
        for value in private_values:
            assert value not in text
            assert value not in denied.text
        assert "314159265" not in text
        events = http.client.get(
            f"/api/v1/cases/{work.case_id}/contract-change-events", headers=http.driver_headers
        )
        assert events.status_code == 200
        operational = json.dumps(events.json(), ensure_ascii=False)
        for value in private_values:
            assert value not in operational
        assert "314159265" not in operational

        assert final["financial_observations"]["settlement_state"] == "UNKNOWN"
        assert final["external_receipt_state"] == final["legal_effect_state"] == "UNKNOWN"
        assert final["completeness_state"] == "REVIEW_REQUIRED"
        assert final["open_obligation_ids"]
        checked.append(True)

    monkeypatch.setattr(closure, "_changes", changes_runner)
    closure.test_repriced_actions_reach_closure_without_transferring_prior_consents(
        session_factory, tmp_path, monkeypatch, continuity_qualifier=inspect
    )
    assert checked == [True] and private_values
