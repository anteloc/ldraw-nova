"""Deterministic structure for the Linden Row run 3 (orchestrator-owned).

Builds the structural submodels of every storey (slab, walls, ring) and the roof deck from WALLS,
and exposes the exact SNOT mount stud points that task agents must use (mounts()).

Module-local coordinates: X/Z in studs (cell centres at .5), h in LDU up; front = -Z.
Wall courses k = 0..5: body h [8+24k, 32+24k]; a side-stud brick in course k has its studs at h = 22+24k.
"""
from __future__ import annotations
import sys
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
if str(RUN) not in sys.path:
    sys.path.insert(0, str(RUN))
from common import PALETTE, Ry, FACE_YAW, add_ldu, side_studs, panel_R, seat, clean  # noqa: E402
from ldraw_tools.architecture import Module, line, slab, ring, window4, door4  # noqa: E402

W, D = 24, 16
FACE_OF = {'front': '-Z', 'back': '+Z', 'left': '-X', 'right': '+X'}
WIDTH = {'30414': 4, '11211': 2, '87087': 1, '4070': 1}

# opening: (face, a0, a1, k0, k1, frame)  a = X for front/back (-12..12), Z for left/right (-7..7)
# frame: None (left open for a task submodel), 'window' (window4, 3 courses) or 'door' (door4, 6 courses)
# mount:   (name, face, a0, a1, k, ref)  -> side-stud bricks filling a0..a1 in course k
WALLS = {
    'ground': dict(body=PALETTE['stone'], trim=PALETTE['accent'], openings=[
        ('front', -10, 10, 0, 3, None),               # shopfront (ground-shopfront)
        ('left', -2, 2, 1, 3, 'window'), ('right', -2, 2, 1, 3, 'window'),
        ('back', -2, 2, 0, 5, 'door'), ('back', -8, -4, 1, 3, 'window'), ('back', 4, 8, 1, 3, 'window'),
    ], mounts=[
        ('pier-L', 'front', -12, -10, 2, '11211'), ('pier-R', 'front', 10, 12, 2, '11211'),
        ('lintel', 'front', -10, 10, 4, '30414'),     # awning seat (studs h 118)
        ('fascia', 'front', -10, 10, 5, '30414'),     # sign seat (studs h 142)
        ('rear-head-L', 'back', -8, -4, 4, '30414'), ('rear-head-R', 'back', 4, 8, 4, '30414'),
    ]),
    'floor2': dict(body=PALETTE['brick'], trim=PALETTE['trim'], openings=[
        ('front', -10, -6, 1, 3, 'window'), ('front', 6, 10, 1, 3, 'window'),
        ('front', -4, 4, 1, 3, None),                 # bay opening (floor2-bay)
        ('left', -2, 2, 1, 3, 'window'), ('right', -2, 2, 1, 3, 'window'),
        ('back', -8, -4, 1, 3, 'window'), ('back', 4, 8, 1, 3, 'window'),
    ], mounts=[
        ('head-L', 'front', -10, -6, 4, '30414'), ('head-R', 'front', 6, 10, 4, '30414'),
        ('pier-L', 'front', -12, -10, 2, '11211'), ('pier-R', 'front', 10, 12, 2, '11211'),
        ('pier-CL', 'front', -6, -4, 2, '11211'), ('pier-CR', 'front', 4, 6, 2, '11211'),
        ('box-L', 'front', -9, -7, 0, '4070'), ('box-R', 'front', 7, 9, 0, '4070'),
        ('rear-head-L', 'back', -8, -4, 4, '30414'), ('rear-head-R', 'back', 4, 8, 4, '30414'),
    ]),
    'floor3': dict(body=PALETTE['brick'], trim=PALETTE['trim'], openings=[
        ('front', -2, 2, 0, 5, None),                 # French doors (floor3-french-doors)
        ('front', -10, -6, 1, 4, None), ('front', 6, 10, 1, 4, None),   # tall windows (floor3-windows)
        ('left', -2, 2, 1, 3, None), ('right', -2, 2, 1, 3, None),
        ('back', -8, -4, 1, 3, None), ('back', 4, 8, 1, 3, None),
    ], mounts=[
        ('cornice-L', 'front', -12, -2, 0, '30414'), ('cornice-R', 'front', 2, 12, 0, '30414'),
        ('pilaster-L', 'front', -4, -2, 2, '11211'), ('pilaster-R', 'front', 2, 4, 2, '11211'),
        ('rear-head-L', 'back', -8, -4, 4, '30414'), ('rear-head-R', 'back', 4, 8, 4, '30414'),
    ]),
}
for spec in WALLS.values():  # cornice-L/R: 10 cells -> 30414 + 30414 + 11211 handled by fill
    pass


