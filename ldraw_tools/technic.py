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
    return json.loads((DATA / 'technic-parts.json').read_text())


def canonical(code):
    code = code.casefold().removesuffix('.dat')
    return registry()['aliases'].get(code, code)


def definition(local):
    """Return a reviewed definition only for its exact expanded geometry."""
    code = canonical(local.code)
    entry = registry()['parts'].get(code)
    if entry is None:
        return None
    key = id(local)
    cached = _geometry_cache.get(key)
    if cached is None or cached[0] is not local:
        digest = hashlib.sha256(json.dumps([jsonable(v) for v in local.points],
                                          separators=(',', ':')).encode()).hexdigest()
        cached = (local, digest)
        _geometry_cache[key] = cached
        if len(_geometry_cache) > 128:
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
            position=Vector(*port['at']), frame=frame_for_axis(Vector(*port['axis'])),
            profile=CylindricalProfile((CylindricalSection(shape, 6, port['length']),),
                centered=kind is not Kind.STUD, friction=port.get('friction', False),
                caps=CylindricalCaps.ONE if kind is Kind.STUD else CylindricalCaps.NONE),
            feature_id=PREFIX+port['id'], name=port['id'], owner_code=code,
            source=Source.OVERRIDE, confidence=1, freedoms=frozenset(freedoms),
            provenance=('nova:technic-parts-v1', entry['evidence']),
            scale_inheritance='none',
        )


def curate(inspection):
    occurrences = []
    for item in inspection.occurrences:
        entry = definition(item.local)
        # Non-rigid transforms must never receive authored mechanical evidence.
        matrix = np.asarray(item.occurrence.matrix.rows)
        proper = np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6) and np.linalg.det(matrix) > 0
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


def fit(first, second):
    """Full receiving-bore containment, keyed roll and positive engagement."""
    if not eligible(first, second):
        return None
    male, hole = (first, second) if first.kind in MALE else (second, first)
    residual = connection_residual(male, hole)
    if residual.distance > TOL or residual.alignment < math.cos(math.radians(0.5)):
        return None
    if hole.kind is Kind.AXLE_HOLE and residual.roll_alignment < math.cos(math.radians(0.5)):
        return None
    offset = (hole.position - male.position).dot(male.axis)
    low, high = offset - hole.length/2, offset + hole.length/2
    if hole.length <= TOL or low < -male.length/2-TOL or high > male.length/2+TOL:
        return None
    # Supported thin layers occupy a half-module cell of a standard grip.
    # Two such layers must jointly fill the pin grip before claiming retention.
    if male.kind is Kind.PIN and not (abs(offset) <= TOL and abs(hole.length-male.length) <= TOL or
                                      hole.length == 10 and abs(abs(offset)-5) <= TOL):
        return None
    return dict(interval=[low, high], engagement=hole.length,
                behavior='bearing' if male.kind is Kind.AXLE and hole.kind is Kind.PIN_HOLE else
                         'keyed' if male.kind is Kind.AXLE else 'pin',
                friction=male.profile.friction)


def contacts(inspection):
    """Only reviewed port pairs; other connection families are handled upstream."""
    items = inspection.occurrences
    for i, first in enumerate(items):
        for second in items[i+1:]:
            for a in first.connections:
                if not managed(a):
                    continue
                for b in second.connections:
                    details = fit(a, b)
                    if details is None:
                        continue
                    male = a if a.kind in MALE else b
                    yield ConnectionContact(first, second, a, b, connection_residual(a, b),
                        Status.POTENTIAL if male.kind is Kind.PIN and details['engagement'] < male.length-TOL
                        else Status.CONFIRMED)


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
                if (a, af) != (b, bf) and min(hi, high)-max(lo, low) > TOL:
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


def parts_report(parts, code=None):
    codes = [canonical(code)] if code else list(registry()['parts'])
    if any(c not in registry()['parts'] for c in codes):
        raise ValueError('Part is outside the reviewed Technic registry; use technic parts')
    result = []
    for c in codes:
        geometry = parts.geometry(c)
        entry = registry()['parts'][c]
        result.append(dict(ref=c+'.dat', **entry, geometry_matches=definition(geometry) is not None))
    return dict(version=1, units='LDU', parts=result,
                note='Reviewed nominal interfaces; manufacturing fit and strength remain unproven.')
