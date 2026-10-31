"""Promote reviewed source submodels into the submodel atlas; inspection must precede recording reviews."""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import html
import json
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.common import atomic_write, dumps, get_parts, models_path
from ldraw_tools.discovery import confined, source_id
from ldraw_tools.manuals import current_manual, current_review, prepare_manual, regenerate_placement, sha, write_manual_viewer

SELECTIONS = HERE/'selections.json'
SOURCE_FIELD = 'SUBMODELS_DESCRIPTIONS_JEV.full_description'
NOTE_KEYS = ('lesson', 'construction', 'interfaces', 'parent_context', 'reuse_notes')
GUIDE_KEYS = ('parent_supplies', 'corrected_description', 'board_reading', 'limits')
USES = {'adapt', 'inspiration'}
GROUPS = {'examples', 'details'}
LEGEND = ('Magenta edges mark highlighted parts or the parts added in a source step. Pale grey, see-through parts '
          'are ghosted context. A neon-green rod (`#39FF14`) is a synthetic axis marker, not a part. Stud maps recolour '
          'each part by where its studs point: up lilac, +X rose, −X vermilion, +Z electric blue, −Z aqua, down lime, '
          'odd angle violet. These synthetic colours are ΔE ≥ 16 from every LDraw colour. LDraw −Y is up; LeoCAD '
          '`right` shows the model\'s right side, from −X.')
STANDARD_LIMITS = ('The source and renders teach a construction. They do not prove clutch, fit, clearance, travel or '
                   'stability. Boards are rendered from synthetic inspection copies, and poses are rigid re-placements.')


def seeds(*, promoted=True):
    rows = json.loads(SELECTIONS.read_text())['references']
    return [r for r in rows if r['status'] == 'promoted'] if promoted else rows


def board_name(key, recipe):
    stem = Path(recipe).stem
    return 'mosaic' if stem == key else stem.removeprefix(key+'-')


def preflight(seed, *, complete=True):
    """Check identity, parent and recipes before any atlas folder is touched."""
    from ldraw_xray import Style
    from ldraw_xray.mpd import Document
    from ldraw_xray.recipe import load_recipe
    key = seed['key']
    if seed['use'] not in USES or seed['catalog_group'] not in GROUPS:
        raise ValueError(key+': choose a known use and catalog group')
    if complete and (any(not seed['notes'].get(k, '').strip() for k in NOTE_KEYS)
                     or any(not seed['guide'].get(k, '').strip() for k in GUIDE_KEYS)):
        raise ValueError(key+': complete the study notes and guide fields before promotion')
    source = confined(models_path(), seed['model'])
    if sha(source) != seed['source_sha256']:
        raise ValueError(key+': source changed: '+seed['model'])
    if seed['discovery']['id'] != source_id('submodels', model=seed['model'], section=seed['section']):
        raise ValueError(key+': discovery id does not match the source identity')
    doc = Document.read(source)
    if not doc.block(seed['section']).placements() or seed['parent'] not in doc.parents_of(seed['section']):
        raise ValueError(key+': section or parent no longer matches the source')
    for path in seed['recipes']:
        recipe = load_recipe(HERE/path, Style())
        if recipe['source'] != str(source.resolve()) or recipe['section'] != seed['section']:
            raise ValueError(key+': recipe does not inspect this section: '+path)
    return source


def render_boards(seed, folder, session):
    """Render each reviewed recipe and keep only its mosaic plus portable provenance."""
    target = folder/'board'
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    boards = []
    for path in seed['recipes']:
        image = f'board/{board_name(seed["key"], path)}.png'
        with TemporaryDirectory(prefix='submodel-board-') as temp:
            manifest = session.board(HERE/path, output=Path(temp)/'board', force=True)
            shutil.copyfile(Path(manifest['output'])/manifest['mosaic']['output'], folder/image)
        source, mosaic = manifest['source'], manifest['mosaic']
        boards.append(dict(recipe=path, recipe_sha256=sha(HERE/path), image=image, image_sha256=sha(folder/image),
            title=manifest['title'], mode=manifest['mode'],
            source=dict(model=seed['model'], section=source['section'], sha256=source['source_sha256'],
                        steps=source['steps'], parents=source['parents']),
            panels=[dict(panel=i, label=p['label'], view=p.get('view'), step=p.get('step'), layers=p.get('layers', []),
                         warnings=p.get('warnings', [])) for i, p in enumerate(manifest['panels'], 1)],
            legend=mosaic['legend'], note=mosaic['note'], duplicates=mosaic['duplicates'],
            limitations=mosaic['limitations'], versions=manifest['versions'],
            replay=f'./ldraw-xray board run examples/submodel-atlas/{path} --output output/boards/{Path(path).stem}'))
    atomic_write(target/'board.json', dumps(dict(version=1, synthetic_note=manifest['synthetic_note'], boards=boards))+'\n')
    return boards


