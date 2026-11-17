"""Build-time checks a Technic builder would make by eye.

They run on every model that contains parts with Technic ports; no contract is
needed. They read the placed ports and part bodies only:

* a pin or axle that crosses a solid member where it has no hole
  (``technic.through_solid``), and two members in the same hole cells
  (``technic.cell_overlap``) — both errors;
* a pin grip that sticks out into the air (``technic.open_pin``);
* a turning axle that can slide out of its bearings (``technic.loose_axle``);
* a worm with nothing backing it against its thrust (``technic.thrust_unbacked``);
* the findings of the kinematic graph (``mechanism.diagnostics``).

A *cell* is the stud-wide block of plastic around one hole of a beam, Technic
brick or connector: 20 LDU across and as long as the hole. Each rule was run
on the official sets before it was enabled (``scripts/technic_corpus.py
checks``); a gear held at an axle end only by its cross hole is how LEGO builds
and is not reported.
"""
from __future__ import annotations

import re
from collections import defaultdict

import numpy as np

from .appearance import body
from .common import jsonable
from .mechanism import analyse, diagnostics as graph_diagnostics, gear_row, real, summary as graph_summary
from .technic import HOLES, MALE, Kind, definition, managed
from .placement import face_name


def heading(vector):
    """+X, -Z … or the rounded vector when the axis is oblique."""
    name = face_name(np.round(vector, 6))
    return name if name != 'oblique' else '[' + ', '.join(f'{v:.2f}' for v in vector) + ']'

SOLID = re.compile(r'^Technic (Beam|Liftarm|Brick|Cross Block|Axle and Pin Connector|Connector|Angle Connector|'
                   r'Pin Joiner|Axle Joiner|Frame)\b')
SKIN = re.compile(r'Panel|Fairing|Plate|Flex', re.I)
HALF = 10.0          # half the width of a cell across its hole
DEPTH = 4.0          # LDU two cells must share in every direction to count as one space
REACH = (1.5, 6.0, 11.0)   # LDU beyond an axle end at which a solid part stops it


def _vector(value):
    return np.array(jsonable(value), float)


def _unit(vector):
    return vector / np.linalg.norm(vector)


def ports_of(inspection):
    """World-space pins/axles of every occurrence, and the cells of solid members."""
    males, cells = [], []
    for item in inspection.occurrences:
        entry = definition(item.local)
        if entry is None:
            continue
        description = entry['description']
        solid = entry['role'] == 'member' and SOLID.match(description) and not SKIN.search(description)
        for feature in item.connections:
            if not managed(feature):
                continue
            row = dict(owner=item.index, port=feature.feature_id.removeprefix('technic:'), at=_vector(feature.position),
                       axis=_unit(_vector(feature.axis)), length=float(feature.length), kind=feature.kind,
                       role=entry['role'], hollow='Brick' in description)
            if feature.kind in MALE:
                males.append(row)
            elif feature.kind in HOLES and solid:
                cells.append(row)
    return males, cells


class Bodies:
    """Point tests against the stud-free vertex boxes of placed parts."""

    def __init__(self, inspection):
        self.rows = []
        for item in inspection.occurrences:
            shape = body(item)
            if shape is None or item.bounds is None:
                continue
            matrix = np.array(item.occurrence.matrix.rows, float)
            if not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6):
                continue
            holes = [(_vector(f.position), _unit(_vector(f.axis)), float(f.length))
                     for f in item.connections if managed(f) and f.kind in HOLES]
            self.rows.append((item.index, matrix, _vector(item.occurrence.position), shape[1], shape[2], holes,
                              any(managed(f) for f in item.connections)))
        boxes ={o.index: (_vector(o.bounds.min), _vector(o.bounds.max)) for o in inspection.occurrences if o.bounds}
        self.low = np.array([boxes[r[0]][0] for r in self.rows]) if self.rows else np.zeros((0, 3))
        self.high = np.array([boxes[r[0]][1] for r in self.rows]) if self.rows else np.zeros((0, 3))

    def hit(self, point, axis=None, exclude=(), *, holes_pass=True, unmanaged_only=False):
        """Index of a part whose body holds ``point``, or None.

        With ``holes_pass`` a part that has a hole coaxial with ``axis`` at the
        point does not count: a shaft can run into it.
        """
        if not len(self.rows):
            return None
        inside = np.flatnonzero(np.all((self.low - 0.5 <= point) & (point <= self.high + 0.5), axis=1))
        for k in inside:
            index, matrix, position, low, high, holes, has_ports = self.rows[k]
            if index in exclude or (unmanaged_only and has_ports):
                continue
            local = matrix.T @ (point - position)
            if np.any(local < low - 0.25) or np.any(local > high + 0.25):
                continue
            if holes_pass and axis is not None and any(
                    abs(float(h_axis @ axis)) > 0.9995
                    and np.linalg.norm((point - c) - ((point - c) @ h_axis) * h_axis) <= 1.0
                    and abs(float((point - c) @ h_axis)) <= length / 2 + 1 for c, h_axis, length in holes):
                continue
            return index
        return None


