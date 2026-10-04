"""Track brick occupancy, stud connections and supported build ordering."""

from dataclasses import dataclass
import networkx as nx
import numpy as np
from scipy.ndimage import binary_dilation, binary_fill_holes, distance_transform_edt, label
from scipy.spatial import cKDTree


BRICK_PARTS = {
    (2, 4): "3001.DAT",
    (2, 6): "2456.DAT",
    (1, 4): "3010.DAT",
    (1, 2): "3004.DAT",
    (1, 1): "3005.DAT",
    (2, 2): "3003.DAT",
}


def part_for_dimensions(h: int, w: int) -> str:
    try:
        return BRICK_PARTS[tuple(sorted((h, w)))]
    except KeyError:
        raise ValueError(f"No brick part for dimensions: {h}x{w}") from None


@dataclass(frozen=True, order=True, kw_only=True)
class Brick:
    """
    Represents a 1-unit-tall rectangular brick.
    """

    h: int
    w: int
    x: int
    y: int
    z: int
    color: int = 4

    @property
    def part_id(self) -> str:
        return part_for_dimensions(self.h, self.w)

    @property
    def ori(self) -> int:
        return 1 if self.h > self.w else 0

    @property
    def area(self) -> int:
        return self.h * self.w

    @property
    def slice_2d(self) -> (slice, slice):
        return (slice(self.x, self.x + self.h), slice(self.y, self.y + self.w))

    @property
    def slice(self) -> (slice, slice, int):
        return (*self.slice_2d, self.z)

    def __repr__(self):
        return self.to_txt()[:-1]

    def to_txt(self) -> str:
        return f"{self.h}x{self.w} ({self.x},{self.y},{self.z})\n"

    def to_ldr(self, base_height: float = 0, color: int = 4) -> str:
        x = (self.x + self.h * 0.5) * 20
        z = (self.y + self.w * 0.5) * 20
        y = (self.z + base_height) * -24
        matrix = "0 0 1 0 1 0 -1 0 0" if self.ori == 0 else "-1 0 0 0 1 0 0 0 -1"
        line = f"1 {color} {x} {y} {z} {matrix} {self.part_id}\n"
        step_line = "0 STEP\n"
        return line + step_line


def brick_support_type(occupancy: np.ndarray, brick: Brick) -> str:
    """
    Determine how a brick is supported by the occupied voxels (indexed [x, y, z]).

    Returns:
        'ground' - brick is on ground level (z=0)
        'below' - brick has support from below
        'above' - brick only has support from above
        'floating' - brick has no support
    """
    if brick.z == 0:
        return "ground"
    if np.any(occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z - 1]):
        return "below"
    if brick.z + 1 < occupancy.shape[2] and np.any(
        occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z + 1]
    ):
        return "above"
    return "floating"


def reorder_bricks_for_stability(bricks: list[Brick], shape: tuple[int, int, int]) -> tuple[list[Brick], set[Brick]]:
    if not bricks:
        return (bricks, set())
    occupancy = np.zeros(shape, dtype=np.int32)
    ordered_bricks = []
    remaining_set = set(range(len(bricks)))
    deferred_bricks = set()
    deferred_voxels = np.zeros(shape, dtype=bool)

    def place(brick: Brick) -> None:
        occupancy[brick.slice] += 1
        ordered_bricks.append(brick)
    while remaining_set:
        supported_below = []
        supported_above = []
        for idx in remaining_set:
            support = brick_support_type(occupancy, bricks[idx])
            if support == 'ground' or support == 'below':
                supported_below.append(idx)
            elif support == 'above':
                supported_above.append(idx)
        supported_below.sort(key=lambda i: (bricks[i].z, bricks[i].x, bricks[i].y))
        supported_above.sort(key=lambda i: (-bricks[i].z, bricks[i].x, bricks[i].y))
        if supported_below:
            for idx in supported_below:
                brick = bricks[idx]
                place(brick)
                remaining_set.discard(idx)
                if brick.z > 0:
                    support_voxels = occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z - 1]
                    deferred_support = deferred_voxels[brick.slice_2d[0], brick.slice_2d[1], brick.z - 1]
                    if np.all((support_voxels > 0) == deferred_support):
                        deferred_bricks.add(brick)
                        deferred_voxels[brick.slice] = True
        elif supported_above:
            idx = supported_above[0]
            brick = bricks[idx]
            place(brick)
            remaining_set.discard(idx)
            deferred_bricks.add(brick)
            deferred_voxels[brick.slice] = True
        else:
            forced_idx = max(remaining_set, key=lambda i: (-bricks[i].z, bricks[i].x, bricks[i].y))
            forced_brick = bricks[forced_idx]
            place(forced_brick)
            remaining_set.discard(forced_idx)
            deferred_bricks.add(forced_brick)
            deferred_voxels[forced_brick.slice] = True
    return ordered_bricks, deferred_bricks


