"""Pneumatic press: a hand pump, valve and cylinder joined by three LSynth hoses.

Inspired by lsynth-nova's TECHNIC_PNEUMATIC_HOSE example (pump, switch and cylinder with beveled
hoses), rebuilt with current pneumatic parts on a working bench. Run from the repository root:

    .venv/bin/python examples/flex/pneumatic-press/generate.py
    ./ldraw-agent flex build examples/flex/pneumatic-press/hoses.ldr \
        --output examples/flex/pneumatic-press/hoses.mpd --namespace press-hoses --force
    ./ldraw-agent review examples/flex/pneumatic-press/press.plan.json --outdir output/press-review --contacts all

The generator writes the plan and the hose constraint source from the same nozzle frames, so a
moved component also moves its hose ends. Every hose end starts on a nozzle base and runs straight
along the nozzle before it bends, as in the LSynth example.

World axes: X right, -Z front, -Y up; Y=0 is the bench top.
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
from ldraw_tools.flex_authoring import Endpoint, Waypoint, hose_waypoints, marker_matrix as route_matrix  # noqa: E402

AUTHOR = 'Pneumatic press generator (Claude Code, Claude Opus 5.5) for anteloc'

BENCH, FRAME, ACCENT, PNEU, DIE = 72, 71, 14, 71, 0      # dark/light bluish grey, yellow, grey parts, black
SUPPLY, LINE_UP, LINE_DOWN = 0, 4, 1                     # hose colours: supply black, cylinder red and blue
HOSE_TYPE = 'TECHNIC_PNEUMATIC_HOSE_BEVELED'

COLUMN_BRICKS = 8
BEAM_TOP = -24 * COLUMN_BRICKS - 24                      # 3702 crossbeam on the columns
BEAM_HOLE = BEAM_TOP + 10                                # its holes run along Z, 10 below its top
PRESS = np.array([0.0, 0.0, 30.0])                       # press axis (x, -, z): cylinder in front of the beam
BEAM_Z = 50
STROKE = 116                                             # 74981-f2 (extended): rod-end hole below the mount hole
HEAD_TOP = BEAM_HOLE + STROKE - 10                       # 3701 head brick hangs from the rod end
ANVIL_TOP = -64

PUMP = np.array([-120.0, -14.0, -20.0])                  # 2797c01-f1 origin: its 2 x 2 base bottom is 14 below
VALVE = np.array([40.0, -56.0, -110.0])                  # 4694c01-f1 origin: 56 above its stud sockets (x along the grid)


def Ry(degrees):
    return np.array(rotation('y', degrees).rows, float)


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


DIMS = {'3001': (4, 2), '3003': (2, 2), '3004': (2, 1), '3020': (4, 2), '3034': (8, 2), '3035': (8, 4),
        '92438': (16, 8), '3701': (4, 1), '3702': (8, 1), '3069b': (2, 1), '87079': (4, 2), '3068b': (2, 2)}

# Rigid placements of the pneumatic parts. Local nozzle frames (base, axis, length) are the R=4 male
# cylinders in each part's LDCad shadow data, read with `./ldraw-agent part`.
CYL_R = np.array([[0, 0, -1], [0, -1, 0], [-1, 0, 0]], float)   # rod down, holes along Z, nozzles +X
PUMP_R = Ry(-90)                                                   # nozzle points +X
VALVE_R = Ry(-90)                                                  # nozzles face the press (+Z), lever to the right
CYL_ORIGIN = np.array([PRESS[0], BEAM_HOLE, PRESS[2]])
NOZZLES = {
    'pump': (PUMP, PUMP_R, (0, 0, -20), (0, 0, -1), 16),
    'valve-up': (VALVE, VALVE_R, (10, 15, 0), (1, 0, 0), 14),
    'valve-in': (VALVE, VALVE_R, (10, 26, 6), (1, 0, 0), 14),
    'valve-down': (VALVE, VALVE_R, (10, 37, 0), (1, 0, 0), 14),
    'cyl-top': (CYL_ORIGIN, CYL_R, (0, -10, -10), (0, 0, -1), 16),
    'cyl-bottom': (CYL_ORIGIN, CYL_R, (0, -60, -10), (0, 0, -1), 16),
}


def nozzle(name):
    """World nozzle base and outward unit axis."""
    origin, r, base, axis, _ = NOZZLES[name]
    axis = r @ np.array(axis, float)
    return origin + r @ np.array(base, float), axis / np.linalg.norm(axis)


# --- rigid sections --------------------------------------------------------------------------------

def bench():
    s = Section('press-bench.ldr', 'Press bench: two bonded plate layers')
    s.box('bench-1', '92438', BENCH, -160, 160, -160, 0, 8)
    s.box('bench-1-rear', '92438', BENCH, -160, 160, 0, 160, 8)
    s.step()
    s.box('bench-2-mid', '92438', BENCH, -160, 160, -80, 80, 0, 'Bridges the lower seam')
    s.box('bench-2-front-l', '3035', BENCH, -160, 0, -160, -80, 0)
    s.box('bench-2-front-r', '3035', BENCH, 0, 160, -160, -80, 0)
    s.box('bench-2-rear-l', '3035', BENCH, -160, 0, 80, 160, 0)
    s.box('bench-2-rear-r', '3035', BENCH, 0, 160, 80, 160, 0)
    return s


def frame():
    """C-frame: two 2 x 2 columns, a Technic crossbeam with column caps, a bonding top plate and anvil."""
    s = Section('press-frame.ldr', 'Press frame: columns, Technic crossbeam, top plate and anvil')
    for i in range(COLUMN_BRICKS):
        s.step()
        for side, sx in (('l', -1), ('r', 1)):
            x0, x1 = sorted((40 * sx, 80 * sx))
            s.box(f'column-{side}{i}', '3003', ACCENT if i % 2 else FRAME, x0, x1, 40, 80, -24 * (i + 1))
    s.step()
    s.box('beam', '3702', FRAME, -80, 80, BEAM_Z - 10, BEAM_Z + 10, BEAM_TOP, 'Technic crossbeam; the cylinder hangs from its centre hole')
    for side, sx in (('l', -1), ('r', 1)):
        x0, x1 = sorted((40 * sx, 80 * sx))
        s.box(f'cap-{side}', '3004', FRAME, x0, x1, 60, 80, BEAM_TOP, 'Column cap beside the beam')
    s.step()
    s.box('top', '3034', ACCENT, -80, 80, 40, 80, BEAM_TOP - 8, 'Bonds beam and column caps')
    s.step()
    s.box('anvil-a', '3001', DIE, -40, 40, 20, 60, -24)
    s.box('anvil-b', '3001', DIE, -40, 40, 20, 60, -48)
    s.box('anvil-plate', '3020', FRAME, -40, 40, 20, 60, -56)
    s.box('anvil-face', '87079', FRAME, -40, 40, 20, 60, ANVIL_TOP, 'Smooth anvil face')
    return s


def press():
    """Cylinder pinned to the crossbeam; press head pinned to the rod end, with a die plate below."""
    s = Section('press-ram.ldr', 'Press ram: extended cylinder, pins, head and die')
    s.add('cylinder', '74981-f2', PNEU, CYL_ORIGIN, CYL_R, 'Extended 1 x 1 cylinder, rod down')
    s.add('mount-pin', '3673', DIE, [PRESS[0], BEAM_HOLE, (PRESS[2] + BEAM_Z) / 2], Ry(90), 'Mount ring to beam hole')
    rod_end = BEAM_HOLE + STROKE
    s.step()
    s.box('head', '3701', ACCENT, -40, 40, BEAM_Z - 10, BEAM_Z + 10, HEAD_TOP, 'Press head')
    s.add('head-pin', '3673', DIE, [PRESS[0], rod_end, (PRESS[2] + BEAM_Z) / 2], Ry(90), 'Rod end to head hole')
    s.step()
    s.box('die', '3020', DIE, -40, 40, 20, 60, HEAD_TOP + 24, 'Die plate under the head; 4 LDU above the anvil face')
    return s


def controls():
    s = Section('press-controls.ldr', 'Press controls: hand pump and valve')
    s.add('pump', '2797c01-f1', PNEU, PUMP, PUMP_R, 'Hand pump on a 2 x 2 stud pad')
    s.add('valve', '4694c01-f1', PNEU, VALVE, VALVE_R, 'Valve; nozzles toward the press, lever to the right')
    return s


# --- hoses -----------------------------------------------------------------------------------------

LEAD = 22                                                # straight run beyond each nozzle base
# name: (colour, from, to, via [(point, direction), ...])
HOSES = [
    ('supply', SUPPLY, 'pump', 'valve-in', []),
    ('line-up', LINE_UP, 'valve-up', 'cyl-top', [((80, -120, -30), (0.2, -1, 0.5))]),
    ('line-down', LINE_DOWN, 'valve-down', 'cyl-bottom', [((74, -80, -36), (0.2, -1, 0.5))]),
]


def marker_matrix(direction):
    """Retain the reviewed fixture's roll while using the shared frame helper."""
    d = np.asarray(direction, float) / np.linalg.norm(direction)
    return route_matrix(d, up=(0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0))


