#!/usr/bin/env python3
"""An-225 Mriya at about 1:100: a System-brick model parked with its nose visor raised.

Run from the repository root:

    .venv/bin/python examples/an225/generate.py            # write the plan
    ./ldraw-agent build examples/an225/an225-mriya.plan.json ...

Authoring conventions follow ldraw_tools.architecture.Module: x/z in studs,
h upwards in LDU, emitted as LDraw [20x, -h, 20z]. X is across the aircraft
(port -X), -Z is forward and Y=0 is the ground. Station s counts studs aft of
the closed nose tip; z = s - S0. Every height below is a body plane measured
from the installed part geometry; bounding-box heights are never used for
stacking. No part is mirrored or scaled: left/right wedges use their real
opposite-hand counterparts.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ldraw_tools.architecture import Module  # noqa: E402
from ldraw_tools.builder import rotation  # noqa: E402
from ldraw_tools.vehicles import axle  # noqa: E402

OUT = Path(__file__).resolve().parent
AUTHOR = 'ldraw-nova An-225 Mriya study'
S0 = 52  # station of the model origin; the airframe spans s=0..106


def Z(s):
    return s - S0


# ---------------------------------------------------------------- palette roles
BODY, CHEAT, PIN = 15, 1, 14            # white fuselage, blue cheatline, yellow pinstripe
WING, BELLY, GEAR = 71, 71, 72          # light grey flying surfaces and belly, dark grey gear
GLASS, TYRE, RIM = 10375, 256, 71       # trans-black glazing, rubber black tyres
METAL, DARK = 315, 72                   # flat silver engine details, dark grey
FLOOR, MARK = 71, 14                    # hold floor and yellow loading marks
PORT_LAMP, STBD_LAMP = 36, 34           # trans red (port) / trans green (starboard)

# ------------------------------------------------------ measured part vocabulary
# Rectangular parts: long axis along local X (checked with `ldraw-agent part`).
PLATE = {(1, 1): '3024', (1, 2): '3023b', (1, 3): '3623', (1, 4): '3710', (1, 6): '3666',
         (1, 8): '3460', (1, 10): '4477', (1, 12): '60479', (2, 2): '3022', (2, 3): '3021',
         (2, 4): '3020', (2, 6): '3795', (2, 8): '3034', (2, 10): '3832', (2, 12): '2445',
         (2, 14): '91988', (2, 16): '4282', (4, 4): '3031', (4, 6): '3032', (4, 8): '3035',
         (4, 10): '3030', (4, 12): '3029', (6, 6): '3958', (6, 8): '3036', (6, 10): '3033',
         (6, 12): '3028', (6, 14): '3456', (6, 16): '3027', (8, 8): '41539', (8, 16): '92438'}
BRICK = {(1, 1): '3005', (1, 2): '3004', (1, 3): '3622', (1, 4): '3010', (1, 6): '3009',
         (1, 8): '3008', (1, 10): '6111', (1, 12): '6112', (2, 2): '3003', (2, 3): '3002',
         (2, 4): '3001', (2, 6): '2456', (2, 8): '3007'}
TILE = {(1, 1): '3070b', (1, 2): '3069b', (1, 3): '63864', (1, 4): '2431', (1, 6): '6636',
        (1, 8): '4162', (2, 2): '3068b', (2, 3): '26603', (2, 4): '87079', (2, 6): '69729'}
TABLES = {'plate': PLATE, 'brick': BRICK, 'tile': TILE}
BODY_H = {'plate': 8, 'tile': 8, 'brick': 24}

TILE.update({(4, 4): '1751', (3, 6): '6934', (6, 6): '10202', (6, 8): '6320', (8, 16): '48288'})


def rect(m, kind, x0, s0, w, d, base, colour, **kw):
    """Axis-aligned plate/brick/tile over x0..x0+w, s0..s0+d, underside at base."""
    a, b = sorted((w, d))
    ref = TABLES[kind][(a, b)]
    yaw = 0 if w >= d else 90
    return m.add(ref, colour, x0 + w / 2, base + BODY_H[kind], Z(s0) + d / 2, yaw=yaw, **kw)


def split(n, options=(12, 10, 8, 6, 4, 3, 2, 1), first=None):
    """Integer run lengths using real part lengths; `first` staggers joints."""
    out = []
    if first and n:
        f = max(o for o in options if o <= min(first, n))
        out.append(f)
        n -= f
    while n > 0:
        k = next(o for o in options if o <= n)
        out.append(k)
        n -= k
    return out


def run(m, kind, x0, s0, s1, base, colour, *, first=None, special=None):
    """A 1-wide run along the fuselage; `special` maps single cells s -> (ref, colour)."""
    options = sorted({k[1] for k in TABLES[kind] if k[0] == 1}, reverse=True)
    special = special or {}
    s = s0
    for cut in sorted(k for k in special if s0 <= k < s1) + [s1]:
        for n in split(cut - s, options, first):
            rect(m, kind, x0, s, 1, n, base, colour)
            s += n
        first = None
        if cut < s1:
            ref, colour_ = special[cut]
            m.add(ref, colour_, x0 + .5, base + BODY_H[kind], Z(cut) + .5)
            s = cut + 1


def pack(cells, sizes, key, below=None):
    """Greedy exact cover of integer (x, s) cells with rectangles, in scan order `key`.

    With `below` (cell -> supporting piece id), each rectangle prefers to bridge at least
    two supporting pieces (a running bond), then to rest on one, then to be large.
    """
    free = set(cells)
    out = []
    for c in sorted(free, key=key):
        if c not in free:
            continue
        x, s = c
        best = None
        for w, d in sizes:
            block = {(x + i, s + j) for i in range(w) for j in range(d)}
            if not block <= free:
                continue
            n = len({below[q] for q in block if q in below}) if below else 2
            score = (n >= 2, n > 0, w * d)
            if best is None or score > best[0]:
                best = (score, (x, s, w, d), block)
            if n >= 2:
                break          # sizes are ordered by area: this is the largest bridging block
        if best is None:
            raise ValueError(f'cannot cover cell {c}')
        out.append(best[1])
        free -= best[2]
    return out


def sizes_for(kind, prefer):
    sizes = set()
    for a, b in TABLES[kind]:
        if kind == 'brick' and a > 1 and b > 8:
            continue
        sizes.add((a, b))
        sizes.add((b, a))
    # prefer='s': long runs along the fuselage/chord; prefer='x': along the span.
    return sorted(sizes, key=lambda wd: (-wd[0] * wd[1], wd[0] > wd[1] if prefer == 's' else wd[0] < wd[1]))


def field(m, cells_, base, colour, prefer='s', key=None, kind='plate', below=None, tag=None, preset=()):
    """Pack and place a layer; returns cell -> piece id for bonding the next layer.

    `preset` rectangles (x, s, w, d) are placed first, e.g. deliberate tie plates.
    """
    key = key or (lambda c: (c[1], c[0]))
    placed = {}
    taken = {(x + i, s + j) for x, s, w, d in preset for i in range(w) for j in range(d)}
    assert taken <= set(cells_), 'preset rectangles must lie inside the layer'
    for x, s, w, d in list(preset) + pack(set(cells_) - taken, sizes_for(kind, prefer), key, below):
        pid = rect(m, kind, x, s, w, d, base, colour)
        for i in range(w):
            for j in range(d):
                placed[(x + i, s + j)] = (tag, pid)
    return placed


def cells(x0, x1, s0, s1):
    return {(x, s) for x in range(x0, x1) for s in range(s0, s1)}


def hinged(parent, module, axis_h, axis_s, degrees, id):
    """Place a module authored in the closed pose, rigidly rotated about an X-axis hinge line."""
    R = np.array(rotation('x', degrees).rows)
    a = np.array([0, -axis_h, 20 * Z(axis_s)], float)
    at = a - R @ a
    return parent.add(module, 16, at[0] / 20, -at[1], at[2] / 20, matrix=R.round(12).tolist(), id=id)


# ============================================================ master layout
# Heights (LDU, upward) --------------------------------------------------
HOLDER_TOP = 23                # 4600 stud body plane (holder origin), from vehicles.axle('classic')
KEEL = (39, 47, 55)            # three keel plate layers, underside 39 (tyre tops at 36)
FLOOR = 63                     # hold floor tiles / wall base plates underside (top 71)
COURSES = [71, 95, 119, 143, 167]   # wall brick undersides; top of the last is 191
CEIL = 191                     # blue ceiling / cheatline plate field underside
PINSTRIPE = 199                # yellow wall plate underside
UPPER = 207                    # upper-deck brick course underside (top 231)
ROOF = 231                     # roof plate field underside (top 239)
SKIN = 239                     # wing/stabiliser/roof-edge underside (top of the roof plates)
TOP = 255                      # fuselage roof top and flush wing top
# Stations (studs aft of the closed nose tip) -----------------------------
FRONT = 7                      # fixed fuselage front: cargo opening plane
HINGE_S = 7                    # visor hinge row occupies s=7..8 on the ceiling
CAB = 9                        # upper deck/windscreen start, behind the hinge sweep zone
AFT = 72                       # start of the belly upsweep
STEPS = 6                      # 4-stud belly steps (13547 rows) s=72..96
TAIL = 100                     # end of the full-width fuselage; tail cone s=100..104
STRIPE_END = 96                # blue/yellow cheatline stops ahead of the tail cone
SPONSON = (37, 57)
MAIN_GEAR_S = 39               # first main holder front edge; seven 2-stud holders
NOSE_GEAR_S = 11
WING_LE, WING_TE = 32, 50      # root chord (|x|<=5); 1:2 LE and 1:4 TE sweep outboard
STAB_LE, STAB_TE = 88, 100
ENGINES = (12, 20, 28)         # engine centre |x| in studs
VISOR_AXIS = (213, HINGE_S + .5)   # 3937/3938 hinge line: 10 LDU below the 3938 stud plane
VISOR_DEG = -70                # nose-up rotation about +X
RAMP_AXIS = (69, 6.5)          # 44301a/44302a finger line: 2 LDU below the floor top
WINDOWS = (13, 15, 17, 19, 21, 23)
BURAN = (28, 56)


RAMP_FRONT = -1                # ramp deck spans s=-1..6 (7 studs ahead of the lip hinge)
RAMP_DEG = 22.5                # a 44301a/44302a click detent (the teeth mesh every 22.5 deg)


def ramp_angle():
    """Click-detent tilt; assert the ramp's front underside edge stays at or above the ground."""
    h, s = RAMP_AXIS
    dz, y = 20 * (RAMP_FRONT - s), h - FLOOR   # front-bottom edge relative to the axis (LDraw y down)
    t = math.radians(RAMP_DEG)
    toe = h - (y * math.cos(t) - dz * math.sin(t))
    assert toe >= 0, f'ramp toe below ground: {toe:.2f}'
    return RAMP_DEG


