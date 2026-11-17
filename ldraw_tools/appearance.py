"""Checks for defects people see that structural checks miss.

Every result is a warning naming placements, so an agent knows where to look:

* ``appearance.deep_overlap``: each part of a pair has geometry at least 2 LDU
  inside the other's body. Bodies are the boxes of each part's vertices without
  its studs, so seated studs never count, and a part sitting inside a hollow
  shell (seats in a moulded hull, a door in an arch) fails the test in one
  direction. Recognised connections and interlocking families (glass in frames,
  doors, hinges, Technic pins and axles, tyres on wheels, minifigure parts,
  flexible parts) are excluded. Vertices are a sample of the surface; open a
  close-up before changing the model.
* ``appearance.exposed_side_studs``: sideways studs with nothing on them whose
  outward ray leaves the model, so the bare stud is visible.
* ``appearance.glass_obstructed``: an opaque part covers half or more of a
  vertical pane within 16 LDU in front of or behind it.

The checks use part bounds and connector positions only. They complement, and
never replace, looking at the renders.
"""
from __future__ import annotations

import re

import numpy as np

from .collision import oriented_box

DEEP = 2.0          # LDU a vertex must lie inside the other part's body
REACH = 400.0       # LDU a sideways stud's ray must clear to face open space
PANE_GAP = 16.0     # LDU probed in front of and behind a pane
LIMIT = 20          # individual pair/pane warnings before a summary warning

FLEXIBLE = re.compile(r'hose|tube|cable|string|chain|tread|track link|band|lsynth|spring|rubber', re.I)
FIGURE = re.compile(r'minifig|figure', re.I)
SHAFT = re.compile(r'\bpin\b|axle|bush', re.I)
TYRE = re.compile(r'tyre|tire', re.I)
WHEEL = re.compile(r'wheel|rim|hub', re.I)
GLAZING = re.compile(r'glass|pane|windscreen|canopy', re.I)
FRAME = re.compile(r'window|door|frame|windscreen|glass|shutter|canopy', re.I)
DOOR = re.compile(r'door|frame|shutter|gate', re.I)
JOINT = re.compile(r'hinge|turntable|ball|socket|tow ball|clip|\bbar\b|holder|handle|lever', re.I)
FOLIAGE = re.compile(r'plant|leaves|leaf|flower|petal|foliage|grass|bush|tree|palm|stem|vine|bamboo|seaweed', re.I)
PANE = re.compile(r'glass|pane|window|windscreen|canopy|door', re.I)
SEAT = re.compile(r'seat|chair|minifig|figure', re.I)
_BODIES = {}


def description(item):
    return item.local.description or item.occurrence.reference


def transparent(item, clear):
    """Occurrence colours carry only codes; transparency comes from LDConfig."""
    return getattr(item.occurrence.colour, 'code', None) in clear


def interlocked(a, b, clear):
    """Known families whose parts legitimately occupy each other's bounds."""
    da, db = description(a), description(b)
    pair = (da, db)
    if any(FLEXIBLE.search(d) for d in pair) or any(SHAFT.search(d) for d in pair):
        return True
    if any(all(pattern.search(d) for d in pair) for pattern in (FIGURE, JOINT, DOOR, FOLIAGE)):
        return True  # figure assemblies, hinge halves, doors in frames, layered foliage
    if (TYRE.search(da) and WHEEL.search(db)) or (TYRE.search(db) and WHEEL.search(da)):
        return True
    for pane, other, pane_item in ((da, db, a), (db, da, b)):
        if (transparent(pane_item, clear) or GLAZING.search(pane)) and FRAME.search(other):
            return True
    return False


def vector(value):
    return np.array([value.x, value.y, value.z], float)


