"""Presence in selected bytes never establishes buyer compliance or signature."""

from types import SimpleNamespace
from uuid import uuid4

from app.modules.preparation.application import document_content
from app.modules.preparation.application.document_content import (
    ResponsePlanDraftItem,
    build_response_plan_draft,
)
from app.modules.preparation.infrastructure.response_artifact import source_contributions
from app.modules.preparation.public.contracts import ResponseContribution


def _point(identity, *, family="RC", source="CURRENT_SOURCE", lots=(1,)):
    return SimpleNamespace(
        requirement_id=identity,
        document_family=family,
        confirmation_outcome="CONFIRMED",
        source_proof_state=source,
        source_locator_label="Ligne 1",
        source_anchor=None,
        structured_candidate=SimpleNamespace(lot_numbers=lots, lot_state="CANDIDATE"),
    )


def _parts(*values):
    items = tuple(
        ResponsePlanDraftItem(identity, "METHOD", "Accès", "Site occupé", 1, 1)
        for identity, _, _ in values
    )
    content = build_response_plan_draft(
        plan_version=1,
        draft_version=1,
        items=items,
        contributions=tuple(
            ResponseContribution(
                requirement_id=identity, section_code="METHOD", content=text, missing=missing
            )
            for identity, text, missing in values
        ),
    )
    return source_contributions(content.encode())


def _project(points, parts, *, regions=None):
    assert hasattr(document_content, "build_response_coverage"), (
        "Selected response coverage is missing"
    )
    return document_content.build_response_coverage(
        requirements=points, contributions=parts, regions=regions
    )


def test_coverage_keeps_every_safe_requirement_and_the_exact_lot_candidate():
    present, absent, private = uuid4(), uuid4(), uuid4()
    rows = _project(
        [_point(present), _point(absent, lots=()), _point(private, family="DPGF")],
        _parts((present, "Accès accompagné.", "Horaire à confirmer")),
    )
    assert [row["requirement_id"] for row in rows] == [present, absent]
    assert rows[0]["response_state"] == "TEXT_WITH_GAPS"
    assert rows[0]["pieces"][0]["missing"] == "Horaire à confirmer"
    assert rows[0]["lot_candidates"] == [1]
    assert rows[1]["lot_candidates"] == []
    assert rows[1]["response_state"] == "MISSING"
    assert rows[1]["pieces"] == []
    assert all(
        row["applicability"] == row["coverage"] == row["signature"] == "UNKNOWN" for row in rows
    )


def test_docx_only_counts_regions_actually_filled_from_selected_contributions():
    included, source_only = uuid4(), uuid4()
    parts = _parts((included, "Accès accompagné.", ""), (source_only, "Autre réponse.", ""))
    rows = _project(
        [_point(included), _point(source_only)],
        parts,
        regions=[
            dict(
                locator="/word/document.xml/p[1]",
                state="FILLED",
                text_sha256="a" * 64,
                source=dict(requirement_id=str(included), section_code="METHOD"),
            )
        ],
    )
    assert rows[0]["response_state"] == "TEXT_PRESENT"
    assert rows[0]["pieces"][0]["locator"] == "/word/document.xml/p[1]"
    assert rows[1]["response_state"] == "MISSING"
    assert rows[1]["pieces"] == []


def test_unknown_region_or_missing_text_cannot_cover_an_exigence():
    identity = uuid4()
    parts = _parts((identity, "", "Attestation absente"))
    row = _project([_point(identity)], parts)[0]
    assert row["response_state"] == "MISSING"
    assert row["pieces"][0]["missing"] == "Attestation absente"
    row = _project(
        [_point(identity)],
        parts,
        regions=[
            dict(
                locator="p[1]",
                state="UNKNOWN",
                text_sha256="a" * 64,
                source=dict(requirement_id=str(identity), section_code="METHOD"),
            )
        ],
    )[0]
    assert row["response_state"] == "MISSING"


def test_unproven_or_unconfirmed_source_stays_unknown_even_with_text():
    identity = uuid4()
    row = _project([_point(identity, source="UNKNOWN")], _parts((identity, "Texte déclaré.", "")))[
        0
    ]
    assert row["response_state"] == "UNKNOWN"
    assert row["lot_candidates"] == []


def test_multiple_sections_keep_their_own_offsets_hashes_and_missing_declarations():
    identity = uuid4()
    parts = _parts((identity, "Texte déclaré.", ""))
    row = _project([_point(identity)], parts)[0]
    part = next(iter(parts.values()))
    assert row["pieces"][0]["start_byte"] == part.start_byte
    assert row["pieces"][0]["end_byte"] == part.end_byte
    assert row["pieces"][0]["sha256"] == part.raw_sha256
    assert row["response_state"] == "TEXT_PRESENT"
    assert row["coverage"] == "UNKNOWN"


def test_native_missing_only_contribution_is_readable_with_exact_missing_state():
    identity = uuid4()
    parts = _parts((identity, "", "Attestation absente"))
    part = parts[(str(identity), "METHOD")]
    assert part.text is None
    assert part.missing == "Attestation absente"


def test_human_missing_starting_with_unknown_is_not_the_automatic_placeholder():
    identity = uuid4()
    row = _project(
        [_point(identity)],
        _parts((identity, "Accès accompagné.", "UNKNOWN — signature à obtenir")),
    )[0]
    assert row["response_state"] == "TEXT_WITH_GAPS"
