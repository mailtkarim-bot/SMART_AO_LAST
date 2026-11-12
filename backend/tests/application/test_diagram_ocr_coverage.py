from dataclasses import replace
from hashlib import sha256
from importlib import import_module
from importlib.util import find_spec
from uuid import UUID

import pytest
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
)

from tests.application.test_diagram_topology import image


def case(tokens=True):
    png = image((), ((35, 30, 105, 110),), ((45, 40, 65, 50, 70), (45, 70, 95, 80, 70)))
    scope = StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, sha256(png).hexdigest(), 42, 240, 220
    )
    return dict(
        png_bytes=png,
        expected_scope=scope,
        diagram_region=RegionAnchor(scope, (0, 0, 239, 219)),
        tokens=(
            RegionToken("non", "NON", RegionAnchor(scope, (44, 39, 66, 51))),
            RegionToken("eligible", "ELIGIBLE", RegionAnchor(scope, (44, 69, 96, 81))),
        )
        if tokens
        else (),
        render_dpi=150,
    )


def api():
    name = "app.modules.dce.infrastructure.diagram_ocr_coverage"
    assert find_spec(name), "raster OCR coverage missing"
    return import_module(name)


def adapter(text="NON ELIGIBLE", error=False, seen=None):
    from types import SimpleNamespace

    from app.modules.dce.infrastructure.advanced_extraction import RapidOcrAdvancedExtractionAdapter

    runtime = RapidOcrAdvancedExtractionAdapter()

    def engine(pixels):
        if seen is not None:
            seen.append(pixels.shape)
        if error:
            raise RuntimeError("SYNTHETIC_FAILURE")
        return SimpleNamespace(txts=(text,), boxes=[])

    runtime._engine = engine
    return runtime


def test_frame_without_ocr_is_retained_unknown_from_pixels():
    d = case(False)
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=None)
    assert len(r.frames) == 1 and len(r.nodes) == 1
    assert r.frames[0].state == "UNKNOWN" and r.nodes[0].text_state == "UNKNOWN"
    assert r.frames[0].missing_regions and not r.admission_granted


def test_full_ink_and_independent_text_agreement_remain_candidate():
    d = case()
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter())
    assert r.frames[0].uncovered_pixels == 0
    assert r.frames[0].state == "INK_AND_TEXT_CONCORDANCE_CANDIDATE"
    assert r.nodes[0].text_state == "SOURCE_TEXT_CANDIDATE"
    assert r.semantic_state == "UNKNOWN" and r.status == "REVIEW_REQUIRED"


def test_missing_negation_outside_remaining_box_is_unknown():
    d = case()
    d["tokens"] = d["tokens"][1:]
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter())
    assert r.frames[0].uncovered_pixels > 0 and r.frames[0].missing_regions
    assert r.nodes[0].text_state == "UNKNOWN"


def test_missing_negation_inside_same_box_is_unknown_on_reread():
    d = case()
    d["tokens"] = (
        RegionToken("merged", "ELIGIBLE", RegionAnchor(d["expected_scope"], (44, 39, 96, 81))),
    )
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter())
    assert r.frames[0].uncovered_pixels == 0 and r.nodes[0].text_state == "UNKNOWN"


def test_covered_boxes_without_reread_do_not_qualify_text():
    d = case()
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=None)
    assert r.frames[0].uncovered_pixels == 0 and r.nodes[0].text_state == "UNKNOWN"


def test_frame_detection_is_independent_of_horizontal_stroke_sort_order():
    d = case(False)
    png = image(((35, 30, 105, 30), (20, 110, 120, 110), (35, 30, 35, 110), (105, 30, 105, 110)))
    d["png_bytes"] = png
    d["expected_scope"] = replace(d["expected_scope"], render_sha256=sha256(png).hexdigest())
    d["diagram_region"] = replace(d["diagram_region"], scope=d["expected_scope"])
    assert (
        len(api().extract_raster_frame_regions(**{k: v for k, v in d.items() if k != "tokens"}))
        == 1
    )


