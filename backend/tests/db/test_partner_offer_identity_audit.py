"""Scoped identities must not disclose another tenant through an unknown source."""

import os
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.patron_partner_offer_prices import _command_error
from app.platform.events.dispatcher import CommandExecutionError
from tests.db.test_partner_offer_price import NOW, _command, _received, _seed


@pytest.fixture(autouse=True)
def isolated_disposable_records(database_engine):
    if os.environ.get("SMART_AO_TEST_DISPOSABLE_DATABASE") != "1" or not os.environ.get(
        "SMART_AO_TEST_DATABASE_URL"
    ):
        pytest.skip("Explicit disposable PostgreSQL required for collision fixtures")
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))
    yield
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))


def test_unknown_source_must_not_disclose_foreign_price_declaration_identity(
    database_engine, session_factory
):
    _, case_a, actor_a, service_a = _seed(database_engine, session_factory)
    tenant_b, case_b, actor_b, service_b = _seed(database_engine, session_factory)
    source_b, _ = _received(database_engine, tenant_id=tenant_b, case_id=case_b, actor=actor_b)
    declaration_b = _command(case_b, source_b)
    service_b.declare(actor=actor_b, command=declaration_b, now=NOW)
    unknown_source = uuid4()
    observations = []
    for declaration_id in [declaration_b.declaration_id, uuid4()]:
        candidate = _command(case_a, unknown_source).model_copy(
            update={"declaration_id": declaration_id}
        )
        with pytest.raises(CommandExecutionError) as failure:
            service_a.declare(actor=actor_a, command=candidate, now=NOW)
        response = _command_error(failure.value)
        observations.append((response.status_code, response.detail))
    assert observations == [(404, "NOT_FOUND_OR_FORBIDDEN")] * 2


def test_valid_source_accepts_an_identity_used_only_in_another_tenant(
    database_engine, session_factory
):
    tenant_a, case_a, actor_a, service_a = _seed(database_engine, session_factory)
    tenant_b, case_b, actor_b, service_b = _seed(database_engine, session_factory)
    source_b, _ = _received(database_engine, tenant_id=tenant_b, case_id=case_b, actor=actor_b)
    source_a, _ = _received(database_engine, tenant_id=tenant_a, case_id=case_a, actor=actor_a)
    declaration_b = _command(case_b, source_b)
    service_b.declare(actor=actor_b, command=declaration_b, now=NOW)
    own = _command(case_a, source_a).model_copy(
        update={"declaration_id": declaration_b.declaration_id}
    )
    result = service_a.declare(actor=actor_a, command=own, now=NOW)
    assert result.result_code == "PARTNER_OFFER_PRICE_DECLARED"
    assert service_a.declare(actor=actor_a, command=own, now=NOW).replayed is True
