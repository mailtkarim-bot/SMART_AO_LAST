"""Bounded RC signals on retrieved text; no applicability or document precedence."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from typing import Literal
from uuid import UUID

from app.modules.knowledge.application.rc_specific_intent import VISIT_QUALIFIER
from app.modules.knowledge.domain.retrieval import DataClassification, RetrievalChunk


@dataclass(frozen=True, slots=True)
class RcSignalAnchor:
    signal: str
    start_byte: int
    end_byte: int
    excerpt: str


@dataclass(frozen=True, slots=True)
class RcClauseEvidence:
    source_fragment_id: UUID
    tenant_id: UUID
    case_id: UUID
    dce_version_id: UUID
    source_sha256: str
    segment_sha256: str
    start_byte: int
    end_byte: int
    excerpt: str
    locator: dict[str, object]
    subject: str
    lot: int | None
    value: str
    kind: Literal["ASSERTION", "NEGATION", "RECTIFICATION", "UNKNOWN"]
    visit_type_proof: RcSignalAnchor | None = None
    directive_signal: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    condition_signals: tuple[RcSignalAnchor, ...] = ()
    directive_anchors: tuple[RcSignalAnchor, ...] = ()


@dataclass(frozen=True, slots=True)
class RcConflictLink:
    left: RcClauseEvidence
    right: RcClauseEvidence
    kind: Literal["OPPOSITION", "RECTIFICATION_OPPOSITION"]
    applicability: Literal["UNKNOWN"] = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class RcConflictProjection:
    clauses: tuple[RcClauseEvidence, ...] = ()
    links: tuple[RcConflictLink, ...] = ()
    unknown_regions: tuple[RcClauseEvidence, ...] = ()


_CUE = re.compile(r"\b(?:visite|mémoire\s+technique|DC1|DC2|DPGF|variantes?|rectificatif)\b", re.I)
_CONDITION = re.compile(
    r"\b(?:si|sauf|lorsque|selon|sous\s+réserve|en\s+cas|à\s+condition|à\s+défaut)\b", re.I
)
_CLAUSE = re.compile(
    r"(?:(?P<rect>rectificatif)\s*:\s*)?"
    r"(?:(?:pour\s+le\s+)?lot\s+(?P<lot>[0-9]{1,3})\s*:\s*)?"
    r"(?P<subject>(?:la|une|aucune)\s+visite|(?:le|un|aucun)\s+(?:mémoire\s+technique|DC1|DC2)|"
    r"(?:la|une|aucune)\s+DPGF|les\s+variantes)\s+"
    r"(?P<predicate>.+?)(?:\s+pour\s+le\s+lot\s+(?P<end_lot>[0-9]{1,3}))?\.",
    re.I,
)
_QUALIFIED_CLAUSE = re.compile(
    _CLAUSE.pattern.replace(r"\s+visite|", r"\s+visite(?:\s+" + VISIT_QUALIFIER + r")?|"), re.I
)
# shortcut: finite grammar, extend with development regressions and new held-out proof.
_REQUIRED = {"est obligatoire", "est exigé", "est exigée", "est requis", "est requise"}
_OPTIONAL = {
    "est facultative",
    "est facultatif",
    "n'est pas obligatoire",
    "n'est pas exigé",
    "n'est pas exigée",
    "n'est pas requis",
    "n'est pas requise",
}
_NONE = {"n'est exigé", "n'est exigée", "n'est requis", "n'est requise"}
_ALLOWED = {"sont autorisées", "sont permises"}
_FORBIDDEN = {"sont interdites", "ne sont pas autorisées", "ne sont pas permises"}


# shortcut: single imperative and explicit lot only; extend on development regressions.
_IMPERATIVE = re.compile(
    r"(?:(?:pour\s+le\s+)?lot\s+(?P<lot>[0-9]{1,3})\s*[:,]\s*)?"
    r"(?P<directive>joindre|fournir|remettre|présenter|effectuer|réaliser)\s+"
    r"(?P<subject>(?:le|un)\s+(?:formulaire\s+)?(?:DC[12]|mémoire\s+technique)|"
    r"(?:la|une)\s+visite(?:\s+" + VISIT_QUALIFIER + r")?)"
    r"(?:\s+pour\s+le\s+lot\s+(?P<end_lot>[0-9]{1,3}))?\.",
    re.I,
)


_CONDITIONAL_IMPERATIVE = re.compile(
    _IMPERATIVE.pattern.replace(r"(?P<lot>", r"(?:n[°o]\s*)?(?P<lot>")
    .replace(r"(?P<end_lot>", r"(?:n[°o]\s*)?(?P<end_lot>")
    .removesuffix(r"\.")
    + r"(?:\s+(?P<condition>(?:si|sauf|lorsque|sous\s+réserve|en\s+cas|à\s+condition)"
    r"\s+[^.!?]+))?\.",
    re.I,
)


def _inside_quotation(text: str) -> bool:
    closing: list[str] = []
    pairs = {"«": "»", "“": "”", "„": "“", "‘": "’", '"': '"'}
    for i, char in enumerate(text):
        if closing and char == closing[-1]:
            apostrophe = (
                char in {"'", "’"}
                and 0 < i < len(text) - 1
                and text[i - 1].isalnum()
                and text[i + 1].isalnum()
            )
            if not apostrophe:
                closing.pop()
        elif char in pairs:
            closing.append(pairs[char])
        elif char == "'" and (i == 0 or not text[i - 1].isalnum()):
            closing.append("'")
    return bool(closing)


def project_rc_conflicts(
    chunks: Sequence[RetrievalChunk],
    *,
    regions: Mapping[UUID, tuple[int, str]] | None = None,
    source_prefixes: Mapping[UUID, str] | None = None,
    qualified_visits: bool = False,
    independent_visit_type: bool = False,
    independent_rc_directive: bool = False,
    source_contexts: Mapping[UUID, str] | None = None,
    imperative_sources: bool = False,
    conditional_imperatives: bool = False,
) -> RcConflictProjection:
    """Only compare exact, unconditioned clauses within identical security/version/lot scope."""
    if len(chunks) > 50:
        raise ValueError("candidate RC budget exceeded")
    if independent_rc_directive and not independent_visit_type:
        raise ValueError("independent source proof required for RC directive")
    if independent_visit_type and not qualified_visits:
        raise ValueError("qualified visit parsing required for type proof")
    if conditional_imperatives and not imperative_sources:
        raise ValueError("imperative source proof required for conditions")
    if imperative_sources and not independent_rc_directive:
        raise ValueError("independent RC directive required for imperatives")
    clauses: list[RcClauseEvidence] = []
    unknown: list[RcClauseEvidence] = []
    seen: set[tuple[UUID, UUID, UUID, UUID, int, int, str]] = set()
    for chunk in chunks:
        if chunk.classification not in {
            DataClassification.PUBLIC,
            DataClassification.INTERNAL_OPERATIONAL,
        }:
            continue
        base, source_hash = (regions or {}).get(
            chunk.chunk_id, (0, sha256(chunk.text.encode()).hexdigest())
        )
        if base < 0 or not re.fullmatch(r"[0-9a-f]{64}", source_hash):
            raise ValueError("invalid RC source region")
        prefix = (source_prefixes or {}).get(chunk.chunk_id, "")
        if source_prefixes is not None and len(prefix.encode()) != base:
            raise ValueError("RC source prefix does not match region")
        if independent_visit_type and base > 0 and source_prefixes is None:
            raise ValueError("source prefix required for independent visit proof")
        whole_context = chunk.text
        if independent_visit_type:
            whole_context = (source_contexts or {}).get(chunk.chunk_id, chunk.text)
            whole_bytes = whole_context.encode()
            if (
                sha256(whole_bytes).hexdigest() != source_hash
                or whole_bytes[base : base + len(chunk.text.encode())] != chunk.text.encode()
                or source_prefixes is not None
                and whole_bytes[:base].decode() != prefix
            ):
                raise ValueError("independent type context does not match source")
        context_condition = independent_visit_type and bool(_CONDITION.search(whole_context))
        for span in re.finditer(r"[^.!?]+[.!?]?", chunk.text):
            excerpt = span[0].strip()
            if not _CUE.search(excerpt):
                continue
            start = span.start() + len(span[0]) - len(span[0].lstrip())
            lower = base + len(chunk.text[:start].encode())
            upper = lower + len(excerpt.encode())
            key = (
                chunk.tenant_id,
                chunk.case_id,
                chunk.dce_version_id,
                chunk.source_fragment_id,
                lower,
                upper,
                source_hash,
            )
            if key in seen:
                continue
            seen.add(key)
            match = (_QUALIFIED_CLAUSE if qualified_visits else _CLAUSE).fullmatch(excerpt)
            context_before = prefix + chunk.text[:start]
            upstream_condition = bool(_CONDITION.search(context_before))
            if base > 0 and span.start() == 0:
                match = None  # An overlapping segment may begin inside an upstream condition.
            if upstream_condition and not independent_visit_type:
                match = None  # No proof that an earlier condition stopped applying.
            if qualified_visits and _inside_quotation(context_before):
                match = None
            type_proof = None
            directive: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
            conditions: tuple[RcSignalAnchor, ...] = ()
            subject, value = "UNKNOWN", "UNKNOWN"
            lot: int | None = None
            kind: Literal["ASSERTION", "NEGATION", "RECTIFICATION", "UNKNOWN"] = "UNKNOWN"
            directive_anchors: tuple[RcSignalAnchor, ...] = ()
            if match:
                subject_text = match["subject"].casefold()
                subject = (
                    "VISIT_MEDICAL"
                    if qualified_visits and "médicale" in subject_text
                    else "VISIT_SITE"
                    if qualified_visits and re.search(r"\b(?:chantier|site|locaux)\b", subject_text)
                    else "VISIT"
                    if "visite" in subject_text
                    else "VARIANTS"
                    if "variantes" in subject_text
                    else "MEMOIRE_TECHNIQUE"
                    if "mémoire" in subject_text
                    else subject_text.split()[-1].upper()
                )
                predicate = " ".join(match["predicate"].casefold().replace("’", "'").split())
                if independent_visit_type and subject in {"VISIT_MEDICAL", "VISIT_SITE"}:
                    type_proof = RcSignalAnchor(
                        subject,
                        lower + len(excerpt[: match.start("subject")].encode()),
                        lower + len(excerpt[: match.end("subject")].encode()),
                        match["subject"],
                    )
                if (
                    independent_rc_directive
                    and subject
                    in {
                        "VISIT",
                        "VISIT_MEDICAL",
                        "VISIT_SITE",
                        "DC1",
                        "DC2",
                        "MEMOIRE_TECHNIQUE",
                        "VARIANTS",
                    }
                ) or (independent_visit_type and subject in {"VISIT_MEDICAL", "VISIT_SITE"}):
                    markers = _REQUIRED | _OPTIONAL | _NONE
                    if independent_rc_directive and subject == "VARIANTS":
                        markers |= _ALLOWED | _FORBIDDEN
                    if predicate in markers or any(
                        predicate.startswith(marker + " ")
                        and _CONDITION.match(predicate[len(marker) :].strip())
                        for marker in markers
                    ):
                        directive = "CANDIDATE"
                    context = whole_context
                    origin = 0
                    signals = list(_CONDITION.finditer(context))
                    if len(signals) > 16:
                        raise ValueError("candidate condition signal budget exceeded")
                    conditions = tuple(
                        RcSignalAnchor(
                            "CONDITION",
                            origin + len(context[: m.start()].encode()),
                            origin + len(context[: m.end()].encode()),
                            m[0],
                        )
                        for m in signals
                    )
                negative_subject = subject_text.startswith(("aucun ", "aucune "))
                if subject == "VARIANTS":
                    value = (
                        "ALLOWED"
                        if predicate in _ALLOWED
                        else "FORBIDDEN"
                        if predicate in _FORBIDDEN
                        else "UNKNOWN"
                    )
                elif negative_subject:
                    value = "NOT_REQUIRED" if predicate in _NONE else "UNKNOWN"
                else:
                    value = (
                        "REQUIRED"
                        if predicate in _REQUIRED
                        else "NOT_REQUIRED"
                        if predicate in _OPTIONAL
                        else "UNKNOWN"
                    )
                lots = [match[k] for k in ("lot", "end_lot") if match[k]]
                if len(lots) == 1 and int(lots[0]) > 0:
                    lot = int(lots[0])
                if context_condition:
                    value = "UNKNOWN"
                if value != "UNKNOWN" and lot is not None:
                    kind = (
                        "RECTIFICATION"
                        if match["rect"]
                        else "NEGATION"
                        if negative_subject or "n'" in predicate or "ne " in predicate
                        else "ASSERTION"
                    )
            imperative = (
                (_CONDITIONAL_IMPERATIVE if conditional_imperatives else _IMPERATIVE).fullmatch(
                    excerpt
                )
                if imperative_sources and match is None
                else None
            )
            if (
                imperative is not None
                and not context_before.strip()  # Earlier preamble applicability is unproved.
                and (
                    not context_condition
                    or conditional_imperatives
                    and imperative["condition"] is not None
                )
                and (
                    not conditional_imperatives
                    or whole_context.strip() == excerpt
                    and len(list(_CUE.finditer(excerpt))) == 1
                    and len(re.findall(r"\blots?\b", excerpt, re.I)) == 1
                )
                and not _inside_quotation(context_before)
                and not (base > 0 and span.start() == 0)
            ):
                lots = [k for k in ("lot", "end_lot") if imperative[k]]
                subject_text = imperative["subject"].casefold()
                visit = "visite" in subject_text
                if (
                    len(lots) == 1
                    and int(imperative[lots[0]]) > 0
                    and (imperative["directive"].casefold() in {"effectuer", "réaliser"}) == visit
                    and not (visit and "formulaire" in subject_text)
                ):
                    subject = (
                        "VISIT_MEDICAL"
                        if "médicale" in subject_text
                        else "VISIT_SITE"
                        if visit and re.search(r"\b(?:chantier|site|locaux)\b", subject_text)
                        else "VISIT"
                        if visit
                        else "MEMOIRE_TECHNIQUE"
                        if "mémoire" in subject_text
                        else subject_text.split()[-1].upper()
                    )
                    lot = int(imperative[lots[0]])
                    value, kind, directive = "REQUIRED", "ASSERTION", "CANDIDATE"
                    if conditional_imperatives and imperative["condition"] is not None:
                        value, kind = "UNKNOWN", "UNKNOWN"
                        conditions = (
                            RcSignalAnchor(
                                "CONDITION",
                                lower + len(excerpt[: imperative.start("condition")].encode()),
                                lower + len(excerpt[: imperative.end("condition")].encode()),
                                imperative["condition"],
                            ),
                        )
                    directive_anchors = tuple(
                        RcSignalAnchor(
                            signal,
                            lower + len(excerpt[: imperative.start(group)].encode()),
                            lower + len(excerpt[: imperative.end(group)].encode()),
                            imperative[group],
                        )
                        for signal, group in (
                            ("SUBJECT", "subject"),
                            ("DIRECTIVE", "directive"),
                            ("LOT", lots[0]),
                        )
                    )
                    if subject in {"VISIT_MEDICAL", "VISIT_SITE"}:
                        a = directive_anchors[0]
                        type_proof = RcSignalAnchor(subject, a.start_byte, a.end_byte, a.excerpt)
            item = RcClauseEvidence(
                chunk.source_fragment_id,
                chunk.tenant_id,
                chunk.case_id,
                chunk.dce_version_id,
                source_hash,
                sha256(chunk.text.encode()).hexdigest(),
                lower,
                upper,
                excerpt,
                deepcopy(chunk.locator),
                subject,
                lot,
                value,
                kind,
                type_proof,
                directive,
                conditions,
                directive_anchors,
            )
            (unknown if kind == "UNKNOWN" else clauses).append(item)
            if len(clauses) + len(unknown) > 256:
                raise ValueError("candidate RC clause budget exceeded")
    links: list[RcConflictLink] = []
    for i, left in enumerate(clauses):
        for right in clauses[i + 1 :]:
            if (left.tenant_id, left.case_id, left.dce_version_id, left.subject, left.lot) != (
                right.tenant_id,
                right.case_id,
                right.dce_version_id,
                right.subject,
                right.lot,
            ) or left.value == right.value:
                continue
            if (
                left.source_fragment_id == right.source_fragment_id
                and left.source_sha256 != right.source_sha256
            ):
                continue
            links.append(
                RcConflictLink(
                    left,
                    right,
                    "RECTIFICATION_OPPOSITION"
                    if "RECTIFICATION" in (left.kind, right.kind)
                    else "OPPOSITION",
                )
            )
    return RcConflictProjection(tuple(clauses), tuple(links), tuple(unknown))
