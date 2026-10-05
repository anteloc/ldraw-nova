"""Build and review a cheap voxel draft before the final sculpture conversion.

Draft packing is only for design feedback. Final bricks always use sculpture.convert.
"""
from __future__ import annotations

import io
import json
from collections import Counter
from dataclasses import dataclass

import numpy as np
from scipy import ndimage

from .sculpture import EMPTY, rasterize

# Draft footprints match the design builder; the final converter chooses its six parts.
SIZES = sorted([(2, 8), (2, 6), (2, 4), (2, 3), (2, 2),
                (1, 8), (1, 6), (1, 4), (1, 3), (1, 2), (1, 1)],
               key=lambda s: (-(s[0] * s[1]), -s[0]))
UNITS = {"brick": {"studs": 1.2}}
PALETTE = {72: ('Dark Bluish Gray', '6C6E68'),
 71: ('Light Bluish Gray', 'A0A5A9'),
 84: ('Medium Nougat', 'AA7D55'),
 308: ('Dark Brown', '352100'),
 70: ('Reddish Brown', '582A12'),
 28: ('Dark Tan', '958A73'),
 19: ('Tan', 'E4CD9E'),
 85: ('Dark Purple', '3F3691'),
 272: ('Dark Blue', '0A3463'),
 212: ('Bright Light Blue', '9FC3E9'),
 322: ('Medium Azure', '36AEBF'),
 321: ('Dark Azure', '078BC9'),
 73: ('Medium Blue', '5A93DB'),
 1: ('Blue', '0055BF'),
 330: ('Olive Green', '9B9A5A'),
 323: ('Light Aqua', 'ADC3C0'),
 27: ('Lime', 'BBE90B'),
 10: ('Bright Green', '4B9F4A'),
 2: ('Green', '237841'),
 288: ('Dark Green', '184632'),
 378: ('Sand Green', 'A0BCAC'),
 226: ('Bright Light Yellow', 'FFF03A'),
 14: ('Yellow', 'F2CD37'),
 78: ('Light Nougat', 'F6D7B3'),
 191: ('Bright Light Orange', 'F8BB3D'),
 25: ('Orange', 'FE8A18'),
 484: ('Dark Orange', 'A95500'),
 30: ('Medium Lavender', 'AC78BA'),
 29: ('Bright Pink', 'E4ADC8'),
 5: ('Dark Pink', 'C870A0'),
 26: ('Magenta', '923978'),
 320: ('Dark Red', '720E0F'),
 4: ('Red', 'C91A09'),
 15: ('White', 'FFFFFF'),
 0: ('Black', '05131D')}


@dataclass
class Draft:
    grid: np.ndarray
    solid_grid: np.ndarray
    bricks: list
    grounded_groups: int
    warnings: list
    owner: np.ndarray

    def summary(self):
        w, d, n = self.grid.shape
        weak = sum(v == 1 for v in _joint_degrees(self.owner).values())
        return {"checks_passed": True, "draft_bricks": len(self.bricks),
                "grid": [w, d, n], "weak_bricks": weak,
                "grounded_groups": self.grounded_groups, "warnings": self.warnings}

@dataclass
class PackResult:
    bricks: list[tuple[int, int, int, int, int, int]]  # (color, x0, z0, layer, fx, fz)
    owner: np.ndarray
    loose: list[int]
    grounded_groups: int

def _connectivity(bricks, owner: np.ndarray) -> PackResult:
    """Group bricks joined by vertical overlap; anything not joined to layer 0 is loose."""
    parent = list(range(len(bricks)))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for layer in range(owner.shape[2] - 1):
        a, b = owner[:, :, layer], owner[:, :, layer + 1]
        both = (a >= 0) & (b >= 0)
        for p, q in set(zip(a[both].tolist(), b[both].tolist())):
            parent[find(p)] = find(q)
    ground_roots = {find(i) for i, brick in enumerate(bricks) if brick[3] == 0}
    loose = [i for i in range(len(bricks)) if find(i) not in ground_roots]
    return PackResult(bricks, owner, loose, len(ground_roots))