def body(item):
    """Local vertices without stud cylinders, and their box; cached per part."""
    code = item.occurrence.part_code.casefold()
    if code not in _BODIES:
        points = np.unique(np.round(np.array([(p.x, p.y, p.z) for p in item.local.points], float), 4), axis=0) \
            if item.local.points else np.zeros((0, 3))
        keep = np.ones(len(points), bool)
        # Protruding studs: connector studs plus stud primitives that are not
        # underside tubes (tube primitives are also listed as receptacles).
        tubes = {r.name for r in item.local.receptacles}
        cylinders = [(vector(f.position), vector(f.axis)) for f in item.local.connections if stud_like(f)]
        cylinders += [(vector(s.position), vector(s.up)) for s in item.local.studs if s.name not in tubes]
        for base, axis in cylinders:
            length = np.linalg.norm(axis)
            if length < 1e-9:
                continue
            axis = axis / length
            offset = points - base
            along = offset @ axis
            radial = np.linalg.norm(offset - np.outer(along, axis), axis=1)
            keep &= ~((along >= -0.01) & (along <= 4.01) & (radial <= 6.01))
        points = points[keep]
        _BODIES[code] = (points, points.min(axis=0), points.max(axis=0)) if len(points) else None
    return _BODIES[code]


def pose(item):
    matrix = np.array(item.occurrence.matrix.rows, float)
    if not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6):
        return None
    return matrix, vector(item.occurrence.position)


def penetrating(source, target):
    """Count source vertices deeper than DEEP inside target's body; and the deepest."""
    a, b = body(source), body(target)
    pa, pb = pose(source), pose(target)
    if a is None or b is None or pa is None or pb is None:
        return 0, 0.0
    points = a[0] @ pa[0].T + pa[1]
    local = (points - pb[1]) @ pb[0]
    low, high = b[1] + DEEP, b[2] - DEEP
    if np.any(low > high):
        return 0, 0.0
    hit = np.all((local > low) & (local < high), axis=1)
    if not hit.any():
        return 0, 0.0
    depth = np.minimum(local[hit] - b[1], b[2] - local[hit]).min(axis=1).max()
    return int(hit.sum()), float(depth)


def span(feature, axis):
    """A connector's extent along a shared axis, as projected coordinates."""
    start = vector(feature.position) @ axis
    length = feature.length * (vector(feature.axis) @ axis)
    if feature.centered:
        return start - abs(length) / 2, start + abs(length) / 2
    return min(start, start + length), max(start, start + length)


def radius(feature):
    sections = getattr(feature.profile, 'sections', ())
    return sections[0].radius if sections else None


def inserted(a, b):
    """A male interface sits inside a coaxial female one of the same radius.

    Covers bars in hollow studs, clips on bars and pins or axles in holes whose
    engagement the general contact query does not recognise. Grid-aligned studs
    and sockets that merely share an axis do not count: their spans must overlap.
    """
    for fa in a.connections:
        for fb in b.connections:
            if {fa.role.value, fb.role.value} != {'male', 'female'}:
                continue
            male, female = (fa, fb) if fa.role.value == 'male' else (fb, fa)
            rm, rf = radius(male), radius(female)
            # The male must fit the hole: a bar (R4) in a stud hole (R6) counts.
            if rm is None or rf is None or not rf - 2.5 <= rm <= rf + 0.6:
                continue
            axis = vector(fa.axis)
            if abs(axis @ vector(fb.axis)) < 0.995:
                continue
            offset = vector(fb.position) - vector(fa.position)
            if np.linalg.norm(offset - (offset @ axis) * axis) > 0.5:
                continue
            (a0, a1), (b0, b1) = span(fa, axis), span(fb, axis)
            if min(a1, b1) - max(a0, b0) > 1.0:
                return True
    return False


