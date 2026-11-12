"""Changes follow exact reconstructed handovers with private cash present."""

import json

from tests.db import test_l10_repriced_execution as execution
from tests.db.test_l09_private_cash_handover import (
    test_private_cash_never_enters_repriced_handover as run_private_handover,
)


def test_changes_do_not_expose_private_cash_after_repriced_handover(
    session_factory, tmp_path, monkeypatch, closure_qualifier=None, private_qualifier=None
):
    checked = []

    def handover_runner(factory, root, patch, change_qualifier):
        def inspect(factory, http, packet, control, phase, work, result, private):
            change_qualifier(factory, http, packet, control, phase, work, result)
            url = f"/api/v1/cases/{work.case_id}/contract-change-events"
            response = http.client.get(url, headers=http.driver_headers)
            assert response.status_code == 200, response.text
            body = json.dumps(response.json(), ensure_ascii=False)
            for value in private:
                assert value not in body
            for value in ("314159265", "source_details", "closing_minor", "cash_schedule"):
                assert value not in body
            events = response.json()["events"]
            assert any(
                row["handover_snapshot_id"] == result["view"]["snapshot_id"] for row in events
            )
            checked.append(phase)
            if private_qualifier is not None:
                private_qualifier(list(private))

        return run_private_handover(factory, root, patch, change_qualifier=inspect)

    monkeypatch.setattr(execution, "_handover", handover_runner)
    execution.test_changes_follow_the_repriced_handover_without_reusing_prior_acts(
        session_factory, tmp_path, monkeypatch, closure_qualifier=closure_qualifier
    )
    assert checked == [1, 2]
