import pytest

from ldraw_tools.validation import validate_text
from conftest import mpd, ref


def codes(text, parts, **kwargs):
    return {d["code"] for d in validate_text(text, parts, **kwargs)[1]}


def test_valid_assembly(parts):
    assert not validate_text(mpd(ref()), parts)[1]


@pytest.mark.parametrize("body,code", [
    ("6 0", "parse.invalid_line"),
    ("1 4 0 0", "syntax.field_count"),
    (ref(colour=24), "colour.edge_on_surface"),
    (ref(colour=999999), "model.unknown_colour"),
    (ref(colour=16), "colour.unresolved_current"),
    (ref(position="nan 0 0"), "number.nonfinite"),
    (ref(matrix="0 0 0 0 1 0 0 0 1"), "matrix.singular"),
    (ref(matrix="1 0.2 0 0 1 0 0 0 1"), "assembly.nonrigid"),
    (ref(matrix="-1 0 0 0 1 0 0 0 1"), "assembly.nonrigid"),
    (ref("missing.dat"), "model.unknown_part"),
    (ref()+"\n"+ref(colour=1), "assembly.duplicate"),
    ("0 STEP extra\n"+ref(), "meta.step_arguments"),
    ("0 BFC INVERTNEXT\n0 // comment\n"+ref(), "bfc.invertnext"),
    (ref()+"\n0 BFC CERTIFY CCW", "bfc.certification_order"),
    ("0 BFC CERTIFY INVERTNEXT\n"+ref(), "bfc.syntax"),
    ("0 !TEXMAP START PLANAR 0 0 0 1 0 0 0 1 0 x.png\n"+ref(), "coverage.unsupported_meta"),
    ("0 !COLOUR Foo CODE 999 VALUE #FF0000 EDGE #000000\n"+ref(), "coverage.unsupported_meta"),
])
def test_broken_assembly(parts, body, code):
    assert code in codes(mpd(body), parts)


def test_bom_and_encoding(parts):
    text=mpd(ref())
    assert "encoding.bom" in codes("\ufeff"+text, parts)
    assert "encoding.line_endings" in codes(text.replace("\r\n","\n"), parts)


def test_crlf_and_blank_invertnext(parts):
    text=mpd("0 BFC CERTIFY CCW\n0 BFC INVERTNEXT\n\n"+ref())
    assert "bfc.invertnext" not in codes(text, parts, assembly=False)


def test_nofile_ignored_and_preamble_rejected(parts):
    assert not codes(mpd(ref())+"Email signature\r\n19 bad\r\n", parts)
    assert "mpd.preamble_geometry" in codes(ref()+"\n"+mpd(ref()), parts)


def test_duplicate_section_and_cycle(parts):
    assert "mpd.duplicate_section" in codes(mpd(ref())+mpd(ref(),"MAIN.LDR"),parts)
    assert "mpd.cycle" in codes(mpd(ref("child.ldr"))+mpd(ref("main.ldr"),"child.ldr"),parts)


def test_references_case_spaces_and_transform_composition(parts):
    text=mpd(ref("Child Model.LDR",position="10 0 0",matrix="0 0 1 0 1 0 -1 0 0"))
    text+=mpd(ref(colour=16,position="20 0 0"),"child model.ldr")
    model, problems=validate_text(text,parts)
    assert not problems
    occ=list(model.iter_occurrences())[0]
    assert (occ.position.x,occ.position.y,occ.position.z)==(10,0,-20)
    assert occ.colour.code==4
    assert model.bill_of_materials(parts=parts)[0].quantity==1


def test_duplicate_across_submodels(parts):
    text=mpd(ref("child.ldr")+"\n"+ref("child.ldr",colour=1))+mpd(ref(colour=16),"child.ldr")
    assert "assembly.duplicate" in codes(text,parts)


@pytest.mark.parametrize("body,code", [
    ("2 24 0 0 0 0 0 0", "geometry.zero_length"),
    ("3 4 0 0 0 1 0 0 2 0 0", "geometry.degenerate"),
    ("4 4 0 0 0 1 0 0 1 1 0 0 1 1", "geometry.nonplanar"),
    ("4 4 0 0 0 1 1 0 0 1 0 1 0 0", "geometry.quad_winding"),
    ("4 4 0 0 0 2 0 0 0.5 0.5 0 0 2 0", "geometry.quad_winding"),
])
def test_polygon_validity(parts,body,code):
    assert code in codes(mpd(body),parts,assembly=False)


def test_valid_direct_colour_and_rounded_rotation(parts):
    assert not codes(mpd("3 0x2FF00AB 0 0 0 20 0 0 0 0 20"),parts,assembly=False)
    assert not codes(mpd(ref(matrix="0.707107 0 0.707107 0 1 0 -0.707107 0 0.707107")),parts)


def test_repeated_filename_spaces_fail_explicitly(parts):
    text=mpd(ref("child  model.ldr"))+mpd(ref(colour=16),"child  model.ldr")
    assert "coverage.filename_whitespace" in codes(text,parts)
