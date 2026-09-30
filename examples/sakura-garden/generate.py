"""Sakura Garden: a five-storey pagoda above a koi pond in cherry-blossom season.

Writes an editable JSON plan; build it with `./ldraw-agent build`. Authoring
coordinates follow ldraw_tools.architecture: X/Z in studs, h in LDU upwards,
every module has its bottom at h=0 and faces -Z. Part frames were measured
with `ldraw-agent part`; the notes in design-brief.md list them.

Usage:
    .venv/bin/python output/sakura-garden/generate.py [--main NAME]

`--main` writes a prototype plan whose root is one module (module review).
"""
from __future__ import annotations

import argparse
import json
import math
import zlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from ldraw_tools.architecture import Module  # noqa: E402

AUTHOR = 'ldraw-nova sakura-garden generator'
ROOT = Path(__file__).resolve().parent

C = dict(
    post=4,          # Red: vermilion posts, lattice, corbels, bridge, torii
    wall=15,         # White plaster panels
    shadow=320,      # Dark_Red eave decks and screens behind lattice
    roof=72,         # Dark_Bluish_Grey roof tiles
    gold=297,        # Pearl_Gold spire, bells, eave tips, finials
    stone=71,        # Light_Bluish_Grey plinth, lanterns, footings
    ink=0,           # Black torii kasagi and strut
    earth=28,        # Dark_Tan hidden terrain layers and bank faces
    moss=2,          # Green lawn
    deep_moss=288,   # Dark_Green moss under trees, pine needles
    path=19,         # Tan flagstone path
    gravel=15,       # White raked gravel
    pond=272,        # Dark_Blue pond bed
    water=41,        # Trans_Medium_Blue water surface
    bark=70,         # Reddish_Brown trunks and branches
    blossom=29,      # Bright_Pink blossom foliage
    blush=13,        # Pink blossom foliage
    petal=15,        # White petals
    rose=5,          # Dark_Pink petal accents
    glow=46,         # Trans_Yellow lantern light
    bamboo=2,        # Green bamboo
    young_bamboo=10, # Bright_Green bamboo
    koi_water=321,   # Dark_Azure background of the printed koi tiles
    rake=151,        # Very_Light_Bluish_Grey alternate raked-gravel rows
    skin=14,         # Yellow minifigure skin
    iris=30,         # Medium_Lavender pond-side irises
    saffron=25,      # Orange monk's robe
)
G = 24               # terrain top: three plate layers on the baseplate

# Footprint centre of parts whose origin is not their footprint centre, in the
# part's own frame (LDU, x, z). Slopes: origin on the high stud row, low edge
# toward local -Z.
LOCAL = {
    '3039': (0, -10), '3040b': (0, -10), '3298': (0, -20), '4286': (0, -20),
    '3045': (10, -10), '3675': (20, -20), '3665b': (0, -10),
}


def yaw_matrix(deg):
    c, s = round(math.cos(math.radians(deg)), 12), round(math.sin(math.radians(deg)), 12)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def rotate(deg, x, z):
    r = yaw_matrix(deg)
    return r[0][0] * x + r[0][2] * z, r[2][0] * x + r[2][2] * z


def outward_yaw(dx, dz):
    """Yaw that turns local -Z toward the world direction (dx, dz)."""
    return round(math.degrees(math.atan2(-dx, -dz)), 6)


def put(m, ref, colour, cx, h, cz, yaw=0, purpose=None):
    """Place a part by its footprint centre (studs) rather than its origin."""
    lx, lz = LOCAL.get(ref, (0, 0))
    ox, oz = rotate(yaw, lx, lz)
    return m.add(ref, colour, round(cx - ox / 20, 6), h, round(cz - oz / 20, 6),
                 yaw=yaw, purpose=purpose)


# ---------------------------------------------------------------- tilers

PLATE = {  # (along-x, along-z) -> part at yaw 0; the tiler also uses swaps
    (1, 1): '3024', (2, 1): '3023b', (3, 1): '3623', (4, 1): '3710', (6, 1): '3666',
    (8, 1): '3460', (10, 1): '4477',
    (2, 2): '3022', (3, 2): '3021', (4, 2): '3020', (6, 2): '3795', (8, 2): '3034',
    (10, 2): '3832', (12, 2): '2445', (14, 2): '91988', (16, 2): '4282',
    (4, 4): '3031', (6, 4): '3032', (8, 4): '3035', (10, 4): '3030', (12, 4): '3029',
    (6, 6): '3958', (8, 6): '3036', (10, 6): '3033', (12, 6): '3028', (14, 6): '3456',
    (16, 6): '3027', (8, 8): '41539', (16, 8): '92438', (16, 16): '91405',
}
TILE = {(1, 1): '3070b', (2, 1): '3069b', (3, 1): '63864', (4, 1): '2431', (6, 1): '6636',
        (8, 1): '4162', (2, 2): '3068b', (4, 2): '87079'}
BRICK = {(1, 1): '3005', (2, 1): '3004', (3, 1): '3622', (4, 1): '3010', (6, 1): '3009',
         (8, 1): '3008', (2, 2): '3003', (3, 2): '3002', (4, 2): '3001', (6, 2): '2456'}
GRILLE = {(2, 1): '2412b', (1, 1): '3070b'}


def cover(cells, table, *, prefer='x'):
    """Greedy rectangle cover of unit cells (i, j) with real part sizes.

    Returns (part, i0, j0, w, d), w along X and d along Z; largest area first
    so big parts bind a layer, `prefer` breaks orientation ties.
    """
    cells = set(cells)
    sizes = []
    for (a, b), ref in table.items():
        sizes.append((a, b, ref))
        if a != b:
            sizes.append((b, a, ref))
    along = (lambda s: s[1] > s[0]) if prefer == 'x' else (lambda s: s[0] > s[1])
    sizes.sort(key=lambda s: (-(s[0] * s[1]), along(s)))
    out = []
    for i, j in sorted(cells, key=lambda c: (c[1], c[0])):
        if (i, j) not in cells:
            continue
        for w, d, ref in sizes:
            block = {(i + a, j + b) for a in range(w) for b in range(d)}
            if block <= cells:
                cells -= block
                out.append((ref, i, j, w, d))
                break
        else:
            raise ValueError(f'cannot cover cell {(i, j)}')
    return out


def lay(m, cells, h, colour, table=PLATE, *, prefer='x', purpose=None, colour_of=None):
    """Lay parts over unit cells whose lower corners are (i, j) in studs."""
    for ref, i, j, w, d in cover(cells, table, prefer=prefer):
        yaw = 0 if table.get((w, d)) == ref else 90
        c = colour_of(i, j) if colour_of else colour
        m.add(ref, c, i + w / 2, h, j + d / 2, yaw=yaw, purpose=purpose)


def rect(x0, z0, w, d):
    return {(x0 + a, z0 + b) for a in range(w) for b in range(d)}


def ring_cells(n, k=0):
    """Cells of ring k (0 = outermost) of an n x n square centred on the origin."""
    lo, hi = -n // 2 + k, n // 2 - 1 - k
    return {(i, j) for i in range(lo, hi + 1) for j in range(lo, hi + 1)
            if i in (lo, hi) or j in (lo, hi)}


