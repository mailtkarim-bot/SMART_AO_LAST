"""L10 source/impact/action qualification using the repriced exact packet's handovers."""

import json
from uuid import uuid4

import sqlalchemy as sa
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord
from tests.db.test_l09_repriced_packet_handover import (
    test_repriced_packet_reaches_responsable_with_fresh_sources_and_acts as _handover,
)
from tests.db.test_l10_rectified_changes import (
    test_changes_require_explicit_current_v2_sources_and_never_transfer_v1_acts as _changes,
)


def _repriced_handover(session_factory, tmp_path, monkeypatch, technical_docx, change_qualifier):
    assert technical_docx is False

    def qualified(factory, http, run, control, generation, w, handover):
        change_qualifier(factory, http, run, control, generation, w, handover)
        root = f"/api/v1/patron/cases/{w.case_id}/contract-change-events"
        private = http.client.get(root, headers=http.patron_headers)
        assert private.status_code == 200, private.text
        row = next(
            event
            for event in private.json()["events"]
            if event["handover_snapshot_id"] == handover["view"]["snapshot_id"]
        )
        assert row["a1_engagements_state"] == "UNKNOWN" and row["a1_engagements"] == []

        def ids():
            return dict(
                command_id=str(uuid4()), idempotency_key=str(uuid4()), correlation_id=str(uuid4())
            )

        linkage = str(uuid4())
        unknown = dict(
            ids(),
            linkage_id=linkage,
            expected_revision=0,
            state="UNKNOWN",
            selected_sources=[],
            rationale="Aucun engagement A1 courant identifié.",
            unknown_reason="Source A1 absente de cette passation.",
        )
        linked = http.client.post(
            root + f"/{row['event_id']}/engagement-links", headers=http.patron_headers, json=unknown
        )
        assert linked.status_code == 201, linked.text

        def counts():
            with factory() as session:
                return tuple(
                    session.scalar(sa.select(sa.func.count()).select_from(model))
                    for model in (DomainEventRecord, OutboxMessageRecord)
                )

        before = counts()
        attempt = dict(
            ids(),
            declaration_id=str(uuid4()),
            linkage_id=linkage,
            source=dict(
                condition_id=str(uuid4()),
                requirement_id=str(uuid4()),
                requirement_revision=1,
                impact_id=str(uuid4()),
                impact_revision=1,
                profile_version_id=str(uuid4()),
                profile_version=1,
                profile_sha256="a" * 64,
            ),
            expected_revision=0,
            axis="COST",
            impact_state="UNKNOWN",
            impact_unknown_reason="Montant non établi sans source A1 courante.",
            measurement_state="UNKNOWN",
            source_refs=row["source_refs"],
            evidence_refs=[],
            assumptions=["Tentative négative, aucune source inventée comme valide."],
            rationale="Refus attendu avant toute déclaration C3.",
        )
        denied = http.client.post(
            root + f"/{row['event_id']}/impact-declarations",
            headers=http.patron_headers,
            json=attempt,
        )
        assert (
            denied.status_code == 422
            and denied.json()["detail"] == "C2_LINKAGE_NOT_CURRENT_OR_LINKED"
        ), denied.text
        assert counts() == before
        after = http.client.get(root, headers=http.patron_headers).json()
        own = next(event for event in after["events"] if event["event_id"] == row["event_id"])
        assert own["impact_declarations"] == []
        (tmp_path / f"c3-source-missing-v{generation}.json").write_text(
            json.dumps(
                dict(
                    event_id=row["event_id"],
                    state="UNKNOWN",
                    refusal=denied.json(),
                    no_effect=counts() == before,
                )
            )
        )

    _handover(session_factory, tmp_path, monkeypatch, change_qualifier=qualified)


def test_changes_follow_the_repriced_handover_without_reusing_prior_acts(
    session_factory, tmp_path, monkeypatch, closure_qualifier=None
):
    monkeypatch.setenv("SMART_AO_L10_V2_PROOF_DIR", str(tmp_path / "l10-proof"))
    _changes(
        session_factory,
        tmp_path,
        monkeypatch,
        False,
        closure_qualifier=closure_qualifier,
        handover_runner=_repriced_handover,
    )
