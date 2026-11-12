from dataclasses import replace
from importlib import import_module
from importlib.util import find_spec
from uuid import UUID

import pytest
from app.modules.dce.application.conditional_diagram import ConditionalNode
from app.modules.dce.application.diagram_evidence import ArrowheadEvidence, qualify_branch_label
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
)


def api():
    name = "app.modules.dce.application.discovered_diagram"
    assert find_spec(name), "discovered diagram decoder missing"
    return import_module(name)


def case():
    m = api()
    s = StructureScope(UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, "b" * 64, 42, 1000, 1000)
    specs = [
        ("existing", "ENTRY", (350, 50, 490, 100), "Moteur existant?"),
        ("new", "ENTRY", (700, 50, 840, 100), "Moteur neuf?"),
        ("equipped", "CONDITION", (350, 200, 490, 250), "Variateur déjà présent?"),
        ("async", "CONDITION", (500, 350, 640, 400), "Moteur asynchrone?"),
        ("ie2", "CONDITION", (400, 550, 520, 600), "Le moteur est de classe IE2"),
        ("ie34", "CONDITION", (650, 550, 800, 600), "Le moteur est de classe IE3 ou IE4"),
        ("no", "OUTCOME", (70, 800, 220, 850), "NON ELIGIBLE"),
        ("contact", "OUTCOME", (390, 800, 530, 850), "Contacter votre correspondant CEE centre"),
        ("yes", "OUTCOME", (650, 800, 800, 850), "ELIGIBLE"),
        ("inlet", "JUNCTION", (560, 220, 570, 230), ""),
        ("reject", "JUNCTION", (140, 370, 150, 380), ""),
        ("split", "JUNCTION", (560, 470, 570, 480), ""),
    ]
    tokens = []
    nodes = []
    for name, kind, box, text in specs:
        anchor = RegionAnchor(s, box)
        ids = ()
        if text:
            ids = (f"t-{name}",)
            tokens.append(RegionToken(ids[0], text, anchor))
        nodes.append(
            ConditionalNode(
                name,
                kind,
                anchor,
                ids,
                junction_state="SOURCE_JUNCTION_CANDIDATE" if kind == "JUNCTION" else None,
                text_state="SOURCE_TEXT_CANDIDATE" if text else None,
            )
        )
    rows = [
        ("r1", "existing", "equipped", ((420, 100), (420, 195)), True),
        ("r2", "new", "inlet", ((770, 100), (770, 225), (565, 225)), False),
        ("r3", "equipped", "inlet", ((490, 225), (565, 225)), False),
        ("r4", "inlet", "async", ((565, 225), (565, 345)), True),
        ("r5", "equipped", "reject", ((350, 225), (145, 225), (145, 375)), False),
        ("r6", "async", "reject", ((500, 375), (145, 375)), False),
        ("r7", "reject", "no", ((145, 375), (145, 795)), True),
        ("r8", "async", "split", ((565, 400), (565, 475)), False),
        ("r9", "split", "ie2", ((565, 475), (460, 475), (460, 545)), True),
        ("r10", "split", "ie34", ((565, 475), (725, 475), (725, 545)), True),
        ("r11", "ie2", "contact", ((460, 600), (460, 795)), True),
        ("r12", "ie34", "yes", ((725, 600), (725, 795)), True),
    ]
    routes = []
    for rid, a, b, path, head in rows:
        h = (
            ArrowheadEvidence(
                s,
                "PIXEL_HEAD_CANDIDATE",
                path[-1],
                RegionAnchor(
                    s, (path[-1][0] - 4, path[-1][1] - 8, path[-1][0] + 4, path[-1][1] + 1)
                ),
            )
            if head
            else None
        )
        if a > b:
            a, b = b, a
            path = tuple(reversed(path))
        routes.append(
            m.DiscoveredRoute(
                rid,
                (a, b),
                RegionAnchor(s, (0, 0, 999, 999)),
                path,
                "SOURCE_PATH_CANDIDATE",
                (h,) if h else (),
            )
        )
    labels = []
    for rid, text, box in [
        ("r2", "OUI", (750, 150, 765, 169)),
        ("r3", "NON", (510, 209, 533, 220)),
        ("r5", "OUI", (270, 209, 293, 220)),
        ("r6", "NON", (320, 355, 343, 370)),
        ("r8", "OUI", (580, 425, 603, 446)),
    ]:
        t = RegionToken(f"label-{rid}", text, RegionAnchor(s, box))
        tokens.append(t)
        labels.append(qualify_branch_label(expected_scope=s, raw_token=t))
    return dict(
        expected_scope=s,
        nodes=tuple(nodes),
        tokens=tuple(tokens),
        routes=tuple(routes),
        labels=tuple(labels),
    )


