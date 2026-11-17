"""Reviewed Technic interfaces and seating, independent of mechanism simulation.

The registry replaces only mechanical features on measured, fingerprinted parts.
Unknown parts keep their original evidence. Contacts involving a reviewed port
must satisfy these rules; the generic cylinder solver cannot bypass them.
"""
from __future__ import annotations

from collections import OrderedDict, defaultdict
from dataclasses import replace
from functools import lru_cache
import hashlib
import json
import math

import numpy as np
from ldraw import Matrix, Vector
from ldraw.connection_types import (
    ConnectionFeature, ConnectionKind as Kind, ConnectionRole as Role,
    ConnectionSource as Source, ConnectionStatus as Status,
    ConnectionFreedom as Freedom, CylindricalProfile, CylindricalSection,
    CylindricalCaps, SectionShape, SnapTransform, connection_residual,
    frame_for_axis, snap_transform,
)
from ldraw.inspection import ConnectionContact, SnapCandidate

from .common import DATA, jsonable

MECHANICAL = {Kind.PIN, Kind.PIN_HOLE, Kind.AXLE, Kind.AXLE_HOLE}
MALE = {Kind.PIN, Kind.AXLE}
HOLES = {Kind.PIN_HOLE, Kind.AXLE_HOLE}
PREFIX = 'technic:'
TOL = 0.2
_geometry_cache = OrderedDict()


@lru_cache(maxsize=1)
def registry():
    """Reviewed parts plus the table derived from shadow metadata; reviewed wins."""
    reviewed = json.loads((DATA / 'technic-parts.json').read_text())
    path = DATA / 'technic-ports.json'
    derived = json.loads(path.read_text()) if path.exists() else dict(parts={}, aliases={})
    parts = {code: entry for code, entry in derived['parts'].items() if entry['role'] != 'withheld'}
    parts.update(reviewed['parts'])
    aliases = {**derived.get('aliases', {}), **reviewed['aliases']}
    return dict(version=reviewed['version'], units=reviewed['units'], parts=parts, aliases=aliases)


STRUCTURAL_ROLES = frozenset({'member', 'connector', 'shaft', 'retainer', 'bridge'})


def structural(code):
    """A static frame part: beams, bricks, pins, axles and bushes, not gears or equipment."""
    entry = registry()['parts'].get(canonical(code))
    return entry is not None and entry['role'] in STRUCTURAL_ROLES


def reviewed(code):
    """True for a hand-measured entry, False for one derived from shadow data."""
    entry = registry()['parts'].get(canonical(code))
    return entry is not None and 'geometry_sha256' in entry


def canonical(code):
    code = code.casefold().removesuffix('.dat')
    return registry()['aliases'].get(code, code)


def definition(local):
    """Return a reviewed definition only for its exact expanded geometry."""
    code = canonical(local.code)
    entry = registry()['parts'].get(code)
    if entry is None:
        return None
    if 'geometry_sha256' not in entry:
        # Derived entry: valid while the metadata it was made from is unchanged.
        features = local.connections
        key = id(features)
        cached = _geometry_cache.get(key)
        if cached is None or cached[0] is not features:
            from .technic_ports import fingerprint
            cached = (features, fingerprint(features))
            _geometry_cache[key] = cached
            if len(_geometry_cache) > 512:
                _geometry_cache.popitem(last=False)
        return entry if cached[1] == entry['features_sha256'] else None
    # pyldraw builds a new PartGeometry per lookup but shares its points tuple,
    # so key the fingerprint on the points: one hash per part and process.
    points = local.points
    key = id(points)
    cached = _geometry_cache.get(key)
    if cached is None or cached[0] is not points:
        digest = hashlib.sha256(json.dumps([jsonable(v) for v in points],
                                          separators=(',', ':')).encode()).hexdigest()
        cached = (points, digest)
        _geometry_cache[key] = cached
        if len(_geometry_cache) > 512:
            _geometry_cache.popitem(last=False)
    return entry if cached[1] == entry['geometry_sha256'] else None


def managed(feature):
    return bool(feature.feature_id and feature.feature_id.startswith(PREFIX)
                and feature.kind in MECHANICAL)


