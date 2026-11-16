"""Technic ports for any part, derived from its LDCad connector metadata.

The reviewed registry (``data/technic-parts.json``) names the ports of a few
dozen measured parts. This module derives the same kind of record for every
other part from the authored ``SNAP_CYL`` cylinders that ship with the shadow
library: where each pin, axle, pin hole and axle hole is, which way it runs
and how long its nominal engagement is.

The derivation is deliberately small and testable:

* only authored cylinders count (no primitive inference), and grouped snaps
  (rails, universal-joint internals) are left out;
* a male is cut where it changes between pin and axle and at its collars, and
  a long pin is cut into 20 LDU grips, because that is what a hole receives;
* lengths snap to the 10 LDU module, so a 16 LDU bore between two 2 LDU
  recesses is a 20 LDU hole;
* a male and a female of the same part that already sit in each other (a
  shortcut assembly) are internal and are not ports.

``scripts/technic_ports.py`` writes the result to ``data/technic-ports.json``;
tests require it to reproduce the reviewed registry.
"""
from __future__ import annotations

import hashlib
import json
import re

import numpy as np

MECHANICAL = ('pin', 'pin_hole', 'axle', 'axle_hole')
AUTHORED = ('ldcad_shadow', 'ldcad_inline')
MODULE = 20.0

# Friction comes from the description; these parts have ridges it omits.
FRICTION_OVERRIDES = {'32054': True, '87082': True, '65304': True}

ROLES = (
    ('connector', r'^Technic (Pin|Axle Pin)\b(?!.*(Joiner|Connector))'),
    ('shaft', r'^Technic Axle\b(?!.*(Joiner|Connector|Pin|Towball|Flexible))'),
    ('retainer', r'^Technic Bush\b'),
    ('gear', r'^Technic (Gear|Worm|Turntable|Differential|Clutch)\b|Gear Rack'),
    ('wheel', r'^(Wheel|Technic Wheel|Technic Wedge Belt Wheel|Technic Tread Sprocket|Technic Sprocket)\b'),
    ('member', r'^Technic (Beam|Brick|Plate|Liftarm|Cross Block|Connector|Angle Connector|Axle Joiner|'
               r'Pin Joiner|Pin Connector|Axle Connector|Panel|Fairing|Steering|Suspension|Link|Frame|Rotor|'
               r'Triangle|Cam|Engine|Crankshaft|Changeover|Driving Ring|Shock|Linear Actuator|Hub)\b'),
)


def clean_description(text):
    return (text or '').lstrip('~=_ ').strip()


def role_for(description):
    text = clean_description(description)
    for role, pattern in ROLES:
        if re.search(pattern, text):
            return role
    return 'equipment'


def friction_for(code, description):
    if code in FRICTION_OVERRIDES:
        return FRICTION_OVERRIDES[code]
    text = clean_description(description)
    return 'with Friction' in text and 'without Friction' not in text


def raw_features(connections):
    """Authored mechanical cylinders as plain rows, in a stable order."""
    rows = []
    for feature in connections:
        if feature.kind.value not in MECHANICAL or feature.source.value not in AUTHORED:
            continue
        sections = getattr(feature.profile, 'sections', None)
        if not sections:
            continue
        axis = np.array([feature.axis.x, feature.axis.y, feature.axis.z], float)
        norm = np.linalg.norm(axis)
        if norm < 1e-9:
            continue
        axis = axis / norm
        position = np.array([feature.position.x, feature.position.y, feature.position.z], float)
        total = float(sum(s.length for s in sections))
        start = position - axis * total / 2 if feature.profile.centered else position
        rows.append(dict(male=feature.role.value == 'male', start=start, axis=axis,
                         sections=[(s.shape.value, float(s.radius), float(s.length)) for s in sections],
                         group=getattr(feature, 'group', None)))
    return rows


def fingerprint(connections):
    """Hash of the metadata a derived entry was made from."""
    rows = [[r['male'], np.round(r['start'], 3).tolist(), np.round(r['axis'], 6).tolist(),
             [[s, round(a, 3), round(b, 3)] for s, a, b in r['sections']], r['group']]
            for r in raw_features(connections)]
    rows.sort(key=lambda row: json.dumps(row))
    text = json.dumps(rows, separators=(',', ':')).replace('-0.0', '0.0')
    return hashlib.sha256(text.encode()).hexdigest()


def _classes(sections, male):
    out, cursor = [], 0.0
    for shape, radius, length in sections:
        if shape == 'axle':
            kind = 'axle'
        elif shape == 'round' and 5.4 <= radius <= 6.6:
            kind = 'pin'
        elif shape == 'round' and 6.6 < radius <= 9.5:
            kind = 'collar'
        elif shape == 'round' and 3.4 <= radius <= 4.6 and male:
            kind = 'nozzle'
        else:
            kind = 'skip'
        if out and out[-1][0] == kind:
            out[-1][2] = cursor + length
        else:
            out.append([kind, cursor, cursor + length])
        cursor += length
    return out


