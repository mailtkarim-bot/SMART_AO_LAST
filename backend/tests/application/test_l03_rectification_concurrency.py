from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Event, get_ident
from uuid import uuid4

import sqlalchemy as sa
from app.modules.case.application.commands import LinkCaseDceVersionCommand
from app.modules.case.application.link_dce_version_handler import LinkCaseDceVersionHandler
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application.commands import RegisterDceVersionCommand
from app.modules.dce.application.handlers import RegisterDceVersionHandler
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError

from tests.application.test_register_dce_version import (
    _command,
    _context,
    _hash_manifest,
    _seed_clean_staged_objects,
    _seed_consultation,
)
from tests.db.test_regulatory_profile_persistence import _case


def test_new_case_link_cannot_escape_concurrent_rectification(database_engine, session_factory):
    tenant, consultation = _seed_consultation(session_factory)
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "RegisterDceVersion": RegisterDceVersionHandler(),
            "LinkCaseDceVersion": LinkCaseDceVersionHandler(),
        },
    )
    old = _command(consultation_id=consultation)
    _seed_clean_staged_objects(
        session_factory, tenant_id=tenant, consultation_id=consultation, command=old
    )
    dispatcher.dispatch(command=old, context=_context(tenant))
    case_id = uuid4()
    with session_factory.begin() as s:
        case = _case(tenant_id=tenant, case_id=case_id, marker="e")
        case.consultation_id = consultation
        s.add(case)
    fresh = _command(consultation_id=consultation).model_copy(
        update={"corpus_hash": _hash_manifest("e" * 64, "b" * 64)}
    )
    _seed_clean_staged_objects(
        session_factory,
        tenant_id=tenant,
        consultation_id=consultation,
        command=fresh,
        first_hash="e" * 64,
    )
    rectified = RegisterDceVersionCommand.model_validate(
        {
            **fresh.model_dump(),
            "provenance_channel": "RECTIFICATION",
            "predecessor_dce_version_id": old.dce_version_id,
            "expected_predecessor_revision": 0,
            "replacement_reason": "Rectificatif synthétique exact.",
        }
    )
    selected, release, link_done = Event(), Event(), Event()
    worker: list[int] = []

    def pause_after_case_selection(conn, cursor, statement, parameters, context, executemany):
        if (
            worker
            and get_ident() == worker[0]
            and "cases.applicable_dce_version_id" in statement
            and "FOR UPDATE" in statement
        ):
            selected.set()
            assert release.wait(10), "test barrier not released"

    def rectify():
        worker.append(get_ident())
        return dispatcher.dispatch(command=rectified, context=_context(tenant))

    def link():
        try:
            return dispatcher.dispatch(
                command=LinkCaseDceVersionCommand(
                    command_id=uuid4(),
                    idempotency_key=uuid4(),
                    case_id=case_id,
                    dce_version_id=old.dce_version_id,
                    expected_case_revision=1,
                    reason="Rattachement synthétique concurrent.",
                ),
                context=replace(_context(tenant), case_id=case_id),
            )
        except CommandExecutionError:
            return None
        finally:
            link_done.set()

    sa.event.listen(database_engine, "after_cursor_execute", pause_after_case_selection)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            replacement = pool.submit(rectify)
            assert selected.wait(10)
            linking = pool.submit(link)
            link_done.wait(2)
            release.set()
            replacement.result(timeout=10)
            linking.result(timeout=10)
    finally:
        release.set()
        sa.event.remove(database_engine, "after_cursor_execute", pause_after_case_selection)
    with session_factory() as s:
        case = s.get(CaseRecord, case_id)
        assert case is not None
        assert case.applicable_dce_version_id is None or case.dce_freshness == "REVIEW_REQUIRED"
