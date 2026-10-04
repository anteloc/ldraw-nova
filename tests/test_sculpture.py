import json
import random
import subprocess
import sys

import pytest

pytest.importorskip("networkx")
pytest.importorskip("scipy")
from ldraw_tools.sculpture import (
    convert,
    load_voxels,
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
    assert report["stud_components"] == 1
    assert report["brick_count"] < 64
    assert original.count("0 STEP") == report["brick_count"]
    assert "\n" not in original.replace("\r\n", "")


def test_disconnected_islands_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="disconnected"):
        convert(source(tmp_path, [[0, 0, 0, 4], [3, 0, 0, 4]]))


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
    path = source(tmp_path, [[0, 0, 0, 4], [3, 0, 0, 4]])
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
