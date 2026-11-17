"""The kinematic graph of a built Technic pose, and what it says about the build.

Nothing here moves a model. From the placed parts and their seated ports it
derives the things a mechanical engineer reads off a drawing:

* **rigid groups**: parts bonded by studs, friction pins and keyed axle fits;
* **joints** between groups: a frictionless pin or an axle in a round hole
  turns about its axis; a shock absorber, pneumatic cylinder or linear
  actuator slides along the line between its end eyes;
* **couplings**: gear pairs at their exact centre distance, bevels and worms in
  the arrangements the official sets use, pinions on a rack's pitch line.

``analyse`` builds the graph, ``diagnostics`` reports the defects that follow
from it (a gear short of meshing, a geared shaft keyed to the frame, a mesh
whose two shafts no common frame carries), and ``mobility`` answers a declared
intent: with this part as input, can it move, and does that output move with
it? Mobility is the rank of the joint constraints at the built pose. It is
instantaneous, ignores play and can mislead at a singular pose.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from functools import lru_cache
from itertools import combinations

import numpy as np

from .common import DATA, jsonable
from .technic import MALE, Kind, canonical, definition, endpoints, fit, managed

MESH_TOLERANCE = 0.6       # LDU off the exact centre distance that still meshes
NEAR = 6.0                 # LDU within which two gears were plainly meant to mesh
OVERHANG = 40.0            # LDU from a gear to its nearest bearing (92% of official gears are within it)
SPAN = 160.0               # LDU between the bearings either side of a gear (95% of official gears are within it)
MOTORS = ('58121', '58120', '99499', '43362', '87577', '95658', '22169', '22172', '54696', '54799', '45303', '21980')


@lru_cache(maxsize=1)
def gear_table():
    path = DATA / 'technic-gears.json'
    return json.loads(path.read_text()) if path.exists() else dict(gears={}, perpendicular=[], worm=[])


def gear_row(code):
    gears = gear_table()['gears']
    key = code.casefold().removesuffix('.dat')
    return gears.get(key) or gears.get(canonical(key))


def _vector(value):
    return np.array(jsonable(value), float)


def _unit(vector):
    return vector / np.linalg.norm(vector)


def _same_line(point, axis, other_point, other_axis, tolerance=0.5):
    if abs(float(axis @ other_axis)) < 0.9995:
        return False
    delta = other_point - point
    return float(np.linalg.norm(delta - (delta @ axis) * axis)) <= tolerance


TELESCOPE = re.compile(r'Shock Absorber|Linear Actuator|Pneumatic Cylinder|Actuator', re.I)


def motor(entry):
    return bool(entry) and entry['description'].startswith('Electric') and 'Motor' in entry['description']


def real(index):
    """The occurrence a body belongs to: a telescoping part's rod end is numbered -(index + 1)."""
    return index if index >= 0 else -index - 1


def telescoping(items, entries):
    """Shock absorbers, cylinders and actuators: the end ports farthest apart split into two bodies.

    Returns {occurrence index: dict(virtual, rod_ports, axis, point)}; the rod
    end becomes body ``virtual`` and slides along ``axis`` against the barrel.
    """
    result = {}
    for index, item in items.items():
        entry = entries.get(index)
        if entry is None or not TELESCOPE.search(entry['description']):
            continue
        ports = [p for p in entry['ports'] if p['kind'] in ('pin', 'axle', 'pin_hole', 'axle_hole')]
        if len(ports) < 2:
            continue
        points = [np.array(p['at'], float) for p in ports]
        first, last = max(combinations(range(len(points)), 2),
                          key=lambda pair: float(np.linalg.norm(points[pair[0]] - points[pair[1]])))
        line = points[last] - points[first]
        if np.linalg.norm(line) < 20:
            continue
        line = line / np.linalg.norm(line)
        middle = (points[first] + points[last]) / 2
        rotation = np.array(item.occurrence.matrix.rows, float)
        result[index] = dict(virtual=-index - 1, axis=_unit(rotation @ line),
                             point=rotation @ middle + _vector(item.occurrence.position),
                             rod_ports={p['id'] for p, q in zip(ports, points) if float((q - middle) @ line) > 0})
    return result


class Groups:
    def __init__(self, members):
        self.parent = {m: m for m in members}

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[max(a, b)] = min(a, b)
            return True
        return False


