"""Fast check: connectivity from clean ports, collisions, stud seating, plan-id reports."""
import subprocess
import sys

import pytest

from conftest import mpd, ref
from ldraw_tools.check import check_model, compare_intended, format_report, mermaid_graph
from ldraw_tools.common import ROOT, library_path
from ldraw_tools.partcache import PartCache

PIN_UP = "0 -1 0 1 0 0 0 0 1"     # 2780 shaft (local X) along world Y


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
        report = check_model(ROOT / f"examples/technic-atlas/mechanisms/{name}/{name}.mpd", official, library)
        assert report["checks_passed"], format_report(report)


def test_crane_boom_is_reported_and_graphed(official, library):
    report = check_model(ROOT / "examples/atlas-crane/atlas-crane.mpd", official, library)
    floating = {m["module"]: m["floating"] for m in report["modules"]}
    assert floating["atc-boom-0"] == 181 and not report["checks_passed"]
    graph = mermaid_graph(report)
    assert graph.startswith("flowchart") and "atc_boom_0" in graph and ":::bad" in graph
    intended = compare_intended(report, "```mermaid\nflowchart LR\n  atc_super_0 -->|pins| atc_boom_0\n```")
    assert intended["missing"] == [["atc_boom_0", "atc_super_0"]]


def test_cli_prints_text_and_sets_exit_status(official):
    result = subprocess.run([sys.executable, "-m", "ldraw_tools.cli", "check", str(ROOT / "examples/bridge.mpd")],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0 and result.stdout.startswith("PASS")
