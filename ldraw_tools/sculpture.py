"""Rasterize coloured shape designs, pack rectangular bricks and export sculpture MPDs."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
from ldraw import Model
from ldraw.lines import Comment
from scipy.ndimage import binary_fill_holes, distance_transform_edt

from .builder import serialize_mpd
from .sculpture_packing import Voxel2Brick
from .sculpture_structure import BrickStructure, audit_supports, add_voxel_supports

MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_GRID_CELLS = 262144
MAX_EXTENT = 96

EMPTY = -1
MAX_WIDTH = MAX_DEPTH = 64
MAX_LAYERS = 96
MAX_SHAPES = 600
MAX_VOXELS = 65_536
COLOURS = set(range(512)) - {16, 24}


def _as_range(value, name, limit):
    if isinstance(value, (int, float)):
        value = [value, value]
    if not (isinstance(value, (list, tuple)) and len(value) == 2):
        raise ValueError(f"'{name}' must be [start, end] (inclusive integers)")
    try:
        numbers = [float(v) for v in value]
        if not all(np.isfinite(numbers)):
            raise ValueError("non-finite range")
        lo, hi = sorted(int(round(v)) for v in numbers)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"'{name}' must contain finite numbers") from exc
    lo, hi = max(lo, 0), min(hi, limit - 1)
    return lo, hi


def _floats(value, n, name):
    if isinstance(value, (int, float)) and n > 1:
        value = [value] * n
    if not (isinstance(value, (list, tuple)) and len(value) == n):
        raise ValueError(f"'{name}' must be a list of {n} numbers")
    try:
        out = [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"'{name}' must contain numbers") from exc
    if not all(np.isfinite(out)):
        raise ValueError(f"'{name}' must contain finite numbers")
    return out


def rasterize(design):
    """Apply the design's shapes in order. Returns (grid[x, z, layer] of colour or -1, unit)."""
    unit = str(design.get("layer_unit", "brick")).lower()
    if unit != "brick":
        raise ValueError("layer_unit must be 'brick'")
    grid_spec = design.get("grid") or {}
    try:
        dimensions = [grid_spec[k] for k in ("width", "depth", "layers")]
        if any(type(value) is not int for value in dimensions):
            raise ValueError("non-integer dimensions")
        width, depth, layers = dimensions
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("grid must have integer width, depth and layers") from exc
    if not (1 <= width <= MAX_WIDTH and 1 <= depth <= MAX_DEPTH and 1 <= layers <= MAX_LAYERS):
        raise ValueError(
            f"grid too large: max {MAX_WIDTH} x {MAX_DEPTH} studs and {MAX_LAYERS} {unit} layers"
        )
    shapes = design.get("shapes")
    if not isinstance(shapes, list) or not shapes:
        raise ValueError("shapes must be a non-empty list")
    if len(shapes) > MAX_SHAPES:
        raise ValueError(f"too many shapes ({len(shapes)}); max {MAX_SHAPES}")

    if width * depth * layers > MAX_GRID_CELLS:
        raise ValueError("Design bounds exceed 262144 grid cells; reduce resolution")
    grid = np.full((width, depth, layers), EMPTY, dtype=np.int32)
    X, Z, Y = np.meshgrid(np.arange(width), np.arange(depth), np.arange(layers), indexing="ij")

    for index, shape in enumerate(shapes):
        where = f"shapes[{index}]"
        if not isinstance(shape, dict):
            raise ValueError(f"{where} must be an object")
        kind = shape.get("shape")
        mode = shape.get("mode", "fill")
        if mode not in ("fill", "paint", "carve"):
            raise ValueError(f"{where}: mode must be fill, paint or carve")
        colour = shape.get("color")
        if mode != "carve" and kind != "layer":
            if type(colour) is not int or colour not in COLOURS:
                raise ValueError(
                    f"{where}: color {colour!r} is not in the palette. Use explicit LDraw colour codes (not inherited 16 or edge 24)"
                )

        if kind == "box":
            x0, x1 = _as_range(shape.get("x"), f"{where}.x", width)
            y0, y1 = _as_range(shape.get("y"), f"{where}.y", layers)
            z0, z1 = _as_range(shape.get("z"), f"{where}.z", depth)
            mask = np.zeros_like(grid, dtype=bool)
            if x0 <= x1 and y0 <= y1 and z0 <= z1:
                mask[x0 : x1 + 1, z0 : z1 + 1, y0 : y1 + 1] = True
        elif kind == "ellipsoid":
            cx, cy, cz = _floats(shape.get("center"), 3, f"{where}.center")
            rx, ry, rz = _floats(shape.get("radius"), 3, f"{where}.radius")
            if min(rx, ry, rz) <= 0:
                raise ValueError(f"{where}: radius values must be positive")
            mask = ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 <= 1.0
        elif kind == "cylinder":
            axis = shape.get("axis", "y")
            if axis not in ("x", "y", "z"):
                raise ValueError(f"{where}: axis must be x, y or z")
            others = {"x": ("y", "z"), "y": ("x", "z"), "z": ("x", "y")}[axis]
            ca, cb = _floats(shape.get("center"), 2, f"{where}.center")
            ra, rb = _floats(shape.get("radius"), 2, f"{where}.radius")
            if min(ra, rb) <= 0:
                raise ValueError(f"{where}: radius values must be positive")
            coords = {"x": X, "y": Y, "z": Z}
            limit = {"x": width, "y": layers, "z": depth}[axis]
            lo, hi = _as_range(shape.get("range"), f"{where}.range", limit)
            along = coords[axis]
            mask = (
                (((coords[others[0]] - ca) / ra) ** 2 + ((coords[others[1]] - cb) / rb) ** 2 <= 1.0)
                & (along >= lo)
                & (along <= hi)
            )
        elif kind == "layer":
            y0, y1 = _as_range(shape.get("y"), f"{where}.y", layers)
            rows = shape.get("rows")
            legend = shape.get("legend") or {}
            if not isinstance(rows, list) or not all(isinstance(r, str) for r in rows):
                raise ValueError(f"{where}: rows must be a list of strings (one per z row, front first)")
            if not isinstance(legend, dict):
                raise ValueError(f"{where}: legend must map single characters to color codes")
            colours = {}
            for char, code in legend.items():
                if (
                    not isinstance(char, str)
                    or len(char) != 1
                    or (mode != "carve" and (type(code) is not int or code not in COLOURS))
                ):
                    raise ValueError(
                        f"{where}: legend entry {char!r}: {code!r} must map one character to a palette color"
                    )
                colours[char] = code if isinstance(code, int) else EMPTY
            for z, row in enumerate(rows[:depth]):
                for x, char in enumerate(row[:width]):
                    if char in (".", " "):
                        continue
                    if char not in colours:
                        raise ValueError(f"{where}: character {char!r} in row {z} is not in the legend")
                    cells = (x, z, slice(y0, y1 + 1))
                    if mode == "carve":
                        grid[cells] = EMPTY
                    elif mode == "paint":
                        grid[cells] = np.where(grid[cells] != EMPTY, colours[char], EMPTY)
                    else:
                        grid[cells] = colours[char]
            continue
        else:
            raise ValueError(f"{where}: unknown shape {kind!r} (use box, ellipsoid, cylinder or layer)")

        if mode == "carve":
            grid[mask] = EMPTY
        elif mode == "paint":
            grid[mask & (grid != EMPTY)] = colour
        else:
            grid[mask] = colour

    filled = int((grid != EMPTY).sum())
    if filled == 0:
        raise ValueError("the design is empty after applying all shapes")
    if filled > MAX_VOXELS:
        raise ValueError(f"design has {filled} voxels; keep it under {MAX_VOXELS}")
    return grid, unit


