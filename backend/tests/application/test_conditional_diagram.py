from dataclasses import replace
from importlib import import_module
from importlib.util import find_spec
from uuid import UUID

import pytest
from app.modules.dce.application.diagram_evidence import ArrowheadEvidence, qualify_branch_label
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
)


def api():
    name = "app.modules.dce.application.conditional_diagram"
    assert find_spec(name) is not None, "conditional diagram assembler missing"
    return import_module(name)


def case():
    m = api()
    scope = StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, "b" * 64, 42, 1000, 1000
    )
    specs = (
        ("existing", "ENTRY", "Installation variateur sur moteur existant"),
        ("new", "ENTRY", "Installation variateur sur moteur neuf"),
        ("equipped", "CONDITION", "Moteur déjà équipé d'un variateur ?"),
        ("inlet", "JUNCTION", ""),
        ("async", "CONDITION", "Moteur asynchrone ?"),
        ("reject", "JUNCTION", ""),
        ("split", "JUNCTION", ""),
        ("ie2", "CONDITION", "Le moteur est de classe IE2"),
        ("ie34", "CONDITION", "Le moteur est de classe IE3 ou IE4"),
        ("no", "OUTCOME", "NON ELIGIBLE"),
        ("contact", "OUTCOME", "Contacter votre correspondant CEE centre"),
        ("yes", "OUTCOME", "ELIGIBLE"),
    )
    tokens, nodes = [], []
    for i, (name, kind, text) in enumerate(specs):
        anchor = RegionAnchor(scope, (50 + i * 65, 100, 80 + i * 65, 125))
        ids: tuple[str, ...] = () if not text else ("text-" + name,)
        if text:
            tokens.append(RegionToken(ids[0], text, anchor))
        nodes.append(
            m.ConditionalNode(
                name,
                kind,
                anchor,
                ids,
                "SOURCE_JUNCTION_CANDIDATE" if kind == "JUNCTION" else None,
                text_state="SOURCE_TEXT_CANDIDATE" if kind != "JUNCTION" else None,
            )
        )
    pairs = (
        ("e1", "existing", "equipped", None),
        ("e2", "new", "inlet", "OUI"),
        ("e3", "equipped", "inlet", "NON"),
        ("e4", "inlet", "async", None),
        ("e5", "equipped", "reject", "OUI"),
        ("e6", "async", "reject", "NON"),
        ("e7", "reject", "no", None),
        ("e8", "async", "split", "OUI"),
        ("e9", "split", "ie2", None),
        ("e10", "split", "ie34", None),
        ("e11", "ie2", "contact", None),
        ("e12", "ie34", "yes", None),
    )
    requirements, evidence = [], []
    by_id = {n.node_id: n for n in nodes}
    for rid, source, target, label in pairs:
        a, b = by_id[source].anchor.bbox, by_id[target].anchor.bbox
        start, end = ((a[0] + a[2]) / 2, 112), ((b[0] + b[2]) / 2, 112)
        branch = None
        label_id = None
        if label:
            label_id = "label-" + rid
            offset = 0 if label == "OUI" else 20
            t = RegionToken(
                label_id, label, RegionAnchor(scope, (a[0] + offset, 90, a[0] + offset + 10, 99))
            )
            tokens.append(t)
            branch = qualify_branch_label(expected_scope=scope, raw_token=t)
        requirements.append(m.RelationRequirement(rid, source, target, label_id, label))
        region = RegionAnchor(scope, (min(a[0], b[0]) - 5, 65, max(a[2], b[2]) + 5, 140))
        head = (
            None
            if by_id[target].kind == "JUNCTION"
            else ArrowheadEvidence(
                scope,
                "PIXEL_HEAD_CANDIDATE",
                end,
                RegionAnchor(scope, (end[0] - 2, 110, end[0] + 2, 114)),
            )
        )
        evidence.append(
            m.ConditionalRelationEvidence(
                rid, region, (start, end), "SOURCE_PATH_CANDIDATE", branch, head
            )
        )
    return dict(
        expected_scope=scope,
        tokens=tuple(tokens),
        nodes=tuple(nodes),
        required_relations=tuple(requirements),
        evidence=tuple(evidence),
    )


