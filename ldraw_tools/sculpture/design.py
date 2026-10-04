"""Rasterize the same compact shape designs used by llmToBricks."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

EMPTY = -1
MAX_WIDTH = MAX_DEPTH = 64
MAX_LAYERS = {"brick": 96}
MAX_SHAPES = 600
MAX_VOXELS = 65_536
UNITS = {"brick"}


def load_palette():
    return {code: (str(code), "") for code in range(512) if code not in {16, 24}}


def palette_prompt_text(palette):
    return "explicit LDraw colour codes (not inherited 16 or edge 24)"


class DesignError(ValueError):
    """The design is invalid; the message explains what the agent should revise."""


def _as_range(value: Any, name: str, limit: int) -> Tuple[int, int]:
    if isinstance(value, (int, float)):
        value = [value, value]
    if not (isinstance(value, (list, tuple)) and len(value) == 2):
        raise DesignError(f"'{name}' must be [start, end] (inclusive integers)")
    try:
        numbers = [float(v) for v in value]
        if not all(np.isfinite(numbers)):
            raise ValueError("non-finite range")
        lo, hi = sorted(int(round(v)) for v in numbers)
    except (TypeError, ValueError, OverflowError) as exc:
        raise DesignError(f"'{name}' must contain finite numbers") from exc
    lo, hi = max(lo, 0), min(hi, limit - 1)
    return lo, hi


def _floats(value: Any, n: int, name: str) -> List[float]:
    if isinstance(value, (int, float)) and n > 1:
        value = [value] * n
    if not (isinstance(value, (list, tuple)) and len(value) == n):
        raise DesignError(f"'{name}' must be a list of {n} numbers")
    try:
        out = [float(v) for v in value]
    except (TypeError, ValueError) as exc:
        raise DesignError(f"'{name}' must contain numbers") from exc
    if not all(np.isfinite(out)):
        raise DesignError(f"'{name}' must contain finite numbers")
    return out


def rasterize(
    design: Dict[str, Any], palette: Optional[Dict[int, Tuple[str, str]]] = None
) -> Tuple[np.ndarray, str]:
    """Apply the design's shapes in order. Returns (grid[x, z, layer] of color or -1, unit)."""
    palette = palette if palette is not None else load_palette()
    unit = str(design.get("layer_unit", "brick")).lower()
    if unit not in UNITS:
        raise DesignError("layer_unit must be 'brick'")
    grid_spec = design.get("grid") or {}
    try:
        dimensions = [grid_spec[k] for k in ("width", "depth", "layers")]
        if any(type(value) is not int for value in dimensions):
            raise ValueError("non-integer dimensions")
        width, depth, layers = dimensions
    except (KeyError, TypeError, ValueError) as exc:
        raise DesignError("grid must have integer width, depth and layers") from exc
    if not (
        1 <= width <= MAX_WIDTH
        and 1 <= depth <= MAX_DEPTH
        and 1 <= layers <= MAX_LAYERS[unit]
    ):
        raise DesignError(
            f"grid too large: max {MAX_WIDTH} x {MAX_DEPTH} studs and {MAX_LAYERS[unit]} {unit} layers"
        )
    shapes = design.get("shapes")
    if not isinstance(shapes, list) or not shapes:
        raise DesignError("shapes must be a non-empty list")
    if len(shapes) > MAX_SHAPES:
        raise DesignError(f"too many shapes ({len(shapes)}); max {MAX_SHAPES}")

    if width * depth * layers > 262_144:
        raise DesignError("Design bounds exceed 262144 grid cells; reduce resolution")
    grid = np.full((width, depth, layers), EMPTY, dtype=np.int32)
    X, Z, Y = np.meshgrid(
        np.arange(width), np.arange(depth), np.arange(layers), indexing="ij"
    )

    for index, shape in enumerate(shapes):
        where = f"shapes[{index}]"
        if not isinstance(shape, dict):
            raise DesignError(f"{where} must be an object")
        kind = shape.get("shape")
        mode = shape.get("mode", "fill")
        if mode not in ("fill", "paint", "carve"):
            raise DesignError(f"{where}: mode must be fill, paint or carve")
        color = shape.get("color")
        if mode != "carve" and kind != "layer":
            if type(color) is not int or color not in palette:
                raise DesignError(
                    f"{where}: color {color!r} is not in the palette. Use one of: {palette_prompt_text(palette)}"
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
                raise DesignError(f"{where}: radius values must be positive")
            mask = ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + (
                (Z - cz) / rz
            ) ** 2 <= 1.0
        elif kind == "cylinder":
            axis = shape.get("axis", "y")
            if axis not in ("x", "y", "z"):
                raise DesignError(f"{where}: axis must be x, y or z")
            others = {"x": ("y", "z"), "y": ("x", "z"), "z": ("x", "y")}[axis]
            ca, cb = _floats(shape.get("center"), 2, f"{where}.center")
            ra, rb = _floats(shape.get("radius"), 2, f"{where}.radius")
            if min(ra, rb) <= 0:
                raise DesignError(f"{where}: radius values must be positive")
            coords = {"x": X, "y": Y, "z": Z}
            limit = {"x": width, "y": layers, "z": depth}[axis]
            lo, hi = _as_range(shape.get("range"), f"{where}.range", limit)
            along = coords[axis]
            mask = (
                (
                    ((coords[others[0]] - ca) / ra) ** 2
                    + ((coords[others[1]] - cb) / rb) ** 2
                    <= 1.0
                )
                & (along >= lo)
                & (along <= hi)
            )
        elif kind == "layer":
            y0, y1 = _as_range(shape.get("y"), f"{where}.y", layers)
            rows = shape.get("rows")
            legend = shape.get("legend") or {}
            if not isinstance(rows, list) or not all(isinstance(r, str) for r in rows):
                raise DesignError(
                    f"{where}: rows must be a list of strings (one per z row, front first)"
                )
            if not isinstance(legend, dict):
                raise DesignError(
                    f"{where}: legend must map single characters to color codes"
                )
            colors: Dict[str, int] = {}
            for char, code in legend.items():
                if (
                    not isinstance(char, str)
                    or len(char) != 1
                    or (
                        mode != "carve"
                        and (type(code) is not int or code not in palette)
                    )
                ):
                    raise DesignError(
                        f"{where}: legend entry {char!r}: {code!r} must map one character to a palette color"
                    )
                colors[char] = code if isinstance(code, int) else EMPTY
            for z, row in enumerate(rows[:depth]):
                for x, char in enumerate(row[:width]):
                    if char in (".", " "):
                        continue
                    if char not in colors:
                        raise DesignError(
                            f"{where}: character {char!r} in row {z} is not in the legend"
                        )
                    cells = (x, z, slice(y0, y1 + 1))
                    if mode == "carve":
                        grid[cells] = EMPTY
                    elif mode == "paint":
                        grid[cells] = np.where(
                            grid[cells] != EMPTY, colors[char], EMPTY
                        )
                    else:
                        grid[cells] = colors[char]
            continue
        else:
            raise DesignError(
                f"{where}: unknown shape {kind!r} (use box, ellipsoid, cylinder or layer)"
            )

        if mode == "carve":
            grid[mask] = EMPTY
        elif mode == "paint":
            grid[mask & (grid != EMPTY)] = color
        else:
            grid[mask] = color

    filled = int((grid != EMPTY).sum())
    if filled == 0:
        raise DesignError("the design is empty after applying all shapes")
    if filled > MAX_VOXELS:
        raise DesignError(f"design has {filled} voxels; keep it under {MAX_VOXELS}")
    return grid, unit
