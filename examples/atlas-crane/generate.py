"""Atlas AT-90: an original 4-axle Technic all-terrain crane, generated as a modular LDraw plan.

Run from the repository root:

    .venv/bin/python output/atlas-crane/generate.py [--stage carrier|full] [--slew DEG] [--luff DEG]
    ./ldraw-agent build output/atlas-crane/atlas-crane.plan.json \
        --output output/atlas-crane/atlas-crane.mpd --contacts none --detail summary --force

World axes: X across (+X right), Y down (Y=0 road), Z along (-Z forward).
Scale ~1:23 (tyre 32019 = 157 LDU ~ 1.45 m).  See design-brief.md for the layout rationale.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from crane_lib import (Frame, Section, axle, basis, beam, beam_holes, bush, clean, pin, rot, v)  # noqa: E402

AUTHOR = 'Atlas AT-90 generator (Claude Code, Claude Opus 5.5) for anteloc'

# ------------------------------------------------------------------ palette roles
YELLOW, BLACK, DBG, LBG, RED, WHITE = 14, 0, 72, 71, 4, 15
TORANGE, TCLEAR, TRED, TBROWN, SILVER = 57, 47, 36, 40, 80
RIM = LBG

# ------------------------------------------------------------------ master layout (LDU)
YW = -80                      # wheel centre height (tyre r=78.3)
XW = 130                      # wheel origin |x|; tyre local +Z points inward
AXLE_Z = [-470, -250, 190, 410]
Y_DECK = -250                 # top of deck / walkway panels (panel centre -240)
X_BODY = 170                  # body side |x|
ROT180 = basis(x='-X', z='-Z')
XR = 60                       # rail web centre |x|
YC = -160                     # rail web centre height: web spans YC-50 .. YC+50
RAIL_Z0 = -560                # front end of the rail chain
N_WEB = 6                     # 64179 frames, 140 LDU each -> rails end at +280
Y_DECK_BEAM = YC - 60         # crossmember centre (-220); deck beam top at -230
WEB_Z = [RAIL_Z0 + 70 + 140 * k for k in range(N_WEB)]


def web_face_z(zc):
    return [zc - 60, zc - 20, zc + 20, zc + 60]


# ------------------------------------------------------------------ wheel + axle

def wheel_section():
    s = Section('atc-wheel.ldr', 'Road wheel: 18 x 37 rim in a 64 x 37 tyre; local +Z points inboard')
    s.add('86652', RIM, (0, 0, 0), purpose='six-peghole rim, axle bore along local Z')
    s.add('32019', BLACK, (0, 0, 0), purpose='20/64 x 37 S tyre')
    return s


def axle_section(name, driven=True):
    s = Section(name, 'Steered axle station: through-shaft, ' + ('28T differential, ' if driven else '')
                + 'round axle tubes, steering-hub bearings, hydropneumatic struts and two wheels')
    if driven:
        s.add('62821', DBG, (0, 0, 0), basis(z='X', y='Y'), purpose='differential, bore on the shaft')
    for sx in (-1, 1):
        s.add('62462', DBG, (sx * 50, 0, 0), purpose='axle tube (round joiner) over the half-shaft')
    s.step()
    for sx in (-1, 1):
        out = 'X' if sx > 0 else '-X'
        s.add('11950', DBG, (sx * 100, 0, 0), basis(z=out, y='Y'), purpose='steering hub bearing')
    axle(s, 16, (0, 0, 0), 'X', LBG, purpose='through half-shaft, diff to both rims')
    s.step()
    for sx in (-1, 1):
        inward = '-X' if sx > 0 else 'X'
        s.add('atc-wheel.ldr', 16, (sx * XW, 0, 0), basis(z=inward, x='Y'), purpose='road wheel')
    s.step()
    for sx in (-1, 1):
        # strut: local +Y (towards the eye at y=110) points up; eye at y = -40-110 = -150
        s.add('76138', YELLOW, (sx * 100, -30, 40), basis(y='-Y', z='Z'), purpose='hydropneumatic strut')
    return s


# ------------------------------------------------------------------ chassis frame

def frame_section():
    s = Section('atc-frame.ldr', 'Carrier ladder frame: 7x5 open-frame webs with beam flanges and crossmembers')
    web_R = basis(x='-Y', y='X')          # holes along world X, 100 tall, 140 long
    for sx in (-1, 1):
        for zc in WEB_Z:
            s.add('64179', BLACK, (sx * XR, YC, zc), web_R, purpose='rail web (open frame)')
    s.step()
    # outer flanges: top row staggered against bottom row
    flange_top = [(13, -430), (15, -150), (13, 130)]
    flange_bot = [(15, -410), (15, -110), (13, 170)]
    face = sorted(z for zc in WEB_Z for z in web_face_z(zc))
    for sx in (-1, 1):
        for row_y, layout in ((YC - 40, flange_top), (YC + 40, flange_bot)):
            holes = []
            for n, zc in layout:
                beam(s, n, (sx * (XR + 20), row_y, zc), 'Z', 'X', DBG, purpose='rail flange')
                holes += [round(p[2]) for p in beam_holes(n, (0, 0, zc), 'Z')]
            for z in face:
                if z in holes and not (row_y > YC and z == 270):
                    pin(s, (sx * (XR + 10), row_y, z), 'X', BLACK, purpose='flange-to-web pin')
    s.step()
    # deck crossmembers on the web top bars (in-plane vertical holes at zc-40, zc+40)
    for zc in WEB_Z:
        for z in (zc - 40, zc + 40):
            beam(s, 7, (0, Y_DECK_BEAM, z), 'X', 'Y', DBG, purpose='deck crossmember')
            for sx in (-1, 1):
                pin(s, (sx * XR, YC - 50, z), 'Y', BLACK, purpose='crossmember-to-web pin')
    # lower crossmembers clear of the axle stations
    for z in (-350, -170, -70, 30, 250):
        beam(s, 7, (0, YC + 60, z), 'X', 'Y', DBG, purpose='lower crossmember')
        for sx in (-1, 1):
            pin(s, (sx * XR, YC + 50, z), 'Y', BLACK, purpose='crossmember-to-web pin')
    return s


# ------------------------------------------------------------------ brick walls (System cab shells)

BRICK_1XN = {1: '3005', 2: '3004', 3: '3622', 4: '3010', 6: '3009', 8: '3008'}


def fill_row(n, offset):
    """Split n studs into 1xN brick lengths; `offset` staggers the joints (running bond)."""
    out, left = [], n
    if offset and n > 2:
        out.append(offset)
        left -= offset
    while left:
        for k in (8, 6, 4, 3, 2, 1):
            if k <= left:
                out.append(k)
                left -= k
                break
    return out


def brick_row(sec, start, along, n, y_top, colour, offset=0, purpose=None):
    """Lay 1xN bricks along a stud row. start = centre of the first stud (x, z)."""
    a = unit_xz(along)
    R = np.eye(3) if abs(a[0]) > 0.5 else basis(x='Z', y='Y')
    pos = 0
    for k in fill_row(n, offset):
        c = np.array([start[0], y_top, start[1]]) + np.array([a[0], 0, a[1]]) * (20 * pos + 10 * (k - 1))
        sec.add(BRICK_1XN[k], colour, c, R, purpose=purpose)
        pos += k


def unit_xz(d):
    return {'X': (1, 0), '-X': (-1, 0), 'Z': (0, 1), '-Z': (0, -1)}[d]


# ------------------------------------------------------------------ carrier bodywork

def body_section():
    s = Section('atc-body.ldr', 'Carrier bodywork: mudguards, skirts, walkways, deck, lockers and bumpers')
    flat_z = basis(x='Z', y='Y')              # 64782/15458 lying flat, long along Z
    side_z = basis(x='Z', z='Y')              # panel standing, long along Z, face along X
    for i, z in enumerate(AXLE_Z):
        for sx in (-1, 1):
            R = np.eye(3) if sx > 0 else ROT180
            s.add('2509', YELLOW, (sx * 160, -81, z), R, purpose=f'arched mudguard, axle {i + 1}')
            s.add('15458', YELLOW, (sx * X_BODY, -200, z), side_z, purpose='skirt above the wheel arch')
    s.step()
    # walkways: full length strip each side, flush with the deck
    for z in (-470, -250, -30, 190, 410):
        for sx in (-1, 1):
            s.add('64782', DBG, (sx * 120, -240, z), flat_z, purpose='walkway panel (non-slip grey)')
    # centre deck ahead of the slewing ring
    for z in (-470, -250):
        s.add('64782', DBG, (0, -240, z), flat_z, purpose='centre deck panel')
    s.step()
    # lockers between axles 2 and 3 (left) - the right side carries the fuel tank
    s.add('15458', YELLOW, (-X_BODY, -200, -30), side_z, purpose='locker door')
    for z in (-110, -30, 50):
        s.add('3069b', DBG, (-X_BODY - 10, -206, z), basis(x='Z', y='-X'), purpose='locker handle')
    s.step()
    # front bumper with lamps and tow eyes
    s.add('3703', BLACK, (0, -110, -755), purpose='front bumper (Technic brick 1x16)')
    for sx in (-1, 1):
        s.add('3069b', TCLEAR, (sx * 130, -118, -755), purpose='front lamp')
        s.add('3069b', TORANGE, (sx * 90, -118, -755), purpose='indicator')
    # rear bumper with tail lights
    s.add('3703', BLACK, (0, -130, 710), purpose='rear bumper (Technic brick 1x16)')
    for sx in (-1, 1):
        s.add('3069b', TRED, (sx * 130, -138, 710), purpose='tail light')
        s.add('3069b', TORANGE, (sx * 90, -138, 710), purpose='rear indicator')
    return s


CAB_X0, CAB_Z0 = -175, -745


def cab_section():
    s = Section('atc-cab.ldr', 'Driver cab (front left): brick shell, grille band, 1x4x5 windows, roof details')
    x0, z0 = CAB_X0, CAB_Z0          # cab outer corner (8 x 8 studs)
    floor = -130
    s.add('41539', DBG, (x0 + 80, floor, z0 + 80), purpose='cab floor plate 8x8')
    s.step()
    course_top = [floor - 24 * (k + 1) for k in range(9)]
    for k, yt in enumerate(course_top):
        col = BLACK if k == 0 else YELLOW
        off = 1 if k % 2 else 0
        if k == 1:      # lamp + grille band across the front
            for xs, ref, c in ((x0 + 10, '3005', TCLEAR), (x0 + 150, '3005', TCLEAR)):
                s.add(ref, c, (xs, yt, z0 + 10), purpose='cab headlamp')
            for n in range(3):
                s.add('2877', BLACK, (x0 + 40 + 40 * n, yt, z0 + 10), purpose='cab front grille')
        elif k < 4:
            brick_row(s, (x0 + 10, z0 + 10), 'X', 8, yt, col, off, 'cab front wall')
        for xs in (x0 + 10, x0 + 150):
            if k < 4:
                brick_row(s, (xs, z0 + 30), 'Z', 7, yt, col, off, 'cab side wall')
            else:
                brick_row(s, (xs, z0 + 110), 'Z', 3, yt, YELLOW, 0, 'cab side pillar')
        brick_row(s, (x0 + 30, z0 + 150), 'X', 6, yt, col, 0 if k % 2 else 1, 'cab rear wall')
    s.step()
    wtop = course_top[-1]
    for xc in (x0 + 40, x0 + 120):
        s.add('2493b', BLACK, (xc, wtop, z0 + 10), purpose='windscreen frame 1x4x5')
        s.add('2494', TBROWN, (xc, wtop, z0 + 10), purpose='tinted windscreen glass')
    Rz = basis(x='Z', y='Y')
    for xs in (x0 + 10, x0 + 150):
        s.add('2493b', BLACK, (xs, wtop, z0 + 60), Rz, purpose='side window frame')
        s.add('2494', TBROWN, (xs, wtop, z0 + 60), Rz, purpose='side window glass')
    s.step()
    roof = wtop - 8
    s.add('41539', YELLOW, (x0 + 80, roof, z0 + 80), purpose='cab roof 8x8')
    s.add('4162', BLACK, (x0 + 80, roof - 8, z0 + 10), purpose='sun visor')
    s.add('3001', DBG, (x0 + 80, roof - 24, z0 + 110), purpose='roof air-conditioning unit')
    s.add('87079', DBG, (x0 + 80, roof - 32, z0 + 110), purpose='air-conditioning cover')
    for xs in (x0 + 20, x0 + 140):
        s.add('6141', TORANGE, (xs, roof - 8, z0 + 140), purpose='beacon base')
        s.add('3062b', TORANGE, (xs, roof - 32, z0 + 140), purpose='rotating beacon')
    # rear-view mirrors on arms at the front corners
    for sx, xm in ((-1, x0 - 10), (1, x0 + 170)):
        s.add('3004', BLACK, (xm, wtop + 24, z0 + 10), Rz, purpose='mirror arm block')
        s.add('3069b', BLACK, (xm, wtop - 8 + 24, z0 + 10), Rz, purpose='mirror head')
    return s


def front_box_section():
    s = Section('atc-front.ldr', 'Front equipment box beside the cab and the boom rest')
    x0, z0, floor = CAB_X0 + 160, CAB_Z0, -130     # 9 x 8 studs right of the cab
    for y, col in ((floor, DBG), (floor - 128, YELLOW)):
        s.add('41539', col, (x0 + 80, y, z0 + 80), purpose='front box floor/lid 8x8')
        s.add('3460', col, (x0 + 170, y, z0 + 80), basis(x='Z', y='Y'), purpose='front box floor/lid 1x8')
    for k in range(5):
        yt = floor - 24 * (k + 1)
        col = BLACK if k == 0 else YELLOW
        if k in (1, 2):
            for n in range(4):
                s.add('2877', BLACK, (x0 + 20 + 40 * n, yt, z0 + 10), purpose='front air intake grille')
            s.add('3005', YELLOW, (x0 + 170, yt, z0 + 10), purpose='front box corner')
        else:
            brick_row(s, (x0 + 10, z0 + 10), 'X', 9, yt, col, k % 2, 'front box face')
        brick_row(s, (x0 + 170, z0 + 30), 'Z', 7, yt, col, k % 2, 'front box side')
    for n in range(4):
        s.add('2412b', BLACK, (x0 + 40 + 40 * n, floor - 136, z0 + 50), purpose='lid vent')
    s.step()
    # boom rest: two posts and a V saddle over the front axle
    zr = -520
    for sx in (-1, 1):
        beam(s, 9, (sx * 40, -340, zr), 'Y', 'Z', YELLOW, purpose='boom rest post')
    beam(s, 7, (0, -440, zr), 'X', 'Z', YELLOW, purpose='boom rest cross head')
    for sx in (-1, 1):
        d = np.array([sx * 0.7071, -0.7071, 0])
        s.add('32523', BLACK, np.array([sx * 50, -470, zr]), basis(y='Z', z=d), purpose='boom rest saddle arm')
    # sling crate on the front deck: low walls, chains inside
    cx, cz = 110, -330
    s.add('3032', DBG, (cx, -258, cz), basis(x='Z', y='Y'), purpose='sling crate base 4x6')
    for dz in (-50, 50):
        s.add('3010', BLACK, (cx, -282, cz + dz), purpose='sling crate end wall')
    for dx in (-30, 30):
        s.add('3010', BLACK, (cx + dx, -282, cz), basis(x='Z', y='Y'), purpose='sling crate side wall')
    for dz in (-20, 20):
        s.add('3641', BLACK, (cx, -266, cz + dz), basis(z='-Y', x='X'), purpose='coiled sling (tyre as rope coil)')
    s.add('3136', LBG, (cx, -270, cz), basis(y='Z', z='Y'), purpose='spare crane hook in the crate')
    return s


def outrigger_section():
    """Right-hand outrigger; local origin at the carrier side (world x=90), box centreline y=0."""
    s = Section('atc-outrigger.ldr', 'Outrigger: fixed box, twin extended beams with red tips, actuator jack and pad')
    for zw in (-30, 30):
        for y in (-10, 10):
            beam(s, 5, (50, y, zw), 'X', 'Z', DBG, purpose='outrigger box wall')
    # staggered joints: z=-10 layer yellow 9 + red 5, z=+10 layer yellow 11 + red 3
    for y in (-10, 10):
        beam(s, 9, (130, y, -10), 'X', 'Z', YELLOW, purpose='extended outrigger beam')
        beam(s, 5, (270, y, -10), 'X', 'Z', RED, purpose='outrigger beam tip (warning red)')
        beam(s, 11, (150, y, 10), 'X', 'Z', YELLOW, purpose='extended outrigger beam')
        beam(s, 3, (290, y, 10), 'X', 'Z', RED, purpose='outrigger beam tip (warning red)')
    s.step()
    for x in (70, 90):
        for y in (-10, 10):
            axle(s, 4, (x, y, 0), 'Z', LBG, purpose='box-to-beam locking shaft (wall, both beam layers, wall)')
    for x in (150, 230, 250, 290):
        for y in (-10, 10):
            pin(s, (x, y, 0), 'Z', BLACK, purpose='beam doubling pin (bridges the staggered joints)')
    s.step()
    R_jack = basis(x='Z', z='Y')
    s.add('92693c01-f1', DBG, (330, -10, 0), R_jack, purpose='vertical jack (linear actuator) at the beam tip')
    s.add('60474', RED, (330, 119, 0), purpose='outrigger pad (round plate 4x4)')
    return s


def fuel_tank(s, c):
    """Original saddle tank: three 4x4 cylinders on a shaft, dished end caps (axis along Z)."""
    c = np.array(c, float)
    Rz = np.eye(3)
    axle(s, 6, c, 'Z', LBG, purpose='fuel tank shaft')
    for dz in (-20, 20):
        s.add('41531', SILVER, c + (0, 0, dz), Rz, purpose='fuel tank shell')
    for sz in (-1, 1):
        s.add('3960', SILVER, c + (0, 0, sz * 44), basis(y=(0, 0, sz), x='X'), purpose='fuel tank end cap')


def hood_section():
    s = Section('atc-hood.ldr', 'Carrier engine hood: 8x8 plate with grille tiles; hinge line at local z=0')
    s.add('41539', BLACK, (0, 0, 80), purpose='engine hood plate 8x8')
    for row in range(4):
        for n in range(4):
            s.add('2412b', DBG, (-60 + 40 * n, -8, 20 + 40 * row), basis(x='Z', y='Y'), purpose='hood ventilation grille')
    return s


def rear_bay_section():
    s = Section('atc-rear.ldr', 'Rear engine bay: extension rails, carrier V8 under a grille hood, radiator, exhaust')
    for sx in (-1, 1):
        for y in (YC - 40, YC + 40):
            beam(s, 15, (sx * 80, y, 450), 'Z', 'X', DBG, purpose='rear extension rail')
            beam(s, 5, (sx * 100, y, 290), 'Z', 'X', DBG, purpose='rail splice plate')
            zs_pins = (250, 310, 330) if y < YC else (250, 290, 310, 330)
            for z in zs_pins:
                pin(s, (sx * 90, y, z), 'X', BLACK, purpose='splice pin (flange/extension + splice)')
        pin(s, (sx * 80, YC + 40, 270), 'X', BLACK, long=True, purpose='web + flange + splice pin')
    s.step()
    s.add(V8_ROOT, LBG, (0, -199, 580), ROT180, purpose='carrier V8 (adapted from 42082)')
    s.step()
    # rear body: louvred radiator wall + warning band, closed left side, open right side (V8 on show)
    x_l, z_f, z_r = -170, 540, 700
    for k in range(5):
        yt = -130 - 24 * (k + 1)
        if k < 3:
            s.add('3005', YELLOW, (-150, yt, z_r - 10), purpose='rear wall corner')
            for n in range(7):
                s.add('2877', BLACK, (-120 + 40 * n, yt, z_r - 10), purpose='radiator louvre (grille brick)')
            s.add('3005', YELLOW, (150, yt, z_r - 10), purpose='rear wall corner')
        elif k == 3:
            for n in range(8):
                s.add('3004', RED if n % 2 else WHITE, (-140 + 40 * n, yt, z_r - 10), purpose='rear warning band')
        else:
            brick_row(s, (-150, z_r - 10), 'X', 16, yt, YELLOW, 0, 'rear wall top course')
        if k >= 1:
            brick_row(s, (x_l + 10, z_f + 10), 'Z', 7, yt, YELLOW if k > 1 else BLACK, k % 2, 'rear body left side')
    for zp in (z_f + 10, z_r - 30):
        beam(s, 5, (150, -200, zp), 'Y', 'X', YELLOW, purpose='rear body right post (open side)')
    s.step()
    for sx in (-1, 1):
        s.add('3035', DBG, (sx * 130, -258, 620), basis(x='Z', y='Y'), purpose='rear walkway plate 4x8')
    s.add('atc-hood.ldr', 16, (0, -250, z_f), rot('x', 65), purpose='engine hood, hinged open for service')
    s.add(EXHAUST_ROOT, SILVER, (-130, -386, 640), purpose='exhaust silencer and stack (adapted from 8285)')
    fuel_tank(s, (130, -175, 0))
    return s


# ------------------------------------------------------------------ assets

ASSETS = {
    'v8': ('assets/atc-v8.mpd', 'atc-v8-00-42082---engine.ldr'),
    'i6': ('assets/atc-i6.mpd', 'atc-i6-00-8285---engine.ldr'),
    'hook': ('assets/atc-hook.mpd', 'atc-hook-00-42082---hook.ldr'),
    'exhaust': ('assets/atc-exhaust.mpd', 'atc-exhaust-00-8285---exhaust1.ldr'),
    'tank': ('assets/atc-tank.mpd', 'atc-tank-00-8285---tank.ldr'),
    'steps': ('assets/atc-steps.mpd', 'atc-steps-00-8285---sidepanel1.ldr'),
    'seat': ('assets/atc-seat.mpd', 'atc-seat-00-42082---seat.ldr'),
    'steer': ('assets/atc-steer.mpd', 'atc-steer-00-42082---steerwheel.ldr'),
}
V8_ROOT = ASSETS['v8'][1]
I6_ROOT = ASSETS['i6'][1]
HOOK_ROOT = ASSETS['hook'][1]
EXHAUST_ROOT = ASSETS['exhaust'][1]
TANK_ROOT = 'atc-tank-00-8285---tank.ldr'


# ------------------------------------------------------------------ superstructure (S frame)
# S origin: slewing axis at the top face of the turntable; -Z = boom direction at slew 0.

TT_WORLD = np.array([0.0, -260.0, -30.0])    # turntable pair origin (world)
S_ORIGIN = TT_WORLD + np.array([0, -30.0, 0])
PIVOT_S = np.array([0.0, -120.0, 150.0])     # boom-frame origin in S (pivot hole sits at B y=-10)
WEB_R = basis(x='-Y', y='X')                 # 64179 standing in the YZ plane, holes along X


def superstructure_section():
    s = Section('atc-super.ldr', 'Revolving superstructure: platform, boom foot plates, operator cab, '
                'transverse inline-six, hoist winch and counterweight')
    s.add('18938', BLACK, (0, 30, 0), purpose='turntable top (60 tooth), rotates with the superstructure')
    s.step()
    for xc in (-100, 0, 100):
        for zc in (-110, 30, 170, 310, 450):
            s.add('64179', DBG, (xc, -10, zc), purpose='revolving platform frame')
    s.step()
    for sx in (-1, 1):
        for yc in (-70, -170):
            s.add('64179', YELLOW, (sx * 80, yc, 170), WEB_R, purpose='boom foot side plate')
    axle(s, 10, (0, -130, 150), 'X', BLACK, purpose='boom pivot shaft')
    s.step()
    # hoist winch on top of the counterweight
    yw, zw = -262, 450
    axle(s, 10, (0, yw, zw), 'X', LBG, purpose='winch shaft')
    for x in (-20, 20):
        s.add('41531', BLACK, (x, yw, zw), basis(z='X', y='Y'), purpose='winch drum (rope wraps)')
    for x in (-50, 50):
        s.add('3736', YELLOW, (x, yw, zw), basis(z='X', y='Y'), purpose='winch drum flange')
    for sx in (-1, 1):
        beam(s, 5, (sx * 80, yw + 40, zw), 'Y', 'X', DBG, purpose='winch upright')
    s.step()
    # transverse inline-six under the engine hood (crank across the platform)
    s.add(I6_ROOT, LBG, (70, -160, 330), basis(z='X', y='Y'), purpose='superstructure inline-six (adapted from 8285)')
    s.step()
    # counterweight: 16-stud slabs, dark grey, yellow cap
    for k in range(6):
        yt = -20 - 24 * (k + 1)
        for zr in range(3):
            s.add('2465', BLACK if k % 2 else DBG, (0, yt, 410 + 20 * zr), purpose='counterweight slab')
        s.add('6112', BLACK if k % 2 else DBG, (0, yt, 470), purpose='counterweight slab (rear)')
        for sx in (-1, 1):
            s.add('3004', RED if (k + (sx > 0)) % 2 else WHITE, (sx * 140, yt, 470), purpose='counterweight warning corner')
    for zc in (420, 460):
        s.add('4282', YELLOW, (0, -172, zc), purpose='counterweight cap plate 2x16')
    s.step()
    # house sides: closed on the left, the right side is left open over the engine (service opening)
    side = basis(x='Z', z='Y')
    for zc in (-60, 160):
        s.add('64782', YELLOW, (150, -70, zc), side, purpose='superstructure house side (right)')
    for zc in (60, 280):
        s.add('64782', YELLOW, (-150, -70, zc), side, purpose='superstructure house side (left)')
    s.add('64782', YELLOW, (0, -196, 330), purpose='engine hood roof')
    s.step()
    operator_cab(s)
    return s


def operator_cab(s):
    """Narrow, tall operator cab on the left of the boom foot (S frame)."""
    x0, z0, floor = -175, -210, -28       # 4 wide (x) by 8 long (z) studs; plate top at -28
    course = [floor - 24 * (k + 1) for k in range(8)]
    s.add('3035', DBG, (x0 + 40, floor, z0 + 80), basis(x='Z', y='Y'), purpose='cab floor 4x8')
    for k, yt in enumerate(course):
        col = BLACK if k == 0 else YELLOW
        if k < 2:
            brick_row(s, (x0 + 10, z0 + 10), 'X', 4, yt, col, 0, 'operator cab front')
            brick_row(s, (x0 + 10, z0 + 30), 'Z', 7, yt, col, k % 2, 'operator cab outer side')
            brick_row(s, (x0 + 70, z0 + 30), 'Z', 7, yt, col, k % 2, 'operator cab inner side')
        else:
            for xs in (x0 + 10, x0 + 70):
                brick_row(s, (xs, z0 + 110), 'Z', 3, yt, YELLOW, 0, 'operator cab side, rear')
        brick_row(s, (x0 + 30, z0 + 150), 'X', 2, yt, col, 0, 'operator cab rear')
    wt = course[-1]
    s.add('57894', BLACK, (x0 + 40, wt, z0 + 10), purpose='operator cab front window frame')
    s.add('57895', TBROWN, (x0 + 40, wt, z0 + 10), purpose='front glass')
    Rz = basis(x='Z', y='Y')
    s.add('57894', BLACK, (x0 + 10, wt, z0 + 60), Rz, purpose='operator cab side window frame')
    s.add('57895', TBROWN, (x0 + 10, wt, z0 + 60), Rz, purpose='side glass')
    s.add('57894', BLACK, (x0 + 70, wt, z0 + 60), Rz, purpose='inner side window frame')
    s.add('57895', TBROWN, (x0 + 70, wt, z0 + 60), Rz, purpose='inner side glass')
    s.add('3035', YELLOW, (x0 + 40, wt - 8, z0 + 80), basis(x='Z', y='Y'), purpose='operator cab roof')
    s.add('3062b', TORANGE, (x0 + 40, wt - 32, z0 + 150), purpose='superstructure beacon')
    s.add('3710', BLACK, (x0 + 40, wt - 16, z0 + 10), purpose='operator cab sun visor')
    for zc in (z0 + 50, z0 + 110):
        s.add('3069b', TCLEAR, (x0 + 40, wt - 16, zc), basis(x='Z', y='Y'), purpose='roof work light')


# ------------------------------------------------------------------ telescopic boom (B frame)
# B origin = boom pivot frame: boom axis along -Z, section bottoms at y ~ 0..+20, tops at -160.
# Profiles: (outer half-width, top y, bottom y); panels: 64782 (100 wide) / 15458 (60 wide).
PROFILES = {
    'B0': dict(hw=70, top=-160, bot=20, panel='64782', side='64782', side_h=100, rows=(-30, -10)),
    'T1': dict(hw=50, top=-140, bot=0, panel='15458', side='15458', side_h=60, rows=(-110, -90), side_yc=-50),
    'T2': dict(hw=30, top=-120, bot=-20, panel='15458', side=None, side_h=0, rows=(-90, -70, -50)),
}


def boom_member(s, name, z_rear, n_panels, colour, beam_colour):
    """One telescopic section from z_rear forward (-Z) in 220-LDU panel bays."""
    p = PROFILES[name]
    hw, top, bot = p['hw'], p['top'], p['bot']
    flat = basis(x='Z', y='Y')
    stand = basis(x='Z', z='Y')
    L = 220 * n_panels
    for k in range(n_panels):
        zc = z_rear - 110 - 220 * k
        s.add(p['panel'], colour, (0, top + 10, zc), flat, purpose=f'{name} top plate')
        s.add(p['panel'], colour, (0, bot - 10, zc), flat, purpose=f'{name} bottom plate')
        if p['side']:
            yc = p.get('side_yc', top + 20 + p['side_h'] / 2)
            for sx in (-1, 1):
                s.add(p['side'], colour, (sx * (hw - 10), yc, zc), stand, purpose=f'{name} side web')
    # longitudinal beam rows (holes along X) and flanges, chained 15-hole beams
    for sx in (-1, 1):
        x = sx * (hw - 10)
        for y in (*p['rows'], top + 10, bot - 10):
            if name == 'T2' and y in (top + 10, bot - 10):
                continue
            holes = 'Y' if y in (top + 10, bot - 10) else 'X'
            z = z_rear
            for n in chain(L // 20):
                beam(s, n, (x, y, z - 10 * n), 'Z', holes, beam_colour, purpose=f'{name} longitudinal member')
                z -= 20 * n
    return z_rear - L


def chain(studs):
    """Split a stud length into available beam lengths (longest first)."""
    out, left = [], studs
    while left:
        for n in (15, 13, 11, 9, 7, 5, 3):
            rest = left - n
            if rest == 0 or rest >= 3:
                out.append(n)
                left = rest
                break
        else:
            raise ValueError(studs)
    return out


def boom_section(ext1, ext2):
    s = Section('atc-boom.ldr', 'Three-section telescopic boom with head sheaves (B frame: pivot origin, axis -Z)')
    b0_tip = boom_member(s, 'B0', 40, 4, YELLOW, BLACK)            # base: z +40 .. -840
    s.step()
    t1_rear = 40 - 20 - ext1                                        # nested, slides forward by ext1
    t1_tip = boom_member(s, 'T1', t1_rear, 4, YELLOW, YELLOW)
    s.step()
    t2_rear = t1_rear - 20 - ext2
    t2_tip = boom_member(s, 'T2', t2_rear, 4, YELLOW, YELLOW)
    s.step()
    # boom head: sheave block at the T2 tip
    zs, ys = t2_tip - 50, -90
    axle(s, 6, (0, ys, zs), 'X', LBG, purpose='head sheave shaft')
    for x in (-10, 10):
        s.add('3736', DBG, (x, ys, zs), basis(z='X', y='Y'), purpose='head sheave')
    for sx in (-1, 1):
        beam(s, 5, (sx * 40, ys, zs + 40), 'Z', 'X', YELLOW, purpose='boom head cheek')
    fly_jib(s, x0=80, y_bot=-30, z0=-150, bays=9)
    # aircraft warning light on the boom head
    s.add('87994', BLACK, (40, ys - 40, zs + 40), basis(x='-Y', y='X'), purpose='head light mast (bar 3L)')
    s.add('3062b', TRED, (40, ys - 94, zs + 40), purpose='aircraft warning light')
    # luffing cylinder lugs under the base section
    for x in (-60, -20, 20, 60):
        beam(s, 3, (x, 50, -LUG_D), 'Y', 'X', BLACK, purpose='luffing cylinder lug')
    axle(s, 8, (0, LUG_Y, -LUG_D), 'X', LBG, purpose='luffing cylinder eye shaft')
    s.anchors['head'] = {'at': clean([0, ys, zs], 3)}
    return s, np.array([0.0, ys, zs]), b0_tip


LUG_D = 330            # distance of the cylinder lugs ahead of the pivot (B frame)
LUG_Y = 50             # eye shaft through the middle hole of the lugs, 30 below the base plate


def fly_jib(s, x0, y_bot, z0, bays):
    """Folded lattice fly-jib stowed on the base section: 80-high Warren truss, 60-long bays.

    Chords are 20-thick beams (holes along X) at x0; each diagonal is two stacked 6x0.5 liftarms
    (end holes 100 apart = 60/80/100 triangle); nodes use 3-layer pins through chord + two diagonals."""
    y_top = y_bot - 80
    L = 60 * bays
    for y in (y_bot, y_top):
        z = z0 + 10
        for n in chain(L // 20 + 1):
            beam(s, n, (x0, y, z - 10 * n), 'Z', 'X', YELLOW, purpose='fly-jib chord')
            z -= 20 * n
    for k in range(bays):
        za, zb = z0 - 60 * k, z0 - 60 * (k + 1)
        ya, yb = (y_bot, y_top) if k % 2 == 0 else (y_top, y_bot)
        a, b = np.array([0, ya, za], float), np.array([0, yb, zb], float)
        d = (b - a) / np.linalg.norm(b - a)
        layer = x0 + 20 if k % 2 == 0 else x0 + 40
        for dx in (-5, 5):
            c = (a + b) / 2 + np.array([layer + dx, 0, 0])
            s.add('32063', YELLOW, c, basis(y='X', z=d), purpose='fly-jib diagonal (doubled 6x0.5 liftarm)')
    for k in range(bays + 1):
        z = z0 - 60 * k
        bottom = k % 2 == 0
        y = y_bot if bottom else y_top
        both = 0 < k < bays
        if bottom:      # through the boom's side hole row as well
            axle(s, 4 if both else 3, (x0 + (10 if both else 0), y, z), 'X', BLACK,
                 purpose='fly-jib node shaft (boom row, chord, diagonals)')
        else:
            pin(s, (x0 + (20 if both else 10), y, z), 'X', BLACK, long=both,
                purpose='fly-jib node pin (chord + diagonals)')
    for k in range(bays):
        pin(s, (x0 - 10, y_bot, z0 - 60 * k - 20), 'X', BLACK, purpose='fly-jib stowage pin into the base section')


def luff_matrix(deg):
    return rot('x', -deg)


# ------------------------------------------------------------------ assembly

def carrier_section():
    s = Section('atc-carrier.ldr', 'Carrier: frame, axle stations, bodywork, cab, outriggers and engine bay')
    s.add('atc-frame.ldr', 16, (0, 0, 0), purpose='ladder frame')
    s.add('atc-rear.ldr', 16, (0, 0, 0), purpose='rear engine bay')
    s.step()
    for i, z in enumerate(AXLE_Z):
        name = 'atc-axle-driven.ldr' if i in (1, 2) else 'atc-axle.ldr'
        R = np.eye(3)                                  # struts sit behind every axle
        s.add(name, 16, (0, YW, z), R, purpose=f'axle station {i + 1}')
    s.step()
    s.add('atc-body.ldr', 16, (0, 0, 0), purpose='bodywork')
    s.add('atc-cab.ldr', 16, (0, 0, 0), purpose='driver cab')
    s.add('atc-front.ldr', 16, (0, 0, 0), purpose='front equipment box and boom rest')
    s.add('18939', LBG, TT_WORLD, purpose='turntable bottom (60 tooth) on the deck crossmembers')
    s.step()
    for z in (-100, 560):
        s.add('atc-outrigger.ldr', 16, (90, -127, z), purpose='right outrigger')
        s.add('atc-outrigger.ldr', 16, (-90, -127, z), ROT180, purpose='left outrigger')
    return s


POSE = dict(slew=0.0, luff=40.0, ext1=440, ext2=440, hook_drop=400)
LA_EYES = np.array([0.0, -20.0, 285.0])      # 61927-f2: rear clevis -> front eye (local), measured


def la_matrix(direction):
    """Rotation about X taking the actuator's eye-to-eye vector onto `direction` (YZ plane)."""
    u = LA_EYES / np.linalg.norm(LA_EYES)
    d = direction / np.linalg.norm(direction)
    a = np.arctan2(d[1], d[2]) - np.arctan2(u[1], u[2])
    return rot('x', -np.degrees(a))


