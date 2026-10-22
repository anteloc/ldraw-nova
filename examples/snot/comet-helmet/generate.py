"""Comet: a 1950s pulp sci-fi astronaut helmet in SNOT, with LSynth ribbed hoses to twin air tanks.

Run from the repository root:

    .venv/bin/python examples/snot/comet-helmet/generate.py
    ./ldraw-agent flex build examples/snot/comet-helmet/hoses.ldr \
        --output examples/snot/comet-helmet/hoses.mpd --namespace comet-hoses --force
    ./ldraw-agent review examples/snot/comet-helmet/comet.plan.json --outdir output/comet-review --contacts all

The generator writes the plan and the hose constraint source. Both use the same port and valve
constants, so a moved port also moves its hose end. `--tune` (needs lsynth-nova) searches each
hose's final lead-in for a segment chain that ends flush on its port stud.

World axes: X is width (the helmet's right is +X), -Z is forward (the face), -Y is up, and Y=0 is
the display base's top surface. The helmet section has its own frame: Y=0 is the shell underside.
Every sideways module is seated with origin = stud - R * socket, using inspected connector positions.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for parent in HERE.parents:
    if (parent / 'ldraw_tools').is_dir():
        sys.path.insert(0, str(parent))
        break

from ldraw_tools.builder import rotation  # noqa: E402

AUTHOR = 'Comet generator (Claude Code, Claude Opus 5.5) for anteloc'

# Palette roles (LDraw codes)
SHELL, ACCENT, METAL, GLASS = 15, 4, 179, 40       # white, red, flat (pearl) silver, trans-black
BASE, FRAME, GOLD, HOSE = 0, 72, 297, 0            # black, dark bluish grey, pearl gold, black hose

# --- helmet frame: part origins (body tops); Y=0 is the shell underside ------------------------------
B0, C1, P1, C2, P2 = -8, -32, -40, -64, -72        # floor plate, course, plate, course, plate
S_TOP = -112                                       # SNOT course: 32952 bricks span -72..-112
S_ARC, S_PLATE = -96, (-104, -112)                 # its corner columns: one 48092 and two 30565
P3, C4, PTOP = -120, -144, -152                    # plate, course, top plate
SIDE_ROWS = (S_TOP + 10, S_TOP + 30)               # 32952 side studs, 10 and 30 below its top
FACE_Y = sum(SIDE_ROWS) / 2                        # centre of each 2 x 4 side-stud field
TIER1, TIER2, DOME = -176, -200, -240              # crown: outer tier and riser, inner tier, dome
FACE = 120                                         # flat faces; corners are r=80 arcs about (+-40, +-40)

# --- world frame -----------------------------------------------------------------------------------
COLUMN = 4                                         # 87081 round bricks under the collar
HELMET_Y = -24 * COLUMN - 24 - 8                   # collar 18897 + 74611, then the shell underside
TANK_X, TANK_Z = 40, 200                           # tank centres (+-40, 200): 4 x 4 parts need even 20s
TANK_COURSES = (2, 3)                              # 87081 bricks below and above the strap plate
STRAP_Y = -8 - 24 * TANK_COURSES[0]               # tank feet stand in an 8 LDU tile recess
VALVE_Y = STRAP_Y - 24 * TANK_COURSES[1] - 8 - 48 - 24  # band, cone 3943b, then the 30367c valve's stud base

FACES = {'front': (0, 0, -1), 'right': (1, 0, 0), 'back': (0, 0, 1), 'left': (-1, 0, 0)}
QUADRANTS = ((1, -1), (-1, -1), (1, 1), (-1, 1))
QUAD_YAW = {(1, -1): 0, (-1, -1): 90, (1, 1): -90, (-1, 1): 180}   # arcs face (+x, -z) unrotated
QNAME = {(1, -1): 'fr', (-1, -1): 'fl', (1, 1): 'br', (-1, 1): 'bl'}  # front/back, right/left
SIDE = {1: 'r', -1: 'l'}
FACE_YAW = {(0, 0, -1): 0, (1, 0, 0): -90, (0, 0, 1): 180, (-1, 0, 0): 90}  # local -Z faces outward


def Ry(degrees):
    return np.array(rotation('y', degrees).rows, float)


def orient(up, along):
    """Proper rotation sending the part's local up (-Y) to `up` and its local +X to `along`."""
    x = np.array(along, float)
    y = -np.array(up, float)
    r = np.column_stack([x, y, np.cross(x, y)])
    assert np.allclose(r.T @ r, np.eye(3)) and np.isclose(np.linalg.det(r), 1)
    return r


