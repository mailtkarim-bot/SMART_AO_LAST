"""Bounded literal comparison of known RC signals; never an admission decision."""

import re
import unicodedata
from uuid import UUID

from app.modules.submission.public.final_control_contracts import BuyerFileComparison

_CANDIDATE = re.compile(
    r"format|\bpdf\b|\bdocx\b|\bpng\b|\bzip\b|archive|individuell|profil|plateforme"
)
_FORMAT = re.compile(r"le memoire technique doit etre remis au format (pdf|docx|png)")
_KBIS = re.compile(r"(?:le kbis|l'extrait kbis) doit etre fourni au format (pdf|docx|png)")
_MIME = {
    "PDF": "application/pdf",
    "DOCX": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "PNG": "image/png",
}
_MODES = {
    "le pli doit etre remis sous forme d'une archive zip": "ZIP",
    "les archives zip sont interdites": "NO_ZIP",
    "les fichiers doivent etre deposes individuellement, sans archive": "INDIVIDUAL_FILES",
    "les fichiers doivent etre deposes individuellement": "INDIVIDUAL_FILES",
}


def _normalized(text):
    value = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return " ".join(value.lower().replace("’", "'").split())


def _source_issue(row, dce_version_id, source_state):
    if source_state != "CURRENT" or row.source_state != "CURRENT_SOURCE":
        return "SOURCE_NOT_CURRENT"
    if row.confirmation != "CONFIRMED":
        return "SOURCE_NOT_CONFIRMED"
    if row.document_family != "RC":
        return "UNSUPPORTED_SOURCE_FAMILY"
    if row.lot_candidates:
        return "LOT_SCOPE_UNKNOWN"
    anchor = row.source_anchor
    if (
        not isinstance(anchor, dict)
        or str(anchor.get("dce_version_id")) != str(dce_version_id)
        or not row.source_locator.strip()
    ):
        return "SOURCE_ANCHOR_UNKNOWN"
    if not all(
        isinstance(anchor.get(key), str) and re.fullmatch(r"[a-f0-9]{64}", anchor[key])
        for key in ["source_sha256", "fragment_sha256"]
    ):
        return "SOURCE_ANCHOR_UNKNOWN"
    try:
        for key in ["dce_document_id", "extraction_id"]:
            UUID(str(anchor.get(key)))
    except ValueError:
        return "SOURCE_ANCHOR_UNKNOWN"
    return None


def compare_buyer_files(*, files, requirements, dce_version_id, source_state):
    rows = []
    uncertain_scopes: set[str] = set()
    for row in requirements:
        excerpt = row.source_excerpt or ""
        text = _normalized(excerpt)
        if text.startswith("format de fichier : "):
            text = text[len("format de fichier : ") :]
        # A complete name-only instruction does not impose a MIME format via its extension.
        if re.fullmatch(
            r"(?:le memoire technique|le kbis) doit etre nomme "
            r'(?:«[^«»\r\n]{1,255}»|"[^"\r\n]{1,255}")\.?',
            text,
        ):
            continue
        if not _CANDIDATE.search(text):
            continue
        scope = "UNSPECIFIED"
        requested = "UNKNOWN"
        reason = "UNSUPPORTED_OR_AMBIGUOUS_SIGNAL"
        state = "UNKNOWN"
        target = []
        if len(text) > 2000 or "…" in excerpt or "..." in excerpt:
            reason = "TRUNCATED_OR_LIMITED_SOURCE"
        else:
            text = text.removesuffix(".")
            if text.startswith("format de fichier : "):
                text = text[len("format de fichier : ") :]
            technical = _FORMAT.fullmatch(text)
            kbis = _KBIS.fullmatch(text)
            selected = technical if technical is not None else kbis
            generic = re.fullmatch(r"le format (pdf|docx|png) est obligatoire", text)
            if selected is not None:
                scope = "TECHNICAL_RESPONSE" if technical else "KBIS"
                requested = selected.group(1).upper()
                target = [f for f in files if f.document_kind == scope]
                reason = _source_issue(row, dce_version_id, source_state)
                if reason is None:
                    if not target and any(f.document_kind == "UNKNOWN" for f in files):
                        reason = "TARGET_SCOPE_UNKNOWN"
                    elif not target:
                        state = "OBSERVED_MISMATCH"
                        reason = "TARGET_FILE_MISSING"
                    elif any(
                        f.presence != "VERIFIED_SOURCE" or f.media_type is None for f in target
                    ):
                        reason = "OBSERVED_FILE_UNKNOWN"
                    else:
                        state = (
                            "OBSERVED_MATCH"
                            if all(f.media_type == _MIME[requested] for f in target)
                            else "OBSERVED_MISMATCH"
                        )
                        reason = "MIME_EQUAL" if state == "OBSERVED_MATCH" else "MIME_DIFFERS"
            elif text in _MODES:
                scope = "DELIVERY"
                requested = _MODES[text]
                reason = _source_issue(row, dce_version_id, source_state)
                if reason is None:
                    state = "OBSERVED_MATCH" if requested == "ZIP" else "OBSERVED_MISMATCH"
                    reason = "LOCAL_ZIP_ONLY" if requested == "ZIP" else "LOCAL_ZIP_DIFFERS"
            elif "profil" in text or "plateforme" in text:
                reason = "EXTERNAL_CHANNEL_NOT_VERIFIED"
            elif generic is not None:
                requested = generic.group(1).upper()
                reason = "TARGET_SCOPE_UNKNOWN"
        if state == "UNKNOWN" and _source_issue(row, dce_version_id, source_state) is None:
            # An unparsed current instruction on the same subject prevents a reassuring match.
            if re.search(r"\bmemoire technique\b", text):
                uncertain_scopes.add("TECHNICAL_RESPONSE")
            if re.search(r"\bkbis\b", text):
                uncertain_scopes.add("KBIS")
            if re.search(r"\bzip\b|archive|individuell", text):
                uncertain_scopes.add("DELIVERY")
        rows.append(
            BuyerFileComparison(
                requirement_id=row.requirement_id,
                source_excerpt=row.source_excerpt,
                source_locator=row.source_locator,
                source_anchor=row.source_anchor,
                confirmation=row.confirmation,
                scope=scope,
                requested=requested,
                files=target,
                state=state,
                reason_code=reason,
            )
        )
    demands: dict[str, set[str]] = {}
    for row in rows:
        if row.state == "UNKNOWN":
            continue
        wanted = "NON_ARCHIVE" if row.requested in {"NO_ZIP", "INDIVIDUAL_FILES"} else row.requested
        demands.setdefault(row.scope, set()).add(wanted)
    for row in rows:
        if row.scope in uncertain_scopes and row.state != "UNKNOWN":
            row.state = "UNKNOWN"
            row.reason_code = "UNRESOLVED_SCOPED_SOURCE"
        if len(demands.get(row.scope, set())) > 1:
            row.state = "UNKNOWN"
            row.reason_code = "CONFLICTING_SOURCE_REQUIREMENTS"
    return rows