def local_features(code, entry):
    for port in entry['ports']:
        kind = Kind(port['kind'])
        male = kind in MALE or kind is Kind.STUD
        shape = SectionShape.AXLE if kind in {Kind.AXLE, Kind.AXLE_HOLE} else SectionShape.ROUND
        freedoms = set()
        if kind in {Kind.PIN, Kind.PIN_HOLE}:
            freedoms.add(Freedom.ROTATE)
        if kind in {Kind.AXLE, Kind.AXLE_HOLE}:
            freedoms.add(Freedom.SLIDE)
        yield ConnectionFeature(
            kind=kind, role=Role.MALE if male else Role.FEMALE,
            position=Vector(*port['at']),
            # A recorded radial turns the cross (bent arms, crosses moulded at 45 degrees).
            frame=frame_for_axis(Vector(*port['axis']), radial=Vector(*port['radial']) if 'radial' in port else None),
            profile=CylindricalProfile((CylindricalSection(shape, 6, port['length']),),
                centered=kind not in {Kind.STUD, Kind.STUD_RECEPTACLE}, friction=port.get('friction', False),
                caps=CylindricalCaps.ONE if kind in {Kind.STUD, Kind.STUD_RECEPTACLE} else CylindricalCaps.NONE),
            feature_id=PREFIX+port['id'], name=port['id'], owner_code=code,
            source=Source.OVERRIDE, confidence=1, freedoms=frozenset(freedoms),
            provenance=(('nova:technic-parts-v1', entry['evidence']) if 'evidence' in entry
                        else ('nova:technic-ports-v1', 'LDCad shadow SNAP_CYL metadata')),
            scale_inheritance='none',
        )


# A rotation written with three or four decimals (0.966, 0.7071) is still a rotation.
ROUNDED = 2.5e-3


def curate(inspection):
    occurrences = []
    for item in inspection.occurrences:
        entry = definition(item.local)
        # Scaled, sheared or mirrored transforms never receive mechanical ports; rounding is tolerated.
        matrix = np.asarray(item.occurrence.matrix.rows)
        proper = np.allclose(matrix.T @ matrix, np.eye(3), atol=ROUNDED) and np.linalg.det(matrix) > 0
        if entry is not None and proper:
            retained = tuple(f for f in item.connections if f.kind not in MECHANICAL
                             and not (f.feature_id or '').startswith(PREFIX))
            ports = tuple(f.transformed(position=item.occurrence.position,
                                        matrix=item.occurrence.matrix, inherit=False)
                          for f in local_features(canonical(item.local.code), entry))
            item = replace(item, connections=(*retained, *ports))
        occurrences.append(item)
    return replace(inspection, occurrences=tuple(occurrences))


def eligible(first, second):
    if not (managed(first) and managed(second)):
        return False
    a, b = (first, second) if first.kind in MALE else (second, first)
    return (a.kind is Kind.PIN and b.kind is Kind.PIN_HOLE or
            a.kind is Kind.AXLE and b.kind in HOLES)


# A cross keys within 5 degrees. Official models leave bushes and axles a few degrees off
# (0.5-5 degrees is common there); a wrongly rolled part is off by 45 or 90.
KEYED_ROLL = math.cos(math.radians(5))
# Derived hole lengths are rounded up to whole modules (a 7 LDU bevel gear is listed as 10,
# an 8 LDU plate as 10), so neighbours on one shaft can seem to overlap by up to 3 LDU.
NOMINAL_SLACK = 3.0

# An axle end may stop inside a hole: it still keys or bears on what it fills.
# It must fill a whole module, less the 2.5 LDU by which nominal lengths can
# exceed a blind bore. A pin grip must sit wholly in its hole.
AXLE_ENGAGEMENT = 2.5


def engaged(male, hole):
    """(low, high) of the hole along the male, clipped to the male for axles; None if not engaged."""
    offset = (hole.position - male.position).dot(male.axis)
    low, high = offset - hole.length/2, offset + hole.length/2
    half = male.length/2
    if hole.length <= TOL:
        return None
    if low >= -half-TOL and high <= half+TOL:
        return low, high
    if male.kind is Kind.AXLE:
        low, high = max(low, -half), min(high, half)
        if high - low >= min(hole.length, 10) - AXLE_ENGAGEMENT - TOL:
            return low, high
    return None


