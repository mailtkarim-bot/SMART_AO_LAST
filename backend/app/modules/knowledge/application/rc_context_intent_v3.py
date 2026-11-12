"""Qualify bounded workflow contexts and retain original query provenance."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from hashlib import sha256
from typing import get_args

from app.modules.knowledge.application.rc_candidate_conflicts import RcSignalAnchor
from app.modules.knowledge.application.rc_compositional_intent_v2 import (
    _DEMAND as _DEMAND_V2,
)
from app.modules.knowledge.application.rc_compositional_intent_v2 import (
    recognize_rc_intent as _recognize_v2,
)
from app.modules.knowledge.application.rc_query_intent import (
    Coverage,
    Demand,
    RcQueryIntent,
    Subject,
)
from app.modules.knowledge.application.rc_query_scope import RcQueryLot
from app.modules.knowledge.application.retrieval import _FINANCIAL_QUERY_PATTERN

# shortcut: finite workflow grammar; other contexts stay unqualified until a new version.
NEUTRAL_CONTEXT_PATTERNS = (
    r"pour\s+(?:préparer|rédiger|constituer|compléter|organiser)\s+(?:notre|la|une)\s+(?:offre|réponse|candidature|dossier)",
    r"dans\s+le\s+cadre\s+de\s+(?:notre|la)\s+(?:réponse|offre|candidature)",
    r"pour\s+la\s+(?:préparation|rédaction|constitution)\s+de\s+notre\s+(?:offre|réponse|candidature|dossier)",
    r"à\s+titre\s+de\s+précision",
    r"pour\s+information",
)
_CONTEXT = r"(?:" + "|".join(NEUTRAL_CONTEXT_PATTERNS) + r")"
_PREFIX = re.compile(r"^\s*" + _CONTEXT + r"\s*[,:—]\s*", re.I)
_SUFFIX = re.compile(r",\s*" + _CONTEXT + r"\s*(?=\?\s*$)", re.I)
_META = re.compile(
    r'[«»“”"]|\b(?:mot|terme|expliquez|ignore|réponds|signifie|exemple|comparaison|contrairement)\b',
    re.I,
)
_REFERENCE = re.compile(
    r"\b(?:(?:ce|cet|cette|ces)\s+(?:document|formulaire|pièce|élément)|celui|celle|ceux|celles)\b"
    r"|\b(?:le|la|les)\s+(?:fournir|joindre|remettre|présenter|annexer|produire|effectuer|réaliser)\b",
    re.I,
)


@dataclass(frozen=True, slots=True)
class RcContextRecognition:
    intent: RcQueryIntent | None
    reason: str
    mechanism: str = "rc-context-v3"
    anchor_convention: str = "lexical-cue-v3"
    context_evidence: tuple[RcSignalAnchor, ...] = ()


def recognize_rc_intent(query: str) -> RcContextRecognition:
    if not isinstance(query, str) or not query.strip() or len(query) > 2000:
        return RcContextRecognition(None, "INVALID_QUERY_BUDGET")
    try:
        original = query.encode()
    except UnicodeError:
        return RcContextRecognition(None, "INVALID_QUERY_BUDGET")
    if _FINANCIAL_QUERY_PATTERN.search(query):
        return RcContextRecognition(None, "FINANCIAL_SCOPE_REFUSED")
    original_hash = sha256(original).hexdigest()
    regions = [
        (m.start(), m.end()) for m in (_PREFIX.match(query), _SUFFIX.search(query)) if m is not None
    ]
    contexts = tuple(
        RcSignalAnchor(
            "NEUTRAL_CONTEXT",
            len(query[:start].encode()),
            len(query[:end].encode()),
            query[start:end],
        )
        for start, end in regions
    )

    def failure(reason: str) -> RcContextRecognition:
        return RcContextRecognition(
            RcQueryIntent("UNKNOWN", "UNKNOWN", "UNKNOWN", RcQueryLot(), (), original_hash),
            reason,
            context_evidence=contexts,
        )

    if len(regions) == 2 and regions[0][1] > regions[1][0]:
        return replace(failure("INSUFFICIENT_EVIDENCE"), context_evidence=())
    chars = list(query)
    for start, end in regions:
        chars[start:end] = " " * (end - start)
    view = "".join(chars)
    view_bytes = view.encode()

    def mapped(anchor: RcSignalAnchor) -> RcSignalAnchor:
        start, end = anchor.start_byte, anchor.end_byte
        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
            or not 0 <= start < end <= len(view_bytes)
        ):
            raise ValueError("invalid candidate anchor")
        lower = len(view_bytes[:start].decode())
        upper = len(view_bytes[:end].decode())
        if any(lower < stop and begin < upper for begin, stop in regions):
            raise ValueError("candidate anchor overlaps qualified context")
        if query[lower:upper] != anchor.excerpt:
            raise ValueError("candidate anchor differs from original query")
        return RcSignalAnchor(
            anchor.signal, len(query[:lower].encode()), len(query[:upper].encode()), anchor.excerpt
        )

    try:
        result = _recognize_v2(view)
        reason = result.reason
        if not isinstance(reason, str) or not reason:
            return failure("INVALID_RECOGNIZER_OUTPUT")
        intent = result.intent
        if intent is None or intent.query_sha256 != sha256(view_bytes).hexdigest():
            return failure("INVALID_RECOGNIZER_OUTPUT")
        if (
            intent.subject not in get_args(Subject)
            or intent.demand not in get_args(Demand)
            or intent.coverage not in get_args(Coverage)
        ):
            return failure("INVALID_RECOGNIZER_OUTPUT")
        anchors = tuple(mapped(a) for a in intent.anchors)
        subject_anchors = [a for a in anchors if a.signal == "SUBJECT"]
        expected_subject = "UNKNOWN"
        if len(subject_anchors) == 1:
            cue = " ".join(subject_anchors[0].excerpt.casefold().split())
            if cue in {"dc1", "dc2"}:
                expected_subject = cue.upper()
            elif cue == "mémoire technique":
                expected_subject = "MEMOIRE_TECHNIQUE"
            elif re.fullmatch(r"variantes?", cue):
                expected_subject = "VARIANTS"
            elif re.fullmatch(r"visites?", cue):
                expected_subject = "VISIT"
            elif re.fullmatch(r"visites? médicales?", cue):
                expected_subject = "VISIT_MEDICAL"
            elif re.fullmatch(r"visites? (?:de|du|des) (?:chantier|site|locaux)", cue):
                expected_subject = "VISIT_SITE"
        if intent.subject != expected_subject:
            return failure("INVALID_RECOGNIZER_OUTPUT")
        allowed = {
            "COVERED": {("OBLIGATION", "UNIQUE_EXPLICIT_REQUEST")},
            "UNSUPPORTED": {
                ("OBLIGATION", "UNSUPPORTED_CONDITION"),
                ("DATE_TIME", "UNSUPPORTED_TIME"),
                ("LOCATION", "UNSUPPORTED_LOCATION"),
            },
            "AMBIGUOUS": {
                ("UNKNOWN", reason)
                for reason in (
                    "INVALID_LOT",
                    "MULTIPLE_LOTS",
                    "MULTIPLE_SUBJECTS",
                    "MULTIPLE_DEMANDS",
                )
            },
            "UNKNOWN": {
                ("UNKNOWN", reason)
                for reason in (
                    "TRUNCATED",
                    "NON_ACTIVE_REQUEST",
                    "UNRESOLVED_REFERENCE",
                    "UNKNOWN_SUBJECT",
                    "INSUFFICIENT_EVIDENCE",
                )
            },
        }
        if (intent.demand, reason) not in allowed[intent.coverage]:
            return failure("INVALID_RECOGNIZER_OUTPUT")
        demand_anchors = [a for a in anchors if a.signal == "DEMAND"]
        if intent.coverage in {"COVERED", "UNSUPPORTED"}:
            if intent.subject == "UNKNOWN" or len(subject_anchors) != 1 or len(demand_anchors) != 1:
                return failure("INVALID_RECOGNIZER_OUTPUT")
            cue = demand_anchors[0].excerpt
            valid_cue = (
                bool(
                    re.fullmatch(r"(?:à\s+quelle\s+(?:heure|date)|quel\s+horaire|quand)", cue, re.I)
                )
                if intent.demand == "DATE_TIME"
                else bool(re.fullmatch(r"(?:où|lieu)", cue, re.I))
                if intent.demand == "LOCATION"
                else bool(_DEMAND_V2.fullmatch(cue))
                or reason == "UNSUPPORTED_CONDITION"
                and bool(
                    re.fullmatch(
                        r"(?:(?:à|sous)\s+quelles\s+conditions|dans\s+quels\s+cas)", cue, re.I
                    )
                )
            )
            if not valid_cue:
                return failure("INVALID_RECOGNIZER_OUTPUT")
        signals = [a.signal for a in anchors]
        if any(signal not in {"SUBJECT", "DEMAND", "LOT"} for signal in signals):
            return failure("INVALID_RECOGNIZER_OUTPUT")
        if intent.coverage == "COVERED" and (
            intent.subject == "UNKNOWN"
            or intent.demand != "OBLIGATION"
            or signals.count("SUBJECT") != 1
            or signals.count("DEMAND") != 1
        ):
            return failure("INVALID_RECOGNIZER_OUTPUT")
        if intent.coverage in {"UNKNOWN", "AMBIGUOUS"} and "DEMAND" in signals:
            return failure("INVALID_RECOGNIZER_OUTPUT")
        lot_anchors = [a for a in anchors if a.signal == "LOT"]
        scope = intent.scope
        if scope.state == "CANDIDATE":
            if any(
                not isinstance(v, int) or isinstance(v, bool)
                for v in (scope.lot, scope.start_byte, scope.end_byte)
            ):
                return failure("INVALID_RECOGNIZER_OUTPUT")
            if len(lot_anchors) != 1:
                return failure("INVALID_RECOGNIZER_OUTPUT")
            lot = lot_anchors[0]
            literal = re.fullmatch(r"lot\s+(?:n[°o]\s*)?([0-9]+)", lot.excerpt, re.I)
            if not literal or not 1 <= int(literal[1]) <= 999 or int(literal[1]) != scope.lot:
                return failure("INVALID_RECOGNIZER_OUTPUT")
            if (intent.scope.start_byte, intent.scope.end_byte) != (
                next(a for a in intent.anchors if a.signal == "LOT").start_byte,
                next(a for a in intent.anchors if a.signal == "LOT").end_byte,
            ):
                return failure("INVALID_RECOGNIZER_OUTPUT")
            scope = RcQueryLot("CANDIDATE", scope.lot, lot.start_byte, lot.end_byte)
        elif (
            scope.state != "UNKNOWN"
            or scope.lot is not None
            or scope.start_byte is not None
            or scope.end_byte is not None
            or lot_anchors
        ):
            return failure("INVALID_RECOGNIZER_OUTPUT")
        intent = replace(intent, scope=scope, anchors=anchors, query_sha256=original_hash)
    except TimeoutError:
        return failure("RECOGNIZER_UNAVAILABLE")
    except (ValueError, UnicodeError, AttributeError, TypeError, StopIteration):
        return failure("INVALID_RECOGNIZER_OUTPUT")
    reason = result.reason
    if (
        reason == "NON_ACTIVE_REQUEST"
        and not query.rstrip().endswith("?")
        and not _META.search(query)
    ):
        reason = "INSUFFICIENT_EVIDENCE"
    if (
        reason == "UNRESOLVED_REFERENCE"
        and intent.subject == "UNKNOWN"
        and not _REFERENCE.search(query)
    ):
        reason = "UNKNOWN_SUBJECT"
    return RcContextRecognition(intent, reason, context_evidence=contexts)
