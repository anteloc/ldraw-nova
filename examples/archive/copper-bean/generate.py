"""The Copper Bean: three storeys of apartments over a corner coffee shop.

Writes an editable JSON plan; build it with `./ldraw-agent build`. Authoring
coordinates follow ldraw_tools.architecture: X/Z in studs, h in LDU upwards,
every module has bottom Y=0 and faces -Z. No OMR geometry is copied; the
minifigure stack below is measured from this library's own connector frames.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from ldraw_tools.architecture import (
    Module, slab, line, ring, window4, door4, display4,
    lamp, bench, planter,
)

# ---- measured with `ldraw-agent part` against the installed library --------
# 3815b hips carry pins at (+-2,12,0); 3816c/3817c legs have the matching
# pin holes at (-+2,0,0), so the legs sit 12 LDU below the hips origin.
# 973 torso pin holes (+-10,32,0) meet the hips pins (+-10,0,0): 32 above.
# 3626b head sits 25 above the torso origin and hair shares the head origin.
# Seated: the legs take a proper -90 degree rotation about the figure's own X.
# The hips underside and the rotated thigh underside then share one plane
# 20.75 LDU below the hips origin, which is the seat.
# 3819 (left arm) is a mirrored reference to 3818 and its shadow connection
# frames are rejected under reflection, so 43368/43369 (arm with integral
# hand, each with its own geometry) are used instead.
HIPS_TO_LEGS = 12
HIPS_TO_TORSO = 32
HIPS_TO_HEAD = 57
SHOULDER_X = 15.552 / 20          # 973c01 seats both arms at this offset
SHOULDER_DROP = 9
STANDING_HIPS = 40                # 3816c foot bottom is 28 below its origin
SEATED_HIPS = 20.75
ARM_SWING = -60                   # clears the horizontal thighs of a sitter
SIT = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]      # proper rotation, det = +1
SNOT = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]     # upright tile on side studs

AUTHOR = 'ldraw-nova copper-bean generator'
ROOT = Path(__file__).resolve().parent

C = dict(
    shop=288,        # Dark_Green shopfront, awning and parasol
    body=19,         # Tan apartment walls
    trim=15,         # White frames, cornices, balustrades, parapet
    floor=70,        # Reddish_Brown decks and café furniture
    roof=72,         # Dark_Bluish_Grey roof surface, road, table frame
    paving=71,       # Light_Bluish_Grey pavement
    terrace=28,      # Dark_Tan café decking
    lawn=2,          # Green side gardens
    glass=47,
    flower=4,
    skin=14,
)

BUILDING_Z = 5       # building centre; its front face lands on stud line -1


# ---------------------------------------------------------------- maths


def rot(axis, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return {'x': [[1, 0, 0], [0, c, -s], [0, s, c]],
            'y': [[c, 0, s], [0, 1, 0], [-s, 0, c]],
            'z': [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]


def compose(a, b):
    return [[round(sum(a[i][k] * b[k][j] for k in range(3)), 6) for j in range(3)]
            for i in range(3)]


# ---------------------------------------------------------------- helpers


def run(m, x, z, n, h, colour, *, axis='x', bond=False, blocked=()):
    """One wall course of n cells, skipping the reserved opening cells."""
    i = 0
    while i < n:
        if i in blocked:
            i += 1
            continue
        end = i + 1
        while end < n and end not in blocked:
            end += 1
        if axis == 'x':
            line(m, x + i, z, end - i, h, colour, bond=bond)
        else:
            line(m, x, z + i, end - i, h, colour, axis='z', bond=bond)
        i = end


def cells(n, centre, width):
    """Cell indices of an opening `width` studs wide centred on `centre`."""
    lower = -n / 2
    return {i for i in range(n) if centre - width / 2 <= lower + i < centre + width / 2}


def crown(m, w, d, h, trim, *, project=2):
    """Cornice ring: `project` studs at the front, one stud on flank and rear.

    Every plate keeps at least one stud row over the wall head and is clamped
    by the storey deck above, so nothing in the ring is a free cantilever.
    """
    for x in range(-w // 2 + 1, w // 2, 2):
        m.add('3021', trim, x, h, -d / 2 - project / 2 + .5, yaw=90,
              purpose='Front string course; its rear stud row bears on the wall')
        m.add('3022', trim, x, h, d / 2, purpose='Rear cornice, half over the wall')
    for x in [-w / 2, w / 2]:
        for z in range(-d // 2 + 2, d // 2 - 1, 2):
            m.add('3022', trim, x, h, z, purpose='Flank cornice, half over the wall')


# ---------------------------------------------------------------- building


def shop(name, w=16, d=12, *, rows=8, sign='3068bp25'):
    """Ground floor: two display bays, a glazed entrance, sign fascia, awning.

    Courses 0-5 carry the 144 LDU glazing; courses 6-7 form the sign band, so
    the printed tile clears the door head instead of straddling it.
    """
    m = Module(name, f'{w} by {d} stud coffee shop: full-height display glazing, '
                     'central entrance, printed sign fascia, projecting cornice '
                     'and a striped awning')
    body, trim = C['shop'], C['trim']
    slab(m, -w / 2, -d / 2, w, d, 8, C['floor'])
    glazing = cells(w, -5, 4) | cells(w, 0, 4) | cells(w, 5, 4)
    fascia = cells(w, 0, 6)
    flank = cells(d - 2, -3, 4) | cells(d - 2, 3, 4)
    back_door = cells(w, -4, 4)
    back_window = cells(w, 4, 4)
    for row in range(rows):
        m.step()
        h = 8 + 24 * (row + 1)
        course = C['roof'] if row == 0 else body
        run(m, -w / 2, -d / 2 + .5, w, h, course, bond=bool(row % 2),
            blocked=glazing if row < 6 else (fascia if row == rows - 1 else set()))
        run(m, -w / 2, d / 2 - .5, w, h, course, bond=bool(row % 2),
            blocked=(back_door if row < 6 else set())
                    | (back_window if 2 <= row <= 4 else set()))
        for x in [-w / 2 + .5, w / 2 - .5]:
            run(m, x, -d / 2 + 1, d - 2, h, course, axis='z', bond=bool(row % 2),
                blocked=flank if 2 <= row <= 4 else ())
    m.step()
    for x in [-5, 5]:
        m.add(display4(trim), trim, x, 8, -d / 2 + .5,
              purpose='Full-height fixed display glazing in reserved cells')
    m.add(door4(trim, trim, 'glazed'), trim, 0, 8, -d / 2 + .5, purpose='Shop entrance')
    m.add(door4(trim, C['floor'], 'traditional'), trim, -4, 8, d / 2 - .5, yaw=180,
          purpose='Service door onto the rear garden')
    for z in [-3, 3]:
        m.add(window4(trim, C['glass']), trim, -w / 2 + .5, 56, z, yaw=90)
        m.add(window4(trim, C['glass']), trim, w / 2 - .5, 56, z, yaw=-90)
    m.add(window4(trim, C['glass']), trim, 4, 56, d / 2 - .5, yaw=180)
    m.step()
    # Interior: service counter, espresso machine and two window tables, all
    # visible through the display glazing.
    line(m, -6, 3.5, 6, 32, C['floor'])
    slab(m, -6, 3, 4, 1, 40, trim, tile=True)
    m.add('3023b', trim, -1, 40, 3.5, purpose='Plate run under the espresso machine')
    for x in [-1.5, -.5]:
        m.add('3062b', C['roof'], x, 64, 3.5)
        m.add('3024', trim, x, 72, 3.5)
    for z in [-2, 2]:
        m.add('3062b', C['roof'], 3.5, 32, z + .5)
        m.add('3062b', C['roof'], 3.5, 56, z + .5)
        m.add('4032a', trim, 3, 64, z, purpose='Pedestal table beside the glazing')
        for sx in [1.5, 5.5]:
            m.add('3062b', C['floor'], sx, 32, z + .5)
            m.add('3024', C['floor'], sx, 40, z + .5)
    m.step()
    head = 8 + 24 * rows
    for x in [-2, 0, 2]:
        m.add('11211', body, x, head, -d / 2 + .5,
              purpose='Side studs face -Z and carry one panel of the sign board')
        m.add(sign if x == 0 else '3068b', trim, x, head - 20, -d / 2 - .4,
              matrix=SNOT,
              purpose='Printed coffee-cup tile' if x == 0 else 'Sign board panel')
    m.step()
    crown(m, w, d, head + 8, trim)
    m.step()
    for i, x in enumerate(range(-w // 2 + 1, w // 2, 2)):
        m.add('3039', trim if i % 2 else C['shop'], x, head + 32, -d / 2 - .5,
              purpose='Awning stripe; 3039 sockets sit on the cornice stud grid')
    m.anchor('roof', h=head + 8).anchor('doorstep', 0, 8, -d / 2)
    return m


def storey(name, w=16, d=12, *, rows=6, windows=(-5, 0, 5), door=None,
           balustrade=False):
    """One apartment floor, its cornice, and an optional balcony balustrade."""
    m = Module(name, f'{w} by {d} stud apartment storey: reserved window bays, '
                     'projecting cornice and a lift-off floor interface')
    body, trim = C['body'], C['trim']
    slab(m, -w / 2, -d / 2, w, d, 8, C['floor'])
    bays = set()
    for x in windows:
        bays |= cells(w, x, 4)
    doorway = cells(w, door, 4) if door is not None else set()
    flank = cells(d - 2, -3, 4) | cells(d - 2, 3, 4)
    rear = cells(w, -4, 4) | cells(w, 4, 4)
    for row in range(rows):
        m.step()
        h = 8 + 24 * (row + 1)
        band = 2 <= row <= 4
        blocked = set(doorway) | (bays if band else set())
        run(m, -w / 2, -d / 2 + .5, w, h, body, bond=bool(row % 2), blocked=blocked)
        run(m, -w / 2, d / 2 - .5, w, h, body, bond=bool(row % 2),
            blocked=rear if band else ())
        for x in [-w / 2 + .5, w / 2 - .5]:
            run(m, x, -d / 2 + 1, d - 2, h, body, axis='z', bond=bool(row % 2),
                blocked=flank if band else ())
    m.step()
    for x in windows:
        m.add(window4(trim, C['glass']), trim, x, 56, -d / 2 + .5)
    if door is not None:
        m.add(door4(trim, trim, 'glazed'), trim, door, 8, -d / 2 + .5,
              purpose='French door onto the balcony formed by the cornice below')
    for z in [-3, 3]:
        m.add(window4(trim, C['glass']), trim, -w / 2 + .5, 56, z, yaw=90)
        m.add(window4(trim, C['glass']), trim, w / 2 - .5, 56, z, yaw=-90)
    for x in [-4, 4]:
        m.add(window4(trim, C['glass']), trim, x, 56, d / 2 - .5, yaw=180)
    m.step()
    head = 8 + 24 * rows
    crown(m, w, d, head + 8, trim)
    if balustrade:
        m.step()
        for x in range(-w // 2 + 2, w // 2, 4):
            m.add('3633', trim, x, head + 32, -d / 2 - 1.5,
                  purpose='Balcony lattice; all four posts stand on cornice studs')
        for x in [-7.5, 7.5]:
            m.add('3062b', C['floor'], x, head + 32, -d / 2 - .5)
            m.add('24866', C['flower'], x, head + 40, -d / 2 - .5,
                  purpose='Balcony flower pot behind the railing')
    m.anchor('roof', h=head + 8)
    return m


def roof(name, w=16, d=12):
    """Lift-off roof: parapet, tiled terrace and a studded service bay."""
    m = Module(name, 'Lift-off flat roof: parapet, quiet tiled terrace and a '
                     'studded service bay with stair head, chimney and planting')
    trim = C['trim']
    slab(m, -w / 2, -d / 2, w, d, 8, trim)
    ring(m, w, d, 32, trim, plate=False)
    ring(m, w, d, 40, trim)
    slab(m, -w / 2 + 1, -d / 2 + 1, 10, d - 2, 16, C['roof'], tile=True)
    m.step()
    for row in range(3):
        h = 8 + 24 * (row + 1)
        run(m, 3, 1.5, 3, h, C['body'])
        run(m, 3, 3.5, 3, h, C['body'])
        for x in [3.5, 5.5]:
            run(m, x, 2, 1, h, C['body'], axis='z')
    slab(m, 3, 1, 3, 3, 88, trim, tile=True)
    m.step()
    for row in range(4):
        m.add('3003', C['floor'], 5, 8 + 24 * (row + 1), -1)
    m.add('3022', C['roof'], 5, 112, -1, purpose='Chimney cap')
    m.add(planter(C['flower']), C['flower'], 5, 8, -4,
          purpose='Roof planting on the studded service bay')
    return m


# ---------------------------------------------------------------- figures


def minifig(name, *, torso, legs, hair, hair_ref='3901', head='3626bp01',
            seated=True):
    """One assembled minifigure; bottom Y=0 is the seat plane or the pavement."""
    base = SEATED_HIPS if seated else STANDING_HIPS
    m = Module(name, 'Seated minifigure: hips and thighs bear on one seat plane'
                     if seated else 'Standing minifigure on a stud surface')
    m.add('3815b', legs, 0, base, 0, purpose='Hips set the whole figure datum')
    for ref in ['3816c', '3817c']:
        m.add(ref, legs, 0, base - HIPS_TO_LEGS, 0,
              **({'matrix': SIT} if seated else {}))
    m.add('973', torso, 0, base + HIPS_TO_TORSO, 0)
    swing = ARM_SWING if seated else 0
    m.add('43368', torso, -SHOULDER_X, base + HIPS_TO_TORSO - SHOULDER_DROP, 0,
          matrix=compose(rot('z', 9.79), rot('x', swing)),
          purpose='Right arm swung clear of the horizontal thigh')
    m.add('43369', torso, SHOULDER_X, base + HIPS_TO_TORSO - SHOULDER_DROP, 0,
          matrix=compose(rot('z', -9.79), rot('x', swing)))
    m.add(head, C['skin'], 0, base + HIPS_TO_HEAD, 0)
    m.add(hair_ref, hair, 0, base + HIPS_TO_HEAD, 0,
          purpose='Hair shares the head origin and grips its stud')
    return m


def cafe_chair(name='cafe-chair'):
    """Two by three stud bistro chair; smooth seat top at 32 LDU, front -Z."""
    m = Module(name, 'Bistro chair: one 2x3 base plate ties the seat block to '
                     'the back frame; smooth seat top at 40 LDU, front -Z')
    m.add('3021', C['trim'], 0, 8, .5, yaw=90,
          purpose='Single base plate so seat and back frame are one object')
    m.add('3003', C['trim'], 0, 32, 0)
    m.add('3068b', C['floor'], 0, 40, 0, purpose='Smooth seat so the hips bear flat')
    m.add('3004', C['trim'], 0, 32, 1.5)
    m.add('3004', C['trim'], 0, 56, 1.5)
    m.add('3023b', C['floor'], 0, 64, 1.5, purpose='Back rail below shoulder height')
    m.anchor('seat', 0, 40, 0)
    return m


def cafe_table(name='cafe-table'):
    """Five by four stud terrace table pierced for the parasol mast.

    The local origin is the mast axis. A one by two stud void keeps 10 LDU of
    clearance round the 10 LDU mast; four round legs stand on deck studs.
    """
    m = Module(name, 'Terrace table pierced for a parasol mast: four round legs '
                     'on real studs, top surface 64 LDU above its own base')
    for x in [-2, 2]:
        for z in [-1.5, 1.5]:
            m.add('3062b', C['trim'], x, 24, z)
            m.add('3062b', C['trim'], x, 48, z)
    m.step()
    for z in [-1.5, 1.5]:
        m.add('3710', C['trim'], -.5, 56, z,
              purpose='Rail on the left leg; its centre stud carries the middle plate')
        m.add('3024', C['trim'], 2, 56, z, purpose='Cap on the right leg')
    m.step()
    m.add('3020', C['floor'], -1.5, 64, 0, yaw=90, purpose='Left half of the top')
    m.add('3020', C['floor'], 1.5, 64, 0, yaw=90, purpose='Right half of the top')
    m.add('3024', C['floor'], 0, 64, -1.5, purpose='Centre plate on the front rail')
    m.add('3024', C['floor'], 0, 64, 1.5, purpose='Centre plate on the rear rail')
    m.anchor('top', 0, 64, 0)
    return m


def terrace(name='bean-terrace'):
    """The whole parasol group; local origin is the mast axis, bottom Y=0.

    Chairs and table stand on the deck studs below; each guest bears on the
    chair seat 32 LDU up, so the figures form their own connected objects.
    """
    m = Module(name, 'Pavement café: pierced table, three bistro chairs, three '
                     'seated guests with coffee, under a complete 8x8 parasol')
    m.add('958c01', C['shop'], 0, 0, 0, id='parasol',
          purpose='Complete parasol; its round stand grips six deck studs')
    m.add(cafe_table(), C['trim'], 0, 0, 0, id='table')
    chair = cafe_chair()
    guests = [('left', -3.5, 0, -90, 320, 0, 70, '3901'),
              ('right', 3.5, 0, 90, 1, 72, 0, '6093a'),
              ('front', -.5, -3, 180, 25, 70, 28, '43751')]
    for label, x, z, yaw, torso, legs, hair, hair_ref in guests:
        m.add(chair, C['floor'], x, 0, z, yaw=yaw, id=f'chair-{label}')
        m.add(minifig(f'bean-guest-{label}', torso=torso, legs=legs, hair=hair,
                      hair_ref=hair_ref), C['skin'], x, 40, z, yaw=yaw,
              id=f'guest-{label}',
              purpose='Bears on the chair seat below; a figure is its own object')
    m.step()
    for x, z in [(-2, .5), (2, .5), (0, -1.5)]:
        m.add('3899', C['trim'], x, 88, z, purpose='Coffee, one cup per guest')
    m.add('6141', C['trim'], -1, 72, -.5)
    m.add('24866', C['flower'], -1, 80, -.5, purpose='Table posy')
    m.anchor('mast', 0, 0, 0)
    return m


def street_tree(leaf=2, blossom=5):
    """Compact street tree, 168 LDU tall; bottom Y=0, four stud plinth.

    Shorter and denser than the atlas garden tree so it does not out-scale the
    shopfront. Reserve the nine stud canopy clearing, not only the plinth.
    """
    m = Module(f'street-tree-{leaf}-{blossom}',
               'Compact street tree: earth plinth, round trunk and three leaf tiers')
    slab(m, -2, -2, 4, 4, 8, C['lawn'])
    slab(m, -1, -1, 2, 2, 16, C['floor'])
    for i in range(3):
        m.add('3062b', C['floor'], -.5, 40 + 24 * i, -.5)
    m.add('2417', leaf, -.5, 96, -.5)
    m.add('3062b', C['floor'], -.5, 120, -.5)
    m.add('2417', leaf, -.5, 128, -.5, yaw=90)
    m.add('3062b', C['floor'], -.5, 152, -.5)
    m.add('2423', blossom, -.5, 160, -.5, yaw=180)
    m.add('2423', leaf, -.5, 168, -.5)
    for x in [-1.5, .5, 1.5]:
        m.add('24866', blossom, x, 16, -1.5)
    return m


def flowers(m, spots, h=8, colour=4, stem=2):
    for x, z in spots:
        m.add('3062b', stem, x, h + 24, z)
        m.add('24866', colour, x, h + 32, z)


# ---------------------------------------------------------------- scene


def paving(m, x0, z0, w, d, colour, *, h=8, reserved=()):
    """One stud paving lattice; reserved rectangles stay bare for fixtures."""
    laid = getattr(m, '_laid', set())
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + d):
            if any(a <= x < a + cw and b <= z < b + cd for a, b, cw, cd in reserved):
                continue
            if (x, z) in laid:
                continue
            m.add('3070b', colour, x + .5, h, z + .5)
            laid.add((x, z))
    m._laid = laid


def scene():
    m = Module('copper-bean', 'The Copper Bean: three storeys of apartments over '
                              'a corner coffee shop, with a parasol terrace on '
                              'the pavement')
    m.add('3811', C['paving'], id='site',
          purpose='32x32 stud site; every footprint is reserved before paving')

    # -- building stack -------------------------------------------------
    ground = shop('bean-shop')
    first = storey('bean-flat-one', windows=(-5, 0, 5), balustrade=True)
    second = storey('bean-flat-two', windows=(-6, 6), door=0)
    m.add(ground, C['shop'], 0, 0, BUILDING_Z, id='shop')
    m.add(first, C['body'], id='flat-one',
          attach={'to': 'shop', 'anchor': 'roof', 'using': 'base'})
    m.add(second, C['body'], id='flat-two',
          attach={'to': 'flat-one', 'anchor': 'roof', 'using': 'base'})
    m.add(roof('bean-roof'), C['trim'], id='roof',
          attach={'to': 'flat-two', 'anchor': 'roof', 'using': 'base'})

    # -- ground surfaces -------------------------------------------------
    m.step()
    reserved = [(-10, -13, 16, 12),              # café terrace deck
                (-16, -14, 32, 1),               # kerb course
                (10, -8, 4, 4), (-15, -8, 4, 4),  # tree plinths
                (6, -13, 2, 2), (-13, -13, 2, 2),  # lampposts
                (6, -5, 4, 2), (-14, -4, 4, 2)]  # benches
    paving(m, -16, -14, 32, 13, C['paving'], reserved=reserved)
    slab(m, -16, -16, 32, 2, 8, C['roof'], tile=True)
    line(m, -16, -13.5, 32, 8, C['trim'], plate=True)
    slab(m, -10, -13, 16, 12, 8, C['terrace'])
    slab(m, -16, -1, 8, 17, 8, C['lawn'])
    slab(m, 8, -1, 8, 17, 8, C['lawn'])
    slab(m, -8, 11, 16, 5, 8, C['lawn'])

    # -- pavement café ------------------------------------------------------
    m.step()
    m.add(terrace(), C['trim'], -4.5, 8, -8, id='cafe-terrace',
          purpose='Parasol group; its own origin is the parasol mast axis')

    # -- street furniture ---------------------------------------------------
    m.step()
    m.add(street_tree(288, 5), C['lawn'], 12, 0, -6)
    m.add(street_tree(2, 14), C['lawn'], -13, 0, -6)
    m.add(lamp(), 0, 7, 0, -12)
    m.add(lamp(), 0, -12, 0, -12)
    m.add(bench(C['floor']), C['floor'], 8, 0, -4, yaw=180)
    m.add(bench(C['floor']), C['floor'], -12, 0, -3, yaw=180)
    m.add(planter(C['flower']), C['flower'], -7, 8, -2,
          purpose='Flower box on the terrace beside the entrance')
    m.add(planter(14), 14, 3, 8, -2)

    # -- rear garden: service path, planting and a quiet seat ---------------
    m.step()
    slab(m, 8, -1, 3, 14, 16, C['paving'], tile=True)
    slab(m, -6, 11, 14, 2, 16, C['paving'], tile=True)
    m.add(street_tree(2, 4), C['lawn'], 13, 8, 4)
    m.add(street_tree(288, 14), C['lawn'], -12, 8, 6)
    m.add(bench(C['floor']), C['floor'], 13, 8, 9, yaw=90,
          purpose='Garden seat facing the building across the path')
    m.add(planter(5), 5, -4, 8, 14, purpose='Bed beside the service door')
    m.add(planter(14), 14, 2, 8, 14)
    flowers(m, [(10.5, 13.5), (11.5, 14.5), (13.5, 13.5), (-9.5, 12.5),
                (-14.5, 2.5), (-13.5, 10.5), (-10.5, 0.5), (11.5, 0.5)])
    return m


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=ROOT)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    plan = scene().plan()
    plan['author'] = AUTHOR
    path = args.outdir / 'copper-bean.plan.json'
    path.write_text(json.dumps(plan, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
