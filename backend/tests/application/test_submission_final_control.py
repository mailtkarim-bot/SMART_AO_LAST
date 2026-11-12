from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.modules.preparation.public.contracts import ResponseCitedAnnex, ResponseCoverageRequirement
from app.modules.submission.application.final_control import build_final_control


def test_missing_cited_file_and_text_stay_missing_despite_p5():
    requirement, document, package_id = uuid4(), uuid4(), uuid4()
    package = SimpleNamespace(
        id=package_id,
        version=2,
        technical_document_id=document,
        technical_document_version=2,
        manifest_sha256="c" * 64,
        dce_version_id=uuid4(),
        manifest_json={
            "schema_version": 3,
            "entries": [
                {
                    "kind": "TECHNICAL_RESPONSE",
                    "document_id": str(document),
                    "version": 2,
                    "sha256": "a" * 64,
                }
            ],
            "preparation_source": {
                "technical_document_id": str(document),
                "technical_document_version": 2,
            },
        },
    )
    missing = ResponseCoverageRequirement(
        requirement_id=requirement,
        document_family="RC",
        source_state="CURRENT",
        confirmation="CONFIRMED",
        source_locator="page:2",
        source_excerpt="Joindre une preuve.",
        lot_candidates=[1],
        response_state="MISSING",
        pieces=[],
    )
    coverage = SimpleNamespace(
        content_format="MARKDOWN",
        selected_response=SimpleNamespace(content_sha256="a" * 64),
        requirements=[missing],
        cited_annexes=[
            ResponseCitedAnnex(
                requirement_id=requirement,
                section_code="ATTESTATION",
                document_id=uuid4(),
                sha256="b" * 64,
            )
        ],
    )
    result = build_final_control(
        package=package,
        coverage=coverage,
        source_state="CURRENT",
        authorization=SimpleNamespace(id=uuid4()),
    )
    assert result.state == "PARTIAL" and result.p5_authorization_status == "RECORDED"
    assert result.requirements[0].response_state == "MISSING"
    assert len(result.missing_cited_annexes) == 1
    assert result.signature_records == [] and result.signature_visibility == "RESTRICTED"
    assert (
        result.signature_verification == result.signer_authority == result.conformity == "UNKNOWN"
    )
    assert result.files[0].signature == "UNKNOWN"


@pytest.mark.parametrize(
    "divergence", ["hash", "document", "version", "format", "duplicate", "annex", "schema"]
)
def test_final_control_rejects_candidate_entries_that_diverge_from_verified_c10_bytes(divergence):
    import pytest
    from app.platform.events.dispatcher import CommandExecutionError

    document, package_id = uuid4(), uuid4()
    package = SimpleNamespace(
        id=package_id,
        version=1,
        manifest_sha256="c" * 64,
        dce_version_id=uuid4(),
        technical_document_id=document,
        technical_document_version=2,
        manifest_json={
            "schema_version": 3,
            "entries": [
                {
                    "kind": "TECHNICAL_RESPONSE",
                    "document_id": str(document),
                    "version": 2,
                    "sha256": "a" * 64,
                }
            ],
            "preparation_source": {
                "technical_document_id": str(document),
                "technical_document_version": 2,
                "annexes": [],
            },
        },
    )
    manifest = package.manifest_json
    entry = manifest["entries"][0]
    if divergence == "hash":
        entry["sha256"] = "b" * 64
    elif divergence == "document":
        entry["document_id"] = str(uuid4())
    elif divergence == "version":
        entry["version"] = 9
    elif divergence == "format":
        entry["content_format"] = "DOCX"
    elif divergence == "duplicate":
        manifest["entries"].append(dict(entry))
    elif divergence == "annex":
        manifest["entries"].append({"kind": "SOURCE_ANNEX", "sha256": "b" * 64})
    elif divergence == "schema":
        manifest["schema_version"] = 2
    verified = SimpleNamespace(
        selected_response=SimpleNamespace(content_sha256="a" * 64),
        content_format="MARKDOWN",
        requirements=[],
        cited_annexes=[],
    )
    with pytest.raises(CommandExecutionError, match="SUBMISSION_MANIFEST_INTEGRITY_FAILED"):
        build_final_control(
            package=package, coverage=verified, source_state="CURRENT", authorization=None
        )


def test_third_party_file_exposes_its_kind_and_format_without_asserting_official_validity():
    technical, evidence, requirement = uuid4(), uuid4(), uuid4()
    annex = dict(
        document_id=str(evidence),
        sha256="b" * 64,
        requirement_ids=[str(requirement)],
        document_kind="KBIS",
        media_type="application/pdf",
        byte_size=50,
        archive_path=f"annexes/{evidence}.pdf",
        signature="UNKNOWN",
    )
    package = SimpleNamespace(
        id=uuid4(),
        version=1,
        manifest_sha256="c" * 64,
        dce_version_id=uuid4(),
        technical_document_id=technical,
        technical_document_version=1,
        manifest_json={
            "schema_version": 3,
            "entries": [
                {
                    "kind": "TECHNICAL_RESPONSE",
                    "document_id": str(technical),
                    "version": 1,
                    "sha256": "a" * 64,
                },
                {"kind": "SOURCE_ANNEX", **annex},
            ],
            "preparation_source": {
                "technical_document_id": str(technical),
                "technical_document_version": 1,
                "annexes": [annex],
            },
        },
    )
    coverage = SimpleNamespace(
        selected_response=SimpleNamespace(content_sha256="a" * 64),
        content_format="MARKDOWN",
        requirements=[],
        cited_annexes=[],
    )
    report = build_final_control(
        package=package, coverage=coverage, source_state="CURRENT", authorization=None
    )
    evidence_file = next(f for f in report.files if f.document_id == evidence)
    assert evidence_file.document_kind == "KBIS"
    assert evidence_file.media_type == "application/pdf"
    assert evidence_file.presence == "VERIFIED_SOURCE"
    assert evidence_file.validity == evidence_file.signature == report.conformity == "UNKNOWN"
