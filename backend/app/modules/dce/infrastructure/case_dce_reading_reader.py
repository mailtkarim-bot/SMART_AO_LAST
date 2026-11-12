"""Tenant-scoped closed read adapter for the DCE applicable to one Case."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from hashlib import sha256
from typing import Any, Final
from uuid import UUID, uuid5

import sqlalchemy as sa
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application.analysis import is_valid_rc_observation
from app.modules.dce.application.classification import current_completed_extraction_condition
from app.modules.dce.application.commands import DceArchiveEntryInput
from app.modules.dce.application.document_announcements import (
    MAX_ANNOUNCEMENT_EXCERPT,
    conflicting_announcements,
    detect_document_announcement_sequence,
    detect_document_announcements,
)
from app.modules.dce.application.extraction import (
    EXTRACTOR_ID,
    EXTRACTOR_VERSION,
    MAX_FRAGMENT_CHARS,
)
from app.modules.dce.application.queries import (
    CaseDceAnnouncementAnchor,
    CaseDceAnnouncementProjection,
    CaseDceCoverageException,
    CaseDceCoverageProjection,
    CaseDceDocumentCoverage,
    CaseDceReadingAvailability,
    CaseDceReadingCounters,
    CaseDceReadingLookup,
    CaseDceReadingProjection,
    CaseDceReadingReader,
    CaseDceReadingRequirementProjection,
)
from app.modules.dce.application.requirement_values import (
    RcStructuredCandidate,
    project_rc_requirement_values,
    rc_rectification_is_ambiguous,
)
from app.modules.dce.application.requirements import REQUIREMENT_TYPES
from app.modules.dce.application.source_anchor_projection import DceSourceAnchorProjection
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_rc_analysis import (
    DceRcAnalysisRunRecord,
    DceRcRequirementObservationRecord,
)
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import (
    DceRequirementMaterializationRunRecord,
    DceRequirementRecord,
    DceRequirementSourceRecord,
)
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentClassificationRecord,
    DceDocumentIssueRecord,
    DceDocumentRecord,
    DceMissingDocumentDeclarationRecord,
    DceVersionRecord,
)
from app.modules.dce.infrastructure.preparation_readiness import current_preparation_readiness
from app.modules.dce.infrastructure.source_anchor_reader import SqlAlchemyDceSourceAnchorReader

_MAX_ANNOUNCEMENT_SOURCE_FRAGMENTS = 2000
_MAX_ANNOUNCEMENT_CHAIN_ANCHORS = 8192
_MAX_ANNOUNCEMENT_SOURCE_CHARS = 2_000_000
_MAX_ANNOUNCEMENT_CANDIDATES = 1000

_SAFE_DOCUMENT_FAMILIES: Final[frozenset[str]] = frozenset(
    {
        "RC",
        "CCAP",
        "CCTP",
        "AE",
        "BPU",
        "DPGF",
        "PLAN",
        "ANNEX",
        "RECTIFICATION",
    }
)
_SOURCE_UNCLASSIFIED: Final[str] = "SOURCE_UNCLASSIFIED"
_SOURCE_LOCALIZED: Final[str] = "Source localisée"
_PENDING_HUMAN_CONFIRMATION: Final[str] = "PENDING_HUMAN_CONFIRMATION"


class SqlAlchemyCaseDceReadingReader(CaseDceReadingReader):
    """Rebuild the closed DCE reading view for one Case from source registers.

    It never returns source text, quarantine storage keys, audit facts, financial
    information, or current-confirmation authors. Source hashes and parser versions
    are exposed only for tenant-scoped fragments explicitly linked to a requirement.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(
        self,
        *,
        tenant_id: UUID | str,
        case_id: UUID | str,
    ) -> CaseDceReadingLookup | None:
        case = self._session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == case_id,
            )
        )
        if case is None:
            return None

        if case.applicable_dce_version_id is None:
            return self._unavailable_lookup(
                case=case,
                availability=CaseDceReadingAvailability.NO_APPLICABLE_DCE,
            )

        dce = self._session.scalar(
            sa.select(DceVersionRecord).where(
                DceVersionRecord.tenant_id == tenant_id,
                DceVersionRecord.id == case.applicable_dce_version_id,
            )
        )
        if dce is None:
            return self._unavailable_lookup(
                case=case,
                availability=CaseDceReadingAvailability.DCE_REFERENCE_BROKEN,
            )

        requirements = self._read_requirements(tenant_id=tenant_id, dce_version_id=dce.id)
        counters = self._counters(requirements)
        return CaseDceReadingLookup(
            case_id=case.id,
            work_label=case.title,
            case_lifecycle=case.lifecycle,
            commercial_stage=case.commercial_stage,
            dce_freshness=case.dce_freshness,
            availability=CaseDceReadingAvailability.AVAILABLE,
            reading=CaseDceReadingProjection(
                dce_version_id=dce.id,
                lifecycle=dce.lifecycle,
                integrity=dce.integrity,
                classification_readiness=dce.classification_readiness,
                analysis_readiness=current_preparation_readiness(self._session, version=dce)[0],
                source_received_at=dce.source_received_at,
                requirements=requirements,
                counters=counters,
                coverage=self._read_coverage(
                    tenant_id=tenant_id,
                    dce_version_id=dce.id,
                    case_scope_kind=case.scope_kind,
                ),
            ),
        )

    def _read_coverage(
        self,
        *,
        tenant_id: UUID | str,
        dce_version_id: UUID,
        case_scope_kind: str,
    ) -> CaseDceCoverageProjection:
        document = DceDocumentRecord
        extraction = DceDocumentExtractionRecord
        fragment = DceDocumentExtractionFragmentRecord
        classification = DceDocumentClassificationRecord
        # A refusal wins timestamp ties; never fall back to an older successful run.
        latest = (
            sa.select(extraction.id)
            .where(
                extraction.tenant_id == tenant_id,
                extraction.dce_version_id == dce_version_id,
                extraction.dce_document_id == document.id,
            )
            .order_by(
                extraction.created_at.desc(),
                (extraction.status != "COMPLETED").desc(),
                extraction.id.desc(),
            )
            .limit(1)
            .correlate(document)
            .scalar_subquery()
        )
        actual_fragments = (
            sa.select(sa.func.count(fragment.id))
            .where(fragment.tenant_id == tenant_id, fragment.extraction_id == extraction.id)
            .correlate(extraction)
            .scalar_subquery()
        )
        rows = self._session.execute(
            sa.select(
                document.id.label("document_id"),
                extraction.id.label("extraction_id"),
                classification.classification,
                extraction.status,
                extraction.fragment_count,
                (extraction.input_sha256 == document.sha256).label("input_matches"),
                actual_fragments.label("actual_fragment_count"),
            )
            .select_from(document)
            .outerjoin(
                extraction, sa.and_(extraction.tenant_id == tenant_id, extraction.id == latest)
            )
            .outerjoin(
                classification,
                sa.and_(
                    classification.tenant_id == tenant_id,
                    classification.dce_document_id == document.id,
                    classification.is_current.is_(True),
                ),
            )
            .where(document.tenant_id == tenant_id, document.dce_version_id == dce_version_id)
            .order_by(document.id)
        )
        items = []
        for row in rows:
            state = row.status or "NOT_STARTED"
            if state == "COMPLETED" and (
                not row.input_matches
                or not row.fragment_count
                or row.actual_fragment_count != row.fragment_count
            ):
                state = "REVIEW_REQUIRED"
            items.append(
                CaseDceDocumentCoverage(
                    document_id=row.document_id,
                    extraction_id=row.extraction_id,
                    document_family=_safe_document_family(row.classification),
                    extraction_status=state,
                )
            )
        completed = sum(item.extraction_status == "COMPLETED" for item in items)
        announcement_state, announcements = self._read_announcements(
            tenant_id=tenant_id,
            dce_version_id=dce_version_id,
            documents=tuple(items),
        )
        return CaseDceCoverageProjection(
            case_scope_kind=case_scope_kind,
            documents=tuple(items),
            total_documents=len(items),
            completed_extractions=completed,
            unread_documents=len(items) - completed,
            announcement_scan_state=announcement_state,
            announcements=announcements,
            exceptions=self._read_coverage_exceptions(
                tenant_id=tenant_id,
                dce_version_id=dce_version_id,
                current_extractions={item.document_id: item.extraction_id for item in items},
            ),
        )

    def _read_announcements(
        self,
        *,
        tenant_id: UUID | str,
        dce_version_id: UUID,
        documents: tuple[CaseDceDocumentCoverage, ...],
    ) -> tuple[str, tuple[CaseDceAnnouncementProjection, ...]]:
        rc_documents = [item for item in documents if item.document_family == "RC"]
        eligible = {
            item.document_id for item in rc_documents if item.extraction_status == "COMPLETED"
        }
        if not eligible:
            return ("REVIEW_REQUIRED" if rc_documents else "UNKNOWN"), ()
        fragment, extraction, document = (
            DceDocumentExtractionFragmentRecord,
            DceDocumentExtractionRecord,
            DceDocumentRecord,
        )
        rows = list(
            self._session.execute(
                sa.select(
                    fragment.id.label("fragment_id"),
                    extraction.id.label("extraction_id"),
                    extraction.extractor_id,
                    extraction.extractor_version,
                    document.id.label("document_id"),
                    fragment.text,
                    fragment.ordinal,
                    fragment.text_sha256,
                    fragment.locator_json,
                )
                .select_from(fragment)
                .join(
                    extraction,
                    sa.and_(
                        extraction.tenant_id == tenant_id,
                        extraction.id == fragment.extraction_id,
                        extraction.dce_version_id == dce_version_id,
                        extraction.status == "COMPLETED",
                    ),
                )
                .join(
                    document,
                    sa.and_(
                        document.tenant_id == tenant_id,
                        document.id == extraction.dce_document_id,
                        document.dce_version_id == dce_version_id,
                        document.sha256 == extraction.input_sha256,
                    ),
                )
                .where(
                    fragment.tenant_id == tenant_id,
                    document.id.in_(eligible),
                    current_completed_extraction_condition(tenant_id=tenant_id),
                )
                .order_by(document.id, fragment.ordinal, fragment.id)
                .limit(_MAX_ANNOUNCEMENT_SOURCE_FRAGMENTS + 1)
            )
        )
        if (
            len(rows) > _MAX_ANNOUNCEMENT_SOURCE_FRAGMENTS
            or sum(len(row.text) for row in rows) > _MAX_ANNOUNCEMENT_SOURCE_CHARS
        ):
            return "REJECTED_LIMIT", ()
        uncertain = len(eligible) != len(rc_documents)
        seen_documents = set()
        candidates = []
        raw_candidates = []
        groups: list[list[int]] = []
        separators: list[list[str]] = []
        previous = None
        for index, row in enumerate(rows):
            seen_documents.add(row.document_id)
            if sha256(row.text.encode()).hexdigest() != row.text_sha256:
                uncertain = True
                previous = None
                continue
            separator = None
            if previous is not None and (
                previous.document_id == row.document_id
                and previous.extraction_id == row.extraction_id
                and row.extractor_id == EXTRACTOR_ID
                and row.extractor_version == EXTRACTOR_VERSION
                and previous.ordinal + 1 == row.ordinal
                and isinstance(previous.locator_json, dict)
                and isinstance(row.locator_json, dict)
                and previous.locator_json.get("kind") == row.locator_json.get("kind") == "pdf_page"
                and _positive_int(previous.locator_json.get("page"))
                and _positive_int(previous.locator_json.get("part"))
                and _positive_int(row.locator_json.get("page"))
                and _positive_int(row.locator_json.get("part"))
            ):
                if (
                    row.locator_json["page"] == previous.locator_json["page"]
                    and row.locator_json["part"] == previous.locator_json["part"] + 1
                    and len(previous.text) == MAX_FRAGMENT_CHARS
                ):
                    separator = ""
                elif (
                    row.locator_json["page"] == previous.locator_json["page"] + 1
                    and row.locator_json["part"] == 1
                ):
                    separator = "\n"
            if separator is None:
                groups.append([index])
                separators.append([])
            else:
                groups[-1].append(index)
                separators[-1].append(separator)
            previous = row
        anchor_count = 0
        for indices, joins in zip(groups, separators, strict=True):
            group = [rows[index] for index in indices]
            try:
                matches = detect_document_announcement_sequence(
                    tuple(row.text for row in group), tuple(joins)
                )
                own_matches = [
                    {
                        (x.document_family, x.start_byte_offset, x.end_byte_offset): x
                        for x in detect_document_announcements(row.text)
                    }
                    for row in group
                ]
            except ValueError:
                return "REJECTED_LIMIT", ()
            for chained in matches:
                sources = [a for a in chained.anchors if a.kind == "SOURCE"]
                contexts = [a for a in chained.anchors if a.kind == "HEADING"]
                source = sources[0]
                context = contexts[0] if contexts else None
                row = group[source.fragment_index]
                context_row = group[context.fragment_index] if context else row
                match = replace(
                    chained.announcement,
                    start_byte_offset=source.start_byte_offset,
                    end_byte_offset=source.end_byte_offset,
                    context_start_byte_offset=context.start_byte_offset if context else None,
                    context_end_byte_offset=context.end_byte_offset if context else None,
                )
                row_bytes = row.text.encode()
                local = own_matches[source.fragment_index].get(
                    (match.document_family, source.start_byte_offset, source.end_byte_offset)
                )
                line_is_local = (
                    isinstance(row.locator_json, dict)
                    and row.locator_json.get("part") == 1
                    or any(x in row_bytes[: source.start_byte_offset] for x in (b"\n", b"\r"))
                    or source.fragment_index > 0
                    and joins[source.fragment_index - 1] == ""
                    and group[source.fragment_index - 1].text.endswith(("\n", "\r"))
                )
                autonomous = len(sources) == 1 and local is not None and line_is_local
                if autonomous and local is not None:
                    match = local
                    context_row = row
                retained_context_index = (
                    source.fragment_index
                    if autonomous
                    else context.fragment_index
                    if context
                    else -1
                )
                prefix_unproved = False
                first_locator = group[0].locator_json
                if (
                    isinstance(first_locator, dict)
                    and _positive_int(first_locator.get("part"))
                    and first_locator["part"] > 1
                    and (
                        source.fragment_index == 0
                        and b"\n" not in group[0].text.encode()[: source.start_byte_offset]
                        or match.context_start_byte_offset is not None
                        and retained_context_index == 0
                        and b"\n" not in group[0].text.encode()[: match.context_start_byte_offset]
                    )
                ):
                    match = replace(match, claim="AMBIGUOUS", lot_numbers=())
                    prefix_unproved = True
                    uncertain = True
                cross_fragment = (
                    not autonomous and len({a.fragment_index for a in chained.anchors}) > 1
                )
                anchors = (
                    tuple(
                        CaseDceAnnouncementAnchor(
                            fragment_id=group[a.fragment_index].fragment_id,
                            fragment_ordinal=group[a.fragment_index].ordinal,
                            locator_label=_source_locator_label(
                                document_family="RC",
                                locator_json=group[a.fragment_index].locator_json,
                            ),
                            part=group[a.fragment_index].locator_json["part"],
                            kind=a.kind,
                            start_byte_offset=a.start_byte_offset,
                            end_byte_offset=a.end_byte_offset,
                        )
                        for a in chained.anchors
                    )
                    if cross_fragment
                    else ()
                )
                anchor_count += len(anchors)
                if anchor_count > _MAX_ANNOUNCEMENT_CHAIN_ANCHORS:
                    return "REJECTED_LIMIT", ()
                legacy_continuation = (
                    not autonomous
                    and len(sources) == len(contexts) == 1
                    and context is not None
                    and source.fragment_index == context.fragment_index + 1
                    and joins[context.fragment_index] == "\n"
                    and not context_row.text.encode()[context.end_byte_offset :].strip()
                    and len(context_row.text.splitlines()[-1]) <= MAX_ANNOUNCEMENT_EXCERPT
                )
                if prefix_unproved:
                    version = "3"
                elif legacy_continuation:
                    version = "2"
                else:
                    version = "3" if cross_fragment else "1"
                identity = (
                    f"announcement:1:{match.document_family}:"
                    f"{match.start_byte_offset}:{match.end_byte_offset}:{match.context_start_byte_offset}"
                    + (
                        f":{context_row.fragment_id}"
                        if context_row.fragment_id != row.fragment_id
                        else ""
                    )
                )
                if version == "3":
                    identity += ":chain:3:" + ":".join(
                        f"{a.fragment_id}:{a.kind}:{a.start_byte_offset}:{a.end_byte_offset}"
                        for a in anchors
                    )
                label = _source_locator_label(document_family="RC", locator_json=row.locator_json)
                candidates.append(
                    CaseDceAnnouncementProjection(
                        candidate_id=uuid5(row.fragment_id, identity),
                        document_family=match.document_family,
                        claim=match.claim,
                        lot_numbers=match.lot_numbers,
                        source_document_id=row.document_id,
                        source_extraction_id=row.extraction_id,
                        source_fragment_id=row.fragment_id,
                        source_locator_label=label,
                        source_locator_state="UNKNOWN"
                        if label == _SOURCE_LOCALIZED
                        else "RESOLVED",
                        start_byte_offset=match.start_byte_offset,
                        end_byte_offset=match.end_byte_offset,
                        context_fragment_id=context_row.fragment_id
                        if match.context_start_byte_offset is not None
                        else None,
                        context_locator_label=_source_locator_label(
                            document_family="RC", locator_json=context_row.locator_json
                        )
                        if match.context_start_byte_offset is not None
                        else None,
                        rule_version=version,
                        context_start_byte_offset=match.context_start_byte_offset,
                        context_end_byte_offset=match.context_end_byte_offset,
                        anchor_chain=anchors,
                        family_candidate_document_ids=tuple(
                            item.document_id
                            for item in documents
                            if item.document_family == match.document_family
                        ),
                    )
                )
                raw_candidates.append(match)
                uncertain = uncertain or match.claim == "AMBIGUOUS"
                if len(candidates) > _MAX_ANNOUNCEMENT_CANDIDATES:
                    return "REJECTED_LIMIT", ()
        conflicts = conflicting_announcements(tuple(raw_candidates))
        return (
            "REVIEW_REQUIRED" if uncertain or eligible - seen_documents else "CANDIDATES_ONLY",
            tuple(
                replace(item, conflict_state="CONFLICTING_CANDIDATES")
                if index in conflicts
                else item
                for index, item in enumerate(candidates)
            ),
        )

    def _read_coverage_exceptions(
        self,
        *,
        tenant_id: UUID | str,
        dce_version_id: UUID,
        current_extractions: dict[UUID, UUID | None],
    ) -> tuple[CaseDceCoverageException, ...]:
        exceptions = []
        for issue, source_hash, extraction_matches, anchored_id in self._session.execute(
            sa.select(
                DceDocumentIssueRecord,
                DceDocumentRecord.sha256,
                sa.and_(
                    DceDocumentExtractionRecord.input_sha256 == DceDocumentRecord.sha256,
                    DceDocumentExtractionRecord.extractor_id == "smart-ao-archive-inventory",
                    DceDocumentExtractionRecord.extractor_version == "1",
                ),
                DceDocumentExtractionRecord.id,
            )
            .join(
                DceDocumentRecord,
                sa.and_(
                    DceDocumentRecord.tenant_id == tenant_id,
                    DceDocumentRecord.id == DceDocumentIssueRecord.dce_document_id,
                    DceDocumentRecord.dce_version_id == dce_version_id,
                ),
            )
            .outerjoin(
                DceDocumentExtractionRecord,
                sa.and_(
                    DceDocumentExtractionRecord.tenant_id == tenant_id,
                    DceDocumentExtractionRecord.dce_document_id == DceDocumentRecord.id,
                    DceDocumentExtractionRecord.dce_version_id == dce_version_id,
                    sa.cast(DceDocumentExtractionRecord.id, sa.String)
                    == DceDocumentIssueRecord.locator_json["extraction_id"].astext,
                ),
            )
            .where(
                DceDocumentIssueRecord.tenant_id == tenant_id,
                DceDocumentIssueRecord.dce_version_id == dce_version_id,
                DceDocumentIssueRecord.issue_kind == "ARCHIVE_ENTRY_NOT_ADMITTED",
            )
        ):
            current = current_extractions.get(issue.dce_document_id)
            locator = issue.locator_json or {}
            recorded = locator.get("extraction_id")
            if current is not None and anchored_id is not None and anchored_id != current:
                # Historical runs stay persisted but do not describe the current extraction.
                continue
            try:
                entry = DceArchiveEntryInput.model_validate(
                    {
                        key: locator.get(key)
                        for key in ("entry_path", "entry_name_sha256", "entry_sha256", "state")
                    }
                )
            except ValidationError:
                entry = DceArchiveEntryInput(entry_path=[], state="UNREADABLE")
                resolved = False
            else:
                resolved = (
                    current is not None
                    and recorded == str(current)
                    and locator.get("kind") == "archive_entry"
                    and locator.get("source_sha256") == source_hash
                    and extraction_matches
                )
            exceptions.append(
                CaseDceCoverageException(
                    observation_id=issue.id,
                    kind="ARCHIVE_ENTRY",
                    state=entry.state if resolved else "UNREADABLE",
                    document_id=issue.dce_document_id,
                    extraction_id=current if resolved else None,
                    entry_path=tuple(entry.entry_path) if resolved else (),
                    document_family="SOURCE_UNCLASSIFIED",
                    source_state="RESOLVED" if resolved else "UNKNOWN",
                )
            )
        for declaration in self._session.scalars(
            sa.select(DceMissingDocumentDeclarationRecord).where(
                DceMissingDocumentDeclarationRecord.tenant_id == tenant_id,
                DceMissingDocumentDeclarationRecord.dce_version_id == dce_version_id,
            )
        ):
            exceptions.append(
                CaseDceCoverageException(
                    observation_id=declaration.id,
                    kind="DECLARED_MISSING",
                    state="DECLARED_MISSING",
                    document_id=None,
                    extraction_id=None,
                    entry_path=(),
                    document_family=_safe_document_family(declaration.expected_document_family),
                    # A free-text source reference is not a qualified fragment anchor.
                    source_state="UNKNOWN",
                )
            )
        return tuple(
            sorted(
                exceptions,
                key=lambda item: (
                    item.kind,
                    str(item.document_id or ""),
                    item.entry_path,
                    str(item.observation_id),
                ),
            )
        )

    @staticmethod
    def _unavailable_lookup(
        *,
        case: CaseRecord,
        availability: CaseDceReadingAvailability,
    ) -> CaseDceReadingLookup:
        return CaseDceReadingLookup(
            case_id=case.id,
            work_label=case.title,
            case_lifecycle=case.lifecycle,
            commercial_stage=case.commercial_stage,
            dce_freshness=case.dce_freshness,
            availability=availability,
            reading=None,
        )

    def _read_requirements(
        self,
        *,
        tenant_id: UUID | str,
        dce_version_id: UUID,
    ) -> tuple[CaseDceReadingRequirementProjection, ...]:
        latest_materialization = (
            sa.select(DceRequirementMaterializationRunRecord.id)
            .where(
                DceRequirementMaterializationRunRecord.tenant_id == tenant_id,
                DceRequirementMaterializationRunRecord.dce_version_id == dce_version_id,
            )
            .order_by(
                DceRequirementMaterializationRunRecord.created_at.desc(),
                DceRequirementMaterializationRunRecord.id.desc(),
            )
            .limit(1)
            .scalar_subquery()
        )
        # Failed retries invalidate proof but must not erase the last visible register.
        latest_visible_materialization = (
            sa.select(DceRequirementMaterializationRunRecord.id)
            .where(
                DceRequirementMaterializationRunRecord.tenant_id == tenant_id,
                DceRequirementMaterializationRunRecord.dce_version_id == dce_version_id,
                sa.or_(
                    DceRequirementMaterializationRunRecord.status == "NO_SIGNAL",
                    sa.and_(
                        DceRequirementMaterializationRunRecord.status == "COMPLETED",
                        sa.select(DceRequirementRecord.id)
                        .where(
                            DceRequirementRecord.tenant_id == tenant_id,
                            DceRequirementRecord.dce_version_id == dce_version_id,
                            DceRequirementRecord.requirements_run_id
                            == DceRequirementMaterializationRunRecord.id,
                        )
                        .correlate(DceRequirementMaterializationRunRecord)
                        .exists(),
                    ),
                ),
            )
            .order_by(
                DceRequirementMaterializationRunRecord.created_at.desc(),
                DceRequirementMaterializationRunRecord.id.desc(),
            )
            .limit(1)
            .scalar_subquery()
        )
        latest_analysis = (
            sa.select(DceRcAnalysisRunRecord.id)
            .where(
                DceRcAnalysisRunRecord.tenant_id == tenant_id,
                DceRcAnalysisRunRecord.dce_version_id == dce_version_id,
            )
            .order_by(
                DceRcAnalysisRunRecord.created_at.desc(),
                (DceRcAnalysisRunRecord.status != "COMPLETED").desc(),
                DceRcAnalysisRunRecord.id.desc(),
            )
            .limit(1)
            .correlate(None)
            .scalar_subquery()
        )
        rows = self._session.execute(
            sa.select(
                DceRequirementRecord.id,
                DceRequirementRecord.requirement_type,
                DceRequirementRecord.directive_signal,
                DceRequirementRecord.uncertainty_status,
                DceRequirementConfirmationCurrentRecord.outcome,
                DceRequirementConfirmationCurrentRecord.revision,
                DceDocumentClassificationRecord.classification,
                sa.case(
                    (
                        sa.and_(
                            DceDocumentExtractionRecord.id.is_not(None),
                            DceDocumentRecord.id.is_not(None),
                        ),
                        DceDocumentExtractionFragmentRecord.locator_json,
                    ),
                    else_=None,
                ).label("locator_json"),
                DceRequirementSourceRecord.fragment_id.label("source_fragment_id"),
                DceRequirementSourceRecord.start_byte_offset.label("value_start"),
                DceRequirementSourceRecord.end_byte_offset.label("value_end"),
                DceRcRequirementObservationRecord.excerpt.label("value_excerpt"),
                DceRcRequirementObservationRecord.requirement_kind.label("value_kind"),
                DceRcRequirementObservationRecord.rule_id.label("value_rule"),
                DceRcRequirementObservationRecord.rule_version.label("value_version"),
                DceRcRequirementObservationRecord.directive.label("value_directive"),
                DceRcRequirementObservationRecord.fragment_id.label("observation_fragment"),
                DceRcRequirementObservationRecord.start_byte_offset.label("observation_start"),
                DceRcRequirementObservationRecord.end_byte_offset.label("observation_end"),
                (DceRequirementRecord.requirements_run_id == latest_materialization).label(
                    "current_materialization"
                ),
                (DceRcRequirementObservationRecord.analysis_id == latest_analysis).label(
                    "current_analysis"
                ),
                current_completed_extraction_condition(tenant_id=tenant_id).label(
                    "current_extraction"
                ),
                DceVersionRecord.lifecycle.label("source_lifecycle"),
                DceVersionRecord.integrity.label("source_integrity"),
            )
            .select_from(DceRequirementRecord)
            .outerjoin(
                DceRequirementConfirmationCurrentRecord,
                sa.and_(
                    DceRequirementConfirmationCurrentRecord.tenant_id == tenant_id,
                    DceRequirementConfirmationCurrentRecord.requirement_id
                    == DceRequirementRecord.id,
                ),
            )
            .outerjoin(
                DceRequirementSourceRecord,
                sa.and_(
                    DceRequirementSourceRecord.tenant_id == tenant_id,
                    DceRequirementSourceRecord.requirement_id == DceRequirementRecord.id,
                ),
            )
            .outerjoin(
                DceDocumentExtractionFragmentRecord,
                sa.and_(
                    DceDocumentExtractionFragmentRecord.tenant_id == tenant_id,
                    DceDocumentExtractionFragmentRecord.id
                    == DceRequirementSourceRecord.fragment_id,
                ),
            )
            .outerjoin(
                DceDocumentExtractionRecord,
                sa.and_(
                    DceDocumentExtractionRecord.tenant_id == tenant_id,
                    DceDocumentExtractionRecord.id
                    == DceDocumentExtractionFragmentRecord.extraction_id,
                    DceDocumentExtractionRecord.dce_version_id == dce_version_id,
                    DceDocumentExtractionRecord.status == "COMPLETED",
                ),
            )
            .outerjoin(
                DceDocumentRecord,
                sa.and_(
                    DceDocumentRecord.tenant_id == tenant_id,
                    DceDocumentRecord.id == DceDocumentExtractionRecord.dce_document_id,
                    DceDocumentRecord.dce_version_id == dce_version_id,
                ),
            )
            .outerjoin(
                DceDocumentClassificationRecord,
                sa.and_(
                    DceDocumentClassificationRecord.tenant_id == tenant_id,
                    DceDocumentClassificationRecord.dce_document_id == DceDocumentRecord.id,
                    DceDocumentClassificationRecord.is_current.is_(True),
                ),
            )
            .outerjoin(
                DceRcRequirementObservationRecord,
                sa.and_(
                    DceRcRequirementObservationRecord.tenant_id == tenant_id,
                    DceRcRequirementObservationRecord.id
                    == DceRequirementRecord.source_observation_id,
                    DceRcRequirementObservationRecord.id
                    == DceRequirementSourceRecord.source_observation_id,
                    DceRcRequirementObservationRecord.dce_version_id == dce_version_id,
                ),
            )
            .outerjoin(
                DceVersionRecord,
                sa.and_(
                    DceVersionRecord.tenant_id == tenant_id,
                    DceVersionRecord.id == dce_version_id,
                ),
            )
            .where(
                DceRequirementRecord.tenant_id == tenant_id,
                DceRequirementRecord.dce_version_id == dce_version_id,
                DceRequirementRecord.requirements_run_id == latest_visible_materialization,
            )
            .order_by(
                DceRequirementRecord.requirement_type,
                DceRequirementRecord.id,
            )
        ).all()

        source_anchors = SqlAlchemyDceSourceAnchorReader().get_many(
            session=self._session,
            tenant_id=tenant_id,
            fragment_ids=(row.source_fragment_id for row in rows if row.source_fragment_id),
            dce_version_id=dce_version_id,
        )
        eligible_ids = tuple(
            {
                row.source_fragment_id
                for row in rows
                if row.source_fragment_id in source_anchors
                and row.current_analysis
                and row.current_materialization
                and row.current_extraction
                and row.value_version in {"5", "6", "7", "8", "9", "10", "11"}
                and row.source_lifecycle == "ADMITTED"
                and row.source_integrity == "VERIFIED"
            }
        )
        # Several requirements may quote one fragment; fetch its private text only once.
        source_texts = (
            dict(
                self._session.execute(
                    sa.select(
                        DceDocumentExtractionFragmentRecord.id,
                        DceDocumentExtractionFragmentRecord.text,
                    ).where(
                        DceDocumentExtractionFragmentRecord.tenant_id == tenant_id,
                        DceDocumentExtractionFragmentRecord.id.in_(eligible_ids),
                    )
                ).all()
            )
            if eligible_ids
            else {}
        )
        proof_reasons = {
            row.id: self._source_proof_reason(
                row=row,
                source_anchor=source_anchors.get(row.source_fragment_id),
                source_text=source_texts.get(row.source_fragment_id),
            )
            for row in rows
        }
        projections = tuple(
            replace(
                self._requirement_projection(
                    requirement_id=row.id,
                    confirmation_revision=row.revision,
                    requirement_type=row.requirement_type,
                    directive_signal=row.directive_signal,
                    uncertainty_status=row.uncertainty_status,
                    confirmation_outcome=row.outcome,
                    classification=row.classification,
                    locator_json=row.locator_json,
                    source_anchor=source_anchors.get(row.source_fragment_id),
                ),
                source_proof_state="CURRENT_SOURCE"
                if proof_reasons[row.id] == "SOURCE_CURRENT"
                else "UNKNOWN",
                source_start_byte_offset=row.value_start
                if proof_reasons[row.id] == "SOURCE_CURRENT"
                else None,
                source_end_byte_offset=row.value_end
                if proof_reasons[row.id] == "SOURCE_CURRENT"
                else None,
                structured_candidate=self._structured_candidate(
                    row=row,
                    source_anchor=source_anchors.get(row.source_fragment_id),
                    source_text=source_texts.get(row.source_fragment_id),
                ),
            )
            for row in rows
        )
        contexts: dict[UUID, dict[UUID, str]] = {}
        for row in rows:
            anchor = source_anchors.get(row.source_fragment_id)
            if (
                anchor is not None
                and row.classification == "RC"
                and row.current_analysis
                and row.current_materialization
                and row.current_extraction
                and row.source_fragment_id in source_texts
            ):
                contexts.setdefault(anchor.extraction_id, {})[row.source_fragment_id] = (
                    source_texts[row.source_fragment_id]
                )
        ambiguous = {
            key
            for key, fragments in contexts.items()
            if rc_rectification_is_ambiguous(fragments.values())
        }
        projections = tuple(
            replace(
                item,
                structured_candidate=RcStructuredCandidate(
                    state="REVIEW_REQUIRED",
                    reason_code="RECTIFICATION_REVIEW_REQUIRED",
                    source_fragment_id=row.source_fragment_id,
                ),
            )
            if (
                item.requirement_type == "SUBMISSION_DEADLINE_SIGNAL"
                and (anchor := source_anchors.get(row.source_fragment_id)) is not None
                and anchor.extraction_id in ambiguous
                and item.structured_candidate is not None
                and item.structured_candidate.state == "CANDIDATES_ONLY"
            )
            else item
            for row, item in zip(rows, projections, strict=True)
        )
        projections = _refuse_conflicting_deadlines(projections)
        return tuple(
            sorted(
                projections,
                key=lambda item: (
                    item.requirement_type,
                    item.source_locator_label,
                    str(item.requirement_id),
                ),
            )
        )

    @staticmethod
    def _source_proof_reason(
        *, row: Any, source_anchor: DceSourceAnchorProjection | None, source_text: str | None
    ) -> str:
        if source_anchor is None:
            return "UNPROVEN_SOURCE"
        if (
            not row.current_materialization
            or not row.current_analysis
            or not row.current_extraction
            or row.source_lifecycle != "ADMITTED"
            or row.source_integrity != "VERIFIED"
        ):
            return "STALE_SOURCE"
        if row.value_version not in {"5", "6", "7", "8", "9", "10", "11"}:
            return "UNSUPPORTED_ANALYSIS"
        text = source_text
        start, end = row.value_start, row.value_end
        if (
            not isinstance(text, str)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or start < 0
            or end <= start
            or end > len(text.encode())
            or row.observation_fragment != row.source_fragment_id
            or row.observation_start != start
            or row.observation_end != end
            or sha256(text.encode()).hexdigest() != source_anchor.fragment_sha256
            or REQUIREMENT_TYPES.get(row.value_kind) != row.requirement_type
            or row.value_directive != row.directive_signal
        ):
            return "INVALID_SOURCE_PROOF"
        try:
            excerpt = text.encode()[start:end].decode()
        except UnicodeDecodeError:
            return "INVALID_SOURCE_PROOF"
        if excerpt != row.value_excerpt or not is_valid_rc_observation(
            requirement_kind=row.value_kind,
            rule_id=row.value_rule,
            directive=row.value_directive,
            excerpt=excerpt,
            rule_version=row.value_version,
            source_locator_kind=source_anchor.locator.kind.value
            if source_anchor.locator is not None
            else None,
        ):
            return "INVALID_SOURCE_PROOF"
        return "SOURCE_CURRENT"

    @classmethod
    def _structured_candidate(
        cls, *, row: Any, source_anchor: DceSourceAnchorProjection | None, source_text: str | None
    ) -> RcStructuredCandidate:
        unknown = RcStructuredCandidate()
        if (
            source_anchor is None
            or source_anchor.locator is None
            or (
                row.classification != "RC"
                and row.requirement_type
                not in {
                    "TECHNICAL_PRESCRIPTION",
                    "LOGISTICS_CONSTRAINT",
                    "SCHEDULE_CONSTRAINT",
                    "HSE_CONSTRAINT",
                    "PAYMENT_TERM_SIGNAL",
                    "ACCEPTANCE_TERM_SIGNAL",
                }
            )
        ):
            return unknown
        reason = cls._source_proof_reason(
            row=row, source_anchor=source_anchor, source_text=source_text
        )
        if reason != "SOURCE_CURRENT":
            return replace(
                unknown,
                state="REVIEW_REQUIRED" if reason == "INVALID_SOURCE_PROOF" else "UNKNOWN",
                reason_code=reason,
            )
        assert source_text is not None
        return project_rc_requirement_values(
            excerpt=source_text.encode()[row.value_start : row.value_end].decode(),
            requirement_type=row.requirement_type,
            directive_signal=row.directive_signal,
            start_byte_offset=row.value_start,
            source_fragment_id=row.source_fragment_id,
        )

    @staticmethod
    def _requirement_projection(
        *,
        requirement_id: UUID,
        confirmation_revision: int | None,
        requirement_type: str,
        directive_signal: str,
        uncertainty_status: str,
        confirmation_outcome: str | None,
        classification: str | None,
        locator_json: object,
        source_anchor: DceSourceAnchorProjection | None = None,
    ) -> CaseDceReadingRequirementProjection:
        document_family = _safe_document_family(classification)
        return CaseDceReadingRequirementProjection(
            requirement_id=requirement_id,
            confirmation_revision=confirmation_revision,
            requirement_type=requirement_type,
            directive_signal=directive_signal,
            confirmation_outcome=confirmation_outcome or _PENDING_HUMAN_CONFIRMATION,
            uncertainty_status=uncertainty_status,
            document_family=document_family,
            source_locator_label=_source_locator_label(
                document_family=document_family,
                locator_json=locator_json,
            ),
            source_anchor=source_anchor,
        )

    @staticmethod
    def _counters(
        requirements: Iterable[CaseDceReadingRequirementProjection],
    ) -> CaseDceReadingCounters:
        materialized = tuple(requirements)
        outcomes = tuple(item.confirmation_outcome for item in materialized)
        return CaseDceReadingCounters(
            total=len(materialized),
            pending_human_confirmation=outcomes.count(_PENDING_HUMAN_CONFIRMATION),
            confirmed=outcomes.count("CONFIRMED"),
            review_required=outcomes.count("REVIEW_REQUIRED"),
            not_applicable=outcomes.count("NOT_APPLICABLE"),
        )


