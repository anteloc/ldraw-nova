"""Rebuild the System vehicle teaching set and optional LeoCAD review artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ldraw_tools.builder import build_plan
from ldraw_tools.common import atomic_write, dumps, get_parts, library_path
from ldraw_tools.external import render, compare_bom
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.vehicle_review import review_vehicle
from ldraw_tools.vehicles import DESIGNS, design_brief, vehicle_plan
from ldraw import inspect_model


def generate(outdir, *, renders=False, names=None):
    outdir = Path(outdir)
    parts = get_parts()
    rows = []
    for name in names or DESIGNS:
        folder = outdir/name
        plan = vehicle_plan(name)
        text, model, diagnostics = build_plan(plan, parts)
        geometry = analyze_geometry(model, parts, detail='summary')
        diagnostics += geometry['diagnostics']
        vehicle = review_vehicle(model, parts)
        if any(d['severity']=='error' for d in diagnostics) or not vehicle['checks_passed']:
            raise ValueError(dumps(dict(assembly=diagnostics, vehicle=vehicle['diagnostics'])))
        source = folder/(name+'.mpd')
        sha = hashlib.sha256(text.encode()).hexdigest()
        atomic_write(source, text)
        atomic_write(folder/'scene.plan.json', dumps(plan)+'\n')
        atomic_write(folder/'design-brief.json', dumps(design_brief(name))+'\n')
        validation = dict(source_sha256=sha, checks_passed=True, physical_validity='not_proven',
                          diagnostics=diagnostics, geometry=geometry)
        atomic_write(folder/'validation.json', dumps(validation)+'\n')
        atomic_write(folder/'vehicle-check.json', dumps(dict(source_sha256=sha, **vehicle))+'\n')
        atomic_write(folder/'bom.json', dumps(dict(source_sha256=sha, bom=model.bill_of_materials(parts=parts)))+'\n')
        row = dict(key=name, title=DESIGNS[name]['title'], category='System road vehicle',
                   lesson=DESIGNS[name]['lesson'], model=f'{name}/{name}.mpd',
                   plan=f'{name}/scene.plan.json', guide='README.md',
                   source_sha256=sha, physical_placements=geometry['occurrence_count'],
                   checks_passed=True, vehicle_checks_passed=True)
        if renders:
            inspection = inspect_model(model, parts)
            rendered = render(source, library_path(), folder,
                              views=['home','front','back','right','top','bottom'], bounds=inspection.bounds)
            comparison = compare_bom(model, parts, folder/'leocad-bom.csv')
            if not comparison['matches']:
                raise ValueError(dumps(comparison))
            rendered['images'] = [Path(p).name for p in rendered['images']]
            rendered['bom'] = Path(rendered['bom']).name
            atomic_write(folder/'render-manifest.json', dumps(dict(source_sha256=sha, **rendered))+'\n')
            atomic_write(folder/'bom-comparison.json', dumps(dict(source_sha256=sha, **comparison))+'\n')
            row.update(preview=f'{name}/home.png', bom_matches=True)
        else:
            # Reuse evidence only when it belongs to this exact source revision.
            manifest = folder/'render-manifest.json'
            comparison = folder/'bom-comparison.json'
            if manifest.is_file() and comparison.is_file():
                old_render = json.loads(manifest.read_text())
                old_bom = json.loads(comparison.read_text())
                if (old_render.get('source_sha256') == old_bom.get('source_sha256') == sha
                        and old_bom.get('matches')
                        and all((folder/p).is_file() for p in old_render.get('images', []))
                        and (folder/'home.png').is_file()):
                    row.update(preview=f'{name}/home.png', bom_matches=True)
        rows.append(row)
        print(f'{name}: {geometry["occurrence_count"]} placements; assembly and road checks passed', flush=True)
    atomic_write(outdir/'catalog.json', dumps(dict(examples=rows, details=[]))+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path('output/vehicle-atlas'))
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--name', choices=list(DESIGNS), action='append')
    args = parser.parse_args()
    generate(args.outdir, renders=args.render, names=args.name)
