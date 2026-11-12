"""Compose an exact, non-authorizing view from already verified native sources."""

from app.modules.submission.application.buyer_file_comparison import compare_buyer_files
from app.modules.submission.application.buyer_name_size_comparison import compare_buyer_names_sizes
from app.modules.submission.public.final_control_contracts import (
    FinalControlFile,
    SubmissionFinalControlProjection,
    SubmissionPricingReference,
)
from app.platform.events.dispatcher import CommandExecutionError


def build_final_control(*, package, coverage, source_state, authorization, pricing_reference=None):
    manifest = package.manifest_json
    source = manifest.get("preparation_source") or {}
    entries = manifest.get("entries")
    schema = manifest.get("schema_version")
    if (
        schema not in {2, 3}
        or (schema == 3) != (manifest.get("preparation_source") is not None)
        or not isinstance(source, dict)
        or not isinstance(entries, list)
        or any(not isinstance(item, dict) for item in entries)
        or not isinstance(source.get("annexes", []), list)
    ):
        raise CommandExecutionError("SUBMISSION_MANIFEST_INTEGRITY_FAILED")
    if source_state == "CURRENT":
        technical = [item for item in entries if item.get("kind") == "TECHNICAL_RESPONSE"]
        annex_entries = [item for item in entries if item.get("kind") == "SOURCE_ANNEX"]
        if (
            coverage is None
            or len(technical) != 1
            or technical[0].get("document_id") != str(package.technical_document_id)
            or technical[0].get("version") != package.technical_document_version
            or technical[0].get("sha256") != coverage.selected_response.content_sha256
            or technical[0].get("content_format", "MARKDOWN") != coverage.content_format
            or source.get("technical_document_id") != str(package.technical_document_id)
            or source.get("technical_document_version") != package.technical_document_version
            or annex_entries
            != [{"kind": "SOURCE_ANNEX", **item} for item in source.get("annexes", [])]
        ):
            raise CommandExecutionError("SUBMISSION_MANIFEST_INTEGRITY_FAILED")
    presence = "VERIFIED_SOURCE" if source_state == "CURRENT" else "UNKNOWN"
    files = []
    without_file = []
    for entry in manifest["entries"]:
        if entry["kind"] == "TECHNICAL_RESPONSE":
            files.append(
                FinalControlFile(
                    archive_path="technical-response.docx"
                    if entry.get("content_format") == "DOCX"
                    else "technical-response.md",
                    document_kind="TECHNICAL_RESPONSE",
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    if entry.get("content_format") == "DOCX"
                    else "text/markdown",
                    document_id=entry["document_id"],
                    sha256=entry["sha256"],
                    byte_size=getattr(coverage, "content_byte_size", None)
                    if source_state == "CURRENT"
                    else None,
                    presence=presence,
                )
            )
        elif entry["kind"] != "SOURCE_ANNEX":
            without_file.append(entry["kind"])
    for annex in source.get("annexes", []):
        files.append(
            FinalControlFile(
                archive_path=annex["archive_path"],
                document_kind=annex["document_kind"],
                media_type=annex["media_type"],
                document_id=annex["document_id"],
                sha256=annex["sha256"],
                byte_size=annex["byte_size"],
                requirement_ids=annex["requirement_ids"],
                presence=presence,
            )
        )
    included = {
        (str(requirement), str(item.document_id), item.sha256)
        for item in files
        if item.presence == "VERIFIED_SOURCE"
        for requirement in item.requirement_ids
    }
    comparisons = compare_buyer_files(
        files=files,
        requirements=coverage.requirements if coverage else [],
        dce_version_id=package.dce_version_id,
        source_state=source_state,
    )
    name_sizes = compare_buyer_names_sizes(
        files=files,
        requirements=coverage.requirements if coverage else [],
        dce_version_id=package.dce_version_id,
        source_state=source_state,
    )
    return SubmissionFinalControlProjection(
        name_size_comparisons=name_sizes,
        buyer_names_sizes_state="OBSERVATIONS_AVAILABLE"
        if any(r.state != "UNKNOWN" for r in name_sizes)
        else "UNKNOWN",
        submission_package_id=package.id,
        package_version=package.version,
        manifest_sha256=package.manifest_sha256,
        dce_version_id=package.dce_version_id,
        state="PARTIAL" if source_state == "CURRENT" else source_state,
        source_state=source_state,
        local_delivery_mode="LOCAL_ZIP" if source_state == "CURRENT" else "UNKNOWN",
        buyer_formats_state="OBSERVATIONS_AVAILABLE"
        if any(r.state != "UNKNOWN" for r in comparisons)
        else "UNKNOWN",
        format_comparisons=comparisons,
        files=files,
        requirements=coverage.requirements if coverage else [],
        missing_cited_annexes=[
            item
            for item in coverage.cited_annexes
            if (str(item.requirement_id), str(item.document_id), item.sha256) not in included
        ]
        if coverage
        else [],
        entries_without_exported_file=without_file,
        patron_review_ids=[item["review_id"] for item in source.get("response_drafts", [])]
        if source_state == "CURRENT"
        else [],
        p5_authorization_status="RECORDED" if authorization else "NOT_RECORDED",
        p5_authorization_id=authorization.id if authorization else None,
        pricing_reference=pricing_reference or SubmissionPricingReference(),
    )