def _male_runs(sections):
    """(kind, low, high, stops) along the feature for each pin or axle run."""
    runs = _classes(sections, True)
    if any(kind == 'skip' and high - low > 1e-6 for kind, low, high in runs) and \
            not any(kind in ('pin', 'axle') for kind, low, high in runs):
        return []
    result = []
    for index, (kind, low, high) in enumerate(runs):
        if kind not in ('pin', 'axle'):
            continue
        stops = set()
        before = runs[index - 1] if index else None
        after = runs[index + 1] if index + 1 < len(runs) else None
        for side, neighbour in (('-', before), ('+', after)):
            if neighbour is None or neighbour[0] != 'collar':
                continue
            width = neighbour[2] - neighbour[1]
            other = runs[index - 2] if side == '-' and index >= 2 else runs[index + 2] if side == '+' and index + 2 < len(runs) else None
            shared = other is not None and other[0] == kind
            keep = width / 2 if shared else width if kind == 'pin' or other is None or other[0] not in ('pin', 'axle') else 0.0
            if side == '-':
                low -= keep
            else:
                high += keep
            stops.add(side)
        result.append([kind, low, high, stops])
    final = []
    for kind, low, high, stops in result:
        count = round((high - low) / MODULE)
        if kind == 'pin' and count >= 2 and abs((high - low) - MODULE * count) <= 2.5:
            step = (high - low) / count
            for i in range(count):
                ends = {s for s in stops if (s == '-' and i == 0) or (s == '+' and i == count - 1)}
                final.append((kind, low + step * i, low + step * (i + 1), ends))
        else:
            final.append((kind, low, high, stops))
    return final


def _female_runs(sections):
    runs = [r for r in _classes(sections, False) if r[0] != 'nozzle']
    used = [r for r in runs if r[0] in ('pin', 'axle', 'collar')]
    if not any(r[0] in ('pin', 'axle') for r in used):
        return []
    low, high = used[0][1], used[-1][2]
    axle = sum(r[2] - r[1] for r in used if r[0] == 'axle')
    kind = 'axle_hole' if axle >= 5 else 'pin_hole'
    count = round((high - low) / MODULE)
    if kind == 'pin_hole' and count >= 2 and abs((high - low) - MODULE * count) <= 2.5:
        step = (high - low) / count
        return [(kind, low + step * i, low + step * (i + 1), set()) for i in range(count)]
    return [(kind, low, high, set())]


def nominal(length, female):
    """Snap an engagement length to the 10 LDU module when it is close."""
    target = round(length / 10) * 10
    if target >= 10 and abs(length - target) <= (4.5 if female else 2.5):
        return float(target)
    return round(float(length), 3)


def _parallel(a, b):
    return abs(abs(float(a @ b)) - 1) < 1e-4


def _same_line(p, a, q, tolerance=0.75):
    delta = q - p
    return float(np.linalg.norm(delta - (delta @ a) * a)) <= tolerance


