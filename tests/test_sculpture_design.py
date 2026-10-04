import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

pytest.importorskip("scipy")
pytest.importorskip("networkx")
from ldraw_tools.sculpture.design import rasterize
from ldraw_tools.sculpture.conversion import convert, load_voxels


def design(shapes, **kwargs):
    return {"grid": {"width": 4, "depth": 4, "layers": 4}, "shapes": shapes, **kwargs}


def test_brickbuilder_design_axes_and_raw_voxels_produce_identical_bricks(tmp_path):
    data = design([{"shape": "box", "x": [0, 2], "y": [0, 3], "z": [0, 1], "color": 4}])
    path = tmp_path / "design.json"
    path.write_text(json.dumps(data))
    occupied, _ = load_voxels(path)
    assert occupied.shape == (3, 2, 4)  # Shape y is vertical; raw z is vertical.
    text, report = convert(path)
    path.write_text(
        json.dumps(
            {
                "voxels": [
                    [x, y, z, 4] for x in range(3) for y in range(2) for z in range(4)
                ]
            }
        )
    )
    raw, raw_report = convert(path)
    assert text == raw and report == raw_report


def test_ordered_shapes_paint_and_carve_without_painting_air():
    grid, unit = rasterize(
        design(
            [
                {"shape": "box", "x": [0, 1], "y": [0, 1], "z": [0, 1], "color": 4},
                {
                    "shape": "box",
                    "x": [0, 3],
                    "y": 1,
                    "z": [0, 3],
                    "color": 1,
                    "mode": "paint",
                },
                {"shape": "box", "x": 0, "y": 0, "z": 0, "mode": "carve"},
            ]
        )
    )
    assert unit == "brick" and int((grid >= 0).sum()) == 7
    assert grid[0, 0, 0] == -1 and grid[1, 1, 1] == 1 and grid[3, 3, 1] == -1


def test_ellipsoid_cylinder_and_layer_follow_brickbuilder_schema():
    grid, _ = rasterize(
        design(
            [
                {
                    "shape": "ellipsoid",
                    "center": [1, 1, 1],
                    "radius": [1, 1, 1],
                    "color": 4,
                },
                {
                    "shape": "cylinder",
                    "axis": "y",
                    "center": [1, 1],
                    "radius": 0.5,
                    "range": [0, 3],
                    "color": 1,
                },
                {
                    "shape": "layer",
                    "y": 3,
                    "rows": ["....", ".A.."],
                    "legend": {"A": 14},
                },
            ]
        )
    )
    assert np.array_equal(grid[1, 1, :], [1, 1, 1, 14])
    assert grid[0, 1, 1] == 4 and grid[0, 0, 0] == -1


@pytest.mark.parametrize(
    "updates",
    [
        {"grid": {"width": True, "depth": 4, "layers": 4}},
        {"grid": {"width": 64, "depth": 64, "layers": 96}},
        {"layer_unit": "plate"},
        {"shapes": [None]},
        {"shapes": [{"shape": "box", "x": [None, 3], "y": 0, "z": 0, "color": 4}]},
        {"shapes": [{"shape": "box", "x": 0, "y": 0, "z": 0, "color": 16}]},
    ],
)
def test_malformed_or_oversized_design_is_rejected(updates):
    data = design([{"shape": "box", "x": 0, "y": 0, "z": 0, "color": 4}])
    data.update(updates)
    with pytest.raises(ValueError):
        rasterize(data)


def test_cli_exports_design_without_overwriting_source(tmp_path, official):
    path = tmp_path / "design.json"
    path.write_text(
        json.dumps(
            {
                "grid": {"width": 4, "depth": 4, "layers": 4},
                "shapes": [
                    {"shape": "box", "x": [0, 3], "y": [0, 3], "z": [0, 3], "color": 4}
                ],
            }
        )
    )
    original = path.read_text()
    output = tmp_path / "model.mpd"
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
    assert run.returncode == 0, run.stdout + run.stderr
    report = json.loads(run.stdout)
    assert path.read_text() == original
    assert output.is_file() and report["stud_components"] == 1


def test_sculpture_guide_retains_main_no_base_and_review_rules():
    guide = (
        Path(__file__).resolve().parents[1] / "docs/agent/sculptures.md"
    ).read_text()
    assert "Do not add a display base, stand, plinth, or ground plate" in guide
    assert "unless the user explicitly asks for a base or stand" in guide
    assert "at most 299" in guide and "publish_model" in guide
    assert "fixed-seed color-constrained rectangular-brick packing" in guide