def deep_overlaps(pairs, by_index, connected, clear=frozenset()):
    """Pairs where each part has vertices well inside the other's body."""
    found = []
    for pair in pairs:
        if pair['status'] == 'rectangular_body_overlap':
            continue  # already an error with its own repair hint
        key = tuple(sorted(pair['instances']))
        if key in connected:
            continue
        a, b = (by_index[i] for i in pair['instances'])
        if interlocked(a, b, clear):
            continue
        count_ab, depth_ab = penetrating(a, b)
        if count_ab < 2:
            continue
        count_ba, depth_ba = penetrating(b, a)
        if count_ba < 2 or inserted(a, b):
            continue
        found.append(dict(instances=list(pair['instances']), depth=round(min(depth_ab, depth_ba), 1)))
    found.sort(key=lambda row: -row['depth'])
    return found


def stud_like(feature):
    sections = getattr(feature.profile, 'sections', ())
    return (feature.kind.value == 'stud' and feature.role.value == 'male' and len(sections) == 1
            and abs(sections[0].radius - 6) < 1e-6)


def facing(vector):
    axis = int(np.argmax(np.abs(vector)))
    return ('+' if vector[axis] > 0 else '-') + 'XYZ'[axis]


def boxes(inspection):
    lo = np.array([[o.bounds.min.x, o.bounds.min.y, o.bounds.min.z] for o in inspection.occurrences], float)
    hi = np.array([[o.bounds.max.x, o.bounds.max.y, o.bounds.max.z] for o in inspection.occurrences], float)
    return lo - 0.5, hi + 0.5


def ray_hits(origin, direction, lo, hi, reach):
    with np.errstate(divide='ignore', invalid='ignore'):
        inverse = 1.0 / np.where(np.abs(direction) < 1e-12, 1e-12, direction)
        t1, t2 = (lo - origin) * inverse, (hi - origin) * inverse
    near = np.max(np.minimum(t1, t2), axis=1)
    far = np.min(np.maximum(t1, t2), axis=1)
    return (far >= np.maximum(near, 0)) & (near <= reach)


def exposed_side_studs(inspection, mated=frozenset()):
    """Sideways studs with no mated part whose outward ray escapes the model."""
    if not inspection.occurrences:
        return []
    lo, hi = boxes(inspection)
    position = {o.index: n for n, o in enumerate(inspection.occurrences)}
    found = []
    for item in inspection.occurrences:
        for feature in item.connections:
            if not stud_like(feature) or (item.index, feature.feature_id) in mated:
                continue
            axis = np.array([feature.axis.x, feature.axis.y, feature.axis.z], float)
            if abs(axis[1]) >= 0.5:
                continue
            base = np.array([feature.position.x, feature.position.y, feature.position.z], float)
            hits = ray_hits(base + 4.5 * axis, axis, lo, hi, REACH)
            hits[position[item.index]] = False
            if not hits.any():
                found.append(dict(instance=item.index, at=[round(float(v), 1) + 0.0 for v in base],
                                  facing=facing(axis)))
    return found


def inside(points, box):
    centre, matrix, half = box
    local = (points - centre) @ matrix
    return np.all(np.abs(local) <= half + 1e-6, axis=1)