def seat(r, socket, stud):
    """Part origin placing its local `socket` exactly on the target `stud` base."""
    return np.array(stud, float) - r @ np.array(socket, float)


def clean(v):
    out = float(round(float(v), 9))
    return 0.0 if out == 0 else out


class Section:
    def __init__(self, name, description):
        self.name, self.description, self.steps = name, description, []

    def step(self):
        self.steps.append([])
        return self

    def add(self, id, ref, colour, at, r=None, purpose=None):
        ref = ref if ref.endswith(('.dat', '.ldr')) else ref + '.dat'
        entry = dict(id=id, ref=ref, colour=colour, at=[clean(v) for v in at])
        if r is not None and not np.allclose(r, np.eye(3)):
            entry['matrix'] = [[clean(v) for v in row] for row in np.asarray(r)]
        if purpose:
            entry['purpose'] = purpose
        if not self.steps:
            self.step()
        self.steps[-1].append(entry)
        return entry

    def box(self, id, ref, colour, x0, x1, z0, z1, top, purpose=None):
        """Upright rectangular part covering [x0,x1] x [z0,z1] with its origin (body top) at `top`."""
        nx, nz = DIMS[ref]
        w, d = (x1 - x0) / 20, (z1 - z0) / 20
        if (w, d) == (nx, nz):
            r = None
        elif (w, d) == (nz, nx):
            r = Ry(90)
        else:
            raise ValueError(f'{id}: {ref} is {nx}x{nz}, not {w}x{d}')
        return self.add(id, ref, colour, [(x0 + x1) / 2, top, (z0 + z1) / 2], r, purpose)

    def plan(self):
        return dict(name=self.name, description=self.description, steps=[s for s in self.steps if s])


# x_studs (local X) and z_studs (local Z) of the upright rectangular parts used with Section.box.
DIMS = {'3001': (4, 2), '3005': (1, 1), '3010': (4, 1), '3020': (4, 2), '3029': (12, 4), '3031': (4, 4),
        '3035': (8, 4), '91405': (16, 16), '2412b': (2, 1), '6636': (6, 1), '2431': (4, 1), '3069b': (2, 1),
        '4162': (8, 1), '87079': (4, 2), '6934': (6, 3), '1751': (4, 4), '6320': (8, 6), '3795': (6, 2), '69729': (6, 2)}


def tangent(d):
    """Horizontal direction along a face whose outward normal is d."""
    return np.array([abs(d[2]), 0, abs(d[0])], float)


# --- helmet: shell ---------------------------------------------------------------------------------

def plate_layer(s, name, top):
    """Full 12 x 12 plate layer: four 6003 quadrants with r=80 round corners, split on the axes.

    Each quadrant covers its corner arc and half of two straights. The 48092 arcs only clutch upward
    in the connector data, so this is what joins every corner column to the rest of the shell; the
    straights, which cross the axes, bond the quadrants to one another in every course.
    """
    for sx, sz in QUADRANTS:
        s.add(f'{name}-{QNAME[sx, sz]}', '6003', SHELL, [60 * sx, top, 60 * sz], Ry(QUAD_YAW[sx, sz]),
              '6 x 6 quadrant with the r=80 round corner')


def course(s, name, top, colour=SHELL):
    """One brick course: four 48092 r=80 arcs and four 1 x 4 straights."""
    for sx, sz in QUADRANTS:
        s.add(f'{name}-arc{QNAME[sx, sz]}', '48092', colour, [40 * sx, top, 40 * sz], Ry(QUAD_YAW[sx, sz]))
    for face, d in FACES.items():
        s.add(f'{name}-{face}', '3010', colour, np.array(d) * (FACE - 10) + [0, top, 0], None if d[0] == 0 else Ry(90))


