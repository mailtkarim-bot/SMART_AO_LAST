"""Versioned local query interpretation; no source reading or business conclusion."""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256

from app.modules.knowledge.application.rc_candidate_conflicts import RcSignalAnchor
from app.modules.knowledge.application.rc_query_intent import (
    Coverage,
    Demand,
    RcQueryIntent,
    Subject,
)
from app.modules.knowledge.application.rc_query_scope import RcQueryLot
from app.modules.knowledge.application.retrieval import _FINANCIAL_QUERY_PATTERN

_SUBJECT = re.compile(
    r"\b(?:DC[12]|mémoire\s+technique|variantes?|visites?(?:\s+(?:(?:de|du|des)\s+(?!lot\b)[\w-]+|médicales?|(?!(?:de|du|des|est|sont|pour|au|dans|doit|serait|obligatoire|facultative)\b)[\w-]+))?)\b",
    re.I,
)
_LOT = re.compile(r"\blot\s+(?:n[°o]\s*)?([+-]?[0-9]+)(?!\w)", re.I)
# shortcut: finite lexical relations; new families require development proof and a new version.
_ACTION = r"(?:annexer|produire|joindre|fournir|remettre|présenter|effectuer|réaliser)"
_DEMAND = re.compile(
    r"\b(?:peut-on|est-il\s+permis\s+de)\s+ne\s+pas\s+(?:(?:le|la|les)\s+)?"
    + _ACTION
    + r"|\b(?:est-il|serait-il)\s+(?:nécessaire|indispensable|obligatoire)\s+de\s+"
    + _ACTION
    + r"|\bn['’]est-il\s+pas\s+nécessaire\s+de\s+"
    + _ACTION
    + r"|\b(?:faut-il|doit-on)\s+(?:impérativement\s+)?"
    + _ACTION
    + r"|\bpeut-on\s+(?:se|s['’]en)\s*dispenser"
    + r"|\bobligation\s+de\s+"
    + _ACTION
    + r"|\btenu\s+de\s+"
    + _ACTION
    + r"|\bà\s+produire"
    + r"|\b(?:impératives?|indispensables?|imposé(?:e)?s?|recevables?|admises?|"
    r"optionnelles?|nécessaires?|incontournables?|obligatoires?|facultati(?:f|ve)s?|"
    r"requis(?:es?)?|exigé(?:e)?s?|autorisées?|permises?|interdites?)\b",
    re.I,
)
_TIME = re.compile(r"\b(?:à\s+quelle\s+(?:heure|date)|quel\s+horaire|quand)\b", re.I)
_PLACE = re.compile(r"\b(?:où|lieu)\b", re.I)
_CONDITION = re.compile(r"\b(?:si|sauf|lorsque|sous\s+réserve|en\s+cas|à\s+condition)\b", re.I)
_INVERSION = re.compile(
    r"\b(?:est|sont|serait|constitue|existe)-(?:il|elle|elles|ils|t-il)\b", re.I
)


@dataclass(frozen=True, slots=True)
class RcIntentRecognition:
    intent: RcQueryIntent | None
    reason: str
    mechanism: str = "rc-compositional-v2"
    anchor_convention: str = "lexical-cue-v2"


