"""Creative drafts, final-save guarantees, and independent invalid assembly probes."""
import json
import shutil
import subprocess
import sys

import numpy as np
import pytest

from conftest import mpd, ref
from ldraw_tools.builder import build_plan, serialize_mpd
from ldraw_tools.check import _outside, check_model, compare_intended
from ldraw_tools.common import ROOT, library_path
from ldraw_tools.kit import KitError, KitValidationError, Model


@pytest.mark.parametrize("body", [
    ref("60592.dat") + "\n" + ref("60592.dat", position="10 0 0"),
    ref("3043.dat", position="430 -244 390") + "\n" + ref("6143.dat", position="410 -224 390", matrix="-1 0 0 0 -1 0 0 0 1"),
    ref() + "\n" + ref(position="200 0 0"),
])
def test_bad_assemblies_never_pass(official, tmp_path, body):
    path = tmp_path / "bad.mpd"
    path.write_text(mpd(body))
    report = check_model(path, official, library_path())
    assert not report["checks_passed"] and report["verdict"] == "FAIL"
    assert report["physical_validity"] == "not_proven"


def test_mate_rejects_incompatible_profiles_even_in_exploration(official):
    m = Model("m", "Profile compatibility")
    hole = m.place("32064", "Red")
    with pytest.raises(KitError, match="incompatible ports"):
        m.mate("3005", "Blue", "stud[0]", to=hole.port("axle_hole[0]"))


def test_no_false_support_on_ridge_peak(official, tmp_path):
    m = Model("roof", "A ridge cannot support a chimney on top")
    ridge = m.place("3043", "Red")
    m.place("6143", "Light_Bluish_Grey", level=ridge.top)
    with pytest.raises(KitValidationError):
        m.save(tmp_path / "roof.mpd")
    assert not (tmp_path / "roof.mpd").exists()


def test_drafts_renderable_and_failed_final_save_preserves_output(official, tmp_path):
    m = Model("explore", "Try the composition before finishing attachments")
    m.place("3001", "Red")
    m.place("3001", "Blue", cell=(10, 0))
    draft = tmp_path / "draft.mpd"
    report = m.save(draft, draft=True, quiet=True)
    assert draft.exists() and report["draft"] and not report["checks_passed"]
    assert "!NOVA DRAFT" in draft.read_text()
    final = tmp_path / "final.mpd"
    final.write_text("previous reviewed revision")
    with pytest.raises(KitValidationError) as error:
        m.save(final)
    assert error.value.report["floating_count"] == 1
    assert final.read_text() == "previous reviewed revision"
    assert not list(tmp_path.glob("*.tmp*"))


def test_strict_feedback_is_optional_but_final_check_is_not(official, tmp_path):
    explore = Model("draft", "Intersecting massing studies")
    explore.place("3001", "Red")
    explore.place("3001", "Blue", cell=(1, 0))
    with pytest.raises(KitValidationError):
        explore.save(tmp_path / "invalid.mpd")
    detail = Model("detail", "Engineer a known detail", strict=True)
    detail.place("3001", "Red")
    with pytest.raises(KitError, match="collides"):
        detail.place("3001", "Blue", cell=(1, 0))


def test_stack_and_plan_round_trip(official, tmp_path):
    m = Model("stack", "Ordinary studded stacking")
    base = m.place("3001", "Red", id="base")
    m.place("3020", "Blue", level=base.top, id="deck")
    final = tmp_path / "stack.mpd"
    assert m.save(final, quiet=True)["checks_passed"]
    text, rebuilt, diagnostics = build_plan(m.plan(), official)
    assert not diagnostics and text == final.read_bytes().decode()
    assert serialize_mpd(rebuilt) == text


def test_exported_port_follows_rotated_module_instance(official, tmp_path):
    m = Model("modules", "Modules export real attachment ports")
    block = m.section("block", "An independently built module")
    base = block.place("3001", "Red")
    block.expose_port("top", base.port("stud[0]"))
    block.anchor("base", at=(0, 0, 0))
    instance = m.add(block, None, at=(80, -40, 20), turn=90, id="block")
    world = instance.port("top")
    assert np.allclose(world.P, instance.R @ base.port("stud[0]").P + instance.t)
    m.mate("3005", "Blue", "pin_hole[0]", to=world, id="cap")
    assert m.save(tmp_path / "modules.mpd", quiet=True)["checks_passed"]
    plan = m.plan()
    assert plan["sections"][1]["anchors"]["base"]["at"] == [0, 0, 0]
    assert not build_plan(plan, official)[2]


