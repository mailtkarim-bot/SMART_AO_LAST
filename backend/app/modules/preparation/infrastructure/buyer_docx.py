"""Bounded OOXML frame editing: explicit regions, unchanged non-document parts."""

from __future__ import annotations

import copy
import io
import re
import stat
import zipfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePosixPath

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
MARKER = re.compile(r"^\[\[REPONSE:([A-Z0-9_]{1,64})\]\]$")
UNKNOWN = "UNKNOWN — contribution non renseignée."


@dataclass(frozen=True)
class DocxRegion:
    locator: str
    xml_sha256: str
    text: str
    state: str = "UNFILLED"


@dataclass(frozen=True)
class DocxFill:
    locator: str
    expected_xml_sha256: str
    text: str | None


@dataclass(frozen=True)
class FilledDocx:
    content: bytes
    regions: tuple[DocxRegion, ...]


def _xml(raw: bytes):
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
    root = etree.fromstring(raw, parser)
    if root.getroottree().docinfo.doctype:
        raise ValueError("DOCX_ACTIVE_CONTENT_REVIEW_REQUIRED")
    return root


def _package(content: bytes):
    if len(content) > 5 * 1024 * 1024:
        raise ValueError("DOCX_SIZE_LIMIT")
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
        entries = archive.infolist()
        if len(entries) > 256 or sum(e.file_size for e in entries) > 20 * 1024 * 1024:
            raise ValueError("DOCX_SIZE_LIMIT")
        names = [e.filename for e in entries]
        if len({n.casefold() for n in names}) != len(names):
            raise ValueError("DOCX_DUPLICATE_PART")
        parts = {}
        for entry in entries:
            path = PurePosixPath(entry.filename)
            if (
                path.is_absolute()
                or ".." in path.parts
                or path.as_posix() != entry.filename.rstrip("/")
                or "\\" in entry.filename
                or stat.S_ISLNK(entry.external_attr >> 16)
                or entry.flag_bits & 1
                or entry.file_size > 4 * 1024 * 1024
                or entry.file_size > max(entry.compress_size, 1) * 200
            ):
                raise ValueError("DOCX_UNSAFE_PART")
            lower = entry.filename.casefold()
            if any(p in lower for p in ("vbaproject", "activex/", "embeddings/")):
                raise ValueError("DOCX_ACTIVE_CONTENT_REVIEW_REQUIRED")
            raw = archive.read(entry)
            parts[entry.filename] = raw
            if lower.endswith((".xml", ".rels")):
                root = _xml(raw)
                if lower.startswith("word/") and root.xpath(
                    ".//w:instrText | .//w:fldSimple | .//w:altChunk | "
                    ".//w:object | .//w:ins | .//w:del",
                    namespaces=NS,
                ):
                    raise ValueError("DOCX_ACTIVE_CONTENT_REVIEW_REQUIRED")
                if lower.endswith(".rels") and any(
                    node.get("TargetMode", "").casefold() == "external" for node in root
                ):
                    raise ValueError("DOCX_EXTERNAL_RELATIONSHIP_REVIEW_REQUIRED")
                if entry.filename != "word/document.xml" and b"[[REPONSE:" in raw:
                    raise ValueError("DOCX_REGION_OUTSIDE_BODY_REVIEW_REQUIRED")
        if "word/document.xml" not in parts or "[Content_Types].xml" not in parts:
            raise ValueError("DOCX_PART_REQUIRED")
        types = _xml(parts["[Content_Types].xml"])
        main = [n for n in types if n.get("PartName") == "/word/document.xml"]
        if (
            len(main) != 1
            or main[0].get("ContentType")
            != "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
        ):
            raise ValueError("DOCX_CONTENT_TYPE_REQUIRED")
        root = _xml(parts["word/document.xml"])
        if root.tag != f"{{{W}}}document" or root.xpath(
            ".//w:instrText | .//w:fldSimple | .//w:altChunk | .//w:object | .//w:ins | .//w:del",
            namespaces=NS,
        ):
            raise ValueError("DOCX_ACTIVE_CONTENT_REVIEW_REQUIRED")
        return entries, parts, root
    except (zipfile.BadZipFile, etree.XMLSyntaxError, RuntimeError, KeyError) as error:
        raise ValueError("DOCX_PACKAGE_REVIEW_REQUIRED") from error


