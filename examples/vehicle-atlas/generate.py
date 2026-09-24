"""Rebuild System vehicle families and dedicated fitting examples with optional renders."""
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
from ldraw_tools.vehicle_details import DETAILS, detail_plan
from ldraw import inspect_model


def artifacts(outdir, relative, name, plan, parts, *, renders=False, profile=None):
    folder = outdir/relative
    text, model, diagnostics = build_plan(plan, parts)
    geometry = analyze_geometry(model, parts, detail='summary')
    diagnostics += geometry['diagnostics']
    vehicle = review_vehicle(model, parts, profile=profile) if profile else None
    if any(d['severity']=='error' for d in diagnostics) or (vehicle and not vehicle['checks_passed']):
        raise ValueError(dumps(dict(assembly=diagnostics, vehicle=vehicle and vehicle['diagnostics'])))
    source = folder/(name+'.mpd')
    sha = hashlib.sha256(text.encode()).hexdigest()
    atomic_write(source, text)
    atomic_write(folder/'scene.plan.json', dumps(plan)+'\n')
    validation = dict(source_sha256=sha, checks_passed=True, physical_validity='not_proven',
                      diagnostics=diagnostics, geometry=geometry)
    atomic_write(folder/'validation.json', dumps(validation)+'\n')
    if vehicle:
        atomic_write(folder/'vehicle-check.json', dumps(dict(source_sha256=sha, **vehicle))+'\n')
    atomic_write(folder/'bom.json', dumps(dict(source_sha256=sha, bom=model.bill_of_materials(parts=parts)))+'\n')
    row = dict(model=f'{relative}/{name}.mpd', plan=f'{relative}/scene.plan.json', guide='README.md',
               source_sha256=sha, physical_placements=geometry['occurrence_count'], checks_passed=True)
    if profile:
        row.update(profile=profile, vehicle_checks_passed=True)
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
        row.update(preview=f'{relative}/home.png', bom_matches=True)
    else:
        # Evidence is reusable only for this exact source revision.
        manifest, comparison = folder/'render-manifest.json', folder/'bom-comparison.json'
        if manifest.is_file() and comparison.is_file():
            old_render = json.loads(manifest.read_text())
            old_bom = json.loads(comparison.read_text())
            if (old_render.get('source_sha256') == old_bom.get('source_sha256') == sha
                    and old_bom.get('matches')
                    and all((folder/p).is_file() for p in old_render.get('images', []))
                    and (folder/'home.png').is_file()):
                row.update(preview=f'{relative}/home.png', bom_matches=True)
    print(f'{relative}: {geometry["occurrence_count"]} placements; assembly'+(f' and {profile}' if profile else '')+' checks passed', flush=True)
    return row


def generate(outdir, *, renders=False, names=None, details=None):
    outdir = Path(outdir)
    parts = get_parts()
    all_examples = names is None and details is None
    rows, detail_rows = [], []
    for name in DESIGNS if all_examples else names or []:
        design = DESIGNS[name]
        row = artifacts(outdir, name, name, vehicle_plan(name), parts,
                        renders=renders, profile=design.get('profile','road'))
        row.update(key=name, title=design['title'], category='System '+design.get('profile','road')+' vehicle', lesson=design['lesson'])
        atomic_write(outdir/name/'design-brief.json', dumps(design_brief(name))+'\n')
        rows.append(row)
    for name in DETAILS if all_examples else details or []:
        recipe = DETAILS[name]
        row = artifacts(outdir, 'details/'+name, name, detail_plan(name), parts, renders=renders)
        row.update(key=name, title=name.replace('-',' ').title(), category='Vehicle fitting',
                   description=recipe['description'], placement_notes=recipe['interface'])
        atomic_write(outdir/'details'/name/'recipe.json', dumps(recipe)+'\n')
        detail_rows.append(row)
    atomic_write(outdir/'catalog.json', dumps(dict(examples=rows, details=detail_rows))+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path('output/vehicle-atlas'))
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--name', choices=list(DESIGNS), action='append')
    parser.add_argument('--detail', choices=list(DETAILS), action='append')
    args = parser.parse_args()
    generate(args.outdir, renders=args.render, names=args.name, details=args.detail)
