"""Local JWT/AppRuntime receipt lineage, scoped identities and human acts only."""

from dataclasses import replace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.platform.security.models import IdentityRecord, TenantMembershipRecord
from tests.api.test_case_resolution_api import NOW, _client
from tests.application.test_financial_report_draft_lines import _seed_draft
from tests.db.test_c08_margin_http_recipe import session_headers
from tests.db.test_partner_offer_identity_audit import isolated_disposable_records  # noqa: F401
from tests.db.test_partner_offer_line_comparison import _line_command
from tests.db.test_partner_offer_scope_review import _command as scope_command
from tests.db.test_regulatory_profile_persistence import _case


def _keys():
    return {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
    }


def _post_twice(client, path, headers, payload):
    first = client.post(path, headers=headers, json=payload)
    assert first.status_code == 201, first.text
    retry = client.post(path, headers=headers, json=payload)
    assert retry.status_code == 200 and retry.json()["replayed"] is True, retry.text
    return first


def _flow(client, case_id, headers, ids, amount):
    c09 = f"/api/v1/cases/{case_id}/partners"
    c08 = f"/api/v1/patron/cases/{case_id}"
    request = {
        **_keys(),
        "case_id": str(case_id),
        "event_id": str(ids["request"]),
        "partner_id": str(ids["partner_a"]),
        "expected_revision": 0,
        "partner_kind": "SUPPLIER",
        "partner_label": "SYNTHETIC a",
        "source_locator": "fixture://request",
        "rationale": "Local synthetic declaration; no external dispatch",
    }
    _post_twice(client, c09 + "/requests", headers, request)
    receipts = []
    for suffix, revision, kind, mandate in [
        ("a", 1, "SUPPLIER", "NOT_APPLICABLE"),
        ("b", 0, "CO_CONTRACTOR", "UNKNOWN"),
    ]:
        receipt = {
            **_keys(),
            "case_id": str(case_id),
            "event_id": str(ids["receipt_" + suffix]),
            "partner_id": str(ids["partner_" + suffix]),
            "expected_revision": revision,
            "request_event_id": str(ids["request"]) if suffix == "a" else None,
            "partner_kind": kind,
            "partner_label": "SYNTHETIC " + suffix,
            "source_locator": f"fixture://{amount}/response-{suffix}",
            "rationale": "Synthetic receipt only",
            "valid_until": None,
            "exclusions_state": "DECLARED",
            "exclusions": [],
            "mandate_state": mandate,
            "mandate_source_locator": None,
        }
        _post_twice(client, c09 + "/receipts", headers, receipt)
        receipts.append(ids["receipt_" + suffix])
    price = {
        **_keys(),
        "declaration_id": str(ids["price"]),
        "expected_revision": 0,
        "amount_as_declared": amount,
        "currency_code": "EUR",
    }
    _post_twice(client, c08 + f"/partner-offer-prices/{receipts[0]}/declarations", headers, price)
    scope = scope_command(case_id, ids["comparison"], tuple(receipts)).model_copy(
        update={"review_id": ids["review"]}
    )
    _post_twice(
        client,
        c08 + "/partner-offer-scope-reviews",
        headers,
        scope.model_dump(mode="json", exclude={"case_id"}),
    )
    lines = _line_command(case_id, scope.review_id, tuple(receipts), unknown=True).model_copy(
        update={"record_id": ids["lines"]}
    )
    _post_twice(
        client,
        c08 + "/partner-offer-line-comparisons",
        headers,
        lines.model_dump(mode="json", exclude={"case_id"}),
    )
    history = client.get(c09, headers=headers).json()
    assert {item["event_type"] for item in history["events"]} == {"REQUESTED", "RECEIVED"}
    assert all(item["validity_current"] == "UNKNOWN" for item in history["events"])
    prices = client.get(c08 + "/partner-offer-prices", headers=headers).json()
    assert prices["offers"][0]["declarations"][0]["amount_as_declared"] == amount
    assert all(item["validity_current"] == "UNKNOWN" for item in prices["offers"])
    line_read = client.get(c08 + "/partner-offer-line-comparisons", headers=headers).json()[
        "comparisons"
    ][0]
    assert (
        line_read["scope_review_id"] == str(ids["review"])
        and line_read["scope_review_revision"] == 1
    )
    assert line_read["requires_reassessment"] is False
    for member in line_read["groups"][0]["members"]:
        assert member["quantity_state"] == "UNKNOWN" and member["quantity"] is None
    assert "sha256" not in str(history) and "amount_as_declared" not in str(line_read)
    _post_twice(
        client,
        c09 + "/engagements",
        headers,
        {
            **_keys(),
            "case_id": str(case_id),
            "event_id": str(ids["first_engagement"]),
            "partner_id": str(ids["partner_a"]),
            "expected_revision": 2,
            "receipt_event_id": str(receipts[0]),
            "source_locator": "fixture://first-separate-human-act",
            "rationale": "Human fixture only",
        },
    )
    return c09, c08, receipts, scope, lines


