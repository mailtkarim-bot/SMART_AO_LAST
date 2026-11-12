"""Unwired, source-revalidated candidate retrieval. No persistence or business act."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass, field, replace
from hashlib import sha256
from math import sqrt
from typing import Literal, Protocol
from uuid import UUID, uuid5

from app.modules.knowledge.application.rc_candidate_conflicts import (
    RcClauseEvidence,
    RcConflictProjection,
    project_rc_conflicts,
)
from app.modules.knowledge.application.rc_query_intent import RcQueryIntent, parse_rc_query_intent
from app.modules.knowledge.application.rc_query_scope import (
    RcQueryLot,
    parse_query_lot,
    scope_rc_projection,
)
from app.modules.knowledge.application.rc_recall import generic_rc_subject, obligation_rc_subject
from app.modules.knowledge.application.rc_specific_intent import RcVisitIntent, parse_visit_intent
from app.modules.knowledge.application.retrieval import (
    _FINANCIAL_QUERY_PATTERN,
    FinancialRetrievalQueryRejected,
    InMemoryVectorIndex,
)
from app.modules.knowledge.application.service import DceRetrievalSource
from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile
from app.modules.knowledge.domain.retrieval import (
    DataClassification,
    EmbeddingVector,
    RetrievalChunk,
    RetrievalResult,
    RetrievalScope,
)


class CandidateEncoder(Protocol):
    @property
    def profile_id(self) -> str: ...
    def encode_passages(self, texts: Sequence[str]) -> list[tuple[float, ...]]: ...
    def encode_query(self, text: str) -> tuple[float, ...]: ...


@dataclass(frozen=True, slots=True)
class CandidateSegment:
    chunk: RetrievalChunk
    start_byte: int
    end_byte: int
    source_sha256: str
    segment_sha256: str


@dataclass(frozen=True, slots=True)
class CandidateHit:
    result: RetrievalResult
    start_byte: int
    end_byte: int
    source_sha256: str
    segment_sha256: str


@dataclass(frozen=True, slots=True)
class CandidateScoreTrace:
    chunk_id: UUID
    source_fragment_id: UUID
    rank: int
    score: float
    threshold: float
    start_byte: int
    end_byte: int
    source_sha256: str
    segment_sha256: str
    decision: str


@dataclass(frozen=True, slots=True)
class CandidateReading:
    profile_id: str
    state: Literal["ABSTAIN", "CANDIDATES_ONLY", "REVIEW_REQUIRED"]
    reason: str
    hits: tuple[CandidateHit, ...] = ()
    answer_state: Literal["UNKNOWN"] = "UNKNOWN"
    review_source_ids: tuple[UUID, ...] = ()
    rc_projection: RcConflictProjection = field(default_factory=RcConflictProjection)
    query_lot: RcQueryLot | None = None
    rc_unscoped_evidence: tuple[RcClauseEvidence, ...] = ()
    score_trace: tuple[CandidateScoreTrace, ...] = ()
    specific_intent: RcVisitIntent | None = None
    visit_type_evidence: tuple[RcClauseEvidence, ...] = ()
    query_intent: RcQueryIntent | None = None


def segment_chunks(
    chunks: Sequence[RetrievalChunk], profile: CandidateRetrievalProfile
) -> tuple[CandidateSegment, ...]:
    segments: list[CandidateSegment] = []
    seen = set()
    for source in chunks:
        if source.source_fragment_id in seen:
            raise ValueError("duplicate source fragment")
        seen.add(source.source_fragment_id)
        start = 0
        raw = source.text.encode()
        while start < len(source.text):
            end = min(start + profile.segment_chars, len(source.text))
            if end < len(source.text):
                boundary = source.text.rfind(" ", start + profile.segment_chars // 2, end)
                if boundary >= 0:
                    end = boundary + 1
            text = source.text[start:end]
            lower, upper = len(source.text[:start].encode()), len(source.text[:end].encode())
            if text.strip():
                chunk = RetrievalChunk(
                    chunk_id=uuid5(
                        source.source_fragment_id, f"{profile.profile_id}:{lower}:{upper}"
                    ),
                    source_fragment_id=source.source_fragment_id,
                    tenant_id=source.tenant_id,
                    case_id=source.case_id,
                    dce_version_id=source.dce_version_id,
                    ordinal=len(segments) + 1,
                    text=text,
                    locator={
                        **deepcopy(source.locator),
                        "candidate_start_byte": lower,
                        "candidate_end_byte": upper,
                    },
                    classification=source.classification,
                )
                segments.append(
                    CandidateSegment(
                        chunk,
                        lower,
                        upper,
                        sha256(raw).hexdigest(),
                        sha256(text.encode()).hexdigest(),
                    )
                )
                if len(segments) > 512:
                    raise ValueError("candidate segment budget exceeded")
            if end == len(source.text):
                break
            start = max(start + 1, end - profile.overlap_chars)
    return tuple(segments)


def _vectors(
    values: Sequence[tuple[float, ...]], count: int, dimension: int
) -> list[EmbeddingVector]:
    if len(values) != count:
        raise ValueError("candidate embedding count mismatch")
    vectors = [EmbeddingVector(values=tuple(row)) for row in values]
    if any(
        v.dimension != dimension or abs(sqrt(sum(x * x for x in v.values)) - 1) > 0.001
        for v in vectors
    ):
        raise ValueError("candidate embedding dimension/normalization mismatch")
    return vectors


class CandidateRetrievalService:
    def __init__(
        self,
        *,
        profile: CandidateRetrievalProfile,
        source: DceRetrievalSource,
        encoder: CandidateEncoder,
    ) -> None:
        if encoder.profile_id != profile.profile_id:
            raise ValueError("candidate encoder profile mismatch")
        self._profile = profile
        self._source = source
        self._encoder = encoder
        self._snapshot: tuple[str, InMemoryVectorIndex, tuple[CandidateSegment, ...]] | None = None

    @property
    def profile(self) -> CandidateRetrievalProfile:
        return self._profile

    def _current(self, scope: RetrievalScope) -> tuple[list[RetrievalChunk], str]:
        chunks = [
            c
            for c in self._source.read_chunks(
                tenant_id=scope.tenant_id,
                case_id=scope.case_id,
                dce_version_id=scope.dce_version_id,
            )
            if c.is_visible_in(scope)
            and c.classification
            in {DataClassification.PUBLIC, DataClassification.INTERNAL_OPERATIONAL}
        ]
        if len(chunks) > 128:
            raise ValueError("candidate source budget exceeded")
        chunks.sort(key=lambda c: (c.ordinal, str(c.source_fragment_id)))
        identity = [
            self.profile.profile_id,
            str(scope.tenant_id),
            str(scope.case_id),
            str(scope.dce_version_id),
            [
                (
                    str(c.source_fragment_id),
                    str(c.chunk_id),
                    c.ordinal,
                    c.classification.value,
                    sha256(c.text.encode()).hexdigest(),
                    c.locator,
                )
                for c in chunks
            ],
        ]
        return chunks, sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def retrieve(self, *, query: str, scope: RetrievalScope, top_k: int = 5) -> CandidateReading:
        if not query.strip() or len(query) > 2000 or not 1 <= top_k <= 50:
            raise ValueError("invalid candidate query budget")
        if _FINANCIAL_QUERY_PATTERN.search(query):
            raise FinancialRetrievalQueryRejected("FINANCIAL_RETRIEVAL_SCOPE_REQUIRED")
        query_intent = (
            parse_rc_query_intent(
                query,
                extended_forms=self.profile.review_policy
                in {"rc-imperative-v9", "rc-conditional-v10"},
            )
            if self.profile.review_policy
            in {"rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"}
            else None
        )
        intent = (
            parse_visit_intent(
                query,
                strict=self.profile.review_policy
                in {
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                },
            )
            if self.profile.review_policy
            in {
                "rc-specific-v5",
                "rc-type-proof-v6",
                "rc-subject-proof-v7",
                "rc-intent-v8",
                "rc-imperative-v9",
                "rc-conditional-v10",
            }
            else None
        )
        query_lot = (
            parse_query_lot(query)
            if self.profile.review_policy
            in {
                "rc-query-lot-v3",
                "rc-recall-v4",
                "rc-specific-v5",
                "rc-type-proof-v6",
                "rc-subject-proof-v7",
                "rc-intent-v8",
                "rc-imperative-v9",
                "rc-conditional-v10",
            }
            else None
        )
        subject = (
            obligation_rc_subject(query)
            if self.profile.review_policy
            in {"rc-subject-proof-v7", "rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"}
            else None
        )
        if query_intent is not None:
            query_lot = query_intent.scope
            if query_intent.coverage == "COVERED" and query_intent.subject in {
                "VISIT_MEDICAL",
                "VISIT_SITE",
            }:
                anchor = next(a for a in query_intent.anchors if a.signal == "SUBJECT")
                intent = RcVisitIntent(
                    "CANDIDATE", query_intent.subject, anchor.start_byte, anchor.end_byte
                )
                subject = None
            else:
                intent = (
                    RcVisitIntent("UNKNOWN")
                    if query_intent.coverage != "COVERED"
                    and any(
                        a.signal == "SUBJECT" and a.excerpt.casefold().startswith("visite")
                        for a in query_intent.anchors
                    )
                    else RcVisitIntent()
                )
                subject = query_intent.subject if query_intent.coverage == "COVERED" else None
        if self._encoder.profile_id != self.profile.profile_id:
            self._snapshot = None
            raise ValueError("candidate encoder profile changed")
        if query_intent is not None and query_intent.coverage != "COVERED":
            return CandidateReading(
                self.profile.profile_id,
                "ABSTAIN",
                "RC_QUERY_NOT_COVERED",
                query_lot=query_lot,
                specific_intent=intent,
                query_intent=query_intent,
            )
        chunks, key = self._current(scope)
        snapshot = self._snapshot
        if snapshot is None or snapshot[0] != key:
            self._snapshot = None
            if not chunks:
                return CandidateReading(
                    self.profile.profile_id,
                    "ABSTAIN",
                    "NO_CURRENT_SOURCE",
                    query_lot=query_lot,
                    specific_intent=intent,
                    query_intent=query_intent,
                )
            segments = segment_chunks(chunks, self.profile)
            vectors = _vectors(
                self._encoder.encode_passages([s.chunk.text for s in segments]),
                len(segments),
                self.profile.dimension,
            )
            index = InMemoryVectorIndex()
            index.upsert(chunks=[s.chunk for s in segments], embeddings=vectors)
            snapshot = (key, index, segments)
            self._snapshot = snapshot
        _, index, segments = snapshot
        [vector] = _vectors([self._encoder.encode_query(query)], 1, self.profile.dimension)
        if self._encoder.profile_id != self.profile.profile_id:
            self._snapshot = None
            raise ValueError("candidate encoder profile changed")
        results = index.search(
            query=vector,
            scope=scope,
            top_k=50
            if self.profile.review_policy
            in {
                "rc-recall-v4",
                "rc-specific-v5",
                "rc-type-proof-v6",
                "rc-subject-proof-v7",
                "rc-intent-v8",
                "rc-imperative-v9",
                "rc-conditional-v10",
            }
            else top_k,
            embedding_model=self.profile.profile_id,
        )
        _, current_key = self._current(scope)
        if current_key != key:
            self._snapshot = None
            return CandidateReading(
                self.profile.profile_id,
                "REVIEW_REQUIRED",
                "SOURCE_CHANGED",
                query_lot=query_lot,
                specific_intent=intent,
                query_intent=query_intent,
            )
        regions = {s.chunk.chunk_id: s for s in segments}
        source_by_id = {c.source_fragment_id: c for c in chunks}
        prefixes = (
            {
                r.chunk.chunk_id: source_by_id[r.chunk.source_fragment_id]
                .text.encode()[: regions[r.chunk.chunk_id].start_byte]
                .decode()
                for r in results
            }
            if self.profile.review_policy
            in {
                "rc-recall-v4",
                "rc-specific-v5",
                "rc-type-proof-v6",
                "rc-subject-proof-v7",
                "rc-intent-v8",
                "rc-imperative-v9",
                "rc-conditional-v10",
            }
            else None
        )
        specific_rejections: dict[UUID, str] = {}
        whole_contexts = (
            {r.chunk.chunk_id: source_by_id[r.chunk.source_fragment_id].text for r in results}
            if self.profile.review_policy
            in {
                "rc-type-proof-v6",
                "rc-subject-proof-v7",
                "rc-intent-v8",
                "rc-imperative-v9",
                "rc-conditional-v10",
            }
            else None
        )
        typed_ids: set[UUID] = set()
        type_records: dict[tuple[UUID, int, int, str], RcClauseEvidence] = {}
        if intent is not None and (intent.state != "NONE" or subject is not None):
            for r in results:
                if intent.state == "UNKNOWN" or subject == "UNKNOWN":
                    specific_rejections[r.chunk.chunk_id] = "SPECIFIC_QUERY_UNKNOWN"
                    continue
                region = regions[r.chunk.chunk_id]
                qualified = project_rc_conflicts(
                    [r.chunk],
                    regions={r.chunk.chunk_id: (region.start_byte, region.source_sha256)},
                    source_prefixes={r.chunk.chunk_id: prefixes[r.chunk.chunk_id]}
                    if prefixes is not None
                    else None,
                    qualified_visits=True,
                    independent_visit_type=self.profile.review_policy
                    in {
                        "rc-type-proof-v6",
                        "rc-subject-proof-v7",
                        "rc-intent-v8",
                        "rc-imperative-v9",
                        "rc-conditional-v10",
                    },
                    independent_rc_directive=self.profile.review_policy
                    in {
                        "rc-subject-proof-v7",
                        "rc-intent-v8",
                        "rc-imperative-v9",
                        "rc-conditional-v10",
                    },
                    source_contexts=whole_contexts,
                    imperative_sources=self.profile.review_policy
                    in {"rc-imperative-v9", "rc-conditional-v10"},
                    conditional_imperatives=self.profile.review_policy == "rc-conditional-v10",
                )
                qualified_evidence = (*qualified.clauses, *qualified.unknown_regions)
                for c in qualified_evidence:
                    if c.visit_type_proof is not None:
                        type_records[
                            (c.source_fragment_id, c.start_byte, c.end_byte, c.source_sha256)
                        ] = c
                        if len(type_records) > 256:
                            raise ValueError("candidate visit type proof budget exceeded")
                matched = any(
                    (
                        c.subject == intent.subject
                        if intent.state == "CANDIDATE"
                        else c.subject in {"VISIT", "VISIT_MEDICAL", "VISIT_SITE"}
                        if subject == "VISIT"
                        else c.subject == subject
                    )
                    and (
                        c.directive_signal == "CANDIDATE"
                        if self.profile.review_policy
                        in {
                            "rc-subject-proof-v7",
                            "rc-intent-v8",
                            "rc-imperative-v9",
                            "rc-conditional-v10",
                        }
                        else (
                            (c.visit_type_proof is not None and c.directive_signal == "CANDIDATE")
                            if self.profile.review_policy
                            in {
                                "rc-type-proof-v6",
                                "rc-subject-proof-v7",
                                "rc-intent-v8",
                                "rc-imperative-v9",
                                "rc-conditional-v10",
                            }
                            else c.value != "UNKNOWN"
                        )
                    )
                    and (query_lot is None or query_lot.lot is None or c.lot == query_lot.lot)
                    for c in qualified_evidence
                )
                if matched:
                    typed_ids.add(r.chunk.chunk_id)
                else:
                    specific_rejections[r.chunk.chunk_id] = (
                        "SPECIFIC_MISMATCH" if qualified.clauses else "SPECIFIC_UNPROVEN"
                    )
        chosen = [
            r
            for r in results
            if r.score >= self.profile.minimum_score and r.chunk.chunk_id not in specific_rejections
        ]
        score_trace: tuple[CandidateScoreTrace, ...] = ()
        if self.profile.review_policy in {
            "rc-recall-v4",
            "rc-specific-v5",
            "rc-type-proof-v6",
            "rc-subject-proof-v7",
            "rc-intent-v8",
            "rc-imperative-v9",
            "rc-conditional-v10",
        }:
            subject = (
                subject
                if self.profile.review_policy
                in {"rc-subject-proof-v7", "rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"}
                else generic_rc_subject(query)
            )
            rescue_ids = set()
            typed_rescue_ids: set[UUID] = set()
            for r in results:
                if r.score >= self.profile.minimum_score or r.chunk.chunk_id in specific_rejections:
                    continue
                if (
                    self.profile.review_policy
                    in {
                        "rc-type-proof-v6",
                        "rc-subject-proof-v7",
                        "rc-intent-v8",
                        "rc-imperative-v9",
                        "rc-conditional-v10",
                    }
                    and r.chunk.chunk_id in typed_ids
                ):
                    rescue_ids.add(r.chunk.chunk_id)
                    typed_rescue_ids.add(r.chunk.chunk_id)
                    continue
                if (
                    self.profile.review_policy
                    in {
                        "rc-subject-proof-v7",
                        "rc-intent-v8",
                        "rc-imperative-v9",
                        "rc-conditional-v10",
                    }
                    or subject is None
                ):
                    continue
                region = regions[r.chunk.chunk_id]
                rescue_projection = project_rc_conflicts(
                    [r.chunk],
                    regions={r.chunk.chunk_id: (region.start_byte, region.source_sha256)},
                    source_prefixes={r.chunk.chunk_id: prefixes[r.chunk.chunk_id]}
                    if prefixes is not None
                    else None,
                    qualified_visits=self.profile.review_policy
                    in {
                        "rc-specific-v5",
                        "rc-type-proof-v6",
                        "rc-subject-proof-v7",
                        "rc-intent-v8",
                        "rc-imperative-v9",
                        "rc-conditional-v10",
                    },
                    independent_visit_type=self.profile.review_policy
                    in {
                        "rc-type-proof-v6",
                        "rc-subject-proof-v7",
                        "rc-intent-v8",
                        "rc-imperative-v9",
                        "rc-conditional-v10",
                    },
                    independent_rc_directive=self.profile.review_policy
                    in {
                        "rc-subject-proof-v7",
                        "rc-intent-v8",
                        "rc-imperative-v9",
                        "rc-conditional-v10",
                    },
                    source_contexts=whole_contexts,
                    imperative_sources=self.profile.review_policy
                    in {"rc-imperative-v9", "rc-conditional-v10"},
                    conditional_imperatives=self.profile.review_policy == "rc-conditional-v10",
                )
                if any(c.subject == subject for c in rescue_projection.clauses):
                    rescue_ids.add(r.chunk.chunk_id)
            chosen = (chosen + [r for r in results if r.chunk.chunk_id in rescue_ids])[:top_k]
            selected_ids = {r.chunk.chunk_id for r in chosen}
            score_trace = tuple(
                CandidateScoreTrace(
                    r.chunk.chunk_id,
                    r.chunk.source_fragment_id,
                    rank,
                    r.score,
                    self.profile.minimum_score,
                    regions[r.chunk.chunk_id].start_byte,
                    regions[r.chunk.chunk_id].end_byte,
                    regions[r.chunk.chunk_id].source_sha256,
                    regions[r.chunk.chunk_id].segment_sha256,
                    specific_rejections.get(
                        r.chunk.chunk_id,
                        "DENSE_FLOOR"
                        if r.chunk.chunk_id in selected_ids
                        and r.score >= self.profile.minimum_score
                        else "RC_TYPED_RESCUE"
                        if r.chunk.chunk_id in typed_rescue_ids and r.chunk.chunk_id in selected_ids
                        else "RC_SUBJECT_RESCUE"
                        if r.chunk.chunk_id in selected_ids
                        else "TOP_K_LIMIT"
                        if r.score >= self.profile.minimum_score or r.chunk.chunk_id in rescue_ids
                        else "BELOW_FLOOR",
                    ),
                )
                for rank, r in enumerate(results, 1)
            )
        hits = tuple(
            CandidateHit(
                replace(r, chunk=replace(r.chunk, locator=deepcopy(r.chunk.locator))),
                regions[r.chunk.chunk_id].start_byte,
                regions[r.chunk.chunk_id].end_byte,
                regions[r.chunk.chunk_id].source_sha256,
                regions[r.chunk.chunk_id].segment_sha256,
            )
            for r in chosen
        )
        if not hits:
            return CandidateReading(
                self.profile.profile_id,
                "ABSTAIN",
                "RC_SPECIFIC_EVIDENCE_UNPROVEN"
                if intent is not None and intent.state != "NONE"
                else "BELOW_EXPERIMENTAL_FLOOR",
                query_lot=query_lot,
                score_trace=score_trace,
                specific_intent=intent,
                query_intent=query_intent,
                visit_type_evidence=tuple(type_records.values()),
            )
        if self.profile.review_policy in {
            "rc-opposition-v2",
            "rc-query-lot-v3",
            "rc-recall-v4",
            "rc-specific-v5",
            "rc-type-proof-v6",
            "rc-subject-proof-v7",
            "rc-intent-v8",
            "rc-imperative-v9",
            "rc-conditional-v10",
        }:
            projection = project_rc_conflicts(
                [h.result.chunk for h in hits],
                regions={h.result.chunk.chunk_id: (h.start_byte, h.source_sha256) for h in hits},
                source_prefixes=prefixes,
                qualified_visits=self.profile.review_policy
                in {
                    "rc-specific-v5",
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                },
                independent_visit_type=self.profile.review_policy
                in {
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                },
                independent_rc_directive=self.profile.review_policy
                in {
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                },
                source_contexts=whole_contexts,
                imperative_sources=self.profile.review_policy
                in {"rc-imperative-v9", "rc-conditional-v10"},
                conditional_imperatives=self.profile.review_policy == "rc-conditional-v10",
            )
            unscoped: tuple[RcClauseEvidence, ...] = ()
            if intent is not None and intent.state == "CANDIDATE":
                unscoped = tuple(
                    c
                    for c in (*projection.clauses, *projection.unknown_regions)
                    if c.subject != intent.subject
                )
                projection = RcConflictProjection(
                    tuple(c for c in projection.clauses if c.subject == intent.subject),
                    tuple(
                        link
                        for link in projection.links
                        if link.left.subject == link.right.subject == intent.subject
                    ),
                    tuple(c for c in projection.unknown_regions if c.subject == intent.subject),
                )
            if (
                self.profile.review_policy
                in {"rc-subject-proof-v7", "rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"}
                and subject is not None
            ):
                allowed = (
                    {"VISIT", "VISIT_MEDICAL", "VISIT_SITE"} if subject == "VISIT" else {subject}
                )
                unscoped += tuple(
                    c
                    for c in (*projection.clauses, *projection.unknown_regions)
                    if c.subject not in allowed
                )
                projection = RcConflictProjection(
                    tuple(c for c in projection.clauses if c.subject in allowed),
                    tuple(
                        link
                        for link in projection.links
                        if link.left.subject in allowed and link.right.subject in allowed
                    ),
                    tuple(c for c in projection.unknown_regions if c.subject in allowed),
                )
            if query_lot is not None:
                projection, lot_unscoped = scope_rc_projection(projection, query_lot)
                unscoped += lot_unscoped
            evidence = [e for link in projection.links for e in (link.left, link.right)]
            evidence.extend(projection.unknown_regions)
            evidence.extend(c for c in projection.clauses if c.kind == "RECTIFICATION")
            sources = tuple(dict.fromkeys(e.source_fragment_id for e in evidence))
            reason = (
                "RC_OPPOSITION_SIGNAL"
                if projection.links
                else "RC_UNPROVEN_CLAUSE"
                if projection.unknown_regions
                else "RECTIFICATION_SIGNAL"
                if sources
                else "SOURCE_CANDIDATES_ONLY"
            )
            if query_lot is not None:
                if query_lot.state == "UNKNOWN":
                    reason = "RC_QUERY_LOT_UNKNOWN"
                elif not projection.clauses and not projection.unknown_regions:
                    reason = "RC_NO_PROVEN_MATCHING_LOT"
            return CandidateReading(
                self.profile.profile_id,
                "REVIEW_REQUIRED"
                if sources or reason in {"RC_QUERY_LOT_UNKNOWN", "RC_NO_PROVEN_MATCHING_LOT"}
                else "CANDIDATES_ONLY",
                reason,
                hits,
                review_source_ids=sources,
                rc_projection=projection,
                query_lot=query_lot,
                rc_unscoped_evidence=unscoped,
                score_trace=score_trace,
                specific_intent=intent,
                query_intent=query_intent,
                visit_type_evidence=tuple(type_records.values()),
            )
        review_sources = tuple(
            dict.fromkeys(
                h.result.chunk.source_fragment_id
                for h in hits
                if re.search(r"\b(?:rectificatif|annul\w*|remplac\w*)\b", h.result.chunk.text, re.I)
            )
        )
        review = bool(review_sources)
        return CandidateReading(
            self.profile.profile_id,
            "REVIEW_REQUIRED" if review else "CANDIDATES_ONLY",
            "RECTIFICATION_SIGNAL" if review else "SOURCE_CANDIDATES_ONLY",
            hits,
            review_source_ids=review_sources,
        )