def shell():
    """Hollow 12 x 12 shell with r=80 corners and one SNOT course exposing a 2 x 4 stud field per face."""
    s = Section('comet-shell.ldr', 'Comet helmet shell: alternating plate layers, r=80 corner courses, SNOT course')
    s.step()
    plate_layer(s, 'floor', B0)
    s.step()
    course(s, 'c1', C1)
    plate_layer(s, 'p1', P1)
    s.step()
    course(s, 'c2', C2, ACCENT)
    plate_layer(s, 'p2', P2)
    s.step()  # SNOT course: four 32952 per face; each corner column is an arc and two quarter plates
    for face, d in FACES.items():
        t = tangent(d)
        for i, u in enumerate((-30, -10, 10, 30)):
            s.add(f'snot-{face}-{i}', '32952', SHELL, np.array(d) * (FACE - 10) + t * u + [0, S_TOP, 0],
                  Ry(FACE_YAW[d]), f'Two side studs facing {face}')
    for sx, sz in QUADRANTS:
        s.add(f's-arc{QNAME[sx, sz]}', '48092', SHELL, [40 * sx, S_ARC, 40 * sz], Ry(QUAD_YAW[sx, sz]))
        for j, top in enumerate(S_PLATE):
            s.add(f's-fill{j}{QNAME[sx, sz]}', '30565', SHELL, [80 * sx, top, 80 * sz], Ry(QUAD_YAW[sx, sz]),
                  'Corner fill to the SNOT course height')
    s.step()
    plate_layer(s, 'p3', P3)
    course(s, 'c4', C4)
    s.step()
    plate_layer(s, 'top', PTOP)
    return s


def crown():
    """Stepped crown: an outer curved tier, a riser carrying an inner curved tier, and a dome.

    Both tiers use curved-top corner arcs (5651 r=80, 65617 r=60) about the same centres as the shell
    corners, with 37352 curved-top bricks on the flat faces. The four 49612 quarter domes form an
    r=80 dome that touches the inner tier's flat faces.
    """
    s = Section('comet-crown.ldr', 'Comet crown: curved tiers on a riser, quarter-dome cap and antenna')
    s.step()  # Riser inside the outer tier; hidden under the inner tier and the dome
    for sx, sz in QUADRANTS:
        s.add(f'riser-arc{QNAME[sx, sz]}', '5152', SHELL, [40 * sx, TIER1, 40 * sz], Ry(QUAD_YAW[sx, sz]))
        s.add(f'riser-fill{QNAME[sx, sz]}', '3063b', SHELL, [50 * sx, TIER1, 50 * sz], Ry(QUAD_YAW[sx, sz]),
              'r=20..40 macaroni fills the corner between the round dome and the rounded-square tier')
    for face, d in FACES.items():
        s.add(f'riser-{face}', '3010', SHELL, np.array(d) * 90 + [0, TIER1, 0], None if d[0] == 0 else Ry(90))
    for i, (x0, z0) in enumerate(((-40, -80), (0, -80), (-40, 0), (0, 0))):
        s.box(f'riser-core{i}', '3001', SHELL, x0, x0 + 40, z0, z0 + 80, TIER1)
    s.box('riser-arm-right', '3001', SHELL, 40, 80, -40, 40, TIER1)
    s.box('riser-arm-left', '3001', SHELL, -80, -40, -40, 40, TIER1)
    s.step()  # Outer tier on the shell's top plate
    for sx, sz in QUADRANTS:
        s.add(f'tier1-arc{QNAME[sx, sz]}', '5651', SHELL, [40 * sx, TIER1, 40 * sz], Ry(QUAD_YAW[sx, sz]))
    for face, d in FACES.items():
        for k in (-1, 1):
            s.add(f'tier1-{face}-{SIDE[k]}', '37352', SHELL, np.array(d) * (FACE - 10) + tangent(d) * 20 * k + [0, TIER1, 0],
                  Ry(FACE_YAW[d]), 'Curved top descending outward')
    s.step()  # Inner tier on the riser
    for sx, sz in QUADRANTS:
        s.add(f'tier2-arc{QNAME[sx, sz]}', '65617', ACCENT, [40 * sx, TIER2, 40 * sz], Ry(QUAD_YAW[sx, sz]))
    for face, d in FACES.items():
        for k in (-1, 1):
            s.add(f'tier2-{face}-{SIDE[k]}', '37352', ACCENT, np.array(d) * 90 + tangent(d) * 20 * k + [0, TIER2, 0],
                  Ry(FACE_YAW[d]), 'Red crown band')
    s.step()  # Dome: four quarter domes, each 10 LDU off-centre so their sockets meet the stud grid
    for sx, sz in QUADRANTS:
        s.add(f'dome{QNAME[sx, sz]}', '49612', SHELL, [10 * sx, DOME, 10 * sz], Ry(QUAD_YAW[sx, sz]))
    s.step()
    s.add('antenna-base', '30367c', ACCENT, [0, DOME - 24, 0], None, 'Domed cap on the four centre studs')
    s.add('antenna', '3957a', METAL, [0, DOME - 24 - 8, 0], None, 'Antenna on the cap\'s hollow stud')
    return s


