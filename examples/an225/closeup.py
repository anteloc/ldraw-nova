#!/usr/bin/env python3
"""Close-up review renders of selected An-225 regions (review aid, not part of the model).

Uses the toolkit's LeoCAD adapter with an explicit framing box, so the same MPD is
rendered and only the camera changes. Run from the repository root:

    .venv/bin/python examples/an225/closeup.py [MPD] [--outdir DIR] [--regions nose tail ...]
"""
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ldraw_tools.common import library_path  # noqa: E402
from ldraw_tools.external import render  # noqa: E402

S0 = 52


def box(x0, x1, h0, h1, s0, s1):
    """Framing box from studs across (x), LDU height (h, upward) and stations (s)."""
    v = lambda x, y, z: SimpleNamespace(x=x, y=y, z=z)  # noqa: E731
    return SimpleNamespace(min=v(20 * x0, -h1, 20 * (s0 - S0)), max=v(20 * x1, -h0, 20 * (s1 - S0)))


REGIONS = {
    'nose': (box(-7, 7, 0, 330, -3, 22), ('home', 'left', 'front')),
    'tail': (box(-22, 22, 150, 450, 78, 106), ('home', 'left', 'back')),
    'gear': (box(-8, 8, 0, 150, 8, 60), ('left', 'bottom')),
    'engines': (box(8, 32, 120, 280, 28, 50), ('home', 'front')),
    'aft': (box(-7, 7, 20, 280, 62, 106), ('left', 'home', 'bottom')),
    'sponson': (box(-8, 8, 0, 160, 30, 64), ('left', 'home')),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('mpd', nargs='?', type=Path, default=Path(__file__).with_name('an225-mriya.mpd'))
    parser.add_argument('--outdir', type=Path, default=Path(__file__).with_name('review') / 'closeups')
    parser.add_argument('--regions', nargs='+', default=list(REGIONS))
    args = parser.parse_args()
    for name in args.regions:
        bounds, views = REGIONS[name]
        result = render(args.mpd, library_path(), args.outdir / name, views=views, bounds=bounds)
        print(name, [Path(p).name for p in result['images']])


if __name__ == '__main__':
    main()