def test_adjacent_cells_do_not_create_a_composite_text_frame():
    d = case(False)
    png = image((), ((35, 30, 105, 110), (105, 30, 175, 110)))
    d["png_bytes"] = png
    d["expected_scope"] = replace(d["expected_scope"], render_sha256=sha256(png).hexdigest())
    d["diagram_region"] = replace(d["diagram_region"], scope=d["expected_scope"])
    r = api().extract_raster_frame_regions(**{k: v for k, v in d.items() if k != "tokens"})
    assert {a.bbox for a in r} == {(35, 30, 105, 110), (105, 30, 175, 110)}


def test_composite_filter_is_independent_of_set_iteration_order():
    for left, mid, right in ((25, 110, 210), (30, 120, 200), (20, 90, 180), (40, 120, 220)):
        d = case(False)
        png = image((), ((left, 40, mid, 120), (mid, 40, right, 120)))
        d["png_bytes"] = png
        d["expected_scope"] = replace(d["expected_scope"], render_sha256=sha256(png).hexdigest())
        d["diagram_region"] = replace(d["diagram_region"], scope=d["expected_scope"])
        assert (
            len(api().extract_raster_frame_regions(**{k: v for k, v in d.items() if k != "tokens"}))
            == 2
        )


def test_blank_closed_region_is_retained_without_inventing_text_node():
    d = case(False)
    png = image((), ((35, 30, 105, 110),))
    d["png_bytes"] = png
    d["expected_scope"] = replace(d["expected_scope"], render_sha256=sha256(png).hexdigest())
    d["diagram_region"] = replace(d["diagram_region"], scope=d["expected_scope"])
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=None)
    assert len(r.frames) == 1 and r.frames[0].state == "UNKNOWN"
    assert r.nodes == ()


def test_disconnected_diagonal_corner_is_not_a_closed_frame():
    d = case(False)
    png = image(((36, 30, 105, 30), (35, 31, 35, 110), (35, 110, 105, 110), (105, 30, 105, 110)))
    d["png_bytes"] = png
    d["expected_scope"] = replace(d["expected_scope"], render_sha256=sha256(png).hexdigest())
    d["diagram_region"] = replace(d["diagram_region"], scope=d["expected_scope"])
    assert api().extract_raster_frame_regions(**{k: v for k, v in d.items() if k != "tokens"}) == ()


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", UUID(int=9)),
        ("document_id", UUID(int=9)),
        ("version_id", UUID(int=9)),
        ("source_sha256", "b" * 64),
        ("render_sha256", "b" * 64),
    ],
)
def test_foreign_token_scope_refused(field, value):
    d = case()
    t = d["tokens"][0]
    d["tokens"] = (
        replace(t, anchor=replace(t.anchor, scope=replace(d["expected_scope"], **{field: value}))),
    )
    with pytest.raises(ValueError, match="SCOPE"):
        api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter())


def test_failed_controlled_ocr_preserves_unknown_and_failure():
    d = case()
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter(error=True))
    assert (
        r.nodes[0].text_state == "UNKNOWN"
        and r.frames[0].readings[0].failure_code == "OCR_RUNTIME_FAILED"
    )


def test_wrong_adapter_type_refused():
    with pytest.raises(ValueError, match="ADAPTER_INVALID"):
        api().qualify_candidate_ocr_coverage(**case(), ocr_adapter=object())


def test_reread_hash_is_computed_from_crop_pixels():
    from io import BytesIO

    from PIL import Image

    d = case()
    seen = []
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter(seen=seen))
    im = Image.open(BytesIO(d["png_bytes"]))
    crop = im.crop((37, 32, 103, 108)).resize((198, 228), Image.Resampling.LANCZOS)
    buf = BytesIO()
    crop.save(buf, format="PNG")
    assert r.frames[0].readings[0].crop_sha256 == sha256(buf.getvalue()).hexdigest()
    assert seen == [(228, 198, 3)]


def test_nested_frames_remain_unknown():
    d = case(False)
    png = image((), ((25, 20, 115, 120), (35, 30, 105, 110)), ((45, 40, 65, 50, 70),))
    d["png_bytes"] = png
    d["expected_scope"] = replace(d["expected_scope"], render_sha256=sha256(png).hexdigest())
    d["diagram_region"] = replace(d["diagram_region"], scope=d["expected_scope"])
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=None)
    assert len(r.frames) == 2 and all(f.reason == "AMBIGUOUS_FRAMES" for f in r.frames)