def run(**changes):
    d = case()
    d.update(changes)
    return api().reconstruct_discovered_diagram(**d)


def test_seven_paths_are_rebuilt_without_expected_relations_or_paths():
    r = run()
    assert len(r.assembly.paths) == 7
    assert r.unresolved_routes == () and r.unassigned_labels == ()
    assert sum(d.direction_state == "PIXEL_DIRECTION_CANDIDATE" for d in r.decisions) == 7
    assert sum(d.direction_state == "QUESTION_PORT_DIRECTION_CANDIDATE" for d in r.decisions) == 5
    assert sorted(p.document_outcome for p in r.assembly.paths) == sorted(
        ["DOCUMENT_NON_ELIGIBLE_CEE"] * 3
        + ["CONTACT_CEE_CORRESPONDENT"] * 2
        + ["DOCUMENT_ELIGIBLE_CEE"] * 2
    )
    assert (
        r.status == "REVIEW_REQUIRED"
        and r.business_eligibility == "UNKNOWN"
        and not r.admission_granted
    )


def test_reversed_input_order_does_not_supply_an_arrow_direction():
    d = case()
    routes = tuple(
        replace(v, endpoint_ids=tuple(reversed(v.endpoint_ids)), path=tuple(reversed(v.path)))
        for v in reversed(d["routes"])
    )
    assert (
        run(
            routes=routes,
            nodes=tuple(reversed(d["nodes"])),
            tokens=tuple(reversed(d["tokens"])),
            labels=tuple(reversed(d["labels"])),
        )
        == run()
    )


def test_conflicting_heads_cannot_be_overridden_by_a_label():
    d = case()
    r = d["routes"][0]
    p = r.path[0] if r.heads[0].tip == r.path[-1] else r.path[-1]
    h = replace(
        r.heads[0],
        tip=p,
        anchor=RegionAnchor(d["expected_scope"], (p[0] - 4, p[1] - 8, p[0] + 4, p[1] + 1)),
    )
    result = run(routes=(replace(r, heads=r.heads + (h,)),) + d["routes"][1:])
    assert "r1" in result.unresolved_routes


def test_unreadable_label_never_orients_a_question_port():
    d = case()
    old = d["labels"][-1].raw_token
    raw = replace(old, text="Iño")
    labels = d["labels"][:-1] + (
        qualify_branch_label(expected_scope=d["expected_scope"], raw_token=raw),
    )
    r = run(
        tokens=tuple(raw if t.token_id == raw.token_id else t for t in d["tokens"]), labels=labels
    )
    assert "r8" in r.unresolved_routes
    assert all(p.state == "UNKNOWN" or "split" not in p.node_ids for p in r.assembly.paths)


def test_label_candidates_on_two_routes_remain_ambiguous():
    d = case()
    duplicate = replace(d["routes"][2], route_id="duplicate")
    r = run(routes=d["routes"] + (duplicate,))
    assert "r3" in r.unresolved_routes and "duplicate" in r.unresolved_routes


def test_outcome_words_are_not_boolean_branch_answers():
    d = case()
    old = d["labels"][0].raw_token
    raw = replace(old, text="ELIGIBLE")
    labels = (qualify_branch_label(expected_scope=d["expected_scope"], raw_token=raw),) + d[
        "labels"
    ][1:]
    assert (
        "r2"
        in run(
            tokens=tuple(raw if t.token_id == raw.token_id else t for t in d["tokens"]),
            labels=labels,
        ).unresolved_routes
    )