# --- helmet: SNOT modules (local Y=0 is the side-stud base plane, local up faces outward) ----------

def faceplate():
    s = Section('comet-faceplate.ldr', 'Comet porthole: silver ring, smoked glass and rivets, built flat')
    s.step()
    s.add('ring', '11213', METAL, [0, -8, 0], None, 'Seated on the eight forward-facing side studs')
    s.step()
    s.add('jumper', '87580', METAL, [0, -16, 0], None, 'Centre stud for the glass')
    for i, (x, z) in enumerate(((50, -10), (50, 10), (-50, -10), (-50, 10), (-10, 50), (10, 50), (-10, -50), (10, -50))):
        s.add(f'rivet-{i}', '98138', METAL, [x, -16, z], None, 'Rivet')
    s.step()
    s.add('glass', '3960', GLASS, [0, -32, 0], None, 'Smoked bubble glass')
    return s


def cheek():
    """Symmetric ear disc; placed twice by rotation. The 6141's stud is the hose port."""
    s = Section('comet-cheek.ldr', 'Comet cheek port: red disc, silver dish and the hose spigot')
    s.step()
    s.add('disc', '60474', ACCENT, [0, -8, 0], None, 'Round base on the side-stud field')
    s.step()
    s.add('jumper', '87580', ACCENT, [0, -16, 0], None, 'Centre stud for the dish')
    s.step()
    s.add('dish', '3960', METAL, [0, -32, 0], None, 'Ear dish')
    s.step()
    s.add('port', '85861', ACCENT, [0, -40, 0], None, 'Hose port: the ribbed hose slides over this stud')
    return s


PORT_LOCAL = (0, -40, 0)                            # stud base of the cheek's 85861


def vent():
    s = Section('comet-vent.ldr', 'Comet rear vent: grille plate on the backward-facing side studs')
    s.step()
    s.add('plate', '3020', FRAME, [0, -8, 0], None, 'Seated on the eight backward-facing side studs')
    s.step()
    for i, (x, z) in enumerate(((-20, -10), (20, -10), (-20, 10), (20, 10))):
        s.add(f'grille-{i}', '2412b', METAL, [x, -16, z], None, 'Vent grille')
    return s


MODULE_R = {face: orient(up=d, along=tuple(tangent(d))) for face, d in FACES.items()}


def field_stud(face, u, row):
    """Helmet-frame stud base on a face's side-stud field: u along the face tangent, row 0 lower."""
    d = np.array(FACES[face], float)
    return d * FACE + tangent(d) * u + [0, SIDE_ROWS[1 - row], 0]


def module_origin(face):
    """Seat a module's local socket (-30, 0, -10) on the matching side stud of the face's field."""
    r = MODULE_R[face]
    socket = np.array([-30, 0, -10], float)
    world = r @ socket                              # local x lies along the tangent, local z vertical
    row = 0 if world[1] > 0 else 1
    return seat(r, socket, field_stud(face, -30, row))


def helmet():
    s = Section('comet-helmet.ldr', 'Comet helmet: shell, crown and SNOT modules in the helmet frame')
    s.add('shell', 'comet-shell.ldr', 16, [0, 0, 0])
    s.step().add('crown', 'comet-crown.ldr', 16, [0, 0, 0])
    s.step()
    s.add('faceplate', 'comet-faceplate.ldr', 16, module_origin('front'), MODULE_R['front'])
    for face in ('right', 'left'):
        s.add(f'cheek-{face}', 'comet-cheek.ldr', 16, module_origin(face), MODULE_R[face])
    s.add('vent', 'comet-vent.ldr', 16, module_origin('back'), MODULE_R['back'])
    return s


