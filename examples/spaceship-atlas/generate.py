"""Rebuild pinned spaceship studies; inspection must precede recording reviews."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import html
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ldraw import Piece, Vector
from ldraw_tools.builder import serialize_mpd
from ldraw_tools.common import atomic_write, dumps, get_parts, jsonable, models_path
from ldraw_tools.discovery import confined
from ldraw_tools.document import parse_source, resolve_section
from ldraw_tools.manuals import prepare_manual, regenerate_placement, sha


def adapted_source(seed, source, temp):
    repairs = seed.get('position_repairs', [])
    if not repairs:
        return source
    model = parse_source(source)
    for repair in repairs:
        section = resolve_section(model, repair['section'])
        found = [i for i,p in enumerate(section.objects) if isinstance(p, Piece)
                 and p.reference == repair['part'] and jsonable(p.position) == repair['before']]
        if len(found) != 1:
            raise ValueError('A recorded position repair no longer matches exactly one source placement')
        i = found[0]
        section.objects[i] = replace(section.objects[i], position=Vector(*repair['after']))
    target = Path(temp)/source.name
    atomic_write(target, serialize_mpd(model))
    return target


def generate(outdir, *, names=None, renders=True):
    outdir = Path(outdir)
    seeds = json.loads(Path(__file__).with_name('selections.json').read_text())['references']
    if names and set(names)-{s['key'] for s in seeds}:
        raise ValueError('Unknown spaceship selection')
    parts = get_parts()
    catalog_path = outdir/'catalog.json'
    old = json.loads(catalog_path.read_text()) if catalog_path.exists() else {'examples':[], 'details':[]}
    rows = {r['key']:r for r in old['examples']+old['details']}
    for seed in seeds:
        key = seed['key']
        if names and key not in names:
            continue
        source = confined(models_path(), seed['model'])
        if sha(source) != seed['source_sha256']:
            raise ValueError('Source changed: '+seed['model'])
        folder = outdir/key
        with TemporaryDirectory(prefix='space-source-') as temp:
            prepared = adapted_source(seed, source, temp)
            report = prepare_manual(prepared, seed['section'], folder, parts, kind='construction',
                title=seed['title'], notes=seed['notes'], views=seed['views'], overview=seed['overview'],
                renders=renders, normalize_rotations=True, repair_bfc=True, force=True, max_instances=3000)
            # Keep the original identity even when a precisely recorded copy was adapted.
            origin = dict(model=seed['model'], section=seed['section'], sha256=seed['source_sha256'],
                prepared_sha256=sha(prepared), position_repairs=seed.get('position_repairs', []),
                reason=seed.get('repair_reason', 'No additional source position repairs.'))
        atomic_write(folder/'source-origin.json', dumps(origin)+'\n')
        report['artifact_hashes']['source-origin.json'] = sha(folder/'source-origin.json')
        atomic_write(folder/'manual.json', dumps(report)+'\n')
        from ldraw_tools.manuals import write_manual_viewer
        write_manual_viewer(folder, report, json.loads((folder/'study-notes.json').read_text()))
        if seed['use'] != 'inspiration' and (not report['source_checks_passed'] or report['bom_matches'] is False):
            raise ValueError(key+': review its source checks before admitting it as reusable')
        if report['source_checks_passed']:
            regenerate_placement(folder)
            atomic_write(folder/'generate.py', '''"""Rebuild the placement from the bundled source and plan."""
from pathlib import Path
import sys
if __name__ == '__main__':
    folder=Path(__file__).resolve().parent
    for parent in folder.parents:
        if (parent/'ldraw_tools').is_dir():
            sys.path.insert(0,str(parent));break
    from ldraw_tools.manuals import regenerate_placement
    print(regenerate_placement(folder))
''')
        notes=seed['notes']
        status='Inspiration study: source errors remain; inspect source-checks.json. Export as a checked construction is blocked.' if seed['use']=='inspiration' else 'Reusable source construction after visual review; inspect new interfaces after adaptation.'
        repair_text=seed.get('repair_reason','No additional position repairs were made.')
        atomic_write(folder/'GUIDE.md',f'''# {seed['title']}

{notes['lesson']}

{status}

[Study images](index.html) · [Source](source.mpd) · [Editable plan](scene.plan.json) · [Checks](source-checks.json) · [Original source and adaptations](source-origin.json)

## Read the construction

{notes['construction']}

{notes['interfaces']}

{notes['parent_context']}

{notes['reuse_notes']}

## Source and evidence

Source: `{seed['model']}` / `{seed['section']}`. Original SHA-256: `{seed['source_sha256']}`. Original authors and licences remain in the source; [extraction.json](extraction.json) records renaming and bounded preparation changes. {repair_text}

{report['physical_placements']} physical placements. {'The images show completed-model views; source step data identifies smaller sections to study.' if seed['overview'] else 'The manual preserves source STEP groups, with highlighted additions and per-step parts.'} {'Python and LeoCAD BOMs match.' if report['bom_matches'] else 'Rendered BOM comparison is pending.'} Visual review is recorded separately after opening the actual images.

## Adapt it

{'Study its silhouette and techniques, then rebuild or repair selected sections before use.' if seed['use']=='inspiration' else f'Run `./ldraw-agent spaceship export {key} --outdir output/my-{key}`. Build the copied `scene.plan.json` with the ordinary builder and inspect its interfaces in the new model.'}

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector. Measure the actual front direction, envelope and mounting parts before changing the pose. Analytical mechanism verification remains deferred; no flight performance or physical certification is claimed.
''')
        rows[key]=dict(key=key,title=seed['title'],category=seed['category'],lesson=notes['lesson'],use=seed['use'],
            group=seed['catalog_group'],model=f'{key}/source.mpd',plan=f'{key}/scene.plan.json',guide=f'{key}/GUIDE.md',
            manual=f'{key}/index.html',study_notes=f'{key}/study-notes.json',physical_placements=report['physical_placements'],
            source_checks_passed=report['source_checks_passed'],bom_matches=report['bom_matches'],visual_review_status='pending',
            **({'preview':f'{key}/renders/home.png'} if renders else {}),
            **({'generator':f'{key}/generate.py'} if report['source_checks_passed'] else {}))
        catalog=dict(version=1,examples=[r for r in rows.values() if r['group']=='examples'],details=[r for r in rows.values() if r['group']=='details'])
        atomic_write(catalog_path,dumps(catalog)+'\n')
        print(f'{key}: {report["physical_placements"]} parts, source checks {report["source_checks_passed"]}, BOM {report["bom_matches"]}',flush=True)
    cards=[]
    for row in rows.values():
        preview=f'<img src="{html.escape(row["preview"])}" alt="">' if row.get('preview') else ''
        cards.append(f'<article><a href="{row["manual"]}">{preview}<h2>{html.escape(row["title"])}</h2></a><p>{html.escape(row["use"])} · {row["physical_placements"]} parts</p><p>{html.escape(row["lesson"])}</p><a href="{row["guide"]}">Construction guide</a></article>')
    atomic_write(outdir/'index.html','''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spaceship atlas</title><style>body{font:16px/1.5 system-ui;max-width:1200px;margin:32px auto;padding:0 20px;background:#f6f8fa;color:#20303a}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{padding:20px;border:1px solid #ccd5dd;background:white;border-radius:8px}img{width:100%}a{color:#165e9e}h2{font-size:20px}</style><h1>Spaceships: silhouettes, structures and details</h1><p>Study whole ships for proportions. Open smaller constructions to learn their parts and build order. Inspiration entries retain unresolved source errors and cannot be exported as checked assemblies.</p><main>'''+''.join(cards)+'</main></html>')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--name',action='append')
    parser.add_argument('--no-render',action='store_true')
    args=parser.parse_args()
    generate(args.outdir,names=args.name,renders=not args.no_render)
