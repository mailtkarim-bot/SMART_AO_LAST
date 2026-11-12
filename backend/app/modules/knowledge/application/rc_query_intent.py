"""Closed query recognition only; no source applicability or business authority."""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

from app.modules.knowledge.application.rc_candidate_conflicts import RcSignalAnchor
from app.modules.knowledge.application.rc_query_scope import RcQueryLot, parse_query_lot
from app.modules.knowledge.application.rc_specific_intent import VISIT_QUALIFIER

Subject = Literal[
    "VISIT", "VISIT_MEDICAL", "VISIT_SITE", "DC1", "DC2", "MEMOIRE_TECHNIQUE", "VARIANTS", "UNKNOWN"
]
Demand = Literal["OBLIGATION", "DATE_TIME", "LOCATION", "UNKNOWN"]
Coverage = Literal["COVERED", "UNSUPPORTED", "AMBIGUOUS", "UNKNOWN"]
_SUBJECT = (
    r"(?:visites?(?:\s+"
    + VISIT_QUALIFIER.replace("médicale", "médicales?")
    + r")?|DC[12]|mémoire\s+technique|variantes?)"
)
_SUBJECTS = re.compile(r"\b" + _SUBJECT + r"\b", re.I)
_CAPTURE = r"(?P<subject>" + _SUBJECT + r")"
_ARTICLE = r"(?:la|le|les|une|un|des)\s+"
_DESCRIPTOR = r"(?:(?P<form>formulaire)\s+|(?P<participation>participation)\s+à\s+(?:la|une)\s+)?"
_ADJECTIVE = (
    r"(?:obligatoires?|exigé(?:e)?s?|requis(?:es?)?|facultati(?:f|ve)s?|"
    r"imposé(?:e)?s?|nécessaires?|demandé(?:e)?s?|autorisées?|permises?|interdites?)"
)
_SUFFIX = r"(?:\s+(?:pour\s+le|du|au)\s+lot\s+(?:n[°o]\s*)?[0-9]{1,3})?\s*\?\s*"
_PATTERNS = [
    re.compile(p + _SUFFIX, re.I)
    for p in [
        r"\s*(?:est-ce\s+que\s+)?"
        + _ARTICLE
        + _DESCRIPTOR
        + _CAPTURE
        + r"\s+(?:est-elle|est-il|sont-elles|sont-ils|est|sont)\s+(?P<demand>"
        + _ADJECTIVE
        + r")",
        r"\s*quelles\s+"
        + _CAPTURE
        + r"\s+sont\s+(?P<demand>"
        + _ADJECTIVE
        + r")(?:\s+par\s+le\s+règlement)?",
        r"\s*quelles\s+sont\s+les\s+(?P<demand>obligations)\s+de\s+" + _CAPTURE,
        r"\s*quelles\s+(?P<demand>obligations)\s+de\s+" + _CAPTURE + r"\s+sont\s+prévues",
        r"\s*(?P<demand>faut-il\s+(?P<action>effectuer|réaliser|prévoir|joindre|fournir|remettre|présenter))\s+"
        + _ARTICLE
        + _DESCRIPTOR
        + _CAPTURE
        + r"(?:\s+au\s+dossier)?",
        r"\s*" + _ARTICLE + _CAPTURE + r"\s+(?P<demand>doit-(?:il|elle)\s+être\s+"
        r"(?P<passive>remis(?:e)?|fourni(?:e)?|joint(?:e)?|présenté(?:e)?|effectuée|réalisée|prévue))",
    ]
]


@dataclass(frozen=True, slots=True)
class RcQueryIntent:
    subject: Subject
    demand: Demand
    coverage: Coverage
    scope: RcQueryLot
    anchors: tuple[RcSignalAnchor, ...]
    query_sha256: str


