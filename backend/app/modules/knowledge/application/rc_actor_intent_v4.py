"""Experimental relation proofs for a question; no source or business authority."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from hashlib import sha256

from app.modules.knowledge.application.rc_candidate_conflicts import RcSignalAnchor
from app.modules.knowledge.application.rc_context_intent_v3 import NEUTRAL_CONTEXT_PATTERNS
from app.modules.knowledge.application.rc_context_intent_v3 import recognize_rc_intent as _v3
from app.modules.knowledge.application.rc_query_intent import RcQueryIntent, _subject
from app.modules.knowledge.application.rc_query_scope import RcQueryLot, parse_query_lot
from app.modules.knowledge.application.retrieval import _FINANCIAL_QUERY_PATTERN


@dataclass(frozen=True, slots=True)
class ContextBinding:
    context: RcSignalAnchor
    owner: RcSignalAnchor | None = None


@dataclass(frozen=True, slots=True)
class RcActorRecognition:
    intent: RcQueryIntent | None
    reason: str
    actor: RcSignalAnchor | None = None
    object_evidence: RcSignalAnchor | None = None
    action_evidence: RcSignalAnchor | None = None
    contexts: tuple[ContextBinding, ...] = ()
    attachment_evidence: RcSignalAnchor | None = None
    mechanism: str = "rc-actor-intent-v4"
    anchor_convention: str = "original-query-utf8-v4"


# shortcut: bounded explicit relations; other constructions require a new qualified version.
_POSSESSIVE = (
    r"pour\s+(?:préparer|rédiger|constituer|compléter|organiser)\s+"
    r"(?:sa\s+(?:candidature|réponse)|son\s+(?:offre|dossier))"
)
_CONTEXT = r"(?:" + "|".join((*NEUTRAL_CONTEXT_PATTERNS, _POSSESSIVE)) + r")"
_PREFIX = re.compile(r"^\s*" + _CONTEXT + r"\s*[,:—]\s*", re.I)
_SUFFIX = re.compile(r",\s*" + _CONTEXT + r"\s*(?=\?\s*$)", re.I)
_ACTOR = (
    r"(?:(?:le|chaque|un|tout)\s+(?:candidat|soumissionnaire|titulaire|employeur|opérateur)"
    r"|les\s+(?:candidats|soumissionnaires|titulaires|employeurs|opérateurs)"
    r"|l['’](?:employeur|opérateur))"
)
_CUE = (
    r"DC[12]|mémoire\s+technique|variantes?|"
    r"visites?(?:\s+(?:médicales?|(?:de|du|des)\s+(?:chantier|site|locaux)))?"
)
_OBJECT = (
    r"(?P<object>(?:(?:le|la|les|un|une|des)\s+)?(?P<form>formulaire\s+)?"
    r"(?P<cue>" + _CUE + r")(?:\s+(?P<qualifier>signé|renseigné|complété))?)"
)
_ACTION = r"joindre|fournir|remettre|présenter|annexer|produire|effectuer|réaliser|proposer"
_LOT_TEXT = r"lot\s+(?:n[°o]\s*)?[0-9]{1,3}"
_CORE = re.compile(
    r"\s*(?:(?:pour\s+le\s+)?" + _LOT_TEXT + r"\s*[:,]\s*)?"
    r"(?P<actor>" + _ACTOR + r")\s+"
    r"(?P<request>(?P<ne>ne\s+)?(?P<modal>doivent-ils|doit-il|doivent|doit|"
    r"est-il\s+tenu\s+de|sont-ils\s+tenus\s+de)(?P<pas>\s+pas)?)\s+"
    r"(?P<action>"
    + _ACTION
    + r")\s+"
    + _OBJECT
    + r"(?:\s+(?P<attachment>au\s+dossier|à\s+(?:sa|notre|la)\s+candidature|"
    r"à\s+(?:son|notre|la)\s+offre))?"
    r"(?:\s+(?:pour\s+le|du|au)\s+" + _LOT_TEXT + r")?\s*\?\s*",
    re.I,
)
_CONDITION = re.compile(
    r"\b(?:si|sauf|lorsque|sans|uniquement|sous\s+réserve|en\s+cas|à\s+condition)\b", re.I
)
_NEGATED_ACTION = re.compile(r"\bne\s+(?:pas|jamais)\s+(?:" + _ACTION + r")\b", re.I)


def recognize_rc_intent(query: str) -> RcActorRecognition:
    if not isinstance(query, str) or not query.strip() or len(query) > 2000:
        return RcActorRecognition(None, "INVALID_QUERY_BUDGET")
    try:
        raw = query.encode()
    except UnicodeError:
        return RcActorRecognition(None, "INVALID_QUERY_BUDGET")
    if _FINANCIAL_QUERY_PATTERN.search(query):
        return RcActorRecognition(None, "FINANCIAL_SCOPE_REFUSED")
    digest = sha256(raw).hexdigest()

    def failure(reason: str) -> RcActorRecognition:
        return RcActorRecognition(
            RcQueryIntent("UNKNOWN", "UNKNOWN", "UNKNOWN", RcQueryLot(), (), digest), reason
        )

    def anchor(signal: str, start: int, end: int) -> RcSignalAnchor:
        return RcSignalAnchor(
            signal, len(query[:start].encode()), len(query[:end].encode()), query[start:end]
        )

    if _CONDITION.search(query):
        return failure("CONDITIONAL_UNQUALIFIED")
    if _NEGATED_ACTION.search(query):
        return failure("NEGATION_SCOPE_UNQUALIFIED")
    if query.count("?") != 1 or not query.rstrip().endswith("?"):
        return failure("NON_ACTIVE_REQUEST")
    prefix, suffix = _PREFIX.match(query), _SUFFIX.search(query)
    regions = [(m.start(), m.end()) for m in (prefix, suffix) if m is not None]
    if len(regions) == 2 and regions[0][1] > regions[1][0]:
        return failure("OVERLAPPING_CONTEXT")
    start = prefix.end() if prefix else 0
    end = suffix.start() if suffix else len(query)
    core = query[start:end] + ("?" if suffix else "")
    match = _CORE.fullmatch(core)
    scope = parse_query_lot(query)
    if re.search(r"\blots?\b", query, re.I) and scope.state != "CANDIDATE":
        return failure("LOT_UNQUALIFIED")
    if match is None:
        if any(re.search(r"\b(?:sa|son)\b", query[a:b], re.I) for a, b in regions):
            return failure("UNRESOLVED_POSSESSOR")
        legacy = _v3(query)
        if legacy.intent is None or legacy.intent.coverage != "COVERED":
            return failure(legacy.reason)
        subject_anchor = next(a for a in legacy.intent.anchors if a.signal == "SUBJECT")
        object_match = next(
            (
                m
                for m in re.finditer(r"\b" + _OBJECT + r"\b", query, re.I)
                if len(query[: m.start("cue")].encode()) == subject_anchor.start_byte
                and len(query[: m.end("cue")].encode()) == subject_anchor.end_byte
            ),
            None,
        )
        if (
            object_match is None
            or object_match["form"]
            and legacy.intent.subject not in {"DC1", "DC2"}
        ):
            return failure("OBJECT_HEAD_UNQUALIFIED")
        object_anchor = anchor("OBJECT", object_match.start("object"), object_match.end("object"))
        legacy_anchors = []
        for a in legacy.intent.anchors:
            if a.signal == "DEMAND":
                lower = len(raw[: a.start_byte].decode())
                predicate = re.search(
                    r"\b(?:est-il|est-elle|sont-ils|sont-elles|serait-il|serait-elle)\s+(?:(?:un|une)\s+(?:pièce|document)\s+)?$",
                    query[:lower],
                    re.I,
                )
                if predicate:
                    a = anchor("DEMAND", predicate.start(), len(raw[: a.end_byte].decode()))
            legacy_anchors.append(a)
        return RcActorRecognition(
            replace(legacy.intent, anchors=tuple(legacy_anchors)),
            "UNIQUE_EXPLICIT_REQUEST",
            object_evidence=object_anchor,
            contexts=tuple(ContextBinding(a) for a in legacy.context_evidence),
        )

    def group(signal: str, name: str) -> RcSignalAnchor:
        return anchor(signal, start + match.start(name), start + match.end(name))

    actor = group("ACTOR", "actor")
    plural = bool(re.match(r"les\s", actor.excerpt, re.I))
    plural_modal = match["modal"].casefold().startswith(("doivent", "sont-ils"))
    if plural != plural_modal or bool(match["ne"]) != bool(match["pas"]):
        return failure("ACTOR_REQUEST_DISCORDANT")
    subject = _subject(match["cue"])
    if match["form"] and subject not in {"DC1", "DC2"}:
        return failure("OBJECT_HEAD_UNQUALIFIED")
    action = match["action"].casefold()
    if subject.startswith("VISIT"):
        compatible = action in {"effectuer", "réaliser"} and match["qualifier"] is None
    elif subject == "VARIANTS":
        compatible = action in {"proposer", "présenter", "remettre"} and match["qualifier"] is None
    else:
        compatible = action in {
            "joindre",
            "fournir",
            "remettre",
            "présenter",
            "annexer",
            "produire",
        }
    if not compatible:
        return failure("ACTION_OBJECT_DISCORDANT")
    subject_anchor = group("SUBJECT", "cue")
    demand = anchor("DEMAND", start + match.start("request"), start + match.end("action"))
    anchors = [subject_anchor, demand]
    if scope.state == "CANDIDATE":
        assert scope.start_byte is not None and scope.end_byte is not None
        anchors.append(
            RcSignalAnchor(
                "LOT",
                scope.start_byte,
                scope.end_byte,
                raw[scope.start_byte : scope.end_byte].decode(),
            )
        )
    bindings = tuple(
        ContextBinding(
            anchor("NEUTRAL_CONTEXT", a, b),
            actor if re.search(r"\b(?:sa|son)\b", query[a:b], re.I) else None,
        )
        for a, b in regions
    )
    return RcActorRecognition(
        RcQueryIntent(
            subject,
            "OBLIGATION",
            "COVERED",
            scope,
            tuple(sorted(anchors, key=lambda a: (a.start_byte, a.end_byte))),
            digest,
        ),
        "UNIQUE_EXPLICIT_REQUEST",
        actor,
        group("OBJECT", "object"),
        group("ACTION", "action"),
        bindings,
        group("WORKFLOW_ATTACHMENT", "attachment") if match["attachment"] else None,
    )