def ramp_toe_height():
    h, s = RAMP_AXIS
    dz, y = 20 * (RAMP_FRONT - s), h - FLOOR
    t = math.radians(RAMP_DEG)
    return round(h - (y * math.cos(t) - dz * math.sin(t)), 2)


# ============================================================ running gear
def main_gear():
    m = Module('an225-main-gear', 'Seven-axle main landing-gear bogie: 4600/4624/3641 pairs from the '
               'measured classic axle recipe on a staggered beam; local ground Y=0, beam top Y=-39')
    wheel = axle('classic', rim_colour=RIM)
    for k in range(7):
        m.add(wheel, 16, 0, 0, 1 + 2 * k, id=f'axle-{k}')
    m.step()
    for base, lengths in [(HOLDER_TOP, (8, 6)), (HOLDER_TOP + 8, (6, 8))]:
        z = 0
        for n in lengths:
            m.add(PLATE[(2, n)], GEAR, 0, base + 8, z + n / 2, yaw=90, purpose='bogie beam bonding the holders')
            z += n
    m.anchor('keel', h=KEEL[0], z=7)
    return m


def nose_leg():
    m = Module('an225-nose-leg', 'Nose landing-gear leg: one classic wheel pair and a two-plate strut; '
               'local ground Y=0, top Y=-39 meets the keel underside')
    m.add(axle('classic', rim_colour=RIM), 16, 0, 0, 0, id='axle')
    m.add('3022', GEAR, 0, HOLDER_TOP + 8, 0, id='strut-lower')
    m.add('3022', GEAR, 0, HOLDER_TOP + 16, 0, id='strut-upper')
    return m