class ConnectivityBrickStructure:
    """
    Brick structure that keeps graph connectivity information
    """

    def __init__(self, shape: tuple[int, int, int]):
        self.voxel_bricks = np.zeros(shape, dtype=int)
        self.bricks = {}
        self.node_id_counter = 0
        self.connection_graph = nx.Graph()
        self.neighbor_graph = nx.Graph()
        self._connected_components = None
        self._component_labels = None

    @property
    def max_x(self) -> int:
        return self.voxel_bricks.shape[0]

    @property
    def max_y(self) -> int:
        return self.voxel_bricks.shape[1]

    @property
    def max_z(self) -> int:
        return self.voxel_bricks.shape[2]

    def _reset_cache(self) -> None:
        self._connected_components = None
        self._component_labels = None

    def connected_components(self):
        if self._connected_components is None:
            self._connected_components = list(
                nx.connected_components(self.connection_graph)
            )
        return self._connected_components

    def component_labels(self) -> np.ndarray:
        if self._component_labels is None:
            self._component_labels = np.zeros_like(self.voxel_bricks)
            for i, comp in enumerate(self.connected_components()):
                for node in comp:
                    brick = self.bricks[node]
                    self._component_labels[brick.slice] = i + 1
        return self._component_labels

    def node_exists(self, node_id: int):
        return node_id in self.bricks

    def add_brick(self, brick: Brick) -> int:
        self._reset_cache()
        if self.voxel_bricks[brick.slice].any():
            raise ValueError(f"Cannot place brick {brick} due to collisions")
        self.node_id_counter += 1
        node = self.node_id_counter
        self.bricks[node] = brick
        self.voxel_bricks[brick.slice] = node
        self.connection_graph.add_node(node)
        self.neighbor_graph.add_node(node)
        vert_neighbors = {
            (node, self.voxel_bricks[x, y, brick.z - 1])
            for x in range(brick.x, brick.x + brick.h)
            for y in range(brick.y, brick.y + brick.w)
            if brick.z > 0
        } | {
            (node, self.voxel_bricks[x, y, brick.z + 1])
            for x in range(brick.x, brick.x + brick.h)
            for y in range(brick.y, brick.y + brick.w)
            if brick.z + 1 < self.max_z
        }
        vert_neighbors = list(filter(lambda e: e[1] != 0, vert_neighbors))
        horz_neighbors = (
            {
                (node, self.voxel_bricks[brick.x - 1, y, brick.z])
                for y in range(brick.y, brick.y + brick.w)
                if brick.x > 0
            }
            | {
                (node, self.voxel_bricks[brick.x + brick.h, y, brick.z])
                for y in range(brick.y, brick.y + brick.w)
                if brick.x + brick.h < self.max_x
            }
            | {
                (node, self.voxel_bricks[x, brick.y - 1, brick.z])
                for x in range(brick.x, brick.x + brick.h)
                if brick.y > 0
            }
            | {
                (node, self.voxel_bricks[x, brick.y + brick.w, brick.z])
                for x in range(brick.x, brick.x + brick.h)
                if brick.y + brick.w < self.max_y
            }
        )
        horz_neighbors = list(filter(lambda e: e[1] != 0, horz_neighbors))
        self.connection_graph.add_edges_from(vert_neighbors)
        self.neighbor_graph.add_edges_from(vert_neighbors + horz_neighbors)
        return node

    def add_bricks(self, bricks: list[Brick]) -> list[int]:
        return [self.add_brick(brick) for brick in bricks]

    def remove_brick(self, node_id: int) -> None:
        self._reset_cache()
        brick = self.bricks[node_id]
        self.bricks.pop(node_id)
        self.voxel_bricks[brick.slice] = 0
        self.connection_graph.remove_node(node_id)
        self.neighbor_graph.remove_node(node_id)

    def remove_voxel_subset(self, voxel_subset: np.ndarray) -> list[Brick]:
        """
        Erases all bricks inside the specified subset of voxels.
        Assumes that all bricks in voxel_subset are completely contained within voxel_subset.
        """
        removed_bricks = []
        nodes = set(np.unique(self.voxel_bricks[voxel_subset])) - {0}
        for node in nodes:
            brick = self.bricks[node]
            assert voxel_subset[brick.slice].all()
            removed_bricks.append(brick)
            self.remove_brick(node)
        return removed_bricks