def _refuse_conflicting_deadlines(
    items: tuple[CaseDceReadingRequirementProjection, ...],
) -> tuple[CaseDceReadingRequirementProjection, ...]:
    deadlines = [
        (i, item.structured_candidate)
        for i, item in enumerate(items)
        if item.requirement_type == "SUBMISSION_DEADLINE_SIGNAL"
        and item.structured_candidate is not None
        and item.structured_candidate.state == "CANDIDATES_ONLY"
        and (item.structured_candidate.date_iso or item.structured_candidate.time_local)
    ]
    conflicts: set[int] = set()
    if len(deadlines) > 256:
        conflicts.update(i for i, _ in deadlines)
    else:
        for pos, (i, first) in enumerate(deadlines):
            for j, second in deadlines[pos + 1 :]:
                if (
                    first.lot_numbers
                    and second.lot_numbers
                    and set(first.lot_numbers).isdisjoint(second.lot_numbers)
                ):
                    continue
                if any(
                    a is not None and b is not None and a != b
                    for a, b in (
                        (first.date_iso, second.date_iso),
                        (first.time_local, second.time_local),
                        (first.timezone, second.timezone),
                    )
                ):
                    conflicts.update((i, j))
    return tuple(
        replace(
            item,
            structured_candidate=RcStructuredCandidate(
                state="REVIEW_REQUIRED",
                reason_code="COMPARISON_LIMIT" if len(deadlines) > 256 else "CONFLICTING_VALUES",
                source_fragment_id=item.structured_candidate.source_fragment_id,
            ),
        )
        if i in conflicts and item.structured_candidate is not None
        else item
        for i, item in enumerate(items)
    )


