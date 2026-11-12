import pytest
from app.modules.dce.application.document_announcements import detect_document_announcements


@pytest.mark.parametrize(
    ("text", "family", "claim", "lots"),
    [
        ("Le dossier comprend le CCAP.", "CCAP", "PROVIDED_SIGNAL", ()),
        ("Le CCTP est joint au dossier pour le lot 02.", "CCTP", "PROVIDED_SIGNAL", (2,)),
        ("Le CCAP n’est pas joint au dossier.", "CCAP", "NOT_PROVIDED_SIGNAL", ()),
        ("Le candidat doit remettre le BPU.", "BPU", "SUBMISSION_SIGNAL", ()),
        ("Le BPU n’est pas à remettre.", "BPU", "NOT_REQUIRED_SIGNAL", ()),
        ("L’acte d’engagement est fourni dans le DCE.", "AE", "PROVIDED_SIGNAL", ()),
        (
            "Le cahier des clauses techniques particulières est joint.",
            "CCTP",
            "PROVIDED_SIGNAL",
            (),
        ),
        ("Le DCE comprend : RC, CCAP et CCTP.", "CCTP", "PROVIDED_SIGNAL", ()),
    ],
)
def test_announcements_keep_the_claim_and_exact_source_window(text, family, claim, lots):
    result = detect_document_announcements(text)
    item = next(x for x in result if x.document_family == family)
    assert item.claim == claim
    assert item.lot_numbers == lots
    assert text.encode()[item.start_byte_offset : item.end_byte_offset].decode() == item.excerpt
    assert item.presence_status == item.applicability == item.criticality == "UNKNOWN"


def test_adjacent_clauses_do_not_transfer_negation_or_lot():
    text = "Le CCAP n’est pas joint pour le lot 2. Le CCTP est joint pour le lot 3."
    result = detect_document_announcements(text)
    assert [(x.document_family, x.claim, x.lot_numbers) for x in result] == [
        ("CCAP", "NOT_PROVIDED_SIGNAL", (2,)),
        ("CCTP", "PROVIDED_SIGNAL", (3,)),
    ]


@pytest.mark.parametrize(
    "text",
    [
        "L’entreprise intervient selon le CCAP.",
        "Le CCTP décrit les travaux.",
        "Le prix comporte un coût de planification.",
        "La référence RC-44 est un identifiant interne.",
    ],
)
def test_mentions_without_document_announcement_do_not_create_candidates(text):
    assert detect_document_announcements(text) == ()


def test_contradictory_provision_and_unclear_scope_stay_unknown():
    text = "Le CCAP est joint mais il n’est pas fourni pour certains lots."
    result = detect_document_announcements(text)
    assert len(result) == 1
    assert result[0].claim == "AMBIGUOUS"
    assert result[0].lot_numbers == ()
    assert result[0].presence_status == "UNKNOWN"


@pytest.mark.parametrize(
    ("text", "family", "claim"),
    [
        ("Le CCAP est joint sauf pour le lot 2.", "CCAP", "AMBIGUOUS"),
        ("Le CCAP sera fourni ultérieurement.", "CCAP", "AMBIGUOUS"),
        ("Le BPU est à remettre si cette prestation est retenue.", "BPU", "AMBIGUOUS"),
        ("Ne pas joindre le CCAP à l’offre.", "CCAP", "PROHIBITED_SUBMISSION_SIGNAL"),
    ],
)
def test_exceptions_future_and_prohibition_are_not_flattened(text, family, claim):
    result = detect_document_announcements(text)
    assert result[0].document_family == family
    assert result[0].claim == claim
    assert result[0].presence_status == "UNKNOWN"
    if claim == "AMBIGUOUS":
        assert result[0].lot_numbers == ()


@pytest.mark.parametrize(
    "text",
    [
        "Le candidat comprend le CCAP.",
        "Le dossier comprend une référence RC-44.",
        "Le CCAP n’est pas applicable au lot 2.",
    ],
)
def test_actor_understanding_identifiers_and_applicability_are_not_document_provision(text):
    assert detect_document_announcements(text) == ()


