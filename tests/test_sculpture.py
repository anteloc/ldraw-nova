import json
import random
import subprocess
import sys

import numpy as np
import pytest

nx = pytest.importorskip("networkx")
pytest.importorskip("scipy")
from ldraw_tools.sculpture.brick_structure import Brick, ConnectivityBrickStructure
from ldraw_tools.sculpture.conversion import (
    convert,
    load_voxels,
    reorder_connected_bricks,
)


def source(tmp_path, rows):
    path = tmp_path / "voxels.json"
    path.write_text(json.dumps({"voxels": rows}))
    return path


def box(x=4, y=4, z=4):
    return [[i, j, k, 4] for i in range(x) for j in range(y) for k in range(z)]


def test_reproducible_bytes_with_shuffled_negative_coordinates(tmp_path):
    rows = box()
    original, report = convert(source(tmp_path, rows))
    random.Random(7).shuffle(rows)
    rows = [[x - 20, y - 30, z - 40, c] for x, y, z, c in rows]
    again, report2 = convert(source(tmp_path, rows))
    assert original == again and report == report2
    assert report["stud_components"] == 1 and report["connected_instruction_prefixes"]
    assert report["brick_count"] < 64
    assert original.count("0 STEP") == report["brick_count"]
    assert "\n" not in original.replace("\r\n", "")


def test_every_prefix_connected_with_hanging_branch():
    # A beam locks a second ground column, then unlocks a hanging tail.
    bricks = [
        Brick(h=1, w=1, x=0, y=0, z=0),
        Brick(h=1, w=4, x=0, y=0, z=1),
        Brick(h=1, w=1, x=0, y=2, z=0),
        Brick(h=1, w=1, x=0, y=3, z=0),
    ]
    ordered, _ = reorder_connected_bricks(bricks, (1, 4, 2))
    graph = ConnectivityBrickStructure((1, 4, 2))
    for brick in ordered:
        graph.add_brick(brick)
        assert nx.is_connected(graph.connection_graph)
    assert ordered[1].z == 1  # Not all ground bricks first: they do not interlock.
    assert set(ordered) == set(bricks)


def test_side_touching_is_not_a_stud_connection():
    bricks = [Brick(h=1, w=1, x=0, y=0, z=0), Brick(h=1, w=1, x=1, y=0, z=0)]
    with pytest.raises(ValueError, match="disconnected"):
        reorder_connected_bricks(bricks, (2, 1, 1))


def test_disconnected_input_never_silently_loses_subject_voxels(tmp_path):
    rows = [[0, 0, 0, 4], [10, 0, 0, 1]]
    _, report = convert(source(tmp_path, rows))
    repaired = report["voxel_data"]["voxels"]
    assert all(row in repaired for row in rows)
    assert report["exterior_support_voxels"] > 0 and report["unresolved_voxels"] == 0


def test_flat_section_is_repacked_after_support_additions(tmp_path, official):
    rows = box(20, 2, 1)
    text, report = convert(source(tmp_path, rows))
    assert report["support_repair_rounds"] > 0
    assert report["exterior_support_voxels"] > 0
    assert all(row in report["voxel_data"]["voxels"] for row in rows)
    assert text.count("0 STEP") == report["step_count"]
    # Verify the actual exported brick assembly, not only reported connectivity.
    from ldraw_tools.validation import validate_text
    from ldraw_tools.geometry import analyze_geometry

    model, issues = validate_text(text, official)
    assert not [issue for issue in issues if issue["severity"] == "error"]
    assert len(analyze_geometry(model, official)["optimistic_components"]) == 1


def test_floating_coloured_island_gets_support_without_recolouring(tmp_path):
    rows = box(2, 2, 3) + [[7, 0, 4, 1]]
    _, report = convert(source(tmp_path, rows))
    assert all(row in report["voxel_data"]["voxels"] for row in rows)
    assert report["support_repair_rounds"] > 0


def test_unresolved_colour_seam_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="disconnected.*after support repair"):
        convert(source(tmp_path, [[0, 0, 0, 4], [1, 0, 0, 1]]))


def test_supports_cannot_exceed_the_saved_voxel_input_budget(tmp_path, monkeypatch):
    from ldraw_tools.sculpture import conversion

    monkeypatch.setattr(conversion, "MAX_VOXELS", 2)
    with pytest.raises(ValueError, match="disconnected.*after support repair"):
        convert(source(tmp_path, [[0, 0, 0, 4], [10, 0, 0, 4]]))


def test_single_voxel_and_palette(tmp_path):
    text, report = convert(source(tmp_path, [[0, 0, 0, 1]]))
    assert report["brick_count"] == 1 and "1 1 " in text
    assert "3005.dat" in text


def test_hollow_shell_uses_only_enclosed_support(tmp_path):
    rows = [row for row in box(5, 5, 5) if any(v in (0, 4) for v in row[:3])]
    _, report = convert(source(tmp_path, rows))
    assert report["input_voxels"] == 98 and report["interior_support_voxels"] == 27


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [[0, 0, 0]],
        [[0, 0, 0.5, 4]],
        [[True, 0, 0, 4]],
        [[0, 0, 0, 16]],
        [[0, 0, 0, 24]],
        [[0, 0, 0, 4], [0, 0, 0, 1]],
        [[0, 0, 0, 4], [100, 0, 0, 4]],
    ],
)
def test_bad_input_rejected_before_packing(tmp_path, rows):
    with pytest.raises(ValueError):
        load_voxels(source(tmp_path, rows))


def test_cli_rejects_without_overwriting_output(tmp_path):
    path = source(tmp_path, [[0, 0, 0, 4], [1, 0, 0, 1]])
    output = tmp_path / "sculpture.mpd"
    output.write_text("previous valid model")
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "ldraw_tools.cli",
            "sculpture",
            str(path),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    assert run.returncode != 0 and not json.loads(run.stdout)["checks_passed"]
    assert output.read_text() == "previous valid model"


def test_real_library_export_validates(tmp_path, official):
    from ldraw_tools.validation import validate_text
    from ldraw_tools.geometry import analyze_geometry

    text, report = convert(source(tmp_path, box()))
    model, issues = validate_text(text, official)
    assert model is not None and not [d for d in issues if d["severity"] == "error"]
    geometry = analyze_geometry(model, official)
    assert not [d for d in geometry["diagnostics"] if d["severity"] == "error"]
    assert len(geometry["optimistic_components"]) == 1
    assert geometry["occurrence_count"] == report["brick_count"]
