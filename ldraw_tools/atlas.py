"""Promote reviewed source sections into a family atlas and install them as knowledge packages.

An atlas directory (``examples/<family>-atlas``) owns ``selections.json`` (seed rows),
``recipes/`` (ldraw-xray board recipes) and a thin ``generate.py``. Generation writes build
pages, boards and a guide into a separate output directory. After the images have been opened
and ``manual review`` has recorded them, ``install`` copies the folder into
``examples/<package>/`` and writes the README registration that admits the lesson. Nothing is
installed without a current visual review, and the atlas's own compatibility catalog is a
projection of the installed README registrations.
"""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import html
import json
import shutil

from .common import ROOT, atomic_write, dumps, get_parts, models_path
from .discovery import confined, source_id
from .manuals import current_manual, current_review, prepare_manual, regenerate_placement, sha, write_manual_viewer

NOTE_KEYS = ('lesson', 'construction', 'interfaces', 'parent_context', 'reuse_notes')
GUIDE_KEYS = ('parent_supplies', 'corrected_description', 'board_reading', 'limits')
USES = {'adapt', 'inspiration'}
GROUPS = {'examples', 'details'}
SOURCE_FIELD = 'SUBMODELS_DESCRIPTIONS_JEV.full_description'
LEGEND = ('Magenta edges mark highlighted parts or the parts added in a source step. Pale grey, see-through parts '
          'are ghosted context. A neon-green rod (`#39FF14`) is a synthetic axis marker, not a part. Stud maps recolour '
          'each part by where its studs point: up lilac, +X rose, −X vermilion, +Z electric blue, −Z aqua, down lime, '
          'odd angle violet. These synthetic colours are ΔE ≥ 16 from every LDraw colour. LDraw −Y is up; LeoCAD '
          '`right` shows the model\'s right side, from −X.')
STANDARD_LIMITS = ('The source and renders teach a construction. They do not prove clutch, fit, clearance, travel or '
                   'stability. Boards are rendered from synthetic inspection copies, and poses are rigid re-placements.')
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


class Atlas:
    """One family atlas: its directory, family name and seed rows."""

    def __init__(self, directory, *, family=None, root=None):
        self.root = Path(root or ROOT).resolve()
        self.directory = Path(directory).resolve()
        self.selections = self.directory/'selections.json'
        data = json.loads(self.selections.read_text()) if self.selections.is_file() else {}
        self.family = family or data.get('family') or self.directory.name.removesuffix('-atlas')

    @property
    def relative(self):
        return self.directory.relative_to(self.root).as_posix()

    def rows(self):
        if not self.selections.is_file():
            return []
        return json.loads(self.selections.read_text())['references']

    def seeds(self, *, promoted=True):
        rows = self.rows()
        return [r for r in rows if r['status'] == 'promoted'] if promoted else rows

    def seed(self, key):
        return next(r for r in self.rows() if r['key'] == key)

    def save(self, rows):
        atomic_write(self.selections, dumps(dict(version=1, family=self.family, references=rows))+'\n')

    def package_dir(self, seed):
        return confined(self.root/'examples', seed['package'])


def description_of(source, section):
    """The annotated description line that follows ``0 FILE`` in the source."""
    from ldraw_xray.mpd import Document
    block = Document.read(source).block(section)
    first = block.lines[0] if block.lines else ''
    return first[2:].strip() if first.startswith('0 ') and not first.startswith('0 !') else ''


