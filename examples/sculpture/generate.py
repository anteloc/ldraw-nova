"""Recover sculpture cells from a BrickBuilderAI rectangular-brick LDraw export.

Download the Pikachu linked in this folder's README, then pass its .ldr path.
This example accepts only BrickBuilder's six brick sizes and two exported rotations;
it is not a general LDraw importer. No provider credentials are required.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

LIBRARY = Path(__file__).resolve().parents[2] / 'ldraw_tools/sculpture/brick_library.json'


def export_cells(text: str) -> list[list[int]]:
    catalogue = json.loads(LIBRARY.read_text())
    dimensions = {v['partID'].lower(): (v['height'], v['width']) for v in catalogue.values()}
    rotations = {(0., 0., 1., 0., 1., 0., -1., 0., 0.): False,
                 (-1., 0., 0., 0., 1., 0., 0., 0., -1.): True}
    cells = {}
    for number, line in enumerate(text.splitlines(), 1):
        fields = line.split()
        if not fields or fields[0] == '0':
            continue
        if len(fields) != 15 or fields[0] != '1' or fields[-1].lower() not in dimensions:
            raise ValueError(f'Line {number}: use a plain BrickBuilder rectangular-brick export.')
        colour = int(fields[1])
        if not 0 <= colour <= 511 or colour in (16, 24):
            raise ValueError(f'Line {number}: use an explicit LDraw colour.')
        position = [float(v) for v in fields[2:5]]
        matrix = tuple(float(v) for v in fields[5:14])
        if matrix not in rotations:
            raise ValueError(f'Line {number}: unsupported rotation.')
        h, w = dimensions[fields[-1].lower()]
        if rotations[matrix]:
            h, w = w, h
        origin = [position[0] / 20 - h / 2, position[2] / 20 - w / 2, -position[1] / 24]
        if any(not math.isfinite(v) or not math.isclose(v, round(v), abs_tol=1e-8) or abs(v) > 100000 for v in origin):
            raise ValueError(f'Line {number}: brick is not aligned to integer sculpture cells.')
        x, y, z = (round(v) for v in origin)
        for i in range(x, x + h):
            for j in range(y, y + w):
                key = (i, j, z)
                if key in cells:
                    raise ValueError(f'Line {number}: overlapping brick footprints.')
                cells[key] = colour
        if len(cells) > 65536:
            raise ValueError('Export exceeds the sculpture cell limit.')
    if not cells:
        raise ValueError('No sculpture bricks in the export.')
    return [[x, y, z, c] for (x, y, z), c in sorted(cells.items())]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('export', type=Path)
    parser.add_argument('--output', type=Path, default=Path('output/sculpture-example/pikachu.voxels.json'))
    args = parser.parse_args()
    if args.export.stat().st_size > 8 * 1024 * 1024:
        parser.error('Export exceeds 8 MB.')
    try:
        rows = export_cells(args.export.read_text())
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'voxels': rows}))
    print(args.output)


if __name__ == '__main__':
    main()
