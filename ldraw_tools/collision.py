"""Conservative box tests; connector metadata is not a solid-volume model."""
from __future__ import annotations

import numpy as np

from .common import jsonable

TOLERANCE = 1e-5  # LDU; touching faces are not penetration.


def oriented_box(item, profile=None):
    matrix = np.asarray(item.occurrence.matrix.rows, dtype=float)
    if not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6, rtol=0):
        return None
    if profile is None:
        bounds = item.local.bounds
        if bounds is None:
            return None
        low, high = np.array(jsonable(bounds.min)), np.array(jsonable(bounds.max))
    else:
        x, z, h = profile['x_studs'] * 10, profile['z_studs'] * 10, profile['height']
        low, high = np.array([-x, 0, -z]), np.array([x, h, z])
    centre = matrix @ ((low + high) / 2) + np.array(jsonable(item.occurrence.position))
    return centre, matrix, (high - low) / 2


def penetration(first, second):
    """15-axis separating-axis test. None means separated or touching."""
    ca, aa, ha = first
    cb, ab, hb = second
    axes = [*aa.T, *ab.T, *(np.cross(a, b) for a in aa.T for b in ab.T)]
    depths = []
    for axis in axes:
        length = np.linalg.norm(axis)
        if length < 1e-10:
            continue
        axis = axis / length
        depth = np.abs(aa.T @ axis) @ ha + np.abs(ab.T @ axis) @ hb - abs((cb-ca) @ axis)
        if depth <= TOLERANCE:
            return None
        depths.append(float(depth))
    return min(depths)


def collision_pairs(inspection, regular, *, moving=None):
    """Yield AABB candidates, refined by oriented geometry/body envelopes.

    With moving indices, check only cross-boundary pairs; a rigid move preserves
    all internal relationships. The final model still needs full validation.
    """
    boxes = {o.index: oriented_box(o) for o in inspection.occurrences}
    bodies = {o.index: oriented_box(o, regular[o.occurrence.part_code.casefold()])
              for o in inspection.occurrences if o.occurrence.part_code.casefold() in regular}
    ordered = sorted(inspection.occurrences, key=lambda o: o.bounds.min.x)
    for i, first in enumerate(ordered):
        a = np.array([jsonable(first.bounds.min), jsonable(first.bounds.max)])
        for j in range(i + 1, len(ordered)):
            second = ordered[j]
            if second.bounds.min.x >= a[1, 0] - TOLERANCE:
                break
            if moving is not None and (first.index in moving) == (second.index in moving):
                continue
            b = np.array([jsonable(second.bounds.min), jsonable(second.bounds.max)])
            depths = np.minimum(a[1], b[1]) - np.maximum(a[0], b[0])
            if not np.all(depths > TOLERANCE):
                continue
            indices = [first.index, second.index]
            status, depth = 'review_aabb_only', None
            ba, bb = boxes[first.index], boxes[second.index]
            if ba is not None and bb is not None:
                status = 'oriented_bounds_separated' if penetration(ba, bb) is None else 'review_oriented_bounds'
            ba, bb = bodies.get(first.index), bodies.get(second.index)
            if status != 'oriented_bounds_separated' and ba is not None and bb is not None:
                depth = penetration(ba, bb)
                status = 'rectangular_body_overlap' if depth is not None else 'stud_zone_overlap_review_connections'
            yield dict(instances=indices, depths=depths.tolist(), status=status,
                       body_penetration=depth)
