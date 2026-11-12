"""Literal RC name/size observations for known documentary files, never conformity."""

import re
from pathlib import PurePosixPath

from app.modules.submission.application.buyer_file_comparison import _normalized, _source_issue
from app.modules.submission.public.final_control_contracts import BuyerNameSizeComparison

_SUBJECTS = {"le memoire technique": "TECHNICAL_RESPONSE", "le kbis": "KBIS"}
_SIZE = re.compile(
    r"la taille (du memoire technique|du kbis|de chaque fichier) ne doit pas depasser "
    r"([0-9]{1,15}) (octets?|mio)"
)
_CANDIDATE = re.compile(r"\btaille\b|\bnoms?\b|\bnomm[eé]|\boctets?\b|\bmio\b|\bmo\b")


def compare_buyer_names_sizes(*, files, requirements, dce_version_id, source_state):
    rows = []
    uncertain: set[tuple[str, str]] = set()
    for source in requirements:
        quote = source.source_excerpt or ""
        normalized = _normalized(quote)
        if not _CANDIDATE.search(normalized):
            continue
        scope = "UNSPECIFIED"
        criterion = "UNKNOWN"
        requested_name = None
        max_bytes = None
        reason = "UNSUPPORTED_OR_AMBIGUOUS_SIGNAL"
        state = "UNKNOWN"
        targets = []
        truncated = len(quote) > 2000 or "…" in quote or "..." in quote
        if truncated:
            reason = "TRUNCATED_OR_LIMITED_SOURCE"
        else:
            text = normalized.removesuffix(".").removeprefix("format de fichier : ")
            # Never normalize the captured name: case, accents and spaces are exact data.
            name = re.fullmatch(
                r'(.+?) doit (?:être|etre) nommé (?:«([^«»\r\n]{1,255})»|"([^"\r\n]{1,255})")\.?',
                re.sub(r"^format de fichier\s*:\s*", "", quote.strip(), flags=re.IGNORECASE),
                re.IGNORECASE,
            )
            size = _SIZE.fullmatch(text.removeprefix("format de fichier : "))
            if name and _normalized(name.group(1)) in _SUBJECTS:
                scope = _SUBJECTS[_normalized(name.group(1))]
                criterion = "EXACT_NAME"
                requested_name = name.group(2) if name.group(2) is not None else name.group(3)
                if (
                    requested_name in {".", ".."}
                    or any(c in requested_name for c in "/\\*?")
                    or any(ord(c) < 32 for c in requested_name)
                ):
                    criterion = "UNKNOWN"
                    reason = "NAME_PATH_OR_PATTERN_UNKNOWN"
            elif size:
                scope = {
                    "du memoire technique": "TECHNICAL_RESPONSE",
                    "du kbis": "KBIS",
                    "de chaque fichier": "KNOWN_DOCUMENT_FILES",
                }[size.group(1)]
                criterion = "MAX_BYTES"
                max_bytes = int(size.group(2)) * (1048576 if size.group(3) == "mio" else 1)
                if max_bytes > 9007199254740991:
                    criterion, max_bytes, reason = "UNKNOWN", None, "SIZE_LIMIT_UNKNOWN"
            elif text == "les noms des fichiers ne doivent pas contenir d'espaces":
                scope, criterion = "KNOWN_DOCUMENT_FILES", "NO_WHITESPACE"
            elif re.search(r"\b(?:mo|ko)\b", text):
                reason = "SIZE_UNIT_UNKNOWN"
            if criterion != "UNKNOWN":
                targets = (
                    list(files)
                    if scope == "KNOWN_DOCUMENT_FILES"
                    else [f for f in files if f.document_kind == scope]
                )
                reason = _source_issue(source, dce_version_id, source_state)
                if reason is None:
                    if not targets and any(f.document_kind == "UNKNOWN" for f in files):
                        reason = "TARGET_SCOPE_UNKNOWN"
                    elif not targets:
                        state, reason = "OBSERVED_MISMATCH", "TARGET_FILE_MISSING"
                    elif any(f.presence != "VERIFIED_SOURCE" for f in targets) or (
                        criterion == "MAX_BYTES" and any(f.byte_size is None for f in targets)
                    ):
                        reason = "OBSERVED_FILE_UNKNOWN"
                    else:
                        names = [PurePosixPath(f.archive_path).name for f in targets]
                        if criterion == "EXACT_NAME":
                            match = all(n == requested_name for n in names)
                            reason = "NAME_EQUAL" if match else "NAME_DIFFERS"
                        elif criterion == "NO_WHITESPACE":
                            match = all(not any(c.isspace() for c in n) for n in names)
                            reason = "NO_WHITESPACE" if match else "WHITESPACE_FOUND"
                        else:
                            match = all(f.byte_size <= max_bytes for f in targets)
                            reason = "SIZE_WITHIN_LIMIT" if match else "SIZE_EXCEEDS_LIMIT"
                        state = "OBSERVED_MATCH" if match else "OBSERVED_MISMATCH"
        if state == "UNKNOWN" and _source_issue(source, dce_version_id, source_state) is None:
            scopes = []
            if "memoire technique" in normalized:
                scopes.append("TECHNICAL_RESPONSE")
            if re.search(r"\bkbis\b", normalized):
                scopes.append("KBIS")
            if not scopes:
                scopes.append("KNOWN_DOCUMENT_FILES")
            kinds = []
            if "taille" in normalized or re.search(r"\b(?:octets?|mo|mio|ko)\b", normalized):
                kinds.append("SIZE")
            if re.search(r"\bnom", normalized):
                kinds.append("NAME")
            uncertain.update((s, k) for s in scopes for k in kinds)
        rows.append(
            BuyerNameSizeComparison(
                requirement_id=source.requirement_id,
                source_excerpt=source.source_excerpt,
                source_locator=source.source_locator,
                source_anchor=source.source_anchor,
                confirmation=source.confirmation,
                scope=scope,
                criterion=criterion,
                requested_name=requested_name,
                max_bytes=max_bytes,
                files=targets,
                state=state,
                reason_code=reason,
            )
        )
    names_by_scope: dict[str, set[str]] = {}
    for row in rows:
        if (
            row.criterion == "EXACT_NAME"
            and row.state != "UNKNOWN"
            and row.requested_name is not None
        ):
            names_by_scope.setdefault(row.scope, set()).add(row.requested_name)
    space_conflicts = {
        row.scope
        for row in rows
        if row.criterion == "EXACT_NAME"
        and row.state != "UNKNOWN"
        and row.requested_name is not None
        and any(c.isspace() for c in row.requested_name)
        and any(r.criterion == "NO_WHITESPACE" and r.state != "UNKNOWN" for r in rows)
    }
    for row in rows:
        kind = "SIZE" if row.criterion == "MAX_BYTES" else "NAME"
        if row.state != "UNKNOWN" and any(
            k == kind
            and (
                s == row.scope or s == "KNOWN_DOCUMENT_FILES" or row.scope == "KNOWN_DOCUMENT_FILES"
            )
            for s, k in uncertain
        ):
            row.state, row.reason_code = "UNKNOWN", "UNRESOLVED_SCOPED_SOURCE"
        if (row.criterion == "EXACT_NAME" and len(names_by_scope.get(row.scope, set())) > 1) or (
            space_conflicts
            and row.criterion in {"EXACT_NAME", "NO_WHITESPACE"}
            and (row.scope in space_conflicts or row.criterion == "NO_WHITESPACE")
        ):
            row.state, row.reason_code = "UNKNOWN", "CONFLICTING_SOURCE_REQUIREMENTS"
    return rows
