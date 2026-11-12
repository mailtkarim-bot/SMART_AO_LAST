"""Read exact native response bytes and project their stored wording without guessing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from uuid import UUID

from app.modules.membership.public.text_safety import contains_forbidden_text
from app.modules.preparation.infrastructure.buyer_docx import W, _package, _xml


@dataclass(frozen=True)
class NativeContribution:
    requirement_id: str
    section_code: str
    text: str | None
    missing: str
    start_byte: int
    end_byte: int
    raw_sha256: str


_HEADER = re.compile(
    r"^### Exigence [0-9]+ — ([0-9a-f-]{36}) / "
    r"(COVER|UNDERSTANDING|METHOD|RESOURCES|SCHEDULE|RISKS|SOURCES)$"
)
_WORDING = "- Rédaction humaine — non validée par la seule saisie :"


def source_contributions(raw: bytes) -> dict[tuple[str, str], NativeContribution]:
    if len(raw) > 100_000:
        raise ValueError("RESPONSE_SOURCE_LIMIT")
    lines = raw.decode("utf-8").splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line.encode()))
    starts = [
        (i, match)
        for i, line in enumerate(lines)
        if (match := _HEADER.fullmatch(line.rstrip("\r\n")))
    ]
    if not starts or len(starts) > 64:
        raise ValueError("RESPONSE_CONTRIBUTION_REQUIRED")
    result = {}
    for index, (start, match) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(lines)
        requirement, section = str(UUID(match.group(1))), match.group(2)
        key = requirement, section
        if key in result:
            raise ValueError("RESPONSE_CONTRIBUTION_DUPLICATE")
        markers = [i for i in range(start, end) if lines[i].rstrip("\r\n") == _WORDING]
        if len(markers) != 1:
            raise ValueError("RESPONSE_CONTRIBUTION_UNKNOWN")
        first = markers[0] + 1
        # Historical missing-only drafts contain one blank line before the UNKNOWN marker.
        if (
            first + 1 < end
            and not lines[first].strip()
            and lines[first + 1].rstrip("\r\n") == "> UNKNOWN — contenu non rédigé."
        ):
            first += 1
        last = first
        while last < end and lines[last].startswith("> "):
            last += 1
        if first == last or last >= end or not lines[last].startswith("- Manques déclarés : "):
            raise ValueError("RESPONSE_CONTRIBUTION_UNKNOWN")
        text: str | None = "\n".join(line[2:].rstrip("\r\n") for line in lines[first:last])
        if text == "UNKNOWN — contenu non rédigé.":
            text = None
        missing = lines[last][len("- Manques déclarés : ") :].rstrip("\r\n")
        result[key] = NativeContribution(
            requirement,
            section,
            text,
            missing,
            offsets[first],
            offsets[last],
            sha256(raw[offsets[first] : offsets[last]]).hexdigest(),
        )
    return result


def docx_text(content: bytes) -> str:
    _, parts, root = _package(content)
    roots = [root] + [
        _xml(raw)
        for name, raw in parts.items()
        if name.startswith("word/") and name.endswith(".xml") and name != "word/document.xml"
    ]
    paragraphs = []
    for paragraph in (p for part in roots for p in part.findall(f".//{{{W}}}p")):
        text = ""
        for node in paragraph.iter():
            if node.tag == f"{{{W}}}t":
                text += node.text or ""
            elif node.tag == f"{{{W}}}br":
                text += "\n"
        paragraphs.append(text)
    return "\n".join(paragraphs)


def read_response_artifact(storage, draft) -> tuple[bytes, str]:
    content = storage.read(storage_key=draft.storage_key)
    format = getattr(draft, "content_format", "MARKDOWN")
    if sha256(content).hexdigest() != draft.content_sha256:
        raise ValueError("RESPONSE_DRAFT_UNKNOWN")
    if format == "MARKDOWN" and len(content) <= 100_000:
        text = content.decode("utf-8")
    elif format == "DOCX" and len(content) <= 5 * 1024 * 1024:
        text = docx_text(content)
    else:
        raise ValueError("RESPONSE_DRAFT_FORMAT_UNKNOWN")
    if contains_forbidden_text(text):
        raise ValueError("FINANCIAL_DATA_FORBIDDEN")
    return content, text
