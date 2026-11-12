from uuid import uuid4

import pytest


def project(text, kind="SUBMISSION_DEADLINE_SIGNAL", directive="UNSPECIFIED"):
    from app.modules.dce.application.requirement_values import project_rc_requirement_values

    return project_rc_requirement_values(
        excerpt=text,
        requirement_type=kind,
        directive_signal=directive,
        start_byte_offset=7,
        source_fragment_id=uuid4(),
    )


def test_documents_and_lot_are_only_source_candidates():
    text = "Le DC1 et le DC2 sont obligatoires pour le lot 02."
    p = project(text, "CANDIDATURE_DOCUMENT", "REQUIRED_SIGNAL")
    assert p.documents == ("DC1", "DC2") and p.document_state == "CANDIDATE"
    assert p.lot_numbers == (2,) and p.lot_state == "CANDIDATE"
    assert p.applicability == "UNKNOWN" and p.date_state == p.timezone_state == "UNKNOWN"
    for e in p.evidence:
        assert text.encode()[e.start_byte_offset - 7 : e.end_byte_offset - 7]


@pytest.mark.parametrize(
    "date_text,date_value", [("21/11/2034", "2034-11-21"), ("29 février 2032", "2032-02-29")]
)
def test_explicit_deadline_has_separate_date_time_timezone_states(date_text, date_value):
    p = project(f"Date limite de remise : {date_text} à 10h30 pour le lot 2.")
    assert p.date_iso == date_value and p.date_state == "CANDIDATE"
    assert p.time_local == "10:30" and p.time_state == "CANDIDATE"
    assert p.timezone is None and p.timezone_state == "UNKNOWN"
    assert p.applicability == "UNKNOWN"


def test_explicit_utc_does_not_require_an_assumed_french_timezone():
    p = project("Date limite de remise : 21/11/2034 à 10:30 UTC.")
    assert p.timezone == "UTC" and p.timezone_state == "CANDIDATE"


@pytest.mark.parametrize(
    "text",
    [
        "Ancienne date limite de remise : 20/11/2034, nouvelle date : 25/11/2034.",
        "Date limite de remise : 31/02/2034 à 10h30.",
        "Date limite de remise : 21/11/2034 ou 25/11/2034.",
        "Le DC1 ne doit pas être fourni pour le lot 2.",
        "Le mémoire technique est obligatoire si le lot 2 est retenu.",
        "Le DC1 est obligatoire pour les lots 2 à 5.",
    ],
)
def test_ambiguity_never_selects_a_convenient_value(text):
    p = project(text)
    assert p.state == "REVIEW_REQUIRED"
    assert p.documents == p.lot_numbers == p.evidence == ()
    assert p.date_iso is p.time_local is p.timezone is None
    assert p.applicability == "UNKNOWN"


def test_no_year_or_implicit_timezone_is_invented():
    p = project("Date limite de remise : le 21 novembre à 10h30, heure locale.")
    assert p.date_iso is None and p.date_state == "UNKNOWN"
    assert p.time_local == "10:30" and p.timezone is None


def test_doc_mentions_without_positive_directive_are_not_expected_documents():
    p = project("Le DC1 est mentionné pour information.", "CANDIDATURE_DOCUMENT")
    assert p.documents == () and p.document_state == "UNKNOWN"


def test_each_region_reproduces_its_original_unicode_source():
    text = "Préambule é : le mémoire technique est obligatoire pour le lot 02."
    p = project(text, "OFFER_DOCUMENT", "REQUIRED_SIGNAL")
    raw = [
        text.encode()[e.start_byte_offset - 7 : e.end_byte_offset - 7].decode() for e in p.evidence
    ]
    assert raw == ["mémoire technique", "02"]


@pytest.mark.parametrize(
    "text",
    [
        "Date limite de remise : 21/11/2034 à 10:11:12.",
        "Date limite de remise : 21/11/2034 UTC+02h30.",
    ],
)
def test_unsupported_time_never_yields_a_tail_or_timezone_as_clock(text):
    p = project(text)
    assert p.time_local is None and p.time_state == "UNKNOWN"


