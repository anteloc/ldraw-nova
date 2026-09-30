"""Small structural recipes with declared mounting pairs and real part lengths."""
from __future__ import annotations

from collections import defaultdict
import math

import numpy as np

from .builder import rotation
from .common import jsonable
from .technic import canonical, registry

RECIPES = {
    'reinforced-frame': dict(title='Reinforced mounting frame',
        lesson='Four crossmembers, each attached at two separated points, reinforce a moulded frame.'),
    'box-chassis': dict(title='Box chassis',
        lesson='Perpendicular frames and two long rails establish structure in three dimensions.'),
    'frame-tower': dict(title='Frame tower',
        lesson='Repeated box cells joined with overlapping beams and shared three-layer pins.'),
    'service-platform': dict(title='Service platform',
        lesson='A System equipment body and tiled deck mount on a Technic skeleton through eight stud-ended pins.'),
}


class Structure:
    def __init__(self, name):
        self.name = name
        self.entries = {}
        self.wires = []
        self.required = []
        self.assembly = []

    def add(self, name, ref, at, colour=71, matrix=None, phase=20):
        if name in self.entries:
            raise ValueError('Duplicate structural placement name')
        self.entries[name] = dict(id=name, ref=ref+'.dat', at=list(at), colour=colour,
                                 matrix=jsonable(matrix or rotation()), phase=phase)
        return name

    def hole(self, name, point, axis):
        entry = self.entries[name]
        part = registry()['parts'][canonical(entry['ref'])]
        matrix, at = np.array(entry['matrix']), np.array(entry['at'])
        for port in part['ports']:
            if port['kind'] != 'pin_hole':
                continue
            position = at + matrix @ port['at']
            direction = matrix @ port['axis']
            if np.allclose(position, point, atol=1e-6) and abs(np.dot(direction, axis)) > .9999:
                return
        raise ValueError(f'No reviewed pin hole at {point} on {name}')

    def wire(self, first, first_point, second, second_point, axis):
        self.hole(first, first_point, axis)
        self.hole(second, second_point, axis)
        self.wires.append((first, tuple(first_point), second, tuple(second_point), tuple(axis)))

    def install_pins(self):
        # Merge adjacent two-layer connections into a shared three-layer pin.
        lines = defaultdict(set)
        for a, p, b, q, axis in self.wires:
            index = next(i for i, v in enumerate(axis) if v)
            key = (index, *[p[i] for i in range(3) if i != index])
            lines[key].update([(a, p), (b, q)])
        groups = []
        for key, members in sorted(lines.items()):
            index = key[0]
            group = []
            for name, point in sorted(members, key=lambda m: m[1][index]):
                if group and abs(point[index]-group[-1][1][index]-20) > 1e-6:
                    groups.append((index, group))
                    group = []
                group.append((name, point))
            groups.append((index, group))
        for n, (axis, group) in enumerate(groups):
            if len(group) not in {2, 3}:
                raise ValueError('Structural recipe needs a two- or three-layer pin stack')
            centre = np.mean([p for _, p in group], axis=0).tolist()
            matrix = rotation() if axis == 0 else rotation('z', 90) if axis == 1 else rotation('y', -90)
            phase = min(self.entries[name]['phase'] for name, _ in group)+1
            pin = self.add(f'pin-{n}', '2780' if len(group) == 2 else '6558', centre,
                           0 if len(group) == 2 else 1, matrix, phase)
            for name, _ in group:
                self.required.append((pin, name))
            self.assembly.append((pin, [name for name, _ in group if self.entries[name]['phase'] > phase]))

    def finish(self):
        self.install_pins()
        ordered = sorted(self.entries.values(), key=lambda e: (e['phase'], e['id']))
        phases = defaultdict(list)
        indices = {}
        for i, entry in enumerate(ordered):
            indices[entry['id']] = i
            phases[entry['phase']].append({k: v for k, v in entry.items() if k != 'phase'})
        plan = dict(version=1, author='ldraw-nova structural examples', sections=[dict(
            name=self.name+'.ldr', description=RECIPES[self.name]['title']+'; static structure, stage 1',
            steps=list(phases.values()), anchors={'origin': {'at': [0, 0, 0]}})])
        contract = dict(version=1, require_rigid=True,
            required_joints=[dict(between=[indices[a], indices[b]]) for a, b in self.required],
            assembly=[dict(connector=indices[p], before=[indices[n] for n in later])
                      for p, later in self.assembly if later])
        return plan, contract


