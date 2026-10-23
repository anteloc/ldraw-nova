"""Halcyon: an original SNOT interceptor, generated as an ordinary JSON plan.

Run from the repository root:

    .venv/bin/python examples/snot/halcyon/generate.py
    ./ldraw-agent review examples/snot/halcyon/halcyon.plan.json --outdir output/snot-halcyon-review

Ship axes: X is width (starboard +X), -Z is forward, -Y is up. Y=0 is the keel underside and the
origin is the keel centre at the wing roots. Each module has its own local frame; the root places it.
Every sideways part is seated with origin = stud - R * socket, using inspected connector positions.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for parent in HERE.parents:
    if (parent / 'ldraw_tools').is_dir():
        sys.path.insert(0, str(parent))
        break

from ldraw_tools.builder import rotation  # noqa: E402

AUTHOR = 'Halcyon generator (Claude Code, Claude Opus 5.5) for anteloc'

# Palette roles (LDraw codes)
HULL, PANEL, FRAME, ACCENT, BLACK = 15, 71, 72, 321, 0   # white, light/dark bluish grey, dark azure, black
GLASS, GLOW = 40, 57                               # trans-black canopy, trans-orange

# Hull layers: plate/brick tops (part origins), keel underside at Y=0.
K1, K2, K3, K4, K5 = -8, -16, -24, -32, -40         # keel plates; K5 exists only under the nose cap
COURSE = -56                                       # side-stud brick course; its side studs are at Y=-46
SIDE_STUD_Y = COURSE + 10
DECK = -64                                         # deck tiles and slopes

# Each keel layer's hull plates start at NOSE_STEP[layer]; that layer's nose wedge pair fills the 80 LDU ahead.
NOSE_STEP = {K1: -140, K2: -160, K3: -180, K4: -200, K5: -220}


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
DIMS = {
    '3022': (2, 2), '3710': (4, 1), '3034': (8, 2), '3032': (6, 4), '3035': (8, 4), '3036': (8, 6),
    '3030': (10, 4), '3001': (4, 2), '3010': (4, 1), '3008': (8, 1), '3007': (8, 2),
    '3068b': (2, 2), '3069b': (2, 1), '63864': (3, 1), '2431': (4, 1), '6636': (6, 1), '87079': (4, 2),
    '2412b': (2, 1),
}


def side_stud_brick(sec, id, ref, colour, face, centre, top):
    """Place 30414 so its side studs face `face` (+-X or +-Z); `centre` is the brick centre (x, z).

    Unrotated, 30414's four side studs sit on its -Z face (Z=-10), 10 LDU below its top.
    """
    yaw = {(0, 0, -1): 0, (1, 0, 0): -90, (0, 0, 1): 180, (-1, 0, 0): 90}[tuple(face)]
    return sec.add(id, ref, colour, [centre[0], top, centre[1]], Ry(yaw), 'studs face ' + str(face))


# --- modules --------------------------------------------------------------------------------------

SIDES = (('s', 1), ('p', -1))


def xs(sx, a, b):
    """Sorted x interval for a starboard interval [a, b] mirrored by side sign sx."""
    return tuple(sorted((a * sx, b * sx)))


def hull():
    """Keel, side-stud course and deck: a studs-up core exposing stud faces to +-X, -Z and +Z.

    The forward hull (z=-220..40) is four studs wide; the engine pods widen it to twelve studs
    from z=40 to 240. K1/K3 and K2/K4 use different seams, and K2/K4 bridge the core/pod seams at
    x=+-40. Each keel layer starts at NOSE_STEP, where that layer's nose wedge pair ends.
    """
    s = Section('halcyon-hull.ldr', 'Halcyon hull core and engine pods: four keel plates, side-stud course, deck')
    for name, y, fwd in (('k1', K1, '3034'), ('k3', K3, '3030')):
        s.step()
        half = 20 if y == K1 else 40                # K1 leaves room for the two strakes
        s.box(f'{name}-fwd', fwd, FRAME, -half, half, NOSE_STEP[y], 20, y)
        s.box(f'{name}-waist', '3710', FRAME, -40, 40, 20, 40, y)
        s.box(f'{name}-aft', '3030', FRAME, -40, 40, 40, 240, y)
        for side, sx in SIDES:
            s.box(f'{name}-pod-{side}', '3030', FRAME, *xs(sx, 40, 120), 40, 240, y)
        if name == 'k1':
            s.step()
            k2_k4(s, 'k2', K2)
    s.step()
    k2_k4(s, 'k4', K4)
    for side, sx in SIDES:
        s.box(f'k4-pod-out-{side}', '3034', FRAME, *xs(sx, 80, 120), 40, 200, K4)
        s.box(f'k4-pod-tail-{side}', '3022', FRAME, *xs(sx, 80, 120), 200, 240, K4)

    s.step()  # Side-stud course: flank, intake, exhaust and tail stud faces
    for side, sx in SIDES:
        face = (sx, 0, 0)
        for i, z in enumerate((-180, -100, -20)):
            side_stud_brick(s, f'flank-mount-{i}-{side}', '30414', HULL, face, (30 * sx, z), COURSE)
        side_stud_brick(s, f'intake-mount-{side}', '30414', FRAME, (0, 0, -1), (80 * sx, 50), COURSE)
        side_stud_brick(s, f'exhaust-mount-{side}', '30414', FRAME, (0, 0, 1), (80 * sx, 230), COURSE)
        for i, z in enumerate((100, 180)):
            side_stud_brick(s, f'pod-panel-mount-{i}-{side}', '30414', HULL, face, (110 * sx, z), COURSE)
        s.box(f'pod-mid-{side}', '3008', FRAME, *xs(sx, 80, 100), 60, 220, COURSE)
        s.box(f'pod-in-{side}', '3007', HULL, *xs(sx, 40, 80), 60, 220, COURSE)
    for i, z in enumerate((-220, -140, -60)):
        s.box(f'core-{i}', '3001', FRAME, -20, 20, z, z + 80, COURSE)
    s.box('core-waist', '3010', HULL, -40, 40, 20, 40, COURSE)
    s.box('core-front', '3010', FRAME, -40, 40, 40, 60, COURSE)
    s.box('spine-s', '3007', FRAME, 0, 40, 60, 220, COURSE)
    s.box('spine-p', '3007', FRAME, -40, 0, 60, 220, COURSE)
    side_stud_brick(s, 'tail-mount', '30414', FRAME, (0, 0, 1), (0, 230), COURSE)

    s.step()  # Deck: tiles ahead of and behind the canopy, studded plates under it
    s.box('deck-bow', '87079', HULL, -40, 40, -220, -180, DECK)
    s.box('deck-bow-b', '2431', HULL, -40, 40, -180, -160, DECK)
    s.box('deck-bow-stripe', '2431', ACCENT, -40, 40, -160, -140, DECK)
    s.box('cockpit-floor', '3032', FRAME, -40, 40, -140, -20, DECK)
    s.box('cockpit-floor-aft', '3710', FRAME, -40, 40, -20, 0, DECK)
    s.box('deck-waist', '87079', HULL, -40, 40, 0, 40, DECK)

    s.step()  # Cockpit interior, seen through the canopy; the canopy keeps the four studs at x=+-10
    t = DECK - 8
    for side, sx in SIDES:
        s.box(f'cabin-sill-{side}', '3069b', PANEL, *xs(sx, 20, 40), -140, -100, t)
        s.box(f'cabin-side-{side}', '3069b', PANEL, *xs(sx, 20, 40), -80, -40, t)
    s.box('cabin-console', '2431', ACCENT, -40, 40, -100, -80, t)
    s.box('cabin-seat', '3068b', FRAME, -20, 20, -80, -40, t)
    s.box('cabin-aft', '87079', FRAME, -40, 40, -40, 0, t)

    s.step()  # Recessed spine between the pods: grille detail and twin swept tails on the outer columns
    s.box('spine-front', '87079', FRAME, -40, 40, 40, 80, DECK)
    s.box('spine-mid', '87079', FRAME, -40, 40, 80, 120, DECK)
    s.box('spine-grille-a', '2412b', PANEL, -20, 20, 120, 140, DECK)
    s.box('spine-grille-b', '2412b', PANEL, -20, 20, 140, 160, DECK)
    s.box('spine-aft', '87079', FRAME, -20, 20, 160, 240, DECK)
    for side, sx in SIDES:
        s.box(f'spine-edge-{side}', '3069b', FRAME, *xs(sx, 20, 40), 120, 160, DECK)
        s.add(f'tail-{side}', '2340', HULL, [30 * sx, COURSE - 72, 240], None, 'Swept tail on the spine edge')
        s.add(f'tail-cap-{side}', '3069b', ACCENT, [30 * sx, COURSE - 80, 240], Ry(90), 'Tail cap')

    s.step()  # Rounded pod tops: curved slopes back to back along each pod's centreline
    for side, sx in SIDES:
        for i, z in enumerate(range(40, 240, 40)):
            for half, (a, b), out in (('in', (40, 80), -1), ('out', (80, 120), 1)):
                x0, x1 = xs(sx, a, b)
                down = out * sx                        # +1: slope descends toward +X
                s.add(f'pod-top-{side}-{half}{i}', '15068', PANEL if i == 4 else HULL, [(x0 + x1) / 2, COURSE, z + 20],
                      Ry(-90 * down), 'Curved pod top')
    return s


def k2_k4(s, name, y):
    """K2/K4: forward core plates, then eight-stud bridges across the core/pod seams at x=+-40."""
    s.box(f'{name}-fwd', '3035' if y == K4 else '3032', FRAME, -40, 40, NOSE_STEP[y], -40, y)
    s.box(f'{name}-mid', '3032', FRAME, -40, 40, -40, 80, y)
    for side, sx in SIDES:
        s.box(f'{name}-pod-in-{side}', '3022', FRAME, *xs(sx, 40, 80), 40, 80, y)
    s.box(f'{name}-bridge', '3036', FRAME, -80, 80, 80, 200, y)
    s.box(f'{name}-bridge-tail', '3034', FRAME, -80, 80, 200, 240, y)


def flank(side):
    """SNOT side panel: authored upright in its own frame, then turned so local up faces outboard.

    Local X runs aft along the hull and local Y=0 is the hull's side-stud base plane. The upper
    tile row is local Z=+10 on starboard and -10 on port: the two proper rotations send local Z
    to opposite world directions. The parts are identical; only their arrangement differs.
    """
    s = Section(f'halcyon-flank-{side}.ldr', f'Halcyon {"starboard" if side == "s" else "port"} flank panel, '
                'built flat and mounted on side studs')
    upper = 10 if side == 's' else -10
    s.step()
    s.add('base-fwd', '3034', HULL, [-40, -8, 0], None, 'Two-row base plate on the side studs')
    s.add('base-aft', '3020', HULL, [80, -8, 0], None, 'Two-row base plate on the side studs')
    s.step()
    # The stripe's 1 x 8 tile spans the base-plate seam at local X=40, bonding the two plates.
    s.add('stripe-fwd', '2431', ACCENT, [-80, -16, upper], None, 'Accent stripe, level with the pod stripes')
    s.add('stripe-aft', '4162', ACCENT, [40, -16, upper], None, 'Accent stripe bridging the base-plate seam')
    s.add('lower-fwd', '4162', HULL, [-40, -16, -upper], None, 'Lower tile row')
    s.add('lower-aft', '2431', HULL, [80, -16, -upper], None, 'Lower tile row')
    return s


FLANK_R = {'s': orient(up=(1, 0, 0), along=(0, 0, 1)), 'p': orient(up=(-1, 0, 0), along=(0, 0, 1))}
FWD_R = orient(up=(0, 0, -1), along=(1, 0, 0))      # local up points forward
AFT_R = orient(up=(0, 0, 1), along=(1, 0, 0))       # local up points aft


def nozzle():
    """Exhaust built upright along its own axis; the root turns local up to face aft (+Z)."""
    s = Section('halcyon-exhaust.ldr', 'Halcyon exhaust nozzle: round plate, jumper, dish bell and glowing core')
    s.step()
    s.add('ring', '60474', FRAME, [0, 0, 0], None, 'Round 4 x 4 base seated on four aft-facing studs')
    s.step()
    s.add('jumper', '87580', FRAME, [0, -8, 0], None, 'Centre stud for the dish')
    s.step()
    s.add('bell', '3960', PANEL, [0, -24, 0], None, 'Nozzle bell')
    s.step()
    s.add('core', '4740', GLOW, [0, -32, 0], None, 'Glowing core')
    return s


def intake():
    """Intake ring and spinner, built upright along its own axis; the root turns it to face forward."""
    s = Section('halcyon-intake.ldr', 'Halcyon engine intake: round ring and truncated-cone spinner')
    s.step()
    s.add('ring', '60474', FRAME, [0, 0, 0], None, 'Round 4 x 4 intake ring on four forward-facing studs')
    s.step()
    s.add('hub', '3941', PANEL, [0, -24, 0], None, 'Spinner hub')
    s.step()
    s.add('spinner', '98100', HULL, [0, -48, 0], None, 'Spinner cone')
    return s


def nose():
    """Pointed nose in the ship frame: handed wedge-plate pairs under a triple-curved wedge.

    Each keel layer's pair fills the 80 LDU ahead of that layer's hull plates, so each step
    back overlaps the first hull row of the next layer up. The lower layers stop short of the
    tip, giving a chin that rises toward it.
    """
    s = Section('halcyon-nose.ldr', 'Halcyon nose: stepped handed wedge plates under a triple-curved wedge')
    for i, y in enumerate((K1, K2, K3, K4, K5)):
        s.step()
        zc = NOSE_STEP[y] - 40
        colour = HULL
        s.add(f'wedge-{i + 1}s', '41770', colour, [20, y, zc], None, 'Starboard half of the pointed plate')
        s.add(f'wedge-{i + 1}p', '41769', colour, [-20, y, zc], None, 'Port half of the pointed plate')
    s.step()
    s.add('cap', '47753', HULL, [0, K5 - 24, NOSE_STEP[K5] - 40], None, 'Triple-curved nose wedge')
    return s


def aft_cap():
    """Centre panel between the nozzles, built upright and turned to face aft."""
    s = Section('halcyon-aft-cap.ldr', 'Halcyon aft cap: dark panel with grille and two glowing vents')
    s.step()
    s.add('panel', '3020', FRAME, [0, 0, 0], None, 'Seated on the aft-facing tail studs')
    s.step()
    s.add('vent-s', '98138', GLOW, [30, -8, -10], None, 'Glowing vent')
    s.add('vent-p', '98138', GLOW, [-30, -8, -10], None, 'Glowing vent')
    s.add('grille', '2412b', PANEL, [0, -8, -10], None, 'Grille')
    s.add('lower', '2431', PANEL, [0, -8, 10], None, 'Lower tile')
    return s


def wing(side):
    """Swept wing: a handed 6 x 12 wing plate on a root splice that runs under the pod, fully tiled."""
    sx = 1 if side == 's' else -1
    s = Section(f'halcyon-wing-{side}.ldr', f'Halcyon {"starboard" if side == "s" else "port"} wing, root splice and tiles')
    s.step()
    s.box('splice', '3030', FRAME, *xs(sx, 80, 160), 40, 240, K2)
    s.step()
    s.add('wing', '30355' if side == 's' else '30356', HULL, [180 * sx, K3, 120], None, 'Handed 6 x 12 wing plate')
    s.step()
    t = K3 - 8
    s.box('tile-root-a', '3069b', HULL, *xs(sx, 140, 180), 0, 20, t)
    s.add('cannon-mount', '87087', PANEL, [130 * sx, K3 - 24, 10], None, 'Side stud faces forward for the cannon')
    s.box('tile-root-b', '63864', HULL, *xs(sx, 120, 180), 20, 40, t)
    s.box('tile-root-c', '63864', HULL, *xs(sx, 120, 180), 40, 60, t)
    s.box('tile-mid-a', '87079', HULL, *xs(sx, 120, 200), 60, 100, t)
    s.box('tile-mid-b', '2431', HULL, *xs(sx, 120, 200), 100, 120, t)
    s.box('tile-mid-c', '87079', HULL, *xs(sx, 120, 200), 120, 160, t)
    s.box('tile-mid-d', '2431', HULL, *xs(sx, 120, 200), 160, 180, t)
    s.box('tile-edge', '63864', ACCENT, *xs(sx, 200, 220), 120, 180, t)
    s.box('tile-aft', '87079', HULL, *xs(sx, 120, 200), 180, 220, t)
    s.box('tile-trailing', '2431', ACCENT, *xs(sx, 120, 200), 220, 240, t)
    s.box('tile-tip', '3068b', HULL, *xs(sx, 200, 240), 200, 240, t)
    s.step()
    s.add('tip-fin', '44661', HULL, [220 * sx, t, 190], None, 'Wingtip fin')
    return s


def strake(side):
    """Leading-edge strake at keel level: a handed 4 x 8 wing plate bonded under the hull core."""
    sx = 1 if side == 's' else -1
    s = Section(f'halcyon-strake-{side}.ldr', f'Halcyon {"starboard" if side == "s" else "port"} strake')
    s.step()
    s.add('plate', '3933' if side == 's' else '3934', HULL, [60 * sx, K1, -60], None,
          'Handed 4 x 8 wing plate; its inner column runs under the hull')
    s.step()
    s.box('tile-inner', '6636', HULL, *xs(sx, 40, 60), -100, 20, K2)
    s.box('tile-outer', '2431', HULL, *xs(sx, 60, 80), -60, 20, K2)
    return s


def pod_panel(side):
    """One-row SNOT stripe on a pod's outer side, built flat like the flanks."""
    s = Section(f'halcyon-pod-panel-{side}.ldr', f'Halcyon {"starboard" if side == "s" else "port"} pod stripe')
    s.step()
    s.add('base', '3460', HULL, [0, -8, 0], None, 'One-row base plate on the pod side studs')
    s.step()
    s.add('stripe', '4162', ACCENT, [0, -16, 0], None, 'Accent stripe')
    return s


