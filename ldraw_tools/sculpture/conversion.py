"""Strict, reproducible adapter around BrickBuilderAI's voxel packing algorithms."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.ndimage import binary_fill_holes

from .brick_structure import (
    ConnectivityBrickStructure,
    brick_support_type,
    reorder_bricks_for_stability,
)
from .voxel2brick import Voxel2Brick

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
    if not isinstance(data, dict) or set(data) != {"voxels"}:
        raise ValueError(
            'Use a JSON object containing only "voxels": [[x,y,z,colour], ...]'
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


def reorder_connected_bricks(bricks, shape):
    """Use the original instruction priorities, while keeping every prefix connected.

    Ground bricks are not implicitly connected through the table. A hanging brick
    may attach to previously placed studs from above; no floating force-placement
    is exported. This is a connection check, not a force/stress analysis.
    """
    preferred, _ = reorder_bricks_for_stability(sorted(bricks), shape)
    structure = ConnectivityBrickStructure(shape)
    structure.add_bricks(preferred)
    if structure.n_components() != 1:
        raise ValueError(
            "Sculpture has disconnected stud components; add a connected base or supports and retry"
        )
    graph = structure.connection_graph
    ground = [node for node, brick in structure.bricks.items() if brick.z == 0]
    seed = min(ground)
    placed = {seed}
    ordered = [structure.bricks[seed]]
    occupancy = np.zeros(shape, dtype=bool)
    occupancy[ordered[0].slice] = True
    frontier = set(graph.neighbors(seed))
    hanging = 0
    while frontier:
        below = [
            node
            for node in frontier
            if brick_support_type(occupancy, structure.bricks[node])
            in {"ground", "below"}
        ]
        node = min(below or frontier)
        brick = structure.bricks[node]
        if brick_support_type(occupancy, brick) == "above":
            hanging += 1
        ordered.append(brick)
        occupancy[brick.slice] = True
        placed.add(node)
        frontier.remove(node)
        frontier.update(set(graph.neighbors(node)) - placed)
    if len(ordered) != len(bricks):
        raise ValueError("Instruction ordering did not visit the complete sculpture")
    return ordered, hanging


def convert(
    path: str | Path, *, name: str = "sculpture.mpd", title: str = "3D sculpture"
):
    if (
        not name.lower().endswith(".mpd")
        or any(c in name + title for c in "\r\n\x00")
        or any(ord(c) < 32 for c in name + title)
        or "/" in name
        or "\\" in name
    ):
        raise ValueError("Use a single-line title and a plain .mpd filename")
    original, colours = load_voxels(path)
    # Only reinforce enclosed air: no visible exterior additions or lost input cells.
    occupied = binary_fill_holes(np.pad(original, 1))[1:-1, 1:-1, 1:-1]
    added = occupied & ~original
    palette, counts = np.unique(colours[original], return_counts=True)
    colours[added] = int(palette[np.argmax(counts)])
    solver = Voxel2Brick(
        occupied,
        seed=42,
        color_array=colours,
        run_stability_passes=True,
        use_color_constraints=True,
        hard_constraints=True,
        surface_mask=original,
    )
    with redirect_stdout(StringIO()):
        bricks = solver()
    exported = np.zeros(occupied.shape, dtype=bool)
    for brick in bricks:
        if exported[brick.slice].any():
            raise ValueError("Packing produced overlapping bricks")
        exported[brick.slice] = True
    if not np.array_equal(exported, occupied):
        raise ValueError(
            "Packing did not preserve every voxel; adjust supports and retry"
        )
    ordered, hanging = reorder_connected_bricks(bricks, occupied.shape)
    body = "".join(
        brick.to_ldr(color=brick.color).replace(brick.part_id, brick.part_id.lower())
        for brick in ordered
    )
    section_name = Path(name).stem + ".ldr"
    text = (
        f"0 FILE {section_name}\n0 {title}\n0 Name: {section_name}\n0 Author: LDraw Nova\n"
        f"0 !LDRAW_ORG Model\n{body}0 NOFILE\n"
    ).replace("\n", "\r\n")
    report = dict(
        checks_passed=True,
        mode="sculpture",
        algorithm="brickbuilder-voxel2brick",
        seed=42,
        input_voxels=int(original.sum()),
        interior_support_voxels=int(added.sum()),
        brick_count=len(ordered),
        step_count=len(ordered),
        stud_components=1,
        connected_instruction_prefixes=True,
        hanging_steps=hanging,
        physical_validity="not_proven",
    )
    return text, report
