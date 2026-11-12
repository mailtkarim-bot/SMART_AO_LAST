"""Candidate document announcements; lexical mentions never prove presence or absence."""

import re
from dataclasses import dataclass, replace

from app.modules.dce.application.classification import document_family_references

MAX_ANNOUNCEMENT_CHARS = 1_000_000
MAX_ANNOUNCEMENTS = 1000
MAX_ANNOUNCEMENT_EXCERPT = 1000
MAX_ANNOUNCEMENT_LINE_CHARS = 8_000
_CLAUSES = re.compile(r"[^.;!?\n]+(?:[.;!?\n]|$)")
_PROVIDED = re.compile(r"\b(?:joint(?:e|es|s)?|fourni(?:e|es|s)?|annexé(?:e|es|s)?)\b", re.I)
_NOT_PROVIDED = re.compile(
    r"\b(?:n['’]est\s+pas|ne\s+sont\s+pas|non)\s+"
    r"(?:joint(?:e|es|s)?|fourni(?:e|es|s)?|annexé(?:e|es|s)?)\b"
    r"|\b(?:DCE|dossier)\s+ne\s+(?:comprend|comporte|contient)\s+pas\b"
    r"|\b(?:absent(?:e|es|s)?|manquant(?:e|es|s)?)\s+(?:du|au)\s+(?:dossier|DCE)\b",
    re.I,
)
_SUBMISSION = re.compile(
    r"\b(?:(?:doit|doivent|devra|devront)\s+(?:remettre|fournir|joindre|être\s+"
    r"(?:remis(?:e|es)?|fourni(?:e|es|s)?|joint(?:e|es|s)?))"
    r"|à\s+(?:remettre|joindre|fournir))\b",
    re.I,
)
_NOT_REQUIRED = re.compile(
    r"\b(?:n['’]est\s+pas|ne\s+sont\s+pas|non)\s+(?:à\s+)?"
    r"(?:remettre|requis(?:e|es)?|exigé(?:e|es|s)?)\b",
    re.I,
)
_LOT = re.compile(r"\blot\s+(?:n[°o]\s*)?(\d{1,3})(?!\w)", re.I)
_UNCLEAR_LOT = re.compile(r"\blots\b|\blot\s+(?:n[°o]\s*)?\d+\s*(?:ou|et|à|[-–])\s*\d", re.I)

_COMPOSITION = re.compile(
    r"\b(?:DCE|dossier(?:\s+de(?:\s+la)?\s+consultation)?)\s+"
    r"(?:comprend|contient|comporte|est\s+composé\s+(?:de|du|des)|se\s+compose\s+de)\b"
    r"|\bcomposition\s+du\s+(?:DCE|dossier)\b"
    r"|\bpièces\s+constitutives\s+du\s+(?:dossier|DCE)\b",
    re.I,
)
_PROHIBITED = re.compile(r"\b(?:ne\s+pas|interdit\s+de)\s+(?:joindre|remettre|fournir)\b", re.I)
_CONDITIONAL = re.compile(
    r"\b(?:sauf|except[ée]|hors|si|ult[ée]rieurement|selon|option|sera|seront)\b|\bsous\s+r[ée]serve\b|\bsur\s+demande\b",
    re.I,
)
_UNRESOLVED_NEGATION = re.compile(r"\b(?:ne|non|pas|plus|jamais|sans|aucun(?:e)?)\b|\bn['’]", re.I)
_FUTURE_PROVISION = re.compile(r"\b(?:pourra|pourront|pourrait|pourraient|serait|seraient)\b", re.I)
_REFERENCE_RELATION = re.compile(r"\b(?:conform[ée]ment|r[ée]f[ée]rence|renvoi)\b", re.I)

_LIST_PREFIX = re.compile(r"^\s*(?:[-•–]|\d+[.)])\s+")

