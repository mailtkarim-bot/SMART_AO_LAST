from dataclasses import replace
from importlib import import_module
from importlib.util import find_spec
from typing import Any, cast
from uuid import UUID

import pytest


def api() -> Any:
    name = "app.modules.dce.application.structure_projection"
    assert find_spec(name) is not None, "candidate structured projection is missing"
    return cast(Any, import_module(name))


def scope():
    return api().StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, "b" * 64, 1, 100, 200
    )


def token(name, text, box, context=None):
    m = api()
    return m.RegionToken(name, text, m.RegionAnchor(context or scope(), box))


def cell(name, box):
    m = api()
    return m.RegionCell(name, m.RegionAnchor(scope(), box))


def run(tokens=(), cells=(), diagrams=(), arrow_traces=()):
    return api().project_candidate_structure(
        expected_scope=scope(),
        tokens=tuple(tokens),
        cells=tuple(cells),
        diagram_regions=tuple(diagrams),
        arrow_traces=tuple(arrow_traces),
    )


def test_negated_outcome_keeps_both_source_regions_and_no_business_eligibility():
    result = run(
        [token("negative", "NON", (10, 20, 40, 30)), token("outcome", "ELIGIBLE", (10, 31, 50, 41))]
    )
    assert len(result.nodes) == 1
    assert result.nodes[0].text == "NON ELIGIBLE"
    assert set(result.nodes[0].token_ids) == {"negative", "outcome"}
    assert result.nodes[0].polarity == "NEGATED_CANDIDATE"
    assert result.status == "REVIEW_REQUIRED"
    assert result.business_eligibility == "UNKNOWN"
    assert result.admission_granted is False


def test_ambiguous_negation_never_becomes_a_positive_outcome():
    result = run(
        [
            token("n1", "NON", (10, 20, 40, 30)),
            token("n2", "NON", (11, 20, 41, 30)),
            token("e", "ELIGIBLE", (10, 31, 50, 41)),
        ]
    )
    assert all(n.polarity == "UNKNOWN" for n in result.nodes)
    assert result.business_eligibility == "UNKNOWN"


def test_cells_keep_raw_text_and_unknown_value_without_inventing_rows_or_zero():
    result = run(
        [token("price", "Prix de test", (10, 20, 35, 30)), token("weight", "55", (60, 20, 70, 30))],
        [
            cell("label", (5, 15, 40, 40)),
            cell("value", (50, 15, 90, 40)),
            cell("blank", (5, 50, 40, 70)),
        ],
    )
    assert result.cells[0].value is None
    assert all(
        c.value_state == "UNKNOWN" and c.row is None and c.column is None for c in result.cells
    )
    assert any(c.text == "55" for c in result.cells)
    assert any(c.text is None and c.state == "UNKNOWN" for c in result.cells)
    assert all(r.semantic_state == "UNKNOWN" for r in result.relations)
    assert result.lot_applicability == "UNKNOWN"


def test_crossing_or_ambiguous_cell_never_assigns_a_value():
    result = run(
        [token("crossing", "1600", (20, 20, 70, 30))],
        [cell("one", (10, 10, 50, 50)), cell("two", (50, 10, 90, 50))],
    )
    assert all(c.text is None and c.state == "UNKNOWN" for c in result.cells)


def test_diagram_relationship_is_explicit_unknown_without_direction_evidence():
    result = run(
        [token("node", "Moteur de test?", (10, 20, 60, 40))],
        diagrams=[api().RegionAnchor(scope(), (0, 0, 100, 100))],
    )
    assert any(
        r.kind == "DIAGRAM_EDGE"
        and r.semantic_state == "UNKNOWN"
        and r.source_ids == ()
        and r.target_ids == ()
        for r in result.relations
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", UUID(int=9)),
        ("document_id", UUID(int=9)),
        ("version_id", UUID(int=9)),
        ("page", 2),
        ("source_sha256", "c" * 64),
        ("render_sha256", "c" * 64),
    ],
)
def test_foreign_or_stale_region_is_rejected_without_observing_its_content(field, value):
    with pytest.raises(ValueError, match="STRUCTURE_SCOPE_MISMATCH"):
        run(
            [
                token(
                    "foreign",
                    "foreign confidential label",
                    (0, 0, 20, 20),
                    replace(scope(), **{field: value}),
                )
            ]
        )