def run(**changes):
    data = case()
    data.update(changes)
    return api().assemble_conditional_paths(**data)


def test_seven_conditional_paths_keep_joins_and_do_not_decide_real_eligibility():
    result = run()
    assert len(result.paths) == 7 and result.missing_relations == ()
    assert result.unqualified_relations == () and result.ambiguous_relations == ()
    assert result.status == "REVIEW_REQUIRED" and result.business_eligibility == "UNKNOWN"
    assert result.admission_granted is False
    assert {p.document_outcome for p in result.paths} == {
        "DOCUMENT_ELIGIBLE_CEE",
        "DOCUMENT_NON_ELIGIBLE_CEE",
        "CONTACT_CEE_CORRESPONDENT",
    }
    path = next(
        p
        for p in result.paths
        if p.node_ids == ("existing", "equipped", "inlet", "async", "split", "ie34", "yes")
    )
    assert [c.node_id for c in path.conditions] == ["existing", "equipped", "async", "ie34"]
    assert [c.branch_label for c in path.conditions] == [None, "NON", "OUI", None]
    assert path.semantic_state == "UNKNOWN"


def test_missing_upstream_relation_invalidates_six_complete_hypotheses():
    data = case()
    result = run(evidence=tuple(e for e in data["evidence"] if e.relation_id != "e4"))
    assert result.missing_relations == ("e4",)
    assert len(result.paths) == 7
    affected = [p for p in result.paths if "e4" in p.relation_ids]
    assert len(affected) == 6 and all(
        p.state == "UNKNOWN" and p.document_outcome == "UNKNOWN" for p in affected
    )
    assert all("e4" in p.unknown_relation_ids for p in affected)


def test_ie2_contact_is_preserved_as_its_own_documentary_exit():
    paths = [p for p in run().paths if "ie2" in p.node_ids]
    assert len(paths) == 2 and all(p.document_outcome == "CONTACT_CEE_CORRESPONDENT" for p in paths)
    assert all("correspondant CEE" in p.endpoint_text for p in paths)


def test_identical_evidence_replay_and_permutation_are_deterministic():
    data = case()
    baseline = api().assemble_conditional_paths(**data)
    shuffled = {
        **data,
        "nodes": tuple(reversed(data["nodes"])),
        "tokens": tuple(reversed(data["tokens"])),
        "required_relations": tuple(reversed(data["required_relations"])),
        "evidence": tuple(reversed(data["evidence"])) + (data["evidence"][0],),
    }
    assert api().assemble_conditional_paths(**shuffled) == baseline


def test_conflicting_route_observations_are_ambiguous_not_selected():
    data = case()
    e = data["evidence"][0]
    altered = replace(e, path=(e.path[0], (100, 130), e.path[-1]))
    result = run(evidence=data["evidence"] + (altered,))
    assert result.ambiguous_relations == ("e1",)
    assert all(p.state == "UNKNOWN" for p in result.paths if "e1" in p.relation_ids)


def test_unknown_branch_label_blocks_only_its_dependent_paths():
    data = case()
    es = list(data["evidence"])
    i = next(i for i, e in enumerate(es) if e.relation_id == "e2")
    es[i] = replace(es[i], branch=None)
    result = run(evidence=tuple(es))
    assert result.unqualified_relations == ("e2",)
    assert len([p for p in result.paths if p.state == "UNKNOWN"]) == 3


def test_head_without_unique_pixel_proof_cannot_qualify_a_terminal_relation():
    data = case()
    es = tuple(
        replace(e, head=ArrowheadEvidence(data["expected_scope"])) if e.relation_id == "e12" else e
        for e in data["evidence"]
    )
    result = run(evidence=es)
    assert result.unqualified_relations == ("e12",)
    assert all(p.document_outcome == "UNKNOWN" for p in result.paths if "e12" in p.relation_ids)