def fit(first, second):
    """Receiving-bore engagement, keyed roll and alignment."""
    if not eligible(first, second):
        return None
    male, hole = (first, second) if first.kind in MALE else (second, first)
    residual = connection_residual(male, hole)
    if residual.distance > TOL or residual.alignment < math.cos(math.radians(0.5)):
        return None
    if hole.kind is Kind.AXLE_HOLE and residual.roll_alignment < KEYED_ROLL:
        return None
    span = engaged(male, hole)
    if span is None:
        return None
    low, high = span
    offset = (hole.position - male.position).dot(male.axis)
    # Supported thin layers occupy a half-module cell of a standard grip.
    # Two such layers must jointly fill the pin grip before claiming retention.
    if male.kind is Kind.PIN and not (abs(offset) <= TOL and abs(hole.length-male.length) <= TOL or
                                      hole.length == 10 and abs(abs(offset)-5) <= TOL):
        return None
    return dict(interval=[low, high], engagement=high - low,
                behavior='bearing' if male.kind is Kind.AXLE and hole.kind is Kind.PIN_HOLE else
                         'keyed' if male.kind is Kind.AXLE else 'pin',
                friction=male.profile.friction)


def fit_failure(first, second):
    """The first fit rule an aligned pair fails, in words an agent can act on."""
    if not eligible(first, second):
        return 'family: a pin needs a pin hole; an axle needs an axle hole or a pin hole'
    male, hole = (first, second) if first.kind in MALE else (second, first)
    residual = connection_residual(male, hole)
    if residual.distance > TOL or residual.alignment < math.cos(math.radians(0.5)):
        return 'alignment: the axes are offset or tilted'
    if hole.kind is Kind.AXLE_HOLE and residual.roll_alignment < KEYED_ROLL:
        return 'keyed roll: the axle cross does not line up with the cross hole'
    offset = (hole.position - male.position).dot(male.axis)
    if engaged(male, hole) is None:
        return ('engagement: the hole runs past the end of the pin or axle; move it along the axis or use a longer one'
                if male.kind is Kind.PIN else
                'engagement: too little of the axle is inside the hole; move it along the axis or use a longer one')
    if male.kind is Kind.PIN and not (abs(offset) <= TOL and abs(hole.length-male.length) <= TOL or
                                      hole.length == 10 and abs(abs(offset)-5) <= TOL):
        return 'pin grip: centre the pin in a full-depth hole, or use two half-depth layers'
    return None


def nearby_ports(inspection):
    """Conservative broad phase for seating and contact checks.

    A pair whose axial spans touch must have centres within their combined
    half-lengths (plus tolerance). Filter in NumPy; retain the exact fit rules.
    Include incompatible families here so seating review can diagnose them.
    """
    males, holes = [], []
    for item in inspection.occurrences:
        for feature in item.connections:
            if managed(feature):
                (males if feature.kind in MALE else holes).append((item, feature))
    if not holes:
        return
    centres = np.array([jsonable(f.position) for _, f in holes])
    lengths = np.array([f.length for _, f in holes])
    for owner, male in males:
        delta = centres - jsonable(male.position)
        reach = (male.length + lengths) / 2 + 2 * TOL
        for index in np.flatnonzero(np.einsum('ij,ij->i', delta, delta) <= reach * reach):
            receiver, hole = holes[index]
            if owner.index != receiver.index:
                yield owner, male, receiver, hole


def contacts(inspection):
    """Only reviewed port pairs; other connection families are handled upstream."""
    order = {o.index: i for i, o in enumerate(inspection.occurrences)}
    ports = {id(f): i for o in inspection.occurrences for i, f in enumerate(o.connections)}
    found = []
    for owner, male, receiver, hole in nearby_ports(inspection):
        details = fit(male, hole)
        if details is None:
            continue
        first, a, second, b = (owner, male, receiver, hole) if order[owner.index] < order[receiver.index] else (receiver, hole, owner, male)
        contact = ConnectionContact(first, second, a, b, connection_residual(a, b),
            Status.POTENTIAL if male.kind is Kind.PIN and details['engagement'] < male.length-TOL
            else Status.CONFIRMED)
        found.append(((order[first.index], order[second.index], ports[id(a)], ports[id(b)]), contact))
    # Preserve the original occurrence/feature order for reports and consumers.
    yield from (contact for _, contact in sorted(found, key=lambda row: row[0]))


def endpoints(contact):
    if contact.first.kind in MALE:
        return contact.first_occurrence, contact.first, contact.second_occurrence, contact.second
    return contact.second_occurrence, contact.second, contact.first_occurrence, contact.first