def split(n, odd):
    """Brick lengths for a run of n cells; odd courses start short to bond."""
    out, first = [], odd and n > 2
    while n:
        k = 1 if first and n > 1 and n % 2 else (2 if first else min(4, n))
        k = min(k, n)
        out.append(k)
        n -= k
        first = False
    return out


# ---------------------------------------------------------------- pagoda

def side_cells(n):
    """Perimeter cells of an n x n core, corners excluded: (side, cx, cz, yaw_out)."""
    half = n / 2
    for side, yaw in [('front', 0), ('right', -90), ('back', 180), ('left', 90)]:
        for i in range(n - 2):
            t = -half + 1.5 + i
            yield {'front': (side, t, -half + .5, yaw), 'back': (side, -t, half - .5, yaw),
                   'right': (side, half - .5, t, yaw), 'left': (side, -half + .5, -t, yaw)}[side]


def corners(n, inset=.5):
    h = n / 2 - inset
    return [(-h, -h), (h, -h), (h, h), (-h, h)]


def wall_side(m, core, side, row, h, lo, opening, win):
    """One course of one side: white plaster with vermilion posts flanking the window."""
    nside = core - 2
    flank = {lo - 1, lo + opening} if lo >= 1 else set()
    idx = [i for i in range(nside) if not (row >= 1 and i in win)]
    runs, cur = [], []
    for i in idx:
        colour = C['post'] if i in flank else C['wall']
        if cur and (i != cur[-1][0] + 1 or colour != cur[-1][1]):
            runs.append(cur)
            cur = []
        cur.append((i, colour))
    if cur:
        runs.append(cur)
    for run in runs:
        start = run[0][0]
        for n in split(len(run), row % 2 == 1):
            mid = start + (n - 1) / 2
            t = -core / 2 + 1.5 + mid
            ref, colour = BRICK[(n, 1)], run[0][1]
            if side == 'front':
                m.add(ref, colour, t, h, -core / 2 + .5)
            elif side == 'back':
                m.add(ref, colour, -t, h, core / 2 - .5)
            elif side == 'right':
                m.add(ref, colour, core / 2 - .5, h, t, yaw=90)
            else:
                m.add(ref, colour, -core / 2 + .5, h, -t, yaw=90)
            start += n


def storey(k, core, roof, *, rows=3, opening=4):
    """One pagoda storey: walls, lattice windows, corbels, deck and flared roof.

    Local frame: wall bottom at h=0 (the deck top of the storey below), centred
    on the core. Anchor `next` is this deck's top; the next storey stands there
    and this roof's slope ring hides its lowest course.
    """
    m = Module(f'pagoda-storey-{k}',
               f'Pagoda storey {k + 1}: {core}x{core} stud core of white plaster and '
               f'vermilion posts, lattice windows, corbelled eaves and a {roof}x{roof} '
               'flared roof with gilded tips and hanging bells')
    post = C['post']
    nside = core - 2
    lo = (nside - opening) // 2
    win = set(range(lo, lo + opening))
    for row in range(rows):
        m.step()
        h = 24 * (row + 1)
        for cx, cz in corners(core):
            m.add('3005', post, cx, h, cz, purpose='Vermilion corner post')
        for side in ['front', 'right', 'back', 'left']:
            wall_side(m, core, side, row, h, lo, opening, win)
    # lattice windows over courses 1..2 with a dark screen one stud inside
    m.step()
    t = -core / 2 + 1.5 + lo + (opening - 1) / 2
    for cx, cz, yaw in [(t, -core / 2 + .5, 0), (-t, core / 2 - .5, 180),
                        (core / 2 - .5, t, -90), (-core / 2 + .5, -t, 90)]:
        m.add('3185', post, cx, 24 * rows, cz, yaw=yaw,
              purpose='Vermilion lattice window over two courses')
    back = min(opening, core - 4)
    for cx, cz, yaw, width in [(t, -core / 2 + 1.5, 0, opening), (-t, core / 2 - 1.5, 0, opening),
                               (core / 2 - 1.5, t, 90, back), (-core / 2 + 1.5, -t, 90, back)]:
        for row in range(rows):      # from the floor up, so the screen stands on studs
            m.add(BRICK[(width, 1)], C['shadow'], cx, 24 * (row + 1), cz, yaw=yaw,
                  purpose='Dark screen behind the lattice')
    # corbel course: inverted slopes step the eave support outward
    m.step()
    hc = 24 * (rows + 1)
    for cx, cz in corners(core):
        m.add('3005', post, cx, hc, cz, purpose='Corner post continues through the corbels')
    for side, cx, cz, yaw in side_cells(core):
        m.add('3665b', post, cx, hc, cz, yaw=yaw,
              purpose='Corbel: 1x1 underside on the wall head, top overhangs outward')
    # eave deck
    m.step()
    hd = hc + 8
    half = roof // 2
    lay(m, rect(-half, -half, roof, roof), hd, C['shadow'], prefer='x' if k % 2 else 'z',
        purpose='Eave deck; its edge reads as a dark fascia line')
    # eave ring: flat tiles with curved flares sweeping up into raised corners
    m.step()
    ring = ring_cells(roof)
    tips = [(-half, -half), (half - 1, -half), (half - 1, half - 1), (-half, half - 1)]
    flare = set()
    for i, j in tips:
        si, sj = (1 if i < 0 else -1), (1 if j < 0 else -1)
        flare |= {(i + si * n, j) for n in (1, 2, 3)} | {(i, j + sj * n) for n in (1, 2, 3)}
    for i, j in tips:
        si, sj = (1 if i < 0 else -1), (1 if j < 0 else -1)
        for n in range(4):
            m.add('3024', C['roof'], i + .5, hd + 8 * (n + 1), j + .5,
                  purpose='Raised eave corner')
        m.add('98138', C['gold'], i + .5, hd + 40, j + .5, purpose='Gilded eave tip')
        # 50950: origin at its high top, low end toward local -Z
        x0, z0 = i + .5 + si * 2, j + .5 + sj * 2
        m.add('3623', C['roof'], x0, hd + 8, j + .5, purpose='Seat for the eave flare')
        m.add('50950', C['roof'], x0, hd + 32, j + .5, yaw=-90 if si > 0 else 90,
              purpose='Curved flare sweeping up toward the corner')
        m.add('3623', C['roof'], i + .5, hd + 8, z0, yaw=90, purpose='Seat for the eave flare')
        m.add('50950', C['roof'], i + .5, hd + 32, z0, yaw=180 if sj > 0 else 0,
              purpose='Curved flare sweeping up toward the corner')
    lay(m, ring - set(tips) - flare, hd + 8, C['roof'], {(1, 1): '3070b'},
        purpose='Flat eave tiles; single studs keep the seams reading as tile rows')
    # slope ring of single-width slopes and hip corners
    m.step()
    for sx, sz, yaw in [(1, -1, 0), (-1, -1, 90), (-1, 1, 180), (1, 1, -90)]:
        put(m, '3045', C['roof'], sx * (half - 2), hd + 24, sz * (half - 2), yaw=yaw,
            purpose='Hip of the roof')
    for t in range(-half + 3, half - 3):
        x = t + .5
        put(m, '3040b', C['roof'], x, hd + 24, -half + 2, yaw=0)
        put(m, '3040b', C['roof'], -x, hd + 24, half - 2, yaw=180)
        put(m, '3040b', C['roof'], half - 2, hd + 24, x, yaw=-90)
        put(m, '3040b', C['roof'], -half + 2, hd + 24, -x, yaw=90)
    # hanging bells
    m.step()
    for i, j in tips:
        m.add('4589', C['gold'], i + .5, hd - 8, j + .5,
              purpose='Futaku bell: cone stud pressed into the deck underside')
    m.anchor('next', h=hd)
    return m


