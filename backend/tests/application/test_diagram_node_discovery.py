from hashlib import sha256
from importlib import import_module
from uuid import UUID

import pytest
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
)

from tests.application.test_diagram_topology import image


def discover(
    boxes=((35, 30, 105, 90),),
    captions=(("first", "NON", (45, 40, 80, 55)), ("second", "ELIGIBLE", (45, 60, 95, 75))),
    **kwargs,
):
    png = image((), boxes)
    scope = StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, sha256(png).hexdigest(), 42, 240, 220
    )
    tokens = tuple(RegionToken(i, text, RegionAnchor(scope, b)) for i, text, b in captions)
    module = import_module("app.modules.dce.infrastructure.diagram_node_reader")
    return module.discover_candidate_nodes(
        png_bytes=png,
        expected_scope=scope,
        diagram_region=RegionAnchor(scope, (0, 0, 239, 219)),
        tokens=tokens,
        render_dpi=kwargs.pop("render_dpi", 150),
        **kwargs,
    )


def test_groups_raw_tokens_in_closed_frame_without_groups_or_roles():
    from importlib.util import find_spec

    assert find_spec("app.modules.dce.infrastructure.diagram_node_reader"), "node discovery missing"
    result = discover()
    assert len(result.nodes) == 1
    assert result.nodes[0].token_ids == ("first", "second")
    assert result.nodes[0].kind == "OUTCOME"
    assert result.nodes[0].text_state == "SOURCE_TEXT_CANDIDATE"
    assert result.unassigned_tokens == ()
    assert result.status == "REVIEW_REQUIRED" and not result.admission_granted


def test_unframed_branch_label_is_not_a_node():
    result = discover(
        captions=(
            ("q", "Moteur existant?", (45, 40, 95, 55)),
            ("label", "OUI", (120, 100, 150, 115)),
        )
    )
    assert len(result.nodes) == 1
    assert result.nodes[0].kind == "CONDITION"
    assert result.unassigned_tokens == ("label",)


def test_nested_frames_refuse_ambiguous_group():
    result = discover(boxes=((35, 30, 105, 90), (25, 20, 115, 100)))
    assert result.nodes == ()
    assert set(result.unassigned_tokens) == {"first", "second"}


def test_unreadable_frame_preserves_unknown():
    result = discover(captions=(("raw", "???", (45, 40, 80, 55)),))
    assert result.nodes[0].text_state == "UNKNOWN"


def test_contact_correspondent_is_document_outcome():
    result = discover(
        captions=(("raw", "Contacter votre correspondant CEE centre", (45, 40, 95, 55)),)
    )
    assert result.nodes[0].kind == "OUTCOME"


def test_token_order_does_not_change_groups_or_digest():
    a = discover()
    b = discover(
        captions=(("second", "ELIGIBLE", (45, 60, 95, 75)), ("first", "NON", (45, 40, 80, 55)))
    )
    assert a == b


def test_wrong_scale_refused():
    with pytest.raises(ValueError, match="SCALE"):
        discover(render_dpi=300)


def test_token_with_unqualified_individual_frame_joins_unique_discovered_frame():
    result = discover(
        boxes=((35, 30, 105, 150),),
        captions=(
            ("middle", "Contacter votre correspondant CEE", (45, 80, 95, 100)),
            ("bottom", "centre", (45, 130, 80, 145)),
        ),
    )
    assert result.unassigned_tokens == ()
    assert result.nodes[0].token_ids == ("middle", "bottom")
    assert result.nodes[0].kind == "OUTCOME"


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", UUID(int=9)),
        ("document_id", UUID(int=9)),
        ("version_id", UUID(int=9)),
        ("source_sha256", "c" * 64),
        ("render_sha256", "c" * 64),
    ],
)
def test_foreign_or_stale_token_scope_refused(field, value):
    from dataclasses import replace

    r = discover()
    token = r.tokens[0]
    foreign = replace(token, anchor=replace(token.anchor, scope=replace(r.scope, **{field: value})))
    with pytest.raises(ValueError, match="SCOPE"):
        import_module(
            "app.modules.dce.infrastructure.diagram_node_reader"
        ).discover_candidate_nodes(
            png_bytes=image((), ((35, 30, 105, 90),)),
            expected_scope=r.scope,
            diagram_region=r.diagram_region,
            tokens=(foreign,),
            render_dpi=150,
        )


def test_empty_ocr_stays_empty_without_admission():
    r = discover(captions=())
    assert r.nodes == () and r.tokens == () and not r.admission_granted


def test_tokens_outside_region_refused():
    with pytest.raises(ValueError, match="OUTSIDE_REGION"):
        discover(captions=(("outside", "X", (230, 40, 240, 55)),))


def test_token_limit_refused():
    with pytest.raises(ValueError, match="LIMIT"):
        discover(captions=tuple((str(i), "X", (45, 40, 80, 55)) for i in range(33)))


def test_ambiguous_nested_token_is_not_attached_to_other_discovered_frame():
    r = discover(
        boxes=((35, 30, 105, 120), (40, 50, 100, 90)),
        captions=(("non", "NON", (45, 60, 95, 75)), ("eligible", "ELIGIBLE", (45, 94, 95, 104))),
    )
    assert r.unassigned_tokens == ("non",)
    assert r.nodes[0].text_state == "UNKNOWN"
    assert r.nodes[0].token_ids == ("eligible",)