# Native frame X -> world Z, native Y -> world X, native Z -> world Y.
VERTICAL = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]


def box(s, prefix, y, colour, accent):
    for side in [-1, 1]:
        s.add(f'{prefix}-side-{side}', '64179', (60*side, y, 0), colour,
              matrix=_matrix(VERTICAL), phase=10 if side == -1 else 30)
    for level in [-1, 1]:
        h = s.add(f'{prefix}-level-{level}', '64179', (0, y+60*level, 0), accent, phase=20)
        for side in [-1, 1]:
            for z in [-40, 40]:
                s.wire(h, (40*side, y+60*level, z), f'{prefix}-side-{side}',
                       (60*side, y+60*level, z), (1, 0, 0))


def _matrix(rows):
    from ldraw import Matrix
    return Matrix(rows)


def rails(s, prefix, y, colour):
    for side in [-1, 1]:
        rail = s.add(f'rail-{side}', '32278', (40*side, y-80, 0), colour, phase=40)
        for z in [-60, 60]:
            s.wire(rail, (40*side, y-80, z), f'{prefix}-level--1',
                   (40*side, y-60, z), (0, 1, 0))


def body(s, colour, accent):
    for side in [-1, 1]:
        for z in [-100, -40, 40, 100]:
            name = s.add(f'mount-{side}-{z}', '4274', (40*side, -90, z), 7,
                         rotation('z', -90), phase=45)
            rail = f'rail-{side}'
            s.hole(rail, (40*side, -80, z), (0, 1, 0))
            deck = 'deck-front' if z < 0 else 'deck-rear'
            s.required.extend([(name, rail), (name, deck)])
            s.assembly.append((name, [deck]))
    for label, z in [('front', -70), ('rear', 90)]:
        s.add('deck-'+label, '3036', (10, -98, z), 72, rotation('y', 90), phase=50)
    for x in [-30, 10, 50]:
        for z in [-130, -90, -50, -10]:
            s.add(f'deck-tile-{x}-{z}', '3068b', (x, -106, z), 71, phase=60)
    for x in [-40, 60]:
        s.add(f'housing-side-{x}', '3008', (x, -122, 90), 15, rotation('y', 90), phase=60)
    for z in [20, 160]:
        s.add(f'housing-end-{z}', '3010', (10, -122, z), 15, phase=60)
    s.add('housing-roof', '3036', (10, -130, 90), accent, rotation('y', 90), phase=70)
    for z in [40, 60, 80, 100, 120, 140]:
        s.add(f'roof-vent-{z}', '2412b', (10, -138, z), 0, phase=80)
    for x in [-40, 60]:
        for z in [20, 160]:
            s.add(f'beacon-{x}-{z}', '6141', (x, -138, z), 47, phase=80)


def structure_plan(name, *, levels=2, colour=71, accent=14):
    if name not in RECIPES:
        raise ValueError('Unknown structural recipe; use technic list')
    if isinstance(levels, bool) or not isinstance(levels, int) or not 1 <= levels <= 3:
        raise ValueError('Tower levels must be an integer from 1 to 3')
    if any(isinstance(c, bool) or not isinstance(c, int) for c in (colour, accent)):
        raise ValueError('Colours must be integer LDraw colour codes')
    s = Structure(name)
    if name == 'reinforced-frame':
        s.add('frame', '64179', (0, 0, 0), colour, phase=10)
        for z in [-60, -20, 20, 60]:
            beam = s.add(f'crossmember-{z}', '32316', (0, -20, z), accent, rotation('y', 90), phase=20)
            for x in [-40, 40]:
                s.wire('frame', (x, 0, z), beam, (x, -20, z), (0, 1, 0))
    elif name == 'frame-tower':
        for level in range(levels):
            box(s, f'cell-{level}', -160*level, colour, accent)
        for level in range(levels-1):
            y = -160*level
            for side in [-1, 1]:
                for z in [-40, 40]:
                    beam = s.add(f'bridge-{level}-{side}-{z}', '32524', (80*side, y-80, z), accent,
                                 _matrix(VERTICAL), phase=40)
                    for offset, cell in [(-20, level), (-60, level), (-100, level+1), (-140, level+1)]:
                        s.wire(f'cell-{cell}-side-{side}', (60*side, y+offset, z),
                               beam, (80*side, y+offset, z), (1, 0, 0))
    else:
        box(s, 'core', 0, colour, accent)
        rails(s, 'core', 0, 15)
        if name == 'service-platform':
            body(s, colour, accent)
    return s.finish()