def analyse(inspection, found, *, ground=None):
    """Rigid groups, joints, gears and meshes of an inspected model.

    ``found`` are its connection contacts. ``ground`` optionally names the
    occurrence index whose group is the frame; otherwise it is the group that
    carries the most joints, then the one with the most structural members.
    """
    items = {o.index: o for o in inspection.occurrences}
    entries = {i: definition(o.local) for i, o in items.items()}
    roles = {i: (e['role'] if e else None) for i, e in entries.items()}
    telescopes = telescoping(items, entries)
    for index, telescope in telescopes.items():
        roles[telescope['virtual']] = roles[index]
    groups = Groups([*items, *(t['virtual'] for t in telescopes.values())])

    def end(index, port):
        """The body a port belongs to: a telescoping part's rod end is a body of its own."""
        telescope = telescopes.get(index)
        return telescope['virtual'] if telescope and port in telescope['rod_ports'] else index

    contacts, hinges = [], []
    for contact in found:
        first, second = contact.first_occurrence.index, contact.second_occurrence.index
        if first not in items or second not in items:
            continue
        if managed(contact.first) and managed(contact.second):
            male, male_port, hole, hole_port = endpoints(contact)
            details = fit(male_port, hole_port)
            if details is None:
                continue
            if male_port.kind is Kind.AXLE:
                kind = 'keyed' if hole_port.kind is Kind.AXLE_HOLE else 'bearing'
                # A motor's output turns against its case: the shaft it drives is a body of its own.
                if kind == 'keyed' and (motor(entries.get(hole.index)) or motor(entries.get(male.index))):
                    kind = 'bearing'
            else:
                kind = 'friction' if details['friction'] else 'pivot'
            male_id, hole_id = male_port.feature_id.removeprefix('technic:'), hole_port.feature_id.removeprefix('technic:')
            male_index, hole_index = end(male.index, male_id), end(hole.index, hole_id)
            axis, origin = _unit(_vector(male_port.axis)), _vector(male_port.position)
            # The joint lies on the pin or axle's own line: holes seated within tolerance of it
            # must not give one pin two slightly different axes.
            hole_at = _vector(hole_port.position)
            point = origin + axis * float((hole_at - origin) @ axis)
            contacts.append(dict(male=male_index, hole=hole_index, male_port=male_id, hole_port=hole_id, kind=kind,
                                 interval=details['interval'], axis=axis, origin=origin, point=point,
                                 male_length=float(male_port.length), hole_length=float(hole_port.length)))
            if kind in ('keyed', 'friction'):
                groups.union(male_index, hole_index)
            continue
        kinds = {contact.first.kind.value, contact.second.kind.value}
        if kinds & {'clip', 'bar', 'hinge'}:
            hinges.append(dict(a=first, b=second, point=_vector(contact.first.position), axis=_unit(_vector(contact.first.axis))))
        else:
            groups.union(first, second)
    turning = [c for c in contacts if c['kind'] in ('pivot', 'bearing')]

    def joints_now():
        rows = []
        for c in turning:
            a, b = groups.find(c['male']), groups.find(c['hole'])
            if a != b:
                rows.append(dict(a=a, b=b, point=c['point'], axis=c['axis'], via=c['male'], kind=c['kind']))
        for h in hinges:
            a, b = groups.find(h['a']), groups.find(h['b'])
            if a != b:
                rows.append(dict(a=a, b=b, point=h['point'], axis=h['axis'], via=None, kind='hinge'))
        for index, telescope in telescopes.items():
            a, b = groups.find(index), groups.find(telescope['virtual'])
            if a != b:
                rows.append(dict(a=a, b=b, point=telescope['point'], axis=telescope['axis'], via=None, kind='prismatic'))
        return rows

    bodies = [*items, *(t['virtual'] for t in telescopes.values())]
    loose_pairs = set()
    for _ in range(8):
        joints = joints_now()
        members = defaultdict(list)
        for index in bodies:
            members[groups.find(index)].append(index)
        # Two groups that turn about one pin still turn; about two different lines they are rigid.
        lines = defaultdict(list)
        by_group = defaultdict(list)
        for joint in joints:
            if joint['kind'] == 'prismatic':
                continue
            lines[tuple(sorted((joint['a'], joint['b'])))].append(joint)
            by_group[joint['a']].append(joint)
            by_group[joint['b']].append(joint)
        for group, parts in members.items():
            if not all(roles[i] == 'connector' for i in parts):
                continue
            for one, two in combinations(by_group[group], 2):
                if not _same_line(one['point'], one['axis'], two['point'], two['axis']):
                    continue
                ends = [j['b'] if j['a'] == group else j['a'] for j in (one, two)]
                if ends[0] != ends[1]:
                    lines[tuple(sorted(ends))].append(dict(one, a=ends[0], b=ends[1], via=one['via']))
        changed = False
        for (a, b), rows in lines.items():
            distinct = []
            for row in rows:
                if not any(_same_line(row['point'], row['axis'], d['point'], d['axis']) for d in distinct):
                    distinct.append(row)
            if len(distinct) >= 2:
                loose_pairs.add((a, b))
                changed |= groups.union(a, b)
                for row in rows:
                    if row.get('via') is not None:
                        changed |= groups.union(a, row['via'])
        if not changed:
            break
    joints = joints_now()
    members = defaultdict(list)
    for index in sorted(bodies, key=real):
        members[groups.find(index)].append(index)
    if ground is not None and ground in items:
        frame = groups.find(ground)
    else:
        # The frame is what carries the shafts and pivots: the group whose holes the most pins and axles
        # turn in, then the one with the most joints, then the most structural members. Counting members
        # first let a crank built from bricks outrank the beams; a shaft is never the hole side.
        bearings, carried = defaultdict(int), defaultdict(int)
        for joint in joints:
            carried[joint['a']] += 1
            carried[joint['b']] += 1
            if joint['kind'] in ('pivot', 'bearing'):
                bearings[joint['b']] += 1
        frame = max(members, key=lambda g: (bearings[g], carried[g], sum(roles[i] == 'member' for i in members[g]),
                                            len(members[g]), -g)) if members else None
    gears, racks = [], []
    for index, item in items.items():
        row = gear_row(item.occurrence.part_code)
        # A gear placed by a mirrored or rounded matrix carries no ports, so nothing can be said about it.
        if not row or (row['type'] != 'rack' and not any(managed(f) for f in item.connections)):
            continue
        rotation = np.array(item.occurrence.matrix.rows, float)
        position = _vector(item.occurrence.position)
        if abs(np.linalg.det(rotation) - 1) > 1e-3:
            continue
        if row['type'] == 'rack':
            if 'pitch' in row and abs(row['pitch']) <= 20:
                racks.append(dict(index=index, row=row, rotation=rotation, position=position, group=groups.find(index)))
        else:
            gears.append(dict(index=index, row=row, centre=position + rotation @ np.array(row['centre']),
                              axis=_unit(rotation @ np.array(row['axis'])), group=groups.find(index)))
    meshes, near = _meshes(gears, racks)
    return dict(items=items, roles=roles, entries=entries, groups=groups, members=dict(members), frame=frame,
                contacts=contacts, joints=joints, gears=gears, racks=racks, meshes=meshes, near=near)