def scaffold(atlas, *, key, package, model, section, title, category, style='', tags=(), use='adapt',
             group='details', overview=False, views=('home',), parent=None, recipes=(), kind=None,
             techniques=(), subjects=()):
    """Append an unpromoted seed with its identity fields computed from the source."""
    from ldraw_xray.mpd import Document
    rows = atlas.rows()
    if any(r['key'] == key for r in rows) or any(r.get('package') == package for r in rows):
        raise ValueError(key+': key or package already exists')
    source = confined(models_path(), model)
    doc = Document.read(source)
    if not doc.block(section).placements():
        raise ValueError(key+': section has no placements: '+section)
    parents = sorted(doc.parents_of(section))
    if parent is None and len(parents) > 1:
        raise ValueError(key+': choose one parent from '+', '.join(parents))
    parent = parent if parent is not None else (parents[0] if parents else None)
    if parent is not None and parent not in parents:
        raise ValueError(key+': parent does not place this section: '+parent)
    seed = dict(key=key, status='candidate', package=package, model=model, section=section,
                source_sha256=sha(source), parent=parent, title=title, category=category, style=style,
                kind=kind or ('assembly' if group == 'examples' else 'detail'), tags=list(tags),
                techniques=list(techniques), subjects=list(subjects), use=use, catalog_group=group,
                overview=bool(overview), views=list(views),
                discovery=dict(id=source_id('submodels', model=model, section=section), source_field=SOURCE_FIELD,
                               description=description_of(source, section), accuracy=''),
                notes={k: '' for k in NOTE_KEYS}, guide={k: '' for k in GUIDE_KEYS}, recipes=list(recipes))
    rows.append(seed)
    atlas.save(rows)
    return seed


def board_name(key, recipe):
    stem = Path(recipe).stem
    return 'mosaic' if stem == key else stem.removeprefix(key+'-')


def preflight(atlas, seed, *, complete=True):
    """Check identity, parent and recipes before any folder is touched."""
    from ldraw_xray import Style
    from ldraw_xray.mpd import Document
    from ldraw_xray.recipe import load_recipe
    key = seed['key']
    if seed['use'] not in USES or seed['catalog_group'] not in GROUPS:
        raise ValueError(key+': choose a known use and catalog group')
    if not seed.get('package'):
        raise ValueError(key+': name the examples package that will own this lesson')
    if complete and (any(not seed['notes'].get(k, '').strip() for k in NOTE_KEYS)
                     or any(not seed['guide'].get(k, '').strip() for k in GUIDE_KEYS)):
        raise ValueError(key+': complete the study notes and guide fields before promotion')
    source = confined(models_path(), seed['model'])
    if sha(source) != seed['source_sha256']:
        raise ValueError(key+': source changed: '+seed['model'])
    if seed['discovery']['id'] != source_id('submodels', model=seed['model'], section=seed['section']):
        raise ValueError(key+': discovery id does not match the source identity')
    doc = Document.read(source)
    if not doc.block(seed['section']).placements():
        raise ValueError(key+': section no longer matches the source')
    parents = doc.parents_of(seed['section'])
    if (seed['parent'] is None and parents) or (seed['parent'] is not None and seed['parent'] not in parents):
        raise ValueError(key+': parent no longer matches the source')
    for path in seed['recipes']:
        recipe = load_recipe(atlas.directory/path, Style())
        if recipe['source'] != str(source.resolve()) or recipe['section'] != seed['section']:
            raise ValueError(key+': recipe does not inspect this section: '+path)
    return source


def render_boards(atlas, seed, folder, session):
    """Render each reviewed recipe and keep only its mosaic plus portable provenance."""
    target = folder/'board'
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    boards = []
    for path in seed['recipes']:
        image = f'board/{board_name(seed["key"], path)}.png'
        with TemporaryDirectory(prefix='atlas-board-') as temp:
            manifest = session.board(atlas.directory/path, output=Path(temp)/'board', force=True)
            shutil.copyfile(Path(manifest['output'])/manifest['mosaic']['output'], folder/image)
        source, mosaic = manifest['source'], manifest['mosaic']
        boards.append(dict(recipe=path, recipe_sha256=sha(atlas.directory/path), image=image, image_sha256=sha(folder/image),
            title=manifest['title'], mode=manifest['mode'],
            source=dict(model=seed['model'], section=source['section'], sha256=source['source_sha256'],
                        steps=source['steps'], parents=source['parents']),
            panels=[dict(panel=i, label=p['label'], view=p.get('view'), step=p.get('step'), layers=p.get('layers', []),
                         warnings=p.get('warnings', [])) for i, p in enumerate(manifest['panels'], 1)],
            legend=mosaic['legend'], note=mosaic['note'], duplicates=mosaic['duplicates'],
            limitations=mosaic['limitations'], versions=manifest['versions'],
            replay=f'./ldraw-xray board run {atlas.relative}/{path} --output output/boards/{Path(path).stem}'))
    atomic_write(target/'board.json', dumps(dict(version=1, synthetic_note=manifest['synthetic_note'], boards=boards))+'\n')
    return boards