def error_codes(folder):
    checks = json.loads((folder/'source-checks.json').read_text())
    found = checks['diagnostics']+checks['geometry']['diagnostics']
    return Counter(d['code'] for d in found if d['severity'] == 'error')


def matrix_text(matrix):
    return ' / '.join(' '.join(f'{v:g}' for v in row) for row in matrix)


def write_guide(seed, folder, manual):
    key, notes, guide, discovery = seed['key'], seed['notes'], seed['guide'], seed['discovery']
    codes = error_codes(folder)
    steps = sum(len(s['steps']) for s in manual['sections'])
    boards = json.loads((folder/'board/board.json').read_text())['boards'] if (folder/'board/board.json').is_file() else []
    if seed['use'] == 'inspiration':
        status = ('Inspiration study: the source keeps errors ('+', '.join(f'`{c}` ×{n}' for c, n in sorted(codes.items()))
                  +'). Study the technique and rebuild it; `manual export` is blocked.')
    else:
        status = 'Reusable source construction: source checks pass' + (
            ' and the Python and LeoCAD BOMs match.' if manual['bom_matches'] else '; the rendered BOM comparison is pending.')
    links = ['[Build pages](index.html)', *(f'[{"Inspection board" if b["image"].endswith("/mosaic.png") else "Pose sweep"}]({b["image"]})' for b in boards),
             '[Source](source.mpd)', '[Editable plan](scene.plan.json)', '[Checks](source-checks.json)',
             *(['[Board provenance](board/board.json)'] if boards else [])]
    placements = '\n'.join(f'- `{p["section"]}` places it at `{" ".join(f"{v:g}" for v in p["at"])}`, matrix `{matrix_text(p["matrix"])}`.'
                           for p in manual['parents'])
    replay = ('\n\nReplay a board into `output/`:\n\n'+'\n'.join(f'    {b["replay"]}' for b in boards)) if boards else ''
    reuse = ('Rebuild the technique with the new model\'s own parts and interfaces; the source errors above stay in this copy.'
             if seed['use'] == 'inspiration' else
             f'```sh\n./ldraw-agent manual export examples/submodel-atlas/{key} --outdir output/my-{key}\n'
             f'./ldraw-agent build output/my-{key}/scene.plan.json --output output/my-{key}/{key}.mpd\n```\n\n'
             'Export needs a current visual review. Build the copied plan, then inspect its interfaces in the new model.')
    evidence = f'\n\n{guide["evidence"]}' if guide.get('evidence') else ''
    atomic_write(folder/'GUIDE.md', f'''# {seed['title']}

{notes['lesson']}

{status}

{seed['category']} · {manual['physical_placements']} parts · {steps} source steps in {len(manual['sections'])} section{'s' if len(manual['sections']) != 1 else ''}

{' · '.join(links)}{chr(10)*2+'![Inspection board](board/mosaic.png)' if boards else ''}

## Read the construction

{notes['construction']}

{notes['interfaces']}

## What the parent supplies

{placements}

{notes['parent_context']}

{guide['parent_supplies']}

## Description check

- **Database ({discovery['accuracy']}):** “{discovery['description']}”
- **What it is:** {guide['corrected_description']}

## Read the board

{guide['board_reading']}

{LEGEND}{replay}

## Reuse it

{notes['reuse_notes']}

{reuse}

The placement plan preserves source axes. `source_origin` is a positioning frame, not a physical connector.

## Limits

{guide['limits']}

{STANDARD_LIMITS}

## Source and evidence

Source: `{seed['model']}` / `{seed['section']}`, SHA-256 `{seed['source_sha256']}`. Parent: `{seed['parent']}`. Look it up with `./ldraw-agent discover show {discovery['id']}`.

Original authors and licences stay in [source.mpd](source.mpd); [extraction.json](extraction.json) records renamed sections and {len(json.loads((folder/'extraction.json').read_text())['changes'])} bounded preparation changes. {'Python and LeoCAD BOMs match.' if manual['bom_matches'] else 'The rendered BOM comparison does not match or is pending.'} The visual review is recorded separately, after opening the actual images.{evidence}
''')