STRINGS = [(800, '71149'), (600, '14225'), (400, '75924'), (200, '76384')]


def string_run(sec, a, b, purpose):
    """Lay braided strings (41L/31L/21L/11L, end-stud spans 800/600/400/200) along a straight line."""
    a, b = np.array(a, float), np.array(b, float)
    L = np.linalg.norm(b - a)
    d = (b - a) / L
    best = None
    for n8 in range(0, 6):
        for n6 in range(0, 2):
            for n4 in range(0, 2):
                for n2 in range(0, 2):
                    tot = 800 * n8 + 600 * n6 + 400 * n4 + 200 * n2
                    if tot and (best is None or abs(tot - L) < abs(best[0] - L)):
                        best = (tot, [800] * n8 + [600] * n6 + [400] * n4 + [200] * n2)
    spans = best[1]
    scale = L / best[0]              # distribute any residual as small end overlaps/gaps along the line
    R = basis(x=d, y=perp_to(d))
    pos = 0.0
    for span in spans:
        ref = dict((sp, r) for sp, r in STRINGS)[span]
        centre = a + d * (pos + span / 2) * scale
        sec.add(ref, BLACK, centre, R, purpose=purpose)
        pos += span


def perp_to(d):
    up = np.array([0, -1.0, 0])
    p = up - np.dot(up, d) * d
    if np.linalg.norm(p) < 1e-6:
        p = np.array([1.0, 0, 0]) - np.dot([1.0, 0, 0], d) * d
    return p / np.linalg.norm(p)


