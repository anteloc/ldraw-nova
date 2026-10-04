"""Pack coloured voxels into rectangular bricks and reconnect loose regions."""

from collections import Counter
from types import SimpleNamespace

import networkx as nx
import numpy as np
from scipy import ndimage

from .sculpture_structure import BRICK_PARTS, Brick, ConnectivityBrickStructure


def first_zero_idx(arr, axis=-1):
    """Index of the first zero along an axis, or the axis length."""
    arr_eq_zero = arr == 0
    return np.where(arr_eq_zero.any(axis=axis), np.argmax(arr_eq_zero, axis=axis), arr.shape[axis])


def first_nonzero_idx(arr, axis=-1):
    return first_zero_idx(arr == 0, axis)


def k_ring_neighbors(node, k, graph):
    shortest_paths = nx.single_source_shortest_path(graph, node, cutoff=k)
    return list(shortest_paths.keys())


class Voxel2Brick:
    """Fixed-seed rectangular-brick packing and greedy reconnection."""

    def __init__(self, voxels, seed=42, colour_array=None, use_colour_constraints=False,
                 hard_constraints=False, min_support_ratio=0.5, surface_mask=None):
        self.voxels = voxels.astype(bool)
        self.bricks = ConnectivityBrickStructure(voxels.shape)
        self.colour_array = colour_array
        self.surface_mask = surface_mask if surface_mask is not None else voxels.astype(bool)
        self.use_colour_constraints = use_colour_constraints and colour_array is not None
        self.hard_constraints = hard_constraints
        self.min_support_ratio = min_support_ratio
        self.rng = np.random.default_rng(seed)

    @property
    def max_x(self):
        return self.voxels.shape[0]

    @property
    def max_y(self):
        return self.voxels.shape[1]

    @property
    def max_z(self):
        return self.voxels.shape[2]

    def __call__(self):
        self._brickify_voxels_greedy(self.voxels, self._greedy_priority)
        disconnected_bricks = self._find_disconnected_bricks()
        if disconnected_bricks:
            bricks_to_remerge = self._find_bricks_around_disconnected_bricks()
            self.bricks.remove_voxel_subset(bricks_to_remerge)
            original_hard_constraints = self.hard_constraints
            self.hard_constraints = False
            self._brickify_voxels_greedy(bricks_to_remerge, self._component_priority)
            self.hard_constraints = original_hard_constraints
        if self.colour_array is not None:
            self._assign_colours_to_bricks()
        for brick_id in self._find_disconnected_bricks():
            self.bricks.remove_brick(brick_id)
        return list(self.bricks.bricks.values())

    def _brickify_voxels_greedy(self, voxel_subset, priority):
        min_z = first_nonzero_idx(voxel_subset.sum(axis=(0, 1)))
        max_z = self.max_z - first_nonzero_idx(voxel_subset.sum(axis=(0, 1))[::-1])
        for z in range(min_z, max_z):
            self._brickify_layer_greedy(voxel_subset, z, priority)
        assert ((self.bricks.voxel_bricks != 0) == (self.voxels != 0)).all()

    def _brickify_layer_greedy(self, voxel_subset, z, priority):
        brick_dimensions = list(BRICK_PARTS) + [(w, h) for h, w in BRICK_PARTS if h != w]
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
        valid_brick_placements = list(filter(lambda b: voxel_subset[b.slice].all(), all_brick_placements))
        valid_brick_placements = list(filter(self._has_sufficient_support, valid_brick_placements))
        if self.use_colour_constraints:
            colour_valid_placements = []
            for brick in valid_brick_placements:
                if self._is_brick_colour_uniform(brick):
                    colour_valid_placements.append(brick)
                elif not self.hard_constraints:
                    colour_valid_placements.append(brick)
            valid_brick_placements = colour_valid_placements
        for brick in sorted(valid_brick_placements, key=priority):
            try:
                self.bricks.add_brick(brick)
            except ValueError:
                pass

    def _get_shell_voxels(self, brick):
        """Original surface cells within a brick; interior fill does not constrain colour."""
        shell_voxels = []
        z_val = brick.z
        for x in range(brick.x, brick.x + brick.h):
            for y in range(brick.y, brick.y + brick.w):
                if self.surface_mask[x, y, z_val]:
                    shell_voxels.append((x, y, z_val))
        return shell_voxels

    def _is_brick_colour_uniform(self, brick):
        """Whether the visible cells share one colour."""
        if self.colour_array is None:
            return True
        shell_voxels = self._get_shell_voxels(brick)
        if len(shell_voxels) == 0:
            return True
        else:
            colours = np.array([self.colour_array[x, y, z] for x, y, z in shell_voxels])
        if colours.size == 0:
            return True
        first_colour = colours.flat[0]
        return (colours == first_colour).all()

    def _greedy_priority(self, brick):
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

    def _component_priority(self, brick):
        return (-self._count_connecting_components(brick), -brick.area, self.rng.uniform())

    def _calc_support_ratio(self, brick):
        """Calculate support ratio from below."""
        if brick.z == 0:
            return 1.0
        total_area = brick.h * brick.w
        supported_area = self.voxels[*brick.slice_2d, brick.z - 1].sum()
        return supported_area / total_area

    def _calc_support_ratio_above(self, brick):
        """Calculate support ratio from above."""
        if brick.z >= self.max_z - 1:
            return 1.0
        total_area = brick.h * brick.w
        supported_area = self.voxels[*brick.slice_2d, brick.z + 1].sum()
        return supported_area / total_area

    def _has_sufficient_support(self, brick):
        """Require support above or below; allow 1x1 bricks to cover remaining cells."""
        if brick.h == 1 and brick.w == 1:
            return True
        support_below = self._calc_support_ratio(brick)
        support_above = self._calc_support_ratio_above(brick)
        return (support_below >= self.min_support_ratio or support_above >= self.min_support_ratio)

    def _count_gaps(self, brick):
        """Sum seam depths below a candidate brick to favour interlocking layers."""
        if brick.z == 0:
            return 0
        structure_under_brick = self.bricks.voxel_bricks[*brick.slice_2d, : brick.z]
        horz_gaps = structure_under_brick[:-1, :, :] != structure_under_brick[1:, :, :]
        vert_gaps = structure_under_brick[:, :-1, :] != structure_under_brick[:, 1:, :]
        horz_gap_depths = first_zero_idx(horz_gaps[..., ::-1])
        vert_gap_depths = first_zero_idx(vert_gaps[..., ::-1])
        return horz_gap_depths.sum() + vert_gap_depths.sum()

    def _count_connecting_components(self, brick):
        """Number of existing stud components joined by a candidate brick."""
        components = set()
        if brick.z > 0:
            components |= set(np.unique(self.bricks.component_labels()[*brick.slice_2d, brick.z - 1])) - {0}
        if brick.z < self.max_z - 1:
            components |= set(np.unique(self.bricks.component_labels()[*brick.slice_2d, brick.z + 1])) - {0}
        return len(components)

    def _assign_colours_to_bricks(self):
        """Use the majority surface colour, or interior colour for hidden bricks."""
        if self.colour_array is None:
            return
        brick_ids = list(self.bricks.bricks.keys())
        for brick_id in brick_ids:
            if not self.bricks.node_exists(brick_id):
                continue
            brick = self.bricks.bricks[brick_id]
            shell_voxels = self._get_shell_voxels(brick)
            if len(shell_voxels) == 0:
                colours_in_brick = self.colour_array[brick.slice]
            else:
                shell_colours = [self.colour_array[x, y, z] for x, y, z in shell_voxels]
                colours_in_brick = np.array(shell_colours)
            if colours_in_brick.size == 0:
                continue
            unique_colours, counts = np.unique(colours_in_brick, return_counts=True)
            majority_colour = int(unique_colours[np.argmax(counts)])
            self.bricks.remove_brick(brick_id)
            coloured_brick = Brick(
                h=brick.h,
                w=brick.w,
                x=brick.x,
                y=brick.y,
                z=brick.z,
                colour=majority_colour,
            )
            self.bricks.add_brick(coloured_brick)

    def _find_disconnected_bricks(self):
        """Brick IDs outside the largest stud-connected component."""
        if len(self.bricks.bricks) == 0:
            return []
        components = list(nx.connected_components(self.bricks.connection_graph))
        if len(components) <= 1:
            return []
        largest_component = max(components, key=len)
        disconnected = []
        for component in components:
            if component != largest_component:
                disconnected.extend(component)
        return disconnected

    def _find_bricks_around_disconnected_bricks(self, k_ring=1):
        """Mark disconnected bricks and their nearby neighbours for repacking."""
        disconnected_brick_ids = self._find_disconnected_bricks()
        if not disconnected_brick_ids:
            return np.zeros_like(self.voxels)
        critical_voxels = np.zeros_like(self.voxels)
        for brick_id in disconnected_brick_ids:
            if not self.bricks.node_exists(brick_id):
                continue
            critical_nodes = k_ring_neighbors(brick_id, k_ring, self.bricks.neighbor_graph)
            for node in critical_nodes:
                if self.bricks.node_exists(node):
                    brick = self.bricks.bricks[node]
                    critical_voxels[brick.slice] = 1
        return critical_voxels