_OBJECT_GAP = re.compile(
    r"^\s*+(?:(?:le|la|les|un|une|de|du|des|et|documents?|pièces?|suivant(?:e|es|s)?|"
    r"notamment|uniquement|[ld]['’])\s*+)*[:, ]*+\s*+$",
    re.I,
)
_SUBJECT_GAP = re.compile(
    r"^\s*(?:(?:est|sont|a|ont|été|être|sera|seront|pourra|pourront|pourrait|pourraient|"
    r"serait|seraient|n['’]est|n['’]a|ne|pas|plus|jamais|du|de|pour|le|la|les|lot|\d{1,3})\s+)*$",
    re.I,
)
_HEADER_DOCUMENTS = re.compile(
    r"\b(?:DCE|dossier|pièces?|documents?|offre|candidature|composition)\b", re.I
)
_HEADER_PROVISION = re.compile(
    r"\b(?:pièces?|documents?)\s+(?:joint(?:e|es|s)?|fourni(?:e|es|s)?|annexé(?:e|es|s)?)\b", re.I
)
_ROLE_UNCLEAR = re.compile(r"\b(?:offre|candidature|candidat|soumissionnaire)\b", re.I)
_COMPOSITION_LOT = re.compile(r"^\s+pour\s+le\s+lot\s+(?:n[°o]\s*)?\d{1,3}(?!\w)", re.I)
_CONTINUED_CAPTION = re.compile(r"\s*+Composition du dossier\s++[—–-]\s++suite\s*+:?[ \t]*+", re.I)


def _document_composition(text: str) -> bool:
    match = _COMPOSITION.search(text)
    if match is None:
        return False
    tail = text[match.end() :]
    tail = _COMPOSITION_LOT.sub("", tail, count=1)
    references = document_family_references(tail)
    prefix = tail[: references[0][1]] if references else tail
    return _OBJECT_GAP.fullmatch(prefix) is not None


def _linked_reference(
    text: str,
    references: tuple[tuple[str, int, int], ...],
    patterns: tuple[re.Pattern[str], ...],
) -> bool:
    for pattern in patterns:
        for marker in pattern.finditer(text):
            for _, start, end in references:
                if end <= marker.start() and _SUBJECT_GAP.fullmatch(text[end : marker.start()]):
                    return True
                if marker.end() <= start and _OBJECT_GAP.fullmatch(text[marker.end() : start]):
                    return True
    return False


@dataclass(frozen=True, slots=True)
class DocumentAnnouncement:
    document_family: str
    claim: str
    lot_numbers: tuple[int, ...]
    start_byte_offset: int
    end_byte_offset: int
    excerpt: str
    context_start_byte_offset: int | None = None
    context_end_byte_offset: int | None = None
    context_excerpt: str | None = None
    presence_status: str = "UNKNOWN"
    applicability: str = "UNKNOWN"
    criticality: str = "UNKNOWN"


def _claim(
    text: str,
    *,
    allow_provision: bool = True,
    allow_submission: bool = True,
) -> str | None:
    negative = allow_provision and bool(_NOT_PROVIDED.search(text))
    not_required = allow_submission and bool(_NOT_REQUIRED.search(text))
    remainder = _PROHIBITED.sub(" ", _NOT_REQUIRED.sub(" ", _NOT_PROVIDED.sub(" ", text)))
    positive = bool(
        (allow_provision and _PROVIDED.search(_SUBMISSION.sub(" ", remainder)))
        or _document_composition(remainder)
    )
    submission = allow_submission and bool(_SUBMISSION.search(remainder))
    prohibited = allow_submission and bool(_PROHIBITED.search(text))
    claims = [
        state
        for matched, state in (
            (negative, "NOT_PROVIDED_SIGNAL"),
            (not_required, "NOT_REQUIRED_SIGNAL"),
            (positive, "PROVIDED_SIGNAL"),
            (submission, "SUBMISSION_SIGNAL"),
            (prohibited, "PROHIBITED_SUBMISSION_SIGNAL"),
        )
        if matched
    ]
    if positive and _ROLE_UNCLEAR.search(text):
        return "AMBIGUOUS"
    if claims and (
        _CONDITIONAL.search(text)
        or _FUTURE_PROVISION.search(text)
        or _UNRESOLVED_NEGATION.search(remainder)
    ):
        return "AMBIGUOUS"
    return claims[0] if len(claims) == 1 else "AMBIGUOUS" if claims else None


