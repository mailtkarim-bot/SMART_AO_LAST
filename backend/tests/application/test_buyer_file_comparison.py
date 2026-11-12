from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.modules.preparation.public.contracts import ResponseCoverageRequirement
from app.modules.submission.application.final_control import build_final_control


def report_for(
    excerpts,
    *,
    technical="MARKDOWN",
    kbis=True,
    source_state="CURRENT",
    patch=None,
    technical_byte_size=None,
):
    technical_id, evidence_id, version = uuid4(), uuid4(), uuid4()
    annexes: list[dict[str, object]] = []
    source = dict(
        technical_document_id=str(technical_id), technical_document_version=1, annexes=annexes
    )
    entry = dict(
        kind="TECHNICAL_RESPONSE", document_id=str(technical_id), version=1, sha256="a" * 64
    )
    if technical == "DOCX":
        entry["content_format"] = "DOCX"
    entries = [entry]
    if kbis:
        annex = dict(
            document_id=str(evidence_id),
            document_kind="KBIS",
            media_type="application/pdf",
            sha256="b" * 64,
            byte_size=50,
            requirement_ids=[],
            archive_path=f"annexes/{evidence_id}.pdf",
            signature="UNKNOWN",
        )
        annexes.append(annex)
        entries.append({"kind": "SOURCE_ANNEX", **annex})
    requirements = []
    for excerpt in excerpts:
        value = dict(
            requirement_id=uuid4(),
            document_family="RC",
            source_state="CURRENT_SOURCE",
            confirmation="CONFIRMED",
            source_locator="RC · ligne 4",
            source_excerpt=excerpt,
            lot_candidates=[],
            response_state="MISSING",
            pieces=[],
            source_anchor=dict(
                dce_version_id=str(version),
                dce_document_id=str(uuid4()),
                source_sha256="d" * 64,
                extraction_id=str(uuid4()),
                fragment_sha256="e" * 64,
            ),
        )
        if patch:
            value.update(patch)
        requirements.append(ResponseCoverageRequirement(**value))
    package = SimpleNamespace(
        id=uuid4(),
        version=1,
        manifest_sha256="c" * 64,
        dce_version_id=version,
        technical_document_id=technical_id,
        technical_document_version=1,
        manifest_json={"schema_version": 3, "entries": entries, "preparation_source": source},
    )
    coverage = SimpleNamespace(
        requirements=requirements,
        cited_annexes=[],
        content_format=technical,
        content_byte_size=technical_byte_size,
        selected_response=SimpleNamespace(content_sha256="a" * 64),
    )
    return build_final_control(
        package=package, coverage=coverage, source_state=source_state, authorization=None
    )


def test_explicit_pdf_demand_is_compared_to_the_exact_technical_piece():
    report = report_for(["Le mémoire technique doit être remis au format PDF."])
    row = report.format_comparisons[0]
    assert row.state == "OBSERVED_MISMATCH" and row.requested == "PDF"
    assert [f.archive_path for f in row.files] == ["technical-response.md"]
    assert row.source_locator == "RC · ligne 4" and row.source_anchor["source_sha256"] == "d" * 64
    assert row.applicability == row.conformity == report.conformity == "UNKNOWN"
    assert report.p5_authorization_status == "NOT_RECORDED"


def test_kbis_pdf_match_never_grants_conformity_or_p5():
    report = report_for(["Le KBIS doit être fourni au format PDF."])
    row = report.format_comparisons[0]
    assert row.state == "OBSERVED_MATCH" and row.scope == "KBIS"
    assert len(row.files) == 1 and row.files[0].document_kind == "KBIS"
    assert row.conformity == report.conformity == "UNKNOWN"
    assert report.p5_authorization_status == "NOT_RECORDED"


@pytest.mark.parametrize(
    "quote,state",
    [
        ("Le pli doit être remis sous forme d'une archive ZIP.", "OBSERVED_MATCH"),
        ("Les archives ZIP sont interdites.", "OBSERVED_MISMATCH"),
        ("Les fichiers doivent être déposés individuellement, sans archive.", "OBSERVED_MISMATCH"),
    ],
)
def test_local_zip_is_not_a_buyer_submission_or_acceptance(quote, state):
    report = report_for([quote])
    assert report.local_delivery_mode == "LOCAL_ZIP"
    assert report.format_comparisons[0].state == state
    assert report.external_submission == "NOT_PERFORMED" and report.conformity == "UNKNOWN"


@pytest.mark.parametrize(
    "quote",
    [
        "Le format PDF est obligatoire.",
        "Le mémoire technique doit être remis au format PDF ou DOCX.",
        "Le mémoire technique ne doit pas être remis au format PDF.",
        "Le mémoire technique doit être remis au format PDF…",
        "Si la candidature est retenue, le KBIS doit être fourni au format PDF.",
        "Le dépôt se fait sur le profil acheteur.",
    ],
)
def test_uncertain_scope_negation_truncation_condition_or_channel_stays_unknown(quote):
    report = report_for([quote])
    assert report.format_comparisons
    assert all(r.state == r.conformity == "UNKNOWN" for r in report.format_comparisons)
    assert all(r.reason_code for r in report.format_comparisons)


@pytest.mark.parametrize(
    "patch",
    [
        {"confirmation": "PENDING_HUMAN_CONFIRMATION"},
        {"source_anchor": None},
        {"source_state": "UNKNOWN"},
        {"source_anchor": {"dce_version_id": str(uuid4())}},
        {"lot_candidates": [1]},
    ],
)
def test_unverified_source_or_lot_cannot_be_promoted_into_a_match(patch):
    report = report_for(["Le KBIS doit être fourni au format PDF."], patch=patch)
    assert report.format_comparisons[0].state == "UNKNOWN"


def test_conflicting_format_demands_are_retained_and_not_arbitrated():
    report = report_for(
        [
            "Le mémoire technique doit être remis au format PDF.",
            "Le mémoire technique doit être remis au format DOCX.",
        ],
        technical="DOCX",
    )
    assert len(report.format_comparisons) == 2
    assert all(
        r.state == "UNKNOWN" and r.reason_code == "CONFLICTING_SOURCE_REQUIREMENTS"
        for r in report.format_comparisons
    )


def test_missing_target_piece_is_visible_instead_of_a_format_match():
    report = report_for(["Le KBIS doit être fourni au format PDF."], kbis=False)
    row = report.format_comparisons[0]
    assert (
        row.state == "OBSERVED_MISMATCH"
        and row.reason_code == "TARGET_FILE_MISSING"
        and not row.files
    )


def test_obsolete_and_absent_sources_stay_unknown():
    report = report_for(["Le KBIS doit être fourni au format PDF."], source_state="REVIEW_REQUIRED")
    assert report.local_delivery_mode == "UNKNOWN"
    assert report.format_comparisons[0].state == "UNKNOWN"
    empty = report_for([])
    assert empty.buyer_formats_state == "UNKNOWN" and not empty.format_comparisons


def test_a_current_negative_scoped_signal_prevents_a_reassuring_positive_match():
    report = report_for(
        [
            "Le KBIS doit être fourni au format PDF.",
            "Le KBIS ne doit pas être fourni au format PDF.",
        ]
    )
    assert len(report.format_comparisons) == 2
    assert all(r.state == "UNKNOWN" for r in report.format_comparisons)


def test_a_current_compound_signal_on_the_same_scope_is_not_silently_ignored():
    report = report_for(
        [
            "Le KBIS doit être fourni au format PDF.",
            "Le KBIS doit être fourni au format PDF ou DOCX.",
        ]
    )
    assert all(r.state == "UNKNOWN" for r in report.format_comparisons)