def recognize_rc_intent(query: str) -> RcIntentRecognition:
    if not isinstance(query, str) or not query.strip() or len(query) > 2000:
        return RcIntentRecognition(None, "INVALID_QUERY_BUDGET")
    if _FINANCIAL_QUERY_PATTERN.search(query):
        return RcIntentRecognition(None, "FINANCIAL_SCOPE_REFUSED")
    subjects = list(_SUBJECT.finditer(query))
    lots = list(_LOT.finditer(query))
    scope = RcQueryLot()
    anchors: list[RcSignalAnchor] = []

    def anchor(signal: str, m: re.Match[str]) -> RcSignalAnchor:
        return RcSignalAnchor(
            signal, len(query[: m.start()].encode()), len(query[: m.end()].encode()), m[0]
        )

    for m in subjects:
        anchors.append(anchor("SUBJECT", m))
    subject: Subject = "UNKNOWN"
    if len(subjects) == 1:
        text = subjects[0][0].casefold()
        if text in {"dc1", "dc2"}:
            subject = "DC1" if text == "dc1" else "DC2"
        elif text.startswith("mémoire"):
            subject = "MEMOIRE_TECHNIQUE"
        elif text.startswith("variante"):
            subject = "VARIANTS"
        elif re.fullmatch(r"visites?\s+médicales?", text):
            subject = "VISIT_MEDICAL"
        elif re.fullmatch(r"visites?\s+(?:de|du|des)\s+(?:chantier|site|locaux)", text):
            subject = "VISIT_SITE"
        elif re.fullmatch(r"visites?", text):
            subject = "VISIT"
    invalid_lot = any(
        m[1].startswith(("+", "-"))
        or not 1 <= int(m[1]) <= 999
        or re.match(r"(?:[.,]\s*[0-9]|[-/][\w]|\s+(?:bis|ter|quater)\b)", query[m.end() :], re.I)
        for m in lots
    )
    lot_mentions = len(re.findall(r"\blots?\b", query, re.I))
    multiple_lots = (
        len(lots) > 1
        or lot_mentions > 1
        or bool(
            lots
            and re.match(
                r"\s*(?:ou|et|à|[-/])\s*(?:le\s+)?(?:lot\s+)?[0-9]", query[lots[0].end() :], re.I
            )
        )
    )
    if len(lots) == lot_mentions == 1 and not invalid_lot and not multiple_lots:
        a = anchor("LOT", lots[0])
        anchors.append(a)
        scope = RcQueryLot("CANDIDATE", int(lots[0][1]), a.start_byte, a.end_byte)

    def result(demand: Demand, coverage: Coverage, reason: str) -> RcIntentRecognition:
        return RcIntentRecognition(
            RcQueryIntent(
                subject,
                demand,
                coverage,
                scope,
                tuple(sorted(anchors, key=lambda a: (a.start_byte, a.end_byte, a.signal))),
                sha256(query.encode()).hexdigest(),
            ),
            reason,
        )

    if query.rstrip().endswith(("…", "...")) or re.search(
        r"\b(?:si|sauf|et|ou)\s*[?]?\s*$|\b(?:si|lorsque)\s+(?:le|la|un|une|les|des)(?:\s+[\w-]+)?\s*[?]?\s*$",
        query,
        re.I,
    ):
        return result("UNKNOWN", "UNKNOWN", "TRUNCATED")
    if invalid_lot or multiple_lots or lot_mentions and not lots:
        anchors[:] = [a for a in anchors if a.signal != "LOT"]
        scope = RcQueryLot()
        return result(
            "UNKNOWN",
            "AMBIGUOUS",
            "INVALID_LOT"
            if invalid_lot or lot_mentions and not lots and not re.search(r"\blots\b", query, re.I)
            else "MULTIPLE_LOTS",
        )
    if len(subjects) > 1:
        return result("UNKNOWN", "AMBIGUOUS", "MULTIPLE_SUBJECTS")
    times, places, demands = (
        list(_TIME.finditer(query)),
        list(_PLACE.finditer(query)),
        list(_DEMAND.finditer(query)),
    )
    places = [
        p
        for p in places
        if p[0].casefold() == "où"
        or re.search(r"\bquel(?:\s+est\s+le)?\s+$", query[: p.start()], re.I)
    ]
    coordinated_request = re.search(
        r"(?:[,;]|\b(?:et|ou))\s+(?:est-elle|est-il|est-ce|doit-on|faut-il|peut-on|à\s+quelle|quand|où)\b",
        query,
        re.I,
    )
    interrogatives = re.findall(
        r"\b(?:faut-il|doit-on|peut-on|est-il|est-elle|est-ce|serait-il|serait-elle)\b", query, re.I
    )
    if bool(times and places) or bool(
        (times or places) and demands and (coordinated_request or len(interrogatives) > 1)
    ):
        return result("UNKNOWN", "AMBIGUOUS", "MULTIPLE_DEMANDS")
    if re.search(
        r'[;«»“”"]|\b(?:mot|terme|expliquez|ignore|réponds|signifie|exemple|comparaison|contrairement)\b',
        query,
        re.I,
    ) or not query.rstrip().endswith("?"):
        return result("UNKNOWN", "UNKNOWN", "NON_ACTIVE_REQUEST")
    if not subjects:
        reason = (
            "UNRESOLVED_REFERENCE"
            if re.search(
                r"\b(?:même|ce\s+(?:document|formulaire)|celui|celle|ils?|elles?)\b|\b(?:le|la|les)\s+"
                + _ACTION,
                query,
                re.I,
            )
            else "UNKNOWN_SUBJECT"
        )
        return result("UNKNOWN", "UNKNOWN", reason)
    if subject == "UNKNOWN":
        return result("UNKNOWN", "UNKNOWN", "UNKNOWN_SUBJECT")
    if times or places:
        anchors.append(anchor("DEMAND", (times or places)[0]))
        return result(
            "DATE_TIME" if times else "LOCATION",
            "UNSUPPORTED",
            "UNSUPPORTED_TIME" if times else "UNSUPPORTED_LOCATION",
        )
    condition_question = re.search(
        r"\b(?:(?:à|sous)\s+quelles\s+conditions|dans\s+quels\s+cas)\b", query, re.I
    )
    if condition_question:
        anchors.append(anchor("DEMAND", condition_question))
        return result("OBLIGATION", "UNSUPPORTED", "UNSUPPORTED_CONDITION")
    if not demands:
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    # Adjectival status must be linked to an interrogative predicate, not just co-occur.
    m = demands[0]
    local_pronoun = re.search(r"\bne\s+pas\s+(le|la|les)\s+", m[0], re.I)
    if local_pronoun:
        expected_pronoun = (
            "la"
            if subject.startswith("VISIT")
            else "les"
            if subject == "VARIANTS" and subjects[0][0].casefold().endswith("s")
            else "la"
            if subject == "VARIANTS"
            else "le"
        )
        if subjects[0].end() > m.start() or local_pronoun[1].casefold() != expected_pronoun:
            return result("UNKNOWN", "UNKNOWN", "UNRESOLVED_REFERENCE")
    if not _INVERSION.search(query) and not re.search(
        r"^(?:est-il|serait-il|faut-il|doit-on|peut-on|tenu|n[\'’]est-il)", m[0], re.I
    ):
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    if query.count("?") != 1 or re.search(r"\b(?:pourquoi|comment|combien)\b", query, re.I):
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    if len(list(_INVERSION.finditer(query))) > 1:
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    if not re.search(
        r"^(?:est-il|serait-il|faut-il|doit-on|peut-on|tenu|n['’]est-il|obligation|à\s+produire)",
        m[0],
        re.I,
    ) and not re.search(
        r"\b(?:est|sont|serait|constitue)-(?:il|elle|elles|ils|t-il)\s+(?:(?:une?\s+)?(?:pièce|document)\s+)?$",
        query[: m.start()],
        re.I,
    ):
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    if re.search(r"\b(?:et|ou)\b", query, re.I):
        return result("UNKNOWN", "AMBIGUOUS", "MULTIPLE_DEMANDS")
    prefix = query[: subjects[0].start()]
    # A complete leading condition is identified, never assumed satisfied.
    if _CONDITION.match(query.lstrip()) and "," in prefix and prefix.index(",") < m.start():
        prefix = prefix[prefix.index(",") + 1 :]
    # A document mentioned inside another nominal head is not the requested subject.
    prefix = re.sub(
        r"(?:pour\s+le|dans\s+le\s+dossier\s+du|dans\s+le\s+cadre\s+du|du|au)?\s*"
        + _LOT.pattern
        + r"\s*[,—:]?",
        " ",
        prefix,
        flags=re.I,
    )
    if m.end() <= subjects[0].start():
        prefix = prefix.replace(m[0], " ", 1)
    head = re.fullmatch(
        r"\s*[,—:]*\s*(?:(?:est-on|existe-t-il\s+une)\s+)?(?:de\s+)?"
        r"(?:(?:le|la|un|une|les|des|du|de)\s+)?(?:(?:formulaire|remise\s+du)\s+)?",
        prefix,
        re.I,
    )
    declared_formality = subject.startswith("VISIT") and re.fullmatch(
        r"\s*cette\s+formalité\s+est-elle\s*:\s*", prefix, re.I
    )
    if head is None and not declared_formality:
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    anchors.append(anchor("DEMAND", m))
    if _CONDITION.search(query):
        return result("OBLIGATION", "UNSUPPORTED", "UNSUPPORTED_CONDITION")
    action = re.search(_ACTION, m[0], re.I)
    if action and (action[0].casefold() in {"effectuer", "réaliser"}) != subject.startswith(
        "VISIT"
    ):
        anchors.remove(anchor("DEMAND", m))
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    residual = list(query)
    for start, end in (
        [(s.start(), s.end()) for s in subjects]
        + [(m.start(), m.end())]
        + [(lot.start(), lot.end()) for lot in lots]
    ):
        residual[start:end] = " " * (end - start)
    # Only declared grammatical connectors may remain; unknown objects/types are not discarded.
    allowed = set(
        [
            "la",
            "le",
            "les",
            "une",
            "un",
            "des",
            "du",
            "de",
            "à",
            "au",
            "aux",
            "pour",
            "dans",
            "notre",
            "nos",
            "dossier",
            "pli",
            "cadre",
            "est-il",
            "est-elle",
            "sont-ils",
            "sont-elles",
            "serait-elle",
            "serait-il",
            "existe-t-il",
            "constitue-t-il",
            "cette",
            "formalité",
            "est-on",
            "chacun",
        ]
    )
    allowed |= (
        {"libre"}
        if subject == "VARIANTS"
        else {"prévue"}
        if subject.startswith("VISIT")
        else {"remise", "formulaire", "pièce", "document"}
    )
    if any(
        word.casefold() not in allowed
        for word in re.findall(r"[\w]+(?:-[\w]+)*", "".join(residual))
    ):
        anchors.remove(anchor("DEMAND", m))
        return result("UNKNOWN", "UNKNOWN", "INSUFFICIENT_EVIDENCE")
    return result("OBLIGATION", "COVERED", "UNIQUE_EXPLICIT_REQUEST")