def _meshes(gears, racks):
    table = gear_table()
    meshes, near = [], []
    for a, b in combinations(gears, 2):
        ra, rb = a['row'], b['row']
        delta = b['centre'] - a['centre']
        if np.linalg.norm(delta) > ra['radius'] + rb['radius'] + 60:
            continue
        dot = abs(float(a['axis'] @ b['axis']))
        worm = 'worm' in (ra['type'], rb['type'])
        if dot > 0.9995 and not worm:
            if 'bevel' in (ra['type'], rb['type']) or 'knob' in (ra['type'], rb['type']):
                continue
            axial = abs(float(delta @ a['axis']))
            if axial > (ra['width'] + rb['width']) / 2 - 1:
                continue
            distance = float(np.linalg.norm(delta - (delta @ a['axis']) * a['axis']))
            off = distance - ra['radius'] - rb['radius']
            record = dict(a=a['index'], b=b['index'], kind='parallel', distance=round(distance, 3),
                          needs=ra['radius'] + rb['radius'], off=round(off, 3))
            if abs(off) <= MESH_TOLERANCE:
                meshes.append(dict(record, ratio=[ra['teeth'], rb['teeth']]))
            elif -NEAR <= off <= NEAR:
                near.append(record)
        elif dot < 0.0005:
            normal = _unit(np.cross(a['axis'], b['axis']))
            skew = abs(float(delta @ normal))
            off_a, off_b = abs(float(delta @ a['axis'])), abs(float(delta @ b['axis']))
            if worm:
                if ra['type'] == rb['type']:
                    continue
                screw, wheel, off_screw, off_wheel = (a, b, off_a, off_b) if ra['type'] == 'worm' else (b, a, off_b, off_a)
                if wheel['row']['type'] in ('bevel', 'knob'):
                    continue
                needs = screw['row']['radius'] + wheel['row']['radius']
                record = dict(a=screw['index'], b=wheel['index'], kind='worm', distance=round(skew, 3), needs=needs,
                              off=round(skew - needs, 3))
                inside = off_screw <= screw['row']['width'] / 2 + 1 and off_wheel <= wheel['row']['width'] / 2
                if inside and abs(skew - needs) <= MESH_TOLERANCE:
                    meshes.append(dict(record, ratio=[1, wheel['row']['teeth']]))
                elif off_screw <= screw['row']['width'] / 2 + 10 and off_wheel <= 12 and abs(skew - needs) <= NEAR:
                    near.append(record)
                continue
            if skew > NEAR:
                continue
            first, second = sorted([(ra['type'], ra.get('teeth', 0)), (rb['type'], rb.get('teeth', 0))])
            if (ra['type'], ra.get('teeth', 0)) != first:
                off_a, off_b = off_b, off_a
            known = [r for r in table['perpendicular'] if tuple(r['a']) == first and tuple(r['b']) == second]
            if first == second:
                known += [dict(r, offset_a=r['offset_b'], offset_b=r['offset_a']) for r in known]
            if not known:
                # A pair the official sets never use: each gear stands about the other's pitch radius
                # from where the axes cross.
                bevels = {'bevel', 'double_bevel', 'crown'}
                if {ra['type'], rb['type']} <= bevels and skew <= 1.0 and \
                        abs(off_a - (rb['radius'] if (ra['type'], ra.get('teeth', 0)) == first else ra['radius'])) <= 5 and \
                        abs(off_b - (ra['radius'] if (ra['type'], ra.get('teeth', 0)) == first else rb['radius'])) <= 5:
                    meshes.append(dict(a=a['index'], b=b['index'], kind='perpendicular', off=0.0, ratio=[ra['teeth'], rb['teeth']],
                                       offsets=[round(off_a, 2), round(off_b, 2)], needs='pitch rule'))
                continue
            best = min(known, key=lambda r: abs(off_a - r['offset_a']) + abs(off_b - r['offset_b']))
            miss = max(abs(off_a - best['offset_a']), abs(off_b - best['offset_b']), skew)
            record = dict(a=a['index'], b=b['index'], kind='perpendicular', off=round(miss, 3),
                          offsets=[round(off_a, 2), round(off_b, 2)], needs=[best['offset_a'], best['offset_b']])
            if miss <= 1.0:
                meshes.append(dict(record, ratio=[ra['teeth'], rb['teeth']]))
            elif miss <= NEAR:
                near.append(record)
    for rack in racks:
        row = rack['row']
        axes = dict(x=0, y=1, z=2)
        spin, normal = axes[row['pinion_axis']], axes[row['normal']]
        length = [k for k in range(3) if k not in (spin, normal)][0]
        low, high = np.array(row['bounds']['min']), np.array(row['bounds']['max'])
        for gear in gears:
            g = gear['row']
            if g['type'] in ('worm', 'bevel', 'knob') or abs(float((rack['rotation'].T @ gear['axis'])[spin])) < 0.9995:
                continue
            local = rack['rotation'].T @ (gear['centre'] - rack['position'])
            if not (low[length] - 5 <= local[length] <= high[length] + 5):
                continue
            if abs(local[spin] - (low[spin] + high[spin]) / 2) > (high[spin] - low[spin] + g['width']) / 2:
                continue
            needs = row['pitch'] + row['side'] * g['radius']
            off = (local[normal] - needs) * row['side']
            record = dict(a=gear['index'], b=rack['index'], kind='rack', distance=round(float(local[normal]), 3),
                          needs=round(needs, 3), off=round(float(off), 3))
            if abs(off) <= MESH_TOLERANCE:
                meshes.append(dict(record, ratio=[g['teeth'], 0]))
            elif abs(off) <= NEAR:
                near.append(record)
    return meshes, near