def crown(inner):
    m = Module('pagoda-crown', f'{inner}x{inner} stud hipped cap closing the top roof; '
                               'its four apex studs carry the spire')
    half = inner // 2
    lay(m, rect(-half, -half, inner, inner), 24, C['roof'], BRICK, purpose='Cap core')
    m.step()
    for sx, sz, yaw in [(1, -1, 0), (-1, -1, 90), (-1, 1, 180), (1, 1, -90)]:
        put(m, '3045', C['roof'], sx * (half - 1), 48, sz * (half - 1), yaw=yaw,
            purpose='Pyramidal hip')
    m.anchor('apex', h=48)
    return m


def spire(rings=9):
    """Sorin: base drum, jumper, nine inverted-dish rings on single studs, finial."""
    m = Module('pagoda-spire', f'Gilded sorin: base drum, {rings} rings and a rod finial')
    g = C['gold']
    m.add('3941', C['roof'], 0, 24, 0, purpose='Roban base drum on the four apex studs')
    m.add('87580', g, 0, 32, 0, purpose='Jumper: centres the mast on one stud')
    h = 32
    for i in range(rings):
        m.add('85861', g, 0, h + 8, 0, purpose='Mast segment (socketed round plate)')
        m.add('4740', g, 0, h + 16, 0, purpose='Ring: inverted dish on the centre stud')
        h += 16
    m.add('3062b', g, 0, h + 24, 0)
    m.add('4589', g, 0, h + 48, 0, purpose='Water-flame finial')
    m.add('3957a', g, 0, h + 56, 0, purpose='Spire rod')
    return m


PAGODA = dict(cores=[12, 12, 10, 8, 6], roofs=[18, 16, 14, 12, 10])


def pagoda():
    m = Module('pagoda', 'Five-storey pagoda: diminishing flared roofs, gilded spire; '
                         'wall bottom h=0, centred')
    prev = None
    for k, (core, roof) in enumerate(zip(PAGODA['cores'], PAGODA['roofs'])):
        s = storey(k, core, roof)
        if prev is None:
            m.add(s, 16, 0, 0, 0, id=f'storey-{k}')
        else:
            m.add(s, 16, id=f'storey-{k}', attach={'to': prev, 'anchor': 'next', 'using': 'base'})
        prev = f'storey-{k}'
    m.step()
    m.add(crown(PAGODA['roofs'][-1] - 6), 16, id='crown',
          attach={'to': prev, 'anchor': 'next', 'using': 'base'})
    m.add(spire(), 16, id='spire', attach={'to': 'crown', 'anchor': 'apex', 'using': 'base'})
    return m


# ---------------------------------------------------------------- temple ground

