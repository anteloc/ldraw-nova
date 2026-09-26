"""Rebuild attributed mechanism studies from the pinned source selections.

Rendering uses LeoCAD's step export, including highlighted additions. Reopen the
new pages before recording a review; this generator never supplies one.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ldraw_tools.common import atomic_write, dumps, get_parts, models_path
from ldraw_tools.discovery import confined
from ldraw_tools.manuals import prepare_manual, regenerate_placement


def generate(outdir, *, names=None, renders=True):
    outdir = Path(outdir)
    seeds = json.loads(Path(__file__).with_name('selections.json').read_text())['references']
    parts = get_parts()
    catalog_path = outdir/'catalog.json'
    old = json.loads(catalog_path.read_text()) if catalog_path.is_file() else {'examples':[]}
    rows = {r['key']:r for r in old['examples']}
    if names and set(names)-{s['key'] for s in seeds}:
        raise ValueError('Unknown mechanism selection')
    for seed in seeds:
        name = seed['key']
        if names and name not in names:
            continue
        source = confined(models_path(), seed['model'])
        if hashlib.sha256(source.read_bytes()).hexdigest() != seed['source_sha256']:
            raise ValueError(f'{source.name} changed; inspect and update its selection before rebuilding')
        folder = outdir/name
        report = prepare_manual(source, seed['section'], folder, parts, title=seed['title'],
            views=seed['views'], notes=seed['operation'], renders=renders,
            normalize_rotations=True, repair_bfc=True, force=True)
        if not report['source_checks_passed'] or report['bom_matches'] is False:
            raise ValueError(f'{name}: inspect source-checks.json and BOM evidence')
        atomic_write(folder/'generate.py', '''"""Rebuild this editable placement using its bundled source; pages need separate review."""
from pathlib import Path
import sys

if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    for parent in folder.parents:
        if (parent/'ldraw_tools').is_dir():
            sys.path.insert(0, str(parent))
            break
    from ldraw_tools.manuals import regenerate_placement
    print(regenerate_placement(folder))
''')
        regenerate_placement(folder)
        operation = seed['operation']
        text = f'''# {seed['title']}

{seed['lesson']}

[Build manual](index.html) · [Editable placement plan](scene.plan.json) · [Source assembly](source.mpd) · [Operation notes](operation.json)

## Read and adapt the construction

{operation['function']}

- Fixed structure: {operation['fixed']}
- Moving elements: {operation['moving']}
- Input: {operation['input']}
- Output: {operation['output']}

{operation['reuse_notes']}

## Parent context and source

{operation['parent_context']}

Source: `{seed['model']}` / `{seed['section']}`, SHA-256 `{seed['source_sha256']}`. Jev found this reference in `SUBMODELS_DESCRIPTIONS_JEV.full_description` (rank {seed['discovery']['rank']}, relevance score {seed['discovery']['score']}). The extraction retains original authorship and licensing, dependencies and recorded preparation changes in [extraction.json](extraction.json).

## Reuse in a new model

Run `./ldraw-agent mechanism export {name} --outdir output/my-{name}` from the repository root. Read the manual and parent context first. The exported `scene.plan.json` places the complete module with a proper transform; its `source_origin` is a positioning frame, not an asserted connector. Edit the plan to place the module, or its bundled `source.mpd` to adapt internal parts. Keep changes reproducible and inspect the combined model.

Build with `./ldraw-agent build output/my-{name}/scene.plan.json --contacts none --output output/my-{name}/my-{name}.mpd`. The local `generate.py` also rebuilds the placement with normal source/geometry checks and without mechanism analysis.

## Evidence

{report['physical_placements']} physical placements; {sum(len(s['steps']) for s in report['sections'])} nonempty construction steps across {len(report['sections'])} assembly section(s). Source checks pass. {'Python and LeoCAD BOMs match.' if report['bom_matches'] else 'Rendering and BOM comparison are pending.'} See [source-checks.json](source-checks.json) and [manual.json](manual.json).

The operation notes are interpretations of source and images. Analytical mechanism verification is deferred by the user's scope. The pages depict construction states; no movement simulation, load rating or physical operation is certified. Visual review is recorded separately in `visual-review.json` after the images have actually been opened.
'''
        atomic_write(folder/'GUIDE.md', text)
        row = dict(key=name,title=seed['title'],category=seed['category'],lesson=seed['lesson'],
            model=f'{name}/source.mpd',plan=f'{name}/scene.plan.json',guide=f'{name}/GUIDE.md',
            generator=f'{name}/generate.py',manual=f'{name}/index.html',operation=f'{name}/operation.json',
            physical_placements=report['physical_placements'],analytical_verification='deferred',
            visual_review_status='pending',source_sha256=seed['source_sha256'])
        if renders:
            row['preview'] = f'{name}/renders/home.png'
        rows[name] = row
        atomic_write(catalog_path,dumps(dict(version=1,scope='mechanism',examples=list(rows.values()),details=[]))+'\n')
        print(f'{name}: {report["physical_placements"]} parts; {sum(len(s["steps"]) for s in report["sections"])} steps; source checks pass; BOM {report["bom_matches"]}',flush=True)
    cards=[]
    for row in rows.values():
        preview=f'<img src="{html.escape(row["preview"])}" alt="">' if row.get('preview') else ''
        cards.append(f'<article><a href="{row["manual"]}">{preview}<h2>{html.escape(row["title"])}</h2></a><p>{html.escape(row["lesson"])}</p><a href="{row["guide"]}">Adaptation guide</a></article>')
    atomic_write(outdir/'index.html','''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mechanism studies</title><style>body{font:16px/1.5 system-ui;max-width:1200px;margin:32px auto;padding:0 24px;color:#263540;background:#f6f8fa}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:24px}article{padding:20px;background:white;border:1px solid #dce2e7;border-radius:8px}img{width:100%;border-radius:5px}a{color:#165e9e}h2{font-size:20px}</style><h1>Build with mechanisms</h1><p>Six source studies with step-by-step images, real parts and adaptation notes. Open a construction to study its internals before reusing it. Analytical mechanism verification is deferred.</p><main>'''+''.join(cards)+'</main></html>')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--name', action='append')
    parser.add_argument('--no-render', action='store_true')
    args = parser.parse_args()
    generate(args.outdir,names=args.name,renders=not args.no_render)