@dataclass(frozen=True, slots=True)
class _Heading:
    claim: str
    excerpt: str
    start: int
    end: int


def _lot_numbers(text: str) -> tuple[int, ...]:
    return (
        ()
        if _UNCLEAR_LOT.search(text)
        else tuple(sorted({int(match.group(1)) for match in _LOT.finditer(text)}))
    )


def _clause_announcements(
    clause: str,
    source_start: int,
    heading: _Heading | None,
) -> tuple[DocumentAnnouncement, ...]:
    references = document_family_references(clause)
    provision = _document_composition(clause) or _linked_reference(
        clause,
        references,
        (_PROVIDED, _NOT_PROVIDED),
    )
    submission = _linked_reference(clause, references, (_SUBMISSION, _NOT_REQUIRED, _PROHIBITED))
    own_claim = _claim(clause, allow_provision=provision, allow_submission=submission)
    if (
        own_claim is None
        and heading
        and references
        and _OBJECT_GAP.fullmatch(clause[: references[0][1]]) is None
    ):
        return ()
    claim = own_claim or (heading.claim if heading else None)
    if claim is None:
        return ()
    if (
        _CONDITIONAL.search(clause)
        or (heading and heading.claim == "AMBIGUOUS")
        or (heading and _UNCLEAR_LOT.search(clause))
        or (own_claim is None and _UNRESOLVED_NEGATION.search(clause))
    ):
        claim = "AMBIGUOUS"
    if heading and (heading.claim, own_claim) in {
        ("PROVIDED_SIGNAL", "NOT_PROVIDED_SIGNAL"),
        ("SUBMISSION_SIGNAL", "NOT_REQUIRED_SIGNAL"),
        ("SUBMISSION_SIGNAL", "PROHIBITED_SUBMISSION_SIGNAL"),
    }:
        claim = "AMBIGUOUS"
    if len({item[0] for item in references}) > 1 and _REFERENCE_RELATION.search(clause):
        claim = "AMBIGUOUS"
    results: list[DocumentAnnouncement] = []
    seen: set[str] = set()
    for family, start, _end in references:
        if family in seen:
            continue
        seen.add(family)
        lower = max(0, start - 250) if len(clause) > MAX_ANNOUNCEMENT_EXCERPT else 0
        upper = min(len(clause), lower + MAX_ANNOUNCEMENT_EXCERPT)
        excerpt = clause[lower:upper]
        bounded_claim = claim if lower == 0 and upper == len(clause) else "AMBIGUOUS"
        lots = _lot_numbers(clause)
        if lots and heading and _lot_numbers(heading.excerpt) not in {(), lots}:
            bounded_claim = "AMBIGUOUS"
        if not lots and heading and not _UNCLEAR_LOT.search(clause):
            lots = _lot_numbers(heading.excerpt)
        if bounded_claim == "AMBIGUOUS":
            lots = ()
        offset = source_start + len(clause[:lower].encode())
        results.append(
            DocumentAnnouncement(
                document_family=family,
                claim=bounded_claim,
                lot_numbers=lots,
                start_byte_offset=offset,
                end_byte_offset=offset + len(excerpt.encode()),
                excerpt=excerpt,
                context_start_byte_offset=heading.start if heading else None,
                context_end_byte_offset=heading.end if heading else None,
                context_excerpt=heading.excerpt if heading else None,
            )
        )
    return tuple(results)


