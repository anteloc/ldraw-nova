# Adapted from BrickBuilderAI, copyright (c) 2026 Jake Johnson.
# MIT license: see LICENSE.brickbuilder. Integration changes are documented in README.md.
from typing import Callable
import networkx as nx
import numpy as np
from .brick_library import BRICK_PARTS
from .brick_structure import Brick, ConnectivityBrickStructure


def first_zero_idx(arr: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Finds the index of the first occurrence of 0 along axis
    Returns the length of the last dimension if no zero occurs.
    """
    arr_eq_zero = arr == 0
    return np.where(
        arr_eq_zero.any(axis=axis), np.argmax(arr_eq_zero, axis=axis), arr.shape[axis]
    )


def first_nonzero_idx(arr: np.ndarray, axis: int = -1) -> np.ndarray:
    return first_zero_idx(arr == 0, axis)


def k_ring_neighbors(node, k: int, graph: nx.Graph) -> list:
    shortest_paths = nx.single_source_shortest_path(graph, node, cutoff=k)
    return list(shortest_paths.keys())


def valid_brick(h, w) -> bool:
    return tuple(sorted((h, w))) in BRICK_PARTS


def get_merged_brick(b1: Brick, b2: Brick) -> Brick | None:
    assert b1.z == b2.z
    if b1.x == b2.x and b1.h == b2.h and (b1.y + b1.w == b2.y or b2.y + b2.w == b1.y):
        new_h, new_w = (b1.h, b1.w + b2.w)
        if valid_brick(new_h, new_w):
            new_x, new_y = (b1.x, min(b1.y, b2.y))
            return Brick(h=new_h, w=new_w, x=new_x, y=new_y, z=b1.z)
    elif b1.y == b2.y and b1.w == b2.w and (b1.x + b1.h == b2.x or b2.x + b2.h == b1.x):
        new_h, new_w = (b1.h + b2.h, b1.w)
        if valid_brick(new_h, new_w):
            new_x, new_y = (min(b1.x, b2.x), b1.y)
            return Brick(h=new_h, w=new_w, x=new_x, y=new_y, z=b1.z)
    return None


class Voxel2Brick:
    def __init__(
        self,
        voxels: np.ndarray,
        max_failures: int = 10,
        seed: int = 42,
        color_array: np.ndarray = None,
        run_stability_passes: bool = False,
        use_color_constraints: bool = False,
        hard_constraints: bool = False,
        wc: float = 1000.0,
        min_support_ratio: float = 0.5,
        surface_mask: np.ndarray = None,
    ):
        self.voxels = voxels.astype(bool)
        self.bricks = ConnectivityBrickStructure(voxels.shape)
        self.color_array = color_array
        self.run_stability_passes = run_stability_passes
        self.surface_mask = (
            surface_mask if surface_mask is not None else voxels.astype(bool)
        )
        self.use_color_constraints = use_color_constraints and color_array is not None
        self.hard_constraints = hard_constraints
        self.wc = wc
        self.min_support_ratio = min_support_ratio
        self.n_failures = 0
        self.max_failures = max_failures
        self.rng = np.random.default_rng(seed)
        self.disconnected_voxels: list[tuple[int, int, int]] = []

    @property
    def max_x(self) -> int:
        return self.voxels.shape[0]

    @property
    def max_y(self) -> int:
        return self.voxels.shape[1]

    @property
    def max_z(self) -> int:
        return self.voxels.shape[2]

    def __call__(self) -> list[Brick]:
        self._brickify_voxels_greedy(self.voxels, self._greedy_priority)
        min_components_possible = nx.number_connected_components(
            self.bricks.neighbor_graph
        )
        n_components = self.bricks.n_components()
        if self.run_stability_passes:
            self.n_failures = 0
            while self.n_failures < self.max_failures:
                if n_components == min_components_possible:
                    break
                critical_voxels = self._find_critical_voxels_connectivity()
                removed_bricks = self.bricks.remove_voxel_subset(critical_voxels)
                reverse_layer_order = self.rng.uniform() > 0.5
                self._brickify_voxels_greedy(
                    critical_voxels,
                    self._component_priority,
                    reverse_layer_order=reverse_layer_order,
                )
                new_n_components = self.bricks.n_components()
                if new_n_components < n_components:
                    n_components = new_n_components
                    self.n_failures = 0
                else:
                    self.bricks.remove_voxel_subset(critical_voxels)
                    self.bricks.add_bricks(removed_bricks)
                    self.n_failures += 1
        disconnected_bricks = self._find_disconnected_bricks()
        if disconnected_bricks:
            for brick_id in disconnected_bricks:
                if self.bricks.node_exists(brick_id):
                    brick = self.bricks.bricks[brick_id]
                    for x in range(brick.x, brick.x + brick.h):
                        for y in range(brick.y, brick.y + brick.w):
                            self.disconnected_voxels.append((x, y, brick.z))
            bricks_to_remerge = self._find_bricks_around_disconnected_bricks()
            removed_bricks = self.bricks.remove_voxel_subset(bricks_to_remerge)
            original_hard_constraints = self.hard_constraints
            self.hard_constraints = False
            self._brickify_voxels_greedy(bricks_to_remerge, self._component_priority)
            self.hard_constraints = original_hard_constraints
        if self.color_array is not None:
            self._assign_colors_to_bricks()
        return list(self.bricks.bricks.values())

    def _brickify_voxels_greedy(
        self,
        voxel_subset: np.ndarray,
        priority: Callable,
        reverse_layer_order: bool = False,
    ) -> None:
        self._brickify_voxels(
            voxel_subset,
            lambda v, z: self._brickify_layer_greedy(v, z, priority),
            reverse_layer_order=reverse_layer_order,
        )

    def _brickify_voxels(
        self,
        voxel_subset: np.ndarray,
        layer_brickify_fn: Callable,
        reverse_layer_order: bool = False,
    ) -> None:
        min_z = first_nonzero_idx(voxel_subset.sum(axis=(0, 1)))
        max_z = self.max_z - first_nonzero_idx(voxel_subset.sum(axis=(0, 1))[::-1])
        if reverse_layer_order:
            for z in reversed(range(min_z, max_z)):
                layer_brickify_fn(voxel_subset, z)
        else:
            for z in range(min_z, max_z):
                layer_brickify_fn(voxel_subset, z)
        assert ((self.bricks.voxel_bricks != 0) == (self.voxels != 0)).all()

    def _brickify_layer_greedy(
        self, voxel_subset: np.ndarray, z: int, priority: Callable
    ) -> None:
        brick_dimensions = list(BRICK_PARTS) + [
            (w, h) for h, w in BRICK_PARTS if h != w
        ]
        min_x = first_nonzero_idx(voxel_subset[..., z].sum(axis=1))
        max_x = self.max_x - first_nonzero_idx(voxel_subset[..., z].sum(axis=1)[::-1])
        min_y = first_nonzero_idx(voxel_subset[..., z].sum(axis=0))
        max_y = self.max_y - first_nonzero_idx(voxel_subset[..., z].sum(axis=0)[::-1])
        all_brick_placements = [
            Brick(h=h, w=w, x=x, y=y, z=z)
            for h, w in brick_dimensions
            for x in range(min_x, max_x - h + 1)
            for y in range(min_y, max_y - w + 1)
        ]
        valid_brick_placements = list(
            filter(lambda b: voxel_subset[b.slice].all(), all_brick_placements)
        )
        valid_brick_placements = list(
            filter(self._has_sufficient_support, valid_brick_placements)
        )
        if self.use_color_constraints:
            color_valid_placements = []
            for brick in valid_brick_placements:
                if self._is_brick_color_uniform(brick):
                    color_valid_placements.append(brick)
                elif not self.hard_constraints:
                    color_valid_placements.append(brick)
            valid_brick_placements = color_valid_placements
        for brick in sorted(valid_brick_placements, key=priority):
            try:
                self.bricks.add_brick(brick)
            except ValueError:
                pass

    def _get_shell_voxels(self, brick: Brick) -> list[tuple[int, int, int]]:
        """
        Get list of shell (surface) voxel positions for a brick.

        Uses surface_mask if available (which tracks original surface voxels vs interior fill).
        Otherwise falls back to checking if voxel is exposed to outside.
        """
        shell_voxels = []
        z_val = brick.z
        for x in range(brick.x, brick.x + brick.h):
            for y in range(brick.y, brick.y + brick.w):
                if self.surface_mask[x, y, z_val]:
                    shell_voxels.append((x, y, z_val))
        return shell_voxels

    def _is_brick_color_uniform(self, brick: Brick) -> bool:
        """Check if all shell (surface) voxels in brick have the same color."""
        if self.color_array is None:
            return True
        shell_voxels = self._get_shell_voxels(brick)
        if len(shell_voxels) == 0:
            return True
        else:
            colors = np.array([self.color_array[x, y, z] for x, y, z in shell_voxels])
        if colors.size == 0:
            return True
        first_color = colors.flat[0]
        return (colors == first_color).all()

    def _assign_brick_color(self, brick: Brick) -> Brick:
        """Assign color to a brick based on its voxel colors."""
        if self.color_array is None:
            return brick
        colors = self.color_array[brick.slice]
        if colors.size == 0:
            return brick
        unique_colors, counts = np.unique(colors, return_counts=True)
        majority_color = int(unique_colors[np.argmax(counts)])
        return Brick(
            h=brick.h, w=brick.w, x=brick.x, y=brick.y, z=brick.z, color=majority_color
        )

    def _greedy_priority(self, brick: Brick):
        dangles = 1 if 0 < self._calc_support_ratio(brick) < 1 else 0
        shorter_side = min(brick.h, brick.w)
        ori_priority = (-1 if brick.ori == 0 else 1) * (-1) ** brick.z
        return (
            -dangles,
            -self._count_gaps(brick),
            -shorter_side,
            -brick.area,
            ori_priority,
            brick.x,
            brick.y,
            brick.z,
        )

    def _component_priority(self, brick: Brick):
        return (
            -self._count_connecting_components(brick),
            -brick.area,
            self.rng.uniform(),
        )

    def _calc_support_ratio(self, brick: Brick) -> float:
        """Calculate support ratio from below."""
        if brick.z == 0:
            return 1.0
        total_area = brick.h * brick.w
        supported_area = self.voxels[*brick.slice_2d, brick.z - 1].sum()
        return supported_area / total_area

    def _calc_support_ratio_above(self, brick: Brick) -> float:
        """Calculate support ratio from above."""
        if brick.z >= self.max_z - 1:
            return 1.0
        total_area = brick.h * brick.w
        supported_area = self.voxels[*brick.slice_2d, brick.z + 1].sum()
        return supported_area / total_area

    def _has_sufficient_support(self, brick: Brick) -> bool:
        """
        Check if a brick has sufficient support from below OR above.
        A brick needs at least min_support_ratio of its studs supported to be stable.
        For example, with min_support_ratio=0.5, a 2x4 brick needs at least 4 studs supported.

        1x1 bricks are always allowed since they're the smallest unit and must be placed
        to cover all voxels (even floating ones).
        """
        if brick.h == 1 and brick.w == 1:
            return True
        support_below = self._calc_support_ratio(brick)
        support_above = self._calc_support_ratio_above(brick)
        return (
            support_below >= self.min_support_ratio
            or support_above >= self.min_support_ratio
        )

    def _count_gaps(self, brick: Brick) -> int:
        """
        A "gap" is a pair of voxels beneath the brick that belong to two different bricks
        (and hence those two bricks will be connected by placing the brick).
        This function returns the sum of the depths of gaps beneath the brick.
        """
        if brick.z == 0:
            return 0
        structure_under_brick = self.bricks.voxel_bricks[*brick.slice_2d, : brick.z]
        horz_gaps = structure_under_brick[:-1, :, :] != structure_under_brick[1:, :, :]
        vert_gaps = structure_under_brick[:, :-1, :] != structure_under_brick[:, 1:, :]
        horz_gap_depths = first_zero_idx(horz_gaps[..., ::-1])
        vert_gap_depths = first_zero_idx(vert_gaps[..., ::-1])
        return horz_gap_depths.sum() + vert_gap_depths.sum()

    def _count_connecting_components(self, brick: Brick) -> int:
        """
        Returns the number of components that will be connected if brick is added to the structure.
        """
        components = set()
        if brick.z > 0:
            components |= set(
                np.unique(self.bricks.component_labels()[*brick.slice_2d, brick.z - 1])
            ) - {0}
        if brick.z < self.max_z - 1:
            components |= set(
                np.unique(self.bricks.component_labels()[*brick.slice_2d, brick.z + 1])
            ) - {0}
        return len(components)

    def _assign_colors_to_bricks(self) -> None:
        """
        Assign colors to all bricks based on the majority color of shell (surface) voxels.
        Shell voxels are those visible from outside - they determine the brick's visual appearance.
        """
        if self.color_array is None:
            return
        brick_ids = list(self.bricks.bricks.keys())
        for brick_id in brick_ids:
            if not self.bricks.node_exists(brick_id):
                continue
            brick = self.bricks.bricks[brick_id]
            shell_voxels = self._get_shell_voxels(brick)
            if len(shell_voxels) == 0:
                colors_in_brick = self.color_array[brick.slice]
            else:
                shell_colors = [self.color_array[x, y, z] for x, y, z in shell_voxels]
                colors_in_brick = np.array(shell_colors)
            if colors_in_brick.size == 0:
                continue
            unique_colors, counts = np.unique(colors_in_brick, return_counts=True)
            majority_color = int(unique_colors[np.argmax(counts)])
            self.bricks.remove_brick(brick_id)
            colored_brick = Brick(
                h=brick.h,
                w=brick.w,
                x=brick.x,
                y=brick.y,
                z=brick.z,
                color=majority_color,
            )
            self.bricks.add_brick(colored_brick)

    def _find_disconnected_bricks(self) -> list[int]:
        """
        Find bricks that are not connected to the main structure via connection_graph.
        Returns a list of brick IDs that are disconnected (not in the largest component).
        """
        if len(self.bricks.bricks) == 0:
            return []
        components = list(nx.connected_components(self.bricks.connection_graph))
        if len(components) <= 1:
            return []
        largest_component = max(components, key=len)
        disconnected = []
        for component in components:
            if component != largest_component:
                disconnected.extend(sorted(component))
        return disconnected

    def _find_bricks_around_disconnected_bricks(self, k_ring: int = 1) -> np.ndarray:
        """
        Find the voxels of bricks surrounding disconnected bricks.
        Similar to _get_critical_voxels but for all disconnected bricks.
        Returns a voxel array marking the bricks to be removed and re-added.

        Args:
            k_ring: Size of k-ring neighborhood (default=1 only immediate neighbording bricks)
        """
        disconnected_brick_ids = self._find_disconnected_bricks()
        if not disconnected_brick_ids:
            return np.zeros_like(self.voxels)
        critical_voxels = np.zeros_like(self.voxels)
        for brick_id in disconnected_brick_ids:
            if not self.bricks.node_exists(brick_id):
                continue
            critical_nodes = k_ring_neighbors(
                brick_id, k_ring, self.bricks.neighbor_graph
            )
            for node in critical_nodes:
                if self.bricks.node_exists(node):
                    brick = self.bricks.bricks[node]
                    critical_voxels[brick.slice] = 1
        return critical_voxels

    def _find_critical_voxels_connectivity(self) -> np.ndarray:
        """
        From the Legolization paper
        """
        nodes = list(self.bricks.bricks.keys())
        pvals = np.array(
            [self._num_neighboring_components(node) - 1 for node in nodes], dtype=float
        )
        pvals /= pvals.sum()
        selected_node_idx = np.argmax(self.rng.multinomial(1, pvals))
        weakest_node = nodes[selected_node_idx]
        return self._get_critical_voxels(weakest_node)

    def _num_neighboring_components(self, node: int) -> int:
        components = {
            self.bricks.node2component()[neighbor]
            for neighbor in self.bricks.neighbor_graph.neighbors(node)
        } | {self.bricks.node2component()[node]}
        return len(components)

    def _get_critical_voxels(self, critical_node) -> np.ndarray:
        critical_nodes = k_ring_neighbors(
            critical_node, self._k_ring_size(), self.bricks.neighbor_graph
        )
        critical_bricks = [self.bricks.bricks[n] for n in critical_nodes]
        critical_voxels = np.zeros_like(self.voxels)
        for brick in critical_bricks:
            critical_voxels[brick.slice] = 1
        return critical_voxels

    def _k_ring_size(self) -> int:
        return self.n_failures // 10 + 1
