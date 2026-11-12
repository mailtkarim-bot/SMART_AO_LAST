"""Case dossier composition over existing DCE and patron risk registers."""

from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.application.analysis_summary import (
    build_analysis_summary,
    exact_source_excerpt,
)
from app.modules.case.infrastructure.analysis_follow_up_reader import attach_analysis_follow_ups
from app.modules.case.infrastructure.analysis_table_context import attach_table_contexts
from app.modules.dce.application.classification import current_completed_extraction_condition
from app.modules.dce.infrastructure.case_dce_reading_reader import SqlAlchemyCaseDceReadingReader
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord as Fragment,
)
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionRecord as Extraction,
)
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord as Document
from app.modules.dce.infrastructure.source_anchor_reader import SqlAlchemyDceSourceAnchorReader
from app.modules.decision.infrastructure.models.risk import DecisionRiskRecord
from app.modules.decision.infrastructure.risk_repository import SqlAlchemyDecisionRiskRepository


class SqlAlchemyCaseAnalysisSummaryReader:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, *, tenant_id: UUID, case_id: UUID, include_follow_ups: bool = True):
        lookup = SqlAlchemyCaseDceReadingReader(self._session).get(
            tenant_id=tenant_id, case_id=case_id
        )
        if lookup is None:
            return None
        reading = lookup.reading
        if reading is None:
            raise ValueError("CURRENT_DCE_UNAVAILABLE")
        version = reading.dce_version_id
        risks = list(
            self._session.scalars(
                sa.select(DecisionRiskRecord)
                .where(
                    DecisionRiskRecord.tenant_id == tenant_id,
                    DecisionRiskRecord.case_id == case_id,
                    DecisionRiskRecord.dce_version_id == version,
                )
                .order_by(DecisionRiskRecord.id)
                .limit(101)
            )
        )
        requirements = reading.requirements[:200]
        ids = {r.source_fragment_id for r in risks[:100]}
        ids.update(
            r.source_anchor.source_anchor_id for r in requirements if r.source_anchor is not None
        )
        rows = (
            self._session.execute(
                sa.select(Fragment, Extraction, Document)
                .join(
                    Extraction,
                    sa.and_(
                        Extraction.tenant_id == Fragment.tenant_id,
                        Extraction.id == Fragment.extraction_id,
                    ),
                )
                .join(
                    Document,
                    sa.and_(
                        Document.tenant_id == Extraction.tenant_id,
                        Document.id == Extraction.dce_document_id,
                        Document.dce_version_id == Extraction.dce_version_id,
                    ),
                )
                .where(
                    Fragment.tenant_id == tenant_id,
                    Fragment.id.in_(ids),
                    Extraction.dce_version_id == version,
                    Extraction.status == "COMPLETED",
                    current_completed_extraction_condition(tenant_id=tenant_id),
                )
            ).all()
            if ids
            else []
        )
        admissible = (
            lookup.dce_freshness == "CURRENT"
            and reading.lifecycle == "ADMITTED"
            and reading.integrity == "VERIFIED"
        )
        sources = {}
        anchor_reader = SqlAlchemyDceSourceAnchorReader()
        for fragment, extraction, document in rows:
            if not admissible:
                continue
            if (
                sha256(fragment.text.encode()).hexdigest() != fragment.text_sha256
                or extraction.input_sha256 != document.sha256
            ):
                continue
            try:
                anchor = anchor_reader.get(
                    session=self._session, tenant_id=tenant_id, fragment_id=fragment.id
                )
            except ValueError:
                continue
            if anchor is not None:
                sources[fragment.id] = (fragment, anchor)

        def provenance(source):
            if source is None:
                return None
            anchor = source[1]
            return dict(asdict(anchor), locator_state=anchor.locator_state.value)

        req_items = []
        for r in requirements:
            source = (
                sources.get(r.source_anchor.source_anchor_id)
                if r.source_anchor is not None
                else None
            )
            if r.source_proof_state != "CURRENT_SOURCE":
                source = None
            candidate = r.structured_candidate
            excerpt = (
                exact_source_excerpt(
                    source[0].text, r.source_start_byte_offset, r.source_end_byte_offset
                )
                if source
                else None
            )
            req_items.append(
                dict(
                    item_id=r.requirement_id,
                    native_revision=r.confirmation_revision or 0,
                    kind="REQUIREMENT",
                    native_type=r.requirement_type,
                    native_state=r.confirmation_outcome,
                    title=None,
                    source_excerpt=excerpt,
                    source_excerpt_state="EXACT_SOURCE" if excerpt is not None else "UNKNOWN",
                    source_excerpt_unknown_reason=None
                    if excerpt is not None
                    else "READ_BUDGET_EXCEEDED"
                    if source
                    else "SOURCE_UNPROVEN",
                    severity="UNKNOWN",
                    source_state="CURRENT_SOURCE" if source else "UNKNOWN",
                    source_anchor=provenance(source),
                    start_byte_offset=r.source_start_byte_offset if source else None,
                    end_byte_offset=r.source_end_byte_offset if source else None,
                    lot_numbers=list(candidate.lot_numbers) if source and candidate else [],
                    lot_state="CANDIDATE"
                    if source and candidate and candidate.lot_state == "CANDIDATE"
                    else "UNKNOWN",
                )
            )
        risk_items = []
        for r in risks[:100]:
            snapshot = SqlAlchemyDecisionRiskRepository().get_current(
                session=self._session, tenant_id=tenant_id, case_id=case_id, risk_id=r.id
            )
            source = sources.get(r.source_fragment_id)
            if source is not None:
                raw = source[0].text.encode()
                if (
                    not 0 <= r.start_byte_offset < r.end_byte_offset <= len(raw)
                    or raw[r.start_byte_offset : r.end_byte_offset] != r.source_excerpt.encode()
                ):
                    source = None
            excerpt = (
                exact_source_excerpt(source[0].text, r.start_byte_offset, r.end_byte_offset)
                if source
                else None
            )
            risk_items.append(
                dict(
                    item_id=r.id,
                    native_revision=snapshot.revision if snapshot else 1,
                    kind="RISK",
                    native_type=r.category,
                    native_state=snapshot.treatment if snapshot is not None else "UNKNOWN",
                    title=r.title if source else None,
                    source_excerpt=excerpt,
                    source_excerpt_state="EXACT_SOURCE" if excerpt is not None else "UNKNOWN",
                    source_excerpt_unknown_reason=None
                    if excerpt is not None
                    else "READ_BUDGET_EXCEEDED"
                    if source
                    else "SOURCE_UNPROVEN",
                    severity=r.severity if source else "UNKNOWN",
                    source_state="CURRENT_SOURCE" if source else "UNKNOWN",
                    source_anchor=provenance(source),
                    start_byte_offset=r.start_byte_offset if source else None,
                    end_byte_offset=r.end_byte_offset if source else None,
                    lot_numbers=[],
                    lot_state="UNKNOWN",
                )
            )
        attach_table_contexts(
            self._session, tenant_id=tenant_id, version=version, items=(*req_items, *risk_items)
        )
        relations_truncated = (
            attach_analysis_follow_ups(
                self._session,
                tenant_id=tenant_id,
                case_id=case_id,
                version=version,
                requirements=req_items,
                risks=risk_items,
            )
            if include_follow_ups
            else False
        )
        from app.modules.case.infrastructure.analysis_assessment_handler import attach_assessments

        attach_assessments(
            self._session,
            tenant_id=tenant_id,
            case_id=case_id,
            version=version,
            requirements=req_items,
            risks=risk_items,
        )
        return build_analysis_summary(
            case_id=case_id,
            dce_version_id=version,
            case_scope_kind=reading.coverage.case_scope_kind if reading.coverage else "CUSTOM",
            requirements=tuple(req_items),
            risks=tuple(risk_items),
            coverage=reading.coverage,
            truncated=len(reading.requirements) > 200 or len(risks) > 100 or relations_truncated,
            source_context_state="CURRENT" if admissible else "REVIEW_REQUIRED",
        )