PREVIEW_SIZES = sorted(((2, 8), (2, 6), (2, 4), (2, 3), (2, 2),
                        (1, 8), (1, 6), (1, 4), (1, 3), (1, 2), (1, 1)),
                       key=lambda size: (-size[0] * size[1], -size[0]))
EMPTY = -1


def _connectivity(bricks, owner):
    """Group bricks joined by vertical overlap; anything not joined to layer 0 is loose."""
    parent = list(range(len(bricks)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for layer in range(owner.shape[2] - 1):
        (a, b) = (owner[:, :, layer], owner[:, :, layer + 1])
        both = (a >= 0) & (b >= 0)
        for (p, q) in set(zip(a[both].tolist(), b[both].tolist())):
            parent[find(p)] = find(q)
    ground_roots = {find(i) for (i, brick) in enumerate(bricks) if brick[3] == 0}
    loose = [i for i in range(len(bricks)) if find(i) not in ground_roots]
    return SimpleNamespace(bricks=bricks, owner=owner, loose=loose, grounded_groups=len(ground_roots))


def _pack_layers(grid):
    """Bottom-up greedy packer that prefers bricks bonding to the grounded structure."""
    (width, depth, layers) = grid.shape
    owner = np.full(grid.shape, -1, dtype=np.int32)
    bricks = []
    parent = []
    grounded_roots = set()

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for layer in range(layers):
        along_x = layer % 2 == 0
        colors = grid[:, :, layer]
        free = owner[:, :, layer]
        below_owner = owner[:, :, layer - 1] if layer else None
        present = colors != EMPTY
        cells = list(zip(*np.nonzero(present)))
        if layer:
            dist = ndimage.distance_transform_cdt(below_owner == -1, metric='taxicab')
        else:
            dist = np.zeros(colors.shape, dtype=int)
        same = np.zeros(colors.shape, dtype=int)
        for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            shifted = np.full(colors.shape, EMPTY - 1)
            xs = slice(max(dx, 0), colors.shape[0] + min(dx, 0))
            zs = slice(max(dz, 0), colors.shape[1] + min(dz, 0))
            xd = slice(max(-dx, 0), colors.shape[0] + min(-dx, 0))
            zd = slice(max(-dz, 0), colors.shape[1] + min(-dz, 0))
            shifted[xd, zd] = colors[xs, zs]
            same += (shifted == colors) & present
        (sx, sz) = ((1, 1), (-1, -1), (1, -1), (-1, 1))[layer % 4]
        cells.sort(key=lambda ik: (-dist[ik], same[ik] >= 3, sx * ik[0], sz * ik[1]))
        for (i, k) in cells:
            if free[i, k] != -1:
                continue
            color = colors[i, k]
            best = None
            best_score = None
            for (w, l) in PREVIEW_SIZES:
                if w == l:
                    orientations = ((w, l),)
                else:
                    orientations = ((l, w), (w, l)) if along_x else ((w, l), (l, w))
                for (fx, fz) in orientations:
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
                            score = (grounded, bool(below), len(roots), len(below), fx * fz, (fx >= fz) == along_x)
                            if best_score is None or score > best_score:
                                (best, best_score) = ((x0, z0, fx, fz), score)
            (x0, z0, fx, fz) = best
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
    return (bricks, owner)


def _repair_loose(work, result, warnings):
    """Last resort: recolor loose cells to match a grounded neighbor on the same layer (so a brick
    can bridge to it); anything still loose after that is removed."""
    loose = set(result.loose)
    changed = 0
    for n in loose:
        (color, x0, z0, layer, fx, fz) = result.bricks[n]
        neighbors = Counter()
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
        warnings.append(f'Recolored {changed} stud(s) of unsupported overhang so they could bond to the model.')
    return work


def preview_pack(grid):
    """Greedy layer packing used only to check a voxel design before visual review."""
    bricks, owner = _pack_layers(grid)
    return _connectivity(bricks, owner)