@pytest.mark.parametrize("scope", ["lots 2, 3 ou 4", "lots n°2 ou n°3", "lots 2 et 3000"])
def test_partial_lot_list_cannot_become_a_proven_scope(scope):
    p = project(
        "Le DC1 est obligatoire pour les " + scope + ".", "CANDIDATURE_DOCUMENT", "REQUIRED_SIGNAL"
    )
    assert p.state == "REVIEW_REQUIRED" and p.lot_numbers == ()


def test_nominal_multiple_lots_keep_every_original_number():
    text = "Le DC1 est obligatoire pour les lots 2 et 3."
    p = project(text, "CANDIDATURE_DOCUMENT", "REQUIRED_SIGNAL")
    assert p.lot_numbers == (2, 3)
    assert [
        text.encode()[e.start_byte_offset - 7 : e.end_byte_offset - 7].decode()
        for e in p.evidence
        if e.field == "LOT"
    ] == ["2", "3"]


def test_values_embedded_in_a_url_are_not_extracted_as_deadlines_or_lots():
    p = project(
        "Date limite de remise : consulter https://exemple.test/21/11/2034?lot=2&clock=10:30"
    )
    assert p.date_iso is p.time_local is None and p.lot_numbers == ()


def test_candidate_field_needs_matching_value_evidence_in_public_contract():
    from app.modules.dce.public.contracts import CaseDceStructuredCandidateResponse
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CaseDceStructuredCandidateResponse.model_validate(
            {
                "state": "CANDIDATES_ONLY",
                "source_fragment_id": str(uuid4()),
                "documents": ["DC1"],
                "document_state": "CANDIDATE",
                "evidence": [
                    {
                        "field": "DOCUMENT",
                        "value": "DC2",
                        "start_byte_offset": 0,
                        "end_byte_offset": 3,
                    }
                ],
            }
        )


@pytest.mark.parametrize(
    "text",
    [
        "Date limite de remise précisée au profil acheteur, réunion le 21/11/2034.",
        "Date limite de remise : 21/11/2034, réunion à 10h30.",
    ],
)
def test_unrelated_calendar_or_meeting_time_is_not_the_deadline(text):
    p = project(text)
    assert p.state == "REVIEW_REQUIRED" and p.date_iso is p.time_local is None


def test_rectification_with_an_unrelated_meeting_date_is_not_a_conflicting_deadline():
    from app.modules.dce.application.requirement_values import rc_rectification_is_ambiguous

    assert not rc_rectification_is_ambiguous(
        [
            "Rectificatif : réunion le 20/11/2034. Date limite de remise : 21/11/2034.",
        ]
    )


def test_deadline_comparison_budget_is_not_reported_as_a_proven_conflict():
    from app.modules.dce.application.queries import CaseDceReadingRequirementProjection
    from app.modules.dce.infrastructure.case_dce_reading_reader import _refuse_conflicting_deadlines

    p = project("Date limite de remise : 21/11/2034 à 10h30.")
    rows = tuple(
        CaseDceReadingRequirementProjection(
            requirement_id=uuid4(),
            confirmation_revision=None,
            requirement_type="SUBMISSION_DEADLINE_SIGNAL",
            directive_signal="UNSPECIFIED",
            confirmation_outcome="PENDING_HUMAN_CONFIRMATION",
            uncertainty_status="SOURCE_SIGNAL_ONLY",
            document_family="RC",
            source_locator_label="Source",
            structured_candidate=p,
        )
        for _ in range(257)
    )
    result = _refuse_conflicting_deadlines(rows)
    assert all(x.structured_candidate is not None for x in result)
    assert {
        x.structured_candidate.reason_code for x in result if x.structured_candidate is not None
    } == {"COMPARISON_LIMIT"}
    assert all(x.structured_candidate is not None for x in result)
    assert all(
        x.structured_candidate is not None and x.structured_candidate.date_state == "UNKNOWN"
        for x in result
    )


@pytest.mark.parametrize("zone,value", [("UTC+02:30", "UTC+02:30"), ("UTC -01:00", "UTC-01:00")])
def test_explicit_offset_is_not_a_second_clock_or_a_guessed_timezone(zone, value):
    p = project("Date limite de remise : 21/11/2034 à 10h30 " + zone + ".")
    assert p.time_local == "10:30" and p.timezone == value
    assert p.timezone_state == "CANDIDATE" and p.applicability == "UNKNOWN"