def _safe_document_family(classification: str | None) -> str:
    """Return only the closed family vocabulary used by the reading view."""

    if classification in _SAFE_DOCUMENT_FAMILIES:
        return classification
    return _SOURCE_UNCLASSIFIED


def _source_locator_label(*, document_family: str, locator_json: object) -> str:
    """Format a bounded human locator without returning locator JSON or source text."""

    if not isinstance(locator_json, dict):
        return _SOURCE_LOCALIZED

    kind = locator_json.get("kind")
    if kind == "pdf_page":
        page = locator_json.get("page")
        if _positive_int(page):
            return f"{document_family} · page {page}"
    if kind == "docx_paragraph":
        paragraph = locator_json.get("paragraph")
        if _positive_int(paragraph):
            return f"{document_family} · paragraphe {paragraph}"
    if kind == "docx_table_cell" and all(
        _positive_int(locator_json.get(field)) for field in ("table", "row", "column", "paragraph")
    ):
        return (
            f"{document_family} · tableau {locator_json['table']} · ligne {locator_json['row']}"
            f" · colonne {locator_json['column']} · paragraphe {locator_json['paragraph']}"
            " · contexte entre cellules UNKNOWN"
        )
    if kind == "text_line":
        line = locator_json.get("line")
        if _positive_int(line):
            return f"{document_family} · ligne {line}"
    if kind == "xlsx_cell":
        sheet = locator_json.get("sheet")
        cell = locator_json.get("cell")
        if _safe_locator_token(sheet, maximum_length=80) and _safe_locator_token(
            cell, maximum_length=16
        ):
            return f"{document_family} · cellule {sheet}!{cell}"
    return _SOURCE_LOCALIZED


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _safe_locator_token(value: object, *, maximum_length: int) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and len(value) <= maximum_length
        and "\n" not in value
        and "\r" not in value
    )