class BrickStructure:
    """Clean up packed bricks and export supported instruction ordering."""

    def __init__(self, bricks: list[Brick], world_dim: int):
        self.world_dim = world_dim
        self.bricks = list(bricks)
        self.voxel_occupancy = np.zeros((world_dim,) * 3, dtype=int)
        for brick in self.bricks:
            self.voxel_occupancy[brick.slice] += 1

    def to_ldr(self) -> str:
        ordered, deferred = self._reorder_bricks_for_stability(self.bricks)
        if deferred and self.remove_interior_deferred_bricks(deferred):
            ordered, _ = self._reorder_bricks_for_stability(self.bricks)
        if self.remove_floating_bricks():
            ordered, _ = self._reorder_bricks_for_stability(self.bricks)
        return "".join(brick.to_ldr(color=brick.color) for brick in ordered)

    def _reorder_bricks_for_stability(self, bricks: list[Brick]) -> tuple[list[Brick], set[Brick]]:
        return reorder_bricks_for_stability(bricks, (self.world_dim,) * 3)

    def _compute_exterior_mask(self) -> np.ndarray:
        """Find air reachable from outside using six-neighbor connectivity."""
        padded_shape = tuple((s + 2 for s in self.voxel_occupancy.shape))
        padded_air = np.ones(padded_shape, dtype=bool)
        padded_air[1:-1, 1:-1, 1:-1] = self.voxel_occupancy == 0
        structure_6conn = np.array([
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
            [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
        ], dtype=bool)
        labels, _ = label(padded_air, structure=structure_6conn)
        exterior_label = labels[0, 0, 0]
        exterior_padded = labels == exterior_label
        return exterior_padded[1:-1, 1:-1, 1:-1]

    def _is_brick_interior(self, brick: Brick, exterior_mask: np.ndarray) -> bool:
        neighbors = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
        for x in range(brick.x, brick.x + brick.h):
            for y in range(brick.y, brick.y + brick.w):
                z = brick.z
                for dx, dy, dz in neighbors:
                    nx, ny, nz = (x + dx, y + dy, z + dz)
                    if 0 <= nx < self.world_dim and 0 <= ny < self.world_dim and (0 <= nz < self.world_dim):
                        if exterior_mask[nx, ny, nz]:
                            return False
                    else:
                        return False
        return True

    def remove_interior_deferred_bricks(self, deferred_bricks: set[Brick]) -> list[Brick]:
        if not deferred_bricks:
            return []
        exterior_mask = self._compute_exterior_mask()
        removed_bricks = []
        for brick in deferred_bricks:
            if brick not in self.bricks:
                continue
            if self._is_brick_interior(brick, exterior_mask):
                self.voxel_occupancy[brick.slice] -= 1
                self.bricks.remove(brick)
                removed_bricks.append(brick)
        return removed_bricks

    def get_floating_bricks(self) -> list[Brick]:
        return [brick for brick in self.bricks if self.brick_floats(brick)]

    def remove_floating_bricks(self) -> list[Brick]:
        all_removed = []
        while True:
            floating = self.get_floating_bricks()
            if not floating:
                break
            for brick in floating:
                self.voxel_occupancy[brick.slice] -= 1
                self.bricks.remove(brick)
                all_removed.append(brick)
        return all_removed

    def brick_floats(self, brick: Brick) -> bool:
        if brick.z == 0:
            return False
        if np.any(self.voxel_occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z - 1]):
            return False
        if brick.z != self.world_dim - 1 and np.any(self.voxel_occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z + 1]):
            return False
        return True

@dataclass(frozen=True)
class SupportAudit:
    ldr: str
    conflicts: np.ndarray
    connected: np.ndarray