def load_voxels(path):
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
            "voxels": [[int(x), int(y), int(z), int(grid[x, y, z])] for x, y, z in np.argwhere(grid >= 0)]
        }
    if not isinstance(data, dict) or set(data) != {"voxels"}:
        raise ValueError('Use {"voxels": [[x,y,z,colour], ...]} or a grid/shapes design')
    rows = data["voxels"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_VOXELS:
        raise ValueError(f"Supply between 1 and {MAX_VOXELS} voxels")
    cells = {}
    for row in rows:
        if (not isinstance(row, list) or len(row) != 4 or any(type(v) is not int for v in row)):
            raise ValueError("Each voxel must have four integers: x, y, z, LDraw colour")
        x, y, z, colour = row
        if (any(abs(v) > 100000 for v in (x, y, z)) or not 0 <= colour <= 511 or colour in {16, 24}):
            raise ValueError("Use bounded coordinates and explicit LDraw colours (not 16 or 24)")
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


def fill_interior(occupied, colours, thickness):
    """Add an interior shell while retaining the current surface for color constraints."""
    interior = binary_fill_holes(np.pad(occupied, 1))[1:-1, 1:-1, 1:-1] & ~occupied
    filled = occupied | (interior & (distance_transform_edt(~occupied) <= thickness))
    filled_colours = colours.copy()
    filled_colours[filled & ~occupied] = Counter(colours[occupied].tolist()).most_common(1)[0][0]
    return filled, filled_colours, occupied.copy()


def convert(path, *, name="sculpture.mpd", title="Sculpture model"):
    """Fill the shell, pack and reconnect bricks, then clean up and order the export."""
    original, colours = load_voxels(path)
    occupied, colours, surface = fill_interior(original, colours, 2)

    def pack(voxels, colours, surface_mask):
        bricks = Voxel2Brick(
            voxels, seed=42, colour_array=colours, surface_mask=surface_mask,
            use_colour_constraints=True, hard_constraints=True,
        )()
        return BrickStructure(bricks, world_dim=max(voxels.shape))

    structure = pack(occupied, colours, surface)
    requested = original.copy()
    audit = audit_supports(structure, requested)
    original_count = int(occupied.sum())
    repair_rounds = 0
    # Try hidden supports before changing the visible silhouette.
    for inside_only, broad in ((True, False), (True, True), (False, False), (False, True)):
        if not audit.conflicts.any():
            break
        budget = min(20_000, max(256, original_count)) - (int(occupied.sum()) - original_count)
        repaired, repaired_colours = add_voxel_supports(
            occupied, colours, audit, inside_only=inside_only, broad=broad, max_added=budget,
        )
        if repaired is occupied:
            continue
        padding = ((0, 0), (0, 0), (0, repaired.shape[2] - occupied.shape[2]))
        added = repaired & ~np.pad(occupied, padding)
        repaired_surface = np.pad(surface, padding)
        if not inside_only:
            repaired_surface |= added
        repaired_requested = np.pad(requested, padding) | added
        candidate = pack(repaired, repaired_colours, repaired_surface)
        candidate_audit = audit_supports(candidate, repaired_requested)
        repair_rounds += 1
        original_shape = tuple(slice(0, size) for size in original.shape)
        old_score = (int((audit.conflicts[original_shape] & original).sum()), int(audit.conflicts.sum()))
        new_score = (int((candidate_audit.conflicts[original_shape] & original).sum()), int(candidate_audit.conflicts.sum()))
        if new_score < old_score:
            occupied, colours, surface = repaired, repaired_colours, repaired_surface
            structure, audit = candidate, candidate_audit
            requested = repaired_requested
    section = Path(name).stem + ".ldr"
    model = Model(name=section)
    model.set_header(description=title, name=section, author="LDraw Nova", ldraw_org="Model")
    for brick in structure.ordered_bricks():
        model.add(brick.to_piece())
        model.add(Comment("STEP"))
    text = serialize_mpd(model)
    report = dict(checks_passed=True, mode="sculpture", algorithm="voxel2brick",
                  seed=42, input_voxels=int(original.sum()),
                  interior_support_voxels=original_count - int(original.sum()),
                  brick_count=len(structure.bricks), step_count=len(structure.bricks),
                  support_repair_rounds=repair_rounds,
                  support_voxels_added=int(occupied.sum()) - original_count,
                  unresolved_voxels=int(audit.conflicts.sum()),
                  physical_validity="not_proven")
    return text, report
