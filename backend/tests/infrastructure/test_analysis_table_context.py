"""Discordant adapter projections never become exact table evidence."""

from dataclasses import asdict, replace
from hashlib import sha256
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.modules.case.infrastructure import analysis_table_context as context
from app.modules.dce.application.source_anchor_projection import (
    DceSourceAnchorProjection,
    resolve_dce_source_locator,
)


@pytest.mark.parametrize(
    "fault",
    ["none", "version", "identity", "ordinal", "cached_identity", "source_locator", "source_hash"],
)
def test_table_context_requires_exact_fragment_identity(monkeypatch, fault):
    version, tenant, extraction, document, fragment = (uuid4() for _ in range(5))
    text = "Lot 2 : ne pas intervenir si le support est refusé."
    locator = resolve_dce_source_locator(
        dict(kind="docx_table_cell", table=1, row=1, column=1, paragraph=1)
    )
    a = DceSourceAnchorProjection(
        fragment,
        version,
        document,
        extraction,
        1,
        "a" * 64,
        "smart-ao-deterministic",
        "4",
        sha256(text.encode()).hexdigest(),
        locator,
    )
    source = dict(asdict(a), locator_state="RESOLVED")
    if fault == "source_locator":
        source = dict(
            source,
            locator=dict(
                source["locator"], coordinates=dict(table=1, row=9, column=1, paragraph=1)
            ),
        )
    if fault == "source_hash":
        source = dict(source, fragment_sha256="0" * 64)
    item = dict(source_anchor=source)
    changes = {
        "none": {},
        "version": dict(dce_version_id=uuid4()),
        "identity": dict(source_anchor_id=uuid4()),
        "ordinal": dict(fragment_ordinal=2),
        "cached_identity": {},
        "source_locator": {},
        "source_hash": {},
    }
    projected = replace(a, **changes[fault])

    class Reader:
        def get_many(self, **kwargs):
            return {fragment: projected}

    monkeypatch.setattr(context, "SqlAlchemyDceSourceAnchorReader", Reader)
    row = SimpleNamespace(id=fragment, text=text, ordinal=1)
    session = SimpleNamespace(scalars=lambda stmt: [row])
    items = [item]
    if fault == "cached_identity":
        items.append(dict(source_anchor=dict(source, source_anchor_id=uuid4())))
    context.attach_table_contexts(session, tenant_id=tenant, version=version, items=items)
    result = items[-1]["table_context"]
    assert result["state"] == ("EXACT_SOURCE" if fault == "none" else "UNKNOWN")
    assert bool(result["cells"]) == (fault == "none")
