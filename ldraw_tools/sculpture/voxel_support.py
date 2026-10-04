# Adapted from BrickBuilderAI, copyright (c) 2026 Jake Johnson.
# MIT license: see LICENSE.brickbuilder. See README.md for source revisions.
"""Add local stud connections when voxel packing loses parts of a design."""

from dataclasses import dataclass

import networkx as nx
import numpy as np
from scipy.ndimage import (
    binary_dilation,
    binary_fill_holes,
    distance_transform_edt,
    label,
)
from scipy.spatial import cKDTree

from .brick_structure import ConnectivityBrickStructure


@dataclass(frozen=True)
class SupportAudit:
    conflicts: np.ndarray
    connected: np.ndarray
    components: int = 0


def audit_supports(bricks, voxels: np.ndarray) -> SupportAudit:
    """Audit actual stud contacts without dropping or force-placing any subject cells."""
    structure = ConnectivityBrickStructure(voxels.shape)
    for brick in sorted(bricks):
        if (
            brick.x < 0
            or brick.y < 0
            or brick.z < 0
            or brick.x + brick.h > voxels.shape[0]
            or brick.y + brick.w > voxels.shape[1]
            or brick.z >= voxels.shape[2]
        ):
            raise ValueError("Packing produced an out-of-bounds brick")
        structure.add_brick(brick)  # Also rejects overlaps.
    grounded = [
        component
        for component in structure.connected_components()
        if any(structure.bricks[node].z == 0 for node in component)
    ]
    main = max(
        grounded,
        key=lambda component: (
            sum(structure.bricks[node].area for node in component),
            -min(component),
        ),
        default=set(),
    )
    connected = np.isin(structure.voxel_bricks, sorted(main))
    return SupportAudit(voxels & ~connected, connected, structure.n_components())


def _add_internal_supports(
    voxels: np.ndarray,
    colors: np.ndarray,
    conflicts: np.ndarray,
    *,
    broad: bool,
    max_added: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Reinforce enclosed cavities without adding any exterior geometry.

    Six-connected flood filling from outside keeps open cavities and gaps out of
    the interior mask. Local reinforcement looks past the pipeline's two-cell
    shell. Broader reinforcement fills enclosed cavities bordering an affected
    voxel component, allowing hidden connections elsewhere in the same body.
    """
    interior = binary_fill_holes(np.pad(voxels, 1))[1:-1, 1:-1, 1:-1] & ~voxels
    if not interior.any():
        return voxels, colors
    if broad:
        bodies, _ = label(voxels)
        affected = np.unique(bodies[conflicts])
        body = voxels & np.isin(bodies, affected[affected != 0])
        cavities, _ = label(interior)
        touching = np.unique(cavities[binary_dilation(body) & interior])
        additions = interior & np.isin(cavities, touching[touching != 0])
    else:
        additions = interior & binary_dilation(conflicts, iterations=3)
    count = int(additions.sum())
    if not count or count > max_added or int(voxels.sum()) + count > 100_000:
        return voxels, colors
    # Inherit nearby material colors while leaving every existing cell intact.
    nearest = distance_transform_edt(
        ~voxels, return_distances=False, return_indices=True
    )
    repaired, repaired_colors = voxels.copy(), colors.copy()
    repaired[additions] = True
    repaired_colors[additions] = colors[tuple(axis[additions] for axis in nearest)]
    return repaired, repaired_colors


def add_voxel_supports(
    voxels: np.ndarray,
    colors: np.ndarray,
    audit: SupportAudit,
    *,
    inside_only: bool = False,
    broad: bool = False,
    max_added: int = 20_000,
    max_grid_cells: int = 262_144,
    max_extent: int = 96,
) -> tuple[np.ndarray, np.ndarray]:
    """Thicken conflict areas and bridge separate islands to the grounded model.

    A second layer lets the packer stagger bricks across seams in a long flat
    section. Small repairs include its immediate neighbors; a second attempt
    can reinforce the entire affected horizontal section. Separate voxel islands
    get a two-layer Manhattan bridge to the existing main structure. Existing
    cells and colors are never removed or recolored. The converter first calls
    this with inside_only=True and verifies the result before allowing exterior
    reinforcement.
    """
    if not audit.conflicts.any() or max_added <= 0:
        return voxels, colors
    shape = voxels.shape if inside_only else (*voxels.shape[:2], voxels.shape[2] + 1)
    if np.prod(shape) > max_grid_cells or max(shape) > max_extent:
        return voxels, colors
    if inside_only:
        return _add_internal_supports(
            voxels, colors, audit.conflicts, broad=broad, max_added=max_added
        )
    additions: dict[tuple[int, int, int], np.ndarray] = {}

    def add(coord, rgb):
        coord = tuple(int(value) for value in coord)
        if coord[2] >= voxels.shape[2] or not voxels[coord]:
            additions[coord] = rgb

    for z in np.flatnonzero(audit.conflicts.any(axis=(0, 1))):
        plane = voxels[:, :, z]
        if broad:
            sections, _ = label(plane)
            affected = np.unique(sections[audit.conflicts[:, :, z]])
            region = plane & np.isin(sections, affected[affected != 0])
        else:
            region = plane & binary_dilation(audit.conflicts[:, :, z])
        for x, y in np.argwhere(region):
            # Prefer the underside of elevated details; cap sections on the floor.
            support_z = z - 1 if z > 0 else z + 1
            add((x, y, support_z), colors[x, y, z])
            # When the underside already exists, a cap can still bridge brick seams.
            if z > 0 and voxels[x, y, support_z]:
                add((x, y, z + 1), colors[x, y, z])

    components, _ = label(voxels)
    main_labels = np.unique(components[audit.connected])
    separate = np.unique(components[audit.conflicts])
    targets = np.argwhere(audit.connected)
    if len(targets):
        tree = cKDTree(targets)
        for component in separate:
            if component in main_labels:
                continue
            coords = np.argwhere(components == component)
            distances, indices = tree.query(coords, p=1)
            start_index = int(np.argmin(distances))
            start = coords[start_index]
            target = targets[indices[start_index]]
            rgb = colors[tuple(start)]
            current = start.copy()
            # Descend to the anchor's height before bridging horizontally.
            for axis in (2, 0, 1):
                while current[axis] != target[axis]:
                    add(current, rgb)
                    add(current + (0, 0, 1), rgb)
                    current[axis] += 1 if target[axis] > current[axis] else -1
            add(target + (0, 0, 1), rgb)

    # A model with no retained ground needs a pillar before any seam repairs work.
    else:
        x, y, z = np.argwhere(voxels)[0]
        for support_z in range(z):
            add((x, y, support_z), colors[x, y, z])

    if (
        not additions
        or len(additions) > max_added
        or int(voxels.sum()) + len(additions) > 100_000
    ):
        return voxels, colors
    repaired = np.pad(voxels, ((0, 0), (0, 0), (0, 1)))
    repaired_colors = np.pad(colors, ((0, 0), (0, 0), (0, 1)))
    for coord, rgb in additions.items():
        repaired[coord] = True
        repaired_colors[coord] = rgb
    # Do not grow the grid when all supports fit under existing geometry.
    if not repaired[:, :, -1].any():
        repaired = repaired[:, :, :-1]
        repaired_colors = repaired_colors[:, :, :-1]
    return repaired, repaired_colors