def diagnostics(graph):
    """Defects that follow from the graph alone."""
    rows = []

    def issue(code, message, instances, severity='warning', **extra):
        rows.append(dict(code=code, severity=severity, message=message, instances=list(instances), **extra))

    groups, frame, roles = graph['groups'], graph['frame'], graph['roles']
    for record in graph['near']:
        if record['kind'] == 'perpendicular':
            issue('technic.gear_gap', f"These gears stand at {record['offsets']} LDU from where their axes cross; "
                  f"they mesh at {record['needs']}.", [record['a'], record['b']], off=record['off'])
        elif record['kind'] == 'rack':
            code = 'technic.gear_clash' if record['off'] < 0 else 'technic.gear_gap'
            issue(code, f"This pinion stands {abs(record['off']):g} LDU {'into' if record['off'] < 0 else 'off'} the rack's "
                  f"pitch line: its axis is {abs(record['distance']):g} LDU from the rack origin and meshes at "
                  f"{abs(record['needs']):g}.", [record['a'], record['b']], off=record['off'])
        elif record['off'] < 0:
            issue('technic.gear_clash', f"These gears are {-record['off']:g} LDU too close: their axes are "
                  f"{record['distance']:g} LDU apart and mesh at {record['needs']:g}.", [record['a'], record['b']],
                  off=record['off'])
        else:
            issue('technic.gear_gap', f"These gears are {record['off']:g} LDU short of meshing: their axes are "
                  f"{record['distance']:g} LDU apart and mesh at {record['needs']:g}.", [record['a'], record['b']],
                  off=record['off'])
    by_group = defaultdict(list)
    for joint in graph['joints']:
        by_group[joint['a']].append(joint)
        by_group[joint['b']].append(joint)
    frame_members = sum(roles[i] == 'member' for i in graph['members'].get(frame, []))
    geared = defaultdict(list)
    for gear in graph['gears']:
        geared[gear['group']].append(gear)
    meshed = {i for m in graph['meshes'] for i in (m['a'], m['b'])}
    for group, gears in geared.items():
        indices = [g['index'] for g in gears]
        if group == frame and frame_members >= 2:
            # Only gears that are meant to turn matter: ones in a mesh.
            turning = [i for i in indices if i in meshed]
            if turning:
                issue('technic.locked_shaft', 'These gears mesh but cannot turn: their shaft is fixed to the frame by a '
                      'cross hole or friction pin. Carry the shaft in round holes.', turning)
            continue
        if not by_group[group]:
            if any(i in meshed for i in indices):
                issue('technic.unsupported_shaft', 'This geared shaft runs in no bearing: pass its axle through a round '
                      'hole of the frame.', indices)
            continue
        for gear in gears:
            if gear['index'] not in meshed:
                continue
            along = [float((j['point'] - gear['centre']) @ gear['axis']) for j in by_group[group]
                     if _same_line(gear['centre'], gear['axis'], j['point'], j['axis'])]
            if not along:
                continue
            below, above = [-a for a in along if a < 0], [a for a in along if a >= 0]
            if below and above:
                # Carried between bearings: a span up to 160 LDU covers 95% of official gears.
                span = min(below) + min(above)
                if span > SPAN + 0.5:
                    issue('technic.overhung_gear', f"This gear sits in a {span:g} LDU span between bearings; keep it "
                          f"under {SPAN:g} LDU (eight studs) or add a bearing nearer the gear.", [gear['index']])
            elif min(abs(a) for a in along) > OVERHANG + 0.5:
                issue('technic.overhung_gear', f"This gear overhangs its bearing by {min(abs(a) for a in along):g} LDU; "
                      f"keep a gear supported on one side within {OVERHANG:g} LDU (two studs) of its bearing.",
                      [gear['index']])
    for mesh in graph['meshes']:
        a, b = groups.find(mesh['a']), groups.find(mesh['b'])
        if a == b:
            issue('technic.locked_shaft', 'These two meshing gears belong to one rigid group, so neither can turn.',
                  [mesh['a'], mesh['b']])
            continue
        carriers = [{j['b'] if j['a'] == g else j['a'] for j in by_group[g]} for g in (a, b)]
        if mesh['kind'] == 'rack':
            continue
        if carriers[0] and carriers[1] and not carriers[0] & carriers[1]:
            issue('technic.unbraced_mesh', 'The two shafts of this mesh run in different rigid groups, so load can push '
                  'the gears apart. Carry both shafts in one beam or frame.', [mesh['a'], mesh['b']])
    return rows


