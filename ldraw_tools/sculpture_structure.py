"""Track brick occupancy, stud connections and supported build ordering."""

from dataclasses import dataclass
import networkx as nx
import numpy as np
from ldraw import Piece, Vector, Matrix
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


def part_for_dimensions(h, w):
    try:
        return BRICK_PARTS[tuple(sorted((h, w)))]
    except KeyError:
        raise ValueError(f"No brick part for dimensions: {h}x{w}") from None


@dataclass(frozen=True, order=True, kw_only=True)
class Brick:
    """One brick-height rectangular footprint on the voxel grid."""

    h: int
    w: int
    x: int
    y: int
    z: int
    colour: int = 4

    @property
    def part_id(self):
        return part_for_dimensions(self.h, self.w)

    @property
    def ori(self):
        return 1 if self.h > self.w else 0

    @property
    def area(self):
        return self.h * self.w

    @property
    def slice_2d(self):
        return (slice(self.x, self.x + self.h), slice(self.y, self.y + self.w))

    @property
    def slice(self):
        return (*self.slice_2d, self.z)

    def to_piece(self):
        """Convert grid coordinates to an ordinary pyldraw3 placement."""
        x = (self.x + self.h * 0.5) * 20
        z = (self.y + self.w * 0.5) * 20
        y = self.z * -24
        matrix = ([[0, 0, 1], [0, 1, 0], [-1, 0, 0]] if self.ori == 0
                  else [[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
        return Piece.place(self.part_id, colour=self.colour, position=Vector(x, y, z), matrix=Matrix(matrix))


def brick_support_type(occupancy, brick):
    """Classify support from occupied cells above, below or on the ground."""
    if brick.z == 0:
        return "ground"
    if np.any(occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z - 1]):
        return "below"
    if brick.z + 1 < occupancy.shape[2] and np.any(
        occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z + 1]
    ):
        return "above"
    return "floating"


def reorder_bricks_for_stability(bricks, shape):
    if not bricks:
        return (bricks, set())
    occupancy = np.zeros(shape, dtype=np.int32)
    ordered_bricks = []
    remaining_set = set(range(len(bricks)))
    deferred_bricks = set()
    deferred_voxels = np.zeros(shape, dtype=bool)

    def place(brick):
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
    """Track occupancy, stud connections and neighbouring bricks during packing."""

    def __init__(self, shape):
        self.voxel_bricks = np.zeros(shape, dtype=int)
        self.bricks = {}
        self.node_id_counter = 0
        self.connection_graph = nx.Graph()
        self.neighbor_graph = nx.Graph()
        self._connected_components = None
        self._component_labels = None

    @property
    def max_x(self):
        return self.voxel_bricks.shape[0]

    @property
    def max_y(self):
        return self.voxel_bricks.shape[1]

    @property
    def max_z(self):
        return self.voxel_bricks.shape[2]

    def _reset_cache(self):
        self._connected_components = None
        self._component_labels = None

    def connected_components(self):
        if self._connected_components is None:
            self._connected_components = list(nx.connected_components(self.connection_graph))
        return self._connected_components

    def component_labels(self):
        if self._component_labels is None:
            self._component_labels = np.zeros_like(self.voxel_bricks)
            for i, comp in enumerate(self.connected_components()):
                for node in comp:
                    brick = self.bricks[node]
                    self._component_labels[brick.slice] = i + 1
        return self._component_labels

    def node_exists(self, node_id):
        return node_id in self.bricks

    def add_brick(self, brick):
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

    def remove_brick(self, node_id):
        self._reset_cache()
        brick = self.bricks[node_id]
        self.bricks.pop(node_id)
        self.voxel_bricks[brick.slice] = 0
        self.connection_graph.remove_node(node_id)
        self.neighbor_graph.remove_node(node_id)

    def remove_voxel_subset(self, voxel_subset):
        """Remove bricks fully contained in the requested voxel subset."""
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

    def __init__(self, bricks, world_dim):
        self.world_dim = world_dim
        self.bricks = list(bricks)
        self.voxel_occupancy = np.zeros((world_dim,) * 3, dtype=int)
        for brick in self.bricks:
            self.voxel_occupancy[brick.slice] += 1

    def ordered_bricks(self):
        """Remove unbuildable interior/floating bricks and return instruction order."""
        ordered, deferred = self._reorder_bricks_for_stability(self.bricks)
        if deferred and self.remove_interior_deferred_bricks(deferred):
            ordered, _ = self._reorder_bricks_for_stability(self.bricks)
        if self.remove_floating_bricks():
            ordered, _ = self._reorder_bricks_for_stability(self.bricks)
        return ordered

    def _reorder_bricks_for_stability(self, bricks):
        return reorder_bricks_for_stability(bricks, (self.world_dim,) * 3)

    def _compute_exterior_mask(self):
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

    def _is_brick_interior(self, brick, exterior_mask):
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

    def remove_interior_deferred_bricks(self, deferred_bricks):
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

    def get_floating_bricks(self):
        return [brick for brick in self.bricks if self.brick_floats(brick)]

    def remove_floating_bricks(self):
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

    def brick_floats(self, brick):
        if brick.z == 0:
            return False
        if np.any(self.voxel_occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z - 1]):
            return False
        if brick.z != self.world_dim - 1 and np.any(self.voxel_occupancy[brick.slice_2d[0], brick.slice_2d[1], brick.z + 1]):
            return False
        return True