def _pack_layers(grid: np.ndarray):
    """Bottom-up greedy packer that prefers bricks bonding to the grounded structure."""
    width, depth, layers = grid.shape
    owner = np.full(grid.shape, -1, dtype=np.int32)
    bricks: list[tuple[int, int, int, int, int, int]] = []
    parent: list[int] = []
    grounded_roots: set = set()

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for layer in range(layers):
        along_x = layer % 2 == 0  # alternate the bond direction per layer
        colors = grid[:, :, layer]
        free = owner[:, :, layer]
        below_owner = owner[:, :, layer - 1] if layer else None
        present = colors != EMPTY
        cells = list(zip(*np.nonzero(present)))
        if layer:
            dist = ndimage.distance_transform_cdt(below_owner == -1, metric="taxicab")
        else:
            dist = np.zeros(colors.shape, dtype=int)
        # Most-constrained cells first: those with few same-colored neighbors (tips, one-stud
        # columns) get a brick before their neighbors are used up.
        same = np.zeros(colors.shape, dtype=int)
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            shifted = np.full(colors.shape, EMPTY - 1)
            xs = slice(max(dx, 0), colors.shape[0] + min(dx, 0))
            zs = slice(max(dz, 0), colors.shape[1] + min(dz, 0))
            xd = slice(max(-dx, 0), colors.shape[0] + min(-dx, 0))
            zd = slice(max(-dz, 0), colors.shape[1] + min(-dz, 0))
            shifted[xd, zd] = colors[xs, zs]
            same += (shifted == colors) & present
        # Vary the scan direction per layer so seams don't line up from layer to layer.
        sx, sz = ((1, 1), (-1, -1), (1, -1), (-1, 1))[layer % 4]
        cells.sort(key=lambda ik: (-dist[ik], same[ik] >= 3, sx * ik[0], sz * ik[1]))
        for i, k in cells:
            if free[i, k] != -1:
                continue
            color = colors[i, k]
            best = None
            best_score = None
            for w, l in SIZES:
                if w == l:
                    orientations = ((w, l),)
                else:
                    orientations = ((l, w), (w, l)) if along_x else ((w, l), (l, w))
                for fx, fz in orientations:
                    for x0 in range(max(0, i - fx + 1), min(i, width - fx) + 1):
                        for z0 in range(max(0, k - fz + 1), min(k, depth - fz) + 1):
                            block = colors[x0:x0 + fx, z0:z0 + fz]
                            if not (block == color).all() or (free[x0:x0 + fx, z0:z0 + fz] != -1).any():
                                continue
                            if layer:
                                below = set(below_owner[x0:x0 + fx, z0:z0 + fz].ravel().tolist())
                                below.discard(-1)
                            else:
                                below = set()
                            roots = {find(b) for b in below}
                            grounded = layer == 0 or bool(roots & grounded_roots)
                            score = (grounded, bool(below), len(roots), len(below), fx * fz,
                                     (fx >= fz) == along_x)
                            if best_score is None or score > best_score:
                                best, best_score = (x0, z0, fx, fz), score
            x0, z0, fx, fz = best
            idx = len(bricks)
            free[x0:x0 + fx, z0:z0 + fz] = idx
            bricks.append((int(color), int(x0), int(z0), layer, fx, fz))
            parent.append(idx)
            grounded = layer == 0
            if layer:
                for b in set(below_owner[x0:x0 + fx, z0:z0 + fz].ravel().tolist()) - {-1}:
                    grounded = grounded or find(b) in grounded_roots
                    parent[find(b)] = find(idx)
            if grounded:
                grounded_roots.add(find(idx))
    return bricks, owner

def _pack(grid):
    return _connectivity(*_pack_layers(grid))

def _voxel_islands(solid: np.ndarray) -> list[tuple[int, tuple[slice, ...]]]:
    """Face-connected voxel groups that never reach layer 0 (can't be fixed by packing)."""
    labels, count = ndimage.label(solid)
    grounded = set(np.unique(labels[:, :, 0]).tolist()) - {0}
    boxes = ndimage.find_objects(labels)
    islands = []
    for label in range(1, count + 1):
        if label not in grounded:
            islands.append((int((labels == label).sum()), boxes[label - 1]))
    return islands

def _describe_box(box: tuple[slice, ...], layer_offset: int = 0) -> str:
    xs, zs, ys = box
    return (f"x {xs.start}-{xs.stop - 1}, z {zs.start}-{zs.stop - 1}, "
            f"layers {ys.start - layer_offset}-{ys.stop - 1 - layer_offset}")

def _joint_degrees(owner: np.ndarray) -> Counter:
    degree: Counter = Counter()
    for layer in range(owner.shape[2] - 1):
        a, b = owner[:, :, layer], owner[:, :, layer + 1]
        both = (a >= 0) & (b >= 0)
        for p, q in set(zip(a[both].tolist(), b[both].tolist())):
            degree[p] += 1
            degree[q] += 1
    return degree