def summary(graph):
    """Counts for the build summary."""
    return dict(rigid_groups=len(graph['members']), joints=len(graph['joints']), gears=len(graph['gears']),
                meshes=len(graph['meshes']), frame_parts=len(graph['members'].get(graph['frame'], [])))


def mobility(graph, *, inputs, outputs=()):
    """Instantaneous mobility of the built pose with the frame held still.

    ``inputs`` and ``outputs`` are occurrence indices. Returns degrees of
    freedom, whether each input can move, and which outputs move with it.
    """
    groups, frame = graph['groups'], graph['frame']
    bodies = [g for g in graph['members'] if g != frame]
    column = {g: 6 * n for n, g in enumerate(bodies)}
    size = 6 * len(bodies)
    rows = []

    def angular(group, vector, row, scale=1.0):
        if group in column:
            row[column[group]:column[group] + 3] += scale * vector

    def linear(group, point, direction, row, scale=1.0):
        # Velocity of the group's point along a direction: v . d + (w x p) . d = v . d + w . (p x d)
        if group in column:
            row[column[group]:column[group] + 3] += scale * np.cross(point, direction)
            row[column[group] + 3:column[group] + 6] += scale * direction

    for joint in graph['joints']:
        axis = joint['axis']
        helper = np.array([1.0, 0, 0]) if abs(axis[0]) < 0.9 else np.array([0, 1.0, 0])
        u = _unit(np.cross(axis, helper))
        v = np.cross(axis, u)
        sliding = joint['kind'] == 'prismatic'
        # A revolute joint keeps both bodies on its axis and lets them turn about it;
        # a prismatic one keeps them from turning and lets them slide along it.
        for direction in ((u, v, axis) if sliding else (u, v)):
            row = np.zeros(size)
            angular(joint['a'], direction, row)
            angular(joint['b'], direction, row, -1.0)
            rows.append(row)
        for direction in ((u, v) if sliding else (u, v, axis)):
            row = np.zeros(size)
            linear(joint['a'], joint['point'], direction, row)
            linear(joint['b'], joint['point'], direction, row, -1.0)
            rows.append(row)
    by_group = defaultdict(set)
    for joint in graph['joints']:
        by_group[joint['a']].add(joint['b'])
        by_group[joint['b']].add(joint['a'])
    gears = {g['index']: g for g in graph['gears']}
    racks = {r['index']: r for r in graph['racks']}
    for mesh in graph['meshes']:
        a = gears[mesh['a']]
        group_a = groups.find(mesh['a'])
        group_b = groups.find(mesh['b'])
        if group_a == group_b:
            continue
        shared = by_group[group_a] & by_group[group_b]
        carrier = frame if frame in shared or not shared else min(shared)
        row = np.zeros(size)
        if mesh['kind'] == 'rack':
            rack = racks[mesh['b']]
            axes = dict(x=0, y=1, z=2)
            spin, normal = axes[rack['row']['pinion_axis']], axes[rack['row']['normal']]
            length = [k for k in range(3) if k not in (spin, normal)][0]
            travel = rack['rotation'][:, length]
            angular(group_a, a['axis'], row, a['row']['radius'])
            angular(carrier, a['axis'], row, -a['row']['radius'])
            linear(group_b, rack['position'], travel, row)
            linear(carrier, rack['position'], travel, row, -1.0)
        else:
            b = gears[mesh['b']]
            teeth_a = a['row'].get('teeth') or 1
            teeth_b = b['row'].get('teeth') or 1
            sign = -1.0 if float(a['axis'] @ b['axis']) < -0.5 else 1.0
            angular(group_a, a['axis'], row, teeth_a)
            angular(carrier, a['axis'], row, -teeth_a)
            angular(group_b, b['axis'], row, sign * teeth_b)
            angular(carrier, b['axis'], row, -sign * teeth_b)
        rows.append(row)
    if size == 0:
        return dict(degrees_of_freedom=0, bodies=0, inputs={i: False for i in inputs}, outputs={o: False for o in outputs},
                    moving=[], independent={})
    matrix = np.array(rows) if rows else np.zeros((1, size))
    _, values, vt = np.linalg.svd(matrix, full_matrices=True)
    scale = values.max() if len(values) and values.max() > 0 else 1.0
    rank = int(np.sum(values > 1e-8 * scale))
    null = vt[rank:].T                      # columns span the free motions

    def moves(group, space=null):
        if group not in column or space.shape[1] == 0:
            return False
        return bool(np.abs(space[column[group]:column[group] + 6]).max() > 1e-7)

    connector_only = {g for g in bodies if all(graph['roles'][i] == 'connector' for i in graph['members'][g])}
    working = [g for g in bodies if g not in connector_only]
    effective = 0
    if null.shape[1] and working:
        picked = np.vstack([null[column[g]:column[g] + 6] for g in working])
        values = np.linalg.svd(picked, compute_uv=False)
        effective = int(np.sum(values > 1e-6 * max(values.max(), 1e-12)))
    result = dict(degrees_of_freedom=effective, raw_degrees_of_freedom=int(null.shape[1]), bodies=len(bodies),
                  inputs={}, outputs={}, independent={}, moving=[])
    input_groups = [groups.find(i) for i in inputs]
    for index, group in zip(inputs, input_groups):
        result['inputs'][index] = moves(group)
    # Motions that leave every input still: an output that moves in them is not tied to the input.
    still = null
    if null.shape[1] and input_groups:
        held = np.vstack([null[column[g]:column[g] + 6] for g in input_groups if g in column] or [np.zeros((1, null.shape[1]))])
        _, held_values, held_vt = np.linalg.svd(held, full_matrices=True)
        held_rank = int(np.sum(held_values > 1e-7))
        still = null @ held_vt[held_rank:].T
        driven = null @ held_vt[:held_rank].T
    else:
        driven = np.zeros((size, 0))
    for index in outputs:
        group = groups.find(index)
        result['outputs'][index] = moves(group, driven)
        result['independent'][index] = moves(group, still)
    result['moving'] = sorted(i for g in bodies if g not in connector_only and moves(g, driven) for i in graph['members'][g])
    return result


