"""Closed DCE provenance snapshot for a human response contribution."""

import hashlib
import json
from dataclasses import asdict
from types import SimpleNamespace
from typing import Any
from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.case_dce_reading_reader import SqlAlchemyCaseDceReadingReader
from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionFragmentRecord
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.modules.membership.public.text_safety import contains_forbidden_text
from app.platform.events.dispatcher import CommandExecutionError


def contribution_source_snapshots(session, *, tenant_id, case_id, dce_version_id, contributions):
    for model, condition, identity in [
        (CaseRecord, CaseRecord.id == case_id, CaseRecord.id),
        (
            DceRequirementRecord,
            DceRequirementRecord.id.in_([item.requirement_id for item in contributions]),
            DceRequirementRecord.id,
        ),
        (
            DceDocumentRecord,
            DceDocumentRecord.dce_version_id == dce_version_id,
            DceDocumentRecord.id,
        ),
        (DceVersionRecord, DceVersionRecord.id == dce_version_id, DceVersionRecord.id),
    ]:
        session.scalars(
            sa.select(model)
            .where(model.tenant_id == tenant_id, condition)
            .order_by(identity)
            .execution_options(populate_existing=True)
            .with_for_update(nowait=True)
        ).all()
    lookup = SqlAlchemyCaseDceReadingReader(session).get(tenant_id=tenant_id, case_id=case_id)
    if (
        lookup is None
        or lookup.reading is None
        or lookup.reading.dce_version_id != dce_version_id
        or lookup.dce_freshness != "CURRENT"
        or lookup.case_lifecycle != "ACTIVE"
        or lookup.reading.lifecycle != "ADMITTED"
        or lookup.reading.integrity != "VERIFIED"
    ):
        raise CommandExecutionError("CONTRIBUTION_SOURCE_UNKNOWN")
    scope_fingerprint = session.scalar(
        sa.select(CaseRecord.scope_fingerprint).where(
            CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id
        )
    )
    requirements = {point.requirement_id: point for point in lookup.reading.requirements}
    result = {}
    for contribution in contributions:
        point = requirements.get(contribution.requirement_id)
        source: dict[str, Any] = {
            "dce_version_id": str(dce_version_id),
            "requirement_id": str(contribution.requirement_id),
            "source_state": "UNKNOWN",
            "lot": "UNKNOWN",
            "case_scope_fingerprint": scope_fingerprint,
        }
        if point is not None and point.document_family not in {"DPGF", "BPU"}:
            source.update(
                confirmation_revision=point.confirmation_revision,
                document_family=point.document_family,
                locator=point.source_locator_label,
            )
            anchor = point.source_anchor
            if (
                point.source_proof_state == "CURRENT_SOURCE"
                and anchor is not None
                and point.confirmation_outcome == "CONFIRMED"
                and point.confirmation_revision is not None
            ):
                source.update(
                    anchor=asdict(anchor),
                    source_state="CURRENT_SOURCE",
                    start_byte_offset=point.source_start_byte_offset,
                    end_byte_offset=point.source_end_byte_offset,
                )
                fragment = session.scalar(
                    sa.select(DceDocumentExtractionFragmentRecord).where(
                        DceDocumentExtractionFragmentRecord.tenant_id == tenant_id,
                        DceDocumentExtractionFragmentRecord.id == anchor.source_anchor_id,
                    )
                )
                start, end = point.source_start_byte_offset, point.source_end_byte_offset
                if (
                    fragment is not None
                    and start is not None
                    and end is not None
                    and hashlib.sha256(fragment.text.encode()).hexdigest() == anchor.fragment_sha256
                ):
                    try:
                        quote = fragment.text.encode()[start:end].decode("utf-8")
                    except UnicodeDecodeError:
                        quote = ""
                    if quote and not contains_forbidden_text(quote):
                        source["buyer_excerpt"] = quote
        if contribution.content and (
            source["source_state"] != "CURRENT_SOURCE" or not source.get("buyer_excerpt")
        ):
            raise CommandExecutionError("CONTRIBUTION_SOURCE_UNKNOWN")
        result[contribution.requirement_id] = source
    return result


CONTRIBUTION_SOURCE_PREFIX = "- Sources résolues côté serveur : "


def validate_contribution_sources(session, *, tenant_id, case_id, dce_version_id, content):
    rows = [
        line[len(CONTRIBUTION_SOURCE_PREFIX) :]
        for line in content.splitlines()
        if line.startswith(CONTRIBUTION_SOURCE_PREFIX)
    ]
    if not rows:
        return
    try:
        if len(rows) > 64:
            raise ValueError("contribution budget")
        stored = [json.loads(line) for line in rows]
        contributions = [
            SimpleNamespace(
                requirement_id=UUID(item["buyer"]["requirement_id"]),
                content="present",
            )
            for item in stored
        ]
        identities = [(item["buyer"]["requirement_id"], item["section_code"]) for item in stored]
        if len(identities) != len(set(identities)):
            raise ValueError("duplicate contribution")
        current = contribution_source_snapshots(
            session,
            tenant_id=tenant_id,
            case_id=case_id,
            dce_version_id=dce_version_id,
            contributions=contributions,
        )
        for item, contribution in zip(stored, contributions, strict=True):
            if (
                json.loads(json.dumps(current[contribution.requirement_id], default=str))
                != item["buyer"]
            ):
                raise ValueError("stale contribution source")
    except (KeyError, TypeError, ValueError) as error:
        raise CommandExecutionError("CONTRIBUTION_SOURCE_UNKNOWN") from error