def _hollow(grid: np.ndarray) -> np.ndarray:
    """Remove voxels more than 2 studs inside the surface. The ground below the model counts as
    solid, so the bottom layer is hollowed too (open-bottomed like a real brick sculpture)."""
    solid = grid != EMPTY
    padded = np.concatenate([np.ones(solid.shape[:2] + (1,), dtype=bool), solid], axis=2)
    inner = ndimage.binary_erosion(padded, structure=np.ones((5, 5, 3), dtype=bool))[:, :, 1:]
    out = grid.copy()
    out[inner] = EMPTY
    return out

def _repair_loose(work: np.ndarray, result: PackResult, warnings: list[str], offset: int) -> np.ndarray:
    """Last resort: recolor loose cells to match a grounded neighbor on the same layer (so a brick
    can bridge to it); anything still loose after that is removed."""
    loose = set(result.loose)
    changed = 0
    for n in loose:
        color, x0, z0, layer, fx, fz = result.bricks[n]
        neighbors: Counter = Counter()
        for x in range(max(0, x0 - 1), min(work.shape[0], x0 + fx + 1)):
            for z in range(max(0, z0 - 1), min(work.shape[1], z0 + fz + 1)):
                o = result.owner[x, z, layer]
                if o >= 0 and o not in loose:
                    neighbors[int(work[x, z, layer])] += 1
        if neighbors:
            new_color = neighbors.most_common(1)[0][0]
            if new_color != color:
                work[x0:x0 + fx, z0:z0 + fz, layer] = new_color
                changed += fx * fz
    if changed:
        warnings.append(f"Recolored {changed} stud(s) of unsupported overhang so they could bond to the model.")
    return work

def build_design(design, *, max_pieces=5_000, repair=False):
    """Rasterize, hollow, pack and verify. Raises ValueError with Claude-readable fixes.

    repair=True never raises for connectivity: it recolors or drops unsupported bricks instead
    (used for the final attempt so the user always gets a buildable model)."""
    grid, _ = rasterize(design)
    if any(int(c) not in PALETTE for c in np.unique(grid[grid != EMPTY])):
        raise ValueError("Use the documented sculpture colour palette")

    islands = _voxel_islands(grid != EMPTY)
    if islands and not repair:
        details = "; ".join(f"{size} voxels at {_describe_box(box)}" for size, box in islands[:8])
        raise ValueError(
            f"{len(islands)} part(s) of the design float with nothing connecting them to the ground "
            f"layer (layer 0): {details}. Every voxel must connect to layer 0 through touching voxels; "
            "add supports or move these parts so they touch the rest of the model."
        )
    warnings: list[str] = []
    if islands:
        labels, _ = ndimage.label(grid != EMPTY)
        keep = set(np.unique(labels[:, :, 0]).tolist()) - {0}
        dropped = int(((labels > 0) & ~np.isin(labels, list(keep))).sum())
        grid[(labels > 0) & ~np.isin(labels, list(keep))] = EMPTY
        warnings.append(f"Removed {dropped} floating voxel(s) that had no connection to the ground.")

    # The submitted schema has brick-height layers and no implicit plate base.
    offset = 0
    solid = grid != EMPTY
    work = _hollow(grid) if design.get("hollow", True) else grid.copy()

    result = _pack(work)
    for attempt in range(30):  # back-fill hidden interior around floating groups, then re-pack
        if not result.loose:
            break
        added = 0
        for n in result.loose:
            _, x0, z0, layer, fx, fz = result.bricks[n]
            regions = [(slice(x0, x0 + fx), slice(z0, z0 + fz), ll)
                       for ll in (layer - 1, layer + 1) if 0 <= ll < work.shape[2]]
            regions.append((slice(max(0, x0 - 1), x0 + fx + 1), slice(max(0, z0 - 1), z0 + fz + 1), layer))
            for region in regions:
                fill = solid[region] & (work[region] == EMPTY)
                if fill.any():
                    work[region] = np.where(fill, grid[region], work[region])
                    added += int(fill.sum())
        if not added:
            if not repair:
                break
            before = work.copy()
            work = _repair_loose(work, result, warnings, offset)
            if np.array_equal(before, work):
                break
        result = _pack(work)

    removed = np.zeros(work.shape, dtype=bool)
    if result.loose:
        mask = np.isin(result.owner, result.loose)
        labels, _ = ndimage.label(mask)
        areas = [_describe_box(box, offset) for box in ndimage.find_objects(labels)[:8]]
        if not repair:
            raise ValueError(
                f"{len(result.loose)} bricks can't be connected to the rest of the model. Problem areas: "
                + "; ".join(areas)
                + ". Bricks only hold by overlapping bricks directly above or below, and a brick can only "
                "span cells of one color. Usual causes: a one-stud-wide feature of a different color stacked "
                "straight up beside the model (e.g. an ear, a trim line or a hair edge), or an overhang with "
                "nothing under it. Make such features match the color of the cells they sit against, make them "
                "at least 2 studs deep, or support them from below."
            )
        work[mask] = EMPTY
        removed |= mask
        warnings.append(f"Removed {len(result.loose)} brick(s) that could not be connected ({'; '.join(areas)}).")
        result = _pack(work)

    if len(result.bricks) > max_pieces:
        raise ValueError(
            f"the design needs {len(result.bricks)} pieces; keep it under {max_pieces}. "
            "Use a smaller grid or hollow: true."
        )

    # The un-hollowed model with the builder's recolors and removals applied: a solid source for
    # the voxel pipeline (block editor / resize), which hollows models itself.
    solid_grid = np.where(work != EMPTY, work, grid)
    solid_grid[removed] = EMPTY
    return Draft(work, solid_grid, result.bricks, result.grounded_groups, warnings, result.owner)