def label(names, index):
    """A placement path for a body; a telescoping part's rod end is named after its part."""
    if index < 0:
        return names.get(real(index), f'#{real(index)}') + ' (rod end)'
    return names.get(index, f'#{index}')


def describe(graph, names=None):
    """A readable account of the graph for ``technic trace``."""
    names = names or {}

    def name(index):
        return label(names, index)

    groups, frame = graph['groups'], graph['frame']
    by_group = defaultdict(list)
    for joint in graph['joints']:
        by_group[joint['a']].append(joint)
        by_group[joint['b']].append(joint)
    gears = defaultdict(list)
    for gear in graph['gears']:
        gears[gear['group']].append(gear)
    rotors = []
    for group, parts in sorted(graph['members'].items()):
        if group == frame or all(graph['roles'][i] == 'connector' for i in parts):
            continue
        rotors.append(dict(parts=[name(i) for i in parts[:8]] + (['…'] if len(parts) > 8 else []),
                           turns_in=sorted({name(j['via']) if j['via'] is not None else j['kind'] for j in by_group[group]})[:6],
                           joints=len(by_group[group]),
                           gears=[f"{name(g['index'])} ({g['row'].get('teeth', '')}t {g['row']['type']})" for g in gears[group]]))
    meshes = []
    for mesh in graph['meshes']:
        teeth = mesh['ratio']
        ratio = f"{teeth[0]}:{teeth[1]}" if teeth[1] else f"{teeth[0]}t on rack"
        meshes.append(f"{name(mesh['a'])} - {name(mesh['b'])}: {mesh['kind']}, {ratio}")
    return dict(frame=dict(parts=len(graph['members'].get(frame, [])), gears=[name(g['index']) for g in gears.get(frame, [])]),
                moving_groups=rotors, meshes=meshes,
                near_misses=[f"{name(n['a'])} - {name(n['b'])}: {n['kind']}, off by {n['off']:g} LDU" for n in graph['near']],
                note='Static reading of the built pose: rigid groups, turning joints and gear couplings. No motion is simulated.')