def derive(connections):
    """Ports and hose nozzles of one part from its authored connector metadata.

    Returns ``(ports, nozzles)``. Ports are dictionaries with ``kind``, ``at``
    (centre), ``axis``, ``length`` and, on males, ``stops``; they carry no ID
    yet. Nozzles have ``at`` (base) and ``outward``.
    """
    ports, nozzles = [], []
    for row in raw_features(connections):
        if row['group'] or any(shape == 'square' for shape, _, _ in row['sections']):
            continue
        axis, start = row['axis'], row['start']
        if row['male']:
            classes = _classes(row['sections'], True)
            if len(classes) == 1 and classes[0][0] == 'nozzle':
                nozzles.append(dict(at=start.copy(), outward=axis.copy(), length=classes[0][2]))
                continue
            runs = _male_runs(row['sections'])
        else:
            runs = _female_runs(row['sections'])
        for kind, low, high, stops in runs:
            length = nominal(high - low, not row['male'])
            if length < 7.5:
                continue
            centre = start + axis * (low + high) / 2
            if not row['male']:
                kind = kind  # already pin_hole / axle_hole
            ports.append(dict(kind=kind, at=centre, axis=axis.copy(), length=length,
                              male=row['male'], stops=set(stops), raw=(high - low)))
    # One port per place: prefer an axle hole over a pin hole, the longer over the shorter.
    kept = []
    for port in sorted(ports, key=lambda p: (-p['length'], p['kind'] != 'axle_hole')):
        duplicate = None
        for other in kept:
            if other['male'] != port['male'] or not _parallel(other['axis'], port['axis']):
                continue
            if not _same_line(other['at'], other['axis'], port['at']):
                continue
            gap = abs(float((port['at'] - other['at']) @ other['axis']))
            if gap + port['length'] / 2 <= other['length'] / 2 + 1.0 and (port['male'] is False or port['kind'] == other['kind']):
                duplicate = other
                break
        if duplicate is None:
            kept.append(port)
        else:
            duplicate['stops'] |= port['stops']
    # A long male that only repeats shorter runs (a pin described whole and by halves) is dropped.
    result = []
    for port in kept:
        inner = [o for o in kept if o is not port and o['male'] and port['male'] and o['kind'] == port['kind']
                 and o['length'] < port['length'] - 0.5 and _parallel(o['axis'], port['axis'])
                 and _same_line(port['at'], port['axis'], o['at'])
                 and abs(float((o['at'] - port['at']) @ port['axis'])) + o['length'] / 2 <= port['length'] / 2 + 1.0]
        if not inner:
            result.append(port)
    # Males and females of one part that already engage are internal to a shortcut assembly.
    internal = set()
    for i, male in enumerate(result):
        if not male['male']:
            continue
        for j, hole in enumerate(result):
            if hole['male'] or not _parallel(male['axis'], hole['axis']) or not _same_line(male['at'], male['axis'], hole['at']):
                continue
            gap = abs(float((hole['at'] - male['at']) @ male['axis']))
            if gap < (male['length'] + hole['length']) / 2 - 1.0:
                internal.update((i, j))
    result = [p for i, p in enumerate(result) if i not in internal]
    seen, unique = [], []
    for nozzle in nozzles:
        if not any(np.linalg.norm(nozzle['at'] - o['at']) < 0.5 and _parallel(nozzle['outward'], o['outward']) for o in seen):
            seen.append(nozzle)
            unique.append(nozzle)
    return result, unique


def _number(value):
    value = round(float(value), 3)
    return 0.0 if value == 0 else value


def _vector(values, digits=3):
    return [0.0 if round(float(v), digits) == 0 else round(float(v), digits) for v in values]


def _axis_sign(axis):
    """One direction per line: the first non-zero component is positive."""
    for value in axis:
        if abs(value) > 1e-6:
            return axis if value > 0 else -axis
    return axis


def name_ports(ports):
    """Stable IDs: holes ``hole-N``, pin grips ``grip-N``, axles ``shaft`` or ``shaft-N``.

    Each kind is numbered along the direction its centres spread most, then
    along the other two, so numbers rise from one end of the part to the other.
    """
    def order(rows):
        if len(rows) < 2:
            return rows
        centres = np.array([r['at'] for r in rows])
        spread = centres.max(axis=0) - centres.min(axis=0)
        axes = sorted(range(3), key=lambda i: (-round(float(spread[i]), 3), i))
        return sorted(rows, key=lambda r: tuple(round(float(r['at'][i]), 2) for i in axes))

    named = []
    holes = order([p for p in ports if not p['male']])
    grips = order([p for p in ports if p['male'] and p['kind'] == 'pin'])
    shafts = order([p for p in ports if p['male'] and p['kind'] == 'axle'])
    for index, port in enumerate(holes):
        named.append((f'hole-{index}', port))
    for index, port in enumerate(grips):
        named.append((f'grip-{index}', port))
    for index, port in enumerate(shafts):
        named.append(('shaft' if len(shafts) == 1 else f'shaft-{index}', port))
    return named


def entry(code, description, connections, bounds=None):
    """A registry entry for one part, or None when it has no ports or nozzles."""
    ports, nozzles = derive(connections)
    if not ports and not nozzles:
        return None
    friction = friction_for(code, description)
    rows = []
    for identity, port in name_ports(ports):
        row = dict(id=identity, kind=port['kind'], at=_vector(port['at']), axis=_vector(_axis_sign(port['axis']), 6),
                   length=_number(port['length']))
        if port['male']:
            row['friction'] = bool(friction and port['kind'] == 'pin')
            if port['stops']:
                # Stops are named in the port's own (normalised) axis direction.
                flipped = float(_axis_sign(port['axis']) @ port['axis']) < 0
                row['stops'] = sorted(('+' if s == '-' else '-') if flipped else s for s in port['stops'])
        rows.append(row)
    result = dict(description=clean_description(description), role=role_for(description), source='shadow',
                  features_sha256=fingerprint(connections), ports=rows)
    if bounds is not None:
        result['bounds'] = bounds
    if nozzles:
        ordered = sorted(nozzles, key=lambda n: tuple(round(float(v), 2) for v in n['at']))
        result['nozzles'] = [dict(id=f'nozzle-{i}', at=_vector(n['at']), outward=_vector(n['outward'], 6))
                             for i, n in enumerate(ordered)]
    return result