def detect_document_announcements(text: str) -> tuple[DocumentAnnouncement, ...]:
    if len(text) > MAX_ANNOUNCEMENT_CHARS:
        raise ValueError("ANNOUNCEMENT_LIMIT")
    results: list[DocumentAnnouncement] = []
    line_start = 0
    heading = None
    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        if heading and _CONTINUED_CAPTION.fullmatch(line):
            line_start += len(raw_line.encode())
            continue
        if line.strip().startswith("|"):
            cells = list(re.finditer(r"(?<=\|)[^|]+(?=\|)", line))
            # Only a row of complete document names is qualified, never column semantics.
            valid = bool(cells) and line.strip().endswith("|") and len(cells) == line.count("|") - 1
            for cell in cells:
                value = cell.group().strip()
                refs = document_family_references(value)
                valid = valid and len(refs) == 1 and refs[0][1:] == (0, len(value))
            if heading and valid:
                for cell in cells:
                    value = cell.group().strip()
                    start = cell.start() + len(cell.group()) - len(cell.group().lstrip())
                    results.extend(
                        _clause_announcements(
                            value, line_start + len(line[:start].encode()), heading
                        )
                    )
                    if len(results) > MAX_ANNOUNCEMENTS:
                        raise ValueError("ANNOUNCEMENT_LIMIT")
            else:
                heading = None
            line_start += len(raw_line.encode())
            continue
        prefix = _LIST_PREFIX.match(line)
        if prefix is None or not line.strip():
            heading = None
        body_start = prefix.end() if prefix else 0
        body = line[body_start:]
        byte_cursor = line_start + len(line[:body_start].encode())
        last_end = 0
        for segment in _CLAUSES.finditer(body):
            byte_cursor += len(body[last_end : segment.start()].encode())
            raw = segment.group(0)
            clause = raw.rstrip(".;!?\n").strip()
            leading = len(raw) - len(raw.lstrip())
            source_start = byte_cursor + len(raw[:leading].encode())
            results.extend(_clause_announcements(clause, source_start, heading if prefix else None))
            if len(results) > MAX_ANNOUNCEMENTS:
                raise ValueError("ANNOUNCEMENT_LIMIT")
            byte_cursor += len(raw.encode())
            last_end = segment.end()
        header_claim = _claim(
            line,
            allow_provision=bool(
                _HEADER_PROVISION.search(line)
                or _document_composition(line)
                or _NOT_PROVIDED.search(line)
            ),
        )
        if (
            prefix is None
            and line.rstrip().endswith(":")
            and header_claim is not None
            and _HEADER_DOCUMENTS.search(line)
        ):
            header = line.strip()
            offset = line_start + len(line[: len(line) - len(line.lstrip())].encode())
            heading = _Heading(header_claim, header, offset, offset + len(header.encode()))
        line_start += len(raw_line.encode())
    return tuple(results)


def detect_document_announcement_continuation(
    previous_text: str, text: str
) -> tuple[DocumentAnnouncement, ...]:
    """Return only candidates attached to the immediately preceding final heading.

    The caller must independently prove source/extraction/page continuity.
    """
    if len(previous_text) > MAX_ANNOUNCEMENT_CHARS or len(text) > MAX_ANNOUNCEMENT_CHARS:
        raise ValueError("ANNOUNCEMENT_LIMIT")
    lines = previous_text.splitlines(keepends=True)
    if not lines or not text or not _LIST_PREFIX.match(text.splitlines()[0]):
        return ()
    last = lines[-1].rstrip("\r\n")
    if not last.strip() or len(last) > MAX_ANNOUNCEMENT_EXCERPT:
        return ()
    prefix = last + "\n"
    prefix_bytes = len(prefix.encode())
    previous_offset = len(previous_text.encode()) - len(lines[-1].encode())
    return tuple(
        replace(
            item,
            start_byte_offset=item.start_byte_offset - prefix_bytes,
            end_byte_offset=item.end_byte_offset - prefix_bytes,
            context_start_byte_offset=previous_offset + item.context_start_byte_offset,
            context_end_byte_offset=previous_offset + item.context_end_byte_offset,
        )
        for item in detect_document_announcements(prefix + text)
        if item.start_byte_offset >= prefix_bytes
        and item.context_start_byte_offset is not None
        and item.context_end_byte_offset is not None
        and item.context_end_byte_offset < prefix_bytes
    )