def review(model, parts, contract, source_map, *, instance_limit=100000):
    """Check a section's declared mechanism against the built pose."""
    from .connectivity import inspect_connections
    from .connection_adapter import connection_contacts
    table = {row['path']: row['index'] for row in source_map if row['authored']}
    names = {row['index']: row['path'] for row in source_map}

    def resolve(path):
        if path not in table:
            raise ValueError(f'mechanism references absent or non-physical placement {path!r}')
        return table[path]

    inputs = [resolve(p) for p in ([contract['input']] if 'input' in contract else []) + contract.get('inputs', [])]
    outputs = [resolve(p) for p in contract.get('outputs', [])]
    ground = resolve(contract['ground']) if 'ground' in contract else None
    inspection = inspect_connections(model, parts, instance_limit)
    graph = analyse(inspection, connection_contacts(inspection), ground=ground)
    result = mobility(graph, inputs=inputs, outputs=outputs)
    rows = []

    def issue(code, message, instances, severity='error'):
        rows.append(dict(code=code, severity=severity, message=message, instances=list(instances)))

    groups, frame = graph['groups'], graph['frame']
    moving = [label(names, i) for i in result['moving']]
    for index in inputs:
        if result['inputs'][index]:
            continue
        if groups.find(index) == frame:
            issue('technic.mechanism_locked', f"{names[index]} cannot move: it is rigidly joined to the frame. Carry its "
                  'axle in round holes, and use a frictionless pin (3673) where it should pivot.', [index])
        else:
            issue('technic.mechanism_locked', f"{names[index]} cannot move: the joints and gears around it leave it no "
                  'freedom. Look for a second pin on a pivot, a shaft in a cross hole of the frame, or gears that fight.',
                  [index])
    for index in outputs:
        if any(not result['inputs'][i] for i in inputs):
            break
        if not result['outputs'][index]:
            shown = ', '.join(moving[:8]) or 'nothing'
            issue('technic.mechanism_uncoupled', f"Moving the input does not move {names[index]}. Parts that do move with "
                  f"it: {shown}. Follow the chain from there: a gear short of meshing or a missing link ends it.", [index])
        elif result['independent'][index]:
            issue('technic.mechanism_loose', f"{names[index]} can also move while the input is held still.", [index], 'warning')
    if 'dof' in contract and result['degrees_of_freedom'] != contract['dof']:
        issue('technic.mechanism_dof', f"Declared {contract['dof']} degree(s) of freedom; the built pose has "
              f"{result['degrees_of_freedom']} (pins that only spin are not counted).", inputs, 'warning')
    for pair in contract.get('pivots', []):
        a, b = (resolve(p) for p in pair)
        if groups.find(a) == groups.find(b):
            issue('technic.pivot_locked', f"{pair[0]} and {pair[1]} are one rigid group, so they cannot pivot. Join them "
                  'with one frictionless pin (3673) or an axle in a round hole, not friction pins or two pins.', [a, b])
    report = dict(scope='technic-mechanism', checks_passed=not any(r['severity'] == 'error' for r in rows),
                  physical_validity='not_proven', degrees_of_freedom=result['degrees_of_freedom'],
                  input_moves={names[i]: v for i, v in result['inputs'].items()},
                  output_moves_with_input={names[i]: v for i, v in result['outputs'].items()},
                  moving_with_input=moving[:40], graph=describe(graph, names), diagnostics=rows,
                  limitations=['Instantaneous mobility of the built pose with the frame held still; no motion is simulated.',
                               'Play, friction, strength and travel limits are ignored; a singular pose can mislead.',
                               'Shock absorbers, cylinders and actuators slide between their end eyes; ball joints are '
                               'treated as rigid.'])
    return report