def port(face):
    """World stud base and outward axis of a cheek's hose port."""
    origin = module_origin(face) + [0, HELMET_Y, 0]
    return origin + MODULE_R[face] @ np.array(PORT_LOCAL, float), np.array(FACES[face], float)


# --- stand and backpack (world frame) --------------------------------------------------------------

def stand():
    """Display stand: two bonded plate layers, a tiled top with recesses for the column foot, tank
    feet and plaque, then the round column and silver collar. The tile surface is Y=0."""
    s = Section('comet-stand.ldr', 'Comet display stand: tiled base, plaque, round column and silver collar')
    s.step()
    s.box('base-1', '91405', BASE, -160, 160, -160, 160, 16)
    s.box('base-1-rear-r', '3035', BASE, 0, 160, 160, 240, 16)
    s.box('base-1-rear-l', '3035', BASE, -160, 0, 160, 240, 16)
    s.step()
    s.box('base-2', '91405', BASE, -160, 160, -80, 240, 8, 'Bonds the rear strip to the front square')
    s.box('base-2-front-r', '3035', BASE, 0, 160, -160, -80, 8)
    s.box('base-2-front-l', '3035', BASE, -160, 0, -160, -80, 8)
    s.step()  # Tiles around four recesses: plaque, column foot and the two tank feet
    for side, sx in (('r', 1), ('l', -1)):
        x = lambda a, b: tuple(sorted((a * sx, b * sx)))
        s.box(f'tile-edge-{side}', '4162', BASE, *x(0, 160), -160, -140, 0)
        s.box(f'tile-plaque-{side}', '87079', BASE, *x(80, 160), -140, -100, 0)
        s.box(f'tile-plaque-end-{side}', '3069b', BASE, *x(60, 80), -140, -100, 0)
        s.box(f'tile-front-{side}', '6934', BASE, *x(40, 160), -100, -40, 0)
        s.box(f'tile-waist-{side}', '1751', BASE, *x(80, 160), -40, 40, 0)
        s.box(f'tile-waist-in-{side}', '87079', BASE, *x(40, 80), -40, 40, 0)
        s.box(f'tile-back-{side}', '6320', BASE, *x(0, 160), 40, 160, 0)
        s.box(f'tile-rear-{side}', '1751', BASE, *x(80, 160), 160, 240, 0)
    s.box('tile-front-mid', '87079', BASE, -40, 40, -100, -60, 0)
    s.box('tile-front-mid-b', '2431', BASE, -40, 40, -60, -40, 0)
    s.step()
    s.box('plaque-plate', '3795', BASE, -60, 60, -140, -100, 0, 'Raised plaque')
    s.box('plaque', '69729', GOLD, -60, 60, -140, -100, -8, 'Name plaque')
    s.add('column-foot', '60474', FRAME, [0, 0, 0], None, 'Column foot in its recess')
    for i in range(COLUMN):
        s.step()
        s.add(f'column-{i}', '87081', FRAME, [0, -24 * (i + 1), 0], None, 'Round column')
    s.step()
    s.add('collar-ring', '18897', METAL, [0, -24 * COLUMN - 24, 0], None, 'Neck ring')
    s.step()
    s.add('collar-plate', '74611', METAL, [0, HELMET_Y, 0], None, 'Collar flange under the helmet floor')
    return s


