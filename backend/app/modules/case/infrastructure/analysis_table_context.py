"""Bounded geometric context, never inherited lot or obligation semantics."""

from dataclasses import asdict
from hashlib import sha256
from typing import Any
from uuid import UUID

import sqlalchemy as sa

from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord as Fragment,
)
from app.modules.dce.infrastructure.source_anchor_reader import SqlAlchemyDceSourceAnchorReader

MAX_TABLE_FRAGMENTS = 64
MAX_TABLE_BYTES = 16000
MAX_TABLE_CONTEXTS = 16


def attach_table_contexts(session, *, tenant_id, version, items):
    cache: dict[tuple[UUID, int], dict[str, Any]] = {}
    reader = SqlAlchemyDceSourceAnchorReader()
    for item in items:
        source = item.get("source_anchor")
        locator = source.get("locator") if source else None
        if not locator or locator["kind"] != "docx_table_cell":
            continue
        unknown = dict(
            state="UNKNOWN", cells=[], applicability="UNKNOWN", unknown_reason="SOURCE_UNPROVEN"
        )
        item["table_context"] = unknown
        if source["locator_state"] != "RESOLVED":
            continue
        table = locator["coordinates"]["table"]
        key = (source["extraction_id"], table)
        if key in cache:
            cached = cache[key]
            if cached["state"] == "UNKNOWN" or any(
                cell["source_anchor"] == source for cell in cached["cells"]
            ):
                item["table_context"] = cached
            continue
        if len(cache) >= MAX_TABLE_CONTEXTS:
            unknown["unknown_reason"] = "READ_BUDGET_EXCEEDED"
            continue
        rows = list(
            session.scalars(
                sa.select(Fragment)
                .where(
                    Fragment.tenant_id == tenant_id,
                    Fragment.extraction_id == source["extraction_id"],
                    Fragment.locator_json["table"].as_string() == str(table),
                )
                .order_by(Fragment.ordinal)
                .limit(MAX_TABLE_FRAGMENTS + 1)
            )
        )
        cache[key] = unknown
        if (
            len(rows) > MAX_TABLE_FRAGMENTS
            or sum(len(r.text.encode()) for r in rows) > MAX_TABLE_BYTES
        ):
            unknown["unknown_reason"] = "READ_BUDGET_EXCEEDED"
            continue
        try:
            anchors = reader.get_many(
                session=session,
                tenant_id=tenant_id,
                dce_version_id=version,
                fragment_ids=[r.id for r in rows],
            )
        except ValueError:
            continue
        cells = []
        for row in rows:
            anchor = anchors.get(row.id)
            if (
                anchor is None
                or anchor.source_anchor_id != row.id
                or anchor.fragment_ordinal != row.ordinal
                or anchor.dce_version_id != version
                or anchor.locator is None
                or anchor.locator.kind.value != "docx_table_cell"
                or anchor.locator.coordinates["table"] != table
                or anchor.extraction_id != source["extraction_id"]
                or anchor.dce_document_id != source["dce_document_id"]
                or anchor.source_sha256 != source["source_sha256"]
                or anchor.fragment_sha256 != sha256(row.text.encode()).hexdigest()
                or not row.text
                or len(row.text.encode()) > 8000
            ):
                break
            cells.append(
                dict(
                    text=row.text,
                    source_anchor=dict(asdict(anchor), locator_state=anchor.locator_state.value),
                )
            )
        else:
            if cells and any(cell["source_anchor"] == source for cell in cells):
                cache[key] = dict(
                    state="EXACT_SOURCE", cells=cells, applicability="UNKNOWN", unknown_reason=None
                )
                item["table_context"] = cache[key]