def solid_collisions(males, cells):
    """(through_solid, misaligned, cell_overlap) findings keyed by occurrence index pairs."""
    through, misaligned, overlap = {}, {}, {}
    if not cells:
        return through, misaligned, overlap
    at = np.array([c['at'] for c in cells])
    axis = np.array([c['axis'] for c in cells])
    half = np.array([c['length'] / 2 for c in cells])
    owner = np.array([c['owner'] for c in cells])
    for male in males:
        delta = at - male['at']
        reach = male['length'] / 2 + half + 2 * HALF
        close = np.flatnonzero((np.einsum('ij,ij->i', delta, delta) <= reach ** 2) & (owner != male['owner']))
        for index in close:
            d, w = -delta[index], axis[index]       # male centre in the cell's frame
            dot = float(male['axis'] @ w)
            along = float(d @ w)
            if abs(dot) > 0.9995:
                radial = float(np.linalg.norm(d - along * w))
                shared = male['length'] / 2 + half[index] - abs(along)
                # From 5 to 12 LDU off the shaft is in plastic; under 5 it rubs the bore and cannot pass.
                if 5 <= radial < 12 and shared > 2:
                    through[(male['owner'], int(owner[index]))] = dict(port=male['port'], hole=cells[index]['port'],
                                                                     off=round(radial, 2))
                elif 1.5 <= radial < 5 and shared > 2:
                    misaligned[(male['owner'], int(owner[index]))] = dict(port=male['port'], hole=cells[index]['port'],
                                                                        off=round(radial, 2))
            elif abs(dot) < 0.01 and not cells[index]['hollow']:
                # Studded bricks are hollow underneath; only studless members are solid across a hole.
                m = male['axis']
                across = float(d @ np.cross(w, m))
                span = male['length'] / 2 + (HALF - 2) - abs(float(d @ m))
                if abs(along) < half[index] - 2 and abs(across) < HALF - 2 and span > 2:
                    through[(male['owner'], int(owner[index]))] = dict(port=male['port'], hole=cells[index]['port'],
                                                                     off=round(abs(across), 2))
    order = np.argsort(at[:, 0])
    sorted_x = at[order, 0]
    for position, i in enumerate(order):
        end = np.searchsorted(sorted_x, sorted_x[position] + 2 * HALF + 1, side='right')
        for j in order[position + 1:end]:
            if owner[i] == owner[j]:
                continue
            d = at[j] - at[i]
            if np.abs(d).max() > 2 * HALF:
                continue
            dot = float(axis[i] @ axis[j])
            if abs(dot) > 0.9995:
                along = float(d @ axis[i])
                radial = float(np.linalg.norm(d - along * axis[i]))
                if half[i] + half[j] - abs(along) > DEPTH and radial < 2 * HALF - DEPTH - 1:
                    overlap[tuple(sorted((int(owner[i]), int(owner[j]))))] = (cells[i]['port'], cells[j]['port'])
            elif abs(dot) < 0.01:
                n = np.cross(axis[i], axis[j])
                shared = (half[i] + HALF - abs(float(d @ axis[i])), HALF + half[j] - abs(float(d @ axis[j])),
                          2 * HALF - abs(float(d @ n)))
                if min(shared) > DEPTH:
                    overlap[tuple(sorted((int(owner[i]), int(owner[j]))))] = (cells[i]['port'], cells[j]['port'])
    return through, misaligned, overlap