def obstructed_glass(inspection, clear):
    """Vertical panes with an opaque part across half or more of either face."""
    occurrences = list(inspection.occurrences)
    if not occurrences:
        return []
    lo, hi = boxes(inspection)
    found = []
    oriented = {}
    for n, item in enumerate(occurrences):
        # Transparent tiles, plates and bricks are lamps or trim with a backing on purpose.
        if not transparent(item, clear) or not PANE.search(description(item)):
            continue
        box = oriented_box(item)
        if box is None:
            continue
        centre, matrix, half = box
        k = int(np.argmin(half))
        others = [i for i in range(3) if i != k]
        if 2 * half[k] > 8 or min(2 * half[i] for i in others) < 16:
            continue
        normal = matrix[:, k]
        if abs(normal[1]) > 0.7:
            continue  # skylight or floor glass
        u, v = matrix[:, others[0]] * half[others[0]], matrix[:, others[1]] * half[others[1]]
        grid = np.array([(a, b) for a in np.linspace(-0.5, 0.5, 5) for b in np.linspace(-0.5, 0.5, 5)])
        for side in (1, -1):
            depth = np.linspace(1.0, PANE_GAP, 4)
            points = np.array([centre + side * (half[k] + d) * normal + a * u + b * v
                               for d in depth for a, b in grid])
            region_lo, region_hi = points.min(axis=0), points.max(axis=0)
            candidates = np.nonzero(np.all(hi >= region_lo, axis=1) & np.all(lo <= region_hi, axis=1))[0]
            covered = np.zeros(len(points), bool)
            blockers = {}
            for j in candidates:
                other = occurrences[j]
                if j == n or transparent(other, clear) or FRAME.search(description(other)) or SEAT.search(description(other)):
                    continue
                if j not in oriented:
                    oriented[j] = oriented_box(other)
                # A box that encloses the pane is a shell around it (a moulded hull), not a wall behind it.
                if oriented[j] is None or inside(centre[None, :], oriented[j])[0]:
                    continue
                hit = inside(points, oriented[j])
                if hit.any():
                    covered |= hit
                    blockers[other.index] = int(hit.sum())
            # A blocker counts when it covers the pane's face, at any probed depth.
            face = covered.reshape(len(depth), len(grid)).any(axis=0).mean()
            if face >= 0.5 and blockers:
                culprit = max(blockers, key=blockers.get)
                found.append(dict(instances=[item.index, culprit], side='front' if side > 0 else 'back',
                                  coverage=round(float(face), 2), facing=facing(side * normal)))
                break
    return found


def appearance_issues(inspection, *, pairs, contacts, contacts_checked, clear=frozenset(), meshes=()):
    """Warnings with occurrence indices; callers attach placement paths.

    ``clear`` holds the transparent colour codes of the installed LDConfig.
    ``meshes`` are pairs of meshing gears, whose teeth interleave by design.
    """
    from .common import issue
    by_index = {o.index: o for o in inspection.occurrences}
    connected = {tuple(sorted((c.first_occurrence.index, c.second_occurrence.index))) for c in contacts}
    connected |= {tuple(sorted(pair)) for pair in meshes}
    mated = frozenset((occ.index, feature.feature_id) for c in contacts
                      for occ, feature in ((c.first_occurrence, c.first), (c.second_occurrence, c.second)))
    problems = []
    deep = deep_overlaps(pairs, by_index, connected if contacts_checked else set(), clear)
    for row in deep[:LIMIT]:
        problems.append(issue('appearance.deep_overlap',
            f"These parts pass at least {row['depth']} LDU into each other's bodies. "
            'Open a close-up: they are probably inside each other.',
            severity='warning', instances=row['instances'], depth=row['depth']))
    if len(deep) > LIMIT:
        problems.append(issue('appearance.deep_overlap', f'{len(deep) - LIMIT} more deep overlaps are not listed.',
                              severity='warning', count=len(deep) - LIMIT))
    studs = exposed_side_studs(inspection, mated if contacts_checked else frozenset())
    if studs:
        owners = list(dict.fromkeys(s['instance'] for s in studs))
        problems.append(issue('appearance.exposed_side_studs',
            f'{len(studs)} sideways studs have nothing on them and face open space. '
            'Cover them with tiles or plates unless bare studs are intended.',
            severity='warning', count=len(studs), instances=owners[:30], examples=studs[:6]))
    panes = obstructed_glass(inspection, clear)
    for row in panes[:LIMIT]:
        problems.append(issue('appearance.glass_obstructed',
            f"An opaque part covers {int(row['coverage'] * 100)}% of this pane within {int(PANE_GAP)} LDU "
            f"on its {row['side']} side; the window will look blocked.",
            severity='warning', instances=row['instances'], side=row['side'], facing=row['facing']))
    summary = dict(deep_overlaps=len(deep), exposed_side_studs=len(studs), glass_obstructed=len(panes))
    return problems, summary
