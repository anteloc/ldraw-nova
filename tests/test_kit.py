"""Construction kit: grid placement, port mating, call-site errors and saved output."""
import json
import subprocess
import sys

import numpy as np
import pytest

from ldraw_tools.common import ROOT
from ldraw_tools.kit import KitError, Model, axes_matrix


@pytest.fixture
def model(official):
    return Model("kit-test", "Kit test model")


def test_grid_stacking_needs_no_coordinates(model, tmp_path):
    base = model.place("3001", "Red", cell=(0, 0), level=0)
    plate = model.place("4600", "Black", cell=(1, 0), level=base.top)   # wheel pins hang below its stacking plane
    tile = model.place("3068b", "White", cell=(1, 0), level=plate.top)
    assert base.top == 3 and plate.top == 4 and tile.top == 5
    assert model.save(tmp_path / "stack.mpd", quiet=True)["checks_passed"]


def test_errors_name_the_problem_at_the_call(model):
    model.place("3001", "Red", cell=(0, 0), level=0, id="first")
    with pytest.raises(KitError, match=r"sunk 8\.0 LDU on the stud of 'first'.*level=3"):
        model.place("3001", "Blue", cell=(0, 0), level=2)
    with pytest.raises(KitError, match="collides with 'first'"):
        model.place("3001", "Blue", cell=(1, 0), level=0)
    with pytest.raises(KitError, match="has no port 'pin\\[9\\]'.*pin_hole\\[0\\]"):
        model.mate("2780", "Black", "pin[9]", to=model.place("32523", "Red", cell=(5, 5), level=0).port("pin_hole[0]"))


def test_pinned_beams_close_exactly(model, tmp_path):
    a = model.add("32524", "Red", at=(0, -100, 0), axes={"y": "Y", "z": "X"})
    first = model.mate("2780", "Black", "pin[0]", to=a.port("pin_hole[0]"))
    last = model.mate("2780", "Black", "pin[0]", to=a.port("pin_hole[6]"))
    b = model.mate("32524", "Blue", "pin_hole[0]", to=first.port("pin[2]"))
    assert np.allclose(b.port("pin_hole[6]").P, last.port("pin[2]").P, atol=1e-6)
    model.mate("3706", "Light_Bluish_Grey", "axle[0]", to=a.port("pin_hole[3]"))
    assert model.save(tmp_path / "beams.mpd", quiet=True)["checks_passed"]


def test_wheels_mate_to_pins_and_rims(model, tmp_path):
    plate = model.place("4600", "Black", cell=(0, 0), level=0)
    for pin in ("pin[0]", "pin[1]"):
        rim = model.mate("4624", "White", "pin_hole[0]", to=plate.port(pin))
        model.mate("3641", "Black", "tyre_bead[0]", to=rim.port("rim_seat[0]"))
    assert model.save(tmp_path / "wheels.mpd", quiet=True)["checks_passed"]


def test_sections_free_parts_and_rebuildable_plan(model, tmp_path):
    wing = model.section("wing", "A small wing module")
    wing.place("3020", "Blue", cell=(0, 0), level=0, id="wing-plate")
    wing.place("3068b", "White", cell=(0, 0), level=1, id="wing-tile")
    model.place("3001", "Red", cell=(0, 0), level=0, id="body")
    model.add(wing, None, at=(0, -24, 0), id="wing")
    model.place("3005", "Yellow", cell=(10, 10), level=0, id="crate", free="loose crate beside the model")
    path = tmp_path / "modules.mpd"
    report = model.save(path, quiet=True)
    assert report["checks_passed"] and report["free_parts"] == 1
    assert {m["module"] for m in report["modules"]} >= {"wing", "kit-test"}
    rebuilt = tmp_path / "rebuilt.mpd"
    result = subprocess.run([sys.executable, "-m", "ldraw_tools.cli", "build", str(path.with_suffix(".plan.json")),
                             "--output", str(rebuilt), "--contacts", "none", "--detail", "summary"],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout[-500:]
    lines = lambda p: [l for l in p.read_text().splitlines() if l.startswith("1 ")]
    assert lines(rebuilt) == lines(path)
    plan = json.loads(path.with_suffix(".plan.json").read_text())
    assert plan["sections"][0]["name"] == "kit-test.ldr"


@pytest.mark.parametrize("document", ["docs/agent/kit.md", "instructions.md"])
def test_documented_examples_run_and_pass(official, tmp_path, monkeypatch, capsys, document):
    import re
    source = re.search(r"```python\n(.*?)```", (ROOT / document).read_text(), re.S).group(1)
    monkeypatch.chdir(tmp_path)
    exec(compile(source, document, "exec"), {})
    assert capsys.readouterr().out.startswith("PASS")
    assert list(tmp_path.glob("output/*/*.plan.json"))


def test_wall_and_fill_helpers_make_connected_structures(model, tmp_path):
    ground = model.place("3811", "Green", cell=(0, 0), level=0)
    model.wall("Tan", start=(0, 0), length=8, courses=4, level=ground.top, along="X", prefix="front")
    model.wall("Tan", start=(0, 1), length=6, courses=4, level=ground.top, along="Z", prefix="side")
    floor = model.fill("Light_Bluish_Grey", cell=(10, 10), size=(6, 3), level=ground.top)
    assert {h.ref for h in floor} == {"3795.dat", "3666.dat"}
    assert model.save(tmp_path / "shed.mpd", quiet=True)["checks_passed"]


def test_axes_matrix_is_a_proper_rotation():
    rotation = axes_matrix({"y": "X", "z": "-Z"})
    assert np.allclose(rotation @ [0, 1, 0], [1, 0, 0]) and np.isclose(np.linalg.det(rotation), 1)


def test_place_on_any_stud_face(model, tmp_path):
    deck = model.place("3958", "Dark_Bluish_Grey", cell=(0, 0), level=0, id="deck")
    lamp = model.place("4070", "Light_Bluish_Grey", cell=(2, 0), level=deck.top, id="lamp")
    gun = model.place("4589", "Trans_Red", on=lamp.port("stud[0]"), id="gun")        # the headlight's side stud
    assert abs(gun.R[:, 1] @ np.array([0, 0, 1])) > 0.99                             # the cone now points along Z
    bracket = model.place("99780", "White", cell=(2, 2), level=deck.top, id="bracket")
    model.place("3069b", "White", on=bracket.port("stud[0]"), id="side-tile")        # a tile on the vertical face
    with pytest.raises(KitError, match="on= needs a stud"):
        model.place("3069b", "White", on=lamp.port("pin_hole[0]"))
    assert model.save(tmp_path / "on.mpd", quiet=True)["checks_passed"]


def test_mirror_swaps_left_and_right(model, tmp_path):
    hull = model.place("3958", "Dark_Bluish_Grey", cell=(0, 0), level=0, id="hull")
    wing = model.place("41769", "White", cell=(6, 1), level=0, id="wing-right")
    bridge = model.place("3710", "White", cell=(4, 2), level=wing.top, id="bridge-right")   # hull and wing studs
    left = model.mirror([wing, bridge], about=hull)
    assert [h.ref for h in left] == ["41770.dat", "3710.dat"] and [h.id for h in left] == ["wing-left", "bridge-left"]
    assert np.allclose(left[0].box[0][0] + wing.box[1][0], 2 * 50)                          # mirrored about x = 50
    assert model.save(tmp_path / "mirror.mpd", quiet=True)["checks_passed"]
