"""Synthetic workbook to costing and human partner reconciliation, same Affair."""

from dataclasses import asdict
from datetime import UTC, datetime
from uuid import UUID, uuid4

from tests.application.test_pricing_import_commit import _command, _service
from tests.db.test_partner_offer_line_comparison import _line_command, _line_service
from tests.db.test_partner_offer_scope_review import _command as scope_command
from tests.db.test_partner_offer_scope_review import _offer, _receipt
from tests.db.test_pricing_positions import source_setup
from tests.db.test_pricing_positions import workflow as workflow


def test_workbook_costing_and_incomparable_partner_units_remain_sourced(
    database_engine, session_factory, workflow
):
    from app.modules.pricing.application.partner_offer_scope_review_handler import (
        PartnerOfferScopeReviewService,
        partner_offer_scope_review_handlers,
    )
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy

    client, actor, case, report = workflow
    url, _, body, read, _ = source_setup(session_factory, workflow)
    batch = UUID(url.split("/")[-2])
    command = _command(case, report, batch, expected_report_revision=1)
    service = _service(session_factory)
    now = datetime.now(UTC)
    assert not service.commit(actor=actor, command=command, now=now).replayed
    assert service.commit(actor=actor, command=command, now=now).replayed
    data = read()
    assert len(data["positions"]) == 2
    assert all(position["coverage_state"] == "UNKNOWN" for position in data["positions"])
    assert {position["import_source"]["unit"] for position in data["positions"]} == {
        "u",
        "forfait",
    }
    point = data["positions"][0]
    cost = next(cost for cost in data["sources"]["costs"] if cost["label"] == "Pompe achetée")
    body.update(
        position_context_sha256=point["position_context_sha256"],
        cost_refs=[dict(line_id=cost["line_id"], report_revision=cost["report_revision"])],
    )
    endpoint = f"{url}/{point['position_id']}/reviews"
    headers = {"Authorization": "Bearer synthetic"}
    response = client.post(endpoint, json=body, headers=headers)
    assert response.status_code == 201, response.text
    replay = client.post(endpoint, json=body, headers=headers)
    assert replay.status_code == 200 and replay.json()["replayed"]
    current = read()
    assert current["positions"][0]["declared_cost_minor"] == "12000"
    assert current["positions"][1]["cost_state"] == "UNKNOWN"
    assert current["positions"][1]["declared_cost_minor"] is None
    assert current["coverage_state"] == "UNKNOWN"

    receipt_ids = tuple(
        _receipt(
            database_engine,
            tenant_id=actor.tenant_id,
            case_id=case,
            actor=actor,
            label=label,
        )[0]
        for label in ("L06-pieces", "L06-forfait")
    )
    scopes = PartnerOfferScopeReviewService(
        dispatcher=CommandDispatcher(
            session_factory=session_factory, handlers=partner_offer_scope_review_handlers()
        ),
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    )
    scope = scope_command(
        case,
        uuid4(),
        receipt_ids,
        offers=[_offer(receipt_ids[0], transport_state="EXCLUDED"), _offer(receipt_ids[1])],
    )
    scopes.record(actor=actor, command=scope, now=now)
    line = _line_command(case, scope.review_id, receipt_ids)
    group = line.groups[0]
    members = tuple(
        member.model_copy(update={"unit": unit})
        for member, unit in zip(group.members, ("u", "forfait"), strict=True)
    )
    line = line.model_copy(update={"groups": (group.model_copy(update={"members": members}),)})
    lines = _line_service(session_factory)
    assert not lines.record(actor=actor, command=line, now=now).replayed
    assert lines.record(actor=actor, command=line, now=now).replayed
    projection = lines.list_for_case(actor=actor, case_id=case, now=now)
    result = asdict(projection)
    current = result["comparisons"][0]["groups"][0]
    assert current["disposition"] == "NEEDS_CLARIFICATION"
    assert {member["unit"] for member in current["members"]} == {"u", "forfait"}
    assert all(member["source_locator"] for member in current["members"])
    assert "unit_price" not in str(result)
    assert read()["coverage_state"] == "UNKNOWN"