def test_token_order_keeps_digest_and_nodes_identical():
    d = case()
    a = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter())
    d["tokens"] = tuple(reversed(d["tokens"]))
    b = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter())
    assert a == b


def test_declarative_reread_cannot_qualify_text_anymore():
    d = case()
    with pytest.raises(TypeError):
        api().qualify_candidate_ocr_coverage(**d, rereads=())


def test_oversized_controlled_ocr_text_remains_unknown():
    r = api().qualify_candidate_ocr_coverage(**case(), ocr_adapter=adapter("X" * 1025))
    assert (
        r.nodes[0].text_state == "UNKNOWN"
        and r.frames[0].readings[0].failure_code == "OCR_REREAD_LIMIT"
    )


def sequence_adapter(texts, seen=None):
    from types import SimpleNamespace

    from app.modules.dce.infrastructure.advanced_extraction import RapidOcrAdvancedExtractionAdapter

    runtime = RapidOcrAdvancedExtractionAdapter()
    iterator = iter(texts)

    def engine(pixels):
        if seen is not None:
            seen.append(pixels.shape)
        return SimpleNamespace(txts=(next(iterator),), boxes=[])

    runtime._engine = engine
    return runtime


def test_typographic_apostrophe_is_equivalent_without_changing_words():
    d = case()
    d["tokens"] = (
        RegionToken(
            "all",
            "Déjà équipé d'un variateur?",
            RegionAnchor(d["expected_scope"], (44, 39, 96, 81)),
        ),
    )
    r = api().qualify_candidate_ocr_coverage(
        **d, ocr_adapter=adapter("Déjà équipé d’un variateur ?")
    )
    assert r.nodes[0].text_state == "SOURCE_TEXT_CANDIDATE"


def test_spaces_are_rebuilt_only_from_matching_pixel_line_readings():
    r = api().qualify_candidate_ocr_coverage(
        **case(), ocr_adapter=sequence_adapter(("NONELIGIBLE", "NON", "ELIGIBLE"))
    )
    assert r.nodes[0].text_state == "SOURCE_TEXT_CANDIDATE"
    assert r.frames[0].readings[0].text == "NON ELIGIBLE"
    assert r.frames[0].readings[0].original_text == "NONELIGIBLE"
    assert len(r.frames[0].readings[0].line_readings) == 2


def test_repaired_crop_hash_covers_contrast_and_white_border():
    from io import BytesIO

    from PIL import Image, ImageOps

    d = case()
    seen = []
    r = api().qualify_candidate_ocr_coverage(
        **d, ocr_adapter=sequence_adapter(("", "NON ELIGIBLE"), seen=seen)
    )
    im = Image.open(BytesIO(d["png_bytes"]))
    crop = ImageOps.expand(
        ImageOps.autocontrast(ImageOps.grayscale(im.crop((37, 32, 103, 108)))), border=8, fill=255
    )
    crop = crop.resize((246, 276), Image.Resampling.LANCZOS)
    buf = BytesIO()
    crop.save(buf, format="PNG")
    assert r.frames[0].readings[0].crop_sha256 == sha256(buf.getvalue()).hexdigest()
    assert seen == [(228, 198, 3), (276, 246, 3)]


@pytest.mark.parametrize("parts", [("OUI", "ELIGIBLE"), ("ELIGIBLE", "NON"), ("", "ELIGIBLE")])
def test_line_reread_cannot_drop_negation_or_reorder_chars(parts):
    r = api().qualify_candidate_ocr_coverage(
        **case(), ocr_adapter=sequence_adapter(("NONELIGIBLE", *parts))
    )
    assert r.nodes[0].text_state == "UNKNOWN"
    assert r.frames[0].readings[0].failure_code in {"OCR_LINE_CONTENT_CONFLICT", "OCR_LINE_FAILED"}


@pytest.mark.parametrize(
    "raw,reread",
    [
        ("NON ELIGIBLE", "ELIGIBLE"),
        ("déjà équipé", "équipé"),
        ("IE3 ou IE4", "IE3"),
        ("IE2", "IE4"),
    ],
)
def test_normalisation_and_spacing_do_not_erase_business_words(raw, reread):
    d = case()
    d["tokens"] = (RegionToken("all", raw, RegionAnchor(d["expected_scope"], (44, 39, 96, 81))),)
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter(reread))
    assert r.nodes[0].text_state == "UNKNOWN"
    assert r.frames[0].readings[0].line_readings == ()