MAX_ANNOUNCEMENT_ANCHORS = 64


@dataclass(frozen=True, slots=True)
class AnnouncementRegion:
    fragment_index: int
    start_byte_offset: int
    end_byte_offset: int
    kind: str


@dataclass(frozen=True, slots=True)
class ChainedDocumentAnnouncement:
    announcement: DocumentAnnouncement
    anchors: tuple[AnnouncementRegion, ...]


def detect_document_announcement_sequence(
    texts: tuple[str, ...], joins: tuple[str, ...]
) -> tuple[ChainedDocumentAnnouncement, ...]:
    """Map lexical candidates to original regions of a caller-proven source sequence.

    Empty joins preserve exact same-page chunks; newlines separate proved pages.
    This function does not establish document/extraction/locator continuity.
    """
    if len(joins) != max(0, len(texts) - 1) or any(x not in {"", "\n"} for x in joins):
        raise ValueError("ANNOUNCEMENT_SEQUENCE_INVALID")
    parts: list[str] = []
    spans = []
    cursor = chars = 0
    for index, text in enumerate(texts):
        separator = joins[index - 1] if index else ""
        chars += len(separator) + len(text)
        if chars > MAX_ANNOUNCEMENT_CHARS:
            raise ValueError("ANNOUNCEMENT_LIMIT")
        parts.extend((separator, text))
        cursor += len(separator.encode())
        spans.append((cursor, cursor + len(text.encode())))
        cursor = spans[-1][1]

    def regions(start: int, end: int, kind: str) -> tuple[AnnouncementRegion, ...]:
        return tuple(
            AnnouncementRegion(index, max(start, lower) - lower, min(end, upper) - lower, kind)
            for index, (lower, upper) in enumerate(spans)
            if max(start, lower) < min(end, upper)
        )

    joined = "".join(parts)
    # Joining must not enlarge the previously bounded per-fragment logical line.
    if any(len(line) > MAX_ANNOUNCEMENT_LINE_CHARS for line in joined.splitlines()):
        raise ValueError("ANNOUNCEMENT_LIMIT")
    results = []
    for item in detect_document_announcements(joined):
        anchors: tuple[AnnouncementRegion, ...] = ()
        if item.context_start_byte_offset is not None and item.context_end_byte_offset is not None:
            anchors += regions(
                item.context_start_byte_offset, item.context_end_byte_offset, "HEADING"
            )
            anchors += regions(item.context_end_byte_offset, item.start_byte_offset, "BRIDGE")
        anchors += regions(item.start_byte_offset, item.end_byte_offset, "SOURCE")
        if len(anchors) > MAX_ANNOUNCEMENT_ANCHORS:
            raise ValueError("ANNOUNCEMENT_LIMIT")
        results.append(ChainedDocumentAnnouncement(item, anchors))
    return tuple(results)


def conflicting_announcements(items: tuple[DocumentAnnouncement, ...]) -> frozenset[int]:
    """Flag opposing candidate claims only where their declared lot scopes may overlap."""
    opposing = {
        frozenset({"PROVIDED_SIGNAL", "NOT_PROVIDED_SIGNAL"}),
        frozenset({"SUBMISSION_SIGNAL", "NOT_REQUIRED_SIGNAL"}),
        frozenset({"SUBMISSION_SIGNAL", "PROHIBITED_SUBMISSION_SIGNAL"}),
    }
    conflicts: set[int] = set()
    for index, first in enumerate(items):
        for other_index in range(index + 1, len(items)):
            second = items[other_index]
            if first.document_family != second.document_family:
                continue
            if (
                first.lot_numbers
                and second.lot_numbers
                and not set(first.lot_numbers).intersection(second.lot_numbers)
            ):
                continue
            if frozenset({first.claim, second.claim}) in opposing:
                conflicts.update((index, other_index))
    return frozenset(conflicts)
