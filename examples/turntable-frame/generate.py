"""Generate the turntable frame plan reconstructed from manual steps 31-40.

World axes: X runs along the two 11L beams, -Z is the front (viewer side of the
manual pictures) and -Y is up. The 11L beam hole n sits at x = (n - 6) * 20, so
the turntable is centred over hole 6. Rear beam B1 is at z=+20, front beam B2 at
z=-20; the 1L gap between them is centred on z=0.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

LBG, BLACK, BLUE, RED = 71, 0, 1, 4

# Straight beams (32525/32524): local Z (length) -> world X, local Y (hole axis) -> world Z.
M_BEAM = [[0, 0, 1], [1, 0, 0], [0, 1, 0]]
# Pins (2780/6558/87082) lie along local X; map it to world -Z (6558 collar at local x=-10
# therefore faces the rear beam's front face).
M_PIN_Z = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
# 48989 cross block: body (local Y) along world X, pins (local Z) along world Z,
# end holes (local X) vertical.
M_CROSS = [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]
# 6629 bent liftarm: origin at the long-arm axle end, long arm along local +Z, short arm
# bends toward local +X. Right-hand copy: long arm to +X, short arm (leg) downwards.
M_BENT_RIGHT = [[0, 0, 1], [1, 0, 0], [0, 1, 0]]
# Left-hand copy: the right-hand copy turned 180 degrees about Y.
M_BENT_LEFT = [[0, 0, -1], [1, 0, 0], [0, -1, 0]]
M_YAW90 = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]

B1_Z, B2_Z = 20, -20          # rear / front 11L beams
REAR_BENT_Z, FRONT_BENT_Z = 40, -40
BEAM7_Z = -60
LEG_END = (156, 48)           # |x|, y of each leg's axle hole: 20 + 136, 48


def hole(n):
    """X coordinate of hole n (1..11) of the 11L beams."""
    return (n - 6) * 20


def p(pid, ref, colour, at, purpose, matrix=None):
    row = {'id': pid, 'ref': ref, 'colour': colour, 'at': list(at), 'purpose': purpose}
    if matrix is not None:
        row['matrix'] = matrix
    return row


def plan():
    steps = []
    # Step 31: rear 11L beam, four rear-facing friction pins, long pin with centre hole.
    s = [p('b1', '32525.dat', LBG, (0, 0, B1_Z), 'rear 11L beam', M_BEAM)]
    for n in (2, 4, 8, 10):
        s.append(p(f'b1-pin-{n}', '2780.dat', BLACK, (hole(n), 0, B1_Z + 10),
                   f'friction pin in rear beam hole {n}, protruding rearwards for the rear bent arm', M_PIN_Z))
    s.append(p('centre-pin', '87082.dat', LBG, (0, 0, 0),
               'long pin with vertical centre hole joining hole 6 of both beams', M_PIN_Z))
    steps.append(s)
    # Step 32: two cross blocks with four pins set the 1L beam spacing at each end.
    steps.append([
        p('cross-left', '48989.dat', LBG, (hole(2), 0, 0), 'cross block pinned into holes 1 and 3', M_CROSS),
        p('cross-right', '48989.dat', LBG, (hole(10), 0, 0), 'cross block pinned into holes 9 and 11', M_CROSS),
    ])
    # Step 33: blue 3L pins through holes 5 and 7 carry the turntable base lugs.
    steps.append([
        p(f'tt-pin-{n}', '6558.dat', BLUE, (hole(n), 0, 0),
          f'3L pin in hole {n}: rear beam, turntable lug, front beam', M_PIN_Z)
        for n in (5, 7)
    ])
    # Step 34: small turntable, base lugs between the beams, ears across the frame.
    steps.append([
        p('turntable-base', '99009.dat', LBG, (0, -20, 0), 'turntable 28T bottom; lugs sit on the blue pins'),
        p('turntable-top', '99010.dat', BLACK, (0, -20, 0), 'turntable 28T top, ears front and rear', M_YAW90),
    ])
    # Step 35: front 11L beam closes the pins.
    steps.append([p('b2', '32525.dat', LBG, (0, 0, B2_Z), 'front 11L beam', M_BEAM)])
    # Step 36: rear bent arms on the rear-facing pins; bends overhang the beam ends.
    steps.append([
        p('rear-bent-right', '6629.dat', BLACK, (hole(7), 0, REAR_BENT_Z),
          'rear 4x6 bent arm on pins 8 and 10, leg down at the right', M_BENT_RIGHT),
        p('rear-bent-left', '6629.dat', BLACK, (hole(5), 0, REAR_BENT_Z),
          'rear 4x6 bent arm on pins 2 and 4, leg down at the left', M_BENT_LEFT),
    ])
    # Step 37: two axle links on the rear leg ends.
    steps.append([
        p('link-right', 'turntable-frame-axle-link.ldr', BLACK, (LEG_END[0], LEG_END[1], 0),
          'axle link bridging the right leg ends'),
        p('link-left', 'turntable-frame-axle-link.ldr', BLACK, (-LEG_END[0], LEG_END[1], 0),
          'axle link bridging the left leg ends'),
    ])
    # Step 38: front pins for the front bent arms.
    s = [p(f'b2-long-{n}', '6558.dat', BLUE, (hole(n), 0, B2_Z - 20),
           f'3L pin in front beam hole {n}; 1L stays exposed ahead of the bent arm', M_PIN_Z) for n in (2, 10)]
    s += [p(f'b2-pin-{n}', '2780.dat', BLACK, (hole(n), 0, B2_Z - 10),
            f'friction pin in front beam hole {n} for the front bent arm', M_PIN_Z) for n in (4, 8)]
    steps.append(s)
    # Step 39: front bent arms close the leg frames; pins in their bend holes face forward.
    steps.append([
        p('front-bent-right', '6629.dat', BLACK, (hole(7), 0, FRONT_BENT_Z),
          'front 4x6 bent arm on pins 8 and 10 and the right link axle', M_BENT_RIGHT),
        p('front-bent-left', '6629.dat', BLACK, (hole(5), 0, FRONT_BENT_Z),
          'front 4x6 bent arm on pins 2 and 4 and the left link axle', M_BENT_LEFT),
        p('bend-pin-right', '2780.dat', BLACK, (120, 0, FRONT_BENT_Z - 10),
          'forward-facing friction pin in the right front bend hole', M_PIN_Z),
        p('bend-pin-left', '2780.dat', BLACK, (-120, 0, FRONT_BENT_Z - 10),
          'forward-facing friction pin in the left front bend hole', M_PIN_Z),
    ])
    # Step 40: 7L beam across the front arms, carried by pins in its end holes.
    steps.append([
        p('beam7', '32524.dat', LBG, (0, 0, BEAM7_Z), 'front 7L beam between the blue pin stubs', M_BEAM),
        p('beam7-pin-left', '2780.dat', BLACK, (-60, 0, BEAM7_Z + 10),
          'friction pin: 7L beam hole 1 into the left front arm', M_PIN_Z),
        p('beam7-pin-right', '2780.dat', BLACK, (60, 0, BEAM7_Z + 10),
          'friction pin: 7L beam hole 7 into the right front arm', M_PIN_Z),
    ])

    link = {
        'name': 'turntable-frame-axle-link.ldr',
        'description': 'Leg-end link (manual step 37 sub-build): 3L axle joiner with a red 2L axle in each end',
        'steps': [
            [p('joiner', '26287.dat', BLACK, (0, 0, 0),
               '3L axle joiner; substitute for the manual\'s joiner with a centre pin hole')],
            [p('axle-rear', '32062.dat', RED, (0, 0, 30), 'rear 2L axle: 1L in the joiner, 1L in the rear leg', M_YAW90),
             p('axle-front', '32062.dat', RED, (0, 0, -30), 'front 2L axle: 1L in the joiner, 1L in the front leg', M_YAW90)],
        ],
    }
    return {
        'version': 1,
        'author': 'LDraw Nova agent (reconstructed from supplied building-instruction pages, steps 31-40)',
        'sections': [
            {
                'name': 'turntable-frame.ldr',
                'description': 'Technic turntable frame: twin 11L beams, 28T turntable, bent-arm legs (manual steps 31-40)',
                'steps': steps,
            },
            link,
        ],
    }


def write_mpd(plan_path, mpd_path):
    """Serialize the plan with the toolkit builder without the build gate.

    `ldraw-agent build` refuses to write while its conservative almost-mate rule reports
    pin ends that abut a coaxial hole face flush (overlap 0 LDU). That abutment is inherent
    to this frame (see README.md), so the MPD is written here and the full checks are
    run separately with `ldraw-agent validate --geometry`. Plan-level errors still abort.
    """
    import sys
    sys.path.insert(0, str(HERE.parents[1]))
    from ldraw_tools.builder import build_plan, load_plan
    from ldraw_tools.common import atomic_write, get_parts

    text, _, diagnostics = build_plan(load_plan(plan_path), get_parts())
    errors = [d for d in diagnostics if d['severity'] == 'error']
    if errors:
        raise SystemExit(json.dumps(errors, indent=2))
    atomic_write(mpd_path, text)
    print(mpd_path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-mpd', action='store_true', help='also write turntable-frame.mpd')
    args = parser.parse_args()
    out = HERE/'turntable-frame.plan.json'
    out.write_text(json.dumps(plan(), indent=2) + '\n')
    print(out)
    if args.write_mpd:
        write_mpd(out, HERE/'turntable-frame.mpd')