def test_foreign_head_scope_is_rejected_before_results():
    d = case()
    r = d["routes"][0]
    h = replace(r.heads[0], scope=replace(d["expected_scope"], tenant_id=UUID(int=99)))
    with pytest.raises(ValueError, match="STRUCTURE_SCOPE_MISMATCH"):
        run(routes=(replace(r, heads=(h,)),) + d["routes"][1:])


def test_unknown_island_is_preserved_without_inventing_nodes():
    d = case()
    r = replace(
        d["routes"][0],
        route_id="island",
        endpoint_ids=("dangling-a", "dangling-b"),
        heads=(),
        geometry_state="UNKNOWN",
    )
    result = run(routes=d["routes"] + (r,))
    assert "island" in result.unresolved_routes and len(result.assembly.paths) == 7


def test_raw_labels_and_direction_proofs_survive_reconstruction():
    r = run()
    assert r.decisions[0].route.heads
    assert len(r.labels) == 5 and r.assembly.scope == r.scope
    assert all(p.semantic_state == "UNKNOWN" for p in r.assembly.paths)


def test_unknown_geometry_cannot_be_promoted_by_a_head():
    d = case()
    routes = (replace(d["routes"][0], geometry_state="UNKNOWN"),) + d["routes"][1:]
    assert "r1" in run(routes=routes).unresolved_routes


def test_unknown_incoming_route_cannot_turn_downstream_node_into_a_clean_root():
    d = case()
    nodes = tuple(replace(n, kind="ENTRY") if n.node_id == "async" else n for n in d["nodes"])
    routes = tuple(
        replace(r, geometry_state="UNKNOWN") if r.route_id == "r4" else r for r in d["routes"]
    )
    result = run(nodes=nodes, routes=routes)
    assert "async" in result.assembly.unqualified_nodes
    assert all(p.state == "UNKNOWN" for p in result.assembly.paths if p.node_ids[0] == "async")
    assert (
        next(n for n in result.source_nodes if n.node_id == "async").text_state
        == "SOURCE_TEXT_CANDIDATE"
    )


def test_uncertain_question_branch_marks_its_affected_paths_unknown():
    d = case()
    routes = tuple(
        replace(r, geometry_state="UNKNOWN") if r.route_id == "r8" else r for r in d["routes"]
    )
    result = run(routes=routes)
    assert "async" in result.assembly.unqualified_nodes
    assert all(p.state == "UNKNOWN" for p in result.assembly.paths if "async" in p.node_ids)


def test_punctuation_only_caption_is_not_a_qualified_question_port():
    d = case()
    tokens = tuple(replace(t, text="???") if t.token_id == "t-async" else t for t in d["tokens"])
    assert "r8" in run(tokens=tokens).unresolved_routes


def test_forged_label_verdict_is_refused():
    d = case()
    label = replace(d["labels"][0], label="NON")
    with pytest.raises(ValueError, match="DISCOVERED_LABEL_INVALID"):
        run(labels=(label,) + d["labels"][1:])


def test_unknown_detector_version_cannot_qualify_an_arrow():
    d = case()
    r = d["routes"][0]
    h = replace(r.heads[0], detector_version="uncalibrated")
    with pytest.raises(ValueError, match="DISCOVERED_HEAD_INVALID"):
        run(routes=(replace(r, heads=(h,)),) + d["routes"][1:])


def test_input_route_count_is_bounded():
    d = case()
    with pytest.raises(ValueError, match="DISCOVERED_DIAGRAM_LIMIT"):
        run(routes=tuple(replace(d["routes"][0], route_id=f"extra-{i}") for i in range(129)))


def test_raw_route_points_must_stay_inside_their_source_anchor():
    d = case()
    r = replace(d["routes"][0], path=((-1, 20), (420, 195)))
    with pytest.raises(ValueError, match="DISCOVERED_ROUTE_INVALID"):
        run(routes=(r,) + d["routes"][1:])


