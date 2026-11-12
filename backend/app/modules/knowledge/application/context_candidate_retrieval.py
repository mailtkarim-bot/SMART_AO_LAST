"""Explicit experimental composition; no active factory, persistence or business act."""

from __future__ import annotations

import json
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass, replace
from hashlib import sha256
from typing import Literal
from uuid import UUID

from app.modules.knowledge.application.candidate_retrieval import (
    CandidateEncoder,
    CandidateHit,
    CandidateReading,
    CandidateRetrievalService,
    CandidateScoreTrace,
)
from app.modules.knowledge.application.rc_candidate_conflicts import (
    RcConflictProjection,
    project_rc_conflicts,
)
from app.modules.knowledge.application.rc_context_intent_v3 import (
    RcContextRecognition,
    recognize_rc_intent,
)
from app.modules.knowledge.application.rc_query_scope import scope_rc_projection
from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected
from app.modules.knowledge.application.service import DceRetrievalSource
from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile
from app.modules.knowledge.domain.retrieval import (
    DataClassification,
    RetrievalChunk,
    RetrievalScope,
)


@dataclass(frozen=True, slots=True)
class ContextCandidateReading:
    adapter_id: str
    recognition: RcContextRecognition
    reading: CandidateReading


class _ScopedCapture:
    def __init__(self, source: DceRetrievalSource, scope: RetrievalScope) -> None:
        self.source = source
        self.scope = scope
        self.last: tuple[RetrievalChunk, ...] = ()

    def read_chunks(
        self, *, tenant_id: UUID, case_id: UUID, dce_version_id: UUID
    ) -> Sequence[RetrievalChunk]:
        if (tenant_id, case_id, dce_version_id) != (
            self.scope.tenant_id,
            self.scope.case_id,
            self.scope.dce_version_id,
        ):
            raise ValueError("candidate capture scope mismatch")
        visible = [
            c
            for c in self.source.read_chunks(
                tenant_id=tenant_id, case_id=case_id, dce_version_id=dce_version_id
            )
            if c.is_visible_in(self.scope)
            and c.classification
            in {DataClassification.PUBLIC, DataClassification.INTERNAL_OPERATIONAL}
        ]
        if len(visible) > 128:
            raise ValueError("candidate source budget exceeded")
        visible.sort(key=lambda c: (c.ordinal, str(c.source_fragment_id)))
        self.last = tuple(replace(c, locator=deepcopy(c.locator)) for c in visible)
        return self.last


def _projection(
    hits: Sequence[CandidateHit], sources: Sequence[RetrievalChunk]
) -> RcConflictProjection:
    by_id = {c.source_fragment_id: c for c in sources}
    prefixes = {}
    contexts = {}
    for hit in hits:
        chunk = hit.result.chunk
        source = by_id.get(chunk.source_fragment_id)
        if source is None:
            raise ValueError("candidate source provenance mismatch")
        raw = source.text.encode()
        if (
            sha256(raw).hexdigest() != hit.source_sha256
            or raw[hit.start_byte : hit.end_byte] != chunk.text.encode()
            or sha256(chunk.text.encode()).hexdigest() != hit.segment_sha256
        ):
            raise ValueError("candidate source provenance mismatch")
        prefixes[chunk.chunk_id] = raw[: hit.start_byte].decode()
        contexts[chunk.chunk_id] = source.text
    return project_rc_conflicts(
        [h.result.chunk for h in hits],
        regions={h.result.chunk.chunk_id: (h.start_byte, h.source_sha256) for h in hits},
        source_prefixes=prefixes,
        source_contexts=contexts,
        qualified_visits=True,
        independent_visit_type=True,
        independent_rc_directive=True,
        imperative_sources=True,
        conditional_imperatives=True,
    )