def error_codes(folder):
    checks = json.loads((folder/'source-checks.json').read_text())
    found = checks['diagnostics']+checks['geometry']['diagnostics']
    return Counter(d['code'] for d in found if d['severity'] == 'error')


def matrix_text(matrix):
    return ' / '.join(' '.join(f'{v:g}' for v in row) for row in matrix)


def write_guide(atlas, seed, folder, manual):
    key, notes, guide, discovery = seed['key'], seed['notes'], seed['guide'], seed['discovery']
    package = f'examples/{seed["package"]}'
    codes = error_codes(folder)
    steps = sum(len(s['steps']) for s in manual['sections'])
    boards = json.loads((folder/'board/board.json').read_text())['boards'] if (folder/'board/board.json').is_file() else []
    if seed['use'] == 'inspiration':
        status = ('Inspiration study: the source keeps errors ('+', '.join(f'`{c}` ×{n}' for c, n in sorted(codes.items()))
                  +'). Study the technique and rebuild it; `manual export` is blocked.')
    else:
        status = 'Reusable source construction: source checks pass' + (
            ' and the Python and LeoCAD BOMs match.' if manual['bom_matches'] else '; the rendered BOM comparison is pending.')
    pages = 'Completed-model views' if manual.get('image_mode') == 'overview' else 'Build pages'
    links = [f'[{pages}](index.html)', *(f'[{"Inspection board" if b["image"].endswith("/mosaic.png") else "Pose sweep"}]({b["image"]})' for b in boards),
             '[Source](source.mpd)', '[Editable plan](scene.plan.json)', '[Checks](source-checks.json)',
             *(['[Board provenance](board/board.json)'] if boards else [])]
    placements = '\n'.join(f'- `{p["section"]}` places it at `{" ".join(f"{v:g}" for v in p["at"])}`, matrix `{matrix_text(p["matrix"])}`.'
                           for p in manual['parents']) or '- This section is the root of its source model; nothing places it.'
    replay = ('\n\nReplay a board into `output/`:\n\n'+'\n'.join(f'    {b["replay"]}' for b in boards)) if boards else ''
    reuse = ('Rebuild the technique with the new model\'s own parts and interfaces; the source errors above stay in this copy.'
             if seed['use'] == 'inspiration' else
             f'```sh\n./ldraw-agent manual export {package} --outdir output/my-{key}\n'
             f'./ldraw-agent build output/my-{key}/scene.plan.json --output output/my-{key}/{key}.mpd\n```\n\n'
             'Export needs a current visual review. Build the copied plan, then inspect its interfaces in the new model.')
    evidence = f'\n\n{guide["evidence"]}' if guide.get('evidence') else ''
    style = f' · {seed["style"]}' if seed.get('style') else ''
    atomic_write(folder/'GUIDE.md', f'''# {seed['title']}

{notes['lesson']}

{status}

{seed['category']}{style} · {manual['physical_placements']} parts · {steps} source steps in {len(manual['sections'])} section{'s' if len(manual['sections']) != 1 else ''}

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

Source: `{seed['model']}` / `{seed['section']}`, SHA-256 `{seed['source_sha256']}`. Parent: `{seed['parent'] or 'none (root section)'}`. Look it up with `./ldraw-agent discover show {discovery['id']}`.

Original authors and licences stay in [source.mpd](source.mpd); [extraction.json](extraction.json) records renamed sections and {len(json.loads((folder/'extraction.json').read_text())['changes'])} bounded preparation changes. {'Python and LeoCAD BOMs match.' if manual['bom_matches'] else 'The rendered BOM comparison does not match or is pending.'} The visual review is recorded separately, after opening the actual images.{evidence}
''')