@pytest.mark.parametrize(
    "fault", ["hash", "offset", "observation", "legacy", "family", "historical", "utf8"]
)
def test_unproved_reading_source_never_projects_values(fault):
    from dataclasses import replace
    from hashlib import sha256
    from types import SimpleNamespace

    from app.modules.dce.application.source_anchor_projection import (
        DceSourceAnchorProjection,
        DceSourceLocator,
        DceSourceLocatorKind,
    )
    from app.modules.dce.infrastructure.case_dce_reading_reader import (
        SqlAlchemyCaseDceReadingReader,
    )

    text = "É : le DC1 est obligatoire."
    fragment = uuid4()
    anchor = DceSourceAnchorProjection(
        source_anchor_id=fragment,
        dce_version_id=uuid4(),
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_ordinal=1,
        source_sha256="a" * 64,
        extractor_id="synthetic",
        extractor_version="1",
        fragment_sha256=sha256(text.encode()).hexdigest(),
        locator=DceSourceLocator(kind=DceSourceLocatorKind.TEXT_LINE, coordinates={"line": 1}),
    )
    row = SimpleNamespace(
        classification="RC",
        current_materialization=True,
        current_analysis=True,
        current_extraction=True,
        source_lifecycle="ADMITTED",
        source_integrity="VERIFIED",
        value_version="5",
        value_start=0,
        value_end=len(text.encode()),
        observation_start=0,
        observation_end=len(text.encode()),
        observation_fragment=fragment,
        source_fragment_id=fragment,
        value_kind="RC_DOCUMENT_CANDIDATURE",
        requirement_type="CANDIDATURE_DOCUMENT",
        value_directive="REQUIRED_SIGNAL",
        directive_signal="REQUIRED_SIGNAL",
        value_excerpt=text,
        value_rule="CANDIDATURE_FORM_REFERENCE_V1",
    )
    nominal = SqlAlchemyCaseDceReadingReader._structured_candidate(
        row=row, source_anchor=anchor, source_text=text
    )
    assert nominal.documents == ("DC1",)
    if fault == "hash":
        anchor = replace(anchor, fragment_sha256="0" * 64)
    elif fault == "offset":
        row.value_end += 1
    elif fault == "observation":
        row.observation_fragment = uuid4()
    elif fault == "legacy":
        row.value_version = "4"
    elif fault == "family":
        row.classification = "CCTP"
    elif fault == "historical":
        row.current_materialization = False
    elif fault == "utf8":
        row.value_start = row.observation_start = 1
    p = SqlAlchemyCaseDceReadingReader._structured_candidate(
        row=row, source_anchor=anchor, source_text=text
    )
    assert p.state in {"UNKNOWN", "REVIEW_REQUIRED"}
    assert p.documents == p.evidence == () and p.date_iso is None


def test_ambiguous_numeric_day_month_order_is_not_chosen_without_proof():
    p = project("Date limite de remise : 04/05/2034 à 10h30.")
    assert p.state == "REVIEW_REQUIRED" and p.date_iso is None


@pytest.mark.parametrize("text", ["05/05/2034", "5 mai 2034"])
def test_explicit_month_or_identical_numeric_components_have_one_calendar_value(text):
    p = project("Date limite de remise : " + text + ".")
    assert p.date_iso == "2034-05-05" and p.date_state == "CANDIDATE"


@pytest.mark.parametrize("scope", ["lots n°2 à n°5", "lots 2,3-5", "lots 2/3"])
def test_reviewed_lot_ranges_never_publish_a_partial_scope(scope):
    p = project(
        f"Le DC1 est obligatoire pour les {scope}.", "CANDIDATURE_DOCUMENT", "REQUIRED_SIGNAL"
    )
    assert p.state == "REVIEW_REQUIRED"
    assert p.documents == p.lot_numbers == p.evidence == ()


@pytest.mark.parametrize("clock", ["10h30-11h30", "10:30-11:30", "10h30+11h30"])
def test_reviewed_clock_ranges_never_publish_the_first_endpoint(clock):
    p = project(f"Date limite de remise : 21/11/2034 à {clock}.")
    assert p.state == "REVIEW_REQUIRED"
    assert p.time_local is None and p.evidence == ()
