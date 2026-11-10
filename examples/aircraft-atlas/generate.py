"""Prepare, install and refresh aircraft construction lessons; inspection must precede recording reviews.

Studies are prepared into a separate output directory, reviewed with ``./ldraw-agent manual review``
after opening every image, then installed into ``examples/<package>/`` with their README registration.
"""
from pathlib import Path
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.atlas import Atlas, generate, install, probe, refresh, refresh_notes, scaffold  # noqa: E402
from ldraw_tools.common import get_parts  # noqa: E402

ATLAS = Atlas(HERE, family='aircraft')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=ROOT/'output/aircraft-atlas', help='preparation directory (never the atlas itself)')
    parser.add_argument('--name', action='append', help='selection key; repeatable')
    parser.add_argument('--no-render', action='store_true')
    parser.add_argument('--candidates', action='store_true', help='include unpromoted seeds when preparing')
    parser.add_argument('--probe', action='store_true', help='source checks only, no LeoCAD')
    parser.add_argument('--install', action='store_true', help='copy reviewed --name folders into examples/<package>/ and register them')
    parser.add_argument('--force', action='store_true', help='replace an existing installed package')
    parser.add_argument('--refresh-catalog', action='store_true', help='rewrite catalog.json/index.html from installed README registrations')
    parser.add_argument('--refresh-notes', action='store_true', help='rewrite notes, viewer and guide of prepared --name folders from selections.json without re-rendering')
    parser.add_argument('--scaffold', type=Path, help='JSON list of seed specs to append to selections.json')
    args = parser.parse_args()
    if args.scaffold:
        for spec in json.loads(args.scaffold.read_text()):
            seed = scaffold(ATLAS, **spec)
            print(f'{seed["key"]}: parent {seed["parent"]!r}; DB says: {seed["discovery"]["description"]}')
    elif args.probe:
        chosen = [s for s in ATLAS.seeds(promoted=False) if not args.name or s['key'] in args.name]
        probe(ATLAS, args.outdir, chosen, get_parts())
    elif args.install:
        for key in args.name or []:
            print(install(ATLAS, args.outdir, key, force=args.force))
        rows = refresh(ATLAS)
        print(f'{len(rows)} registered aircraft entries')
    elif args.refresh_notes:
        for key in args.name or [s['key'] for s in ATLAS.seeds(promoted=False)]:
            print(refresh_notes(ATLAS, args.outdir, key))
    elif args.refresh_catalog:
        rows = refresh(ATLAS)
        print(f'{len(rows)} registered aircraft entries')
    else:
        generate(ATLAS, args.outdir, names=args.name, renders=not args.no_render, promoted=not args.candidates)