class ContextCandidateRetrieval:
    def __init__(
        self,
        *,
        transport_profile: CandidateRetrievalProfile,
        source: DceRetrievalSource,
        encoder: CandidateEncoder,
    ) -> None:
        if (
            transport_profile.review_policy != "rectification-signal-v1"
            or transport_profile.minimum_score != 0.0
        ):
            raise ValueError("explicit zero-floor transport profile required")
        if encoder.profile_id != transport_profile.profile_id:
            raise ValueError("candidate encoder profile mismatch")
        self._profile = transport_profile
        self._source = source
        self._encoder = encoder
        self._floor = 0.85
        identity = dict(
            transport_profile=transport_profile.profile_id,
            recognizer="rc-context-v3",
            anchor_convention="lexical-cue-v3",
            source_policy="rc-conditional-v10",
            selection_floor=self._floor,
            transport_top_k=50,
        )
        self.adapter_id = (
            "rc-context-retrieval-v1:"
            + sha256(
                json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )

    def retrieve(
        self, *, query: str, scope: RetrievalScope, top_k: int = 5
    ) -> ContextCandidateReading:
        if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 50:
            raise ValueError("invalid candidate top_k budget")
        recognition = recognize_rc_intent(query)
        if recognition.reason == "INVALID_QUERY_BUDGET":
            raise ValueError("invalid candidate query budget")
        if recognition.reason == "FINANCIAL_SCOPE_REFUSED":
            raise FinancialRetrievalQueryRejected("FINANCIAL_RETRIEVAL_SCOPE_REQUIRED")
        intent = recognition.intent
        if intent is None:
            raise ValueError("invalid recognition envelope")

        def wrap(reading: CandidateReading) -> ContextCandidateReading:
            return ContextCandidateReading(
                self.adapter_id,
                recognition,
                replace(reading, query_lot=intent.scope, query_intent=intent),
            )

        def empty(
            state: Literal["ABSTAIN", "REVIEW_REQUIRED"], reason: str
        ) -> ContextCandidateReading:
            return wrap(CandidateReading(self._profile.profile_id, state, reason))

        if intent.coverage != "COVERED":
            return empty("ABSTAIN", "RC_QUERY_NOT_COVERED")
        capture = _ScopedCapture(self._source, scope)
        # Zero is enumeration only; typed proof gates every returned hit and rescue.
        transport = CandidateRetrievalService(
            profile=self._profile, source=capture, encoder=self._encoder
        )
        raw = transport.retrieve(query=query, scope=scope, top_k=50)
        if not raw.hits:
            return wrap(raw)
        validated = capture.last
        allowed = (
            {"VISIT", "VISIT_MEDICAL", "VISIT_SITE"}
            if intent.subject == "VISIT"
            else {intent.subject}
        )
        matched = {}
        for hit in raw.hits:
            projected = _projection([hit], validated)
            matched[hit.result.chunk.chunk_id] = any(
                c.subject in allowed
                and c.directive_signal == "CANDIDATE"
                and (intent.scope.lot is None or c.lot == intent.scope.lot)
                for c in (*projected.clauses, *projected.unknown_regions)
            )
        hits = tuple(h for h in raw.hits if matched[h.result.chunk.chunk_id])[:top_k]
        projected = _projection(hits, validated)
        clauses = tuple(c for c in projected.clauses if c.subject in allowed)
        unknown = tuple(c for c in projected.unknown_regions if c.subject in allowed)
        unscoped = tuple(
            c for c in (*projected.clauses, *projected.unknown_regions) if c.subject not in allowed
        )
        typed = RcConflictProjection(
            clauses,
            tuple(
                link
                for link in projected.links
                if link.left.subject in allowed and link.right.subject in allowed
            ),
            unknown,
        )
        typed, lot_unscoped = scope_rc_projection(typed, intent.scope)
        unscoped += lot_unscoped
        # Revalidate again after projection; a changed read discards all source evidence.
        latest = capture.read_chunks(
            tenant_id=scope.tenant_id, case_id=scope.case_id, dce_version_id=scope.dce_version_id
        )
        if tuple(latest) != validated:
            return empty("REVIEW_REQUIRED", "SOURCE_CHANGED")
        if self._encoder.profile_id != self._profile.profile_id:
            raise ValueError("candidate encoder profile changed")
        selected = {h.result.chunk.chunk_id for h in hits}
        trace = tuple(
            CandidateScoreTrace(
                h.result.chunk.chunk_id,
                h.result.chunk.source_fragment_id,
                rank,
                h.result.score,
                self._floor,
                h.start_byte,
                h.end_byte,
                h.source_sha256,
                h.segment_sha256,
                "SPECIFIC_UNPROVEN"
                if not matched[h.result.chunk.chunk_id]
                else "TOP_K_LIMIT"
                if h.result.chunk.chunk_id not in selected
                else "DENSE_FLOOR"
                if h.result.score >= self._floor
                else "RC_TYPED_RESCUE",
            )
            for rank, h in enumerate(raw.hits, 1)
        )
        if not hits:
            return wrap(
                CandidateReading(
                    self._profile.profile_id,
                    "ABSTAIN",
                    "RC_SPECIFIC_EVIDENCE_UNPROVEN",
                    score_trace=trace,
                )
            )
        evidence = [e for link in typed.links for e in (link.left, link.right)]
        evidence.extend(typed.unknown_regions)
        evidence.extend(c for c in typed.clauses if c.kind == "RECTIFICATION")
        review_ids = tuple(
            dict.fromkeys(
                [e.source_fragment_id for e in evidence]
                + [
                    h.result.chunk.source_fragment_id
                    for h in hits
                    if h.result.chunk.source_fragment_id in raw.review_source_ids
                ]
            )
        )
        reason = (
            "RC_OPPOSITION_SIGNAL"
            if typed.links
            else "RC_UNPROVEN_CLAUSE"
            if typed.unknown_regions
            else "RECTIFICATION_SIGNAL"
            if review_ids
            else "SOURCE_CANDIDATES_ONLY"
        )
        if intent.scope.state == "UNKNOWN":
            reason = "RC_QUERY_LOT_UNKNOWN"
            review_ids = tuple(dict.fromkeys(h.result.chunk.source_fragment_id for h in hits))
        visits = tuple(
            c
            for c in (*typed.clauses, *typed.unknown_regions, *unscoped)
            if c.visit_type_proof is not None and c.subject in allowed
        )
        return wrap(
            CandidateReading(
                self._profile.profile_id,
                "REVIEW_REQUIRED"
                if review_ids or intent.scope.state == "UNKNOWN"
                else "CANDIDATES_ONLY",
                reason,
                hits,
                review_source_ids=review_ids,
                rc_projection=typed,
                rc_unscoped_evidence=unscoped,
                score_trace=trace,
                visit_type_evidence=visits,
            )
        )