def axial(graph, inspection, bodies):
    """Pins sticking into the air, axles that can slide out, worms with nothing behind them."""
    rows = []
    items = graph['items']
    by_male = defaultdict(list)
    for contact in graph['contacts']:
        by_male[contact['male'], contact['male_port']].append(contact)
    open_pins = []
    for item in inspection.occurrences:
        entry = graph['entries'].get(item.index)
        if entry is None:
            continue
        listed = {p['id']: p for p in entry['ports']}
        for feature in item.connections:
            if not managed(feature) or feature.kind not in MALE:
                continue
            port = feature.feature_id.removeprefix('technic:')
            contacts = by_male.get((item.index, port), [])
            centre, axis, half = _vector(feature.position), _unit(_vector(feature.axis)), float(feature.length) / 2
            if feature.kind is Kind.PIN:
                if contacts or entry['role'] != 'connector':
                    continue
                # Only a grip in the air is open; one inside any other part sits in a hole we cannot read.
                samples = [centre + axis * t for t in np.linspace(-half + 3, half - 3, 3)]
                if all(bodies.hit(p, exclude={item.index}, holes_pass=False) is None for p in samples):
                    open_pins.append(item.index)
                continue
            if entry['role'] != 'shaft':
                continue
            bearings = [c for c in contacts if c['kind'] == 'bearing']
            keyed = [c for c in contacts if c['kind'] == 'keyed']
            stops = set(listed.get(port, {}).get('stops', []))
            engaged = {item.index, *(real(c['hole']) for c in contacts)}
            if bearings:
                low = min(b['interval'][0] for b in bearings)
                high = max(b['interval'][1] for b in bearings)

                def held(sign):
                    """Something stops the axle moving toward ``sign`` * axis."""
                    if sign > 0:
                        if '-' in stops or any(k['interval'][1] <= b['interval'][0] + 1 for k in keyed for b in bearings):
                            return True
                        span = np.arange(-half + 2, low - 1, 5.0)
                    else:
                        if '+' in stops or any(k['interval'][0] >= b['interval'][1] - 1 for k in keyed for b in bearings):
                            return True
                        span = np.arange(high + 1, half - 2 + 1e-9, 5.0)
                    # A part without readable ports mounted on the free length (a hub, a pulley) is a stop too.
                    if any(bodies.hit(centre + axis * t, axis, engaged, holes_pass=False, unmanaged_only=True) is not None
                           for t in span):
                        return True
                    tip = centre + axis * half * sign
                    return any(bodies.hit(tip + axis * r * sign, axis, engaged) is not None for r in REACH)

                free = [heading(d) for d, sign in ((axis, 1), (-axis, -1)) if not held(sign)]
                if free:
                    rows.append(dict(code='technic.loose_axle', severity='warning', instances=[item.index],
                                     message='This axle can slide out toward ' + ' and '.join(free)
                                             + ': put a bush or another part keyed to it against its bearing, or use an '
                                               'axle with a stop.', free=free))
            by_part = defaultdict(list)
            for contact in keyed:
                by_part[contact['hole']].append(contact)
            for part, mine in by_part.items():
                if part < 0:
                    continue
                gear = gear_row(items[part].occurrence.part_code)
                if not gear or gear['type'] != 'worm':
                    continue
                low = min(c['interval'][0] for c in mine)
                high = max(c['interval'][1] for c in mine)
                others = [c for c in contacts if c['hole'] != part]

                def backed(end, sign):
                    if any(abs((c['interval'][1] if sign < 0 else c['interval'][0]) - end) <= 1 for c in others):
                        return True
                    if (sign < 0 and '-' in stops and end <= -half + 3) or (sign > 0 and '+' in stops and end >= half - 3):
                        return True
                    return bodies.hit(centre + axis * (end + 1.5 * sign), axis, {item.index, part},
                                      holes_pass=False) is not None

                side = [heading(d) for d, end, sign in ((-axis, low, -1), (axis, high, 1))
                        if not backed(end, sign)]
                if side:
                    rows.append(dict(code='technic.thrust_unbacked', severity='warning', instances=[part],
                                     message='A worm pushes along its axle when it drives; nothing backs this one toward '
                                             + ' and '.join(side) + '. Seat a bush or a beam flush against it (next_to).',
                                     free=side))
    if open_pins:
        rows.append(dict(code='technic.open_pin', severity='warning', instances=sorted(set(open_pins)),
                         count=len(set(open_pins)),
                         message=f'{len(set(open_pins))} pin(s) stick out into the air on one side: the pin holds nothing '
                                 'there. Seat a part on it or remove it.'))
    return rows


def review(inspection, found):
    """Diagnostics and a summary for the Technic content of an inspected model."""
    males, cells = ports_of(inspection)
    if not males and not cells:
        return [], None
    rows = []
    through, misaligned, overlap = solid_collisions(males, cells)
    for (male, member), detail in sorted(through.items()):
        rows.append(dict(code='technic.through_solid', severity='error', instances=[male, member],
                         message=f"{detail['port']} passes through solid plastic, {detail['off']:g} LDU off {detail['hole']}: "
                                 'a pin or axle must run in a hole. Move it onto the hole, or move the part.', **detail))
    for (male, member), detail in sorted(misaligned.items()):
        rows.append(dict(code='technic.misaligned', severity='warning', instances=[male, member],
                         message=f"{detail['port']} runs {detail['off']:g} LDU off the centre of {detail['hole']}, so it cannot "
                                 'pass through the hole. Place it with on: {to, hole, pin} so it is centred.', **detail))
    for pair, ports in sorted(overlap.items()):
        rows.append(dict(code='technic.cell_overlap', severity='error', instances=list(pair),
                         message=f'These two parts occupy the same space at {ports[0]} and {ports[1]}. '
                                 'Lay one beside the other (join ... side) or move it a whole stud.'))
    graph = analyse(inspection, found)
    rows.extend(axial(graph, inspection, Bodies(inspection)))
    rows.extend(graph_diagnostics(graph))
    seated = {(c['male'], c['male_port']) for c in graph['contacts']}
    result = dict(graph_summary(graph), pins_and_axles=len(males), seated=sum((m['owner'], m['port']) in seated for m in males),
                  problems=sorted({r['code'] for r in rows}),
                  mesh_pairs=[(real(m['a']), real(m['b'])) for m in graph['meshes']])
    return rows, result