def luff_base_z(R_luff, x, y_base=-40.0):
    """Platform position (S frame z) of a cylinder base exactly one actuator length from the lug."""
    L = np.linalg.norm(LA_EYES)
    P = PIVOT_S + R_luff @ np.array([x, LUG_Y, -LUG_D])
    dy = P[1] - y_base
    if abs(dy) > L:
        raise ValueError('luffing cylinder too short for this luff angle')
    return P, P[2] + np.sqrt(L * L - dy * dy)


def build(stage, pose=POSE):
    slew, luff = pose['slew'], pose['luff']
    Rs = rot('y', slew)
    F_S = Frame(Rs, S_ORIGIN)
    R_luff = luff_matrix(luff)
    F_B = F_S @ Frame(R_luff, PIVOT_S)

    boom, head_B, _ = boom_section(pose['ext1'], pose['ext2'])
    main = Section('atc-main.ldr', 'Atlas AT-90 all-terrain crane (original design) - working pose')
    main.add('atc-carrier.ldr', 16, (0, 0, 0), purpose='carrier')
    main.step()
    main.add('atc-super.ldr', 16, F_S.t, F_S.R, purpose=f'superstructure, slewed {slew:g} deg')
    main.add('atc-boom.ldr', 16, F_B.t, F_B.R, purpose=f'telescopic boom, luffed {luff:g} deg')
    main.step()
    # twin luffing cylinders: rear clevis on the platform front, eye under the base section
    for x in (-40, 40):
        tip, zb = luff_base_z(R_luff, 0.0)
        tip[0] = x
        base = np.array([x, -40.0, zb])
        d = (tip - base) / np.linalg.norm(tip - base)
        R_la = (2 * np.outer(d, d) - np.eye(3)) @ la_matrix(tip - base)   # rolled 180: clevis bulge away from boom
        origin = base - R_la @ np.array([0, 20.0, 0])     # local rear clevis (0,20,0) on `base`
        main.add('61927-f2', DBG, F_S.p(origin), F_S.R @ R_la, purpose='luffing cylinder (linear actuator, extended)')
    main.step()
    # hoist rope: winch drum top -> head sheave top, braided strings end to end
    head_w = F_B.p(head_B)
    start = F_S.p(np.array([0, -302.0, 450]))
    end = F_B.p(head_B + np.array([0, -47.0, 0]))
    string_run(main, start, end, 'hoist rope run (braided string)')
    # two falls hang vertically from the front of the head sheaves, then the hook block and hook
    fwd = Rs @ np.array([0, 0, -1.0])
    across = Rs @ np.array([1.0, 0, 0])
    top = head_w + 47 * fwd
    drop = pose['hook_drop']
    for o in (-10, 10):
        string_run(main, top + o * across, top + o * across + np.array([0, drop, 0]), 'hoist rope fall')
    block = top + np.array([0, drop + 41, 0])
    main.add(HOOK_ROOT, RED, block, Rs @ basis(x='Z', z='-X'), purpose='hook block (adapted from 42082)')
    main.add('70644', LBG, block + np.array([0, 69 + 29, 0]), Rs, purpose='crane hook')

    secs = [main, carrier_section(), frame_section(), rear_bay_section(),
            axle_section('atc-axle.ldr', driven=False), axle_section('atc-axle-driven.ldr', driven=True),
            wheel_section(), body_section(), cab_section(), front_box_section(), outrigger_section(), hood_section(),
            superstructure_section(), boom]
    return secs, [ASSETS[k][0] for k in ('v8', 'exhaust', 'i6', 'hook')]