def _regions(root):
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("DOCX_BODY_REQUIRED")
    paragraphs = {}
    for index, p in enumerate(body.findall("w:p", NS), 1):
        paragraphs[f"p:{index}"] = p
    for table_index, table in enumerate(body.findall("w:tbl", NS), 1):
        if table.xpath(".//w:tbl | .//w:gridSpan | .//w:vMerge", namespaces=NS):
            continue
        for row_index, row in enumerate(table.findall("w:tr", NS), 1):
            for cell_index, cell in enumerate(row.findall("w:tc", NS), 1):
                for paragraph_index, p in enumerate(cell.findall("w:p", NS), 1):
                    paragraphs[
                        f"t:{table_index}/r:{row_index}/c:{cell_index}/p:{paragraph_index}"
                    ] = p
    result = {}
    for locator, p in paragraphs.items():
        text = "".join(p.xpath(".//w:t/text()", namespaces=NS))
        if not MARKER.fullmatch(text):
            continue
        if any(n.tag not in {f"{{{W}}}pPr", f"{{{W}}}r"} for n in p) or any(
            n.tag not in {f"{{{W}}}rPr", f"{{{W}}}t"} for run in p.findall("w:r", NS) for n in run
        ):
            raise ValueError("DOCX_REGION_STRUCTURE_REVIEW_REQUIRED")
        text_runs = [
            run for run in p.findall("w:r", NS) if "".join(run.xpath("w:t/text()", namespaces=NS))
        ]
        styles = {
            etree.tostring(style) if (style := run.find("w:rPr", NS)) is not None else b""
            for run in text_runs
        }
        if len(styles) > 1:
            raise ValueError("DOCX_REGION_STYLE_REVIEW_REQUIRED")
        result[locator] = (p, DocxRegion(locator, sha256(etree.tostring(p)).hexdigest(), text))
    marked = [
        p
        for p in root.findall(".//w:p", NS)
        if "[[REPONSE:" in "".join(p.xpath(".//w:t/text()", namespaces=NS))
    ]
    if len(marked) != len(result) or len(result) > 64:
        raise ValueError("DOCX_AMBIGUOUS_REGION_REVIEW_REQUIRED")
    if not result:
        raise ValueError("DOCX_NO_FILLABLE_REGION")
    return result


def inspect_template(content: bytes) -> tuple[DocxRegion, ...]:
    _, _, root = _package(content)
    return tuple(region for _, region in _regions(root).values())


def fill_template(content: bytes, fills: tuple[DocxFill, ...]) -> FilledDocx:
    entries, parts, root = _package(content)
    regions = _regions(root)
    if len({f.locator for f in fills}) != len(fills):
        raise ValueError("DOCX_DUPLICATE_FILL")
    by_locator = {f.locator: f for f in fills}
    if set(by_locator) - set(regions):
        raise ValueError("DOCX_REGION_UNKNOWN")
    output = []
    for locator, (paragraph, region) in regions.items():
        fill = by_locator.get(locator)
        if fill is not None and fill.expected_xml_sha256 != region.xml_sha256:
            raise ValueError("DOCX_REGION_CHANGED")
        text = fill.text if fill is not None and fill.text else UNKNOWN
        if len(text.encode()) > 12000 or any(ord(c) < 32 and c not in "\n\t" for c in text):
            raise ValueError("DOCX_FILL_TEXT_LIMIT")
        if "\t" in text:
            raise ValueError("DOCX_FILL_CONTROL_REVIEW_REQUIRED")
        runs = paragraph.findall("w:r", NS)
        properties = runs[0].find("w:rPr", NS) if runs else None
        for run in runs:
            paragraph.remove(run)
        for index, line in enumerate(text.split("\n")):
            run = etree.SubElement(paragraph, f"{{{W}}}r")
            if properties is not None:
                run.append(copy.deepcopy(properties))
            if index:
                etree.SubElement(run, f"{{{W}}}br")
            node = etree.SubElement(run, f"{{{W}}}t")
            node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            node.text = line
        output.append(
            DocxRegion(locator, region.xml_sha256, text, "FILLED" if text != UNKNOWN else "UNKNOWN")
        )
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for entry in entries:
            archive.writestr(entry, parts[entry.filename])
    return FilledDocx(buffer.getvalue(), tuple(output))