# ============================================================ fuselage
def keel():
    m = Module('an225-keel', 'Three-layer bonded keel (underside Y=-39) from the cargo opening to the '
               'belly upsweep, widened under the main-gear sponsons')
    body = cells(-5, 5, FRONT, AFT) | cells(-7, 7, *SPONSON)
    k0 = field(m, body, KEEL[0], BELLY, prefer='s', key=lambda c: (c[1], c[0]), tag='k0')
    m.step()
    # Tie plates carry each 2-wide sponson extension into the main keel (K0/K2 strips align).
    ties = [(-7, SPONSON[0], 6, 16), (-7, SPONSON[0] + 16, 6, 4),
            (1, SPONSON[0], 6, 16), (1, SPONSON[0] + 16, 6, 4)]
    k1 = field(m, body, KEEL[1], BODY, prefer='x', key=lambda c: (c[1], c[0]), below=k0, tag='k1',
               preset=ties)
    m.step()
    field(m, body, KEEL[2], BODY, prefer='s', key=lambda c: (c[1], -c[0]), below=k1, tag='k2')
    return m


def fuselage():
    m = Module('an225-fuselage', 'Fuselage shell: bonded side walls reaching over the belly steps, '
               'blue ceiling cheatline, yellow pinstripe, windowed upper deck and curved-edge roof')
    for x in (-5, 4):
        run(m, 'plate', x, FRONT, AFT, FLOOR, BODY)
    m.step()
    for j, base in enumerate(COURSES):
        s1 = AFT + 4 * (j + 1)       # course j is carried aft by belly-step deck D_j
        for x in (-5, 4):
            run(m, 'brick', x, FRONT, s1, base, BODY, first=(4 if j % 2 else None))
    m.step()
    # The blue cheatline ends at s=96; the tail cone ceiling is white (its underside shows).
    field(m, cells(-5, 5, FRONT, STRIPE_END), CEIL, CHEAT, prefer='x', key=lambda c: (c[1], c[0]))
    field(m, cells(-5, 5, STRIPE_END, TAIL) | cells(-3, 3, TAIL, TAIL + 4), CEIL, BODY, prefer='x')
    m.step()
    glass = {s: ('3005', GLASS) for s in WINDOWS} | {CAB: ('3005', GLASS)}
    for x in (-5, 4):
        run(m, 'plate', x, CAB, STRIPE_END, PINSTRIPE, PIN, first=5)
        run(m, 'plate', x, STRIPE_END, TAIL, PINSTRIPE, BODY)
        run(m, 'brick', x, CAB, TAIL, UPPER, BODY, first=3, special=glass)
    m.step()
    field(m, cells(-5, 5, CAB + 1, TAIL), ROOF, BODY, prefer='s', key=lambda c: (c[1] + 1, c[0]))
    m.step()
    buran = {(x, s) for s in BURAN for x in (-2, 1)}
    for s0, s1 in [(CAB + 3, WING_LE), (WING_TE, STAB_LE)]:
        assert (s1 - s0) % 2 == 0
        for s in range(s0, s1 - 1, 2):
            for side in (-1, 1):
                # 15068: bottom origin, high side toward local +Z; yaw +/-90 turns it outboard.
                m.add('15068', BODY, side * 4, SKIN, Z(s + 1), yaw=90 if side < 0 else -90)
        field(m, cells(-3, 3, s0, s1), SKIN, BODY, prefer='x', key=lambda c: (c[1], c[0]))
        field(m, cells(-3, 3, s0, s1) - buran, SKIN + 8, BODY, kind='tile')
    return m