def catalog_row(seed, folder):
    manual = json.loads((folder/'manual.json').read_text())
    key = seed['key']
    row = dict(key=key, title=seed['title'], category=seed['category'], tags=seed['tags'], lesson=seed['notes']['lesson'],
        description=seed['guide']['corrected_description'], use=seed['use'], group=seed['catalog_group'], parent=seed['parent'],
        source_model=seed['model'], source_section=seed['section'], discovery_id=seed['discovery']['id'],
        model=f'{key}/source.mpd', plan=f'{key}/scene.plan.json', guide=f'{key}/GUIDE.md', manual=f'{key}/index.html',
        study_notes=f'{key}/study-notes.json', physical_placements=manual['physical_placements'],
        steps=sum(len(s['steps']) for s in manual['sections']), source_checks_passed=manual['source_checks_passed'],
        bom_matches=manual['bom_matches'], visual_review_status='pending')
    if (folder/'board/mosaic.png').is_file():
        row['board'] = f'{key}/board/mosaic.png'
    if manual['rendered']:
        row['preview'] = f'{key}/renders/home.png'
    if (folder/'generate.py').is_file():
        row['generator'] = f'{key}/generate.py'
    if current_review(folder) is not None:
        row.update(visual_review_status='visually_reviewed', visual_review=f'{key}/visual-review.json')
    return row