@pytest.mark.parametrize("second_scope", ["tenant", "case"])
def test_real_jwt_case_partner_price_scope_line_history_and_scoped_collisions(
    session_factory, monkeypatch, second_scope
):
    from app.interfaces.http.routes import (
        case_partners,
        patron_partner_offer_line_comparisons,
        patron_partner_offer_prices,
        patron_partner_offer_scope_reviews,
    )

    class RecipeClock:
        @staticmethod
        def now(tz=None):
            return NOW

    for module in [
        case_partners,
        patron_partner_offer_prices,
        patron_partner_offer_scope_reviews,
        patron_partner_offer_line_comparisons,
    ]:
        monkeypatch.setattr(module, "datetime", RecipeClock)
    patron_a, case_a, _, _ = _seed_draft(session_factory)
    if second_scope == "tenant":
        patron_b, case_b, _, _ = _seed_draft(session_factory)
    else:
        patron_b, case_b = patron_a, uuid4()
        with session_factory.begin() as session:
            session.add(_case(tenant_id=patron_a.tenant_id, case_id=case_b, marker="q"))
    client, tokens = _client(session_factory)
    headers_a = session_headers(session_factory, tokens, patron_a)
    headers_b = (
        session_headers(session_factory, tokens, patron_b)
        if second_scope == "tenant"
        else headers_a
    )
    ids = {
        key: uuid4()
        for key in [
            "request",
            "partner_a",
            "partner_b",
            "receipt_a",
            "receipt_b",
            "price",
            "comparison",
            "review",
            "lines",
            "first_engagement",
        ]
    }
    c09, c08, receipts, scope, lines = _flow(client, case_a, headers_a, ids, "100.00")
    _, other_c08, _, _, _ = _flow(client, case_b, headers_b, ids, "900.00")
    foreign_only = uuid4()
    _post_twice(
        client,
        other_c08 + f"/partner-offer-prices/{ids['receipt_a']}/declarations",
        headers_b,
        {
            **_keys(),
            "declaration_id": str(foreign_only),
            "expected_revision": 1,
            "amount_as_declared": "901.00",
            "currency_code": "EUR",
        },
    )
    unknown = uuid4()
    for candidate in [foreign_only, uuid4()]:
        refused = client.post(
            c08 + f"/partner-offer-prices/{unknown}/declarations",
            headers=headers_a,
            json={
                **_keys(),
                "declaration_id": str(candidate),
                "expected_revision": 0,
                "amount_as_declared": "100.00",
                "currency_code": "EUR",
            },
        )
        assert refused.status_code == 404 and refused.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    for revision, candidate in [(1, foreign_only), (2, uuid4())]:
        _post_twice(
            client,
            c08 + f"/partner-offer-prices/{ids['receipt_a']}/declarations",
            headers_a,
            {
                **_keys(),
                "declaration_id": str(candidate),
                "expected_revision": revision,
                "amount_as_declared": "100.00",
                "currency_code": "EUR",
            },
        )
    assert "900.00" not in client.get(c08 + "/partner-offer-prices", headers=headers_a).text
    assert "901.00" not in client.get(c08 + "/partner-offer-prices", headers=headers_a).text
    if second_scope == "tenant":
        assert client.get(c08 + "/partner-offer-prices", headers=headers_b).json()["offers"] == []
    # A cotraitant's unknown mandate cannot become engagement merely through price/comparison.
    forbidden = client.post(
        c09 + "/engagements",
        headers=headers_a,
        json={
            **_keys(),
            "case_id": str(case_a),
            "event_id": str(uuid4()),
            "partner_id": str(ids["partner_b"]),
            "expected_revision": 1,
            "receipt_event_id": str(ids["receipt_b"]),
            "source_locator": "fixture://human-act",
            "rationale": "Synthetic human declaration",
        },
    )
    assert (
        forbidden.status_code == 422
        and forbidden.json()["detail"] == "PARTNER_MANDATE_NOT_RECEIVED"
    )
    # A new review of the same fixed member set invalidates prior line parent revision.
    same_members = scope_command(case_a, ids["comparison"], tuple(receipts), expected_revision=1)
    _post_twice(
        client,
        c08 + "/partner-offer-scope-reviews",
        headers_a,
        same_members.model_dump(mode="json", exclude={"case_id"}),
    )
    prior_line = client.get(c08 + "/partner-offer-line-comparisons", headers=headers_a).json()[
        "comparisons"
    ][0]
    assert (
        prior_line["scope_review_id"] == str(ids["review"])
        and prior_line["requires_reassessment"] is True
    )
    new_receipt = uuid4()
    _post_twice(
        client,
        c09 + "/receipts",
        headers_a,
        {
            **_keys(),
            "case_id": str(case_a),
            "event_id": str(new_receipt),
            "partner_id": str(ids["partner_a"]),
            "expected_revision": 3,
            "request_event_id": None,
            "partner_kind": "SUPPLIER",
            "partner_label": "SYNTHETIC a",
            "source_locator": "fixture://response-a/v2",
            "rationale": "Synthetic replacement",
            "valid_until": None,
            "exclusions_state": "DECLARED",
            "exclusions": [],
            "mandate_state": "NOT_APPLICABLE",
        },
    )
    old_prices = client.get(c08 + "/partner-offer-prices", headers=headers_a).json()["offers"]
    assert (
        next(item for item in old_prices if item["receipt_event_id"] == str(receipts[0]))[
            "is_latest_receipt"
        ]
        is False
    )
    old_scope = client.get(c08 + "/partner-offer-scope-reviews", headers=headers_a).json()[
        "reviews"
    ][0]
    assert old_scope["requires_reassessment"] is True and old_scope["review_id"] == str(
        ids["review"]
    )
    old_lines = client.get(c08 + "/partner-offer-line-comparisons", headers=headers_a).json()[
        "comparisons"
    ][0]
    assert old_lines["requires_reassessment"] is True and old_lines["record_id"] == str(
        ids["lines"]
    )
    stale = lines.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "record_id": uuid4(),
            "expected_revision": 1,
        }
    )
    assert (
        client.post(
            c08 + "/partner-offer-line-comparisons",
            headers=headers_a,
            json=stale.model_dump(mode="json", exclude={"case_id"}),
        ).status_code
        == 409
    )
    refreshed = scope_command(case_a, uuid4(), (new_receipt, ids["receipt_b"]), expected_revision=0)
    _post_twice(
        client,
        c08 + "/partner-offer-scope-reviews",
        headers_a,
        refreshed.model_dump(mode="json", exclude={"case_id"}),
    )
    engagement = {
        **_keys(),
        "case_id": str(case_a),
        "event_id": str(uuid4()),
        "partner_id": str(ids["partner_a"]),
        "expected_revision": 4,
        "receipt_event_id": str(new_receipt),
        "source_locator": "fixture://separate-human-act",
        "rationale": "Human fixture act; not external confirmation",
    }
    _post_twice(client, c09 + "/engagements", headers_a, engagement)
    history = client.get(c09, headers=headers_a).json()["events"]
    declared = next(item for item in history if item["event_id"] == engagement["event_id"])
    assert (
        declared["related_event_id"] == str(new_receipt)
        and declared["validity_current"] == "UNKNOWN"
    )
    # JWT role resolution, not a hand-constructed ActorContext, protects C08 financial views.
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
                tenant_id=patron_a.tenant_id,
                identity_id=identity,
                role="COLLABORATEUR",
                operational_profile="RESPONSABLE",
                state="ACTIVE",
                activated_at=NOW,
            )
        )
    collaborator = replace(
        patron_a,
        identity_id=identity,
        actor_id=identity,
        membership_id=membership,
        session_id=uuid4(),
    )
    collab_headers = session_headers(session_factory, tokens, collaborator)
    for suffix in [
        "partner-offer-prices",
        "partner-offer-scope-reviews",
        "partner-offer-line-comparisons",
    ]:
        refusal = client.get(c08 + "/" + suffix, headers=collab_headers)
        assert refusal.status_code == 403 and refusal.json() == {"detail": "FORBIDDEN"}
    with session_factory() as session:
        assert session.scalar(sa.text("SELECT count(*) FROM decisions")) == 0
        assert session.scalar(sa.text("SELECT count(*) FROM financial_report_lines")) == 0
        for case in [case_a, case_b]:
            assert (
                session.scalar(
                    sa.text("SELECT decision_readiness FROM cases WHERE id=:id"), {"id": case}
                )
                == "NOT_ASSESSED"
            )
