"""Fast check: connectivity from clean ports, collisions, stud seating, plan-id reports."""
import subprocess
import sys

import pytest

from conftest import mpd, ref
from ldraw_tools.check import check_model, compare_intended, format_report, mermaid_graph
from ldraw_tools.common import ROOT, library_path
from ldraw_tools.partcache import PartCache

PIN_UP = "0 -1 0 1 0 0 0 0 1"     # 2780 shaft (local X) along world Y
FIXTURES = ROOT / "tests/fixtures"


@pytest.fixture(scope="module")
def library(official):
    return library_path()


def run(official, library, tmp_path, body, **options):
    path = tmp_path / "model.mpd"
    path.write_text(mpd(body), newline="")
    return check_model(path, official, library, **options)


def test_clean_ports_drop_primitive_guesses(official, library):
    liftarm = PartCache(official, library).get("32140")
    holes = [p for p in liftarm.ports if p["kind"] == "pin_hole"]
    # Four centred bores, not the 26 face/cut-out features pyldraw3 infers from primitives.
    assert len(holes) == 4 and all(p["half"] == 10 and p["p"][1] == 0 for p in holes)
    assert [p["kind"] for p in liftarm.ports].count("axle_hole") == 1


def test_no_inferred_guesses_fake_a_connection(official, library, tmp_path):
    cache = PartCache(official, library)
    # Axle holes are not read as male axles, so a bush cannot "mate" a gear on an empty axle line.
    for code in ("3713", "3941", "94925"):
        assert not [p for p in cache.get(code).ports if p["kind"] == "axle"], code
    # A 1 x 8 brick one plate above a plate's studs is not connected to it.
    gap = run(official, library, tmp_path, "\n".join([ref("3460.dat", 15, "0 -8 0"), ref("3008.dat", 4, "0 -40 0")]))
    assert gap["floating_count"] == 1
    seated = run(official, library, tmp_path, "\n".join([ref("3460.dat", 15, "0 -8 0"), ref("3008.dat", 4, "0 -32 0")]))
    assert seated["checks_passed"], format_report(seated)


def test_part_without_authored_sockets_takes_clipped_inferred_receptacles(official):
    # Library 2026-05 remodelled wings 41769a/41770a: authored studs, receptacles only inferred.
    from types import SimpleNamespace
    from ldraw_tools.partcache import AUTHORED, clean_ports
    brick = official.geometry("3001")
    studs_only = SimpleNamespace(connection_metadata=brick.connection_metadata, top_studs=[], connections=[
        f for f in brick.connections if f.source not in AUTHORED or str(f.role) == "male"])
    ports, coverage = clean_ports(studs_only, body=([-40, 0, -20], [40, 24, 20]))
    sockets = [p for p in ports if p["kind"] == "stud_receptacle"]
    assert coverage == "complete" and sockets
    # Clipped to the body: no socket reaches below the brick's bottom face (y = 24).
    assert all(p["p"][1] + p["half"] <= 24 + 1e-6 for p in sockets)
    assert not [p for p in ports if p["kind"] in ("axle", "pin_hole")]


def test_hinge_plates_keep_their_pivot_and_mate_at_an_angle(official, library, tmp_path):
    from ldraw_tools.kit import Model
    cache = PartCache(official, library)
    # The fingers come from the h1/h2 primitives' authored data: pivot across the plate (Z), not along it.
    for code in ("4275b", "4276b"):
        [hinge] = [p for p in cache.get(code).ports if p["kind"] == "hinge"]
        assert hinge["p"] == [30, 4, 0] and abs(hinge["axis"][2]) == 1 and hinge["half"] == 10
    m = Model("hinge", "Classic hinge plates turned 30 degrees")
    base = m.place("4275b", "Light_Bluish_Grey", cell=(0, 0), level=0, id="base")
    m.mate("4276b", "Light_Bluish_Grey", "hinge[0]", to=base.port("hinge[0]"), roll=30, id="flap")
    report = m.save(tmp_path / "hinge.mpd", quiet=True)
    assert report["checks_passed"], format_report(report)


def test_partial_ports_drop_guesses_of_authored_kinds(official, library):
    # Inverted slope 4287: authored top studs; the inferred studs inside its body are gone.
    studs = [p for p in PartCache(official, library).get("4287").ports if p["kind"] == "stud"]
    assert len(studs) == 3 and all(p["p"][1] < 0 for p in studs)


def test_plate_without_authored_sockets_gets_one_under_each_stud(official):
    # Library 2026-05 wing plates 43723a: authored studs only, and no tube primitives to infer from.
    from types import SimpleNamespace
    from ldraw_tools.partcache import AUTHORED, clean_ports
    plate = official.geometry("3020")
    studs_only = SimpleNamespace(connection_metadata=plate.connection_metadata, top_studs=[], connections=[
        f for f in plate.connections if f.source in AUTHORED and str(f.role) == "male"])
    ports, _ = clean_ports(studs_only, body=([-40, 0, -20], [40, 8, 20]))
    sockets = [p for p in ports if p["kind"] == "stud_receptacle"]
    assert len(sockets) == 8 and all(p["p"][1] + p["half"] == 8 for p in sockets)


def test_loose_figures_are_reported_not_failed(official, library, tmp_path):
    report = run(official, library, tmp_path, "\n".join([ref("3001.dat", 4, "0 0 0"), ref("3626bp01.dat", 14, "200 0 0")]))
    assert report["checks_passed"] and report["figure_parts"] == 1