def backpack():
    """Twin tanks behind the helmet, bonded by a strap plate sandwiched between their courses.
    Their feet stand in the base's tile recess."""
    s = Section('comet-backpack.ldr', 'Comet backpack: twin red tanks with cone shoulders, valves and a strap')
    y = 8
    s.step()
    y -= 8
    for sx in (1, -1):
        s.add(f'foot-{SIDE[sx]}', '60474', METAL, [TANK_X * sx, y, TANK_Z], None, 'Tank foot ring')
    for i in range(TANK_COURSES[0]):
        s.step()
        y -= 24
        for sx in (1, -1):
            s.add(f'tank-low{i}-{SIDE[sx]}', '87081', ACCENT, [TANK_X * sx, y, TANK_Z])
    s.step()
    y -= 8
    assert y == STRAP_Y
    s.box('strap', '3035', FRAME, -80, 80, TANK_Z - 40, TANK_Z + 40, y, 'Harness strap through both tanks')
    for i in range(TANK_COURSES[1]):
        s.step()
        y -= 24
        for sx in (1, -1):
            s.add(f'tank-high{i}-{SIDE[sx]}', '87081', ACCENT, [TANK_X * sx, y, TANK_Z])
    s.step()
    y -= 8
    for sx in (1, -1):
        s.add(f'band-{SIDE[sx]}', '60474', METAL, [TANK_X * sx, y, TANK_Z], None, 'Silver neck band')
    s.step()
    y -= 48
    for sx in (1, -1):
        s.add(f'shoulder-{SIDE[sx]}', '3943b', ACCENT, [TANK_X * sx, y, TANK_Z], None, 'Cone shoulder')
    s.step()
    y -= 24
    assert y == VALVE_Y
    for sx in (1, -1):
        s.add(f'valve-{SIDE[sx]}', '30367c', METAL, [TANK_X * sx, y, TANK_Z], None, 'Valve; its hollow stud is the hose spigot')
    return s


def valve(sx):
    return np.array([TANK_X * sx, VALVE_Y, TANK_Z], float), np.array([0, -1, 0], float)


# --- hoses (LSynth constraint source, world frame) -------------------------------------------------

# Each hose: valve -> straight lead-out -> one shoulder marker -> straight lead-in -> port.
# LEAD_IN was tuned with --tune so the fixed-pitch segment chain ends flush on the port stud.
HOSE_PATH = dict(lead_out=12, shoulder=(160, -240, 40), shoulder_dir=(0.3, 0.2, -0.93))
LEAD_IN = {1: 11.75, -1: 11.75}


def marker_matrix(direction):
    """Proper rotation whose local -Y is the hose's direction of travel."""
    y = -np.array(direction, float)
    y /= np.linalg.norm(y)
    helper = np.array([0, 0, 1.0]) if abs(y[2]) < 0.9 else np.array([1.0, 0, 0])
    x = np.cross(y, helper)
    x /= np.linalg.norm(x)
    z = np.cross(x, y)
    r = np.column_stack([x, y, z])
    assert np.isclose(np.linalg.det(r), 1)
    return r


def hose_markers(sx, lead_in=None, path=None):
    path = path or HOSE_PATH
    lead_in = LEAD_IN[sx] if lead_in is None else lead_in
    start, up = valve(sx)
    end, out = port('right' if sx > 0 else 'left')
    mx, my, mz = path['shoulder']
    dx, dy, dz = path['shoulder_dir']
    shoulder = np.array([mx * sx, my, mz], float)
    shoulder_dir = np.array([dx * sx, dy, dz], float)
    return [(start, up), (start + up * path['lead_out'], up), (shoulder, shoulder_dir),
            (end + out * lead_in, -out), (end, -out)]


def hose_source(lead_in=None, path=None):
    lines = ['0 Comet ribbed hoses: valve to cheek port, editable LSynth constraints',
             '0 Name: hoses.ldr', f'0 Author: {AUTHOR}', '0 !LDRAW_ORG Model']
    for sx in (1, -1):
        lines += ['0 SYNTH BEGIN TECHNIC_RIBBED_HOSE %d' % HOSE, '0 SYNTH SHOW']
        for p, d in hose_markers(sx, None if lead_in is None else lead_in[sx], path):
            m = marker_matrix(d)
            lines.append('1 %d %s %s LS01.dat' % (HOSE, ' '.join(f'{clean(v):g}' for v in p),
                                                    ' '.join(f'{clean(v):.6f}'.rstrip('0').rstrip('.') for v in m.ravel())))
        lines.append('0 SYNTH END')
    return '\r\n'.join(lines) + '\r\n'


# --- hose geometry, shared by --tune and the tests -------------------------------------------------

END_FACE = 2.5                                      # 79.dat open end, local +Y from its origin
SEGMENT_PITCH = 5.5                                 # measured LSynth ribbed-hose pitch (LDU)


