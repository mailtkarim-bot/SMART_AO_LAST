"""Read-only, source-bound RC values; candidates never establish applicability."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time
from typing import Literal
from uuid import UUID

CandidateState = Literal["CANDIDATE", "UNKNOWN"]
ValueField = Literal["DOCUMENT", "DATE", "TIME", "TIMEZONE", "LOT"]


@dataclass(frozen=True, slots=True)
class RcValueEvidence:
    field: ValueField
    value: str
    start_byte_offset: int
    end_byte_offset: int


@dataclass(frozen=True, slots=True)
class RcStructuredCandidate:
    projector_version: str = "1"
    state: Literal["UNKNOWN", "CANDIDATES_ONLY", "REVIEW_REQUIRED"] = "UNKNOWN"
    reason_code: str = "UNPROVEN_SOURCE"
    source_fragment_id: UUID | None = None
    documents: tuple[str, ...] = ()
    document_state: CandidateState = "UNKNOWN"
    date_iso: str | None = None
    date_state: CandidateState = "UNKNOWN"
    time_local: str | None = None
    time_state: CandidateState = "UNKNOWN"
    timezone: str | None = None
    timezone_state: CandidateState = "UNKNOWN"
    lot_numbers: tuple[int, ...] = ()
    lot_state: CandidateState = "UNKNOWN"
    applicability: Literal["UNKNOWN"] = "UNKNOWN"
    evidence: tuple[RcValueEvidence, ...] = ()


_CONTEXT = re.compile(
    r"\b(?:ne|non|pas|sans|aucun(?:e)?|jamais|interdit|si|sauf|selon|hors|lorsque|ou|ancien(?:ne)?s?|initiale?|antérieur(?:e)?|annulé(?:e)?|remplacé(?:e)?)\b"
    r"|\bn['’]|\ben\s+cas\b|\bsous\s+(?:réserve|condition)\b|\bà\s+(?:condition|moins\s+que)\b"
    r"|\blots?\s+(?:n[°o]\s*)?[0-9]+\s*(?:ou|à|[-–])\s*[0-9]+",
    re.I,
)
_DOCS = (
    ("DC1", r"\bDC\s?1\b"),
    ("DC2", r"\bDC\s?2\b"),
    ("DC4", r"\bDC\s?4\b"),
    ("DUME", r"\be?DUME\b"),
    ("MEMOIRE_TECHNIQUE", r"\bmémoire\s+technique\b"),
    ("AE", r"\bacte\s+d['’]engagement\b"),
    ("BPU", r"\bBPU\b"),
    ("DPGF", r"\bDPGF\b"),
)
_DOC_PATTERNS = tuple((code, re.compile(pattern, re.I)) for code, pattern in _DOCS)
_NUMERIC_DATE = re.compile(r"\b([0-9]{1,2})([/.-])([0-9]{1,2})\2([0-9]{4})(?!\w)")
_MONTHS = {
    name: i
    for i, name in enumerate(
        (
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ),
        1,
    )
}
_WORD_DATE = re.compile(r"\b([0-9]{1,2})\s+(" + "|".join(_MONTHS) + r")\s+([0-9]{4})(?!\w)", re.I)
_TIME = re.compile(r"(?<![\w:+-])([0-9]{1,2})[h:]([0-9]{2})(?![\w:])", re.I)
_ZONE = re.compile(r"\bUTC(?:[ \t]*[+-][0-9]{2}:[0-9]{2})?(?![\w+\-:])(?![ \t]*[+-])", re.I)
_LOTS = re.compile(r"\blots?\s+(?:n[°o]\s*)?([0-9]{1,3}(?:\s*(?:,|et)\s*[0-9]{1,3})*)(?!\w)", re.I)
_URL = re.compile(r'https?://[^\s<>"«»]+', re.I)
_VALUE_ANCHOR = re.compile(
    r"\b(?:date\s+(?:et\s+heure\s+)?limites?(?:\s+de)?\s+(?:remise|r[ée]ception|d[ée]p[ôo]t)"
    r"|heure\s+limites?|remises\s+au\s+plus\s+tard\s+le|avant\s+le)\b",
    re.I,
)
_GAP_WORDS = frozenset(_MONTHS) | frozenset(
    {
        "de",
        "la",
        "le",
        "les",
        "des",
        "du",
        "offres",
        "plis",
        "candidatures",
        "pour",
        "lot",
        "lots",
        "n",
        "à",
        "au",
        "est",
        "fixée",
        "fixé",
        "prévue",
        "prévu",
        "reportée",
        "reporté",
        "soit",
        "et",
        "heure",
        "heures",
        "h",
        "utc",
        "v",
        "version",
        "indice",
    }
)


def _attached_to_deadline(excerpt: str, value_start: int) -> bool:
    anchors = tuple(_VALUE_ANCHOR.finditer(excerpt, 0, value_start))
    if not anchors:
        return False
    gap = excerpt[anchors[-1].end() : value_start]
    tokens = re.findall(r"[^\W\d_]+|[0-9]+|[^\s]", gap)
    return all(
        token.casefold() in _GAP_WORDS
        or token in ":,./-'’()°+"
        or token.isascii()
        and token.isdecimal()
        for token in tokens
    )


def rc_rectification_is_ambiguous(texts: Iterable[str]) -> bool:
    marked = False
    dates: set[tuple[int, int, int]] = set()
    for text in texts:
        if len(text) > 8000:
            return True
        marked = (
            marked
            or re.search(
                r"\b(?:rectificati(?:f|on)|ancien(?:ne)?|initiale?|annul\w*|rempla\w*)\b",
                text,
                re.I,
            )
            is not None
        )
        for match in _NUMERIC_DATE.finditer(text):
            if _attached_to_deadline(text, match.start()):
                dates.add((int(match[4]), int(match[3]), int(match[1])))
        for match in _WORD_DATE.finditer(text):
            if _attached_to_deadline(text, match.start()):
                dates.add((int(match[3]), _MONTHS[match[2].casefold()], int(match[1])))
    return marked and len(dates) > 1


def project_rc_requirement_values(
    *,
    excerpt: str,
    requirement_type: str,
    directive_signal: str,
    start_byte_offset: int,
    source_fragment_id: UUID,
) -> RcStructuredCandidate:
    """Interpret only a previously verified v5 clause, never a full untrusted corpus."""

    def refused(reason: str) -> RcStructuredCandidate:
        return RcStructuredCandidate(
            state="REVIEW_REQUIRED", reason_code=reason, source_fragment_id=source_fragment_id
        )

    if len(excerpt.encode()) > 1000 or start_byte_offset < 0:
        return refused("SOURCE_LIMIT")
    if _CONTEXT.search(re.sub(r"\bsans\s+obligation\b", "", excerpt, flags=re.I)):
        return refused("CONTEXT_REVIEW_REQUIRED")
    urls = tuple(_URL.finditer(excerpt))

    def outside_url(match: re.Match[str]) -> bool:
        return not any(match.start() < url.end() and url.start() < match.end() for url in urls)

    evidence: list[RcValueEvidence] = []

    def add(field: ValueField, value: str, match: re.Match[str], group: int = 0) -> None:
        start, end = match.span(group)
        evidence.append(
            RcValueEvidence(
                field,
                value,
                start_byte_offset + len(excerpt[:start].encode()),
                start_byte_offset + len(excerpt[:end].encode()),
            )
        )

    if requirement_type in {"CANDIDATURE_DOCUMENT", "OFFER_DOCUMENT"} and directive_signal in {
        "REQUIRED_SIGNAL",
        "OPTIONAL_SIGNAL",
    }:
        for code, pattern in _DOC_PATTERNS:
            for match in pattern.finditer(excerpt):
                if outside_url(match):
                    add("DOCUMENT", code, match)
    date_value = time_value = zone_value = None
    if requirement_type == "SUBMISSION_DEADLINE_SIGNAL":
        dates = [(m, False) for m in _NUMERIC_DATE.finditer(excerpt) if outside_url(m)]
        dates += [(m, True) for m in _WORD_DATE.finditer(excerpt) if outside_url(m)]
        zones = [m for m in _ZONE.finditer(excerpt) if outside_url(m)]
        # A signed second clock must not hide an interval behind a single first match.
        for match in _TIME.finditer(excerpt):
            if outside_url(match) and re.match(
                r"\s*[-–—+]\s*[0-9]{1,2}[h:][0-9]{2}", excerpt[match.end() :], re.I
            ):
                return refused("AMBIGUOUS_VALUES")
        times = [
            m
            for m in _TIME.finditer(excerpt)
            if outside_url(m)
            and not any(m.start() < z.end() and z.start() < m.end() for z in zones)
        ]
        if len(dates) > 1 or len(times) > 1 or len(zones) > 1:
            return refused("AMBIGUOUS_VALUES")
        if any(
            not _attached_to_deadline(excerpt, m.start())
            for m in [m for m, _ in dates] + times + zones
        ):
            return refused("VALUE_RELATION_UNPROVEN")
        try:
            if dates:
                match, word = dates[0]
                if word:
                    value = date(int(match[3]), _MONTHS[match[2].casefold()], int(match[1]))
                else:
                    if (
                        1 <= int(match[1]) <= 12
                        and 1 <= int(match[3]) <= 12
                        and int(match[1]) != int(match[3])
                    ):
                        return refused("AMBIGUOUS_DATE_ORDER")
                    value = date(int(match[4]), int(match[3]), int(match[1]))
                date_value = value.isoformat()
                add("DATE", date_value, match)
            if times:
                match = times[0]
                time_value = time(int(match[1]), int(match[2])).isoformat(timespec="minutes")
                add("TIME", time_value, match)
            if zones:
                match = zones[0]
                zone_value = re.sub(r"\s", "", match.group()).upper()
                if len(zone_value) > 3:
                    time(int(zone_value[4:6]), int(zone_value[7:9]))
                add("TIMEZONE", zone_value, match)
        except ValueError:
            return refused("INVALID_VALUE")
    for match in _LOTS.finditer(excerpt):
        if outside_url(match):
            if re.match(
                r"\s*(?:,|et|à|[-–—/+])\s*(?:le\s+)?(?:lot\s+)?(?:n[°o]\s*)?[0-9]",
                excerpt[match.end() :],
                re.I,
            ):
                return refused("UNPROVEN_LOT_SCOPE")
            for number in re.finditer(r"[0-9]+", match[1]):
                lower = match.start(1) + number.start()
                upper = match.start(1) + number.end()
                lot_number = int(number.group())
                if lot_number == 0:
                    return refused("INVALID_VALUE")
                evidence.append(
                    RcValueEvidence(
                        "LOT",
                        str(lot_number),
                        start_byte_offset + len(excerpt[:lower].encode()),
                        start_byte_offset + len(excerpt[:upper].encode()),
                    )
                )
    if len(evidence) > 64:
        return refused("CANDIDATE_LIMIT")
    evidence.sort(key=lambda e: (e.start_byte_offset, e.field))
    documents = tuple(dict.fromkeys(e.value for e in evidence if e.field == "DOCUMENT"))
    lots = tuple(sorted({int(e.value) for e in evidence if e.field == "LOT"}))
    return RcStructuredCandidate(
        state="CANDIDATES_ONLY" if evidence else "UNKNOWN",
        reason_code="SOURCE_VALUES_CANDIDATE" if evidence else "NO_PROVEN_VALUE",
        source_fragment_id=source_fragment_id,
        documents=documents,
        document_state="CANDIDATE" if documents else "UNKNOWN",
        date_iso=date_value,
        date_state="CANDIDATE" if date_value else "UNKNOWN",
        time_local=time_value,
        time_state="CANDIDATE" if time_value else "UNKNOWN",
        timezone=zone_value,
        timezone_state="CANDIDATE" if zone_value else "UNKNOWN",
        lot_numbers=lots,
        lot_state="CANDIDATE" if lots else "UNKNOWN",
        evidence=tuple(evidence),
    )