def render_preview_png(grid, unit="brick", palette=None,
                       max_size: int = 1100) -> bytes:
    """Two isometric views (front-left and back-right) of the built voxels, as PNG bytes."""
    from PIL import Image, ImageDraw

    palette = palette or PALETTE
    h = UNITS[unit]["studs"]
    width, depth, layers = grid.shape
    span = width + depth + layers * h
    scale = max(3.0, min(14.0, (max_size / 2 - 40) / (span * 0.95)))

    def view(g: np.ndarray) -> "Image.Image":
        w, d, n = g.shape
        cos30, sin30 = 0.866, 0.5
        img_w = int((w + d) * cos30 * scale) + 40
        img_h = int(((w + d) * sin30 + n * h) * scale) + 40
        image = Image.new("RGB", (img_w, img_h), (246, 246, 244))
        draw = ImageDraw.Draw(image)
        ox, oy = 20 + d * cos30 * scale, 20 + n * h * scale

        def project(x, y, z):
            # viewer is front-left and above; farther along +x/+z moves up the screen
            return (ox + (x - z) * cos30 * scale,
                    oy - y * scale + ((w + d) - (x + z)) * sin30 * scale)

        filled = g != EMPTY
        xs, zs, ls = np.nonzero(filled)
        order = np.argsort(-(xs + zs - ls * h), kind="stable")
        for idx in order:
            x, z, l = int(xs[idx]), int(zs[idx]), int(ls[idx])
            rgb_hex = palette.get(int(g[x, z, l]), ("", "888888"))[1]
            base = tuple(int(rgb_hex[i:i + 2], 16) for i in (0, 2, 4))
            y0, y1 = l * h, (l + 1) * h
            faces = []
            if l + 1 >= n or not filled[x, z, l + 1]:
                faces.append(([(x, y1, z), (x + 1, y1, z), (x + 1, y1, z + 1), (x, y1, z + 1)], 1.0))
            if z == 0 or not filled[x, z - 1, l]:
                faces.append(([(x, y0, z), (x + 1, y0, z), (x + 1, y1, z), (x, y1, z)], 0.82))
            if x == 0 or not filled[x - 1, z, l]:
                faces.append(([(x, y0, z), (x, y0, z + 1), (x, y1, z + 1), (x, y1, z)], 0.66))
            for corners, shade in faces:
                fill = tuple(int(c * shade) for c in base)
                outline = tuple(int(c * shade * 0.8) for c in base)
                draw.polygon([project(*c) for c in corners], fill=fill, outline=outline)
        return image

    front = view(grid)
    back = view(grid[::-1, ::-1, :])
    canvas = Image.new("RGB", (front.width + back.width, max(front.height, back.height)), (246, 246, 244))
    canvas.paste(front, (0, 0))
    canvas.paste(back, (front.width, 0))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 6), "front-left", fill=(90, 90, 90))
    draw.text((front.width + 10, 6), "back-right", fill=(90, 90, 90))
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()

def preview(path, output, voxels, *, repair=False):
    """Save the cheap draft image and accepted solid voxels, without final conversion."""
    from pathlib import Path
    draft = build_design(json.loads(Path(path).read_text()), repair=repair)
    Path(output).write_bytes(render_preview_png(draft.grid))
    rows = [[int(x), int(z), int(y), int(draft.solid_grid[x, z, y])]
            for x, z, y in np.argwhere(draft.solid_grid != EMPTY)]
    Path(voxels).write_text(json.dumps({"voxels": rows}))
    return draft.summary()