def test_nested_module_ports_preserve_roll_and_socket_direction(official, tmp_path):
    m = Model("nested", "Nested interfaces retain the authored frame")
    inner = m.section("inner", "Rotated brick")
    base = inner.add("3001", "Red", turn=90)
    inner.expose_port("top", base.port("stud[0]"))
    outer = m.section("outer", "Nested module")
    nested = outer.add(inner, None, turn=90)
    outer.expose_port("top", nested.port("top"))
    instance = m.add(outer, None, turn=90)
    port = instance.port("top")
    assert instance.ports() == instance.ports("stud") == ["top"]
    assert not instance.ports("pin")
    assert np.allclose(port.reference, instance.R @ nested.R @ base.port("stud[0]").reference)
    m.mate("3005", "Blue", "pin_hole[0]", to=port)
    assert m.save(tmp_path / "nested.mpd", quiet=True)["checks_passed"]


def test_strict_module_placement_checks_geometry_without_partial_mutation(official):
    m = Model("modules", "Inline checks include module instances", strict=True)
    m.place("3001", "Red")
    block = m.section("block", "Module")
    block.place("3001", "Blue")
    with pytest.raises(KitError, match="collides"):
        m.add(block, None, at=(20, 0, 0))
    assert len(m.entries) == len(m.rows) == 1


def test_sections_cannot_form_cycles(official):
    m = Model("cycles", "Reject recursive assemblies")
    child = m.section("child", "Child")
    m.add(child, None)
    with pytest.raises(KitError, match="cycle"):
        child.add(m, None)


def test_reversed_stud_cannot_enter_socket_through_solid(official):
    m = Model("studs", "Direction matters")
    ridge = m.place("3043", "Red")
    with pytest.raises(KitError, match="socket mouth"):
        m.mate("6143", "Light_Bluish_Grey", "stud[0]", to=ridge.port("stud_receptacle[0]"), flip=True)


@pytest.mark.parametrize("assembly", ["pin", "wheel", "hinge"])
def test_valid_interfaces_remain_usable(official, tmp_path, assembly):
    m = Model(assembly, "Known small interface", strict=True)
    if assembly == "pin":
        beam = m.add("32524", "Red", axes={"y": "Y", "z": "X"})
        pin = m.mate("2780", "Black", "pin[0]", to=beam.port("pin_hole[0]"))
        m.mate("32524", "Blue", "pin_hole[0]", to=pin.port("pin[2]"))
    elif assembly == "wheel":
        plate = m.place("4600", "Black")
        rim = m.mate("4624", "White", "pin_hole[0]", to=plate.port("pin[0]"))
        m.mate("3641", "Black", "tyre_bead[0]", to=rim.port("rim_seat[0]"))
    else:
        root = m.place("4275b", "Light_Bluish_Grey")
        m.hinge("4276b", "Blue", "hinge[0]", to=root.port("hinge[0]"), angle=30)
    report = m.save(tmp_path / f"{assembly}.mpd", draft=True, quiet=True)
    assert not report["collision_count"] and not report["floating_count"] and not report["seating_count"]
    if assembly == "hinge":
        # Known coverage gap: finger engagement has no validated collision mask.
        assert report["needs_review"] and report["review_count"] == 1
        with pytest.raises(KitValidationError) as error:
            m.save(tmp_path / "hinge-final.mpd", quiet=True)
        assert error.value.report["verdict"] == "REVIEW"
    else:
        assert not report["needs_review"]
        assert m.save(tmp_path / f"{assembly}-final.mpd", quiet=True)["checks_passed"]


def test_connection_helpers_do_not_invent_interfaces(official):
    m = Model("ports", "Only real matching interfaces")
    brick = m.place("3001", "Red")
    with pytest.raises(KitError, match="two hinge ports"):
        m.hinge("3005", "Blue", "stud[0]", to=brick.port("stud[0]"))
    beam = m.add("32524", "Red", axes={"y": "Y", "z": "X"})
    shifted = m.add("32524", "Blue", axes={"y": "Y", "z": "X"}, at=(0, 20, 0))
    m.pin("Black", between=(beam.port("pin_hole[0]"), shifted.port("pin_hole[0]")))
    # Coaxial studs spaced like two holes still do not accept a pin.
    higher = m.add("3001", "Blue", at=brick.t + [0, 20, 0])
    with pytest.raises(KitError, match="compatible holes"):
        m.pin("Black", between=(brick.port("stud[0]"), higher.port("stud[0]")))


def test_engagement_masks_do_not_erase_material_between_bores():
    edges = np.array([[[0., 0., 0.], [20., 0., 0.]]])
    tris = np.array([[[0., 0., 0.], [20., 0., 0.], [0., 1., 0.]]])
    axis = np.array([0., 1., 0.])
    zones = [(np.array([x, 0., 0.]), axis, 2., -2., 2.) for x in (0., 20.)]
    kept_edges, kept_tris = _outside(edges, tris, zones)
    assert np.array_equal(kept_edges, edges) and np.array_equal(kept_tris, tris)


