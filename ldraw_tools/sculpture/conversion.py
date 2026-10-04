"""Convert colored voxel designs into reproducible rectangular-brick models."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_fill_holes, distance_transform_edt

from .brick_structure import (
    ConnectivityBrickStructure,
    reorder_bricks_for_stability,
)
from .voxel2brick import Voxel2Brick
from .design import rasterize

MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_VOXELS = 65536
MAX_GRID_CELLS = 262144
MAX_EXTENT = 96


def load_voxels(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Read integer [x,y,z,LDraw colour] rows, with z in full brick-height layers."""
    path = Path(path)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Sculpture input exceeds 8 MB")
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "shapes" in data:
        if set(data) - {"grid", "shapes", "title", "layer_unit", "hollow"}:
            raise ValueError(
                "Design input supports grid, shapes, title, layer_unit and hollow; add requested bases explicitly as shapes"
            )
        grid, _ = rasterize(data)
        data = {
            "voxels": [
                [int(x), int(y), int(z), int(grid[x, y, z])]
                for x, y, z in np.argwhere(grid >= 0)
            ]
        }
    if not isinstance(data, dict) or set(data) != {"voxels"}:
        raise ValueError(
            'Use {"voxels": [[x,y,z,colour], ...]} or a grid/shapes design'
        )
    rows = data["voxels"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_VOXELS:
        raise ValueError(f"Supply between 1 and {MAX_VOXELS} voxels")
    cells = {}
    for row in rows:
        if (
            not isinstance(row, list)
            or len(row) != 4
            or any(type(v) is not int for v in row)
        ):
            raise ValueError(
                "Each voxel must have four integers: x, y, z, LDraw colour"
            )
        x, y, z, colour = row
        if (
            any(abs(v) > 100000 for v in (x, y, z))
            or not 0 <= colour <= 511
            or colour in {16, 24}
        ):
            raise ValueError(
                "Use bounded coordinates and explicit LDraw colours (not 16 or 24)"
            )
        key = (x, y, z)
        if key in cells and cells[key] != colour:
            raise ValueError("Conflicting colours at the same voxel")
        cells[key] = colour
    coordinates = np.array(sorted(cells), dtype=np.int32)
    origin = coordinates.min(axis=0)
    shape = coordinates.max(axis=0) - origin + 1
    if max(shape) > MAX_EXTENT or int(np.prod(shape)) > MAX_GRID_CELLS:
        raise ValueError(
            "Sculpture bounds must fit 96 layers per axis and 262144 grid cells; reduce resolution"
        )
    occupied = np.zeros(tuple(shape), dtype=bool)
    colours = np.zeros(tuple(shape), dtype=np.int32)
    for coordinate in coordinates:
        point = tuple(coordinate - origin)
        occupied[point] = True
        colours[point] = cells[tuple(coordinate)]
    return occupied, colours


def convert(path: str | Path, *, name: str = "sculpture.mpd", title: str = "Sculpture model"):
    """Fill interior space, pack bricks with a fixed seed and order build steps."""
    original, colours = load_voxels(path)
    occupied = original.copy()
    interior = binary_fill_holes(np.pad(original, 1))[1:-1, 1:-1, 1:-1] & ~original
    # Fill two layers inward, using the dominant colour.
    occupied |= interior & (distance_transform_edt(~original) <= 2)
    if int(occupied.sum()) > MAX_VOXELS:
        raise ValueError("Interior fill exceeds the sculpture voxel budget")
    from collections import Counter
    colours[occupied & ~original] = Counter(colours[original].tolist()).most_common(1)[0][0]
    with redirect_stdout(StringIO()):
        bricks = Voxel2Brick(
            occupied, seed=42, color_array=colours, surface_mask=original,
            run_stability_passes=False, use_color_constraints=True,
            hard_constraints=True, wc=1000.0, max_failures=100,
        )()
    exported = np.zeros(occupied.shape, dtype=bool)
    for brick in bricks:
        if exported[brick.slice].any():
            raise ValueError("Packing produced overlapping bricks")
        exported[brick.slice] = True
    if not np.array_equal(exported, occupied):
        raise ValueError("Packing did not preserve every voxel; revise the design and retry")
    structure = ConnectivityBrickStructure(occupied.shape)
    structure.add_bricks(bricks)
    if structure.n_components() != 1:
        raise ValueError("Sculpture has disconnected stud components; revise the design and retry")
    with redirect_stdout(StringIO()):
        ordered, deferred = reorder_bricks_for_stability(sorted(bricks), occupied.shape)
    if deferred:
        raise ValueError("Sculpture has unsupported build steps; revise the design and retry")
    body = "".join(brick.to_ldr(color=brick.color).replace(brick.part_id, brick.part_id.lower())
                   for brick in ordered)
    section = Path(name).stem + ".ldr"
    text = (f"0 FILE {section}\n0 {title}\n0 Name: {section}\n0 Author: LDraw Nova\n"
            f"0 !LDRAW_ORG Model\n{body}0 NOFILE\n").replace("\n", "\r\n")
    report = dict(checks_passed=True, mode="sculpture", algorithm="voxel2brick",
                  seed=42, input_voxels=int(original.sum()),
                  interior_support_voxels=int((occupied & ~original).sum()),
                  brick_count=len(ordered), step_count=len(ordered), stud_components=1,
                  physical_validity="not_proven")
    return text, report