def sponsons():
    m = Module('an225-sponsons', 'Main-gear sponson fairings on the widened keel: outer walls, a 2-wide '
               'cap and outward curves meeting the fuselage wall')
    s0, s1 = SPONSON
    for side in (-1, 1):
        xo, xi = (6, 5) if side > 0 else (-7, -6)
        run(m, 'plate', xo, s0, s1, FLOOR, BODY)
        run(m, 'plate', xi, s0, s1, FLOOR, BODY, first=3)
        run(m, 'brick', xo, s0, s1, 71, BODY)
        run(m, 'brick', xo, s0, s1, 95, BODY, first=4)
        for base in (71, 95):
            # Close the hollow fairing ends in the inner column.
            rect(m, 'brick', xi, s0, 1, 1, base, BODY)
            rect(m, 'brick', xi, s1 - 1, 1, 1, base, BODY)
        field(m, cells(min(xi, xo), max(xi, xo) + 1, s0, s1), 119, BODY, prefer='s')
        for s in range(s0, s1 - 1, 2):
            m.add('15068', BODY, (xi + xo + 1) / 2, 127, Z(s + 1), yaw=90 if side < 0 else -90)
    return m


def hold():
    m = Module('an225-hold', 'Cargo hold floor: ramp hinge plates (44302a) at the lip, tiled floor, '
               'yellow threshold; containers stand on exposed keel studs')
    hinge_x = (-4, -2, 1, 3)
    for x in hinge_x:
        m.add('44302a', GEAR, x + .5, FLOOR + 8, Z(8), yaw=90, id=f'ramp-hinge-fixed-{x + 4}')
    m.step()
    containers = CONTAINERS['orange'][0] | CONTAINERS['green'][0]
    floor = cells(-4, 4, FRONT, 31) - containers - {(x, s) for x in hinge_x for s in (7, 8)}
    field(m, {c for c in floor if c[1] == 9}, FLOOR, MARK, kind='tile')
    field(m, {c for c in floor if c[1] != 9}, FLOOR, FLOOR_COLOUR, kind='tile')
    return m


CONTAINERS = {'orange': (cells(-4, -1, 12, 24), 25), 'green': (cells(1, 4, 15, 27), 378)}
FLOOR_COLOUR = 71


def container(name):
    area, colour = CONTAINERS[name]
    x0 = min(c[0] for c in area)
    s0 = min(c[1] for c in area)
    m = Module(f'an225-container-{name}', 'Microscale 40 ft container: three bonded brick courses and a '
               'tiled roof, standing on keel studs (underside Y=-63)')
    for k, base in enumerate((FLOOR, FLOOR + 24, FLOOR + 48)):
        if k % 2 == 0:
            rect(m, 'brick', x0, s0, 2, 8, base, colour)
            rect(m, 'brick', x0, s0 + 8, 2, 4, base, colour)
            rect(m, 'brick', x0 + 2, s0, 1, 12, base, colour)
        else:
            rect(m, 'brick', x0, s0, 1, 12, base, colour)
            rect(m, 'brick', x0 + 1, s0, 2, 4, base, colour)
            rect(m, 'brick', x0 + 1, s0 + 4, 2, 8, base, colour)
    rect(m, 'tile', x0, s0, 3, 6, FLOOR + 72, colour)
    rect(m, 'tile', x0, s0 + 6, 3, 6, FLOOR + 72, colour)
    return m