@pytest.mark.parametrize(
    "box", [(-1, 0, 10, 10), (0, 0, 101, 10), (10, 0, 5, 10), (0, 0, float("nan"), 10)]
)
def test_invalid_or_unbounded_geometry_is_rejected(box):
    with pytest.raises(ValueError, match="STRUCTURE_REGION_INVALID"):
        run([token("invalid", "label", box)])


def test_retry_identity_is_stable_under_input_permutation_and_version_bound():
    labels = [token("a", "label", (0, 0, 10, 10)), token("b", "second", (20, 0, 40, 10))]
    assert run(labels).input_sha256 == run(reversed(labels)).input_sha256
    assert run(labels) == run(labels)


def test_duplicate_ids_are_rejected():
    with pytest.raises(ValueError, match="STRUCTURE_IDENTIFIER_DUPLICATE"):
        run([token("same", "one", (0, 0, 10, 10)), token("same", "two", (20, 0, 30, 10))])


def test_partial_overlapping_text_keeps_the_entire_cell_unknown():
    result = run(
        [token("full", "55", (10, 20, 30, 30)), token("partial", "not complete", (20, 35, 70, 45))],
        [cell("one", (5, 15, 50, 50))],
    )
    assert result.cells[0].state == "UNKNOWN" and result.cells[0].text is None


def test_parent_region_does_not_join_negation_across_distinct_cells():
    result = run(
        [token("n", "NON", (10, 20, 40, 30)), token("e", "ELIGIBLE", (10, 31, 50, 41))],
        [
            cell("parent", (0, 0, 100, 100)),
            cell("top", (5, 15, 60, 30)),
            cell("bottom", (5, 31, 60, 45)),
        ],
    )
    assert len(result.nodes) == 2 and all(n.polarity == "UNKNOWN" for n in result.nodes)


def test_regions_are_bounded_before_pairing_work():
    with pytest.raises(ValueError, match="STRUCTURE_LIMIT"):
        run([token(str(n), "NON", (0, 0, 10, 10)) for n in range(513)])


def test_mutable_region_coordinates_are_rejected():
    with pytest.raises(ValueError, match="STRUCTURE_REGION_INVALID"):
        run([token("mutable", "label", [0, 0, 10, 10])])


@pytest.mark.parametrize(
    "field,value", [("page", True), ("width", 0), ("source_sha256", "not-a-hash")]
)
def test_invalid_expected_scope_is_rejected(field, value):
    with pytest.raises(ValueError, match="STRUCTURE_SCOPE_INVALID"):
        api().project_candidate_structure(
            expected_scope=replace(scope(), **{field: value}), tokens=()
        )


def test_multiple_common_containers_do_not_resolve_a_negation():
    result = run(
        [token("n", "NON", (10, 20, 40, 30)), token("e", "ELIGIBLE", (10, 31, 50, 41))],
        [cell("a", (0, 0, 100, 100)), cell("b", (0, 0, 100, 100))],
    )
    assert len(result.nodes) == 2 and all(n.polarity == "UNKNOWN" for n in result.nodes)


def test_manifest_changes_with_version_and_render_but_not_cell_order():
    m = api()
    labels = [token("a", "label", (10, 20, 30, 30))]
    cells = [cell("a-cell", (0, 0, 50, 50)), cell("b-cell", (60, 60, 90, 90))]
    assert run(labels, cells).input_sha256 == run(labels, reversed(cells)).input_sha256
    for field, value in [("version_id", UUID(int=9)), ("render_sha256", "c" * 64)]:
        changed = replace(scope(), **{field: value})
        t = m.RegionToken("a", "label", m.RegionAnchor(changed, (10, 20, 30, 30)))
        assert (
            m.project_candidate_structure(expected_scope=changed, tokens=(t,)).input_sha256
            != run(labels).input_sha256
        )