def hose_markers(start, end, via):
    p0, a0 = nozzle(start)
    p1, a1 = nozzle(end)
    return [(w.at, w.direction) for w in hose_waypoints(
        Endpoint(p0, a0, LEAD), Endpoint(p1, a1, LEAD), [Waypoint(p, d) for p, d in via])]


def hose_source():
    lines = ['0 Pneumatic press hoses: editable LSynth constraints', '0 Name: hoses.ldr',
             f'0 Author: {AUTHOR}', '0 !LDRAW_ORG Model']
    for name, colour, start, end, via in HOSES:
        lines += [f'0 // {name}', f'0 SYNTH BEGIN {HOSE_TYPE} {colour}', '0 SYNTH SHOW']
        for p, d in hose_markers(start, end, via):
            m = marker_matrix(d)
            lines.append('1 %d %s %s LS01.dat' % (colour, ' '.join(f'{clean(v):g}' for v in p),
                                                    ' '.join(f'{clean(v):.6f}'.rstrip('0').rstrip('.') for v in m.ravel())))
        lines.append('0 SYNTH END')
    return '\r\n'.join(lines) + '\r\n'


def build():
    modules = [bench(), frame(), press(), controls()]
    root = Section('press.ldr', 'Pneumatic press: pump, valve and cylinder joined by three hoses')
    root.add('bench', 'press-bench.ldr', 16, [0, 0, 0])
    root.step().add('frame', 'press-frame.ldr', 16, [0, 0, 0])
    root.step().add('ram', 'press-ram.ldr', 16, [0, 0, 0])
    root.step().add('controls', 'press-controls.ldr', 16, [0, 0, 0])
    root.step().add('hoses', 'press-hoses.ldr', 16, [0, 0, 0])
    return dict(version=1, author=AUTHOR, assets=['hoses.mpd'], sections=[root.plan()] + [m.plan() for m in modules])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--output', type=Path, default=HERE / 'press.plan.json')
    parser.add_argument('--hoses', type=Path, default=HERE / 'hoses.ldr')
    parser.add_argument('--automatic', action='store_true', help='Declare hose source and limits in the plan; review builds the asset')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    plan = build()
    if args.automatic:
        import os
        plan['assets'] = [dict(source=os.path.relpath(args.hoses.resolve(), args.output.parent.resolve()),
                              namespace='press-hoses', checks=dict(min_radius=15, min_separation=10))]
    args.output.write_text(json.dumps(plan, indent=1) + '\n')
    args.hoses.parent.mkdir(parents=True, exist_ok=True)
    args.hoses.write_bytes(hose_source().encode())
    print(args.output)
    print(args.hoses)


if __name__ == '__main__':
    main()
