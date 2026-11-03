#!/usr/bin/env python3
"""Generate the studs-forward retro boombox plan.

Run from the repository root:

    .venv/bin/python examples/boombox/generate.py
    ./ldraw-agent review examples/boombox/boombox.plan.json --outdir examples/boombox-review

World frame of boombox.ldr: ground at Y=0, -Y up, the front faces -Z.
The case is 26 x 6 studs. Its front wall is six courses of 22885 side-stud
bricks: each is 40 LDU high (5 plates = 2 studs), so the stacked side studs
form one continuous 20 LDU grid facing -Z. The fascia and rear panel are
upright plate/tile builds in their own local frames, rotated onto those
sideways studs as rigid submodels.

Panel-local frame (fascia and rear panel): base-plate top at local Y=0,
studs toward local -Y (out of the face), local +Z is up the face. Cell
(c, r) has its centre at x = -230 + 20c, z = 10 + 20r; 24 columns x 12 rows.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Palette roles
CASE = 0          # Black: case frame, lid, base plates, hidden fill
FASCIA = 179      # Pearl Silver: front fascia skin, keys, tuner/knob rings
CONE = 72         # Dark Bluish Grey: woofer cones, rear battery door
CAP = 383         # Chrome Silver: dust caps, antenna
KNOB = 71         # Light Bluish Grey: rotary knobs
ACCENT = 4        # Red: record key, tuner needle, cassette label
WHITE = 15
TUNER = 57        # Trans Orange: back-lit tuner scale
DISPLAY = 322     # Medium Azure: fluorescent tape-counter digits
LED_RED, LED_GREEN = 36, 34

IDENT = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
YAW90 = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
YAW_90 = [[0, 0, -1], [0, 1, 0], [1, 0, 0]]
YAW180 = [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]
# Tiles on side studs: local studs-up (-Y) faces world +X / -X, length runs
# along Z and local +Z points up in both cases.
FACE_RIGHT = [[0, -1, 0], [0, 0, -1], [1, 0, 0]]
FACE_LEFT = [[0, 1, 0], [0, 0, -1], [-1, 0, 0]]
# Rx(90): local studs (-Y) face world -Z, local +Z runs up the face.
FACE_FRONT = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
# Ry(180) * Rx(90): local studs face world +Z, local +Z still runs up.
FACE_BACK = [[-1, 0, 0], [0, 0, -1], [0, -1, 0]]

BRICK = {1: '3005.dat', 2: '3004.dat', 3: '3622.dat', 4: '3010.dat', 6: '3009.dat', 8: '3008.dat'}
PLATE = {1: '3024.dat', 2: '3023b.dat', 3: '3623.dat', 4: '3710.dat', 6: '3666.dat', 8: '3460.dat'}
TILE = {1: '3070b.dat', 2: '3069b.dat', 3: '63864.dat', 4: '2431.dat', 6: '6636.dat', 8: '4162.dat'}

# Plate/tile body heights; brick body 24. Origins are at the top body plane.
PH, BH = 8, 24


def split(n):
    """Split a run into available 1xN lengths: fewest pieces, then fewest 1s."""
    best = {0: []}
    for m in range(1, n + 1):
        options = [best[m - k] + [k] for k in (8, 6, 4, 3, 2, 1) if k <= m and (m - k) in best]
        best[m] = min(options, key=lambda s: (len(s), s.count(1)))
    return sorted(best[n], reverse=True)


def place(pid, ref, colour, at, matrix=None, purpose=None):
    item = {'id': pid, 'ref': ref, 'colour': colour, 'at': [float(v) for v in at]}
    if matrix is not None and matrix != IDENT:
        item['matrix'] = matrix
    if purpose:
        item['purpose'] = purpose
    return item


def cx(c, w=1):
    """Panel-local x centre of w columns starting at column c."""
    return -240 + 20 * c + 10 * w


def cz(r, h=1):
    """Panel-local z centre of h rows starting at row r."""
    return 20 * r + 10 * h


def run_parts(prefix, table, colour, y, row, c0, n, vertical=False):
    """1xN parts covering n cells in a row (or a column when vertical)."""
    out, pos = [], c0
    for k, length in enumerate(split(n)):
        if vertical:
            at, matrix = [cx(row), y, cz(pos, length)], YAW90
        else:
            at, matrix = [cx(pos, length), y, cz(row)], IDENT
        out.append(place(f'{prefix}-{k}', table[length], colour, at, matrix))
        pos += length
    return out


def tile_grid(prefix, free, colour, y, x0, z0, overrides=None):
    """Greedy cover of free (col,row) cells with flat tiles in a local grid.

    x0/z0 are the grid's minimum edges. Larger rectangles first; 1xN pieces
    turn with YAW90 when they run along rows.
    """
    shapes = [((4, 2), '87079.dat', IDENT), ((2, 4), '87079.dat', YAW90), ((2, 2), '3068b.dat', IDENT)]
    shapes += [((n, 1), TILE[n], IDENT) for n in (8, 6, 4, 3, 2)]
    shapes += [((1, n), TILE[n], YAW90) for n in (8, 6, 4, 3, 2)]
    shapes += [((1, 1), TILE[1], IDENT)]
    free = set(free)
    out = []
    for r in sorted({r for _, r in free}):
        for c in sorted({c for c, rr in free if rr == r}):
            if (c, r) not in free:
                continue
            for (w, h), ref, matrix in shapes:
                cells = {(c + i, r + j) for i in range(w) for j in range(h)}
                if cells <= free:
                    at = [x0 + 20 * c + 10 * w, y, z0 + 20 * r + 10 * h]
                    out.append(place(f'{prefix}-{len(out)}', ref, colour, at, matrix))
                    free -= cells
                    break
    return out


# ---------------------------------------------------------------- modules

def speaker_section():
    """8x8 woofer: raised black bezel, recessed dish cone, chrome dust cap.

    Origin: centre of the 8x8 cell area on the base-plate top plane.
    The dish rim is 8 LDU above the exposed base studs (stud tops at -4).
    """
    ring = []
    for name, z in (('lower', -70), ('upper', 70)):
        ring.append(('brick', place(f'bezel-{name}-brick', BRICK[8], CASE, [0, -BH, z])))
        ring.append(('plate', place(f'bezel-{name}-plate', PLATE[8], CASE, [0, -BH - PH, z])))
        ring.append(('tile', place(f'bezel-{name}-tile', TILE[8], CASE, [0, -BH - 2 * PH, z])))
    for name, x in (('left', -70), ('right', 70)):
        ring.append(('brick', place(f'bezel-{name}-brick', BRICK[6], CASE, [x, -BH, 0], YAW90)))
        ring.append(('plate', place(f'bezel-{name}-plate', PLATE[6], CASE, [x, -BH - PH, 0], YAW90)))
        ring.append(('tile', place(f'bezel-{name}-tile', TILE[6], CASE, [x, -BH - 2 * PH, 0], YAW90)))
    steps = [
        [p for kind, p in ring if kind == 'brick'],
        [p for kind, p in ring if kind != 'brick'],
        [place('cone-spacer-lower', '4032a.dat', CASE, [0, -8, 0], purpose='Raises the cone rim clear of the base studs'),
         place('cone-spacer-upper', '4032a.dat', CASE, [0, -16, 0])],
        [place('cone', '44375b.dat', CONE, [0, -24, 0], purpose='Woofer cone: rim at -8, recessed 24 behind the fascia'),
         place('dust-cap', '14769.dat', CAP, [0, -32, 0])],
    ]
    return {'name': 'boombox-speaker.ldr',
            'description': 'Woofer module: bezel ring, floating 6x6 dish cone and dust cap',
            'steps': steps}


def tweeter_section():
    """2x2 tweeter standing 8 LDU proud of the fascia. Origin: base-plate top, 2x2 centre."""
    return {'name': 'boombox-tweeter.ldr',
            'description': 'Tweeter: round brick, silver trim ring and grille tile',
            'steps': [[place('body', '3941.dat', CASE, [0, -BH, 0]),
                       place('trim', '4032a.dat', FASCIA, [0, -BH - PH, 0]),
                       place('grille', '4150p01.dat', KNOB, [0, -BH - 2 * PH, 0])]]}


def knob_section():
    """Rotary knob standing 16 LDU proud of the fascia. Origin: base-plate top, 2x2 centre."""
    return {'name': 'boombox-knob.ldr',
            'description': 'Rotary control: round brick, silver collar, black skirt and knob tile',
            'steps': [[place('body', '3941.dat', CASE, [0, -BH, 0]),
                       place('collar', '4032a.dat', FASCIA, [0, -BH - PH, 0]),
                       place('skirt', '4032a.dat', CASE, [0, -BH - 2 * PH, 0]),
                       place('cap', '14769p0v.dat', KNOB, [0, -BH - 3 * PH, 0])]]}


def fascia_section():
    claimed = set()

    def claim(c0, r0, w, h):
        cells = {(c, r) for c in range(c0, c0 + w) for r in range(r0, r0 + h)}
        assert not cells & claimed, (c0, r0, w, h)
        claimed.update(cells)

    steps = []
    # 1. Base plates: four 12x6 plates, each engaging 72 forward studs.
    steps.append([place(f'base-{i}{j}', '3028.dat', CASE, [-120 + 240 * i, 0, 60 + 120 * j])
                  for j in (0, 1) for i in (0, 1)])

    # 2. Woofers (cols 0-7 and 16-23, rows 1-8) and the deck frame strips.
    woofers = []
    for name, c0 in (('left', 0), ('right', 16)):
        claim(c0, 1, 8, 8)
        woofers.append(place(f'woofer-{name}', 'boombox-speaker.ldr', CASE, [cx(c0, 8), 0, cz(1, 8)]))
    steps.append(woofers)

    deck = []
    for name, c in (('left', 8), ('right', 15)):
        claim(c, 1, 1, 6)
        deck.append(place(f'deck-{name}-brick', BRICK[6], CASE, [cx(c), -BH, cz(1, 6)], YAW90))
        deck.append(place(f'deck-{name}-tile', TILE[6], FASCIA, [cx(c), -BH - PH, cz(1, 6)], YAW90))
    claim(9, 1, 6, 1)
    deck.append(place('deck-sill-brick', BRICK[6], CASE, [cx(9, 6), -BH, cz(1)]))
    deck += [place('deck-sill-tile-0', TILE[2], FASCIA, [cx(9, 2), -BH - PH, cz(1)]),
             place('deck-mic-grille', '2412b.dat', CASE, [cx(11, 2), -BH - PH, cz(1)], purpose='Built-in microphone'),
             place('deck-sill-tile-1', TILE[2], FASCIA, [cx(13, 2), -BH - PH, cz(1)])]
    claim(9, 6, 6, 1)
    deck.append(place('deck-display-brick', BRICK[6], CASE, [cx(9, 6), -BH, cz(6)]))
    # The print is black on the base colour, so the base colour lights the digits.
    deck += [place('tape-counter', '3069bp08.dat', DISPLAY, [cx(9, 2), -BH - PH, cz(6)], purpose='Tape counter'),
             place('led-record', '98138.dat', LED_RED, [cx(11), -BH - PH, cz(6)]),
             place('led-power', '98138.dat', LED_GREEN, [cx(12), -BH - PH, cz(6)]),
             place('eject-grille', '2412b.dat', FASCIA, [cx(13, 2), -BH - PH, cz(6)], purpose='Eject bar')]
    steps.append(deck)

    # 3. Cassette bay (cols 9-14, rows 2-5): recessed to the base studs,
    #    holding a 4x3 cassette 16 LDU behind the fascia surface.
    claim(9, 2, 6, 4)
    cassette = [place('cassette-plate-lower', '3020.dat', CASE, [cx(10, 4), -PH, cz(2, 2)]),
                place('cassette-plate-upper', PLATE[4], CASE, [cx(10, 4), -PH, cz(4)])]
    cassette += [place('cassette-base', TILE[4], WHITE, [cx(10, 4), -2 * PH, cz(2)]),
                 place('cassette-hub-left', TILE[1], WHITE, [cx(10), -2 * PH, cz(3)]),
                 place('cassette-reels', '3069bp02.dat', WHITE, [cx(11, 2), -2 * PH, cz(3)], purpose='Tape reels'),
                 place('cassette-hub-right', TILE[1], WHITE, [cx(13), -2 * PH, cz(3)]),
                 place('cassette-label', TILE[4], ACCENT, [cx(10, 4), -2 * PH, cz(4)])]
    steps.append(cassette)

    # 4. Controls above the deck (rows 7-8): two knobs flanking stereo VU meters.
    controls = []
    for name, c in (('volume', 8), ('tone', 14)):
        claim(c, 7, 2, 2)
        controls.append(place(f'knob-{name}', 'boombox-knob.ldr', CASE, [cx(c, 2), 0, cz(7, 2)]))
    claim(10, 7, 4, 2)
    for r in (7, 8):
        controls.append(place(f'meter-brick-{r}', BRICK[4], CASE, [cx(10, 4), -BH, cz(r)]))
    controls += [place('vu-left', '3068bp70.dat', FASCIA, [cx(10, 2), -BH - PH, cz(7, 2)]),
                 place('vu-right', '3068bp70.dat', FASCIA, [cx(12, 2), -BH - PH, cz(7, 2)])]
    steps.append(controls)

    # 5. Top strip (rows 9-10): tweeters above the woofer centres, tuner dial,
    #    and two-band slider pairs between them. A slider cell stands 8 proud;
    #    its partner cell stays open to the base studs, reading as the slot.
    strip = []
    for name, c in (('left', 3), ('right', 19)):
        claim(c, 9, 2, 2)
        strip.append(place(f'tweeter-{name}', 'boombox-tweeter.ldr', CASE, [cx(c, 2), 0, cz(9, 2)]))
    for name, c, r in (('bass-left', 5, 10), ('treble-left', 7, 9), ('bass-right', 16, 9), ('treble-right', 18, 10)):
        claim(c, 9, 1, 2)
        strip += [place(f'slider-{name}-post', BRICK[1], CASE, [cx(c), -BH, cz(r)]),
                  place(f'slider-{name}-plate', PLATE[1], CASE, [cx(c), -BH - PH, cz(r)]),
                  place(f'slider-{name}-knob', '98138.dat', WHITE, [cx(c), -BH - 2 * PH, cz(r)])]
    claim(8, 9, 8, 2)
    strip.append(place('tuner-backing', '3034.dat', WHITE, [cx(8, 8), -PH, cz(9, 2)], purpose='White backing lights the scale'))
    for r in (9, 10):
        strip.append(place(f'tuner-scale-{r}-low', TILE[4], TUNER, [cx(8, 4), -2 * PH, cz(r)]))
        strip.append(place(f'tuner-scale-{r}-high', TILE[3], TUNER, [cx(13, 3), -2 * PH, cz(r)]))
    strip.append(place('tuner-needle', TILE[2], ACCENT, [cx(12), -2 * PH, cz(9, 2)], YAW90))
    claim(10, 11, 4, 1)
    strip += [place('nameplate-brick', BRICK[4], CASE, [cx(10, 4), -BH, cz(11)]),
              place('nameplate', TILE[4], CAP, [cx(10, 4), -BH - PH, cz(11)], purpose='Blank chrome nameplate')]
    steps.append(strip)

    # 6. Fascia skin: every remaining cell gets a black 1xN brick and a silver tile.
    skin_bricks, skin_tiles = [], []
    for r in range(12):
        c = 0
        while c < 24:
            if (c, r) in claimed:
                c += 1
                continue
            c0 = c
            while c < 24 and (c, r) not in claimed:
                c += 1
            claim(c0, r, c - c0, 1)
            skin_bricks += run_parts(f'skin-r{r}c{c0}-brick', BRICK, CASE, -BH, r, c0, c - c0)
            skin_tiles += run_parts(f'skin-r{r}c{c0}-tile', TILE, FASCIA, -BH - PH, r, c0, c - c0)
    assert len(claimed) == 24 * 12
    steps.append(skin_bricks)
    steps.append(skin_tiles)

    return {'name': 'boombox-fascia.ldr',
            'description': 'Front fascia built studs-up; rotated to face -Z on the 22885 wall',
            'steps': steps}


def rear_section():
    """Rear panel: battery door, vents and rating label on plates and tiles only."""
    steps = [[place(f'base-{i}{j}', '3028.dat', CASE, [-120 + 240 * i, 0, 60 + 120 * j])
              for j in (0, 1) for i in (0, 1)]]
    taken = set()
    details = []
    # Vents: 1x2 grille tiles, rows 8-10, three per row on each side.
    for side, c0 in (('a', 1), ('b', 17)):
        for r in (8, 9, 10):
            for k in range(3):
                c = c0 + 2 * k
                taken |= {(c, r), (c + 1, r)}
                details.append(place(f'vent-{side}{r}-{k}', '2412b.dat', CONE, [cx(c, 2), -PH, cz(r)]))
    # Rating label.
    taken |= {(c, r) for c in range(10, 14) for r in (8, 9)}
    details.append(place('rating-label', '87079.dat', WHITE, [cx(10, 4), -PH, cz(8, 2)]))
    # Battery door with a finger grip.
    door_cells = {(c, r) for c in range(4, 20) for r in range(1, 7)}
    grip = {(c, 6) for c in range(10, 14)}
    for k, c in enumerate((10, 12)):
        details.append(place(f'door-grip-{k}', '2412b.dat', CASE, [cx(c, 2), -PH, cz(6)]))
    taken |= door_cells
    door = tile_grid('door', door_cells - grip, CONE, -PH, -240, 0)
    steps.append(door + details)
    rest = {(c, r) for c in range(24) for r in range(12)} - taken
    steps.append(tile_grid('skin', rest, CASE, -PH, -240, 0))
    return {'name': 'boombox-rear.ldr',
            'description': 'Rear panel built studs-up; rotated to face +Z on the 30414 courses',
            'steps': steps}


def main_section():
    steps = []
    # 1. Feet and base plates (top of base at Y=-16).
    steps.append([place(f'foot-{n}', '4032a.dat', CASE, [x, -8, z])
                  for n, (x, z) in enumerate(((-220, -40), (220, -40), (-220, 40), (220, 40)))]
                 + [place('base-long', '3027.dat', CASE, [-100, -16, 0]),
                    place('base-short', '3033.dat', CASE, [160, -16, 0])])

    # 2. Bottom layer: wall plates, smooth sill in front of the SNOT wall.
    layer = [place(f'front-wall-plate-{i}', PLATE[8], CASE, [x, -24, -10]) for i, x in enumerate((-160, 0, 160))]
    layer += [place(f'sill-tile-{i}', '87079.dat', CASE, [x, -24, -40], purpose='Fascia rests on a smooth sill')
              for i, x in enumerate((-200, -120, -40, 40, 120, 200))]
    layer += [place(f'rear-sill-tile-{i}', TILE[8], CASE, [x, -24, 50], purpose='Rear panel rests on a smooth sill')
              for i, x in enumerate((-160, 0, 160))]
    layer += [place(f'side-plate-{s}', PLATE[6], CASE, [x, -24, 0], YAW90) for s, x in (('left', -250), ('right', 250))]
    steps.append(layer)

    # 3. Front SNOT wall: six running-bond courses of 22885 (studs face -Z at Z=-20).
    for k in range(6):
        y = -64 - 40 * k
        course = []
        if k % 2 == 0:
            course += [place(f'snot-c{k}-{i}', '22885.dat', CASE, [-220 + 40 * i, y, -10]) for i in range(12)]
        else:
            course += [place(f'snot-c{k}-{i}', '22885.dat', CASE, [-200 + 40 * i, y, -10]) for i in range(11)]
            course += [place(f'snot-c{k}-end-{s}', '32952.dat', CASE, [x, y, -10]) for s, x in (('left', -230), ('right', 230))]
        steps.append(course)

    # 4. Side walls: ten 1x6 bricks each, framing both panels' edges. Course 8
    #    carries an outward 11211 whose two side studs hold a strap-lug tile.
    sides = []
    for j in range(10):
        y = -48 - 24 * j
        for s, x, out in (('left', -250, YAW90), ('right', 250, YAW_90)):
            if j != 8:
                sides.append(place(f'side-{s}-{j}', BRICK[6], CASE, [x, y, 0], YAW90))
                continue
            sides += [place(f'side-{s}-{j}-front', BRICK[2], CASE, [x, y, -40], YAW90),
                      place(f'side-{s}-{j}-lug-mount', '11211.dat', CASE, [x, y, 0], out),
                      place(f'side-{s}-{j}-back', BRICK[2], CASE, [x, y, 40], YAW90)]
    sides += [place('strap-lug-left', '2432.dat', FASCIA, [-292, -230, 0], FACE_LEFT,
                    purpose='Tile underside on the 11211 stud plane X=-260'),
              place('strap-lug-right', '2432.dat', FASCIA, [292, -230, 0], FACE_RIGHT,
                    purpose='Tile underside on the 11211 stud plane X=260')]
    steps.append(sides)

    # 5. Back wall (Z 20..40): courses 1 and 6 are 30414 side-stud bricks facing +Z;
    #    their studs fall on panel rows 1 and 7 (24*5 = 20*6). Plate on top.
    layouts = {0: [6, 8, 8, 2], 2: [2, 8, 8, 6], 3: [8, 8, 8], 4: [6, 8, 8, 2],
               5: [2, 8, 8, 6], 7: [6, 8, 8, 2], 8: [8, 8, 8], 9: [2, 8, 8, 6]}
    back = []
    for j in range(10):
        y = -40 - 24 * j
        if j in (1, 6):
            back += [place(f'back-c{j}-snot-{i}', '30414.dat', CASE, [-200 + 80 * i, y, 30], YAW180) for i in range(6)]
            continue
        x = -240
        for i, n in enumerate(layouts[j]):
            back.append(place(f'back-c{j}-{i}', BRICK[n], CASE, [x + 10 * n, y, 30]))
            x += 20 * n
    back += [place(f'back-top-plate-{i}', PLATE[8], CASE, [x, -264, 30]) for i, x in enumerate((-160, 0, 160))]
    steps.append(back)

    # 6. Fascia on the forward studs; rear panel on the backward studs.
    steps.append([place('fascia', 'boombox-fascia.ldr', CASE, [0, -24, -28], FACE_FRONT,
                        purpose='Base-plate underside meets the 22885 stud plane at Z=-20')])
    steps.append([place('rear-panel', 'boombox-rear.ldr', CASE, [0, -24, 48], FACE_BACK,
                        purpose='Base-plate underside meets the 30414 stud plane at Z=40')])

    # 7. Lid plates (seam offset from the base seam), covering the fascia's top edge.
    steps.append([place('lid-short', '3033.dat', CASE, [-160, -272, 0]),
                  place('lid-long', '3027.dat', CASE, [100, -272, 0])])

    # 8. Top controls: piano keys, handle, antenna, smooth lid tiles.
    top_y = -272
    keys = []
    for i, (name, colour) in enumerate((('record', ACCENT), ('play', FASCIA), ('rewind', FASCIA),
                                        ('forward', FASCIA), ('stop', FASCIA), ('pause', FASCIA))):
        keys.append(place(f'key-{name}', '54200.dat', colour, [-50 + 20 * i, top_y, -50]))
    # Handle: two round posts (48), a 1x12 bridge, a 16-high silver grip whose
    # curved 2x1 ends fall away outward over the posts.
    bridge_y = top_y - 2 * BH - PH
    handle = []
    for s, x in (('left', -110), ('right', 110)):
        handle += [place(f'handle-post-{s}-lower', '3062b.dat', CASE, [x, top_y - BH, 10]),
                   place(f'handle-post-{s}-upper', '3062b.dat', CASE, [x, top_y - 2 * BH, 10])]
    handle += [place('handle-bridge', '60479.dat', CASE, [0, bridge_y, 10], purpose='Spans posts at X=+-110'),
               place('handle-grip-plate', PLATE[8], FASCIA, [0, bridge_y - PH, 10]),
               place('handle-grip-tile', TILE[8], FASCIA, [0, bridge_y - 2 * PH, 10]),
               place('handle-end-left', '11477.dat', FASCIA, [-100, bridge_y, 10], YAW90),
               place('handle-end-right', '11477.dat', FASCIA, [100, bridge_y, 10], YAW_90)]
    antenna = [place('antenna', '2569.dat', CAP, [230, top_y - 8, 50], purpose='Telescopic aerial')]
    used = {(c, 0) for c in range(10, 16)} | {(7, 3), (18, 3), (24, 5)}
    lid = tile_grid('lid-tile', {(c, r) for c in range(26) for r in range(6)} - used, CASE, top_y - 8, -260, -60)
    steps.append(keys + lid)
    steps.append(handle + antenna)

    return {'name': 'boombox.ldr',
            'description': 'Studs-forward retro boombox: SNOT fascia and rear panel on a black case',
            'steps': steps}


def build_plan():
    return {
        'version': 1,
        'author': 'ldraw-nova agent (Claude Opus 5.5) for anteloc',
        'sections': [main_section(), fascia_section(), rear_section(),
                     speaker_section(), tweeter_section(), knob_section()],
    }


if __name__ == '__main__':
    plan = build_plan()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--plan', type=Path, default=HERE / 'boombox.plan.json')
    out = parser.parse_args().plan
    out.write_text(json.dumps(plan, indent=1) + '\n')
    count = sum(len(step) for s in plan['sections'] for step in s['steps'])
    print(f'Wrote {out} ({count} placements before submodel expansion)')