def test_token_and_cell_namespace_collision_is_rejected():
    with pytest.raises(ValueError, match="STRUCTURE_IDENTIFIER_DUPLICATE"):
        run([token("same", "label", (10, 20, 30, 30))], [cell("same", (0, 0, 50, 50))])


def test_text_limit_is_enforced():
    with pytest.raises(ValueError, match="STRUCTURE_TEXT_LIMIT"):
        run([token("a", "x" * 1001, (0, 0, 10, 10))])


def test_extreme_integer_coordinate_is_rejected_as_a_region_error():
    with pytest.raises(ValueError, match="STRUCTURE_REGION_INVALID"):
        run([token("a", "label", (0, 0, 10**1000, 10))])


def test_arrow_path_keeps_yes_no_endpoints_order_and_raw_context_labels():
    labels = [
        token("yes", "OUI", (19, 19, 25, 24)),
        token("condition", "Condition existante?", (10, 25, 55, 36)),
        token("no", "NON ELIGIBLE", (36, 59, 55, 70)),
    ]
    trace = arrow()
    result = api().project_candidate_structure(
        expected_scope=scope(), tokens=tuple(labels), arrow_traces=(trace,)
    )
    path = next(r for r in result.relations if r.kind == "ARROW_PATH_CANDIDATE")
    assert (
        path.source_ids == ("yes",)
        and path.target_ids == ("no",)
        and path.context_ids == ("condition",)
    )
    assert path.path == trace.polyline and path.arrowhead_tip == trace.arrowhead_tip
    assert (
        path.semantic_state == "UNKNOWN"
        and result.business_eligibility == "UNKNOWN"
        and not result.admission_granted
    )


def test_arrow_without_a_directional_tip_is_rejected():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_INVALID"):
        api().project_candidate_structure(
            expected_scope=scope(),
            tokens=arrow_tokens(),
            arrow_traces=(arrow(arrowhead_tip=(40, 61)),),
        )


def test_arrow_tip_outside_target_anchor_is_rejected():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_ENDPOINT_REQUIRED"):
        api().project_candidate_structure(
            expected_scope=scope(),
            tokens=arrow_tokens(),
            arrow_traces=(arrow(arrowhead_tip=(0, 60), polyline=((20, 20), (0, 60))),),
        )


def test_arrow_path_scope_mismatch_is_rejected():
    m = api()
    other = replace(scope(), page=2)
    with pytest.raises(ValueError, match="STRUCTURE_SCOPE_MISMATCH"):
        m.project_candidate_structure(
            expected_scope=scope(), tokens=(), arrow_traces=(arrow(scope_value=other),)
        )


def test_ambiguous_endpoint_ids_are_never_guessed():
    m = api()
    labels = (
        token("yes", "OUI", (19, 19, 25, 24)),
        token("yes2", "OUI", (19, 19, 25, 24)),
        token("no", "NON", (36, 59, 55, 70)),
    )
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_AMBIGUOUS"):
        m.project_candidate_structure(
            expected_scope=scope(),
            tokens=labels,
            arrow_traces=(arrow(source_ids=("yes", "yes2")),),
        )


def test_arrow_candidate_requires_bounded_path_and_page_region():
    m = api()
    labels = arrow_tokens()
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_INVALID"):
        m.project_candidate_structure(
            expected_scope=scope(), tokens=labels, arrow_traces=(arrow(polyline=((20, 20),)),)
        )


def test_arrow_evidence_hash_and_detector_are_pinned():
    m = api()
    labels = arrow_tokens()
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_EVIDENCE_REQUIRED"):
        m.project_candidate_structure(
            expected_scope=scope(),
            tokens=labels,
            arrow_traces=(arrow(evidence_sha256="bad"),),
        )