def _cells(face):
    return list(range(-12, 12)) if face in ('front', 'back') else list(range(-7, 7))


def _cell_xyz(face, a):
    """LDU (x, z) of the centre of wall cell a (a = lower stud coordinate along the face)."""
    if face == 'front':
        return (a + .5) * 20, -7.5 * 20
    if face == 'back':
        return (a + .5) * 20, 7.5 * 20
    if face == 'left':
        return -11.5 * 20, (a + .5) * 20
    return 11.5 * 20, (a + .5) * 20


def _brick_runs(a0, a1, ref):
    """Split [a0, a1) into side-stud bricks of `ref`, filling the remainder with smaller side-stud bricks."""
    out, a = [], a0
    order = [ref] + [r for r in ('30414', '11211', '87087') if WIDTH[r] < WIDTH[ref]]
    while a < a1:
        r = next(r for r in order if a + WIDTH[r] <= a1)
        out.append((a, r)); a += WIDTH[r]
    return out


def mounts(module):
    """{name: {face, refs, studs:[(x,y,z) LDU module-local], course k, stud_h}} for the module's SNOT mounts."""
    out = {}
    for name, face, a0, a1, k, ref in WALLS.get(module, {}).get('mounts', []):
        studs, refs = [], []
        for a, r in _brick_runs(a0, a1, ref):
            w = WIDTH[r]
            cx, cz = _cell_xyz(face, a)
            if face in ('front', 'back'):
                cx += (w - 1) * 10
            else:
                cz += (w - 1) * 10
            top = -(32 + 24 * k)
            studs += side_studs(r, (cx, top, cz), FACE_OF[face])
            refs.append(r)
        out[name] = dict(face=FACE_OF[face], refs=refs, course=k, stud_h=22 + 24 * k,
                         studs=[tuple(round(v, 3) for v in s) for s in studs])
    return out


def walls(module):
    spec = WALLS[module]
    m = Module(f'{module}-walls', f'{module} wall core: 1-stud perimeter, openings, SNOT mount courses (orchestrator core)')
    body, trim = spec['body'], spec['trim']
    for k in range(6):
        m.step()
        top = 32 + 24 * k
        for face in ('front', 'back', 'left', 'right'):
            cells = _cells(face)
            blocked = set()
            for f, a0, a1, k0, k1, _ in spec['openings']:
                if f == face and k0 <= k <= k1:
                    blocked |= set(range(a0, a1))
            mounted = {}
            for name, f, a0, a1, kk, ref in spec['mounts']:
                if f == face and kk == k:
                    for a, r in _brick_runs(a0, a1, ref):
                        mounted[a] = r
                        blocked |= set(range(a, a + WIDTH[r]))
            # side-stud bricks
            for a, r in mounted.items():
                w = WIDTH[r]
                cx, cz = _cell_xyz(face, a)
                if face in ('front', 'back'):
                    cx += (w - 1) * 10
                else:
                    cz += (w - 1) * 10
                add_ldu(m, r, body, (cx, -top, cz), Ry(FACE_YAW[FACE_OF[face]]))
            # plain runs
            i = 0
            while i < len(cells):
                if cells[i] in blocked:
                    i += 1; continue
                j = i
                while j < len(cells) and cells[j] not in blocked:
                    j += 1
                n = j - i
                a = cells[i]
                if face in ('front', 'back'):
                    line(m, a, -7.5 if face == 'front' else 7.5, n, top, body, bond=bool(k % 2))
                else:
                    line(m, -11.5 if face == 'left' else 11.5, a, n, top, body, axis='z', bond=bool(k % 2))
                i = j
    m.step()
    for f, a0, a1, k0, k1, frame in spec['openings']:
        if not frame:
            continue
        yaw = {'front': 0, 'back': 180, 'left': 90, 'right': -90}[f]
        mid = (a0 + a1) / 2
        x = mid if f in ('front', 'back') else (-11.5 if f == 'left' else 11.5)
        z = (-7.5 if f == 'front' else 7.5) if f in ('front', 'back') else mid
        unit = door4(PALETTE['trim'], PALETTE['door']) if frame == 'door' else window4(PALETTE['trim'], PALETTE['glass'])
        m.add(unit, PALETTE['trim'], x, 8 + 24 * k0, z, yaw=yaw)
    return m


