"""Bounded explicit visit kinds; no default site kind or medical applicability."""

import re
from dataclasses import dataclass
from typing import Literal

from app.modules.knowledge.application.rc_recall import obligation_rc_subject

VISIT_QUALIFIER = r"(?:médicale|de\s+chantier|du\s+chantier|de\s+site|du\s+site|des\s+locaux)"
_QUESTION = re.compile(
    r"\s*(?:la|une)\s+(?P<visit>visite\s+" + VISIT_QUALIFIER + r")\s+est-elle\s+"
    r"(?:obligatoire|facultative|exigée|requise|imposée)"
    r"(?:\s+(?:pour\s+le|du|au)\s+lot\s+(?:n[°o]\s*)?[0-9]{1,3})?\s*\?\s*",
    re.I,
)


@dataclass(frozen=True, slots=True)
class RcVisitIntent:
    state: Literal["NONE", "CANDIDATE", "UNKNOWN"] = "NONE"
    subject: str | None = None
    start_byte: int | None = None
    end_byte: int | None = None


def parse_visit_intent(query: str, *, strict: bool = False) -> RcVisitIntent:
    if len(query) > 2000:
        raise ValueError("invalid candidate query budget")
    if not re.search(r"\bvisites?\b", query, re.I):
        return RcVisitIntent()
    medical = bool(re.search(r"\b(?:m[ée]dical\w*|médecin\w*|médecine)\b", query, re.I))
    site = bool(re.search(r"\b(?:chantier|site|locaux)\b", query, re.I))
    if not medical and not site:
        return (
            RcVisitIntent("UNKNOWN")
            if strict and obligation_rc_subject(query) != "VISIT"
            else RcVisitIntent()
        )
    match = _QUESTION.fullmatch(query)
    if not match or medical == site:
        return RcVisitIntent("UNKNOWN")
    return RcVisitIntent(
        "CANDIDATE",
        "VISIT_MEDICAL" if medical else "VISIT_SITE",
        len(query[: match.start("visit")].encode()),
        len(query[: match.end("visit")].encode()),
    )