def gear_guide(teeth=()):
    """What an author needs to place gears: radii, mesh distances and the common parts."""
    table = gear_table()
    sizes = sorted(set(teeth)) or [8, 12, 16, 20, 24, 36, 40]
    parts = {}
    for code, row in table['gears'].items():
        if row['type'] == 'rack' or 'Pattern' in row['description'] or 'Obsolete' in row['description']:
            continue
        key = (row['type'], row.get('teeth', 0))
        parts.setdefault(key, []).append(code + '.dat')
    from .technic import corpus_uses
    uses = corpus_uses()

    def usable(kinds, count):
        found = [c for kind in kinds for c in parts.get((kind, count), [])]
        return sorted(found, key=lambda c: (-uses.get(c.removesuffix('.dat'), 0), c))[:4]

    rows = [f"{n} teeth: pitch radius {1.25 * n:g} LDU ({1.25 * n / 20:g} studs); parts "
            + (', '.join(usable(('spur', 'double_bevel', 'crown'), n)) or 'none') for n in sizes]
    grid = {f'{a}+{b}': f"{1.25 * (a + b):g} LDU = {1.25 * (a + b) / 20:g} studs"
            for i, a in enumerate(sizes) for b in sizes[i:]}
    whole = [pair for pair, text in grid.items() if float(text.split()[0]) % 20 == 0]
    return dict(rule='Parallel gears mesh when their axes are 1.25 * (teeth_a + teeth_b) LDU apart; a mismatch of more '
                     'than 0.6 LDU is reported.',
                gears=rows, centre_distance=grid, pairs_on_whole_studs=whole,
                worm='A worm (4716) meshes a gear whose axis crosses it at 10 + pitch radius: 20 LDU for 8 teeth, '
                     '40 for 24, 60 for 40. One worm turn moves the gear one tooth.',
                perpendicular=[f"{r['a'][1]}t {r['a'][0]} + {r['b'][1]}t {r['b'][0]}: centres {r['offset_a']:g} and "
                               f"{r['offset_b']:g} LDU from where the axes cross ({r['count']} in official sets)"
                               for r in table['perpendicular']],
                racks={code + '.dat': f"pinion axis along the rack's {row['pinion_axis']}, {abs(row['pitch']):g} LDU pitch line "
                                      f"offset; an 8-tooth pinion stands {abs(row['pitch'] + row['side'] * 10):g} LDU "
                                      f"{'above' if row['side'] < 0 else 'below'} the rack origin"
                       for code, row in table['gears'].items() if row['type'] == 'rack' and 'pitch' in row
                       and abs(row['pitch']) <= 20},
                evidence=table.get('evidence'))


def trace(source, parts, *, section=None):
    """The kinematic reading of a plan or model, with any declared mechanism checked."""
    from pathlib import Path
    from .connectivity import inspect_connections
    from .connection_adapter import connection_contacts
    source = Path(source)
    names, reviews = {}, {}
    if source.suffix.casefold() == '.json':
        from .builder import load_plan, select_plan
        from .workflow import build_checked
        plan = load_plan(source)
        if section:
            plan = select_plan(plan, section)
        _, model, report = build_checked(plan, parts, detail='summary', contacts='auto')
        if model is None or not report.get('source_map'):
            return dict(checks_passed=False, diagnostics=report['diagnostics'][:10],
                        note='The plan does not build; fix build errors first.')
        names = {row['index']: row['path'] for row in report['source_map']}
        reviews = {name: dict(checks_passed=m['checks_passed'], degrees_of_freedom=m['degrees_of_freedom'],
                              input_moves=m['input_moves'], output_moves_with_input=m['output_moves_with_input'],
                              problems=[d['message'] for d in m['diagnostics']])
                   for name, m in report.get('mechanism', {}).items()}
    else:
        from .validation import validate_file
        model, _ = validate_file(source, parts, assembly=True, section=section)
        if model is None:
            return dict(checks_passed=False, note='The model does not parse; run review on it first.')
    inspection = inspect_connections(model, parts)
    graph = analyse(inspection, connection_contacts(inspection))
    if not names:
        names = {i: f"#{i} {o.occurrence.reference}" for i, o in graph['items'].items()}
    problems = diagnostics(graph)
    result = dict(checks_passed=all(r['checks_passed'] for r in reviews.values()), counts=summary(graph), **describe(graph, names))
    if problems:
        result['problems'] = [f"{d['code']}: {d['message']} [{', '.join(names.get(i, str(i)) for i in d['instances'])}]"
                              for d in problems]
    if reviews:
        result['mechanisms'] = reviews
    return result