def storey_slab(module):
    """Every plate runs front-to-back and rests on the front and/or back ring cells of the storey below.
    floor2: centre X -4..4 extends to Z -10 (bay floor); floor3: centre X -6..6 extends to Z -11 (balcony deck).
    Plates 3027 (6x16), 4282 (2x16) yawed 90 = 16 along Z; 3021 (2x3) / 3034 (2x8) back fillers touch the back ring."""
    m = Module(f'{module}-slab', f'{module} floor slab: front-to-back plates resting on the ring below (orchestrator core)')
    c = PALETTE['door']
    if module == 'floor2':
        m.add('3027', c, -9, 8, 0, yaw=90); m.add('4282', c, -5, 8, 0, yaw=90)
        m.add('4282', c, 5, 8, 0, yaw=90); m.add('3027', c, 9, 8, 0, yaw=90)
        m.add('3027', c, -1, 8, -2, yaw=90); m.add('4282', c, 3, 8, -2, yaw=90)   # Z -10..6
        m.add('3034', c, 0, 8, 7)                                                   # Z 6..8, X -4..4
    elif module == 'floor3':
        m.add('3027', c, -9, 8, 0, yaw=90); m.add('3027', c, 9, 8, 0, yaw=90)
        m.add('3027', c, -3, 8, -3, yaw=90); m.add('3027', c, 3, 8, -3, yaw=90)     # Z -11..5
        for x in (-5, -3, -1, 1, 3, 5):
            m.add('3021', c, x, 8, 6.5, yaw=90)                                     # Z 5..8
    else:
        for x in (-9, -3, 3, 9):
            m.add('3027', c, x, 8, 0, yaw=90)
    return m


def storey_ring(module):
    m = Module(f'{module}-ring', f'{module} top interface ring, top h=160')
    ring(m, W, D, 160, PALETTE['trim'])
    return m


def roof_deck():
    m = Module('roof-deck', 'roof deck: four 6x16 plates 3027 on floor3 ring; studs left exposed for parapets and features')
    for x in (-9, -3, 3, 9):
        m.add('3027', PALETTE['roof'], x, 8, 0, yaw=90)
    return m


CORE = {
    'ground': ['ground-slab', 'ground-walls', 'ground-ring'],
    'floor2': ['floor2-slab', 'floor2-walls', 'floor2-ring'],
    'floor3': ['floor3-slab', 'floor3-walls', 'floor3-ring'],
    'roof': ['roof-deck'],
    'street': [],
}


def build_core(module):
    """Root Module for `module` with its core submodels placed at the origin."""
    root = Module(module, f'Linden Row run 3: {module}')
    if module in WALLS:
        root.anchor('next', h=160)
        for sub in (storey_slab(module), walls(module), storey_ring(module)):
            root.add(sub, 71, id=sub.name)
    elif module == 'roof':
        root.add(roof_deck(), 71, id='roof-deck')
    return root


class Ctx:
    """What a task's parts/<submodel>.py build(ctx) receives."""
    def __init__(self, module):
        import ldraw_tools.architecture as A
        self.module_name = module
        self.Module = Module
        self.add = add_ldu            # add(m, ref_or_Module, colour, [X,Y,Z] LDU, R=None)
        self.panel_R, self.seat, self.side_studs, self.Ry, self.clean = panel_R, seat, side_studs, Ry, clean
        self.PALETTE = PALETTE
        self.mounts = mounts(module)
        self.A = A                    # architecture helpers: A.line, A.slab, A.ring, A.window4, A.door4, A.lamp, ...