def test_official_tight_fits_are_reviews(official, library):
    # UCS Y-wing armour (75181): a grille tile sits 2 LDU into a bar pin by design.
    report = check_model(FIXTURES / "official/y-wing-armour.mpd", official, library)
    assert report["checks_passed"] and report["review_count"], format_report(report)
    from ldraw_tools.common import dumps
    assert '"reviews"' in dumps(report)                       # --json and --report serialise review entries


def test_embedded_copy_named_by_number_keeps_its_family(official, library):
    # The 42110 gearbox embeds clutch gear 35188 as a file titled only "35188"; its
    # meshing with a driving ring is a review, not a collision.
    report = check_model(FIXTURES / "official/four-speed-gearbox.mpd", official, library)
    assert report["checks_passed"], format_report(report)
    assert report["review_count"] > 0


def test_pin_connects_registry_and_non_registry_parts(official, library, tmp_path):
    report = run(official, library, tmp_path, "\n".join([
        ref("32140.dat", 71, "0 0 -40"), ref("32523.dat", 71, "0 -20 0"), ref("2780.dat", 0, "0 -10 20", PIN_UP)]))
    assert report["checks_passed"] and report["floating_count"] == 0 and report["collision_count"] == 0


def test_axle_through_round_hole_is_a_bearing(official, library, tmp_path):
    report = run(official, library, tmp_path, "\n".join([
        ref("32523.dat", 71, "0 0 0"), ref("3705.dat", 0, "0 0 0", PIN_UP)]))
    assert report["floating_count"] == 0 and report["collision_count"] == 0


def test_unbridged_side_by_side_plates_float(official, library, tmp_path):
    halves = [ref("3034.dat", 15, "0 -8 -20"), ref("3034.dat", 15, "0 -8 20")]
    report = run(official, library, tmp_path, "\n".join(halves))
    assert report["floating_count"] == 1 and not report["checks_passed"]
    bridged = run(official, library, tmp_path, "\n".join([*halves, ref("3020.dat", 4, "0 -16 0", "0 0 1 0 1 0 -1 0 0")]))
    assert bridged["checks_passed"], format_report(bridged)


def test_stud_seating_and_overlaps(official, library, tmp_path):
    seated = run(official, library, tmp_path, "\n".join([ref("3001.dat", 4, "0 0 0"), ref("3001.dat", 1, "0 -24 0")]))
    assert seated["checks_passed"]
    sunk = run(official, library, tmp_path, "\n".join([ref("3001.dat", 4, "0 0 0"), ref("3001.dat", 1, "0 -20 0")]))
    assert sunk["seating_count"] and sunk["seating"][0]["offset"] == pytest.approx(-4)
    overlapping = run(official, library, tmp_path, "\n".join([ref("3001.dat", 4, "0 0 0"), ref("3001.dat", 1, "20 0 0")]))
    assert overlapping["collision_count"] == 1
    duplicate = run(official, library, tmp_path, "\n".join([ref("3001.dat", 4, "0 0 0"), ref("3001.dat", 1, "0 0 0")]))
    assert duplicate["duplicate_count"] == 1


def test_declarations_and_plan_ids(official, library, tmp_path):
    body = "\n".join(["0 // base: ground brick", ref("3001.dat", 4, "0 0 0"),
                      "0 // crate: loose crate", "0 !NOVA FREE stands loose beside the wall", ref("3003.dat", 1, "200 0 0")])
    report = run(official, library, tmp_path, body)
    assert report["checks_passed"] and report["free_parts"] == 1
    loose = run(official, library, tmp_path, body.replace("0 !NOVA FREE stands loose beside the wall\n", ""))
    assert loose["floating_groups"][0]["parts"][0]["id"] == "crate"


def test_expert_mechanism_extracts_are_clean(official, library):
    for name in ("four-bar-lift", "cam-follower-engine", "double-cardan-shaft"):
        report = check_model(FIXTURES / f"official/{name}.mpd", official, library)
        assert report["checks_passed"], format_report(report)


def test_floating_module_is_reported_and_graphed(official, library, tmp_path):
    from ldraw_tools.kit import Model
    m = Model("yard", "A base and a boom nobody attached")
    boom = m.section("boom", "Boom")
    boom.place("3001", "Yellow", cell=(0, 0), level=0, id="boom-brick")
    base = m.place("3001", "Red", cell=(0, 0), level=0, id="base")
    m.place("3001", "Red", cell=(0, 0), level=base.top, id="base-top")
    m.add(boom, None, at=(200, 0, 0), id="boom")
    report = m.save(tmp_path / "yard.mpd", quiet=True)
    floating = {mod["module"]: mod["floating"] for mod in report["modules"]}
    assert floating["boom"] == 1 and not report["checks_passed"]
    graph = mermaid_graph(report)
    assert graph.startswith("flowchart") and "boom" in graph and ":::bad" in graph
    intended = compare_intended(report, "```mermaid\nflowchart LR\n  yard -->|studs| boom\n```")
    assert intended["missing"] == [["boom", "yard"]]


def test_cli_prints_text_and_sets_exit_status(official):
    result = subprocess.run([sys.executable, "-m", "ldraw_tools.cli", "check", str(FIXTURES / "bridge.mpd")],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0 and result.stdout.startswith("PASS")
