"""Resolve exact sources for a human operational handover, without private text."""

import hashlib
from uuid import UUID

import sqlalchemy as sa

from app.modules.patron_action.application.operational_handover import (
    PUBLICATION_POLICY,
    canonical_sha256,
    review_context_sha256,
)
from app.modules.preparation.infrastructure.models import GeneratedTechnicalDocumentRecord
from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
    ContractInstrumentSupersessionRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.events.dispatcher import CommandExecutionError


def instrument_record(record):
    return {
        "instrument_version_id": str(record.id),
        "instrument_kind": record.instrument_kind,
        "version_reference": record.version_reference,
        "source_refs": record.source_refs_json,
        "evidence_refs": record.evidence_refs_json,
    }


def enrich_operational_handover(
    session, *, snapshot, case, package, review, revision, condition_ids, context, storage
):
    expected_context = review_context_sha256(
        scope_fingerprint=case.scope_fingerprint,
        dce_version_id=case.applicable_dce_version_id,
        decision_id=snapshot["decision"].get("decision_id"),
        decision_revision=snapshot["decision"].get("revision"),
    )
    if review.expected_source_context_sha256 != expected_context:
        raise CommandExecutionError("HANDOVER_CASE_CONTEXT_CONFLICT")
    if review.expected_handover_revision != revision - 1:
        raise CommandExecutionError("VERSION_CONFLICT")
    if review.expected_offer_manifest_sha256 != package.manifest_sha256:
        raise CommandExecutionError("HANDOVER_OFFER_VERSION_CONFLICT")
    if any(
        point.condition_id is not None and point.condition_id not in condition_ids
        for point in review.points
    ):
        raise CommandExecutionError("HANDOVER_CONDITION_SOURCE_MISMATCH")
    if storage is None:
        raise CommandExecutionError("HANDOVER_DOCUMENT_STORAGE_UNAVAILABLE")
    document = session.scalar(
        sa.select(GeneratedTechnicalDocumentRecord)
        .where(
            GeneratedTechnicalDocumentRecord.tenant_id == context.tenant_id,
            GeneratedTechnicalDocumentRecord.package_id == package.preparation_package_id,
            GeneratedTechnicalDocumentRecord.id == package.technical_document_id,
            GeneratedTechnicalDocumentRecord.version == package.technical_document_version,
        )
        .with_for_update(nowait=True)
    )
    if (
        document is None
        or document.document_kind != "TECHNICAL_RESPONSE"
        or document.state != "GENERATED"
        or document.content_sha256 != snapshot["offer"]["technical_document_sha256"]
    ):
        raise CommandExecutionError("HANDOVER_OFFER_DOCUMENT_NOT_VERIFIED")
    try:
        content = storage.read(storage_key=document.storage_key)
    except OSError as error:
        raise CommandExecutionError("HANDOVER_OFFER_DOCUMENT_UNKNOWN") from error
    if hashlib.sha256(content).hexdigest() != document.content_sha256:
        raise CommandExecutionError("HANDOVER_OFFER_DOCUMENT_HASH_MISMATCH")
    comparison = {"state": "UNKNOWN", "authority_state": "UNKNOWN", "file_sha256": "UNKNOWN"}
    if review.contract_instrument_version_id is not None:
        instrument = session.scalar(
            sa.select(ContractInstrumentVersionRecord)
            .where(
                ContractInstrumentVersionRecord.tenant_id == context.tenant_id,
                ContractInstrumentVersionRecord.case_id == case.id,
                ContractInstrumentVersionRecord.id == review.contract_instrument_version_id,
            )
            .with_for_update(nowait=True)
        )
        if instrument is None:
            raise CommandExecutionError("HANDOVER_CONTRACT_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(
            sa.select(ContractInstrumentSupersessionRecord.id)
            .where(
                ContractInstrumentSupersessionRecord.tenant_id == context.tenant_id,
                ContractInstrumentSupersessionRecord.case_id == case.id,
                ContractInstrumentSupersessionRecord.replaced_contract_instrument_version_id
                == instrument.id,
            )
            .limit(1)
        ):
            raise CommandExecutionError("HANDOVER_CONTRACT_SUPERSEDED")
        record_sha = canonical_sha256(instrument_record(instrument))
        if record_sha != review.expected_contract_record_sha256:
            raise CommandExecutionError("HANDOVER_CONTRACT_VERSION_CONFLICT")
        comparison.update(
            state="HUMAN_DECLARED_LINK",
            instrument_version_id=str(instrument.id),
            instrument_kind=instrument.instrument_kind,
            record_sha256=record_sha,
            declared_reference_state="HUMAN_DECLARED_NOT_EXTERNAL_VERIFICATION",
        )
    proofs = {}
    regions = _docx_body_regions(content) if document.content_format == "DOCX" else ()
    for point in review.points:
        excerpt = point.offer_excerpt.encode() if point.offer_excerpt else None
        state, start, end = unique_excerpt_offsets(content, excerpt)
        location = (
            docx_excerpt_proof(content, excerpt, regions=regions)
            if document.content_format == "DOCX"
            else {"state": state, "start_byte_offset": start, "end_byte_offset": end}
        )
        proofs[str(point.point_id)] = {
            **location,
            "document_id": str(document.id),
            "document_version": document.version,
            "source_sha256": document.content_sha256,
            "contract_excerpt_state": "HUMAN_LOCATOR_ONLY" if point.contract_locator else "UNKNOWN",
        }
    snapshot.update(
        schema_version=2,
        contract_comparison=comparison,
        offer_point_proofs=proofs,
        source_context={
            "case_scope_fingerprint": case.scope_fingerprint,
            "case_dce_version_id": str(case.applicable_dce_version_id)
            if case.applicable_dce_version_id
            else None,
            "decision_id": snapshot["decision"].get("decision_id"),
            "decision_revision": snapshot["decision"].get("revision"),
        },
        operational_review={
            **review.model_dump(mode="json"),
            "publication_policy": PUBLICATION_POLICY,
            "publisher_id": str(context.actor_id),
            "published_at": context.received_at.isoformat(),
        },
    )
    return snapshot