def aft():
    m = Module('an225-aft', 'Upswept rear fuselage: six 4-stud belly steps (3030 deck over 13547 '
               'inverted curves) carried by the long wall courses, 24201 skirt and tapered tail cone')
    for L in range(STEPS):
        s0 = AFT + 4 * L
        base = KEEL[0] + 24 * L
        for x in range(-5, 5):
            # 13547 curves rise toward local -Z; yaw 180 puts the full-depth end forward.
            m.add('13547', BELLY if L == 0 else BODY, x + .5, base + 24, Z(s0) + .5, yaw=180)
        m.add('3030', BODY, 0, base + 32, Z(s0) + 2, purpose=f'belly step deck D{L}')
    m.step()
    for x in range(-5, 5):
        # 24201: full depth toward local +Z; yaw 180 puts it forward, hanging from the ceiling.
        m.add('24201', BODY, x + .5, CEIL, Z(TAIL - 4) + 1.5, yaw=180)
    m.step()
    for x in (-3, -1, 1):
        rect(m, 'brick', x, TAIL - 2, 2, 6, PINSTRIPE, BODY)
    for x in range(-3, 3):
        # 61678 descends toward local -Z; yaw 180 keeps the high end forward.
        m.add('61678', BODY, x + .5, UPPER + 24 + 16, Z(TAIL) + 2, yaw=180)
    return m


def cockpit():
    m = Module('an225-cockpit', 'Upper-deck nose: 3937 visor hinge bases on the ceiling front, '
               'trans-black windscreen band with frames and forehead curve; s=8..9 is hinge clearance')
    for x in (-3, -1, 1, 3):
        # yaw 180: the base's relieved edge faces aft, the direction the visor top swings.
        m.add('3937', DARK, x, CEIL + 8 + 24, Z(HINGE_S) + .5, yaw=180, id=f'visor-hinge-base-{x + 3}')
    m.step()
    field(m, cells(-4, 4, CAB, CAB + 2), PINSTRIPE, BODY, prefer='x')
    for x in (-2, 0, 2):
        m.add('3039', GLASS, x, UPPER + 24, Z(CAB) + 1.5, id=f'windscreen-{x + 2}')
    for x, name in ((-3.5, 'port'), (3.5, 'starboard')):
        m.add('3040b', BODY, x, UPPER + 24, Z(CAB) + 1.5, id=f'windscreen-frame-{name}')
    m.step()
    for x in (-4, -2, 0, 2, 4):
        m.add('15068', BODY, x, SKIN, Z(CAB + 2), id=f'forehead-{x + 4}')
    return m