def audit_supports(structure: BrickStructure, voxels: np.ndarray) -> SupportAudit:
    """Audit the exported bricks, including removal during instruction ordering.

    Only vertical stud contacts connect bricks. Horizontal voxel adjacency alone
    does not. Keep the largest grounded component and report everything omitted
    from the requested geometry, rather than stale pre-reconnection diagnostics.
    """
    structure.to_ldr()
    owners = np.full(voxels.shape, -1, dtype=np.int32)
    graph = nx.Graph()
    for index, brick in enumerate(structure.bricks):
        graph.add_node(index)
        owners[brick.slice] = index
    below, above = owners[:, :, :-1], owners[:, :, 1:]
    contacts = (below >= 0) & (above >= 0)
    if contacts.any():
        graph.add_edges_from(np.unique(np.stack((below[contacts], above[contacts]), axis=1), axis=0))
    grounded = [component for component in nx.connected_components(graph)
                if any(structure.bricks[index].z == 0 for index in component)]
    main = max(grounded, key=lambda component: sum(structure.bricks[index].area for index in component), default=set())
    connected = np.isin(owners, list(main))
    conflicts = voxels & ~connected
    if len(main) != len(structure.bricks):
        for index, brick in enumerate(structure.bricks):
            if index not in main:
                structure.voxel_occupancy[brick.slice] -= 1
        structure.bricks = [brick for index, brick in enumerate(structure.bricks) if index in main]
    ldr = structure.to_ldr()
    return SupportAudit(ldr, conflicts, connected)


def _add_internal_supports(voxels: np.ndarray, colors: np.ndarray, conflicts: np.ndarray,
                           *, broad: bool, max_added: int) -> tuple[np.ndarray, np.ndarray]:
    """Reinforce enclosed cavities without adding any exterior geometry.

    Six-connected flood filling from outside keeps open cavities and gaps out of
    the interior mask. Local reinforcement looks past the pipeline's two-cell
    shell. Broader reinforcement fills enclosed cavities bordering an affected
    voxel component, allowing hidden connections elsewhere in the same body.
    """
    interior = binary_fill_holes(voxels) & ~voxels
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
    nearest = distance_transform_edt(~voxels, return_distances=False, return_indices=True)
    repaired, repaired_colors = voxels.copy(), colors.copy()
    repaired[additions] = True
    repaired_colors[additions] = colors[tuple(axis[additions] for axis in nearest)]
    return repaired, repaired_colors


def add_voxel_supports(voxels: np.ndarray, colors: np.ndarray, audit: SupportAudit,
                       *, inside_only: bool = False, broad: bool = False, max_added: int = 20_000,
                       max_grid_cells: int = 4_000_000) -> tuple[np.ndarray, np.ndarray]:
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
    if np.prod(shape) > max_grid_cells or max(shape) > 256:
        return voxels, colors
    if inside_only:
        return _add_internal_supports(voxels, colors, audit.conflicts, broad=broad, max_added=max_added)
    additions: dict[tuple[int, int, int], np.ndarray] = {}

    def add(coord, color):
        coord = tuple(int(value) for value in coord)
        if coord[2] >= voxels.shape[2] or not voxels[coord]:
            additions[coord] = color

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
            color = colors[tuple(start)]
            current = start.copy()
            # Descend to the anchor's height before bridging horizontally.
            for axis in (2, 0, 1):
                while current[axis] != target[axis]:
                    add(current, color)
                    add(current + (0, 0, 1), color)
                    current[axis] += 1 if target[axis] > current[axis] else -1
            add(target + (0, 0, 1), color)

    # A model with no retained ground needs a pillar before any seam repairs work.
    else:
        x, y, z = np.argwhere(voxels)[0]
        for support_z in range(z):
            add((x, y, support_z), colors[x, y, z])

    if not additions or len(additions) > max_added or int(voxels.sum()) + len(additions) > 100_000:
        return voxels, colors
    repaired = np.pad(voxels, ((0, 0), (0, 0), (0, 1)))
    repaired_colors = np.pad(colors, ((0, 0), (0, 0), (0, 1)))
    for coord, color in additions.items():
        repaired[coord] = True
        repaired_colors[coord] = color
    # Do not grow the grid when all supports fit under existing geometry.
    if not repaired[:, :, -1].any():
        repaired = repaired[:, :, :-1]
        repaired_colors = repaired_colors[:, :, :-1]
    return repaired, repaired_colors