def cannon():
    """Wing-root cannon built upright along its own axis; the root turns local up to face forward."""
    s = Section('halcyon-cannon.ldr', 'Halcyon cannon: stacked round parts on a forward-facing side stud')
    for i, (ref, colour, y) in enumerate((('85861', FRAME, 0), ('3062b', PANEL, -24), ('85861', ACCENT, -32),
                                          ('3062b', PANEL, -56), ('98138', FRAME, -64))):
        s.step()
        s.add(f'barrel-{i}', ref, colour, [0, y, 0])
    return s


def stand():
    """Display stand: round column whose top studs enter the keel plate's underside sockets."""
    s = Section('halcyon-stand.ldr', 'Halcyon display stand')
    s.step()
    s.add('base', '65140', BLACK, [0, 104, 0], None, 'Base plate 8 x 8 with rounded corners')
    s.step()
    s.add('flange', '60474', PANEL, [0, 96, 0], None, 'Round flange')
    for i, y in enumerate((72, 48, 24, 0)):
        s.step()
        s.add(f'column-{i}', '3941', FRAME, [0, y, 0], None, 'Round column brick')
    return s


def cockpit():
    s = Section('halcyon-cockpit.ldr', 'Halcyon canopy')
    s.add('canopy', '30384', GLASS, [0, DECK, -90], None, 'Rounded pointed canopy on the cockpit floor studs')
    return s