def test_list_rows_retain_a_separate_exact_heading_anchor():
    text = "Le DCE comprend les pièces suivantes :\n- RC\n- CCAP\n- CCTP pour le lot 2\n"
    result = detect_document_announcements(text)
    assert [(x.document_family, x.claim) for x in result] == [
        ("RC", "PROVIDED_SIGNAL"),
        ("CCAP", "PROVIDED_SIGNAL"),
        ("CCTP", "PROVIDED_SIGNAL"),
    ]
    for item in result:
        raw = text.encode()
        assert raw[item.start_byte_offset : item.end_byte_offset].decode() == item.excerpt
        assert (
            raw[item.context_start_byte_offset : item.context_end_byte_offset].decode()
            == item.context_excerpt
        )
        assert item.context_excerpt == "Le DCE comprend les pièces suivantes :"
    assert result[-1].lot_numbers == (2,)


def test_list_context_does_not_cross_blank_lines_or_plain_prose():
    text = "Le DCE comprend :\n- CCAP\n\nLe CCTP décrit les travaux.\n- BPU\n"
    result = detect_document_announcements(text)
    assert [x.document_family for x in result] == ["CCAP"]


def test_contradictions_are_compared_with_lot_scope_without_asserting_absence():
    from app.modules.dce.application.document_announcements import conflicting_announcements

    different = detect_document_announcements(
        "Le CCAP est joint pour le lot 2. Le CCAP n’est pas joint pour le lot 3."
    )
    assert conflicting_announcements(different) == frozenset()
    same = detect_document_announcements(
        "Le CCAP est joint pour le lot 2. Le CCAP n’est pas joint pour le lot 2."
    )
    assert conflicting_announcements(same) == frozenset({0, 1})
    assert all(item.presence_status == "UNKNOWN" for item in same)


@pytest.mark.parametrize(
    "text",
    [
        "Le CCAP n’est plus joint au dossier.",
        "Le CCAP n’a pas été fourni.",
        "Le CCAP pourra être fourni.",
    ],
)
def test_unresolved_negation_or_future_is_never_a_positive_provision(text):
    result = detect_document_announcements(text)
    assert result[0].claim == "AMBIGUOUS"


@pytest.mark.parametrize(
    "text",
    [
        "Le DCE comprend uniquement le CCAP, sans le CCTP.",
        "Le CCAP est joint conformément au CCTP.",
    ],
)
def test_excluded_or_referenced_families_do_not_inherit_a_positive_claim(text):
    result = detect_document_announcements(text)
    assert {item.document_family for item in result} == {"CCAP", "CCTP"}
    assert all(item.claim == "AMBIGUOUS" for item in result)


def test_plain_composition_list_keeps_its_candidate_signals():
    result = detect_document_announcements("Le DCE comprend le CCAP et le CCTP.")
    assert [(item.document_family, item.claim) for item in result] == [
        ("CCAP", "PROVIDED_SIGNAL"),
        ("CCTP", "PROVIDED_SIGNAL"),
    ]


def _reference_cases():
    import json
    from pathlib import Path

    fixture = Path(__file__).parents[2] / "fixtures" / "rc_document_announcements_v1.json"
    return json.loads(fixture.read_text())["cases"]


@pytest.mark.parametrize("case", _reference_cases(), ids=lambda case: case["id"])
def test_synthetic_reference_matrix(case):
    actual = detect_document_announcements(case["text"])
    assert [
        {
            "document_family": item.document_family,
            "claim": item.claim,
            "lot_numbers": list(item.lot_numbers),
        }
        for item in actual
    ] == case["expected"]
    for item in actual:
        assert (
            case["text"].encode()[item.start_byte_offset : item.end_byte_offset].decode()
            == item.excerpt
        )
        assert item.presence_status == item.applicability == item.criticality == "UNKNOWN"


