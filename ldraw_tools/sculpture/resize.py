"""BrickBuilder-style grid resampling, retaining categorical LDraw colours."""
from pathlib import Path
import re

import numpy as np

from .conversion import load_voxels, MAX_EXTENT, MAX_GRID_CELLS, MAX_VOXELS


def resample_voxels(path: str | Path, *, resolution: int, library: Path) -> tuple[dict, dict]:
    if type(resolution) is not int or not 8 <= resolution <= MAX_EXTENT:
        raise ValueError("Choose a size from 8 to 96 cells")
    occupied, colours = load_voxels(path)
    shape = np.array(occupied.shape)
    scale = resolution / int(shape.max())
    if scale > 1:
        # Same nearest-neighbour grid sampling as BrickBuilder's upsample_xyzrgb.
        dimensions = np.maximum(1, np.rint(shape * scale).astype(int))
        if int(np.prod(dimensions)) > MAX_GRID_CELLS:
            raise ValueError("Resized world exceeds 262144 cells; choose a smaller size")
        axes = [np.minimum(np.floor(np.arange(n) / scale).astype(int), e - 1)
                for n, e in zip(dimensions, shape)]
        picked = occupied[np.ix_(*axes)]
        if int(picked.sum()) > MAX_VOXELS:
            raise ValueError("Resized sculpture exceeds 65536 occupied cells; choose a smaller size")
        coordinates = np.argwhere(picked)
        values = colours[np.ix_(*axes)][picked]
    elif scale < 1:
        # BrickBuilder bins coordinates and averages RGB before snapping back
        # onto the LEGO palette. Never average numeric LDraw colour identifiers.
        from .glb_import import ldraw_palette
        codes, palette = ldraw_palette(library)
        source_rgb = {}
        for line in (library / 'LDConfig.ldr').read_text(errors='replace').splitlines():
            match = re.match(r'0\s+!COLOUR\s+\S+\s+CODE\s+(\d+)\s+VALUE\s+#([\dA-Fa-f]{6})', line)
            if match:
                source_rgb[int(match[1])] = [int(match[2][i:i + 2], 16) for i in (0, 2, 4)]
        original = np.argwhere(occupied)
        binned = np.floor(original * scale).astype(int)
        coordinates, index = np.unique(binned, axis=0, return_inverse=True)
        try:
            rgb = np.array([source_rgb[int(c)] for c in colours[occupied]], dtype=float)
        except KeyError as exc:
            raise ValueError("A sculpture colour is missing from the LDraw palette") from exc
        sums = np.zeros((len(coordinates), 3))
        np.add.at(sums, index, rgb)
        averaged = np.rint(sums / np.bincount(index)[:, None])
        values = np.empty(len(coordinates), dtype=int)
        for start in range(0, len(coordinates), 512):
            distances = ((averaged[start:start + 512, None] - palette[None]) ** 2).sum(axis=2)
            values[start:start + 512] = codes[distances.argmin(axis=1)]
    else:
        coordinates = np.argwhere(occupied)
        values = colours[occupied]
    rows = [[*map(int, xyz), int(colour)] for xyz, colour in zip(coordinates, values)]
    dimensions = (coordinates.max(axis=0) - coordinates.min(axis=0) + 1).tolist()
    return {"voxels": rows}, {"source": "voxels", "resolution": resolution,
        "from_dimensions": shape.tolist(), "dimensions": dimensions, "resampled_voxels": len(rows)}