def test_ordered_arrow_path_is_bound_to_labels_and_render_but_semantics_stay_unknown():
    m = api()
    result = m.project_candidate_structure(
        expected_scope=scope(), tokens=arrow_tokens(), arrow_traces=(arrow(),)
    )
    relation = next(r for r in result.relations if r.kind == "ARROW_PATH_CANDIDATE")
    assert (
        relation.source_ids == ("yes",)
        and relation.target_ids == ("no",)
        and relation.context_ids == ("condition",)
    )
    assert (
        relation.path == ((20, 20), (40, 20), (40, 60))
        and relation.detector_id == "opencv-houghlinesp-candidate"
    )
    assert (
        relation.semantic_state == "UNKNOWN"
        and result.business_eligibility == "UNKNOWN"
        and not result.admission_granted
    )


def test_arrow_path_preserves_a_negated_destination_as_raw_label_ids():
    m = api()
    labels = (
        token("yes", "OUI", (19, 19, 25, 24)),
        token("non", "NON", (36, 59, 45, 64)),
        token("eligible", "ELIGIBLE", (36, 65, 55, 70)),
    )
    trace = arrow(
        source_ids=("yes",),
        target_ids=("non", "eligible"),
        context_ids=(),
        evidence_region=m.RegionAnchor(scope(), (0, 0, 60, 80)),
    )
    result = m.project_candidate_structure(
        expected_scope=scope(), tokens=labels, arrow_traces=(trace,)
    )
    relation = next(r for r in result.relations if r.kind == "ARROW_PATH_CANDIDATE")
    assert relation.target_ids == ("non", "eligible") and result.business_eligibility == "UNKNOWN"


def test_arrow_tip_must_point_inside_target_label_region():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_ENDPOINT_REQUIRED"):
        run(
            arrow_traces=(arrow(polyline=((20, 20), (0, 60)), arrowhead_tip=(0, 60)),),
            tokens=arrow_tokens(),
        )


def test_reversed_path_fails_endpoint_validation():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_ENDPOINT_REQUIRED"):
        run(
            arrow_traces=(arrow(polyline=((40, 60), (40, 20), (20, 20)), arrowhead_tip=(20, 20)),),
            tokens=arrow_tokens(),
        )


def test_foreign_render_or_detector_evidence_is_rejected():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_EVIDENCE_REQUIRED"):
        run(arrow_traces=(arrow(evidence_sha256="d" * 64),), tokens=arrow_tokens())


def test_trace_and_source_identifiers_must_be_unambiguous():
    labels = arrow_tokens()
    duplicate = token("yes-alias", "OUI", (19, 19, 25, 24))
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_AMBIGUOUS"):
        run(arrow_traces=(arrow(source_ids=("yes", "yes-alias")),), tokens=labels + (duplicate,))
    with pytest.raises(ValueError, match="STRUCTURE_IDENTIFIER_DUPLICATE"):
        run(arrow_traces=(arrow(), arrow(trace_id="arrow-1")), tokens=labels)


def arrow(scope_value=None, **changes):
    m = api()
    scope_value = scope_value or scope()
    values = {
        "trace_id": "arrow-1",
        "scope": scope_value,
        "source_ids": ("yes",),
        "target_ids": ("no",),
        "context_ids": ("condition",),
        "polyline": ((20, 20), (40, 20), (40, 60)),
        "arrowhead_tip": (40, 60),
        "evidence_region": m.RegionAnchor(scope_value, (0, 0, 60, 80)),
        "detector_id": "opencv-houghlinesp-candidate",
        "detector_version": "1",
        "evidence_sha256": scope_value.render_sha256,
        "render_sha256": scope_value.render_sha256,
    }
    values.update(changes)
    return m.ArrowPathEvidence(**values)


def arrow_tokens():
    return (
        token("yes", "OUI", (19, 19, 25, 24)),
        token("condition", "Condition existante ?", (27, 15, 42, 35)),
        token("no", "NON ELIGIBLE", (36, 59, 55, 70)),
    )