def test_annex_noun_is_not_a_provision_verb():
    assert detect_document_announcements("L’annexe décrit les travaux.") == ()


@pytest.mark.parametrize(
    ("text", "claim"),
    [
        ("La DPGF est fournie pour le lot 2.", "PROVIDED_SIGNAL"),
        ("La DPGF n’est pas fournie.", "NOT_PROVIDED_SIGNAL"),
        ("L’annexe n’est pas jointe.", "NOT_PROVIDED_SIGNAL"),
        ("Les annexes sont jointes.", "PROVIDED_SIGNAL"),
    ],
)
def test_gender_and_plural_do_not_drop_document_claims(text, claim):
    result = detect_document_announcements(text)
    assert result[0].claim == claim


@pytest.mark.parametrize(
    "text",
    [
        "Le CCTP décrit le joint de dilatation.",
        "Les matériaux sont fournis conformément au CCAP.",
        "Matériaux fournis :\n- CCAP",
    ],
)
def test_construction_nouns_and_materials_are_not_document_announcements(text):
    assert detect_document_announcements(text) == ()


def test_offer_provision_is_not_asserted_as_dce_provision():
    result = detect_document_announcements("Le CCAP est joint à l’offre.")
    assert result[0].claim == "AMBIGUOUS"


def test_document_participle_without_auxiliary_still_has_a_source():
    result = detect_document_announcements("Le CCAP joint au dossier pour le lot 2.")
    assert result[0].claim == "PROVIDED_SIGNAL"


@pytest.mark.parametrize(
    "text",
    [
        "Le candidat doit fournir les matériaux conformes au CCTP.",
        "Documents à remettre :\n- preuve de conformité au CCAP",
    ],
)
def test_material_actions_and_normative_references_are_not_required_documents(text):
    assert detect_document_announcements(text) == ()


@pytest.mark.parametrize("family", ["CCAP", "CCTP"])
def test_continuation_recovers_list_with_distinct_utf8_anchors(family):
    from app.modules.dce.application import document_announcements as module

    previous = "Préambule.\n  Le DCE comprend les pièces suivantes :"
    text = f"- {family}\n- BPU\nNouvelle section\n- RC"
    scan = module.detect_document_announcement_continuation
    results = scan(previous, text)
    assert {item.document_family for item in results} == {family, "BPU"}
    item = next(item for item in results if item.document_family == family)
    assert item.claim == "PROVIDED_SIGNAL"
    assert text.encode()[item.start_byte_offset : item.end_byte_offset].decode() == family
    assert (
        previous.encode()[item.context_start_byte_offset : item.context_end_byte_offset].decode()
        == "Le DCE comprend les pièces suivantes :"
    )
    assert item.presence_status == item.applicability == item.criticality == "UNKNOWN"


@pytest.mark.parametrize(
    "previous,text",
    [
        ("Le DCE comprend les pièces suivantes :\nAutre section", "- CCAP"),
        ("Le DCE comprend les pièces suivantes :\n\n", "- CCAP"),
        ("Le DCE comprend les pièces suivantes :", "Introduction\n- CCAP"),
        ("Le DCE comprend les pièces suivantes :", "\n- CCAP"),
        ("Le DCE comprend les pièces suivantes :", "CCAP"),
        ("Références normatives :", "- CCAP"),
    ],
)
def test_continuation_refuses_textual_breaks(previous, text):
    from app.modules.dce.application import document_announcements as module

    scan = module.detect_document_announcement_continuation
    assert scan(previous, text) == ()