def plinth(size=22):
    """Stone platform: brick rings, full plate deck, tiled terrace, vermilion railing.

    Rings of the 22-stud square: 0-2 stone terrace, 3 railing, 4 veranda,
    5.. pagoda core (12x12) standing on the deck studs at h=32.
    """
    m = Module('temple-plinth', f'{size}x{size} stud stone platform with a vermilion '
                                'lattice railing and the pagoda; bottom h=0, entry at -Z')
    s = C['stone']
    for n in (size, 16, 12):
        lay(m, ring_cells(n), 24, s, BRICK, purpose='Supporting brick ring')
    m.step()
    lay(m, rect(-size // 2, -size // 2, size, size), 32, s, prefer='z',
        purpose='Platform deck')
    m.step()
    terrace = set().union(*(ring_cells(size, k) for k in (0, 1, 2)))
    veranda = ring_cells(size, 4)
    rail = ring_cells(size, 3)
    gate = {(i, -8) for i in range(-2, 2)}
    lay(m, terrace, 40, s, TILE, purpose='Stone terrace')
    lay(m, veranda | gate, 40, C['roof'], TILE, purpose='Dark veranda around the pagoda')
    m.step()
    # railing: each 16-stud side = post + [4][post][4][post][4] + post
    for cx, cz in corners(16, .5):
        m.add('3062b', C['post'], cx, 56, cz, purpose='Railing corner post')
        m.add('98138', C['gold'], cx, 64, cz, purpose='Gilded post cap')
    for side, yaw in [('front', 0), ('right', -90), ('back', 180), ('left', 90)]:
        for seg, t in enumerate([-5, 0, 5]):
            if side == 'front' and seg == 1:
                continue
            x, z = {'front': (t, -7.5), 'back': (-t, 7.5), 'right': (7.5, t),
                    'left': (-7.5, -t)}[side]
            m.add('3633', C['post'], x, 56, z, yaw=yaw, purpose='Lattice railing panel')
        for t in (-2.5, 2.5):
            x, z = {'front': (t, -7.5), 'back': (-t, 7.5), 'right': (7.5, t),
                    'left': (-7.5, -t)}[side]
            m.add('3062b', C['post'], x, 56, z, purpose='Railing post')
            m.add('98138', C['gold'], x, 64, z, purpose='Gilded post cap')
    m.step()
    m.add(pagoda(), 16, 0, 32, 0, id='pagoda')
    m.anchor('entry', 0, 40, -size / 2)
    return m


def steps(width=6, rises=5):
    """Stone stair, 8 LDU rise per tread, climbing toward +Z to the terrace at 40."""
    m = Module('temple-steps', f'{width}-stud stone stair of {rises} treads; bottom h=0, '
                               'lowest tread at -Z')
    s = C['stone']
    for r in range(rises):
        z = -rises / 2 + .5 + r
        top = 8 * (r + 1)
        h = 0
        body = top - 8
        while body - h >= 24:
            h += 24
            m.add('3009', s, 0, h, z, purpose='Stair core')
        while body - h >= 8:
            h += 8
            m.add('3666', s, 0, h, z, purpose='Stair core')
        m.add('6636', s, 0, top, z, purpose=f'Tread {r + 1}')
    return m


def lantern(name='stone-lantern', colour=None):
    """Kasuga-style toro: round base, post, dish platform, glowing box, dish roof."""
    s = colour or C['stone']
    m = Module(name, 'Stone lantern on a 2x2 stud footing; bottom h=0; 132 LDU tall')
    m.add('18674', s, 0, 8, 0, purpose='Round base; its centre stud carries the post')
    m.add('3062b', s, 0, 32, 0, purpose='Post')
    m.add('3062b', s, 0, 56, 0, purpose='Post')
    m.add('4740', s, 0, 64, 0, purpose='Platform: inverted dish on the centre stud')
    m.add('3062b', C['glow'], 0, 88, 0, purpose='Lit fire box')
    m.add('43898', s, 0, 96, 0, purpose='Umbrella roof: 3x3 dish on the fire box stud')
    m.add('85861', s, 0, 104, 0, purpose='Neck under the jewel')
    m.add('4589', s, 0, 128, 0, purpose='Hoju jewel')
    return m


def bridge():
    """Humped footbridge: two mirrored arch slopes per lane meeting over a pier.

    Four lanes along Z, centred on the origin, 16 studs long. Tip sockets rest
    on the bank studs at h=0. Measured 50967 profile: the feet beside each tip
    and the central legs reach 8 LDU below the tip sockets, so the feet touch
    the water surface (h=-8) and the legs stand on a footing whose top is -8.
    """
    m = Module('arched-bridge', 'Vermilion arched footbridge, 4x16 studs, with a planked crown, '
                                'handrails and gilded giboshi posts; bottom h=0, along Z')
    for x in (-1.5, -.5, .5, 1.5):
        c = C['post'] if abs(x) > 1 else C['bark']
        m.add('50967', c, x, 24, -1, purpose='South span: arch slope, high end at the crown')
        m.add('50967', c, x, 24, 1, yaw=180, purpose='North span: mirrored arch slope')
    m.step()
    # The flat crown between the two arch crests spans only z=+-35 LDU, so the
    # outer crown studs (z=+-30) stay bare; tiles and posts use the inner pair.
    m.add('3022', C['bark'], 0, 32, 0, purpose='Crown planks tie the two inner lanes')
    for x in (-1.5, 1.5):
        for z in (-.5, .5):
            m.add('3062b', C['post'], x, 48, z, purpose='Crown rail post')
            m.add('3062b', C['post'], x, 72, z)
        m.add('3710', C['post'], x, 80, 0, yaw=90, purpose='Handrail on the crown posts')
        m.add('2431', C['post'], x, 88, 0, yaw=90)
    m.step()
    for x in (-2.5, 2.5):
        for z in (-7.5, 7.5):
            m.add('3062b', C['post'], x, 24, z, purpose='Bridge-end post on the bank')
            m.add('3062b', C['post'], x, 48, z)
            m.add('4589', C['gold'], x, 72, z, purpose='Giboshi finial')
    return m


def torii(span=6):
    """Vermilion torii: round pillars, protruding nuki, shimaki and upswept kasagi."""
    m = Module('torii-gate', 'Vermilion torii gate over a 4-stud path; pillars 2x2 round at '
                             f'x=+-{span // 2}; bottom h=0; 192 LDU tall')
    p = C['post']
    xs = (-span / 2, span / 2)
    for x in xs:
        m.add('4032a', C['ink'], x, 8, 0, purpose='Kamebara footing')
        for n in range(4):
            m.add('3941', p, x, 32 + 24 * n, 0, purpose='Round pillar')
    m.step()
    m.add('3832', p, 0, 112, 0, purpose='Nuki tie beam, protruding past both pillars')
    for x in xs:
        m.add('3941', p, x, 136, 0)
        m.add('3941', p, x, 160, 0)
    m.add('3004', C['ink'], 0, 136, -.5, purpose='Gakuzuka centre strut')
    m.add('11211', C['ink'], 0, 160, -.5, purpose='Plaque brick; side studs face -Z')
    # Upright tile on the side studs: the studs are 10 LDU below the brick top,
    # and the rotated tile's back face meets the brick face 18 LDU forward.
    m.add('3069b', C['gold'], 0, 150, -1.4, matrix=SNOT, purpose='Gilded gakuzuka plaque')
    m.step()
    m.add('2445', p, 0, 168, 0, purpose='Shimaki beam')
    m.add('91988', C['ink'], 0, 176, 0, purpose='Kasagi beam')
    lay(m, rect(-5, -1, 10, 2), 184, C['ink'], TILE, purpose='Kasagi top')
    for sx in (-1, 1):
        for z in (-.5, .5):
            m.add('11477', C['ink'], sx * 6, 176, z, yaw=90 * sx,
                  purpose='Upswept kasagi end; curved slope rises outward')
    return m


# ---------------------------------------------------------------- planting

LEAF_STUDS = {
    '2417': [(40, 40), (-40, 40), (40, 0), (-40, 0), (20, -20), (-20, -20), (0, -60),
             (20, 40), (-20, 40), (40, 20), (-40, 20), (20, -40), (-20, -40)],
    '2423': [(-20, -20), (20, -40), (0, -60), (20, -20), (-20, -40)],
}
HUB_STUDS = {   # measured stud grids (studs) of the round hub plates
    '74611': [(x, z) for x in (-3.5, -2.5, -1.5, -.5, .5, 1.5, 2.5, 3.5)
              for z in (-3.5, -2.5, -1.5, -.5, .5, 1.5, 2.5, 3.5)
              if x * x + z * z <= 3.5 ** 2 + .5 ** 2 + .01],
    '11213': [(x, z) for x in (-2.5, -1.5, -.5, .5, 1.5, 2.5)
              for z in (-2.5, -1.5, -.5, .5, 1.5, 2.5) if x * x + z * z <= 2.5 ** 2 + .5 ** 2 + .01],
    '60474': [(x, z) for x in (-1.5, -.5, .5, 1.5) for z in (-1.5, -.5, .5, 1.5)
              if x * x + z * z <= 1.5 ** 2 + .5 ** 2 + .01],
}


def petal_colour(petals, n):
    return petals[n % len(petals)]


def sprig(m, ref, colour, x, h, z, yaw, petals, purpose):
    """A frond whose socket sits on a stud at support top h, petals on its studs."""
    m.add(ref, colour, x, h + 8, z, yaw=yaw, purpose=purpose)
    for n, (lx, lz) in enumerate(LEAF_STUDS[ref] if petals else []):
        dx, dz = rotate(yaw, lx, lz)
        m.add('24866', petal_colour(petals, n + int(abs(x * 7 + z * 3))),
              round(x + dx / 20, 6), h + 16, round(z + dz / 20, 6), yaw=yaw,
              purpose='Blossom cluster on a sprig stud')


def core_studs(x, z):
    return {(x + a, z + b) for a in (-.5, .5) for b in (-.5, .5)}


def cloud_tree(name, description, trunk, tiers, *, bark, top_colour, petals, crown_yaw=45):
    """Stepped cloud canopy on a round trunk.

    Each tier: a round disc on the 2x2 round bricks below, round-brick core
    bumps, a ring of short sprigs on 1x1 round risers at the disc rim, and
    petal clusters on the remaining studs. Discs shrink upward, so every sprig
    (back reach 10 LDU) stays outside the next disc and core. A 4x4 dish on a
    jumper closes the crown.
    """
    m = Module(name, description)
    m.add('60474', bark, 0, 8, 0, purpose='Root flare')
    h = 8
    for n in range(trunk):
        h += 24
        m.add('3941', bark, 0, h, 0, purpose='Trunk')
    for t in tiers:
        m.step()
        h += 8 * t.get('gap', 0)
        for n in range(t.get('stem', 0)):
            h += 24
            m.add('3941', bark, 0, h, 0, purpose='Exposed trunk between pads')
        h += 8
        m.add(t['disc'], t['colour'], 0, h, 0, purpose='Canopy disc')
        used = set()
        for x, z in t['core']:
            used |= core_studs(x, z)
            m.add('3941', t['core_colour'], x, h + 24, z, purpose='Canopy core bump')
        rise = t.get('rise', 24)
        for (x, z), (dx, dz) in t['sprigs']:
            used.add((x, z))
            m.add('3062b', t.get('riser', bark), x, h + 24, z, purpose='Sprig riser')
            top = h + 24
            if rise == 32:
                m.add('85861', t.get('riser', bark), x, h + 32, z)
                top = h + 32
            sprig(m, t.get('sprig_ref', '2423'), t['sprig_colour'], x, top, z,
                  outward_yaw(dx, dz), petals, 'Canopy sprig')
        near = [(x, z) for (x, z), _ in t.get('avoid', [])]
        for n, (x, z) in enumerate(HUB_STUDS[t['disc']]):
            if (x, z) in used or not petals:
                continue
            if any((x - a) ** 2 + (z - b) ** 2 < 1.1 for a, b in near):
                continue
            m.add('24866', petal_colour(petals, n), x, h + 8, z, purpose='Petals on the disc')
        h += 24
    m.step()
    m.add('87580', bark if not petals else tiers[-1]['core_colour'], 0, h + 8, 0,
          purpose='Jumper centring the crown')
    h += 8
    if not petals:
        m.add('3960', top_colour, 0, h + 16, 0, purpose='Crown pad: 4x4 dish on the jumper stud')
        return m
    if tiers[-1]['sprigs']:
        h += 24          # lift the crown frond clear of the last sprig petals
        m.add('3062b', tiers[-1]['core_colour'], 0, h, 0, purpose='Crown riser')
    sprig(m, '2417', top_colour, 0, h, 0, crown_yaw, petals, 'Crown frond')
    return m


AXIS = lambda r: [((r, .5), (1, 0)), ((-.5, r), (0, 1)), ((-r, -.5), (-1, 0)), ((.5, -r), (0, -1))]
DIAG = lambda r: [((r, r), (1, 1)), ((-r, r), (-1, 1)), ((-r, -r), (-1, -1)), ((r, -r), (1, -1))]
# rim studs on the axes, sprigs turned 45 degrees so they fan between the tier below
TWIST = lambda r: [((r, .5), (1, 1)), ((-.5, r), (-1, 1)), ((-r, -.5), (-1, -1)), ((.5, -r), (1, -1))]
PLUS = [(0, 0), (2, 0), (-2, 0), (0, 2), (0, -2)]


def cherry(name, size='large', tones=None, petals=None, omit=(), crown_yaw=45):
    """omit: local sprig directions left out so an edge tree leans into the garden."""
    tones = tones or [C['blossom'], C['blush'], C['blossom']]
    petals = petals or [C['rose'], C['petal'], C['blossom'], C['rose'], C['blush'], C['petal']]
    a, b, c = tones
    if size == 'large':
        tiers = [dict(disc='74611', colour=a, core=PLUS, core_colour=b, sprigs=AXIS(3.5),
                      sprig_colour=b, riser=c),
                 dict(disc='11213', colour=b, core=[(0, 0)], core_colour=a, sprigs=TWIST(2.5),
                      sprig_colour=c, riser=a),
                 dict(disc='60474', colour=c, core=[(0, 0)], core_colour=b, sprigs=[],
                      sprig_colour=c)]
        trunk = 4
    elif size == 'medium':
        tiers = [dict(disc='11213', colour=a, core=[(0, 0)], core_colour=b, sprigs=AXIS(2.5),
                      sprig_colour=b, riser=c),
                 dict(disc='60474', colour=b, core=[(0, 0)], core_colour=a, sprigs=[],
                      sprig_colour=c)]
        trunk = 3
    else:
        tiers = [dict(disc='60474', colour=a, core=[(0, 0)], core_colour=b, sprigs=AXIS(1.5),
                      sprig_colour=b, riser=c)]
        trunk = 2
    for t in tiers:
        t['sprigs'] = [sp for sp in t['sprigs'] if sp[1] not in omit]
    return cloud_tree(name, f'{size.capitalize()} flowering cherry: round trunk and a stepped '
                            'pink cloud canopy with sprigs and petal clusters; bottom h=0',
                      trunk, tiers, bark=C['bark'], top_colour=a, petals=petals,
                      crown_yaw=crown_yaw)


def pine():
    """Cloud-pruned pine (niwaki): three dark green pads separated by bare trunk."""
    g, d = C['moss'], C['deep_moss']
    # Stands one pad-radius in from the west edge: no sprig points west (-X).
    west = lambda sprigs: [sp for sp in sprigs if sp[1][0] >= 0]
    tiers = [dict(disc='74611', colour=d, core=PLUS, core_colour=d, sprigs=west(AXIS(3.5)),
                  sprig_colour=d, riser=d),
             dict(disc='11213', colour=d, core=[(0, 0)], core_colour=d, sprigs=west(TWIST(2.5)),
                  sprig_colour=g, riser=d, stem=1),
             dict(disc='60474', colour=d, core=[(0, 0)], core_colour=d, sprigs=[],
                  sprig_colour=g, stem=1)]
    return cloud_tree('garden-pine', 'Cloud-pruned pine: bare trunk and three needle pads '
                                     'tufted with dark green rosettes; bottom h=0', 3, tiers,
                      bark=C['bark'], top_colour=d, petals=[d, g, d, d, g])


# Plan footprint of the three 30176 leaves (8 LDU cells, local frame); the
# leaves lie 1..18 LDU below the node top, inside that node's own course.
BAMBOO_LEAF = [(12, -28), (12, -20), (12, -12), (12, 12), (12, 20), (12, 28), (20, -36),
               (20, -28), (20, -20), (20, -12), (20, -4), (20, 4), (20, 12), (20, 20), (20, 28),
               (20, 36), (28, -36), (28, -28), (28, -4), (28, 4), (28, 28), (28, 36), (36, -36),
               (36, -4), (36, 4), (36, 36), (44, -4), (44, 4), (52, -4), (52, 4)]


def grove(culms, keep_out=()):
    """Choose a leaf heading per node so no leaf touches another culm or leaf.

    culms: (x, z, height, phase) in studs. Candidate headings every 30 degrees,
    preferring a 137.5-degree spiral; a node with no clear heading stays bare.
    """
    placed = {}                                  # level -> list of LDU points
    plan = []
    for c, (x, z, height, phase) in enumerate(culms):
        leaves = []
        for n in range(2, height):
            if (n + phase) % 2 == 0:
                continue
            prefer = (c * 97 + n * 137.5) % 360
            options = sorted(range(0, 360, 30), key=lambda a: min(abs(a - prefer), 360 - abs(a - prefer)))
            for yaw in options:
                pts = []
                for lx, lz in BAMBOO_LEAF:
                    dx, dz = rotate(yaw, lx, lz)
                    pts.append((x * 20 + dx, z * 20 + dz))
                ok = all(-476 <= px <= 476 and -476 <= pz <= 476 for px, pz in pts)
                for k, (ox, oz, oh, _) in enumerate(culms):
                    if k != c and oh > n and ok:
                        ok = all((px - ox * 20) ** 2 + (pz - oz * 20) ** 2 > 14 ** 2 for px, pz in pts)
                for kx, kz, r in keep_out:
                    if ok:
                        ok = all((px - kx * 20) ** 2 + (pz - kz * 20) ** 2 > (r * 20) ** 2 for px, pz in pts)
                if ok:
                    ok = all((px - qx) ** 2 + (pz - qz) ** 2 > 10 ** 2
                             for px, pz in pts for qx, qz in placed.get(n, []))
                if ok:
                    placed.setdefault(n, []).extend(pts)
                    leaves.append((n, yaw))
                    break
        plan.append((x, z, height, tuple(leaves)))
    return plan


def bamboo_stalk(height, colour, leaves):
    key = '-'.join(f'{n}.{y}' for n, y in leaves)
    m = Module(f'bamboo-{height}-{colour}-{zlib.crc32(key.encode()) % 100000:05d}',
               f'Bamboo culm {height} bricks tall with {len(leaves)} leafy nodes; '
               'bottom h=0 on one stud')
    turn = dict(leaves)
    for n in range(height):
        ref = '30176' if n in turn else '3062b'
        m.add(ref, colour, 0, 24 * (n + 1), 0, yaw=turn.get(n, 0),
              purpose='Leafy node' if n in turn else 'Culm segment')
    m.add('4589', colour, 0, 24 * (height + 1), 0, purpose='Culm tip')
    return m


def rock(colour):
    """Boulder: the 42284 shell's rim reaches 32 LDU below its origin while its
    sockets sit 8 below, so a hidden 2x2 round brick (a square one clips the
    sloping inner ceiling) carries it with the rim resting on
    the flat tiles around the centre studs."""
    m = Module(f'boulder-{colour}', 'Garden boulder, 4x4 footprint: hidden 2x2 round brick and '
                                    'rock shell; bottom h=0, rim on flat tiles')
    m.add('3941', colour, 0, 24, 0, purpose='Hidden round support; clears the shell ceiling')
    m.add('42284', colour, 0, 32, 0, purpose='Rock shell on the brick studs; rim on the ground')
    return m


def basin():
    m = Module('tsukubai', 'Stone water basin with a still surface; bottom h=0 on 2x2 studs')
    m.add('3941', C['stone'], 0, 24, 0, purpose='Basin')
    m.add('14769', C['water'], 0, 32, 0, purpose='Water in the basin')
    return m


def bench():
    m = Module('garden-bench', 'Low timber viewing bench, 4x2 studs; bottom h=0; front -Z')
    for x in (-1.5, 1.5):
        m.add('3062b', C['ink'], x, 24, .5, purpose='Leg')
    m.add('3710', C['bark'], 0, 32, .5, purpose='Seat rail')
    m.add('3020', C['bark'], 0, 40, 0, purpose='Seat')
    lay(m, rect(-2, -1, 4, 2), 48, C['bark'], TILE, purpose='Seat boards')
    return m


# ---------------------------------------------------------------- figures

# Standing minifigure stack measured from this library's connector frames in
# examples/copper-bean/generate.py: legs 12 LDU below the hips origin, torso 32
# above, head 57 above; hips 40 above the stud surface. 43368/43369 arms carry
# their own geometry (a mirrored 3819 is rejected by the assembly profile).
HIPS_TO_LEGS, HIPS_TO_TORSO, HIPS_TO_HEAD, STANDING_HIPS = 12, 32, 57, 40
SHOULDER_X, SHOULDER_DROP = 15.552 / 20, 9


SNOT = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]     # tile top turned to face -Z