# ============================================================ nose visor and ramp
def visor():
    """Hollow nose visor authored in its closed pose (world coordinates), hinged at its top rear.

    Rings of slopes/bricks alternate with plate shelves. Each shelf covers the union of
    the ring cells below and above; the bond-aware packer bridges front, corner and side
    pieces, whose runs overlap by one row so that rectangular plates can join them.
    """
    m = Module('an225-visor', 'Nose visor authored closed: inverted-curve chin, 2-wide slope rings, '
               'bonded plate shelves and 3938 hinge tops; placed rotated about the hinge line')
    reg = {}

    def put(ref, x0, s0, w, d, base, origin_s=None, yaw=0, colour=BODY, height=24, kind=None, tag='ring'):
        """Place a rect-footprint part (origin at its top) and register its cells."""
        if kind:
            pid = rect(m, kind, x0, s0, w, d, base, colour)
        else:
            pid = m.add(ref, colour, x0 + w / 2, base + height,
                        Z(origin_s if origin_s is not None else s0 + d / 2), yaw=yaw)
        for i in range(w):
            for j in range(d):
                reg[(x0 + i, s0 + j)] = (tag, pid)

    def shelf(cells_, base):
        below = dict(reg)
        reg.clear()
        placed = field(m, cells_, base, BODY, prefer='x', key=lambda c: (c[1], abs(c[0] + .5)), below=below)
        reg.update(placed)
        m.step()

    def ring(front_ref, front_s, front_origin, front_d, corner_ref, corner_s, corner_d, side_s, base):
        """Front (2-wide slopes or a brick), corner columns x=-4/3 and side columns x=-5/4."""
        for x0 in (-3, -1, 1):
            if front_ref:
                put(front_ref, x0, front_s, 2, front_d, base, origin_s=front_origin)
        if not front_ref:
            put(None, -3, front_s, 6, 1, base, kind='brick')
        for x0 in (-4, 3):
            if corner_ref:
                put(corner_ref, x0, corner_s, 1, 2, base, origin_s=corner_s + 1.5)
                if corner_d > 2:
                    put(None, x0, corner_s + 2, 1, corner_d - 2, base, kind='brick')
            else:
                put(None, x0, corner_s, 1, corner_d, base, kind='brick')
        for x0 in (-5, 4):
            put(None, x0, side_s, 1, 7 - side_s, base, kind='brick')
        return {c for c in reg}

    def cells_of(front_s, front_d, corner_s, corner_d, side_s):
        return (cells(-3, 3, front_s, front_s + front_d) | {(x, s) for x in (-4, 3) for s in range(corner_s, corner_s + corner_d)}
                | {(x, s) for x in (-5, 4) for s in range(side_s, 7)})

    # Chin: inverted curves rising to the front, inverted 45s at the rounded corners, rear block.
    # Light grey chin continues the belly line and reads as the radome when raised.
    for x in range(-4, 4):
        put('13547', x, 1, 1, 4, KEEL[0], origin_s=4.5, colour=BELLY)
    for x in (-5, 4):
        put('3665b', x, 3, 1, 2, KEEL[0], origin_s=4.5, colour=BELLY)
    for x0, w in ((-5, 4), (-1, 4), (3, 2)):
        put(None, x0, 5, w, 2, KEEL[0], kind='brick')
    m.step()
    shelf(cells(-5, 5, 1, 7) - {(-5, 1), (-5, 2), (4, 1), (4, 2)}, 63)
    rings = [  # front ref, front s, origin, depth, corner ref, corner s, corner depth, side s, base
        ('3660b', 0, 1.5, 2, None, 1, 3, 3, 71),
        (None, 0, None, 1, None, 1, 3, 3, 103),
        ('3039', 0, 1.5, 2, '3040b', 1, 3, 3, 135),
        ('3039', 1, 2.5, 2, '3040b', 2, 3, 4, 167),
        ('3298', 2, 4.5, 3, '4286', 3, 3, 4, 199),
    ]
    for k, (fr, fs, fo, fd, cr, cs, cd, ss, base) in enumerate(rings):
        if cr == '4286':
            # 3x1 slopes: origin 2.5 studs behind the front edge.
            for x0 in (-3, -1, 1):
                put(fr, x0, fs, 2, fd, base, origin_s=fo)
            for x0 in (-4, 3):
                put(cr, x0, cs, 1, 3, base, origin_s=cs + 2.5)
            for x0 in (-5, 4):
                put(None, x0, ss, 1, 7 - ss, base, kind='brick')
        else:
            ring(fr, fs, fo, fd, cr, cs, cd, ss, base)
        if k < len(rings) - 1:
            nxt = rings[k + 1]
            here = cells_of(fs, fd, cs, cd, ss)
            above = cells_of(nxt[1], nxt[3], nxt[5], nxt[6], nxt[7])
            shelf(here | above, base + 24)
        else:
            m.step()
    for x in (-3, -1, 1, 3):
        put('3938', x - 1, HINGE_S, 2, 1, 199, origin_s=HINGE_S + .5, colour=DARK, yaw=180)
    m.step()
    top = cells(-5, 5, 4, 8) - {(-4, 4), (3, 4), (-5, 7), (4, 7)}
    shelf(top, 223)
    field(m, top - cells(-5, 5, 7, 8), 231, BODY, kind='tile', below=dict(reg))
    return m


def ramp():
    m = Module('an225-ramp', 'Forward loading ramp authored flat: 44301a hinge plates and plates, '
               'dark tiled deck with yellow edges; placed rotated down about the floor-lip hinge line')
    hinge_x = (-4, -2, 1, 3)
    for x in hinge_x:
        m.add('44301a', GEAR, x + .5, FLOOR + 8, Z(5), yaw=-90, id=f'ramp-hinge-{x + 4}')
    base = cells(-4, 4, RAMP_FRONT, 6) - {(x, s) for x in hinge_x for s in (4, 5)}
    below = field(m, base, FLOOR, GEAR, prefer='s')
    for x in hinge_x:
        below.update({(x, 4): ('hinge', x), (x, 5): ('hinge', x)})
    m.step()
    field(m, cells(-3, 3, RAMP_FRONT, 6), FLOOR + 8, DARK, kind='tile', below=below)
    for x in (-4, 3):
        field(m, cells(x, x + 1, RAMP_FRONT, 6), FLOOR + 8, MARK, kind='tile', below=below)
    return m


