"""Fresh exact handovers while private cash exists before and after repricing."""

import json

from tests.db.test_l08_private_cash_rebuild import packet_with_private_cash
from tests.db.test_l09_repriced_packet_handover import (
    test_repriced_packet_reaches_responsable_with_fresh_sources_and_acts as run_handover,
)


def test_private_cash_never_enters_repriced_handover(
    session_factory, tmp_path, monkeypatch, change_qualifier=None
):
    active_private: list[str] = []
    report_ids = set()
    stages = []

    def inspect(factory, http, packet, control, phase, work, result):
        view = result["view"]
        raw = json.dumps(view, ensure_ascii=False)
        for value in active_private:
            assert value not in raw
        assert "314159265" not in raw
        assert "source_details" not in raw and "closing_minor" not in raw
        doc = http.client.get(
            f"/api/v1/cases/{work.case_id}/p7-handover/{view['snapshot_id']}/offer-document",
            headers=http.driver_headers,
        )
        assert doc.status_code == 200
        for value in active_private:
            assert value.encode() not in doc.content
        assert b"314159265" not in doc.content
        stages.append((phase, view["snapshot_id"], view["manifest_sha256"]))
        if change_qualifier is not None:
            change_qualifier(
                factory, http, packet, control, phase, work, result, list(active_private)
            )

    def run_packet(factory, root, patch, qualify):
        def handover(factory, http, packet, control, phase, work, private):
            reference = control["pricing_reference"]
            for field in ("referenced", "latest_published"):
                if reference[field]:
                    report_ids.add(reference[field]["report_id"])
            active_private[:] = private + sorted(report_ids)
            qualify(factory, http, packet, control, phase, work)

        return packet_with_private_cash(factory, root, patch, handover_qualifier=handover)

    run_handover(
        session_factory, tmp_path, monkeypatch, change_qualifier=inspect, packet_runner=run_packet
    )
    assert [row[0] for row in stages] == [1, 2]
    assert stages[0][1] != stages[1][1] and stages[0][2] != stages[1][2]
