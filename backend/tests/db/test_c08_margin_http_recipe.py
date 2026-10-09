"""Local synthetic PostgreSQL -> authenticated HTTP -> optional React proof."""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.infrastructure.models import (
    FinancialReportLineRecord,
    FinancialReportSnapshotRecord,
    PricingScenarioRecord,
)
from app.platform.security.models import AuthSessionRecord, IdentityRecord, TenantMembershipRecord
from tests.api.test_case_resolution_api import NOW, _client
from tests.application.test_financial_report_draft_lines import _seed_draft


def session_headers(session_factory, tokens, actor, strength="MFA"):
    with session_factory.begin() as session:
        session.add(
            AuthSessionRecord(
                id=actor.session_id,
                tenant_id=actor.tenant_id,
                membership_id=actor.membership_id,
                identity_id=actor.identity_id,
                state="ACTIVE",
                auth_strength=strength,
                token_version=1,
                issued_at=NOW,
                last_seen_at=NOW,
                expires_at=NOW + timedelta(hours=8),
                absolute_expires_at=NOW + timedelta(hours=12),
                mfa_verified_at=NOW if strength == "MFA" else None,
                revoked_at=None,
                revoke_reason=None,
            )
        )
    return {
        "Authorization": "Bearer "
        + tokens.issue(identity_id=actor.identity_id, session_id=actor.session_id, token_version=1)
    }