@pytest.mark.parametrize(
    "heading,claim,lots",
    [
        ("Le DCE ne comprend pas les pièces suivantes :", "NOT_PROVIDED_SIGNAL", ()),
        ("Documents à joindre pour le lot 2 :", "SUBMISSION_SIGNAL", (2,)),
        ("Le DCE comprend, sauf réserve, les pièces suivantes :", None, ()),
        ("Pièces à joindre si le candidat est retenu :", "AMBIGUOUS", ()),
    ],
)
def test_continuation_preserves_polarity_and_uncertainty(heading, claim, lots):
    from app.modules.dce.application.document_announcements import (
        detect_document_announcement_continuation,
    )

    items = detect_document_announcement_continuation(heading, "- CCAP")
    if claim is None:
        assert items == ()
    else:
        assert len(items) == 1
        assert items[0].claim == claim
        assert items[0].lot_numbers == lots


def test_continuation_stops_at_blank_line_and_does_not_reuse_an_old_list():
    from app.modules.dce.application.document_announcements import (
        detect_document_announcement_continuation,
    )

    assert (
        detect_document_announcement_continuation("Le DCE comprend :", "- CCAP\n\n- CCTP")[
            0
        ].document_family
        == "CCAP"
    )
    assert (
        len(detect_document_announcement_continuation("Le DCE comprend :", "- CCAP\n\n- CCTP")) == 1
    )
    assert detect_document_announcement_continuation("Le DCE comprend :\n- CCAP", "- CCTP") == ()


@pytest.mark.parametrize(
    "line",
    [
        "CCAP ne faisant pas partie du dossier",
        "CCAP non applicable au lot 2",
        "CCAP sans application au lot 2",
        "CCAP jamais requis au lot 2",
    ],
)
def test_continuation_never_overrides_unresolved_negation(line):
    from app.modules.dce.application.document_announcements import (
        detect_document_announcement_continuation,
    )

    items = detect_document_announcement_continuation("Le DCE comprend :", "- " + line)
    assert len(items) == 1
    assert items[0].claim == "AMBIGUOUS"
    assert items[0].lot_numbers == ()


@pytest.mark.parametrize(
    "texts,joins,expected",
    [
        (("Le DCE comprend :", "- CCAP", "- CCTP"), ("\n", "\n"), {"CCAP", "CCTP"}),
        (("Le DCE comprend :\n- CC", "AP\n- CCTP"), ("",), {"CCAP", "CCTP"}),
        (("Le DCE com", "prend :\n- CCAP"), ("",), {"CCAP"}),
        (("Préambule é.\nLe DCE comprend :", "- CCAP\n", "- CCTP"), ("\n", "\n"), {"CCAP"}),
        (("Le DCE comprend :", "- CCAP\nAutre section", "- CCTP"), ("\n", "\n"), {"CCAP"}),
    ],
)
def test_sequence_recovers_only_explicit_list_with_original_regions(texts, joins, expected):
    from app.modules.dce.application import document_announcements as module

    scan = module.detect_document_announcement_sequence
    items = scan(texts, joins)
    assert {x.announcement.document_family for x in items} == expected
    for item in items:
        source = "".join(
            texts[a.fragment_index].encode()[a.start_byte_offset : a.end_byte_offset].decode()
            for a in item.anchors
            if a.kind == "SOURCE"
        )
        context = "".join(
            texts[a.fragment_index].encode()[a.start_byte_offset : a.end_byte_offset].decode()
            for a in item.anchors
            if a.kind == "HEADING"
        )
        assert source == item.announcement.excerpt
        assert context == item.announcement.context_excerpt
        assert (
            item.announcement.presence_status
            == item.announcement.applicability
            == item.announcement.criticality
            == "UNKNOWN"
        )


def test_sequence_keeps_negations_across_three_pages():
    from app.modules.dce.application import document_announcements as module

    scan = module.detect_document_announcement_sequence
    items = scan(
        ("Documents fournis pour le lot 2 :", "- CCAP non applicable", "- CCTP"), ("\n", "\n")
    )
    assert len(items) == 2
    ccap = next(x for x in items if x.announcement.document_family == "CCAP")
    assert ccap.announcement.claim == "AMBIGUOUS"
    assert ccap.announcement.lot_numbers == ()
    cctp = next(x for x in items if x.announcement.document_family == "CCTP")
    assert {a.fragment_index for a in cctp.anchors} == {0, 1, 2}


