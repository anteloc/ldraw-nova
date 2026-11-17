"""Version-pinned frame adaptation for pyldraw3 1.7 stud/wheel mating.

LDCad SNAP_CYL female spans point inward (-Y in the meta frame). pyldraw's
strict stud contact query expects an outward receptacle axis instead. Its
generic snap solver aligns axes, so primitive outward sockets need the inverse
adaptation there. Only temporary query frames change, never library metadata.
Remove/retest this adapter when changing the pyldraw3 dependency pin.
"""
from dataclasses import replace
from importlib.metadata import version

import numpy as np
from ldraw import Matrix, Vector
from ldraw.connection_types import (ConnectionKind, ConnectionSource, ConnectionRole,
                                    CylindricalProfile, CylindricalCaps, SectionShape)

LDCAD = {ConnectionSource.LDCAD_SHADOW, ConnectionSource.LDCAD_INLINE}
REVERSE_AXIS = Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 1]])

# Inspected closed underside cavities; pyldraw 1.7 labels R 6 cylinders
# longer than a stud as pin holes. Keep this separate from generic pin mating.
# 67329 inherits its underside from 22885. See the parrot SNOT reference.
DEEP_STUD_SOCKETS = {'22885': 36, '67329': 36, '47457': 12}


def query_frames(inspection, *, snapping=False):
    def adapt(feature, item):
        # 6014a/b is wider along Z than its rim diameter. The 1.7 annular
        # heuristic picks the shortest bounding-box axis (X), although the
        # wheel hole and official 6014bc01 shortcut establish local Z as axle.
        # Correct query evidence only, retaining the official shortcut centre
        # at Z=-6 and its compatibility list. Never rewrite source geometry.
        if (item.occurrence.part_code.casefold() in {'6014a', '6014b'}
                and feature.kind is ConnectionKind.RIM_SEAT
                and feature.source is ConnectionSource.SHORTCUT
                and '6015' in feature.compatible_parts):
            bounds = item.local.bounds
            feature = replace(feature,
                              frame=item.occurrence.matrix * Matrix([[1,0,0],[0,0,-1],[0,1,0]]),
                              profile=replace(feature.profile, radius=max(bounds.size.x,bounds.size.y)/2,
                                              width=bounds.size.z),
                              provenance=(*feature.provenance, 'nova:6014-local-Z-wheel-axis'))
        authored = feature.source in LDCAD
        profile = feature.profile
        deep_stud_socket = (
            item.occurrence.part_code.casefold() in DEEP_STUD_SOCKETS
            and feature.kind is ConnectionKind.PIN_HOLE
            and isinstance(profile, CylindricalProfile)
            and len(profile.sections) == 1
            and profile.sections[0].shape is SectionShape.ROUND
            and abs(profile.length - DEEP_STUD_SOCKETS[item.occurrence.part_code.casefold()]) < 1e-6
        )
        # LDCad uses closed S 6 cavities for ordinary 1-wide brick/slope
        # undersides. pyldraw 1.7 classifies long ones as pin holes and rejects
        # round/square profile pairs. The inspected deep round sockets above
        # have the same classification problem. Both projections remain
        # potential evidence; other round/axle/pin interfaces are unchanged.
        if (authored and feature.role is ConnectionRole.FEMALE
                and isinstance(profile, CylindricalProfile) and not profile.centered
                and profile.caps in {CylindricalCaps.ONE, CylindricalCaps.B}
                and profile.length >= 4 and profile.sections
                and all((s.shape is SectionShape.SQUARE or deep_stud_socket) and abs(s.radius-6) < 1e-6
                        and not s.flexible for s in profile.sections)):
            feature = replace(feature, kind=ConnectionKind.STUD_RECEPTACLE,
                              source=ConnectionSource.HEURISTIC, confidence=min(feature.confidence, 0.8),
                              profile=replace(profile, sections=tuple(replace(s, shape=SectionShape.ROUND)
                                                                     for s in profile.sections)),
                              provenance=(*feature.provenance,
                                          'nova:deep-stud-socket' if deep_stud_socket
                                          else 'nova:inscribed-stud-in-square-socket'))
        if feature.kind is ConnectionKind.STUD_RECEPTACLE and (authored != snapping):
            feature = replace(feature, frame=feature.frame * REVERSE_AXIS)
        return feature
    return replace(inspection, occurrences=tuple(
        replace(item, connections=tuple(adapt(f, item) for f in item.connections))
        for item in inspection.occurrences))


def connection_contacts(inspection):
    """Port pairs by the Technic fit rules; every other pair by pyldraw's generic matcher.

    A Technic port can still mate with a part that has no ports (a System part
    with a pin, an unlisted connector); only port-to-port pairs must pass the
    stricter rules, so the generic matcher's port-to-port matches are dropped.
    """
    from .technic import managed, contacts
    if not any(managed(f) for o in inspection.occurrences for f in o.connections):
        return (*query_frames(inspection).connection_contacts(), *contacts(inspection))
    mixed = [c for c in query_frames(inspection).connection_contacts()
             if not (managed(c.first) and managed(c.second))]
    return (*mixed, *contacts(inspection))


# --- Bounds of an occurrence without a Python loop over every point ---------
# pyldraw 1.7 transforms each expanded point with a separate Matrix * Vector;
# a model of a few hundred parts spends most of an inspection there. NumPy
# finds the extreme points; the few candidates on a rotated axis are then
# recomputed with the library's own arithmetic, so the box is bit-identical.
_point_arrays = {}
_NEAR = 1e-6


def _points_array(points):
    key = id(points)
    cached = _point_arrays.get(key)
    if cached is None or cached[0] is not points:
        array = np.array([(p.x, p.y, p.z) for p in points], float).reshape(-1, 3)
        cached = (points, array)
        _point_arrays[key] = cached
        if len(_point_arrays) > 4096:
            _point_arrays.pop(next(iter(_point_arrays)))
    return cached[1]


def transformed_bounds(points, *, position, matrix):
    """Exact world AABB of expanded points; same values as pyldraw's loop."""
    from ldraw.part_geometry_types import BoundingBox
    if not isinstance(points, tuple):
        points = tuple(points)
    local = _points_array(points)
    if not len(local):
        return None
    rows = np.asarray(matrix.rows, float)
    origin = (position.x, position.y, position.z)
    world = local @ rows.T
    low, high = [], []
    for axis in range(3):
        values = world[:, axis]
        used = np.flatnonzero(rows[axis])
        least, most = float(values.min()), float(values.max())
        if len(used) == 1 and abs(rows[axis][used[0]]) == 1.0:
            # A signed coordinate: the product is exact in both implementations.
            low.append(least + origin[axis])
            high.append(most + origin[axis])
            continue

        def exact(index):
            point = position + matrix * points[index]
            return (point.x, point.y, point.z)[axis]

        low.append(min(exact(i) for i in np.flatnonzero(values <= least + _NEAR)))
        high.append(max(exact(i) for i in np.flatnonzero(values >= most - _NEAR)))
    return BoundingBox(min=Vector(*low), max=Vector(*high))


def install_fast_bounds():
    """Version-pinned: retest against the library loop when the pin changes."""
    import ldraw.inspection as inspection
    if version('pyldraw3') == '1.7.0' and getattr(inspection.transformed_bounds, '__module__', '') != __name__:
        inspection.library_transformed_bounds = inspection.transformed_bounds
        inspection.transformed_bounds = transformed_bounds


install_fast_bounds()