# ============================================================ flying surfaces
WEDGES = {
    '48205': dict(size=(4, 6), edge=((-40, 60), (20, -60))),
    '48208': dict(size=(4, 6), edge=((-20, -60), (40, 60))),
    '3545': dict(size=(3, 8), edge=((-30, 80), (10, -80))),
    '3544': dict(size=(3, 8), edge=((-10, -80), (30, 80))),
}


def wedge_place(m, target, line, colour, parts, h):
    """Choose the real wedge and yaw whose measured oblique edge lies on `line` inside `target`."""
    x0, x1, s0, s1 = target
    cx, cs = (x0 + x1) / 2, (s0 + s1) / 2
    want = [np.array(p, float) for p in line]
    best = None
    for ref in parts:
        spec = WEDGES[ref]
        for yaw in (0, 90, 180, 270):
            w, d = spec['size'] if yaw in (0, 180) else spec['size'][::-1]
            if abs(w - (x1 - x0)) > .01 or abs(d - (s1 - s0)) > .01:
                continue
            R = np.array(rotation('y', yaw).rows)
            pts = [np.array([cx, cs]) + (R @ np.array([px, 0, pz], float))[[0, 2]] / 20
                   for px, pz in spec['edge']]
            err = min(sum(np.linalg.norm(a - b) for a, b in zip(pts, want)),
                      sum(np.linalg.norm(a - b) for a, b in zip(pts[::-1], want)))
            if best is None or err < best[0]:
                best = (err, ref, yaw)
    if best is None or best[0] > .25:
        raise ValueError(f'no wedge matches {target} {line}: {best}')
    return m.add(best[1], colour, cx, h, Z(cs), yaw=best[2])


def surface(m, *, le0, xl, te0, xt, tip, base, colour, reserved=frozenset(), lights=None):
    """Two bonded layers: studded wedges on 1:2 LE / 1:4 TE lines, plates below, tiles above.

    The second layer's wedges are offset along the same edge lines (2 span/1 chord for the
    LE, 4 span/1 chord for the TE) so they bridge the first layer's wedge joints; its tiles
    are packed to bridge the first layer's plates. Beyond the second layer's span, the
    first layer's full cells (including wedge cells) are tiled with the same bonding rule.
    """
    def le(ax):
        return le0 + max(0, ax - xl) / 2

    def te(ax):
        return te0 + max(0, ax - xt) / 4

    def full(span):
        out = set()
        for x in range(-span, span):
            a_in, a_out = min(abs(x), abs(x + 1)), max(abs(x), abs(x + 1))
            for s in range(int(le0), int(te(span)) + 2):
                if s >= le(a_out) and s + 1 <= te(a_in):
                    out.add((x, s))
        return out

    below = {}
    for layer in (0, 1):
        b = base + 8 * layer
        span = tip - 4 * layer
        covered = {}
        for side in (-1, 1):
            for kind, a, step in (('le', xl + 2 * layer, 6), ('te', xt + 4 * layer, 8)):
                while a + step <= span:
                    z = a + step
                    if kind == 'le':
                        rs = (int(le(a)), int(le(a)) + 4)
                        line = [(side * a, le(a)), (side * z, le(z))]
                        parts = ('48205', '48208')
                    else:
                        rs = (int(round(te(z))) - 3, int(round(te(z))))
                        line = [(side * a, te(a)), (side * z, te(z))]
                        parts = ('3544', '3545')
                    xs = (a, z) if side > 0 else (-z, -a)
                    pid = wedge_place(m, (*xs, *rs), line, colour, parts, b + 8)
                    for c in cells(xs[0], xs[1], *rs):
                        covered[c] = (f'w{layer}', pid)
                    a = z
        inner = full(span) - set(covered)
        if layer == 0:
            placed = field(m, inner, b, colour, prefer='x', key=lambda c: (c[1], c[0]), tag='l0')
            below = {**covered, **placed}
        else:
            field(m, inner, b, colour, prefer='s', key=lambda c: (c[1], c[0]), kind='tile', below=below)
        m.step()
    span1 = tip - 4
    exposed = {c for c in full(tip) if c[0] >= span1 or c[0] < -span1} - set(reserved) - set(lights or {})
    field(m, exposed, base + 8, colour, kind='tile', below=below)
    for c, colour_ in (lights or {}).items():
        m.add('3070b', colour_, c[0] + .5, base + 16, Z(c[1]) + .5, purpose='navigation light tile')


def wing():
    m = Module('an225-wing', 'High swept wing flush with the roof (underside Y=-239): studded 1:2 LE '
               'and 1:4 TE wedges, plate core, tiled top, trans-red/green tip lights')
    surface(m, le0=WING_LE, xl=5, te0=WING_TE, xt=5, tip=53, base=SKIN, colour=WING,
            lights={(52, 57): STBD_LAMP, (-53, 57): PORT_LAMP})
    return m