def test_a_derived_cycle_is_refused_even_outside_the_entry_component():
    d = case()
    s = d["expected_scope"]
    extra_nodes = tuple(
        ConditionalNode(
            f"cycle-{i}",
            "JUNCTION",
            RegionAnchor(s, (x, y, x + 2, y + 2)),
            junction_state="SOURCE_JUNCTION_CANDIDATE",
        )
        for i, (x, y) in enumerate(((50, 30), (150, 30), (150, 80)))
    )
    points = ((50, 30), (150, 30), (150, 80))
    routes = []
    for i in range(3):
        a, b = points[i], points[(i + 1) % 3]
        head = ArrowheadEvidence(
            s, "PIXEL_HEAD_CANDIDATE", b, RegionAnchor(s, (b[0] - 1, b[1] - 1, b[0] + 1, b[1] + 1))
        )
        routes.append(
            api().DiscoveredRoute(
                f"cycle-route-{i}",
                (f"cycle-{i}", f"cycle-{(i + 1) % 3}"),
                RegionAnchor(s, (0, 0, 999, 999)),
                (a, b),
                "SOURCE_PATH_CANDIDATE",
                (head,),
            )
        )
    with pytest.raises(ValueError, match="DIAGRAM_CYCLE"):
        run(nodes=d["nodes"] + extra_nodes, routes=d["routes"] + tuple(routes))


def test_entries_are_derived_from_directed_routes_without_supplied_entry_roles():
    d = case()
    d["nodes"] = tuple(replace(n, kind="CONDITION") if n.kind == "ENTRY" else n for n in d["nodes"])
    r = api().reconstruct_discovered_diagram(**d)
    assert len([p for p in r.assembly.paths if p.state == "SOURCE_CONDITIONAL_PATH_CANDIDATE"]) == 7
    assert {n.node_id for n in r.assembly.nodes if n.kind == "ENTRY"} == {"existing", "new"}
    assert all(n.kind != "ENTRY" for n in r.source_nodes)


def test_unresolved_incoming_route_prevents_false_discovered_entry():
    d = case()
    d["nodes"] = tuple(replace(n, kind="CONDITION") if n.kind == "ENTRY" else n for n in d["nodes"])
    d["routes"] = tuple(
        replace(r, geometry_state="UNKNOWN") if r.route_id == "r1" else r for r in d["routes"]
    )
    r = api().reconstruct_discovered_diagram(**d)
    assert all(
        "equipped" not in p.node_ids or p.state != "SOURCE_CONDITIONAL_PATH_CANDIDATE"
        for p in r.assembly.paths
    )


def test_missing_incoming_route_does_not_turn_lower_question_into_entry():
    d = case()
    d["nodes"] = tuple(replace(n, kind="CONDITION") if n.kind == "ENTRY" else n for n in d["nodes"])
    d["routes"] = tuple(r for r in d["routes"] if r.route_id != "r1")
    r = api().reconstruct_discovered_diagram(**d)
    assert {n.node_id for n in r.assembly.nodes if n.kind == "ENTRY"} == {"new"}
    assert all(p.node_ids[0] == "new" for p in r.assembly.paths)


def test_top_entry_band_accepts_one_pixel_ocr_offset():
    d = case()
    d["nodes"] = tuple(
        replace(n, kind="CONDITION", anchor=replace(n.anchor, bbox=(700, 51, 840, 100)))
        if n.node_id == "new"
        else replace(n, kind="CONDITION")
        if n.kind == "ENTRY"
        else n
        for n in d["nodes"]
    )
    d["tokens"] = tuple(
        replace(t, anchor=replace(t.anchor, bbox=(700, 51, 840, 100)))
        if t.token_id == "t-new"
        else t
        for t in d["tokens"]
    )
    r = api().reconstruct_discovered_diagram(**d)
    assert {n.node_id for n in r.assembly.nodes if n.kind == "ENTRY"} == {"existing", "new"}
    assert len(r.assembly.paths) == 7


def test_calibrated_bt601_detector_version_preserves_candidate_paths():
    d = case()
    routes = tuple(
        replace(
            r,
            heads=tuple(
                replace(h, detector_version="axis-filled-head-bt601-150dpi-v2") for h in r.heads
            ),
        )
        for r in d["routes"]
    )
    result = run(routes=routes)
    assert sum(p.state == "SOURCE_CONDITIONAL_PATH_CANDIDATE" for p in result.assembly.paths) == 7
    assert result.business_eligibility == "UNKNOWN" and not result.admission_granted