def test_arrow_path_keeps_ordered_anchored_labels_and_business_unknown():
    m = api()
    result = m.project_candidate_structure(
        expected_scope=scope(), tokens=arrow_tokens(), arrow_traces=(arrow(),)
    )
    r = next(r for r in result.relations if r.kind == "ARROW_PATH_CANDIDATE")
    assert r.source_ids == ("yes",) and r.target_ids == ("no",) and r.context_ids == ("condition",)
    assert (
        r.path == ((20, 20), (40, 20), (40, 60)) and r.detector_id == "opencv-houghlinesp-candidate"
    )
    assert (
        r.path_state == "SOURCE_PATH_CANDIDATE"
        and r.semantic_state == "UNKNOWN"
        and result.business_eligibility == "UNKNOWN"
        and not result.admission_granted
    )


def test_negative_target_preserves_separate_ocr_fragments():
    m = api()
    labels = (
        token("yes", "OUI", (19, 19, 25, 24)),
        token("non", "NON", (36, 59, 45, 64)),
        token("eligible", "ELIGIBLE", (36, 65, 55, 70)),
    )
    trace = arrow(source_ids=("yes",), target_ids=("non", "eligible"), context_ids=())
    result = m.project_candidate_structure(
        expected_scope=scope(), tokens=labels, arrow_traces=(trace,)
    )
    assert next(r for r in result.relations if r.kind == "ARROW_PATH_CANDIDATE").target_ids == (
        "non",
        "eligible",
    )
    assert result.business_eligibility == "UNKNOWN"


@pytest.mark.parametrize(
    "change",
    [
        {"arrowhead_tip": (90, 90), "polyline": ((20, 20), (90, 90))},
        {"arrowhead_tip": (60, 30)},
        {"polyline": ((20, 20),)},
        {"polyline": ((20, 20), (40, 20), (40, 80))},
        {"evidence_region": api().RegionAnchor(scope(), (0, 0, 100, 100))},
        {"detector_version": "999"},
        {"evidence_sha256": "bad"},
    ],
)
def test_invalid_arrow_path_evidence_is_rejected(change):
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_"):
        run(arrow_traces=(arrow(**change),), tokens=arrow_tokens())


def test_arrow_endpoint_ids_and_trace_ids_are_unambiguous():
    labels = arrow_tokens() + (token("yes-alias", "OUI", (19, 19, 25, 24)),)
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_AMBIGUOUS"):
        run(arrow_traces=(arrow(source_ids=("yes", "yes-alias")),), tokens=labels)
    with pytest.raises(ValueError, match="STRUCTURE_IDENTIFIER_DUPLICATE"):
        run(arrow_traces=(arrow(), arrow()), tokens=arrow_tokens())


def test_two_different_paths_for_the_same_labels_remain_ambiguous():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_AMBIGUOUS"):
        run(
            arrow_traces=(
                arrow(trace_id="path-a"),
                arrow(trace_id="path-b", polyline=((20, 20), (30, 30), (40, 60))),
            ),
            tokens=arrow_tokens(),
        )


def test_multiple_render_paths_for_the_same_labels_refuse_to_guess():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_AMBIGUOUS"):
        run(
            arrow_traces=(
                arrow(trace_id="path-a"),
                arrow(trace_id="path-b", polyline=((20, 20), (30, 30), (40, 60))),
            ),
            tokens=arrow_tokens(),
        )


def test_arrow_evidence_version_is_in_the_manifest():
    result = run(tokens=arrow_tokens(), arrow_traces=(arrow(),))
    assert result.projector_version == "2"


def test_reordered_endpoint_ids_cannot_duplicate_an_arrow():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_AMBIGUOUS"):
        run(
            tokens=arrow_tokens(),
            arrow_traces=(
                arrow(trace_id="path-a", source_ids=("yes", "condition"), context_ids=()),
                arrow(trace_id="path-b", source_ids=("condition", "yes"), context_ids=()),
            ),
        )


def test_zero_length_polyline_is_not_a_path_candidate():
    with pytest.raises(ValueError, match="STRUCTURE_ARROW_INVALID"):
        run(
            tokens=arrow_tokens(),
            arrow_traces=(arrow(polyline=((40, 40), (40, 40)), arrowhead_tip=(40, 40)),),
        )
