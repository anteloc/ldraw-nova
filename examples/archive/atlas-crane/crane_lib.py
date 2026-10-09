"""Geometry helpers for the Atlas AT-90 crane generator.

Conventions (LDraw): X across (+X = right/starboard), Y down (negative Y is up),
Z along the vehicle (-Z = forward).  All placements are emitted as explicit
`at` + proper-rotation `matrix` entries in plan sections.

Measured part conventions used below (see tools/probe.py and the Technic registry):
- Studless beams (32523, 32316, 32524, 40490, 32525, 41239, 32278): length along
  local Z, centred; holes along local Y at z = 20*k - 10*(n-1).
- Pins / axles / axle-pins (2780, 6558, 43093, 3705, ...): shaft along local X, centred.
- Bush 3713: bore along local Z.
- Open frame 64179: 5 (X, 100) x 7 (Z, 140), face holes along Y on the long sides at
  z=+-60,+-20, in-plane X holes at z=-40,0,40, in-plane Z holes on the ends at x=-20,0,20.
"""
from __future__ import annotations

import numpy as np

AX = {
    'X': (1, 0, 0), '-X': (-1, 0, 0),
    'Y': (0, 1, 0), '-Y': (0, -1, 0),
    'Z': (0, 0, 1), '-Z': (0, 0, -1),
}

BEAMS = {2: '43857', 3: '32523', 5: '32316', 7: '32524', 9: '40490', 11: '32525', 13: '41239', 15: '32278'}
AXLES = {2: '32062', 3: '4519', 4: '3705', 5: '32073', 6: '3706', 7: '44294', 8: '3707',
         9: '60485', 10: '3737', 12: '3708', 16: '50451'}


def v(a):
    if isinstance(a, str):
        return np.array(AX[a], float)
    return np.array(a, float)


def unit(a):
    a = v(a)
    return a / np.linalg.norm(a)


def basis(x=None, y=None, z=None):
    """Proper rotation whose columns are the world images of local x, y, z.

    Give any two (the third is derived so that det = +1)."""
    if x is not None and y is not None:
        x, y = unit(x), unit(y)
        z = np.cross(x, y)
    elif y is not None and z is not None:
        y, z = unit(y), unit(z)
        x = np.cross(y, z)
    elif x is not None and z is not None:
        x, z = unit(x), unit(z)
        y = np.cross(z, x)
    else:
        raise ValueError('basis needs two axes')
    m = np.column_stack([x, y, z])
    assert abs(np.linalg.det(m) - 1) < 1e-9, m
    assert np.allclose(m.T @ m, np.eye(3), atol=1e-9), m
    return m


def rot(axis, deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    if axis == 'x':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == 'y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    if axis == 'z':
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    raise ValueError(axis)


def perp(axis):
    """Some unit vector perpendicular to axis (deterministic)."""
    a = unit(axis)
    for c in (np.array([0, 1.0, 0]), np.array([0, 0, 1.0]), np.array([1.0, 0, 0])):
        if abs(np.dot(a, c)) < 0.9:
            p = c - np.dot(a, c) * a
            return p / np.linalg.norm(p)
    raise AssertionError


def clean(x, nd=4):
    r = [round(float(t), nd) for t in np.ravel(x)]
    return [0.0 if t == 0 else t for t in r]


class Frame:
    """A rigid local frame: world = R @ local + t."""

    def __init__(self, R=None, t=(0, 0, 0)):
        self.R = np.eye(3) if R is None else np.array(R, float)
        self.t = v(t)

    def __matmul__(self, other):
        return Frame(self.R @ other.R, self.R @ other.t + self.t)

    def p(self, local):
        return self.R @ v(local) + self.t

    def d(self, local_dir):
        return self.R @ v(local_dir)


class Section:
    """Collects placements for one generated `.ldr` plan section."""

    def __init__(self, name, description, author=None):
        self.name = name
        self.description = description
        self.steps = [[]]
        self.counts = {}
        self.anchors = {}
        self.author = author
        self.frame = Frame()

    def step(self):
        if self.steps[-1]:
            self.steps.append([])

    def _id(self, ref, id):
        if id is None:
            stem = ref.replace('.dat', '').replace('.ldr', '')
            n = self.counts.get(stem, 0)
            self.counts[stem] = n + 1
            id = f'{stem}-{n}'
        return id

    def add(self, ref, colour, at, R=None, id=None, purpose=None, frame=None):
        f = frame or self.frame
        R = np.eye(3) if R is None else np.array(R, float)
        wR = f.R @ R
        wt = f.p(at)
        if not (ref.endswith('.dat') or ref.endswith('.ldr')):
            ref = ref + '.dat'
        e = {'id': self._id(ref, id), 'ref': ref, 'colour': colour,
             'at': clean(wt, 3), 'matrix': [clean(row, 9) for row in wR]}
        if purpose:
            e['purpose'] = purpose
        self.steps[-1].append(e)
        return e

    def plan(self):
        s = {'name': self.name, 'description': self.description,
             'steps': [st for st in self.steps if st]}
        if self.anchors:
            s['anchors'] = self.anchors
        if self.author:
            s['author'] = self.author
        return s

    def count(self):
        return sum(len(s) for s in self.steps)


# ---------------------------------------------------------------- Technic helpers

def beam(sec, n, centre, along, holes, colour, purpose=None, frame=None):
    """Studless beam of n holes; `along` = length dir, `holes` = hole axis."""
    R = basis(y=holes, z=along)
    return sec.add(BEAMS[n], colour, centre, R, purpose=purpose, frame=frame)


def beam_holes(n, centre, along):
    c, a = v(centre), unit(along)
    return [c + a * (20 * k - 10 * (n - 1)) for k in range(n)]


def pin(sec, at, axis, colour=0, long=False, purpose=None, frame=None, ref=None):
    R = basis(x=axis, y=perp(axis))
    return sec.add(ref or ('6558' if long else '2780'), colour, at, R, purpose=purpose, frame=frame)


def axle(sec, n, centre, axis, colour=71, purpose=None, frame=None):
    R = basis(x=axis, y=perp(axis))
    return sec.add(AXLES[n], colour, centre, R, purpose=purpose, frame=frame)


def bush(sec, at, axis, colour=71, half=False, purpose=None, frame=None):
    R = basis(z=axis, x=perp(axis))
    return sec.add('32123b' if half else '3713', colour, at, R, purpose=purpose, frame=frame)


def axlepin(sec, at, axis, colour=1, purpose=None, frame=None):
    """43093: pin end at local -X, axle end at +X; `axis` points pin->axle."""
    R = basis(x=axis, y=perp(axis))
    return sec.add('43093', colour, at, R, purpose=purpose, frame=frame)