def write_catalog(outdir):
    outdir = Path(outdir)
    rows = []
    for seed in seeds():
        folder = outdir/seed['key']
        if (folder/'manual.json').is_file():
            write_guide(seed, folder, json.loads((folder/'manual.json').read_text()))
            rows.append(catalog_row(seed, folder))
    atomic_write(outdir/'catalog.json', dumps(dict(version=1, scope='submodel-construction',
        examples=[r for r in rows if r['group'] == 'examples'], details=[r for r in rows if r['group'] == 'details']))+'\n')
    escape, cards = html.escape, []
    for row in rows:
        image = row.get('board') or row.get('preview')
        picture = f'<img src="{escape(image)}" alt="{escape(row["title"])}" loading="lazy">' if image else ''
        cards.append(f'<article><p class="kind">{escape(row["category"])} · {escape(row["use"])} · {escape(row["visual_review_status"])}</p>'
                     f'<a href="{escape(row["manual"])}">{picture}<h2>{escape(row["title"])}</h2></a><p>{escape(row["lesson"])}</p>'
                     f'<p>{row["physical_placements"]} parts · {row["steps"]} steps · <a href="{escape(row["guide"])}">Guide</a></p></article>')
    atomic_write(outdir/'index.html', '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Submodel atlas</title>
<style>body{font:16px/1.5 system-ui;max-width:1200px;margin:36px auto;padding:0 24px;color:#263540;background:#f6f8fa}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:24px}article{padding:20px;background:white;border:1px solid #dce2e7;border-radius:8px}img{width:100%;border-radius:5px}a{color:#165e9e}h2{font-size:20px}.kind{font-size:13px;text-transform:uppercase;color:#59646e}</style>
<h1>Submodel atlas</h1><p>Reviewed source submodels: how each is built, what its parent supplies and how to read its inspection board.
Inspiration entries keep source errors; rebuild their technique instead of exporting them.</p>
<p><a href="README.md">Atlas guide</a> · <a href="selections.json">Selections</a></p>
<main>''' + ''.join(cards) + '</main></html>\n')
    return rows


ENTRY_GENERATOR = '''"""Rebuild the placement from the bundled source and plan."""
from pathlib import Path
import sys
if __name__ == '__main__':
    folder=Path(__file__).resolve().parent
    for parent in folder.parents:
        if (parent/'ldraw_tools').is_dir():
            sys.path.insert(0,str(parent));break
    from ldraw_tools.manuals import regenerate_placement
    print(regenerate_placement(folder))
'''


def probe(outdir, selected, parts):
    """Run source checks without LeoCAD so each entry's use can be decided before rendering."""
    results = []
    for seed in selected:
        source = preflight(seed, complete=False)
        folder = Path(outdir)/seed['key']
        report = prepare_manual(source, seed['section'], folder, parts, kind='construction', title=seed['title'],
            notes=seed.get('notes'), views=seed['views'], renders=False, normalize_rotations=True, repair_bfc=True,
            force=True, max_instances=3000)
        changes = json.loads((folder/'extraction.json').read_text())['changes']
        results.append(dict(key=seed['key'], use=seed['use'], source_checks_passed=report['source_checks_passed'],
            errors=dict(error_codes(folder)), changes=dict(Counter(c['kind'] for c in changes)),
            physical_placements=report['physical_placements'], sections=len(report['sections']),
            steps=sum(len(s['steps']) for s in report['sections'])))
        print(f'{seed["key"]}: checks {report["source_checks_passed"]} {dict(error_codes(folder))}', flush=True)
    atomic_write(Path(outdir)/'probe.json', dumps(results)+'\n')
    return results


def generate(outdir, *, names=None, renders=True):
    outdir = Path(outdir)
    selected = seeds()
    if names and set(names)-{s['key'] for s in selected}:
        raise ValueError('Unknown or unpromoted submodel selection')
    selected = [s for s in selected if not names or s['key'] in names]
    sources = {s['key']: preflight(s) for s in selected}
    parts = get_parts()
    session = None
    if renders:
        from ldraw_xray.config import XrayConfig
        from ldraw_xray.render import Session
        session = Session(XrayConfig.resolve(shadows=[ROOT/'data/offLibShadow']))
    for seed in selected:
        key, folder = seed['key'], outdir/seed['key']
        report = prepare_manual(sources[key], seed['section'], folder, parts, kind='construction', title=seed['title'],
            notes=seed['notes'], views=seed['views'], renders=renders, normalize_rotations=True, repair_bfc=True,
            force=True, max_instances=3000)
        (folder/'generate.py').unlink(missing_ok=True)
        if renders:
            # Boards are final images: review must list them and export copies them.
            boards = render_boards(seed, folder, session)
            report['final_images'] += [b['image'] for b in boards]
            for name in [*(b['image'] for b in boards), 'board/board.json']:
                report['artifact_hashes'][name] = sha(folder/name)
        else:
            shutil.rmtree(folder/'board', ignore_errors=True)
        atomic_write(folder/'manual.json', dumps(report)+'\n')
        write_manual_viewer(folder, report, json.loads((folder/'study-notes.json').read_text()))
        current_manual(folder)
        if seed['use'] != 'inspiration' and (not report['source_checks_passed'] or (renders and report['bom_matches'] is not True)):
            raise ValueError(key+': review its source checks and BOM before admitting it as reusable')
        if seed['use'] == 'inspiration' and report['source_checks_passed'] and report['bom_matches'] is not False:
            print(f'{key}: checks pass; consider use "adapt"', flush=True)
        if report['source_checks_passed']:
            regenerate_placement(folder)
            atomic_write(folder/'generate.py', ENTRY_GENERATOR)
        print(f'{key}: {report["physical_placements"]} parts, source checks {report["source_checks_passed"]}, BOM {report["bom_matches"]}', flush=True)
        write_catalog(outdir)
    return write_catalog(outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path)
    parser.add_argument('--name', action='append')
    parser.add_argument('--no-render', action='store_true')
    parser.add_argument('--probe', action='store_true', help='source checks only, into output/submodel-probe')
    parser.add_argument('--refresh-catalog', action='store_true', help='rewrite guides and catalog from prepared folders')
    args = parser.parse_args()
    if args.probe:
        chosen = [s for s in seeds() if not args.name or s['key'] in args.name]
        probe(args.outdir or ROOT/'output/submodel-probe', chosen, get_parts())
    elif args.refresh_catalog:
        rows = write_catalog(args.outdir or HERE)
        print(f'{len(rows)} entries; {sum(r["visual_review_status"] == "visually_reviewed" for r in rows)} reviewed')
    else:
        generate(args.outdir or HERE, names=args.name, renders=not args.no_render)