def test_embedded_lookalike_does_not_borrow_library_connectors(official, tmp_path):
    # The name and bounds match 3001, but these faces have no stud/socket geometry.
    faces = "4 16 -40 -4 -20 40 -4 -20 40 -4 20 -40 -4 20\n4 16 -40 24 -20 -40 24 20 40 24 20 40 24 -20"
    path = tmp_path / "lookalike.mpd"
    path.write_text(mpd(ref("custom-3001.dat")) + mpd(faces, "custom-3001.dat").replace("!LDRAW_ORG Model", "!LDRAW_ORG Unofficial_Part"))
    report = check_model(path, official, library_path())
    assert report["unknown_count"] == 1
    assert report["verdict"] == "REVIEW" and not report["checks_passed"]


def test_intended_module_graph_checks_chains_and_unknown_names():
    report = dict(modules=[dict(module=name) for name in ("base", "wall", "roof")],
                  module_edges=[dict(a="base", b="wall")])
    result = compare_intended(report, "```mermaid\nflowchart LR\nbase --> wall --> roof\nroof --> chimney\n```")
    assert result["missing"] == [["roof", "wall"]]
    assert result["unknown_modules"] == ["chimney"]
    with pytest.raises(ValueError, match="No module connection edges"):
        compare_intended(report, "Roof remains above the walls")


def test_overlap_declaration_cannot_turn_collision_into_a_pass(official, tmp_path):
    m = Model("overlap", "Acknowledged uncertainty remains unresolved")
    m.place("3001", "Red", free="standalone study")
    m.place("3001", "Blue", cell=(1, 0), free="standalone study", overlap="investigate this intersection")
    with pytest.raises(KitValidationError) as error:
        m.save(tmp_path / "overlap.mpd", quiet=True)
    assert error.value.report["verdict"] == "REVIEW"
    assert error.value.report["review_count"] == 1


def test_engineering_keeps_the_drafted_canopy_envelope(official, tmp_path):
    m = Model("porch", "Preserve the canopy while adding its supports")
    m.place("3032", "Tan", id="floor")
    canopy = m.place("3032", "Dark_Red", level=10, id="canopy")
    envelope = np.array(canopy.box)
    draft = m.save(tmp_path / "porch-draft.mpd", draft=True, quiet=True)
    assert draft["floating_count"] == 1
    for column, cell in enumerate(((0, 0), (5, 0), (0, 3), (5, 3))):
        for course in range(3):
            m.place("3005", "Tan", cell=cell, level=1 + 3 * course, id=f"column-{column}-{course}")
    assert m.save(tmp_path / "porch.mpd", quiet=True)["checks_passed"]
    assert np.array_equal(canopy.box, envelope)


def test_kit_rejects_scale_shear_and_nonfinite_positions(official):
    m = Model("rigid", "No deformed parts")
    for matrix, at in [(np.eye(3) * 2, (0, 0, 0)), (np.eye(3), (float("nan"), 0, 0))]:
        with pytest.raises(KitError, match="proper rigid rotation"):
            m.add("3001", "Red", matrix=matrix, at=at)


def test_plan_draft_and_final_cli_status(official, tmp_path):
    source = tmp_path / "plan.json"
    source.write_text(json.dumps(dict(version=1, author="Test", sections=[dict(name="main.ldr", description="Draft", steps=[[
        dict(id="a", ref="3001.dat", colour=4, at=[0, 0, 0]),
        dict(id="b", ref="3001.dat", colour=1, at=[10, 0, 0]),
    ]])])))
    output = tmp_path / "draft.mpd"
    result = subprocess.run([sys.executable, "-m", "ldraw_tools.cli", "build", str(source), "--draft", "--output", str(output)],
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["written"] and report["draft"] and not report["checks_passed"]
    result = subprocess.run([sys.executable, "-m", "ldraw_tools.cli", "check", str(output)], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 1
    assert not json.loads(result.stdout)["checks_passed"]


@pytest.mark.skipif(not shutil.which("leocad"), reason="LeoCAD unavailable")
def test_look_does_not_require_passing_geometry(official, tmp_path):
    from ldraw_tools.look import look
    path = tmp_path / "floating.mpd"
    path.write_text(mpd(ref() + "\n" + ref(position="200 0 0")))
    result = look(path, official, library_path(), tmp_path / "views", views=["front"], cell=200)
    from pathlib import Path
    assert Path(result["sheet"]).is_file()