def test_extraction_fragment_preserves_boundary_whitespace_and_its_hash():
    from hashlib import sha256

    from app.modules.dce.application.commands import DceExtractionFragmentInput

    text = "\n  ligne é\r\n "
    fragment = DceExtractionFragmentInput(
        ordinal=1,
        locator_json={"kind": "pdf_page", "page": 1, "part": 2},
        text=text,
        text_sha256=sha256(text.encode()).hexdigest(),
    )
    assert fragment.text == text
    assert sha256(fragment.text.encode()).hexdigest() == fragment.text_sha256


def test_sequence_rejects_invalid_links_and_limits(monkeypatch):
    from app.modules.dce.application import document_announcements as module

    with pytest.raises(ValueError, match="ANNOUNCEMENT_SEQUENCE_INVALID"):
        module.detect_document_announcement_sequence(("a", "b"), (" ",))
    with pytest.raises(ValueError, match="ANNOUNCEMENT_SEQUENCE_INVALID"):
        module.detect_document_announcement_sequence(("a", "b"), ())
    monkeypatch.setattr(module, "MAX_ANNOUNCEMENT_ANCHORS", 1)
    with pytest.raises(ValueError, match="ANNOUNCEMENT_LIMIT"):
        module.detect_document_announcement_sequence(("Le DCE comprend :", "- CCAP"), ("\n",))
    monkeypatch.setattr(module, "MAX_ANNOUNCEMENT_CHARS", 5)
    with pytest.raises(ValueError, match="ANNOUNCEMENT_LIMIT"):
        module.detect_document_announcement_sequence(("123", "456"), ("",))


@pytest.mark.parametrize("prefix", ["", "de "])
def test_object_gap_rejects_long_whitespace_without_backtracking(prefix):
    import signal

    from app.modules.dce.application.document_announcements import _OBJECT_GAP

    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.getitimer(signal.ITIMER_REAL)

    def timed_out(*_):
        raise AssertionError("Object gap exceeded the bounded parse budget")

    signal.signal(signal.SIGALRM, timed_out)
    signal.setitimer(signal.ITIMER_REAL, 2)
    try:
        assert _OBJECT_GAP.fullmatch(prefix + " " * 8000 + "X") is None
    finally:
        signal.setitimer(signal.ITIMER_REAL, *old_timer)
        signal.signal(signal.SIGALRM, old_handler)


def test_sequence_never_expands_the_proved_logical_line_budget():
    from app.modules.dce.application.document_announcements import (
        detect_document_announcement_sequence,
    )

    with pytest.raises(ValueError, match="ANNOUNCEMENT_LIMIT"):
        detect_document_announcement_sequence(("x" * 8000, "x"), ("",))
    items = detect_document_announcement_sequence(
        ("x" * 4000 + "\n", "x" * 4000 + "\nLe DCE comprend :\n- CCAP"), ("",)
    )
    assert len(items) == 1 and items[0].announcement.document_family == "CCAP"


@pytest.mark.parametrize(
    "texts,expected,lots",
    [
        (("Le DCE comprend :", "| CCAP | CCTP |"), ("CCAP", "CCTP"), ()),
        (
            ("Le DCE comprend :", "Composition du dossier — suite\n- CCAP", "- CCTP"),
            ("CCAP", "CCTP"),
            (),
        ),
        (("Le DCE comprend pour le lot 2 :", "- CCAP"), ("CCAP",), (2,)),
    ],
)
def test_residual_calibration_has_exact_source_and_context_regions(texts, expected, lots):
    from app.modules.dce.application.document_announcements import (
        detect_document_announcement_sequence,
    )

    items = detect_document_announcement_sequence(texts, ("\n",) * (len(texts) - 1))
    assert tuple(x.announcement.document_family for x in items) == expected
    for item in items:
        a = item.announcement
        assert a.claim == "PROVIDED_SIGNAL" and a.lot_numbers == lots
        assert a.presence_status == a.applicability == a.criticality == "UNKNOWN"
        for kind, excerpt in (("SOURCE", a.excerpt), ("HEADING", a.context_excerpt)):
            assert (
                "".join(
                    texts[r.fragment_index]
                    .encode()[r.start_byte_offset : r.end_byte_offset]
                    .decode()
                    for r in item.anchors
                    if r.kind == kind
                )
                == excerpt
            )
        if texts[1].startswith("|"):
            assert a.excerpt == a.document_family