def test_foreign_scope_is_rejected_before_missing_counts_or_paths():
    data = case()
    e = data["evidence"][0]
    foreign = replace(data["expected_scope"], tenant_id=UUID(int=9))
    e = replace(e, anchor=replace(e.anchor, scope=foreign))
    with pytest.raises(ValueError, match="STRUCTURE_SCOPE_MISMATCH"):
        run(evidence=(e,))


def test_cyclic_reference_graph_is_refused():
    data = case()
    req = data["required_relations"] + (api().RelationRequirement("back", "split", "async"),)
    with pytest.raises(ValueError, match="DIAGRAM_CYCLE"):
        run(required_relations=req)


def test_unexpected_relation_is_not_silently_admitted():
    data = case()
    unknown = replace(data["evidence"][0], relation_id="unknown")
    with pytest.raises(ValueError, match="DIAGRAM_REFERENCE_MISMATCH"):
        run(evidence=(unknown,))


def test_path_geometry_must_attach_to_both_declared_nodes():
    data = case()
    e = data["evidence"][0]
    bad = replace(e, path=((500, 500), e.path[-1]))
    with pytest.raises(ValueError, match="DIAGRAM_PATH_INVALID"):
        run(evidence=(bad,))


def test_non_eligible_tokens_cannot_be_reduced_to_positive_label():
    data = case()
    old = next(t for t in data["tokens"] if t.token_id == "text-no")
    negative = replace(
        old,
        token_id="negative-no",
        text="NON",
        anchor=RegionAnchor(old.anchor.scope, (old.anchor.bbox[0], 100, old.anchor.bbox[2], 109)),
    )
    positive = replace(
        old,
        text="ELIGIBLE",
        anchor=RegionAnchor(old.anchor.scope, (old.anchor.bbox[0], 110, old.anchor.bbox[2], 125)),
    )
    tokens = tuple(positive if t.token_id == "text-no" else t for t in data["tokens"]) + (negative,)
    result = run(tokens=tokens)
    assert all(p.document_outcome == "UNKNOWN" for p in result.paths if p.node_ids[-1] == "no")


def test_reference_dead_end_never_becomes_a_source_eligibility_result():
    data = case()
    req = tuple(r for r in data["required_relations"] if r.source_id != "async")
    ev = tuple(e for e in data["evidence"] if e.relation_id not in ("e6", "e8"))
    result = run(required_relations=req, evidence=ev)
    assert "async" in result.dead_end_nodes
    assert all(p.document_outcome == "UNKNOWN" for p in result.paths if p.node_ids[-1] == "async")


def test_condition_and_join_regions_and_raw_branch_evidence_survive_assembly():
    result = run()
    assert next(n for n in result.nodes if n.node_id == "inlet").anchor.scope == result.scope
    assert any(t.token_id == "label-e3" and t.text == "NON" for t in result.tokens)
    p = next(p for p in result.paths if p.node_ids[-1] == "yes" and p.node_ids[0] == "existing")
    c = next(c for c in p.conditions if c.node_id == "equipped")
    assert c.branch_evidence.raw_token.text == "NON"


def test_unknown_junction_prevents_six_paths_from_reaching_a_known_exit():
    data = case()
    nodes = tuple(
        replace(n, junction_state="UNKNOWN") if n.node_id == "inlet" else n for n in data["nodes"]
    )
    result = run(nodes=nodes)
    assert "inlet" in result.unqualified_nodes
    assert sum(p.state == "UNKNOWN" for p in result.paths) == 6


def test_token_group_order_does_not_change_the_condition_or_manifest():
    data = case()
    original = next(t for t in data["tokens"] if t.token_id == "text-existing")
    a = replace(
        original,
        text="Installation variateur",
        anchor=RegionAnchor(original.anchor.scope, (50, 100, 80, 111)),
    )
    b = replace(
        original,
        token_id="existing-part2",
        text="sur moteur existant",
        anchor=RegionAnchor(original.anchor.scope, (50, 112, 80, 125)),
    )
    tokens = tuple(a if t.token_id == a.token_id else t for t in data["tokens"]) + (b,)
    nodes = tuple(
        replace(n, token_ids=(a.token_id, b.token_id)) if n.node_id == "existing" else n
        for n in data["nodes"]
    )
    baseline = run(tokens=tokens, nodes=nodes)
    reversed_nodes = tuple(replace(n, token_ids=tuple(reversed(n.token_ids))) for n in nodes)
    assert run(tokens=tokens, nodes=reversed_nodes) == baseline