def current_handover_view(session, record, *, storage=None):
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.decision.infrastructure.models.decision import DecisionRecord
    from app.modules.patron_action.application.operational_handover import public_handover_snapshot
    from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
    from app.modules.patron_action.infrastructure.models.outcome import CaseOutcomeRecord

    data = public_handover_snapshot(record.snapshot_json)
    reasons = []
    historical = False
    case = session.scalar(
        sa.select(CaseRecord).where(
            CaseRecord.tenant_id == record.tenant_id, CaseRecord.id == record.case_id
        )
    )
    latest = session.scalar(
        sa.select(CaseHandoverSnapshotRecord.id)
        .where(
            CaseHandoverSnapshotRecord.tenant_id == record.tenant_id,
            CaseHandoverSnapshotRecord.outcome_id == record.outcome_id,
        )
        .order_by(CaseHandoverSnapshotRecord.revision.desc())
        .limit(1)
    )
    latest_outcome = session.scalar(
        sa.select(CaseOutcomeRecord.id)
        .where(
            CaseOutcomeRecord.tenant_id == record.tenant_id,
            CaseOutcomeRecord.case_id == record.case_id,
            CaseOutcomeRecord.lot_reference == record.lot_reference,
        )
        .order_by(CaseOutcomeRecord.created_at.desc(), CaseOutcomeRecord.id.desc())
        .limit(1)
    )
    if latest != record.id:
        reasons.append("NEWER_HANDOVER")
        historical = True
    if latest_outcome != record.outcome_id:
        reasons.append("OUTCOME_CHANGED")
        historical = True
    captured = data["source_context"]
    if case is None or case.lifecycle != "ACTIVE":
        reasons.append("CASE_NOT_ACTIVE")
    if (
        not captured
        or case is not None
        and (
            captured.get("case_scope_fingerprint") != case.scope_fingerprint
            or captured.get("case_dce_version_id") != str(case.applicable_dce_version_id)
        )
    ):
        reasons.append("CASE_SOURCE_REVIEW_REQUIRED")
    if case is not None and case.dce_freshness != "CURRENT":
        reasons.append("DCE_REVIEW_REQUIRED")
    comparison = data["contract_comparison"]
    if comparison.get("instrument_version_id"):
        contract_id = UUID(comparison["instrument_version_id"])
        contract = session.scalar(
            sa.select(ContractInstrumentVersionRecord).where(
                ContractInstrumentVersionRecord.tenant_id == record.tenant_id,
                ContractInstrumentVersionRecord.case_id == record.case_id,
                ContractInstrumentVersionRecord.id == contract_id,
            )
        )
        if contract is None or canonical_sha256(instrument_record(contract)) != comparison.get(
            "record_sha256"
        ):
            reasons.append("CONTRACT_SOURCE_REVIEW_REQUIRED")
        if session.scalar(
            sa.select(ContractInstrumentSupersessionRecord.id)
            .where(
                ContractInstrumentSupersessionRecord.tenant_id == record.tenant_id,
                ContractInstrumentSupersessionRecord.case_id == record.case_id,
                ContractInstrumentSupersessionRecord.replaced_contract_instrument_version_id
                == contract_id,
            )
            .limit(1)
        ):
            reasons.append("CONTRACT_SUPERSEDED")
    else:
        reasons.append("CONTRACT_LINK_UNKNOWN")
    if captured.get("decision_id"):
        decision = session.scalar(
            sa.select(DecisionRecord).where(
                DecisionRecord.tenant_id == record.tenant_id,
                DecisionRecord.case_id == record.case_id,
                DecisionRecord.id == UUID(captured["decision_id"]),
            )
        )
        if (
            decision is None
            or decision.aggregate_revision != captured.get("decision_revision")
            or decision.validity != "CURRENT"
        ):
            reasons.append("DECISION_REVIEW_REQUIRED")
    from app.modules.decision.infrastructure.analysis_reference import (
        assessment_reference_is_current,
    )
    from app.modules.decision.infrastructure.models.decision import DecisionContextReferenceRecord
    from app.modules.submission.infrastructure.models import SubmissionPackageRecord

    package = session.scalar(
        sa.select(SubmissionPackageRecord).where(
            SubmissionPackageRecord.tenant_id == record.tenant_id,
            SubmissionPackageRecord.case_id == record.case_id,
            SubmissionPackageRecord.id == record.submission_package_id,
        )
    )
    document = (
        session.scalar(
            sa.select(GeneratedTechnicalDocumentRecord).where(
                GeneratedTechnicalDocumentRecord.tenant_id == record.tenant_id,
                GeneratedTechnicalDocumentRecord.id == package.technical_document_id,
                GeneratedTechnicalDocumentRecord.package_id == package.preparation_package_id,
                GeneratedTechnicalDocumentRecord.version == package.technical_document_version,
            )
        )
        if package is not None
        else None
    )
    file_state = "UNKNOWN"
    if storage is not None and package is not None and document is not None:
        try:
            payload = storage.read(storage_key=document.storage_key)
            if (
                canonical_sha256(package.manifest_json) == record.manifest_sha256
                and document.content_sha256 == data["offer"].get("technical_document_sha256")
                and hashlib.sha256(payload).hexdigest() == document.content_sha256
            ):
                file_state = "REVALIDATED_BYTES"
        except (OSError, ValueError):
            file_state = "UNKNOWN"
    if file_state != "REVALIDATED_BYTES":
        reasons.append("OFFER_DOCUMENT_REVIEW_REQUIRED")
    context_id = data["decision"].get("context_id")
    if context_id:
        from app.modules.decision.infrastructure.capacity_reference import (
            capacity_reference_is_current,
        )

        references = session.scalars(
            sa.select(DecisionContextReferenceRecord).where(
                DecisionContextReferenceRecord.tenant_id == record.tenant_id,
                DecisionContextReferenceRecord.decision_context_id == UUID(context_id),
                DecisionContextReferenceRecord.aggregate_type.in_(
                    ("ANALYSIS_ASSESSMENT", "CAPACITY_RUN")
                ),
            )
        ).all()
        if any(
            not (
                capacity_reference_is_current
                if reference.aggregate_type == "CAPACITY_RUN"
                else assessment_reference_is_current
            )(
                session,
                tenant_id=record.tenant_id,
                case_id=record.case_id,
                aggregate_id=reference.aggregate_id,
                aggregate_revision=reference.aggregate_revision,
                content_hash=reference.content_hash,
            )
            for reference in references
        ):
            reasons.append("DECISION_SOURCE_REVIEW_REQUIRED")
    data["offer"]["file_revalidation_state"] = file_state
    state = "HISTORICAL" if historical else "REVIEW_REQUIRED" if reasons else "CURRENT"
    fingerprint = canonical_sha256(
        {
            "snapshot_id": str(record.id),
            "revision": record.revision,
            "snapshot": data,
            "source_state": state,
            "source_reasons": reasons,
        }
    )
    return data, state, tuple(reasons), fingerprint