@pytest.mark.parametrize(
    "tail",
    [
        "Composition du dossier — suite pour le lot 3\n- CCAP",
        "Composition du dossier — suite sans CCAP\n- CCTP",
        "\nComposition du dossier — suite\n- CCAP",
        "Autre section\nComposition du dossier — suite\n- CCAP",
        "| CCAP | non fourni |\n- CCTP",
        "| CCAP | lot 3 |\n- CCTP",
        "| CCAP | |\n- CCTP",
        "| CCAP | référence CCTP |\n- BPU",
    ],
)
def test_new_layouts_never_bridge_ambiguous_cells_or_captions(tail):
    assert detect_document_announcements("Le DCE comprend pour le lot 2 :\n" + tail) == ()


def test_caption_cannot_create_a_heading_without_antecedent():
    assert detect_document_announcements("Composition du dossier — suite\n- CCAP") == ()


def test_heading_and_local_lot_disagreement_is_not_resolved_by_guessing():
    items = detect_document_announcements("Le DCE comprend pour le lot 2 :\n- CCAP pour le lot 3")
    assert len(items) == 1
    assert items[0].claim == "AMBIGUOUS" and items[0].lot_numbers == ()


def test_table_retains_negative_heading_without_inferring_presence():
    items = detect_document_announcements("Le DCE ne comprend pas :\n| CCAP | CCTP |")
    assert len(items) == 2
    assert all(x.claim == "NOT_PROVIDED_SIGNAL" and x.presence_status == "UNKNOWN" for x in items)


@pytest.mark.parametrize("scope", ["pour les lots 2 et 3", "pour le lot 2 ou 3"])
def test_unclear_local_lot_cannot_inherit_scoped_heading(scope):
    items = detect_document_announcements("Le DCE comprend pour le lot 2 :\n- CCAP " + scope)
    assert len(items) == 1
    assert items[0].claim == "AMBIGUOUS" and items[0].lot_numbers == ()


def test_table_byte_regions_survive_utf8_and_exact_chunk_split():
    from app.modules.dce.application.document_announcements import (
        detect_document_announcement_sequence,
    )

    texts = ("Préambule é.\nLe DCE comprend :\r\n| CC", "AP | CCTP |")
    items = detect_document_announcement_sequence(texts, ("",))
    assert len(items) == 2
    for item in items:
        assert (
            "".join(
                texts[a.fragment_index].encode()[a.start_byte_offset : a.end_byte_offset].decode()
                for a in item.anchors
                if a.kind == "SOURCE"
            )
            == item.announcement.document_family
        )


def test_continued_caption_rejects_long_whitespace_with_bounded_cost():
    import signal

    from app.modules.dce.application.document_announcements import _CONTINUED_CAPTION

    handler = signal.getsignal(signal.SIGALRM)
    timer = signal.getitimer(signal.ITIMER_REAL)

    def timed_out(*_):
        raise AssertionError("Continued caption exceeded the bounded parse budget")

    signal.signal(signal.SIGALRM, timed_out)
    signal.setitimer(signal.ITIMER_REAL, 2)
    try:
        assert (
            _CONTINUED_CAPTION.fullmatch("Composition du dossier — suite" + " " * 50000 + "X")
            is None
        )
    finally:
        signal.setitimer(signal.ITIMER_REAL, *timer)
        signal.signal(signal.SIGALRM, handler)