def build():
    """Root steps add whole modules in reading order: core, nose, keel-level strakes and wings,
    SNOT skins, along-axis modules, canopy, stand. The strakes and wing splices are sandwiched
    in the keel, so a physical build inserts them between the K layers."""
    modules = [hull(), nose(), strake('s'), strake('p'), wing('s'), wing('p'), flank('s'), flank('p'),
               pod_panel('s'), pod_panel('p'), intake(), nozzle(), aft_cap(), cannon(), cockpit(), stand()]
    root = Section('halcyon.ldr', 'Halcyon SNOT interceptor on its display stand')
    root.add('hull', 'halcyon-hull.ldr', 16, [0, 0, 0])
    root.step().add('nose', 'halcyon-nose.ldr', 16, [0, 0, 0])
    root.step()
    for side, sx in SIDES:
        root.add(f'strake-{side}', f'halcyon-strake-{side}.ldr', 16, [0, 0, 0])
        root.add(f'wing-{side}', f'halcyon-wing-{side}.ldr', 16, [0, 0, 0])
    root.step()
    for side, sx in SIDES:
        # Flank base plate's front upper socket onto the first side stud at x=+-40, Y=-46, Z=-210.
        root.add(f'flank-{side}', f'halcyon-flank-{side}.ldr', 16,
                 seat(FLANK_R[side], [-110, 0, 10 * sx], [40 * sx, SIDE_STUD_Y, -210]), FLANK_R[side])
        root.add(f'pod-panel-{side}', f'halcyon-pod-panel-{side}.ldr', 16,
                 seat(FLANK_R[side], [-70, 0, 0], [120 * sx, SIDE_STUD_Y, 70]), FLANK_R[side])
    root.step()
    for side, sx in SIDES:
        root.add(f'intake-{side}', 'halcyon-intake.ldr', 16,
                 seat(FWD_R, [10, 8, 10], [80 * sx + 10, SIDE_STUD_Y, 40]), FWD_R)
        root.add(f'exhaust-{side}', 'halcyon-exhaust.ldr', 16,
                 seat(AFT_R, [10, 8, -10], [80 * sx + 10, SIDE_STUD_Y, 240]), AFT_R)
        # 87087 on the wing: top at K3-24, side stud 10 below its top on the z=0 face
        root.add(f'cannon-{side}', 'halcyon-cannon.ldr', 16,
                 seat(FWD_R, [0, 8, 0], [130 * sx, K3 - 24 + 10, 0]), FWD_R)
    root.add('aft-cap', 'halcyon-aft-cap.ldr', 16, seat(AFT_R, [10, 8, -10], [10, SIDE_STUD_Y, 240]), AFT_R)
    root.step().add('cockpit', 'halcyon-cockpit.ldr', 16, [0, 0, 0])
    root.step().add('stand', 'halcyon-stand.ldr', 16, [0, 0, 80])
    return dict(version=1, author=AUTHOR, sections=[root.plan()] + [m.plan() for m in modules])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path, default=HERE / 'halcyon.plan.json')
    args = parser.parse_args()
    plan = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=1) + '\n')
    print(args.output)


if __name__ == '__main__':
    main()