def unique_excerpt_offsets(content, excerpt):
    first = content.find(excerpt) if excerpt else -1
    if first < 0:
        return "UNKNOWN", None, None
    if content.find(excerpt, first + 1) >= 0:
        return "AMBIGUOUS", None, None
    return "EXACT_BYTE_MATCH", first, first + len(excerpt)


def lock_handover_sources(session, snapshot):
    """Writers lock the exact decision/contract referenced by the immutable handover."""
    from app.modules.decision.infrastructure.models.decision import DecisionRecord
    from app.modules.pricing.infrastructure.models.contract_instrument_version import (
        ContractInstrumentVersionRecord,
    )

    for model, identity in (
        (DecisionRecord, snapshot.snapshot_json.get("decision", {}).get("decision_id")),
        (
            ContractInstrumentVersionRecord,
            snapshot.snapshot_json.get("contract_comparison", {}).get("instrument_version_id"),
        ),
    ):
        if identity:
            session.scalar(
                sa.select(model)
                .where(
                    model.tenant_id == snapshot.tenant_id,
                    model.case_id == snapshot.case_id,
                    model.id == UUID(identity),
                )
                .with_for_update(nowait=True)
            )


def _docx_body_regions(content):
    from app.modules.preparation.infrastructure.buyer_docx import NS, W, _package, _xml

    try:
        _, parts, root = _package(content)
        body = root.find("w:body", NS)
        if body is None:
            return ()
        # Conservatively refuse hidden style/default declarations rather than guess inheritance.
        styles = _xml(parts["word/styles.xml"]) if "word/styles.xml" in parts else None
        hidden_styles = styles is not None and bool(
            styles.xpath(".//w:vanish | .//w:webHidden", namespaces=NS)
        )
        part_sha = hashlib.sha256(parts["word/document.xml"]).hexdigest()
        regions = []
        for paragraph in body.findall(f".//{{{W}}}p"):
            text = ""
            for node in paragraph.iter():
                if node.tag == f"{{{W}}}t":
                    text += node.text or ""
                elif node.tag == f"{{{W}}}br":
                    text += "\n"
                elif node.tag == f"{{{W}}}tab":
                    text += "\t"
            parent = paragraph.getparent()
            direct = parent is body
            cell = parent if parent.tag == f"{{{W}}}tc" else None
            row = cell.getparent() if cell is not None else None
            table = row.getparent() if row is not None and row.tag == f"{{{W}}}tr" else None
            simple_cell = (
                table is not None
                and table.tag == f"{{{W}}}tbl"
                and table.getparent() is body
                and not table.xpath(".//w:tbl | .//w:gridSpan | .//w:vMerge", namespaces=NS)
            )
            simple = (
                (direct or simple_cell)
                and not hidden_styles
                and all(n.tag in {f"{{{W}}}pPr", f"{{{W}}}r"} for n in paragraph)
                and all(
                    n.tag in {f"{{{W}}}rPr", f"{{{W}}}t", f"{{{W}}}br", f"{{{W}}}tab"}
                    for run in paragraph.findall("w:r", NS)
                    for n in run
                )
                and not paragraph.xpath(".//w:vanish | .//w:webHidden", namespaces=NS)
            )
            regions.append(
                (
                    "word/document.xml:" + root.getroottree().getpath(paragraph),
                    text.encode(),
                    part_sha,
                    simple,
                )
            )
        return tuple(regions)
    except (ValueError, OSError):
        return ()


def docx_excerpt_proof(content, excerpt, *, regions=None):
    # Offsets are within a paragraph's UTF-8 text, never fabricated ZIP byte offsets.
    unknown = {"state": "UNKNOWN", "start_byte_offset": None, "end_byte_offset": None}
    if not excerpt:
        return unknown
    matches = []
    for locator, text, part_sha, simple in (
        _docx_body_regions(content) if regions is None else regions
    ):
        state, start, end = unique_excerpt_offsets(text, excerpt)
        if state != "UNKNOWN":
            matches.append((state, start, end, locator, text, part_sha, simple))
    if not matches:
        return unknown
    if len(matches) != 1 or matches[0][0] == "AMBIGUOUS":
        return {**unknown, "state": "AMBIGUOUS"}
    _, start, end, locator, text, part_sha, simple = matches[0]
    if not simple:
        return unknown
    return {
        **unknown,
        "state": "EXACT_DOCX_TEXT_MATCH",
        "locator": locator,
        "part_sha256": part_sha,
        "text_sha256": hashlib.sha256(text).hexdigest(),
        "text_start_byte_offset": start,
        "text_end_byte_offset": end,
    }
