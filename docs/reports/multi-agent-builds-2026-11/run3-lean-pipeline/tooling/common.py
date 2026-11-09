"""Shared helpers for the Linden Row urban house modules (orchestrator-owned; do not edit).

Every module generator builds an ldraw_tools.architecture.Module tree and calls
export(root_module, prefix, folder, author). export():
  * namespaces every non-root section name as '<prefix>-<name>.ldr' so module
    plans can all be included by one scene without duplicate section names
    (architecture helpers such as window4() reuse fixed names);
  * writes <folder>/<root>.plan.json   (included by the scene)
  * writes <folder>/test.plan.json     (standalone harness: places the root at the origin)
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

STOREY = 160          # LDU, slab underside to top of plate ring (room(rows=6))
FOOTPRINT = (24, 16)  # studs, X by Z; local origin = footprint centre, bottom Y=0, front -Z

PALETTE = dict(
    brick=320,        # dark red  - upper floor walls
    stone=72,         # dark bluish grey - ground floor rusticated base
    trim=15,          # white - window frames, cornice, copings
    accent=19,        # tan - sills, quoins, string courses
    shop=288,         # dark green - shopfront, awning stripes
    door=70,          # reddish brown - doors, floors, timber
    glass=47,         # trans clear
    metal=0,          # black - railings, lamp, ironwork
    roof=72,          # dark bluish grey - roof deck
    paving=71,        # light bluish grey - sidewalk
    kerb=72,
    green=2,          # green foliage
    flower=5,         # red flowers  (also 14 yellow, 1 blue)
)


def export(root, prefix, folder, author):
    folder = Path(folder)
    plan = root.plan()
    plan['author'] = author
    root_name = root.name + '.ldr'
    rename = {}
    for s in plan['sections']:
        if s['name'] != root_name and not s['name'].startswith(prefix + '-'):
            rename[s['name']] = f"{prefix}-{s['name']}"
    for s in plan['sections']:
        s['name'] = rename.get(s['name'], s['name'])
        for step in s['steps']:
            for p in step:
                p['ref'] = rename.get(p['ref'], p['ref'])
    out = folder / f'{root.name}.plan.json'
    out.write_text(json.dumps(plan, indent=1))
    test = dict(version=1, author=author, includes=[out.name], sections=[dict(
        name=f'{root.name}-test.ldr', description=f'Standalone harness for {root_name}',
        steps=[[dict(id='module', ref=root_name, colour=PALETTE['stone'], at=[0, 0, 0])]])])
    (folder / 'test.plan.json').write_text(json.dumps(test, indent=1))
    n = sum(len(st) for s in plan['sections'] for st in s['steps'])
    print(json.dumps(dict(plan=str(out), test=str(folder / 'test.plan.json'),
                          sections=len(plan['sections']), placements=n)))
    return out


# ----------------------------------------------------------------------------------------------
# SNOT helpers (verified by kit/snot_kit.py — see its docstring for measured contact counts)
# ----------------------------------------------------------------------------------------------
import numpy as np

def Ry(deg):
    a = np.radians(deg); c, s = round(float(np.cos(a)), 12), round(float(np.sin(a)), 12)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)

# Side-stud bricks (30414 1x4, 11211 1x2, 87087 1x1, 4070 headlight) carry their side studs on the
# local -Z face. yaw that turns those studs to face each world direction:
FACE_YAW = {'-Z': 0, '+X': -90, '+Z': 180, '-X': 90}
FACE_VEC = {'-Z': (0, 0, -1), '+X': (1, 0, 0), '+Z': (0, 0, 1), '-X': (-1, 0, 0)}

# A section/part built FLAT (studs up, local -Y) turned so its studs point -Z (out of a front wall)
# and its sockets (+Y) point +Z (into the wall). Local +X stays world +X; local +Z becomes world UP (-Y).
_R0 = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)

def panel_R(face='-Z'):
    """Rotation for a flat-built panel whose studs must face `face` ('-Z','+X','+Z','-X')."""
    return Ry(FACE_YAW[face]) @ _R0

def seat(R, socket, stud):
    """Origin that puts the moving part's local `socket` exactly on world/parent `stud`: stud - R*socket."""
    return np.asarray(stud, float) - np.asarray(R, float) @ np.asarray(socket, float)

def clean(v):
    out = float(round(float(v), 6)); return 0.0 if out == 0 else out

def add_ldu(m, ref, colour, at, R=None, *, id=None, purpose=None):
    """Module.add with an LDU position [X,Y,Z] (Y down) and an optional 3x3 proper rotation."""
    x, y, z = (clean(v) for v in at)
    mat = None if R is None or np.allclose(R, np.eye(3)) else [[clean(v) for v in row] for row in np.asarray(R)]
    return m.add(ref, colour, x / 20, -y, z / 20, matrix=mat, id=id, purpose=purpose)

def side_studs(ref, origin, face='-Z'):
    """World positions of the side-stud bases of a side-stud brick placed at `origin` (its top centre)
    with its studs facing `face`. Unrotated local stud bases: x in {..}, y=+10 (10 LDU below the top), z=-10
    (z=-6 for the recessed 4070 headlight brick)."""
    local = {'30414': [(-30, 10, -10), (-10, 10, -10), (10, 10, -10), (30, 10, -10)],
             '11211': [(-10, 10, -10), (10, 10, -10)],
             '87087': [(0, 10, -10)],
             '4070':  [(0, 10, -6)]}[ref.replace('.dat', '')]
    R = Ry(FACE_YAW[face])
    return [tuple(clean(v) for v in np.asarray(origin, float) + R @ np.array(p, float)) for p in local]

# Vertical rule: side studs sit 10 LDU below each brick top. Studs from two courses can only both
# mate one panel if the courses' stud rows are a multiple of 20 LDU apart (e.g. 40 = one brick + two
# plates). Bricks stacked directly are 24 apart -> a panel can use only ONE of those courses.