def _subject(text: str) -> Subject:
    text = text.casefold()
    if text.startswith("visite"):
        return (
            "VISIT_MEDICAL"
            if "médical" in text
            else "VISIT_SITE"
            if re.search(r"\b(?:chantier|site|locaux)\b", text)
            else "VISIT"
        )
    if text.startswith("mémoire"):
        return "MEMOIRE_TECHNIQUE"
    if text.startswith("variante"):
        return "VARIANTS"
    if text == "dc1":
        return "DC1"
    return "DC2" if text == "dc2" else "UNKNOWN"


def parse_rc_query_intent(query: str, *, extended_forms: bool = False) -> RcQueryIntent:
    if not query.strip() or len(query) > 2000:
        raise ValueError("invalid candidate query budget")
    scope = parse_query_lot(query)
    found = list(_SUBJECTS.finditer(query))
    anchors = []

    def anchor(signal: str, start: int, end: int) -> RcSignalAnchor:
        return RcSignalAnchor(
            signal, len(query[:start].encode()), len(query[:end].encode()), query[start:end]
        )

    for detected in found:
        anchors.append(anchor("SUBJECT", detected.start(), detected.end()))
    if scope.start_byte is not None and scope.end_byte is not None:
        anchors.append(
            RcSignalAnchor(
                "LOT",
                scope.start_byte,
                scope.end_byte,
                query.encode()[scope.start_byte : scope.end_byte].decode(),
            )
        )
    subject: Subject = _subject(found[0][0]) if len(found) == 1 else "UNKNOWN"

    def result(demand: Demand, coverage: Coverage) -> RcQueryIntent:
        return RcQueryIntent(
            subject,
            demand,
            coverage,
            scope,
            tuple(sorted(anchors, key=lambda a: (a.start_byte, a.end_byte, a.signal))),
            sha256(query.encode()).hexdigest(),
        )

    if len(found) > 1 or re.search(r"\blots?\b", query, re.I) and scope.state == "UNKNOWN":
        return result("UNKNOWN", "AMBIGUOUS")
    unsupported: tuple[tuple[Demand, str], ...] = (
        (
            "DATE_TIME",
            r"\b(?:à\s+quelle\s+heure|quelle\s+heure|quel\s+horaire|quelle\s+date|quand)\b",
        ),
        ("LOCATION", r"\boù\b"),
    )
    for demand, temporal_pattern in unsupported:
        temporal = re.search(temporal_pattern, query, re.I)
        if temporal:
            anchors.append(anchor("DEMAND", temporal.start(), temporal.end()))
            return result(demand, "UNSUPPORTED")
    if not found:
        return result("UNKNOWN", "UNKNOWN")
    offset = 0
    patterns = _PATTERNS
    if extended_forms:
        prefix = re.match(r"\s*pour\s+le\s+lot\s+(?:n[°o]\s*)?[0-9]{1,3}\s*[:,]\s*", query, re.I)
        if prefix is not None and scope.state == "CANDIDATE":
            offset = prefix.end()
        patterns = [
            *patterns,
            re.compile(
                r"\s*"
                + _ARTICLE
                + _DESCRIPTOR
                + _CAPTURE
                + r"\s+(?P<demand>doit-(?:il|elle)\s+être\s+"
                r"(?P<passive>remis(?:e)?|fourni(?:e)?|joint(?:e)?|présenté(?:e)?))" + _SUFFIX,
                re.I,
            ),
        ]
    for pattern in patterns:
        match = pattern.fullmatch(query[offset:])
        if match is None:
            continue
        groups = match.groupdict()
        if groups.get("form") and subject not in {"DC1", "DC2"}:
            continue
        if groups.get("participation") and not subject.startswith("VISIT"):
            continue
        action = groups.get("action") or groups.get("passive")
        if action is not None:
            visit_action = action.casefold() in {
                "effectuer",
                "réaliser",
                "prévoir",
                "effectuée",
                "réalisée",
                "prévue",
            }
            if visit_action != subject.startswith("VISIT"):
                continue
        anchors.append(
            anchor("DEMAND", offset + match.start("demand"), offset + match.end("demand"))
        )
        return result("OBLIGATION", "COVERED")
    return result("UNKNOWN", "UNKNOWN")