def conflicts(found):
    """Distinct occupied intervals may share a shaft; intersecting ones may not."""
    by_male, by_hole = defaultdict(list), defaultdict(list)
    for contact in found:
        if not (managed(contact.first) and managed(contact.second)):
            continue
        m, mf, h, hf = endpoints(contact)
        interval = fit(mf, hf)['interval']
        by_male[m.index, mf.feature_id].append((h.index, hf.feature_id, interval))
        by_hole[h.index, hf.feature_id].append((m.index, mf.feature_id))
    problems = []
    for (owner, port), spans in by_male.items():
        for i, (a, af, (lo, hi)) in enumerate(spans):
            for b, bf, (low, high) in spans[i+1:]:
                if (a, af) != (b, bf) and min(hi, high)-max(lo, low) > NOMINAL_SLACK + TOL:
                    problems.append(dict(code='technic.occupied_span', instances=sorted({owner, a, b}), port=port))
    for (owner, port), males in by_hole.items():
        if len(set(males)) > 1:
            problems.append(dict(code='technic.occupied_hole', instances=sorted({owner, *[m[0] for m in males]}), port=port))
    return problems


def candidates(inspection, moving, fixed=None):
    subject = next(o for o in inspection.occurrences if o.index == moving)
    for target in inspection.occurrences:
        if target.index == moving or fixed is not None and target.index != fixed:
            continue
        for a in subject.connections:
            for b in target.connections:
                if not eligible(a, b):
                    continue
                male, hole = (a, b) if a.kind in MALE else (b, a)
                margin = (male.length-hole.length)/2
                if margin < -TOL:
                    continue
                offsets = [0.0] if abs(margin) <= TOL else [-margin, margin]
                if male.kind is Kind.AXLE and margin > TOL:
                    offsets += [float(i) for i in range(math.ceil(-margin/10), math.floor(margin/10)+1)
                                for i in [i*10]]
                    # Preserve an already useful continuous axial coordinate.
                    offsets.append(max(-margin, min(margin, (a.position-b.position).dot(b.axis))))
                delta = snap_transform(a, b)
                for offset in sorted(set(offsets)):
                    shifted = delta.position + b.axis * offset
                    yield SnapCandidate(subject, target, a, b,
                        SnapTransform(shifted + delta.matrix * subject.occurrence.position,
                                      delta.matrix * subject.occurrence.matrix),
                        connection_residual(a, b))


@lru_cache(maxsize=1)
def corpus_uses():
    """Placements of each part in the official Technic sets (scripts/technic_corpus.py)."""
    path = DATA / 'technic-corpus.json'
    return json.loads(path.read_text())['uses'] if path.exists() else {}


def parts_report(parts, code=None, *, role=None, query=None, top=40):
    """One part in full, or the most used parts with ports as a compact list."""
    entries = registry()['parts']
    if code:
        key = canonical(code)
        if key not in entries:
            raise ValueError(f'{code} has no Technic ports in the registry; try technic parts --query WORDS')
        entry = entries[key]
        return dict(version=1, units='LDU', parts=[dict(
            ref=key + '.dat', **entry, source='reviewed' if 'geometry_sha256' in entry else 'shadow',
            uses_in_official_sets=corpus_uses().get(key, 0),
            geometry_matches=definition(parts.geometry(key)) is not None)],
            note='Nominal interfaces; manufacturing fit and strength remain unproven.')
    uses = corpus_uses()
    words = [w.casefold() for w in (query or '').split()]
    rows = []
    for key, entry in entries.items():
        if role and entry['role'] != role:
            continue
        if words and not all(w in entry['description'].casefold() or w == key for w in words):
            continue
        kinds = {}
        for port in entry['ports']:
            kinds[port['kind']] = kinds.get(port['kind'], 0) + 1
        rows.append(dict(ref=key + '.dat', description=entry['description'], role=entry['role'],
                         ports=', '.join(f'{n} {k}' for k, n in kinds.items()), uses=uses.get(key, 0)))
    rows.sort(key=lambda row: (-row['uses'], row['ref']))
    rows = [f"{r['ref']} | {r['description']} | {r['role']} | {r['ports']} | {r['uses']} uses" for r in rows[:top]]
    return dict(version=1, matched=len(rows) if len(rows) < top else sum(
                    1 for k, e in entries.items() if (not role or e['role'] == role)
                    and all(w in e['description'].casefold() or w == k for w in words)),
                shown=len(rows), parts=rows,
                roles=sorted({e['role'] for e in entries.values()}),
                note='uses: placements in the official Technic sets. part CODE lists a part\'s port IDs.')