def hose_segments(lines):
    """(positions, matrices, refs) of one hose's synthesized segment placements."""
    rows = [l.split() for l in lines if l.split()[:1] == ['1']]
    pos = np.array([[float(v) for v in r[2:5]] for r in rows])
    mats = [np.array([float(v) for v in r[5:14]]).reshape(3, 3) for r in rows]
    return pos, mats, [r[14].lower() for r in rows]


def hose_ends(pos, mats):
    """Open-end face centres and outward axes of the first and last end segments."""
    out = []
    for i in (0, -1):
        axis = mats[i][:, 1] / np.linalg.norm(mats[i][:, 1])
        out.append((pos[i] + axis * END_FACE, axis))
    return out


def hose_length(pos):
    return float(np.linalg.norm(np.diff(pos, axis=0), axis=1).sum() + 2 * END_FACE)


def posed_parts(mpd_text):
    """{part name: segment lines} for each posed hose part in a flex asset."""
    parts, current = {}, None
    for line in mpd_text.replace('\r', '').splitlines():
        if line.startswith('0 FILE '):
            current = line[7:].strip() if '-flex-' in line else None
            if current:
                parts[current] = []
        elif current:
            parts[current].append(line)
    return parts


def synthesize(text):
    """Run the installed lsynth-nova CLI on constraint text; return the synthesized segment blocks."""
    from lsynth_nova.config import DEFAULT_CONFIG
    result = subprocess.run([sys.executable, '-m', 'lsynth_nova', '-c', str(DEFAULT_CONFIG), '-'],
                            input=text, text=True, capture_output=True, timeout=90, check=True)
    blocks, current = [], None
    for line in result.stdout.splitlines():
        if line.strip().upper() == '0 SYNTH SYNTHESIZED BEGIN':
            current = []
        elif line.strip().upper() == '0 SYNTH SYNTHESIZED END':
            blocks.append(current)
            current = None
        elif current is not None:
            current.append(line)
    return blocks


def end_gap(lines, sx):
    """Signed distance from the hose's last open face to its port stud base, along the port axis."""
    pos, mats, _ = hose_segments(lines)
    (_, _), (face, _) = hose_ends(pos, mats)
    target, out = port('right' if sx > 0 else 'left')
    return float((face - target) @ out)


def tune():
    """Scan each hose's lead-in for a flush end and report lengths against stock ribbed hoses."""
    for sx in (1, -1):
        best = None
        for lead in np.arange(8.0, 22.01, 0.25):
            lead_in = dict(LEAD_IN)
            lead_in[sx] = float(lead)
            blocks = synthesize(hose_source(lead_in))
            lines = blocks[0 if sx > 0 else 1]
            gap = end_gap(lines, sx)
            pos, _, _ = hose_segments(lines)
            row = (abs(gap), float(lead), gap, hose_length(pos), len(pos))
            best = min(best, row) if best else row
        print(f'side {sx:+d}: lead_in={best[1]} gap={best[2]:.3f} length={best[3]:.1f} '
              f'({best[3] / 20:.2f} L) segments={best[4]}')


# --- assembly --------------------------------------------------------------------------------------

def build():
    modules = [helmet(), shell(), crown(), faceplate(), cheek(), vent(), stand(), backpack()]
    root = Section('comet.ldr', 'Comet: retro astronaut helmet with ribbed hoses and twin air tanks')
    root.add('stand', 'comet-stand.ldr', 16, [0, 0, 0])
    root.step().add('helmet', 'comet-helmet.ldr', 16, [0, HELMET_Y, 0])
    root.step().add('backpack', 'comet-backpack.ldr', 16, [0, 0, 0])
    root.step().add('hoses', 'comet-hoses.ldr', HOSE, [0, 0, 0])
    return dict(version=1, author=AUTHOR, assets=['hoses.mpd'],
                sections=[root.plan()] + [m.plan() for m in modules])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path, default=HERE / 'comet.plan.json')
    parser.add_argument('--hoses', type=Path, default=HERE / 'hoses.ldr')
    parser.add_argument('--tune', action='store_true', help='Search hose lead-ins with lsynth-nova')
    args = parser.parse_args()
    if args.tune:
        tune()
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=1) + '\n')
    args.hoses.write_bytes(hose_source().encode())
    print(args.output)
    print(args.hoses)


if __name__ == '__main__':
    main()