def derive_recoloured(src, dst, mapping, note):
    """Copy an extracted asset, changing only type-1 placement colours; record the change beside it."""
    src, dst = HERE / src, HERE / dst
    out, changed = [], 0
    for line in src.read_text().splitlines(keepends=True):
        f = line.split()
        if len(f) >= 15 and f[0] == '1' and f[1].isdigit() and int(f[1]) in mapping:
            f[1] = str(mapping[int(f[1])])
            line = ' '.join(f) + ('\r\n' if line.endswith('\r\n') else '\n')
            changed += 1
        out.append(line)
    dst.write_text(''.join(out))
    dst.with_suffix('.derived.json').write_text(json.dumps(
        {'derived_from': str(src.relative_to(HERE)), 'colour_mapping': {str(k): v for k, v in mapping.items()},
         'placements_recoloured': changed, 'note': note}, indent=1) + '\n')


def write_plan(secs, path, assets=()):
    plan = {'version': 1, 'author': AUTHOR, 'sections': [s.plan() for s in secs]}
    if assets:
        plan['assets'] = list(assets)
    path.write_text(json.dumps(plan, indent=1) + '\n')
    n = sum(s.count() for s in secs)
    print(f'wrote {path} ({len(secs)} sections, {n} direct placements)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', default='carrier')
    ap.add_argument('--out', default=str(HERE / 'atlas-crane.plan.json'))
    for k, val in POSE.items():
        ap.add_argument('--' + k.replace('_', '-'), type=float, default=val)
    a = ap.parse_args()
    pose = {k: getattr(a, k) for k in POSE}
    secs, assets = build(a.stage, pose)
    write_plan(secs, Path(a.out), assets)