def tail():
    m = Module('an225-tail', 'H-tail: two-layer swept stabiliser on the rear roof and twin 54094 '
               'endplate fins on the stabiliser tips')
    fins = {(x, s) for x in (-21, -20, 19, 20) for s in range(90, 104)}
    surface(m, le0=STAB_LE, xl=3, te0=STAB_TE, xt=5, tip=21, base=SKIN, colour=WING, reserved=fins)
    for x, name in ((-20, 'port'), (20, 'starboard')):
        # 54094: studs at the fin tip, base underside 192 below its origin, sweeping to +Z.
        m.add('54094', BODY, x, SKIN + 8 + 192, Z(103), id=f'fin-{name}')
        # Flag cap on the fin-tip studs: yellow plate under a blue tile.
        m.add('3022', PIN, x, SKIN + 8 + 192 + 8, Z(103), id=f'fin-flag-yellow-{name}')
        m.add('3068b', CHEAT, x, SKIN + 8 + 192 + 16, Z(103), id=f'fin-flag-blue-{name}')
    return m


def engine():
    m = Module('an225-engine', 'D-18T nacelle: dedicated 43121 jet engine hanging from a 2x6 pylon '
               'plate; mount anchor is the pylon top (wing underside), inlet -Z')
    m.add('3795', WING, 0, 8, -.5, yaw=90, id='pylon')
    m.add('3068b', WING, 0, 16, -2.5, id='pylon-fairing')  # clear of the LE wedge line
    m.add('43121', BODY, 0, 0, -1.5, id='nacelle')  # studs at z=-3..0 under the pylon sockets
    m.anchor('mount', h=8)
    return m


def details():
    m = Module('an225-details', 'Buran carrier mounting pylons on the roof centre plates')
    for s in BURAN:
        for x in (-1.5, 1.5):
            m.add('3062b', DARK, x, SKIN + 8 + 24, Z(s) + .5)
    return m


# ============================================================ assembly
def assembly():
    root = Module('an225-mriya', 'Antonov An-225 Mriya at about 1:100, parked on 32 wheels with the '
                  'nose visor raised and ramp lowered; X across, -Z forward, ground Y=0')
    root.add(keel(), 16, id='keel')
    root.add(fuselage(), 16, id='fuselage')
    root.add(sponsons(), 16, id='sponsons')
    root.add(aft(), 16, id='aft-fuselage')
    root.add(cockpit(), 16, id='cockpit')
    root.add(hold(), 16, id='hold')
    for name in CONTAINERS:
        root.add(container(name), 16, id=f'container-{name}')
    root.step()
    gear = main_gear()
    for side, name in ((-1, 'port'), (1, 'starboard')):
        root.add(gear, 16, side * 4, 0, Z(MAIN_GEAR_S), id=f'main-gear-{name}')
    leg = nose_leg()
    for side, name in ((-1, 'port'), (1, 'starboard')):
        root.add(leg, 16, side * 2, 0, Z(NOSE_GEAR_S) + 1, id=f'nose-leg-{name}')
    root.step()
    root.add(wing(), 16, id='wing')
    eng = engine()
    for side, name in ((-1, 'port'), (1, 'starboard')):
        for k, ax in enumerate(ENGINES):
            s_le = WING_LE + (ax - 5) / 2
            root.add(eng, 16, side * ax, SKIN - 8, Z(s_le), id=f'engine-{name}-{k + 1}')
    root.add(tail(), 16, id='tail')
    root.add(details(), 16, id='buran-pylons')
    root.step()
    hinged(root, visor(), *VISOR_AXIS, VISOR_DEG, 'nose-visor')
    hinged(root, ramp(), *RAMP_AXIS, ramp_angle(), 'loading-ramp')
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--plan', type=Path, default=OUT / 'an225-mriya.plan.json')
    parser.add_argument('--closed', action='store_true', help='author the visor/ramp closed (review aid)')
    args = parser.parse_args()
    global VISOR_DEG, ramp_angle
    if args.closed:
        VISOR_DEG = 0
        ramp_angle = lambda: 0.0  # noqa: E731
        globals()['ramp_toe_height'] = lambda: None
    plan = assembly().plan()
    plan['author'] = AUTHOR
    args.plan.write_text(json.dumps(plan, indent=1) + '\n')
    count = sum(len(step) for sec in plan['sections'] for step in sec['steps'])
    print(f'wrote {args.plan} ({len(plan["sections"])} sections, {count} placements before expansion); '
          f'ramp {ramp_angle()} deg (toe {ramp_toe_height()} LDU above ground), visor {VISOR_DEG} deg')


if __name__ == '__main__':
    main()
