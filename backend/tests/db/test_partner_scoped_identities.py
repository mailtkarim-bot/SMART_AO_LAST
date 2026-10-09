"""Public UUIDs retain their values and are isolated by tenant and Case."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.modules.partner.application.partner_handler import (
    CasePartnerService,
    partner_event_handlers,
)
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.modules.pricing.application.partner_offer_price_handler import (
    PartnerOfferPriceService,
    partner_offer_price_handlers,
)
from app.modules.pricing.infrastructure.models.partner_offer_line_comparison import (
    PartnerOfferLineComparisonRecord,
)
from app.modules.pricing.infrastructure.models.partner_offer_price import (
    PartnerOfferPriceDeclarationRecord,
)
from app.modules.pricing.infrastructure.models.partner_offer_scope_review import (
    PartnerOfferScopeReviewRecord,
)
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD
from app.platform.security.authorization import AuthorizationPolicy
from tests.db.test_case_partner_events import _request
from tests.db.test_partner_offer_identity_audit import isolated_disposable_records  # noqa: F401
from tests.db.test_partner_offer_line_comparison import _line_command, _line_service
from tests.db.test_partner_offer_price import _command as price_command
from tests.db.test_partner_offer_scope_review import NOW, _receipt, _seed
from tests.db.test_partner_offer_scope_review import _command as scope_command
from tests.db.test_regulatory_profile_persistence import _case
from tests.support.database import ALEMBIC_INI, DATABASE_URL

ROOTS: dict[
    str,
    tuple[
        type[CasePartnerEventRecord]
        | type[PartnerOfferPriceDeclarationRecord]
        | type[PartnerOfferScopeReviewRecord]
        | type[PartnerOfferLineComparisonRecord],
        str,
    ],
] = {
    "event": (CasePartnerEventRecord, "event_id"),
    "price": (PartnerOfferPriceDeclarationRecord, "id"),
    "scope": (PartnerOfferScopeReviewRecord, "id"),
    "line": (PartnerOfferLineComparisonRecord, "id"),
}


def _config():
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    return config


def _prepare(kind, scope, engine, factory, public_id):
    tenant, case, actor, scope_service = scope
    if kind == "event":
        service = CasePartnerService(
            session_factory=factory,
            policy=AuthorizationPolicy(),
            dispatcher=CommandDispatcher(
                session_factory=factory, handlers=partner_event_handlers()
            ),
        )
        request = _request(case, uuid4()).model_copy(update={"event_id": public_id})
        return request, lambda: service.record_request(actor=actor, command=request, now=NOW)
    receipts = tuple(
        _receipt(engine, tenant_id=tenant, case_id=case, actor=actor, label=label)[0]
        for label in ["A", "B"]
    )
    if kind == "price":
        price_service = PartnerOfferPriceService(
            session_factory=factory,
            policy=AuthorizationPolicy(),
            dispatcher=CommandDispatcher(
                session_factory=factory, handlers=partner_offer_price_handlers()
            ),
        )
        request = price_command(case, receipts[0]).model_copy(update={"declaration_id": public_id})
        return request, lambda: price_service.declare(actor=actor, command=request, now=NOW)
    parent = scope_command(case, uuid4(), receipts)
    if kind == "scope":
        parent = parent.model_copy(update={"review_id": public_id})
        return parent, lambda: scope_service.record(actor=actor, command=parent, now=NOW)
    scope_service.record(actor=actor, command=parent, now=NOW)
    service = _line_service(factory)
    request = _line_command(case, parent.review_id, receipts, unknown=True).model_copy(
        update={"record_id": public_id}
    )
    return request, lambda: service.record(actor=actor, command=request, now=NOW)


@pytest.mark.parametrize("kind", ROOTS)
@pytest.mark.parametrize("other_scope", ["tenant", "case"])
def test_identical_public_ids_do_not_collide_or_merge_orm_entities(
    database_engine, session_factory, kind, other_scope
):
    first = _seed(database_engine, session_factory)
    if other_scope == "tenant":
        second = _seed(database_engine, session_factory)
    else:
        tenant, _, actor, service = first
        case = uuid4()
        with session_factory.begin() as session:
            session.add(_case(tenant_id=tenant, case_id=case, marker="q"))
        second = (tenant, case, actor, service)
    identity = uuid4()
    _, write_first = _prepare(kind, first, database_engine, session_factory, identity)
    _, write_second = _prepare(kind, second, database_engine, session_factory, identity)
    assert write_first().replayed is False
    assert write_second().replayed is False
    assert write_second().replayed is True
    model, field = ROOTS[kind]
    with session_factory() as session:
        rows = session.scalars(sa.select(model).where(getattr(model, field) == identity)).all()
        assert len(rows) == 2 and rows[0] is not rows[1]
        assert {(row.tenant_id, row.case_id) for row in rows} == {
            (first[0], first[1]),
            (second[0], second[1]),
        }
        for scope in [first, second]:
            assert session.get(model, (scope[0], scope[1], identity)).case_id == scope[1]
    assert tuple(column.name for column in model.__table__.primary_key) == (
        "tenant_id",
        "case_id",
        field,
    )


@pytest.mark.parametrize("kind", ROOTS)
def test_simultaneous_foreign_scopes_can_use_the_same_id(database_engine, session_factory, kind):
    identity = uuid4()
    first = _seed(database_engine, session_factory)
    second = _seed(database_engine, session_factory)
    _, one = _prepare(kind, first, database_engine, session_factory, identity)
    _, two = _prepare(kind, second, database_engine, session_factory, identity)
    barrier = Barrier(2)

    def write(operation):
        barrier.wait(timeout=10)
        return operation()

    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(write, operation) for operation in [one, two]]
        assert all(job.result(timeout=30).replayed is False for job in jobs)
    assert one().replayed is True and two().replayed is True


@pytest.mark.parametrize("kind", ROOTS)
def test_same_scope_collision_has_one_effect_and_remains_replayable(
    database_engine, session_factory, kind
):
    from app.platform.events.dispatcher import CommandExecutionError

    identity = uuid4()
    scope = _seed(database_engine, session_factory)
    _, one = _prepare(kind, scope, database_engine, session_factory, identity)
    _, two = _prepare(kind, scope, database_engine, session_factory, identity)
    barrier = Barrier(2)

    def write(operation):
        barrier.wait(timeout=10)
        try:
            return operation()
        except CommandExecutionError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(write, operation) for operation in [one, two]]
        results = [job.result(timeout=30) for job in jobs]
    assert sum(not isinstance(result, str) for result in results) == 1
    error = next(result for result in results if isinstance(result, str))
    assert error.endswith("ID_REUSED")
    model, field = ROOTS[kind]
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(model)
                .where(
                    model.tenant_id == scope[0],
                    model.case_id == scope[1],
                    getattr(model, field) == identity,
                )
            )
            == 1
        )
    assert [one, two][
        next(index for index, result in enumerate(results) if not isinstance(result, str))
    ]().replayed is True


@pytest.mark.parametrize("kind", ROOTS)
def test_downgrade_refuses_repeated_identity_atomically(database_engine, session_factory, kind):
    identity = uuid4()
    first = _seed(database_engine, session_factory)
    second = _seed(database_engine, session_factory)
    _, one = _prepare(kind, first, database_engine, session_factory, identity)
    _, two = _prepare(kind, second, database_engine, session_factory, identity)
    one()
    two()
    with pytest.raises(RuntimeError, match="identities repeat across scopes"):
        command.downgrade(_config(), "20261005_0132")
    with database_engine.connect() as connection:
        assert (
            connection.scalar(sa.text("SELECT version_num FROM alembic_version"))
            == EXPECTED_ALEMBIC_HEAD
        )
    for model, field in ROOTS.values():
        assert sa.inspect(database_engine).get_pk_constraint(model.__tablename__)[
            "constrained_columns"
        ] == ["tenant_id", "case_id", field]
    assert one().replayed and two().replayed


def test_upgrade_downgrade_reupgrade_preserves_historical_rows_and_links(
    database_engine, session_factory
):
    config = _config()
    command.downgrade(config, "20261005_0132")
    scope = _seed(database_engine, session_factory)
    for kind in ROOTS:
        _, operation = _prepare(kind, scope, database_engine, session_factory, uuid4())
        operation()
    tables = [model.__tablename__ for model, _ in ROOTS.values()] + [
        "partner_offer_scope_review_offers",
        "partner_offer_line_groups",
        "partner_offer_line_members",
        "domain_events",
        "command_receipts",
    ]

    def snapshot():
        with database_engine.connect() as connection:
            return {
                table: connection.execute(
                    sa.text(
                        f"SELECT row_to_json(row)::text FROM {table} row "
                        "ORDER BY row_to_json(row)::text"
                    )
                )
                .scalars()
                .all()
                for table in tables
            }

    before = snapshot()
    command.upgrade(config, "head")
    assert snapshot() == before
    command.downgrade(config, "20261005_0132")
    assert snapshot() == before
    command.upgrade(config, "head")
    assert snapshot() == before
    parent = next(
        fk
        for fk in sa.inspect(database_engine).get_foreign_keys("case_partner_events")
        if "related_event_id" in fk["constrained_columns"]
    )
    assert parent["constrained_columns"] == ["tenant_id", "case_id", "related_event_id"]
    assert parent["referred_columns"] == ["tenant_id", "case_id", "event_id"]


def test_upgrade_rejects_historical_cross_case_parent_without_rewriting(
    database_engine, session_factory
):
    config = _config()
    command.downgrade(config, "20261005_0132")
    scope = _seed(database_engine, session_factory)
    parent, write = _prepare("event", scope, database_engine, session_factory, uuid4())
    write()
    second_case, child_id = uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add(_case(tenant_id=scope[0], case_id=second_case, marker="q"))
        session.flush()
        session.add(
            CasePartnerEventRecord(
                event_id=child_id,
                tenant_id=scope[0],
                case_id=second_case,
                partner_id=uuid4(),
                revision=1,
                event_type="RECEIVED",
                partner_kind="SUPPLIER",
                partner_label="Synthetic inconsistent history",
                related_event_id=parent.event_id,
                source_locator="fixture://bad-history",
                rationale="Synthetic only",
                valid_until=None,
                validity_at_recording="UNKNOWN",
                exclusions_state="UNKNOWN",
                exclusions_json=[],
                mandate_state="NOT_APPLICABLE",
                actor_id=scope[2].actor_id,
                membership_id=scope[2].membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
    with pytest.raises(RuntimeError, match="historical parent belongs to another Case"):
        command.upgrade(config, "head")
    with database_engine.connect() as connection:
        assert (
            connection.scalar(sa.text("SELECT version_num FROM alembic_version")) == "20261005_0132"
        )
        assert (
            connection.scalar(
                sa.text("SELECT related_event_id FROM case_partner_events WHERE event_id=:id"),
                {"id": child_id},
            )
            == parent.event_id
        )
    assert sa.inspect(database_engine).get_pk_constraint("case_partner_events")[
        "constrained_columns"
    ] == ["event_id"]