@pytest.mark.db
@pytest.mark.security
def test_c08_synthetic_margin_roundtrip_keeps_missing_inputs_unknown_and_permissions(
    session_factory,
):
    from dataclasses import replace

    with session_factory.begin() as session:
        session.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))
    patron, case_id, report_id, _ = _seed_draft(session_factory)
    client, tokens = _client(session_factory)
    headers = session_headers(session_factory, tokens, patron)
    path = f"/api/v1/patron/cases/{case_id}/financial-reports/{report_id}"
    inputs = [
        ("SALES", 100_003),
        ("DIRECT_COST", 60_001),
        ("OVERHEAD", 7_002),
        ("SUBCONTRACTING", 0),
        ("CONTINGENCY", 0),
    ]
    incomplete = None
    for revision, (category, amount) in enumerate(inputs):
        payload = {
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_revision": revision,
            "category": category,
            "label": "Poste synthétique " + category,
            "quantity_decimal": "1",
            "unit": "forfait",
            "amount_minor": amount,
        }
        if revision == 0:
            rejected = client.post(
                path + "/lines", headers=headers, json={**payload, "amount_minor": None}
            )
            assert rejected.status_code == 422
        written = client.post(path + "/lines", headers=headers, json=payload)
        assert written.status_code == 201, written.text
        replay = client.post(path + "/lines", headers=headers, json=payload)
        assert replay.status_code == 200 and replay.json()["replayed"] is True
        if revision == 0:
            incomplete = client.get(path + "/draft", headers=headers)
            assert incomplete.status_code == 200
            assert incomplete.json()["margin_calculation"]["state"] == "UNKNOWN"
            assert incomplete.json()["margin_calculation"]["gross_margin_minor"] is None
    complete = client.get(path + "/draft", headers=headers)
    assert complete.status_code == 200
    assert complete.headers["Cache-Control"] == "no-store"
    calculation = complete.json()["margin_calculation"]
    assert calculation["state"] == "CALCULATED"
    assert calculation["total_cost_minor"] == 67_003
    assert calculation["gross_margin_minor"] == 33_000
    assert calculation["gross_margin_rate_bps"] == 3299
    with session_factory() as session:
        lines = session.scalars(
            sa.select(FinancialReportLineRecord).where(
                FinancialReportLineRecord.snapshot_id == report_id
            )
        ).all()
        assert len(lines) == 5
        assert set(calculation["basis_line_ids"]) == {str(line.id) for line in lines}
        snapshot = session.get(FinancialReportSnapshotRecord, report_id)
        assert snapshot.aggregate_revision == 5
        assert snapshot.gross_margin_minor == snapshot.gross_margin_rate_bps == 0
        assert (
            session.scalar(
                sa.text("SELECT decision_readiness FROM cases WHERE id=:id"), {"id": case_id}
            )
            == "NOT_ASSESSED"
        )
        assert session.scalar(sa.text("SELECT count(*) FROM decisions")) == 0
    foreign, _, _, _ = _seed_draft(session_factory)
    foreign_headers = session_headers(session_factory, tokens, foreign)
    forbidden = client.get(path + "/draft", headers=foreign_headers)
    nonexistent = client.get(
        f"/api/v1/patron/cases/{uuid4()}/financial-reports/{uuid4()}/draft", headers=foreign_headers
    )
    assert forbidden.status_code == nonexistent.status_code == 404
    assert forbidden.json() == nonexistent.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    identity, membership = uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add(
            IdentityRecord(
                id=identity,
                email_normalized=f"synthetic-{identity}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        session.add(
            TenantMembershipRecord(
                id=membership,
                tenant_id=patron.tenant_id,
                identity_id=identity,
                role="COLLABORATEUR",
                operational_profile="RESPONSABLE",
                state="ACTIVE",
                activated_at=NOW,
            )
        )
    collaborator = replace(
        patron,
        actor_id=identity,
        identity_id=identity,
        membership_id=membership,
        session_id=uuid4(),
    )
    collaborator_headers = session_headers(session_factory, tokens, collaborator)
    refused = client.get(path + "/draft", headers=collaborator_headers)
    assert refused.status_code == 403 and refused.json() == {"detail": "FORBIDDEN"}
    password_only = replace(patron, session_id=uuid4())
    password_headers = session_headers(session_factory, tokens, password_only, "PASSWORD")
    refused_password = client.get(
        path + "/draft",
        headers=password_headers,
    )
    assert refused_password.status_code == 403
    assert "margin_calculation" not in refused_password.json()
    assert client.get(path, headers=headers).status_code == 404
    conflict = client.post(
        path + "/publications",
        headers=headers,
        json={"command_id": str(uuid4()), "idempotency_key": str(uuid4()), "expected_revision": 4},
    )
    assert conflict.status_code == 409 and conflict.json() == {"detail": "VERSION_CONFLICT"}
    publication = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "expected_revision": 5,
    }
    for refused_headers, expected_status in (
        (foreign_headers, 404),
        (collaborator_headers, 403),
        (password_headers, 403),
    ):
        denied_publication = client.post(
            path + "/publications", headers=refused_headers, json=publication
        )
        assert denied_publication.status_code == expected_status
        assert set(denied_publication.json()) == {"detail"}
    published = client.post(
        path + "/publications",
        headers=headers,
        json=publication,
    )
    assert published.status_code == 201, published.text
    replayed = client.post(path + "/publications", headers=headers, json=publication)
    assert replayed.status_code == 200 and replayed.json()["replayed"] is True
    assert replayed.json()["aggregate_refs"] == published.json()["aggregate_refs"]
    assert replayed.json()["event_ids"] == published.json()["event_ids"]
    published_read = client.get(path, headers=headers)
    assert published_read.status_code == 200
    assert published_read.json()["report_id"] == str(report_id)
    assert published_read.json()["case_id"] == str(case_id)
    assert published_read.json()["aggregate_revision"] == 6
    assert published.json()["aggregate_refs"][0]["aggregate_revision"] == 6
    assert published_read.json()["margin_calculation"] == calculation
    assert published_read.headers["Cache-Control"] == "no-store"
    for refused_headers, expected_status in (
        (foreign_headers, 404),
        (collaborator_headers, 403),
        (password_headers, 403),
    ):
        denied = client.get(path, headers=refused_headers)
        assert denied.status_code == expected_status
        assert set(denied.json()) == {"detail"}
    with session_factory() as session:
        assert session.get(FinancialReportSnapshotRecord, report_id).aggregate_revision == 6
        assert session.scalar(sa.select(sa.func.count()).select_from(PricingScenarioRecord)) == 0
        assert session.scalar(sa.text("SELECT count(*) FROM decisions")) == 0
    scenario_path = f"/api/v1/patron/cases/{case_id}/pricing-scenarios"
    command = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "scenario_id": str(uuid4()),
        "source_snapshot_id": str(report_id),
        "scenario_key": "SYNTHETIC_BASE",
        "scenario_type": "BASE",
        "sales_adjustment_bps": 0,
        "cost_adjustment_bps": 0,
        "penalty_reserve_minor": 0,
        "retention_reserve_minor": 0,
        "guarantee_reserve_minor": 0,
        "floor_margin_rate_bps": 500,
        "target_margin_rate_bps": 1000,
        "assumptions": {
            "note": "synthetic-local-only",
            "sales_adjustment_bps": 0,
            "cost_adjustment_bps": 0,
        },
    }
    created = client.post(scenario_path, headers=headers, json=command)
    assert created.status_code == 201, created.text
    replay = client.post(scenario_path, headers=headers, json=command)
    assert replay.status_code == 200 and replay.json()["replayed"] is True
    source_read = client.get(scenario_path, headers=headers)
    assert source_read.status_code == 200 and source_read.headers["Cache-Control"] == "no-store"
    scenario = source_read.json()[0]
    assert scenario["state"] == "DRAFT" and scenario["version"] == 1
    assert scenario["assumptions"] == command["assumptions"]
    for field in (
        "penalty_reserve_minor",
        "retention_reserve_minor",
        "guarantee_reserve_minor",
        "floor_margin_rate_bps",
        "target_margin_rate_bps",
    ):
        assert scenario[field] == command[field]
    assert scenario["source_snapshot_id"] == str(report_id)
    assert scenario["source_snapshot_revision"] == 6
    assert scenario["currency_code"] == "EUR"
    assert scenario["source_basis_state"] == "DECLARED_COMPLETE"
    assert scenario["source_basis_reason"] is None
    assert scenario["gross_margin_minor"] == 33_000 and scenario["gross_margin_rate_bps"] == 3299
    other_case_id = uuid4()
    with session_factory.begin() as session:
        original = session.get(CaseRecord, case_id)
        values = {
            attribute.key: getattr(original, attribute.key)
            for attribute in sa.inspect(CaseRecord).column_attrs
        }
        session.add(
            CaseRecord(**{**values, "id": other_case_id, "functional_identity_hash": "c" * 64})
        )
    assert (
        client.get(
            f"/api/v1/patron/cases/{other_case_id}/pricing-scenarios", headers=headers
        ).json()
        == []
    )
    for suffix, version, state in [("selection", 1, "SELECTED"), ("archive", 2, "ARCHIVED")]:
        transition = {
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "transition_id": str(uuid4()),
            "expected_version": version,
            "reason_code": "SYNTHETIC_REVIEW",
        }
        url = scenario_path + f"/{command['scenario_id']}/{suffix}"
        wrong_urls = [
            f"/api/v1/patron/cases/{scope}/pricing-scenarios/{command['scenario_id']}/{suffix}"
            for scope in (other_case_id, uuid4())
        ]
        for wrong_url in wrong_urls:
            refused_scope = client.post(wrong_url, headers=headers, json=transition)
            assert refused_scope.status_code == 422 and refused_scope.json() == {
                "detail": "NOT_FOUND_OR_FORBIDDEN"
            }
        for refused_headers, status_code, detail in (
            (foreign_headers, 422, "NOT_FOUND_OR_FORBIDDEN"),
            (collaborator_headers, 403, "FORBIDDEN"),
            (password_headers, 403, "STEP_UP_REQUIRED"),
        ):
            denied = client.post(url, headers=refused_headers, json=transition)
            assert denied.status_code == status_code
            assert denied.json() == {"detail": detail}
        invalid = client.post(url, headers=headers, json={**transition, "reason_code": "free text"})
        assert invalid.status_code == 422
        if suffix == "archive":
            rival = {
                **transition,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "transition_id": str(uuid4()),
            }
            start_race = Barrier(2)

            def archive(payload, *, barrier=start_race, endpoint=url):
                barrier.wait(timeout=5)
                return client.post(endpoint, headers=headers, json=payload)

            with ThreadPoolExecutor(max_workers=2) as executor:
                raced = list(executor.map(archive, [transition, rival]))
            assert sorted(response.status_code for response in raced) == [201, 409]
            loser = next(response for response in raced if response.status_code == 409)
            assert loser.json() == {"detail": "VERSION_CONFLICT"}
            if raced[1].status_code == 201:
                transition = rival
            accepted = next(response for response in raced if response.status_code == 201)
        else:
            accepted = client.post(url, headers=headers, json=transition)
        assert accepted.status_code == 201, accepted.text
        replay = client.post(url, headers=headers, json=transition)
        assert replay.status_code == 200 and replay.json()["replayed"] is True
        assert replay.json()["event_ids"] == accepted.json()["event_ids"]
        for wrong_url in wrong_urls:
            refused_replay = client.post(wrong_url, headers=headers, json=transition)
            assert refused_replay.status_code == 422 and refused_replay.json() == {
                "detail": "NOT_FOUND_OR_FORBIDDEN"
            }
        reused = client.post(
            url, headers=headers, json={**transition, "reason_code": "CHANGED_REASON"}
        )
        assert reused.status_code == 409 and reused.json() == {"detail": "IDEMPOTENCY_CONFLICT"}
        read = client.get(scenario_path, headers=headers).json()[0]
        assert read["state"] == state and read["version"] == version + 1
        assert (
            read["source_snapshot_id"] == str(report_id) and read["source_snapshot_revision"] == 6
        )
    foreign_command = {
        **command,
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "scenario_id": str(uuid4()),
    }
    foreign_create = client.post(scenario_path, headers=foreign_headers, json=foreign_command)
    assert foreign_create.status_code == 422 and foreign_create.json() == {
        "detail": "OFFICIAL_PRICE_NOT_PUBLISHED"
    }
    assert client.get(scenario_path, headers=foreign_headers).json() == []
    assert (
        client.get(
            f"/api/v1/patron/cases/{uuid4()}/pricing-scenarios", headers=foreign_headers
        ).json()
        == []
    )
    for refused_headers, expected_detail in [
        (
            session_headers(session_factory, tokens, replace(collaborator, session_id=uuid4())),
            "FORBIDDEN",
        ),
        (
            session_headers(
                session_factory, tokens, replace(password_only, session_id=uuid4()), "PASSWORD"
            ),
            "STEP_UP_REQUIRED",
        ),
    ]:
        response = client.get(scenario_path, headers=refused_headers)
        assert response.status_code == 403 and response.json() == {"detail": expected_detail}
    incomplete_actor, incomplete_case, incomplete_report, _ = _seed_draft(session_factory)
    incomplete_headers = session_headers(session_factory, tokens, incomplete_actor)
    incomplete_report_path = (
        f"/api/v1/patron/cases/{incomplete_case}/financial-reports/{incomplete_report}"
    )
    assert (
        client.post(
            incomplete_report_path + "/publications",
            headers=incomplete_headers,
            json={
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "expected_revision": 0,
            },
        ).status_code
        == 201
    )
    incomplete_scenario_path = f"/api/v1/patron/cases/{incomplete_case}/pricing-scenarios"
    incomplete_published = client.get(incomplete_report_path, headers=incomplete_headers)
    assert incomplete_published.json()["status"] == "PUBLISHED"
    assert incomplete_published.json()["aggregate_revision"] == 1
    assert incomplete_published.json()["margin_calculation"]["state"] == "UNKNOWN"
    incomplete_command = {
        **command,
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "scenario_id": str(uuid4()),
        "source_snapshot_id": str(incomplete_report),
    }
    for _ in range(2):
        refused = client.post(
            incomplete_scenario_path, headers=incomplete_headers, json=incomplete_command
        )
        assert refused.status_code == 422 and refused.json() == {
            "detail": "SCENARIO_SOURCE_UNKNOWN"
        }
    with session_factory.begin() as session:
        assert session.get(PricingScenarioRecord, incomplete_command["scenario_id"]) is None
        session.add(
            PricingScenarioRecord(
                id=uuid4(),
                tenant_id=incomplete_actor.tenant_id,
                case_id=incomplete_case,
                source_snapshot_id=incomplete_report,
                source_snapshot_revision=1,
                scenario_key="SYNTHETIC_HISTORY",
                scenario_type="BASE",
                version=1,
                state="DRAFT",
                assumptions_json={},
                sales_total_minor=0,
                total_cost_minor=0,
                gross_margin_minor=0,
                gross_margin_rate_bps=0,
                actor_id=incomplete_actor.actor_id,
                membership_id=incomplete_actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
        assert (
            session.scalar(
                sa.text("SELECT count(*) FROM pricing_scenarios WHERE tenant_id=:tenant"),
                {"tenant": patron.tenant_id},
            )
            == 1
        )
        assert (
            session.scalar(
                sa.text(
                    "SELECT count(*) FROM pricing_scenario_transitions WHERE tenant_id=:tenant"
                ),
                {"tenant": patron.tenant_id},
            )
            == 2
        )
        assert session.scalar(sa.text("SELECT count(*) FROM decisions")) == 0
        assert (
            session.scalar(
                sa.text("SELECT decision_readiness FROM cases WHERE id=:id"), {"id": case_id}
            )
            == "NOT_ASSESSED"
        )
    historical_read = client.get(incomplete_scenario_path, headers=incomplete_headers)
    assert historical_read.status_code == 200
    assert historical_read.json()[0]["source_basis_state"] == "UNKNOWN"
    assert historical_read.json()[0]["source_basis_reason"] == "MISSING_BASE_CATEGORY"
    historical = historical_read.json()[0]
    historical_archive = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "transition_id": str(uuid4()),
        "expected_version": historical["version"],
        "reason_code": "HUMAN_RETIRED_HISTORY",
    }
    archived_history = client.post(
        incomplete_scenario_path + f"/{historical['scenario_id']}/archive",
        headers=incomplete_headers,
        json=historical_archive,
    )
    assert archived_history.status_code == 201
    history_after = client.get(incomplete_scenario_path, headers=incomplete_headers).json()[0]
    assert history_after["state"] == "ARCHIVED" and history_after["version"] == 2
    assert history_after["source_basis_state"] == "UNKNOWN"
    assert history_after["source_snapshot_id"] == historical["source_snapshot_id"]
    assert history_after["source_snapshot_revision"] == historical["source_snapshot_revision"]
    with session_factory() as session:
        immutable = session.get(PricingScenarioRecord, command["scenario_id"])
        assert immutable.state == "DRAFT" and immutable.version == 1
        assert immutable.source_snapshot_revision == 6
        assert session.scalar(sa.text("SELECT count(*) FROM decisions")) == 0
    if output := os.environ.get("SMART_AO_C08_HTTP_PROOF"):
        assert incomplete is not None
        Path(output).write_text(
            json.dumps(
                {
                    "complete": complete.json(),
                    "incomplete": incomplete.json(),
                    "scenarios_complete": source_read.json(),
                    "scenarios_incomplete": historical_read.json(),
                }
            ),
            encoding="utf-8",
        )
        Path(output).chmod(0o600)