def test_entry_cannot_skip_an_incoming_condition():
    data = case()
    nodes = tuple(replace(n, kind="ENTRY") if n.node_id == "async" else n for n in data["nodes"])
    with pytest.raises(ValueError, match="DIAGRAM_ENTRY_HAS_INCOMING"):
        run(nodes=nodes)


def test_remote_label_cannot_qualify_a_condition_branch():
    data = case()
    old = next(t for t in data["tokens"] if t.token_id == "label-e3")
    raw = replace(old, anchor=RegionAnchor(old.anchor.scope, (100, 300, 110, 310)))
    tokens = tuple(raw if t.token_id == raw.token_id else t for t in data["tokens"])
    branch = qualify_branch_label(expected_scope=data["expected_scope"], raw_token=raw)
    evidence = tuple(
        replace(e, branch=branch, anchor=RegionAnchor(e.anchor.scope, (50, 65, 900, 330)))
        if e.relation_id == "e3"
        else e
        for e in data["evidence"]
    )
    result = run(tokens=tokens, evidence=evidence)
    assert "e3" in result.unqualified_relations


def test_duplicate_yes_reference_branches_are_not_assumed_exclusive():
    data = case()
    req = tuple(
        replace(r, branch_label="OUI") if r.relation_id == "e3" else r
        for r in data["required_relations"]
    )
    with pytest.raises(ValueError, match="DIAGRAM_BRANCH_AMBIGUOUS"):
        run(required_relations=req)


def test_condition_fork_without_boolean_labels_remains_unknown():
    data = case()
    req = tuple(
        replace(r, branch_label=None, branch_token_id=None) if r.source_id == "async" else r
        for r in data["required_relations"]
    )
    evidence = tuple(
        replace(e, branch=None) if e.relation_id in {"e6", "e8"} else e for e in data["evidence"]
    )
    result = run(required_relations=req, evidence=evidence)
    assert "async" in result.unqualified_nodes
    assert all(p.state == "UNKNOWN" for p in result.paths if "async" in p.node_ids)


def test_unreadable_condition_stays_unknown_with_raw_text_preserved():
    data = case()
    tokens = tuple(
        replace(t, text="???") if t.token_id == "text-async" else t for t in data["tokens"]
    )
    result = run(tokens=tokens)
    assert "async" in result.unqualified_nodes
    assert all(p.state == "UNKNOWN" for p in result.paths if "async" in p.node_ids)
    assert next(t for t in result.tokens if t.token_id == "text-async").text == "???"


def test_ambiguous_observations_preserve_crop_and_parser_provenance():
    data = case()
    original = next(e for e in data["evidence"] if e.relation_id == "e2")
    raw = original.branch.raw_token
    reread = replace(raw, token_id="crop-e2")
    branch = qualify_branch_label(
        expected_scope=data["expected_scope"],
        raw_token=raw,
        reread_token=reread,
        reread_input_sha256="c" * 64,
        reread_extractor_id="regional-parser",
        reread_extractor_version="1",
    )
    changed = replace(original, branch=branch)
    result = run(evidence=data["evidence"] + (changed,))
    assert result.ambiguous_relations == ("e2",)
    assert changed in result.evidence and original in result.evidence
    assert result.required_relations == tuple(
        sorted(data["required_relations"], key=lambda r: r.relation_id)
    )


def test_missing_text_qualification_blocks_paths_even_with_nonempty_ocr():
    data = case()
    nodes = tuple(
        replace(n, text_state="UNKNOWN") if n.node_id == "async" else n for n in data["nodes"]
    )
    result = run(nodes=nodes)
    assert "async" in result.unqualified_nodes
    assert all(p.state == "UNKNOWN" for p in result.paths if "async" in p.node_ids)