def test_line_reread_regions_hashes_and_order_are_preserved():
    d = case()
    r = api().qualify_candidate_ocr_coverage(
        **d, ocr_adapter=sequence_adapter(("NONELIGIBLE", "NON", "ELIGIBLE"))
    )
    reading = r.frames[0].readings[0]
    assert reading.input_region.bbox == (37, 32, 103, 108)
    assert len(reading.line_readings) == 2
    assert all(
        p.anchor.scope == d["expected_scope"]
        and len(p.crop_sha256) == 64
        and p.input_region == p.anchor
        for p in reading.line_readings
    )
    assert reading.line_readings[0].anchor.bbox[1] < reading.line_readings[1].anchor.bbox[1]


def test_successful_original_crop_is_preserved_without_enhancement():
    d = case()
    seen = []
    r = api().qualify_candidate_ocr_coverage(**d, ocr_adapter=adapter(seen=seen))
    assert seen == [(228, 198, 3)]
    assert r.frames[0].readings[0].crop_recipe == "scale3-lanczos-v1"


def test_empty_original_reading_is_kept_with_hash_and_failure():
    r = api().qualify_candidate_ocr_coverage(
        **case(), ocr_adapter=sequence_adapter(("", "NON ELIGIBLE"))
    )
    current = r.frames[0].readings[0]
    assert current.failure_code is None and len(current.previous_readings) == 1
    previous = current.previous_readings[0]
    assert previous.failure_code == "OCR_EMPTY_TEXT" and previous.crop_recipe == "scale3-lanczos-v1"
    assert (
        previous.crop_sha256 != current.crop_sha256
        and previous.input_region == current.input_region
    )


def test_more_than_eight_pixel_lines_stays_unknown_without_line_ocr():
    d = case()
    png = image((), ((35, 30, 105, 110),), tuple((45, y, 95, y + 2, 70) for y in range(40, 80, 4)))
    scope = replace(d["expected_scope"], render_sha256=sha256(png).hexdigest())
    d["png_bytes"] = png
    d["expected_scope"] = scope
    d["diagram_region"] = replace(d["diagram_region"], scope=scope)
    d["tokens"] = (RegionToken("merged", "NON ELIGIBLE", RegionAnchor(scope, (44, 39, 96, 81))),)
    seen = []
    r = api().qualify_candidate_ocr_coverage(
        **d, ocr_adapter=sequence_adapter(("NONELIGIBLE",), seen=seen)
    )
    assert (
        r.nodes[0].text_state == "UNKNOWN"
        and r.frames[0].readings[0].failure_code == "OCR_LINE_LIMIT_OR_EMPTY"
    )
    assert len(seen) == 1 and r.frames[0].readings[0].line_readings == ()


def test_two_empty_frame_reads_can_recover_only_with_complete_pixel_lines():
    r = api().qualify_candidate_ocr_coverage(
        **case(), ocr_adapter=sequence_adapter(("", "", "NON", "ELIGIBLE"))
    )
    assert r.nodes[0].text_state == "SOURCE_TEXT_CANDIDATE"
    reading = r.frames[0].readings[0]
    assert len(reading.line_readings) == 2 and reading.original_text == ""
    assert len(reading.previous_readings) == 1


@pytest.mark.parametrize("parts", [("", "ELIGIBLE"), ("ELIGIBLE", "NON"), ("OUI", "ELIGIBLE")])
def test_empty_parent_line_fallback_cannot_omit_or_change_negation(parts):
    r = api().qualify_candidate_ocr_coverage(
        **case(), ocr_adapter=sequence_adapter(("", "", *parts))
    )
    assert r.nodes[0].text_state == "UNKNOWN"
    assert r.frames[0].state == "UNKNOWN"


def test_pixel_line_mask_preserves_unquantized_colored_ink():
    from PIL import Image

    im = Image.new("RGB", (30, 20), "white")
    for y in range(5, 12):
        for x in range(5, 20):
            im.putpixel((x, y), (158, 189, 187))
    parts = api()._read_pixel_lines(im, (40, 40, 70, 60), case()["expected_scope"], adapter("NON"))
    assert len(parts) == 1
    assert parts[0].input_region.bbox == (44, 44, 61, 53)