def catalog_row(seed, folder):
    manual = json.loads((folder/'manual.json').read_text())
    key = seed['key']
    row = dict(key=key, title=seed['title'], category=seed['category'], style=seed.get('style', ''), tags=seed['tags'],
        lesson=seed['notes']['lesson'], description=seed['guide']['corrected_description'], use=seed['use'],
        group=seed['catalog_group'], package=seed['package'], parent=seed['parent'], source_model=seed['model'],
        source_section=seed['section'], discovery_id=seed['discovery']['id'], model=f'{key}/source.mpd',
        plan=f'{key}/scene.plan.json', guide=f'{key}/GUIDE.md', manual=f'{key}/index.html',
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


def write_catalog(atlas, outdir):
    """Working catalog of a preparation output directory; the atlas directory itself is a README projection."""
    outdir = Path(outdir).resolve()
    if outdir == atlas.directory:
        return refresh(atlas)
    rows = []
    for seed in atlas.seeds(promoted=False):
        folder = outdir/seed['key']
        if (folder/'manual.json').is_file():
            write_guide(atlas, seed, folder, json.loads((folder/'manual.json').read_text()))
            rows.append(catalog_row(seed, folder))
    atomic_write(outdir/'catalog.json', dumps(dict(version=1, scope=atlas.family+'-construction',
        examples=[r for r in rows if r['group'] == 'examples'], details=[r for r in rows if r['group'] == 'details']))+'\n')
    escape, cards = html.escape, []
    for row in rows:
        image = row.get('board') or row.get('preview')
        picture = f'<img src="{escape(image)}" alt="{escape(row["title"])}" loading="lazy">' if image else ''
        cards.append(f'<article><p class="kind">{escape(row["category"])} · {escape(row["use"])} · {escape(row["visual_review_status"])}</p>'
                     f'<a href="{escape(row["manual"])}">{picture}<h2>{escape(row["title"])}</h2></a><p>{escape(row["lesson"])}</p>'
                     f'<p>{row["physical_placements"]} parts · {row["steps"]} steps · <a href="{escape(row["guide"])}">Guide</a></p></article>')
    atomic_write(outdir/'index.html', f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(atlas.family)} atlas (preparation)</title>
<style>body{{font:16px/1.5 system-ui;max-width:1200px;margin:36px auto;padding:0 24px;color:#263540;background:#f6f8fa}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:24px}}article{{padding:20px;background:white;border:1px solid #dce2e7;border-radius:8px}}img{{width:100%;border-radius:5px}}a{{color:#165e9e}}h2{{font-size:20px}}.kind{{font-size:13px;text-transform:uppercase;color:#59646e}}</style>
<h1>{escape(atlas.family)} atlas: prepared studies</h1><p>Open each board and every page before recording a review; install only reviewed folders.</p>
<main>''' + ''.join(cards) + '</main></html>\n')
    return rows


def refresh(atlas):
    """Regenerate the atlas directory's compatibility catalog from installed README registrations."""
    from .knowledge import write_compat_catalog
    return write_compat_catalog(atlas.family, atlas.directory, root=atlas.root)


def probe(atlas, outdir, selected, parts):
    """Run source checks without LeoCAD so each entry's use can be decided before rendering."""
    results = []
    for seed in selected:
        source = preflight(atlas, seed, complete=False)
        folder = Path(outdir)/seed['key']
        report = prepare_manual(source, seed['section'], folder, parts, kind='construction', title=seed['title'],
            notes=seed.get('notes'), views=seed['views'], renders=False, normalize_rotations=True, repair_bfc=True,
            force=True, max_instances=3000, overview=seed.get('overview', False))
        changes = json.loads((folder/'extraction.json').read_text())['changes']
        results.append(dict(key=seed['key'], use=seed['use'], source_checks_passed=report['source_checks_passed'],
            errors=dict(error_codes(folder)), changes=dict(Counter(c['kind'] for c in changes)),
            physical_placements=report['physical_placements'], sections=len(report['sections']),
            steps=sum(len(s['steps']) for s in report['sections']), parents=[p['section'] for p in report['parents']]))
        print(f'{seed["key"]}: checks {report["source_checks_passed"]} {dict(error_codes(folder))} '
              f'{report["physical_placements"]} parts', flush=True)
    atomic_write(Path(outdir)/'probe.json', dumps(results)+'\n')
    return results


def generate(atlas, outdir, *, names=None, renders=True, promoted=True):
    """Prepare build pages and boards for seeds into a separate output directory."""
    outdir = Path(outdir).resolve()
    if outdir == atlas.directory or outdir.is_relative_to(atlas.root/'examples'):
        raise ValueError('Prepare studies into a separate --outdir (for example output/); install reviewed folders afterwards.')
    selected = atlas.seeds(promoted=promoted)
    if names and set(names)-{s['key'] for s in selected}:
        raise ValueError('Unknown or unpromoted selection')
    selected = [s for s in selected if not names or s['key'] in names]
    # Candidate rows render first so their notes can be written from the actual images; install requires complete notes.
    sources = {s['key']: preflight(atlas, s, complete=s['status'] == 'promoted') for s in selected}
    parts = get_parts()
    session = None
    if renders:
        from ldraw_xray.config import XrayConfig
        from ldraw_xray.render import Session
        session = Session(XrayConfig.resolve(shadows=[atlas.root/'data/offLibShadow']))
    for seed in selected:
        key, folder = seed['key'], outdir/seed['key']
        report = prepare_manual(sources[key], seed['section'], folder, parts, kind='construction', title=seed['title'],
            notes=seed['notes'], views=seed['views'], renders=renders, normalize_rotations=True, repair_bfc=True,
            force=True, max_instances=3000, overview=seed.get('overview', False))
        (folder/'generate.py').unlink(missing_ok=True)
        if renders:
            # Boards are final images: review must list them and export copies them.
            boards = render_boards(atlas, seed, folder, session) if seed['recipes'] else []
            report['final_images'] += [b['image'] for b in boards]
            for name in [*(b['image'] for b in boards), *(['board/board.json'] if boards else [])]:
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
        write_catalog(atlas, outdir)
    return write_catalog(atlas, outdir)


def registration(atlas, seed, folder):
    """The README knowledge entry for an installed package, bound to its reviewed source."""
    manual = json.loads((folder/'manual.json').read_text())
    package = f'examples/{seed["package"]}'
    notes, guide = seed['notes'], seed['guide']
    entry = dict(id=seed['package'], title=seed['title'],
                 scope='construction' if seed['use'] == 'adapt' else 'inspiration',
                 kind=seed.get('kind') or ('assembly' if seed['catalog_group'] == 'examples' else 'detail'),
                 aliases=[f'{atlas.family}:{seed["key"]}', *seed.get('aliases', [])],
                 families=[atlas.family, *seed.get('families', [])],
                 legacy_groups=[seed['catalog_group']],
                 lesson=' '.join(s for s in (notes['lesson'], notes['reuse_notes']) if s.strip()),
                 limits=' '.join(s for s in (guide['limits'], STANDARD_LIMITS) if s.strip()),
                 subjects=[seed['category'], *seed.get('subjects', [])],
                 techniques=list(seed.get('techniques', [])),
                 style=seed.get('style', ''),
                 origin=dict(model=seed['model'], section=seed['section'], parent=seed['parent'],
                             sha256=seed['source_sha256'], discovery_id=seed['discovery']['id'],
                             database_description=seed['discovery']['description'],
                             description_accuracy=seed['discovery']['accuracy']),
                 model=f'{package}/source.mpd', plan=f'{package}/scene.plan.json', manual=f'{package}/index.html',
                 study_notes=f'{package}/study-notes.json', study_guide=f'{package}/GUIDE.md')
    if (folder/'generate.py').is_file():
        entry['generator'] = f'{package}/generate.py'
    if manual['rendered']:
        entry['preview'] = f'{package}/renders/home.png'
    if (folder/'board/mosaic.png').is_file():
        entry['board'] = f'{package}/board/mosaic.png'
    if (folder/'visual-review.json').is_file():
        entry['visual_review'] = f'{package}/visual-review.json'
    entry['model_sha256'] = sha(folder/'source.mpd')
    return entry


def readme_text(atlas, seed, entry):
    source = f"`{seed['model']}` / `{seed['section']}`" + (f" (placed by `{seed['parent']}`)" if seed['parent'] else ' (root section)')
    style = f" Style: {seed['style']}." if seed.get('style') else ''
    return f'''# {seed['title']}

{entry['lesson']}

Read [GUIDE.md](GUIDE.md) for the construction, what the parent supplies, how to read the board and the limits; [index.html](index.html) holds the {'completed-model views' if seed.get('overview') else 'build pages'}. Source: {source}.{style} Atlas: [{atlas.relative}]({'../'+atlas.directory.name}/README.md).

## Knowledge registration

```ldraw-knowledge
{json.dumps([entry], indent=2, ensure_ascii=False)}
```
'''


def refresh_notes(atlas, outdir, key):
    """Rewrite a prepared study's notes, viewer and guide from the seed without re-rendering.

    Notes are hashed evidence, so the recorded hash is updated and any earlier review is
    dropped: a review must follow the final notes.
    """
    from .manuals import operation_notes
    seed = atlas.seed(key)
    folder = Path(outdir).resolve()/key
    manual = json.loads((folder/'manual.json').read_text())
    notes_file = manual.get('notes_file', 'study-notes.json')
    atomic_write(folder/notes_file, dumps(operation_notes(seed['notes'], kind='construction'))+'\n')
    manual['title'] = seed['title']
    manual['artifact_hashes'][notes_file] = sha(folder/notes_file)
    atomic_write(folder/'manual.json', dumps(manual)+'\n')
    write_manual_viewer(folder, manual, json.loads((folder/notes_file).read_text()))
    (folder/'visual-review.json').unlink(missing_ok=True)
    write_guide(atlas, seed, folder, manual)
    current_manual(folder)
    return dict(key=key, notes=notes_file, review='pending')


def install(atlas, outdir, key, *, force=False):
    """Copy a reviewed study into examples/<package>/ and register it in that package's README."""
    from .knowledge import examples
    seed = atlas.seed(key)
    preflight(atlas, seed, complete=True)
    folder = Path(outdir).resolve()/key
    if current_review(folder) is None:
        raise ValueError(key+': open the images and record a current visual review before installing')
    _, manual = current_manual(folder)
    if seed['use'] == 'adapt' and (not manual['source_checks_passed'] or manual['bom_matches'] is not True):
        raise ValueError(key+': an adapt entry needs passing source checks and a matching rendered BOM')
    if seed['use'] == 'inspiration' and manual['source_checks_passed'] and manual['bom_matches'] is not False:
        raise ValueError(key+': checks pass; register it as adapt or record why it stays inspiration in its guide')
    write_guide(atlas, seed, folder, manual)
    target = atlas.package_dir(seed)
    if target.exists():
        if not force:
            raise ValueError(key+': package exists: '+str(target)+'; use force to replace it')
        shutil.rmtree(target)
    shutil.copytree(folder, target, ignore=shutil.ignore_patterns('__pycache__'))
    entry = registration(atlas, seed, target)
    atomic_write(target/'README.md', readme_text(atlas, seed, entry))
    rows = atlas.rows()
    for row in rows:
        if row['key'] == key:
            row['status'] = 'promoted'
    atlas.save(rows)
    record = next(r for r in examples(atlas.root) if r['id'] == entry['id'])
    if record['scope'] != entry['scope']:
        raise ValueError(key+': registration did not admit as '+entry['scope']+': '+record.get('export_blocker', ''))
    return dict(package=str(target), id=entry['id'], scope=record['scope'], alias=entry['aliases'][0])
