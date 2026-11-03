#!/usr/bin/env python3
"""Reproduce the hinge-angle study that fixed the visor and ramp poses (review aid).

1. 3937/3938 hinge brick with a 1x4 plate on the top, rotated nose-up about the
   hinge line, with the pair at yaw 0 and yaw 180. Only yaw 180 lets the plated top
   swing aft without cutting the base's square top edge.
2. 44302a/44301a click hinge (the ramp lip): mesh crossings every 2.5 degrees show
   the toothed detents at multiples of 22.5 degrees.

Crossings use mesh_clearance.py on real library triangles. Depths of hundredths of an
LDU on the hinge pin are faceting of coincident cylinders; they also occur in the
designed closed pose. Run from the repository root:

    .venv/bin/python examples/an225/hinge_study.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from ldraw_tools.builder import rotation  # noqa: E402
import mesh_clearance as mc  # noqa: E402


def placed(part, R, orient, closed, axis):
    """Part authored at `closed` with orientation `orient`, then rotated by R about `axis`."""
    closed, axis = np.asarray(closed, float), np.asarray(axis, float)
    return dict(part=part, position=(R @ (closed - axis) + axis).tolist(), matrix=(R @ orient).tolist())


def pair(a, b):
    A, B = mc.world(a), mc.world(b)
    n1, _, d1 = mc.crossings(A, B)
    n2, _, d2 = mc.crossings(B, A)
    return dict(crossing_edges=n1 + n2, max_penetration_ldu=round(max(d1, d2), 3))


def hinge_brick(yaw):
    Y = np.array(rotation('y', yaw).rows)
    axis = [0, -14, 0]                     # 10 LDU below the 3938 stud plane at Y=-24
    base = dict(part='3937.dat', position=[0, -24, 0], matrix=Y.tolist())
    rows = []
    for deg in range(0, -95, -5):          # negative = nose-up for the visor (top swings to +Z)
        R = np.array(rotation('x', deg).rows)
        top = placed('3938.dat', R, Y, [0, -24, 0], axis)
        plate = placed('3710.dat', R, Y, [0, -32, 0], axis)
        rows.append(dict(degrees=deg, base_top=pair(base, top), base_plate=pair(base, plate)))
    return rows


def click_hinge():
    fixed = dict(part='44302a.dat', position=[0, 0, 0], matrix=np.array(rotation('y', 90).rows).tolist())
    axis = [0, 2, -30]
    rows = []
    for deg in np.arange(0, 92.5, 2.5):
        R = np.array(rotation('x', float(deg)).rows)
        moving = placed('44301a.dat', R, np.array(rotation('y', -90).rows), [0, 0, -60], axis)
        rows.append(dict(degrees=float(deg), **pair(fixed, moving)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=HERE.parents[1] / "output/an225-hinge-study.json")
    args = parser.parse_args()
    result = dict(
        method='mesh_clearance.py edge/triangle crossings on library geometry; see its docstring',
        hinge_brick_yaw0=hinge_brick(0),
        hinge_brick_yaw180=hinge_brick(180),
        click_hinge=click_hinge(),
        chosen=dict(visor='3937/3938 at yaw 180, -70 deg', ramp='44301a/44302a at the 22.5 deg detent'),
    )
    out = args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + '\n')
    for key in ('hinge_brick_yaw0', 'hinge_brick_yaw180'):
        print(key, ' '.join(f"{r['degrees']}:{r['base_plate']['crossing_edges']}" for r in result[key]))
    print('click', ' '.join(f"{r['degrees']:g}:{r['crossing_edges']}" for r in result['click_hinge']))
    print('wrote', out)


if __name__ == '__main__':
    main()
