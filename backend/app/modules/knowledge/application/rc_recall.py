"""Finite generic RC query grammar for an unwired lexical recall supplement."""

import re


def generic_rc_subject(query: str) -> str | None:
    if len(query) > 2000:
        return None
    text = " ".join(query.split()).casefold()
    # shortcut: finite question forms, extend on development cases with fresh held-out proof.
    if re.fullmatch(
        r"(?:quelles obligations de visite sont prévues|"
        r"quelles sont les obligations de visite)\s*\?",
        text,
    ):
        return "VISIT"
    match = re.fullmatch(
        r"(?:la|le|les|une)\s+(visite|mémoire technique|dc1|dc2|variantes)\s+"
        r"(?:est-elle|est-il|sont-elles)\s+"
        r"(?:obligatoire|obligatoires|exigée|exigé|requise|requis|facultative|facultatif|"
        r"imposée|autorisées|permises|interdites)\s*\?",
        text,
    )
    if not match:
        return None
    return {
        "visite": "VISIT",
        "mémoire technique": "MEMOIRE_TECHNIQUE",
        "variantes": "VARIANTS",
    }.get(match[1], match[1].upper())


def obligation_rc_subject(query: str) -> str | None:
    """Finite obligation query, including its explicit lot suffix; no applicability."""
    text = re.sub(
        r"\s+(?:pour\s+le|du|au)\s+lot\s+(?:n[°o]\s*)?[0-9]{1,3}(?=\s*\?\s*$)",
        "",
        query,
        flags=re.I,
    )
    subject = generic_rc_subject(text)
    if subject is None and re.search(
        r"\b(?:DC1|DC2|variantes?|mémoire\s+technique)\b", query, re.I
    ):
        return "UNKNOWN"
    return subject