@dataclass(frozen=True)
class SupportAudit:
    conflicts: np.ndarray
    connected: np.ndarray


def audit_supports(structure, voxels):
    """Clean up the export and retain the largest grounded stud-connected component."""
    structure.ordered_bricks()
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
    structure.ordered_bricks()
    return SupportAudit(conflicts, connected)


def _add_internal_supports(voxels, colours, conflicts, *, broad, max_added):
    """Reinforce enclosed cavities near conflicts, without changing the exterior."""
    interior = binary_fill_holes(voxels) & ~voxels
    if not interior.any():
        return voxels, colours
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
        return voxels, colours
    # Inherit nearby material colors while leaving every existing cell intact.
    nearest = distance_transform_edt(~voxels, return_distances=False, return_indices=True)
    repaired, repaired_colours = voxels.copy(), colours.copy()
    repaired[additions] = True
    repaired_colours[additions] = colours[tuple(axis[additions] for axis in nearest)]
    return repaired, repaired_colours


def add_voxel_supports(voxels, colours, audit,
                       *, inside_only=False, broad=False, max_added=20_000,
                       max_grid_cells=4_000_000):
    """Thicken seams and bridge islands, preserving existing cells and colours."""
    if not audit.conflicts.any() or max_added <= 0:
        return voxels, colours
    shape = voxels.shape if inside_only else (*voxels.shape[:2], voxels.shape[2] + 1)
    if np.prod(shape) > max_grid_cells or max(shape) > 256:
        return voxels, colours
    if inside_only:
        return _add_internal_supports(voxels, colours, audit.conflicts, broad=broad, max_added=max_added)
    additions = {}

    def add(coord, colour):
        coord = tuple(int(value) for value in coord)
        if coord[2] >= voxels.shape[2] or not voxels[coord]:
            additions[coord] = colour

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
            add((x, y, support_z), colours[x, y, z])
            # When the underside already exists, a cap can still bridge brick seams.
            if z > 0 and voxels[x, y, support_z]:
                add((x, y, z + 1), colours[x, y, z])

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
            colour = colours[tuple(start)]
            current = start.copy()
            # Descend to the anchor's height before bridging horizontally.
            for axis in (2, 0, 1):
                while current[axis] != target[axis]:
                    add(current, colour)
                    add(current + (0, 0, 1), colour)
                    current[axis] += 1 if target[axis] > current[axis] else -1
            add(target + (0, 0, 1), colour)

    # A model with no retained ground needs a pillar before any seam repairs work.
    else:
        x, y, z = np.argwhere(voxels)[0]
        for support_z in range(z):
            add((x, y, support_z), colours[x, y, z])

    if not additions or len(additions) > max_added or int(voxels.sum()) + len(additions) > 100_000:
        return voxels, colours
    repaired = np.pad(voxels, ((0, 0), (0, 0), (0, 1)))
    repaired_colours = np.pad(colours, ((0, 0), (0, 0), (0, 1)))
    for coord, colour in additions.items():
        repaired[coord] = True
        repaired_colours[coord] = colour
    # Do not grow the grid when all supports fit under existing geometry.
    if not repaired[:, :, -1].any():
        repaired = repaired[:, :, :-1]
        repaired_colours = repaired_colours[:, :, :-1]
    return repaired, repaired_colours
