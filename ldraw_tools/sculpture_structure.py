"""Track brick occupancy, stud connections and supported build ordering."""

from dataclasses import dataclass
import networkx as nx
import numpy as np


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


def reorder_bricks_for_stability(
    bricks: list[Brick], shape: tuple[int, int, int]
) -> tuple[list[Brick], set[Brick]]:
    """
    Reorder bricks to place each at its absolute earliest possible position.

    Places ALL below-supported bricks per round (safe because z-first sorting
    guarantees monotonic placement), but only ONE above-supported brick per
    round (to allow correct interleaving with newly-unlocked below bricks).
    Uses an index-set for O(1) removal instead of O(n) list removal.

    Complexity: O(n × rounds) where rounds ≈ max(z), down from O(n²).

    Args:
        bricks: List of bricks to reorder
        shape: (x, y, z) size of the voxel space the bricks live in

    Returns:
        Tuple of (ordered bricks list, set of deferred/force-placed bricks)
    """
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
            if support == "ground" or support == "below":
                supported_below.append(idx)
            elif support == "above":
                supported_above.append(idx)
        supported_below.sort(
            key=lambda i: (
                bricks[i].z,
                bricks[i].x,
                bricks[i].y,
                bricks[i].h,
                bricks[i].w,
                bricks[i].color,
            )
        )
        supported_above.sort(
            key=lambda i: (
                -bricks[i].z,
                bricks[i].x,
                bricks[i].y,
                bricks[i].h,
                bricks[i].w,
                bricks[i].color,
            )
        )
        if supported_below:
            for idx in supported_below:
                brick = bricks[idx]
                place(brick)
                remaining_set.discard(idx)
                if brick.z > 0:
                    support_voxels = occupancy[
                        brick.slice_2d[0], brick.slice_2d[1], brick.z - 1
                    ]
                    deferred_support = deferred_voxels[
                        brick.slice_2d[0], brick.slice_2d[1], brick.z - 1
                    ]
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
            forced_idx = max(
                remaining_set,
                key=lambda i: (
                    -bricks[i].z,
                    bricks[i].x,
                    bricks[i].y,
                    bricks[i].h,
                    bricks[i].w,
                    bricks[i].color,
                ),
            )
            forced_brick = bricks[forced_idx]
            place(forced_brick)
            remaining_set.discard(forced_idx)
            deferred_bricks.add(forced_brick)
            deferred_voxels[forced_brick.slice] = True
    return (ordered_bricks, deferred_bricks)


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

    def n_components(self) -> int:
        return len(self.connected_components())

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
        for node in sorted(nodes):
            brick = self.bricks[node]
            assert voxel_subset[brick.slice].all()
            removed_bricks.append(brick)
            self.remove_brick(node)
        return removed_bricks
