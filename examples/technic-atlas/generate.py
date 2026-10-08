"""Rebuild the stage-1 structural atlas and optionally its seven-view previews."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ldraw_tools.builder import build_plan
from ldraw_tools.common import atomic_write, dumps, get_parts, library_path, jsonable
from ldraw_tools.connectivity import inspect_connections
from ldraw_tools.external import render, compare_bom
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.technic_recipes import RECIPES, structure_plan
from ldraw_tools.technic_review import review_structure
from technic_catalog import write_catalog

VIEWS = ['home', 'front', 'back', 'right', 'left', 'top', 'bottom']
ORDERS = {
    'reinforced-frame': 'Insert the pins into the moulded frame first. Bring each crossmember onto its two projecting pins. Keep both holes aligned and seat the member against the frame; never bend a crossmember to close a mismatch.',
    'box-chassis': 'Prepare the left side frame with its inward-facing pins. Add the upper and lower horizontal frames from the side. Insert the opposite pins, then bring the right side frame onto all four ends together. Insert the upper rail pins before lowering the two rails into place.',
    'frame-tower': 'Build each box cell from one side frame, the horizontal frames and the opposite side frame. Use the specified long pins where a bridge beam adds a third layer; their unused ends must face that beam. Bring neighboring cells to their final spacing, then fit the external bridge beams onto their projecting pins. The STEP constraints describe subassembly order; keep the cells supported during assembly.',
    'service-platform': 'Build the box chassis and fit its two rails. Insert the eight half pins from above, leaving their studs exposed. Press each deck plate onto its four mounts. Add the front deck tiles, equipment housing walls, roof, vents and lamps. The System grid is offset by 10 LDU in X/Z relative to the frame grid; preserve the supplied coordinates.',
}


def reviewed_images(folder, sha, manifest):
    """Retain a manual review only for the exact model and seven image files."""
    path = folder/'visual-review.json'
    if not path.exists() or manifest.get('source_sha256') != sha:
        return False
    review = json.loads(path.read_text())
    expected = {view+'.png' for view in VIEWS}
    hashes = review.get('image_sha256', {})
    return (review.get('status') == 'reviewed' and review.get('source_sha256') == sha
            and set(manifest.get('images', [])) == expected and set(hashes) == expected
            and all((folder/name).is_file()
                    and hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest
                    for name, digest in hashes.items()))


def command_path(path):
    path = path.resolve()
    return shlex.quote((path.relative_to(ROOT) if path.is_relative_to(ROOT) else path).as_posix())


def generate(outdir, *, names=None, renders=False, levels=2, colour=71, accent=14):
    outdir = Path(outdir)
    parts = get_parts()
    catalog_path = outdir/'catalog.json'
    old = json.loads(catalog_path.read_text()) if catalog_path.exists() else {'examples': [], 'details': []}
    rows = {row['key']: row for row in old['examples']}
    for name in names or RECIPES:
        plan, contract = structure_plan(name, levels=levels, colour=colour, accent=accent)
        source, model, diagnostics = build_plan(plan, parts)
        geometry = analyze_geometry(model, parts, detail='summary')
        contract['model_sha256'] = hashlib.sha256(model.to_ldraw().encode()).hexdigest()
        structure = review_structure(model, parts, contract=contract)
        diagnostics += geometry['diagnostics']
        if any(d['severity']=='error' for d in diagnostics) or not structure['checks_passed']:
            raise ValueError(dumps(dict(name=name, diagnostics=diagnostics, structure=structure)))
        folder = outdir/name
        path = folder/(name+'.mpd')
        sha = hashlib.sha256(source.encode()).hexdigest()
        atomic_write(path, source)
        for filename, data in [('scene.plan.json', plan), ('structure.json', contract),
                               ('geometry.json', geometry), ('structure-review.json', structure),
                               ('bom.json', [jsonable(r) for r in model.bill_of_materials(parts=parts)])]:
            atomic_write(folder/filename, dumps(data)+'\n')
        atomic_write(folder/'generate.py',
            '"""Rebuild this structural example and its evidence from the shared recipe."""\n'
            'from pathlib import Path\nimport runpy\n'
            'if __name__ == "__main__":\n'
            '    api = runpy.run_path(str(Path(__file__).resolve().parents[1]/"generate.py"))\n'
            f'    api["generate"](Path(__file__).resolve().parents[1], names=[{name!r}], '
            f'levels={levels}, colour={colour}, accent={accent})\n')
        atomic_write(folder/'GUIDE.md', f'''# {RECIPES[name]['title']}

{RECIPES[name]['lesson']}

This is a static structural example. Parts are unscaled. Pin grips and the mounting pairs in `structure.json` are checked against the reviewed registry. `scene.plan.json` and `generate.py` reproduce the model. The contract uses physical occurrence indices in the generated source and binds to its model revision.

## Assembly order and access

{ORDERS[name]}

Keep pins in their retaining seats and support loose subassemblies while closing the frame. STEP checks verify connector-before-closure order. Insertion paths, hand access, manufacturing fit and loads still require a physical build or further manual inspection.

## Mounting and appearance

Use the measured hole ports, not the outside bounding box, to attach another module. Preserve both connections of each crossmember. The palette separates the grey structure, yellow reinforcement and black pins; white rails identify the body support plane where present. Blue pins identify the selected long-pin variant by convention only—the registry determines its type.

Inspect all seven views, especially the bottom and the hidden face of each mounting pair. Bracing checks use a conservative multiple-pin rule; strength, overturning stability and mechanism behavior are not certified. The tower may need a wider base for a real load.

## Current evidence

- Source SHA-256: `{sha}`
- Physical placements: {geometry['occurrence_count']}
- Reviewed mechanical contacts: {structure['joint_count']}
- Structural member groups after the multiple-pin rule: {len(structure['restrained_groups'])}
- Required mounting pairs: {len(contract['required_joints'])}
- Physical validity: **not proven**.

Run `./ldraw-agent technic check {command_path(path)} --contract {command_path(folder/'structure.json')}` from the repository root. Also run normal `validate --geometry`; a seating check cannot waive unrelated solid intersections.
''')
        row = dict(key=name, title=RECIPES[name]['title'], category='Technic structure',
                   lesson=RECIPES[name]['lesson'], physical_placements=geometry['occurrence_count'],
                   model=f'{name}/{name}.mpd', plan=f'{name}/scene.plan.json',
                   generator=f'{name}/generate.py', guide=f'{name}/GUIDE.md',
                   structure_contract=f'{name}/structure.json', source_sha256=sha,
                   checks_passed=True, physical_validity='not_proven')
        if renders:
            inspection = inspect_connections(model, parts)
            result = render(path, library_path(), folder, views=VIEWS, bounds=inspection.bounds)
            comparison = compare_bom(model, parts, folder/'leocad-bom.csv')
            if not comparison['matches']:
                raise ValueError(dumps(comparison))
            result.update(source_sha256=sha, images=[Path(p).name for p in result['images']],
                          bom='leocad-bom.csv', visual_review='pending')
            atomic_write(folder/'render-manifest.json', dumps(result)+'\n')
            atomic_write(folder/'bom-comparison.json', dumps(dict(source_sha256=sha, **comparison))+'\n')
        manifest = folder/'render-manifest.json'
        if manifest.exists():
            data = json.loads(manifest.read_text())
            if data.get('source_sha256') == sha and all((folder/view).exists() for view in data['images']):
                row['preview'] = f'{name}/home.png'
            reviewed = reviewed_images(folder, sha, data)
            data['visual_review'] = 'reviewed' if reviewed else 'pending'
            atomic_write(manifest, dumps(data)+'\n')
            if reviewed:
                row['visual_review'] = f'{name}/visual-review.json'
        rows[name] = row
        print(f'{name}: {geometry["occurrence_count"]} parts, {structure["joint_count"]} reviewed contacts; checks passed', flush=True)
    write_catalog(outdir, rows.values())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--name', action='append', choices=list(RECIPES))
    parser.add_argument('--renders', action='store_true')
    parser.add_argument('--levels', type=int, default=2)
    parser.add_argument('--colour', type=int, default=71)
    parser.add_argument('--accent', type=int, default=14)
    args = parser.parse_args()
    generate(args.outdir, names=args.name, renders=args.renders, levels=args.levels, colour=args.colour, accent=args.accent)
