#!/usr/bin/env python3
"""Meridian Park -- an original football (soccer) stadium as an editable plan.

Generates ``stadium.plan.json`` (schema: ldraw_tools/data/plan.schema.json)
for ``ldraw-agent build``. Technique inspiration: the vertical grille-brick
terracing observed in the annotated Old Trafford study; all geometry here is
original, with every part origin/bound verified against the supplied library
via ``ldraw-agent part``.

Model layout (world coordinates, y=0 is the table, -y is up):
  - pitch.ldr      elevated 20x26-stud plinth, green 16x24 surface, markings
  - stand-*.ldr    parametric terrace stands (26/20 studs long, 8/6/5 rows)
  - goal.ldr       open-frame goal with back stanchions (placed twice)
  - floodlight.ldr corner pylon (placed four times)
  - stadium.ldr    scene composition (root, first section)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

AUTHOR = "ldraw-nova stadium example generator"
HERE = Path(__file__).resolve().parent

# LDraw colour codes (validated via `ldraw-agent colours`).
RED, WHITE, GREY, GREEN, GLASS, LAMP, BLACK = 4, 15, 72, 2, 43, 47, 0


# --------------------------------------------------------------------------- #
# plan helpers
# --------------------------------------------------------------------------- #
def place(pid, ref, colour, at, yaw=None, repeat=None, purpose=None):
    if "." not in ref:  # bare part code -> physical part reference
        ref += ".dat"
    p = {"id": pid, "ref": ref, "colour": colour, "at": list(at)}
    if yaw is not None:
        p["yaw"] = yaw
    if repeat is not None:
        p["repeat"] = {"count": repeat[0], "step": list(repeat[1])}
    if purpose:
        p["purpose"] = purpose
    return p


def section(name, description, steps):
    return {"name": name, "description": description, "steps": steps}


def grid8(L):
    """8-wide cells + trailing 2-wide fill(s) for length L studs.

    26 studs cannot tile symmetrically with 8-wide cells (24+2), so a single
    trailing 2-wide fill is used; 20 studs tile as 16+2+2 centred.
    """
    if L % 8 == 4:
        full = [-80 + 160 * i for i in range(L // 8)]
        fills = [-(10 * L - 20), 10 * L - 20]
    else:
        full = [(-10 * L) + 80 + 160 * i for i in range(L // 8)]
        fills = [10 * L - 20]
    return full, fills


def grid4(L):
    """4-wide cells; centred 2-wide end fills when L % 4 == 2."""
    if L % 4 == 2:
        full = [(-10 * L) + 100 + 80 * i for i in range(L // 4 - 1)]
        fills = [-(10 * L - 20), 10 * L - 20]
    else:
        full = [(-10 * L) + 40 + 80 * i for i in range(L // 4)]
        fills = []
    return full, fills


# --------------------------------------------------------------------------- #
# pitch.ldr -- plinth, surface, markings, flags, ball
# --------------------------------------------------------------------------- #
def pitch_section():
    steps = []

    # 1. plinth bricks (dark grey): rotated 2x8 columns in 8-deep bands, y=-24
    for zc in (-180, -20, 140):
        steps.append([
            place(f"plinth-{zc}", "3007", GREY, (-180, -24, zc), yaw=90,
                  repeat=(10, (40, 0, 0)),
                  purpose="plinth base, rotated 2x8 column band")])
    steps.append([
        place("plinth-cap-n", "3003", GREY, (-180, -24, 240), repeat=(10, (40, 0, 0)),
              purpose="plinth north edge, 2x2 bricks"),
    ])

    # 2. plate deck, staggered: rotated 4x8 plates over 3 offset bands + fill
    deck = []
    for zc in (-180, -20, 140):
        deck.append(place(f"deck-{zc}", "3035", GREY, (-160, -32, zc), yaw=90,
                          repeat=(5, (80, 0, 0)),
                          purpose="staggered bonding deck"))
    deck.append(place("deck-fill-n", "3022", GREY, (-180, -32, 240), repeat=(10, (40, 0, 0))))
    steps.append(deck)

    # 3. apron ring (grey): 2-stud side strips + 1-stud end strips, y=-40
    apron = []
    for xc in (-180, 180):
        apron.append(place(f"apron-side-{'w' if xc < 0 else 'e'}", "3068b", GREY,
                           (xc, -40, -220), repeat=(12, (0, 0, 40)),
                           purpose="side apron 2x2 tiles"))
    for zc in (250, -250):
        apron.append(place(f"apron-end-{'n' if zc > 0 else 's'}", "3069b", GREY,
                           (-140, -40, zc), repeat=(8, (40, 0, 0)),
                           purpose="end apron 1x2 tiles"))
    for sx in (1, -1):  # 2x1 corner apron tiles beside each flag
        for sz in (1, -1):
            apron.append(place(f"apron-corner-{sz}{sx}", "3069b", GREY,
                               (180 * sx, -40, 250 * sz)))
    steps.append(apron)

    # 4. turf (green): full 4x2 tile rows beyond the halfway stripe
    turf = []
    for zc in (-100, -60, 60, 100):
        turf.append(place(f"turf-{zc}", "87079", GREEN, (-120, -40, zc),
                          repeat=(4, (80, 0, 0)), purpose="mown turf row"))
    steps.append(turf)

    # 5. halfway stripe (white, 4 studs wide)
    steps.append([
        place("stripe-n", "87079", WHITE, (-120, -40, 20), repeat=(4, (80, 0, 0))),
        place("stripe-s", "87079", WHITE, (-120, -40, -20), repeat=(4, (80, 0, 0))),
    ])

    # 6. marking zone: 2x2 tile grid rows (z=+/-140,180,220 per end)
    #    penalty boxes: white outlines, 8 wide x 4 deep (z in [120,200])
    marks = []
    for end in (1, -1):
        tag = "n" if end > 0 else "s"
        for zc in (140 * end, 180 * end):
            for xc in (-140, -100, 100, 140):
                marks.append(place(f"zone-{tag}-{xc}-{zc}", "3068b", GREEN,
                                   (xc, -40, zc)))
        for xc in (-60, 60):  # penalty-box side lines
            for zc in (140 * end, 180 * end):
                marks.append(place(f"pen-side-{tag}-{xc}-{zc}", "3068b", WHITE,
                                   (xc, -40, zc), purpose="penalty box side"))
        for xc in (-20, 20):  # penalty-box front line
            marks.append(place(f"pen-front-{tag}-{xc}", "3068b", WHITE,
                               (xc, -40, 140 * end), purpose="penalty box front"))
        # goal-line row between the posts becomes white plates so goals clamp
        for xc in (-60, 60):
            for zc in (210 * end, 230 * end):
                marks.append(place(f"goal-clamp-{end}-{xc}-{zc}", "3023b", WHITE,
                                   (xc, -40, zc), purpose="goal post footing"))
        for xc in (-20, 20):  # remaining goal-line cells stay green
            marks.append(place(f"goal-line-{tag}-{xc}", "3068b", GREEN,
                               (xc, -40, 220 * end)))
    steps.append(marks)

    # 7. corner flags: green plates + round-brick posts + red round caps
    flags = []
    for sx in (1, -1):
        for sz in (1, -1):
            tag = f"{'n' if sz > 0 else 's'}{'e' if sx > 0 else 'w'}"
            x, z = 140 * sx, 220 * sz
            flags.append(place(f"flag-base-{tag}-a", "3023b", GREEN, (x, -40, z - 10)))
            flags.append(place(f"flag-base-{tag}-b", "3023b", GREEN, (x, -40, z + 10)))
            flags.append(place(f"flag-pole-{tag}", "3062b", WHITE, (x, -64, z + 10),
                               repeat=(2, (0, -24, 0)), purpose="corner flag pole"))
            flags.append(place(f"flag-cap-{tag}", "6141", RED, (x, -96, z + 10)))
    steps.append(flags)

    # 8. the ball, just outside the north penalty box
    steps.append([
        place("ball", "72824p01", WHITE, (20, -58, 150),
              purpose="printed football at the edge of the box")])

    return section("pitch.ldr", "Elevated pitch plinth with turf, markings, "
                                "corner flags and ball", steps)


# --------------------------------------------------------------------------- #
# goal.ldr -- open frame, 4-stud mouth, back stanchions (opens toward -z local)
# --------------------------------------------------------------------------- #
def goal_section():
    posts, bars = [], []
    for xc in (-60, 60):
        posts.append(place(f"post-f-{xc}", "3004", WHITE, (xc, -24, 0),
                           repeat=(3, (0, -24, 0)), purpose="front post"))
        posts.append(place(f"post-b-{xc}", "3004", WHITE, (xc, -24, 20),
                           repeat=(3, (0, -24, 0)), purpose="back stanchion"))
    bars.append(place("bar-f", "3666", WHITE, (0, -80, 0), purpose="crossbar"))
    bars.append(place("bar-b", "3666", WHITE, (0, -80, 20), purpose="back rail"))
    bars.append(place("rail-w", "3023b", WHITE, (-60, -88, 10), yaw=90,
                      purpose="side rail"))
    bars.append(place("rail-e", "3023b", WHITE, (60, -88, 10), yaw=90))
    return section("goal.ldr", "Open-frame goal with back stanchions",
                   [posts, bars])


# --------------------------------------------------------------------------- #
# stands -- one parametric terrace
# --------------------------------------------------------------------------- #
def stand_section(name, L, rows, roof_y, main=False):
    """Build one terrace stand.

    Local frame: origin at the centre of the front-wall outer face, y=0 table.
    z runs 0 (pitch side) to 220 (rear facade). Length L studs (26 or 20);
    ``rows`` grille tiers; ``roof_y`` the roof plate origin (-280 or -208).
    """
    W = 10 * L
    xs8, fills8 = grid8(L)
    xs4, fills4 = grid4(L)
    n2 = L // 2
    desc = (f"{'Main' if main else 'Side' if L == 26 else 'End'} terrace stand: "
            f"{rows} grille rows, cantilever roof")

    steps = []

    # 1. front wall + walkway (terrace threshold), dark grey below white trim
    wall = []
    for y in (-24, -48):
        wall.append(place(f"fw-{y}", "3007", GREY, (xs8[0], y, 20),
                          repeat=(len(xs8), (160, 0, 0))))
        for xc in fills8:
            wall.append(place(f"fw-f-{y}-{xc}", "3003", GREY, (xc, y, 20)))
    wall.append(place("walkway", "3020", WHITE, (xs4[0], -56, 20),
                      repeat=(len(xs4), (80, 0, 0)), purpose="front walkway"))
    for xc in fills4:
        wall.append(place(f"walkway-f-{xc}", "3022", WHITE, (xc, -56, 20)))
    steps.append(wall)

    # 2. terrace: vertical grille rows (red seats) with white plate bands
    terr = []
    for k in range(rows):
        y = -80 - 24 * k
        terr.append(place(f"seat-r{k}", "2877", RED, (-W + 20, y, 50),
                          repeat=(n2, (40, 0, 0)), purpose=f"seat row {k + 1}"))
        if k % 2 == 1 and k < rows - 1:
            terr.append(place(f"band-r{k}", "3023b", WHITE, (-W + 20, y - 8, 50),
                              repeat=(n2, (40, 0, 0)), purpose="tier walkway band"))
    terr.append(place("band-top", "3022", WHITE, (-W + 20, -80 - 24 * (rows - 1) - 8, 60),
                      repeat=(n2, (40, 0, 0)), purpose="top walkway"))
    steps.append(terr)

    # 3. side closure walls: front block rises with the terrace, mid block
    #    rises to the roof band; 1-wide bricks at x = +/-(W+10)
    side = []
    ka = {5: 7, 6: 8, 8: 10}[rows]
    nb = 11 if roof_y == -280 else 8
    pa, pb = -24 * ka - 8, -24 * ka - 16   # cap plates over the front block
    for sx in (1, -1):
        tag = "e" if sx > 0 else "w"
        x = sx * (W + 10)
        for zc in (20, 60):
            side.append(place(f"side-a-{tag}-{zc}", "3004", GREY, (x, -24, zc),
                              yaw=90, repeat=(ka, (0, -24, 0))))
        for y in (pa, pb):
            for zc in (20, 60):
                side.append(place(f"side-a-cap-{tag}-{y}-{zc}", "3023b", WHITE,
                                  (x, y, zc), yaw=90))
        for zc in (100, 140):
            side.append(place(f"side-b-{tag}-{zc}", "3004", GREY, (x, -24, zc),
                              yaw=90, repeat=(nb, (0, -24, 0))))
        side.append(place(f"side-b-col-{tag}", "3005", GREY, (x, -24, 170),
                          repeat=(nb, (0, -24, 0))))
        side.append(place(f"side-b-cap-{tag}", "3023b", WHITE, (x, roof_y + 8, 100),
                          yaw=90, repeat=(3, (0, 0, 40)),
                          purpose="roof trim band"))
    steps.append(side)



    # 4. rear facade: grey plinth courses, white upper wall, white trim band
    nf = 11 if roof_y == -280 else 8
    fac = []
    for k in range(1, nf + 1):
        y = -24 * k
        col = GREY if k <= 2 else WHITE
        fac.append(place(f"fac-{k}", "3007", col, (xs8[0], y, 200),
                         repeat=(len(xs8), (160, 0, 0))))
        for xc in fills8:
            fac.append(place(f"fac-f-{k}-{xc}", "3003", col, (xc, y, 200)))
    fac.append(place("fac-band", "3020", WHITE, (xs4[0], roof_y + 8, 200),
                     repeat=(len(xs4), (80, 0, 0)), purpose="roof seating band"))
    for xc in fills4:
        fac.append(place(f"fac-band-f-{xc}", "3022", WHITE, (xc, roof_y + 8, 200)))
    steps.append(fac)

    # 5. cantilever roof: plates bonded to the facade band, tiled top
    roof = []
    roof.append(place("roof-plate", "3035", WHITE, (xs8[0], roof_y, 160),
                      repeat=(len(xs8), (160, 0, 0)),
                      purpose="4-deep canopy plate"))
    for xc in fills8:
        roof.append(place(f"roof-plate-f-{xc}", "3022", WHITE, (xc, roof_y, 160)))
    yt = roof_y - 8
    for zc in (140, 180):
        roof.append(place(f"roof-tile-{zc}", "87079", WHITE, (xs4[0], yt, zc),
                          repeat=(len(xs4), (80, 0, 0)),
                          purpose="canopy roof tiles"))
    steps.append(roof)

    # 6. glazed fascia hanging at the leading roof edge
    fas = [place("fascia", "4215b", GLASS, (xs4[0], roof_y + 8, 120),
                 repeat=(len(xs4), (80, 0, 0)),
                 purpose="trans-light-blue windscreen fascia")]
    steps.append(fas)

    # 7. main stand only: rooftop scoreboard
    if main:
        sb = []
        for y in (-312, -336):
            sb.append(place(f"sbox-{y}", "3004", BLACK, (-60, y, 190),
                            repeat=(4, (40, 0, 0)), purpose="scoreboard housing"))
        sb.append(place("sbox-cap", "3023b", WHITE, (-60, -344, 190),
                        repeat=(4, (40, 0, 0))))
        sb.append(place("sscreen", "4215b", GLASS, (-40, -360, 170),
                        repeat=(3, (40, 0, 0)), purpose="glazed screen"))
        sb.append(place("sscreen-cap", "3023b", WHITE, (-60, -368, 170),
                        repeat=(4, (40, 0, 0))))
        steps.append(sb)

    return section(name, desc, steps)


# --------------------------------------------------------------------------- #
# floodlight.ldr -- corner pylon
# --------------------------------------------------------------------------- #
def floodlight_section():
    return section(
        "floodlight.ldr", "Corner floodlight pylon with 8 clear lamps",
        [
            [place("pylon-base", "3022", GREY, (0, -8, 0),
                   purpose="pylon footing")],
            [place("pylon-mast", "3941", WHITE, (0, -32, 0),
                   repeat=(14, (0, -24, 0)), purpose="round-brick mast")],
            [place("pylon-rig", "3020", WHITE, (0, -352, 0),
                   purpose="lamp rig plate")],
            [place("lamps-a", "3062b", LAMP, (-30, -376, -10),
                   repeat=(4, (20, 0, 0)), purpose="lamp row"),
             place("lamps-b", "3062b", LAMP, (-30, -376, 10),
                   repeat=(4, (20, 0, 0)), purpose="lamp row")],
        ])



# --------------------------------------------------------------------------- #
# stadium.ldr -- scene composition (root)
# --------------------------------------------------------------------------- #
def scene_section():
    return section(
        "stadium.ldr", "Meridian Park: four-stand terrace ground with "
                       "corner pylons",
        [
            [place("pitch", "pitch.ldr", 16, (0, 0, 0),
                   purpose="elevated pitch, world origin")],
            [place("stand-main", "stand-main.ldr", 16, (0, 0, 260),
                   purpose="8-row main stand, north touchline"),
             place("stand-long", "stand-long.ldr", 16, (0, 0, -260), yaw=180,
                   purpose="6-row stand, south touchline")],
            [place("stand-end-e", "stand-end.ldr", 16, (200, 0, 0), yaw=90,
                   purpose="5-row east end stand"),
             place("stand-end-w", "stand-end.ldr", 16, (-200, 0, 0), yaw=-90,
                   purpose="5-row west end stand")],
            [place("goal-n", "goal.ldr", 15, (0, -40, 240), yaw=180,
                   purpose="north goal on the goal line"),
             place("goal-s", "goal.ldr", 15, (0, -40, -240),
                   purpose="south goal on the goal line")],
            [place("pylon-ne", "floodlight.ldr", 16, (310, 0, 330),
                   purpose="corner pylon"),
             place("pylon-nw", "floodlight.ldr", 16, (-310, 0, 330)),
             place("pylon-se", "floodlight.ldr", 16, (310, 0, -330)),
             place("pylon-sw", "floodlight.ldr", 16, (-310, 0, -330))],
        ])


# --------------------------------------------------------------------------- #
def build_plan():
    return {
        "version": 1,
        "author": AUTHOR,
        "sections": [
            scene_section(),
            pitch_section(),
            goal_section(),
            stand_section("stand-main.ldr", 26, 8, -280, main=True),
            stand_section("stand-long.ldr", 26, 6, -280),
            stand_section("stand-end.ldr", 20, 5, -208),
            floodlight_section(),
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=HERE / "stadium.plan.json")
    args = ap.parse_args()
    plan = build_plan()
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    n = sum(len(s) for sec in plan["sections"] for s in sec["steps"])
    print(f"wrote {args.output} ({len(plan['sections'])} sections, {n} placements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

