"""Strict, reproducible adapter around BrickBuilderAI's voxel packing algorithms."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.ndimage import binary_fill_holes, distance_transform_edt

from .brick_structure import (
    ConnectivityBrickStructure,
    brick_support_type,
    reorder_bricks_for_stability,
)
from .voxel2brick import Voxel2Brick
from .voxel_support import add_voxel_supports, audit_supports
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
            'Use {"voxels": [[x,y,z,colour], ...]} or a BrickBuilder grid/shapes design'
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
            "Sculpture has disconnected stud components; revise the subject's supports and retry"
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
    # Same initial two-cell interior shell as BrickBuilder's shared converter.
    interior = binary_fill_holes(np.pad(original, 1))[1:-1, 1:-1, 1:-1] & ~original
    occupied = original | (interior & (distance_transform_edt(~original) <= 2))
    if int(occupied.sum()) > MAX_VOXELS:
        occupied = original.copy()  # Keep saved voxel data within the same input cap.
    added = occupied & ~original
    palette, counts = np.unique(colours[original], return_counts=True)
    colours[added] = int(palette[np.argmax(counts)])

    def pack(voxels, palette, surface):
        solver = Voxel2Brick(
            voxels,
            seed=42,
            color_array=palette,
            run_stability_passes=False,
            use_color_constraints=True,
            hard_constraints=True,
            wc=1000.0,
            max_failures=100,
            surface_mask=surface,
        )
        with redirect_stdout(StringIO()):
            return solver()

    surface = original.copy()
    bricks = pack(occupied, colours, surface)
    audit = audit_supports(bricks, occupied)
    rounds = 0
    accepted_repairs = []
    initial_count = int(occupied.sum())
    original_region = tuple(slice(0, size) for size in original.shape)
    # Ported from BrickBuilder's inside-first repair pipeline: re-pack and audit
    # every candidate before accepting additions. No pedestal is ever inserted.
    for inside_only, broad in (
        (True, False),
        (True, True),
        (False, False),
        (False, True),
    ):
        if not audit.conflicts.any():
            break
        budget = min(20_000, max(256, initial_count)) - (
            int(occupied.sum()) - initial_count
        )
        budget = min(budget, MAX_VOXELS - int(occupied.sum()))
        repaired, repaired_colours = add_voxel_supports(
            occupied,
            colours,
            audit,
            inside_only=inside_only,
            broad=broad,
            max_added=budget,
            max_grid_cells=MAX_GRID_CELLS,
            max_extent=MAX_EXTENT,
        )
        if repaired is occupied:
            continue
        padding = ((0, 0), (0, 0), (0, repaired.shape[2] - occupied.shape[2]))
        additions = repaired & ~np.pad(occupied, padding)
        repaired_surface = np.pad(surface, padding)
        if not inside_only:
            repaired_surface |= additions
        candidate = pack(repaired, repaired_colours, repaired_surface)
        candidate_audit = audit_supports(candidate, repaired)
        rounds += 1
        old_score = (
            int((audit.conflicts[original_region] & original).sum()),
            int(audit.conflicts.sum()),
        )
        new_score = (
            int((candidate_audit.conflicts[original_region] & original).sum()),
            int(candidate_audit.conflicts.sum()),
        )
        if new_score < old_score:
            occupied, colours, surface = repaired, repaired_colours, repaired_surface
            bricks, audit = candidate, candidate_audit
            accepted_repairs.append(
                dict(
                    placement="interior" if inside_only else "exterior",
                    broad=broad,
                    voxels=int(additions.sum()),
                )
            )
    if audit.conflicts.any():
        raise ValueError(
            f"Sculpture has {int(audit.conflicts.sum())} disconnected voxels after support repair; revise the subject's supports and retry"
        )
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
    exported_colours = np.zeros(occupied.shape, dtype=np.int32)
    for brick in ordered:
        exported_colours[brick.slice] = brick.color
    if not np.array_equal(
        exported_colours[original_region][original], colours[original_region][original]
    ):
        raise ValueError(
            "Packing recoloured subject voxels; revise the colour seams and retry"
        )
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
        interior_support_voxels=int(added.sum())
        + sum(r["voxels"] for r in accepted_repairs if r["placement"] == "interior"),
        exterior_support_voxels=sum(
            r["voxels"] for r in accepted_repairs if r["placement"] == "exterior"
        ),
        support_repair_rounds=rounds,
        accepted_repairs=accepted_repairs,
        unresolved_voxels=0,
        brick_count=len(ordered),
        step_count=len(ordered),
        stud_components=1,
        connected_instruction_prefixes=True,
        hanging_steps=hanging,
        physical_validity="not_proven",
        voxel_data={
            "voxels": [
                [int(x), int(y), int(z), int(exported_colours[x, y, z])]
                for x, y, z in np.argwhere(occupied)
            ]
        },
    )
    return text, report