def rot(axis, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return {'x': [[1, 0, 0], [0, c, -s], [0, s, c]], 'y': [[c, 0, s], [0, 1, 0], [-s, 0, c]],
            'z': [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]


FOOT_Z = 1.2 / 20    # 3816c/3817c foot sockets sit 1.2 LDU behind the leg origin


def figure(name, description, *, torso_ref, torso, legs, head='3626bp01', hair_ref=None,
           hair=0):
    """A standing minifigure; bottom h=0, feet sockets on the stud row z=0, faces -Z."""
    m = Module(name, description)
    base, z = STANDING_HIPS, FOOT_Z
    m.add('3815b', legs, 0, base, z, purpose='Hips set the figure datum')
    for ref in ['3816c', '3817c']:
        m.add(ref, legs, 0, base - HIPS_TO_LEGS, z, purpose='Foot sockets on the studs')
    m.add(torso_ref, torso, 0, base + HIPS_TO_TORSO, z)
    m.add('43368', torso, -SHOULDER_X, base + HIPS_TO_TORSO - SHOULDER_DROP, z,
          matrix=rot('z', 9.79), purpose='Right arm hanging at the shoulder pin')
    m.add('43369', torso, SHOULDER_X, base + HIPS_TO_TORSO - SHOULDER_DROP, z,
          matrix=rot('z', -9.79))
    m.add(head, C['skin'], 0, base + HIPS_TO_HEAD, z)
    if hair_ref:
        m.add(hair_ref, hair, 0, base + HIPS_TO_HEAD, z, purpose='Shares the head origin')
    return m


# ---------------------------------------------------------------- terrain

W = 48               # baseplate studs; cells i, j in [-24, 23]


def zones():
    """Cell -> surface code. Front is -Z (low j)."""
    z = {}
    for i in range(-24, 24):
        for j in range(-24, 24):
            z[(i, j)] = '.'

    def fill(cells, code):
        for c in cells:
            if c in z:
                z[c] = code
    # gravel band around the platform, raked garden, bamboo earth
    fill(rect(-2, -3, 26, 27), 'r')
    fill(rect(15, -22, 8, 11), 'r')
    fill(rect(-24, 13, 9, 11), 'b')
    # moss under the large cherry
    fill({(i, j) for i in range(-15, -3) for j in range(2, 15)
          if (i + 9) ** 2 + (j - 8) ** 2 <= 30}, ':')
    # pond
    water = rect(-21, -17, 19, 11) | rect(-18, -19, 13, 2) | rect(-14, -20, 8, 1) \
        | rect(-19, -6, 5, 1)
    for c in [(-21, -17), (-21, -16), (-20, -17), (-21, -7), (-3, -17), (-3, -16), (-4, -17),
              (-3, -7), (-3, -8), (-18, -19), (-6, -19), (-19, -6)]:
        water.discard(c)
    fill(water, 'w')
    # main axis path, front promenade, bridge approach
    fill(rect(9, -24, 4, 19), 'p')
    fill(rect(-12, -24, 21, 2), 'p')
    fill(rect(-12, -22, 4, 1), 'p')
    # platform and stair footprints
    fill(rect(0, 0, 22, 22), 'P')
    fill(rect(8, -5, 6, 5), 'S')
    return z


FEATURES = {}        # name -> (x, z, footprint cells that must be studded)


def studded(z, cells, code='o'):
    for c in cells:
        z[c] = code


def terrain(z):
    """Three plate layers, water sunk one plate, tiled path/gravel/footings."""
    m = Module('garden-ground', '48x48 stud landscape: lawn, moss, pond, flagstones, '
                                'raked gravel and bamboo earth, three plates thick')
    cells = set(z)
    wet = {c for c, k in z.items() if k == 'w'}
    koi = {c for c, k in z.items() if k in 'kl'}
    # layer 1: whole board; pond bed is dark blue
    footing = {c for c, k in z.items() if k == 's'}
    lay(m, cells - wet - koi - footing, 8, C['earth'], prefer='x', purpose='Ground layer 1')
    lay(m, wet | koi, 8, C['pond'], prefer='x', purpose='Pond bed')
    lay(m, footing, 8, C['stone'], prefer='x', purpose='Pier footing, submerged course')
    m.step()
    dry = cells - wet - koi - footing
    lay(m, dry, 16, C['earth'], prefer='z', purpose='Ground layer 2')
    m.step()
    lay(m, wet, 16, C['water'], TILE, purpose='Water surface')
    lay(m, footing, 16, C['stone'], TILE, purpose='Pier footing at water level')
    groups = {'.': (C['moss'], PLATE), ':': (C['deep_moss'], PLATE), 'b': (C['earth'], PLATE),
              'o': (C['stone'], PLATE), 'P': (C['earth'], PLATE), 'S': (C['earth'], PLATE),
              'q': (C['path'], PLATE),
              'p': (C['path'], TILE), 'g': (C['moss'], TILE), 't': (C['path'], TILE),
              'x': (C['gravel'], TILE)}
    for code, (colour, table) in groups.items():
        sel = {c for c, k in z.items() if k == code}
        if sel:
            lay(m, sel, 24, colour, table, prefer='x',
                purpose={'.': 'Lawn', ':': 'Moss', 'b': 'Bamboo earth', 'o': 'Studded stone footing',
                         'P': 'Under platform', 'S': 'Under stair', 'q': 'Studded path landing',
                         'p': 'Flagstones', 'g': 'Lawn under a boulder rim',
                         't': 'Flagstones under a boulder rim',
                         'x': 'Gravel under a boulder rim'}[code])
    # raked gravel: one-stud rows of white and very light grey tiles
    raked = {c for c, k in z.items() if k == 'r'}
    for j in sorted({c[1] for c in raked}):
        row = {c for c in raked if c[1] == j}
        lay(m, row, 24, C['gravel'] if j % 2 else C['rake'], TILE, prefer='x',
            purpose='Raked gravel row')
    return m


# ---------------------------------------------------------------- scene

def scene():
    z = zones()
    m = Module('sakura-garden', 'Sakura Garden: five-storey pagoda, arched bridge over a koi '
                                'pond, torii gate and flowering cherries on a 48x48 base')
    placements = []

    def need(cx, cz, w, d, code='o'):
        """Reserve the studded footprint a feature stands on."""
        cells = rect(int(math.floor(cx - w / 2)), int(math.floor(cz - d / 2)), w, d)
        for c in cells:
            if z[c] in 'w':
                raise ValueError(f'feature footprint {c} lies in the pond')
            if z[c] in 'prsPS':
                z[c] = code
        return cells

    # bridge: lanes x -12..-9 (centre -10), cells j -21..-6 (centre z -13)
    bx, bz = -10, -13
    for j in range(-21, -5):
        for i in range(-12, -8):
            local = j - bz
            if local in (-8, 7):
                z[(i, j)] = 'q'
            elif -2 <= local <= 1:
                z[(i, j)] = 's'
            else:
                z[(i, j)] = 'w'
    for i in (-13, -8):
        for j in (-21, -6):
            z[(i, j)] = '.' if z[(i, j)] in '.w' else z[(i, j)]
    placements.append(('bridge', bridge(), bx, bz, 0))
    placements.append(('torii', torii(), 11, -19, 0))
    for k, (x, zz) in enumerate([(7, -10), (15, -10), (6, -2), (16, -2), (-1, -9), (-18, 11)]):
        need(x, zz, 2, 2)
        placements.append((f'lantern-{k}', lantern(), x, zz, 0))
    placements.append(('cherry-large', cherry('cherry-large', 'large'), -9, 8, 0))
    # edge trees drop the sprigs that would reach past the baseplate (local
    # directions: +Z faces world +X at yaw 90; +X and +Z face -X and -Z at 180)
    placements.append(('cherry-medium', cherry('cherry-medium', 'medium', omit=[(0, 1)]),
                       19, -6, 90))
    placements.append(('cherry-small', cherry('cherry-small', 'small',
                                              tones=[C['blush'], C['blossom'], C['blush']],
                                              omit=[(1, 0), (0, 1)], crown_yaw=-90),
                       -20, -21, 180))
    placements.append(('pine', pine(), -20, 5, 0))
    # stepping stones from the bridge landing to the stair
    stones = [(-9, -4), (-6, -3), (-3, -4), (0, -5), (3, -4), (6, -5)]
    for x, zz in stones:
        need(x, zz, 2, 2, 'o')
    # boulders at the pond edge and in the raked garden
    boulders = [(-1, -13, C['roof']), (-22, -10, C['stone']), (-16, -4, C['roof']),
                (-5, -19, C['stone']), (18, -18, C['roof']), (20, -14, C['stone'])]
    for x, zz, _ in boulders:
        centre = rect(x - 1, zz - 1, 2, 2)
        for c in rect(x - 2, zz - 2, 4, 4):
            if c in centre:
                z[c] = 'o'
            elif z[c] in '.:':
                z[c] = 'g'
            elif z[c] == 'r':
                z[c] = 'x'
            elif z[c] == 'p':
                z[c] = 't'
            elif z[c] != 'w':
                raise ValueError(f'boulder rim over {z[c]} at {c}')
    need(-17, 16, 2, 2, 'o')
    # platform, stair
    placements.append(('platform', plinth(), 11, 11, 0))
    placements.append(('stair', steps(), 11, -2.5, 0))
    # koi and lily pads replace water tiles
    koi_tiles = [(-17, -10.5, 0, '3069bp0p'), (-6.5, -9, 90, '3069bp0q'),
                 (-14, -15.5, 0, '3069bp0q'), (-5, -14.5, 0, '3069bp0p'),
                 (-19.5, -13, 90, '3069bp0p')]
    for x, zz, yaw, ref in koi_tiles:
        w, d = (2, 1) if yaw == 0 else (1, 2)
        for c in rect(int(math.floor(x - w / 2)), int(math.floor(zz - d / 2)), w, d):
            assert z[c] == 'w', (c, z[c])
            z[c] = 'k'
    pads = [(-17, -8), (-7, -17), (-15, -18)]
    for x, zz in pads:
        for c in rect(x - 1, zz - 1, 2, 2):
            assert z[c] == 'w', (c, z[c])
            z[c] = 'l'

    ground = terrain(z)
    m.add('4186', C['moss'], 0, 0, 0, id='baseplate', purpose='48x48 baseplate')
    m.add(ground, 16, 0, 0, 0, id='ground')
    m.step()
    for x, zz, yaw, ref in koi_tiles:
        m.add(ref, C['koi_water'], x, 16, zz, yaw=yaw, purpose='Printed koi at the surface')
    for x, zz in pads:
        m.add('4032a', C['moss'], x, 16, zz, purpose='Lily pad on the pond bed')
        m.add('24866', C['blush'], x + .5, 24, zz + .5, purpose='Water lily')
    m.step()
    for pid, mod, x, zz, yaw in placements:
        m.add(mod, 16, x, G, zz, yaw=yaw, id=pid)
    m.step()
    for n, (x, zz) in enumerate(stones):
        m.add('14769', C['stone'] if n % 2 else C['roof'], x, G + 8, zz,
              purpose='Stepping stone')
    for n, (x, zz, colour) in enumerate(boulders):
        m.add(rock(colour), 16, x, G, zz, id=f'boulder-{n}')
    m.add(basin(), 16, -17, G, 16, id='basin')
    m.add(bench(), 16, -14, G, -1, yaw=180, id='bench')
    m.step()
    # bamboo grove: culms on the dark earth, staggered phases and turns
    # 3-4 studs apart: a 52 LDU leaf plus 14 LDU culm clearance needs that room
    culms = [(-22.5, 22.5, 10, 0), (-18.5, 22.5, 8, 1), (-20.5, 19.5, 9, 1), (-23.5, 17.5, 7, 0),
             (-16.5, 19.5, 7, 0), (-20.5, 15.5, 8, 0), (-23.5, 13.5, 6, 1)]
    keep_out = [(-17, 16, 1.6), (-18, 11, 1.8), (-20, 5, 7.0)]   # basin, lantern, pine pads
    for n, (x, zz, hgt, leaves) in enumerate(grove(culms, keep_out=keep_out)):
        colour = C['bamboo'] if n % 3 else C['young_bamboo']
        m.add(bamboo_stalk(hgt, colour, leaves), 16, x, G, zz, id=f'bamboo-{n}')
    m.step()
    # people: a visitor in a pink robe on the bridge crown looking over the koi,
    # a gardener in a rice hat beside the raked garden, a monk on the stone path
    lady = figure('visitor-pink-robe', 'Visitor in a pink robe with a knotted bun; '
                  'bottom h=0, faces -Z', torso_ref='973phc', torso=C['blossom'],
                  legs=C['blossom'], head='3626bp02', hair_ref='13251', hair=C['ink'])
    gardener = figure('gardener', 'Gardener in indigo work clothes and a conical rice hat',
                      torso_ref='973', torso=C['pond'], legs=C['pond'], hair_ref='93059',
                      hair=C['path'])
    monk = figure('monk', 'Monk in a saffron robe', torso_ref='973pd99', torso=C['saffron'],
                  legs=C['saffron'])
    m.add(lady, 16, bx + .5, G + 32, bz, yaw=90, id='visitor',
          purpose='East half of the crown plate: her hands clear the west rail by 1 LDU')
    m.add(gardener, 16, 13.5, G, -16, yaw=-90, id='gardener')
    m.add(monk, 16, 4, G, -6.5, yaw=180, id='monk', purpose='Walks toward the pagoda')
    m.step()
    # ground-level footprints of every standing feature, for the checks below
    occupied = set()
    for x, zz, w, d in ([(-9, 8, 4, 4), (19, -6, 4, 4), (-20, -21, 4, 4), (-20, 5, 4, 4),
                         (-14, -1, 4, 2), (-17, 16, 2, 2), (8, -19, 2, 2), (14, -19, 2, 2),
                         (4, -6.5, 2, 1), (13.5, -16, 1, 2)]
                        + [(x, zz, 2, 2) for x, zz in stones]
                        + [(x, zz, 4, 4) for x, zz, _ in boulders]
                        + [(x, zz, 2, 2) for x, zz in [(7, -10), (15, -10), (-1, -9), (-18, 11)]]
                        + [(x, zz, 1, 1) for x in (-12.5, -7.5) for zz in (-20.5, -5.5)]):
        occupied |= rect(int(math.floor(x - w / 2)), int(math.floor(zz - d / 2)), w, d)
    # irises on the pond banks: leafy round plate with a lavender bloom
    irises = [(-22.5, -13.5, 90), (-22.5, -16.5, 200), (-16.5, -21.5, 300),
              (-1.5, -18.5, 150), (-11.5, -3.5, 45)]
    for x, zz, yaw in irises:
        cell = (int(math.floor(x)), int(math.floor(zz)))
        near = {(cell[0] + a, cell[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)}
        assert z[cell] in '.:' and not (near & occupied), (cell, z[cell])
        m.add('32607', C['moss'], x, G + 8, zz, yaw=yaw, purpose='Iris leaves on the bank')
        m.add('24866', C['iris'], x, G + 16, zz, yaw=yaw, purpose='Iris bloom')
        occupied |= near
    # fallen petals on the lawn and moss
    fallen = [(-12.5, 3.5, 29), (-6.5, 1.5, 13), (-4.5, 10.5, 15), (-13.5, 12.5, 29),
              (-8.5, 14.5, 13), (-2.5, 5.5, 29), (17.5, -8.5, 13), (21.5, -4.5, 29),
              (-17.5, -23.5, 29), (-22.5, -19.5, 13), (-14.5, 1.5, 15), (-3.5, 0.5, 13)]
    for x, zz, colour in fallen:
        cell = (int(math.floor(x)), int(math.floor(zz)))
        assert z[cell] in '.:' and cell not in occupied, (cell, z[cell])
        m.add('98138', colour, x, G + 8, zz, purpose='Fallen petal: flat round tile on the lawn')
    FEATURES['zones'] = z
    return m


def prototype(name):
    def build():
        mod = {'pagoda': pagoda, 'bridge': bridge, 'torii': torii, 'lantern': lantern,
               'cherry': lambda: cherry('cherry-large', 'large'), 'pine': pine,
               'platform': plinth}[name]()
        return mod
    return build


BUILDERS = {'sakura-garden': scene}
for _name in ['pagoda', 'bridge', 'torii', 'lantern', 'cherry', 'pine', 'platform']:
    BUILDERS[_name] = prototype(_name)


def ascii_map(z):
    rows = []
    for j in range(23, -25, -1):
        rows.append(''.join(z[(i, j)] for i in range(-24, 24)))
    return '\n'.join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--main', default='sakura-garden', choices=sorted(BUILDERS))
    ap.add_argument('--output', default=None)
    ap.add_argument('--map', action='store_true', help='print the terrain map')
    args = ap.parse_args()
    root = BUILDERS[args.main]()
    plan = root.plan()
    plan['author'] = AUTHOR
    out = Path(args.output) if args.output else ROOT / f'{args.main}.plan.json'
    out.write_text(json.dumps(plan, indent=1) + '\n')
    if args.map and 'zones' in FEATURES:
        (ROOT / 'terrain-map.txt').write_text(ascii_map(FEATURES['zones']) + '\n')
        print(ascii_map(FEATURES['zones']))
    count = sum(len(s) for sec in plan['sections'] for s in sec['steps'])
    print(json.dumps({'plan': str(out), 'sections': len(plan['sections']), 'placements': count}))


if __name__ == '__main__':
    main()
