"""Measured, attributed reference cards and an offline visual inspiration catalog."""
from __future__ import annotations

import html
import hashlib
import json
import shutil
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import get_context
from pathlib import Path

from ldraw import Parts, inspect_model

from .common import atomic_write, dumps, jsonable
from .discovery import confined, digest, record_id
from .document import extract_section, physical_context
from .external import compare_bom, render
from .geometry import analyze_geometry
from .validation import validate_text

CARD_VERSION = 1
VIEWS = ('home', 'front', 'back', 'right', 'left', 'top', 'bottom')
DEFAULT_VIEWS = ('home', 'front', 'right', 'top')


def _passed(diagnostics):
    return not any(d['severity']=='error' for d in diagnostics)


def preview_wrapper(text, root, colour, identity):
    return ('\r\n'.join([f'0 FILE preview-{identity}.ldr', '0 Reference preview with explicit inherited colour',
            '0 Author: ldraw-nova reference catalog', '0 !LDRAW_ORG Model',
            f'1 {colour} 0 0 0 1 0 0 0 1 0 0 0 1 {root}', '0 NOFILE'])+'\r\n'+text)


def prepare_reference(index, row, outdir, *, views=DEFAULT_VIEWS, colour=7, contacts='none', timeout=90, refresh=False):
    if row['kind'] not in {'models','submodels'} or row['record_type'] != 'assembly':
        raise ValueError('Reference cards require a model/submodel assembly; use part-board for parts')
    if not views or any(view not in VIEWS for view in views) or len(set(views)) != len(views):
        raise ValueError('Choose distinct home/front/back/right/left/top/bottom views')
    if colour not in index.parts.colours_by_code or colour in {16,24}:
        raise ValueError('Preview colour must be an explicit installed surface colour')
    if contacts not in {'none','auto','all'}:
        raise ValueError('Unknown contact mode')
    inventory = index.inventory(row)
    destination = Path(outdir).resolve()/row['id']
    destination.mkdir(parents=True, exist_ok=True)
    card_path = destination/'card.json'
    if not hasattr(index, '_review_signature'):
        library = (index.parts.path.parent/'parts').resolve().parent
        roots = [library/'parts', library/'p', *[Path(s.source).resolve() for s in index.parts._connection_shadow_libraries]]
        stamps = []
        for root in roots:
            paths = sorted(root.rglob('*.dat')) if root.is_dir() else [root]
            stamps.extend((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths)
        index._review_signature = digest(stamps)
    key = digest([CARD_VERSION, row['id'], row['source_sha256'], index.manifest_path.read_text(), colour, contacts, index._review_signature])
    if card_path.is_file() and not refresh:
        card = json.loads(card_path.read_text())
        artifacts = ['source.mpd','preview.mpd','extraction.json','renders/leocad-bom.csv', *['renders/'+v+'.png' for v in views]]
        if (card.get('cache_key') == key and all((destination/f).is_file() and
                hashlib.sha256((destination/f).read_bytes()).hexdigest()==card.get('artifact_hashes',{}).get(f) for f in artifacts)
                and all(v in card['views'] for v in views)):
            return card
    if not hasattr(index, '_mesh_parts'):
        index._mesh_parts = Parts(index.parts.path)
    namespace = 'ref-'+row['id'].split('-',1)[1][:16]
    selected = inventory['parser_section']
    text, provenance = extract_section(row['path'], selected, namespace=namespace, repair_bfc=True, normalize_rotations=True)
    provenance['requested_identity'] = {k:row[k] for k in ['id','kind','model','section'] if k in row}
    raw, raw_manifest = extract_section(row['path'], selected, namespace=namespace)
    raw_preview = preview_wrapper(raw, raw_manifest['root'], colour, row['id'])
    _, raw_diagnostics = validate_text(raw_preview, index.parts, assembly=True)
    preview = preview_wrapper(text, provenance['root'], colour, row['id'])
    model, diagnostics = validate_text(preview, index.parts, assembly=True)
    if model is None:
        raise ValueError('Extracted source cannot be parsed')
    atomic_write(destination/'source.mpd', text)
    atomic_write(destination/'preview.mpd', preview)
    atomic_write(destination/'extraction.json', dumps(provenance)+'\n')
    physical, mesh_parts = physical_context(model, index._mesh_parts)
    mesh = inspect_model(physical, mesh_parts)
    geometry = analyze_geometry(model, index.parts, detail='summary', contacts=contacts, output_limit=30) if contacts != 'none' else None
    size = jsonable(mesh.bounds.size) if mesh.bounds else None
    library = (index.parts.path.parent/'parts').resolve().parent
    report = render(destination/'preview.mpd', library, destination/'renders', views=views,
                    timeout=timeout, bounds=mesh.bounds if mesh.complete and not inventory['raw_geometry_sections'] else None)
    comparison = compare_bom(model, index.parts, destination/'renders/leocad-bom.csv')
    card = dict(version=CARD_VERSION, cache_key=key, id=row['id'], kind=row['kind'], model=row['model'],
                section=row.get('section'), parser_section=selected, description=row['description'],
                parent_description=row.get('parent_description'), theme=row.get('theme'),
                source=dict(path=row['path'], sha256=row['source_sha256'], field=row['source_field'], start_line=row['start_line']),
                source_root=provenance['root'], preview_colour=colour, inventory=inventory, attribution=provenance['attribution'],
                bounds=jsonable(mesh.bounds), size_ldu=size,
                size_studs_plates_studs=[size[0]/20,size[1]/8,size[2]/20] if size else None,
                mesh_complete=mesh.complete, mesh_diagnostics=jsonable(mesh.diagnostics),
                raw_assembly_checks_passed=_passed(raw_diagnostics), raw_diagnostic_counts=dict(Counter(d['code'] for d in raw_diagnostics)),
                assembly_checks_passed=_passed(diagnostics), diagnostics=diagnostics,
                repairs=provenance['changes'], geometry=geometry, contacts_checked=bool(geometry and geometry['contacts_checked']),
                bom_comparison=comparison, views=list(views), artifacts=dict(source='source.mpd',preview='preview.mpd',manifest='extraction.json'),
                status='reference' if _passed(diagnostics) and mesh.complete and comparison['matches'] and inventory['physical_accounting_complete'] else 'adaptation_needed',
                visual_review='pending', physical_validity='not_proven',
                limitations=['Bounds describe the source local axes, including protrusions; they are not connection frames.',
                             'Preview colour resolves inherited 16; extraction retains original colours and authorship.',
                             'Passing checks or matching a BOM does not prove connectivity, stability or fit in a new model.'])
    artifacts = ['source.mpd','preview.mpd','extraction.json','renders/leocad-bom.csv', *['renders/'+v+'.png' for v in views]]
    card['artifact_hashes'] = {f:hashlib.sha256((destination/f).read_bytes()).hexdigest() for f in artifacts}
    atomic_write(card_path, dumps(card)+'\n')
    return card


def write_gallery(outdir, entries, failures=()):
    outdir = Path(outdir).resolve()
    safe = html.escape
    articles = []
    for entry in entries:
        card = entry['card']
        directory = entry.get('gallery_directory',card['id'])
        confined(outdir,directory)
        ident = safe(directory,quote=True)
        role = entry.get('role','reference')
        title = entry.get('title') or card['description']
        geometry = card.get('geometry')
        contact_label = ('geometry inspection reports errors' if geometry and not _passed(geometry['diagnostics']) else
                         'contacts inspected' if card['contacts_checked'] else 'contacts pending')
        review = card.get('visual_review','pending')
        review_label = ('Visual review: '+review['decision']+' ('+', '.join(review['views'])+')' if isinstance(review,dict) else 'Visual review pending')
        size = ' × '.join(f'{v:g}' for v in card['size_studs_plates_studs']) if card['size_studs_plates_studs'] else 'unknown'
        links = ' '.join(f'<a href="{ident}/renders/{view}.png">{view}</a>' for view in card['views'])
        keywords = ' '.join([title, role, card['model'], card.get('section') or '', card.get('parent_description') or '', *entry.get('tags',[])])
        articles.append(f'''<article data-search="{safe(keywords.casefold(),quote=True)}" data-kind="{card['kind']}" data-status="{card['status']}">
<a href="{ident}/renders/{card['views'][0]}.png"><img loading="lazy" src="{ident}/renders/{card['views'][0]}.png" alt="{safe(title,quote=True)}"></a>
<div class="content"><div class="eyebrow">{safe(role)} · {card['kind']}</div><h2>{safe(title)}</h2>
<p class="context">In: {safe(card.get('parent_description') or card['model'])}</p>
<p>{safe(entry.get('lesson','Compare the construction and source context before adapting it.'))}</p>
<p class="facts">{card['inventory']['expanded_leaf_count']} placements · {safe(size)} studs/plates/studs</p>
<p><strong>{'Assembly checks pass' if card['assembly_checks_passed'] else 'Assembly checks fail'}</strong> · {'BOM agrees' if card['bom_comparison']['matches'] else 'BOM differs'} · {contact_label}</p>
<p>{safe(review_label)}</p>
<p class="views">{links}</p><details><summary>Source and inspection</summary><p><code>{safe(card['model'])} / {safe(card.get('section') or card['parser_section'])}</code></p>
<p><a href="{ident}/source.mpd">Extracted MPD</a> · <a href="{ident}/card.json">Measured card</a> · <a href="{ident}/extraction.json">Attribution and repairs</a></p>
<p>{safe(entry.get('placement_notes','Origins and orientations are source-local. Inspect the parent placement and exposed connections.'))}</p></details></div></article>''')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LDraw reference library</title><style>
*{box-sizing:border-box}body{font:15px/1.5 system-ui,sans-serif;margin:0;color:#17272c;background:#edf1f0}header{padding:36px max(24px,4vw);background:#173e3d;color:#f2f6ed}h1{font-size:36px;margin:0 0 12px}header p{max-width:900px}nav{position:sticky;top:0;z-index:1;background:#fff;padding:16px max(24px,4vw);display:flex;gap:12px;flex-wrap:wrap;border-bottom:1px solid #c5d1ce}input,select{font:inherit;padding:9px;border:1px solid #b0c1bc;border-radius:5px}input{flex:1;min-width:220px}main{padding:24px max(24px,4vw);display:grid;gap:24px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}article{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 3px 12px #173e3d10}article[hidden]{display:none}img{width:100%;aspect-ratio:5/4;object-fit:contain;background:#303437}.content{padding:20px}h2{font-size:18px;line-height:1.35;margin:8px 0}.eyebrow{text-transform:uppercase;font-size:11px;letter-spacing:1px;color:#47655d}.context,.facts{color:#596b65;font-size:13px}.views{display:flex;gap:10px;flex-wrap:wrap}a{color:#176360}details{border-top:1px solid #dde4e0;padding-top:12px}code{overflow-wrap:anywhere;font-size:12px}#count{align-self:center}footer{padding:24px 4vw;color:#596b65}</style>
<header><h1>LDraw reference library</h1><p>Explore proportions, dedicated fittings and construction ideas. Models provide context; submodels reveal reusable details. Source checks and images support selection, while every adaptation still needs its own review.</p></header>
<nav><input id="query" type="search" aria-label="Search references" placeholder="Search a role, part of a model, style or set…"><select id="kind" aria-label="Reference kind"><option value="">Models and submodels</option><option value="submodels">Submodels</option><option value="models">Whole models</option></select><select id="status" aria-label="Preparation status"><option value="">All preparation states</option><option value="reference">Source checks passed</option><option value="adaptation_needed">Needs preparation</option></select><span id="count"></span></nav><main>'''+''.join(articles)+'''</main><footer>Dimensions use source-local axes. Passing checks does not establish physical buildability. '''+str(len(failures))+''' catalog entries could not be prepared; see catalog.json.</footer>
<script>const cards=[...document.querySelectorAll('article')],q=document.getElementById('query'),kind=document.getElementById('kind'),status=document.getElementById('status');function filter(){const terms=q.value.toLowerCase().split(/\\s+/).filter(Boolean);let visible=0;for(const card of cards){card.hidden=!terms.every(t=>card.dataset.search.includes(t))||(kind.value&&card.dataset.kind!==kind.value)||(status.value&&card.dataset.status!==status.value);if(!card.hidden)visible++;}document.getElementById('count').textContent=visible+' references';}for(const control of [q,kind,status])control.addEventListener('input',filter);filter();</script></html>'''
    atomic_write(outdir/'index.html', page)


def _prepare_seed(index, seed, outdir, views, contacts, refresh):
    identity = seed.get('id') or record_id(seed)
    row = index.get(identity)
    if seed.get('source_sha256') and seed['source_sha256'] != row.get('source_sha256'):
        raise ValueError('Seed source hash differs; review the changed source before updating the manifest')
    card = prepare_reference(index, row, outdir, views=seed.get('views',views), colour=seed.get('colour',7),
                             contacts=seed.get('contacts',contacts), refresh=refresh)
    return dict(seed, id=identity, card=card)


def _worker_init(library, models, database, cache, shadows):
    from .common import get_parts
    from .discovery import DiscoveryIndex
    global _worker_index
    _worker_index = DiscoveryIndex(get_parts(library,shadows=shadows),models,database=database,cache=cache)


def _worker_prepare(seed, outdir, views, contacts, refresh):
    return _prepare_seed(_worker_index,seed,outdir,views,contacts,refresh)


def _catalog_results(index, seeds, outdir, views, contacts, refresh, jobs):
    if jobs == 1:
        for seed in seeds:
            try:
                yield seed, _prepare_seed(index,seed,outdir,views,contacts,refresh), None
            except Exception as exc:
                yield seed, None, str(exc)
        return
    library = (index.parts.path.parent/'parts').resolve().parent
    shadows = [str(s.source) for s in index.parts._connection_shadow_libraries]
    # Processes keep Parts/SQLite/renderer state separate; each card has its own
    # destination and temporary CAD library. Only the parent writes the catalog.
    with ProcessPoolExecutor(max_workers=jobs,mp_context=get_context('spawn'),initializer=_worker_init,
            initargs=(library,index.root,index.database,index.cache,shadows)) as pool:
        futures = {pool.submit(_worker_prepare,seed,outdir,views,contacts,refresh):seed for seed in seeds}
        for future in as_completed(futures):
            seed = futures[future]
            try:
                yield seed, future.result(), None
            except Exception as exc:
                yield seed, None, str(exc)


def build_catalog(index, manifest, outdir, *, views=DEFAULT_VIEWS, contacts='none', refresh=False, progress=None, jobs=1):
    if jobs not in {1,2,3,4}:
        raise ValueError('Catalog jobs must be 1–4')
    index.ensure()
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    entries, failures = [], []
    seeds = manifest.get('references',[])
    if not seeds:
        raise ValueError('Catalog manifest needs a nonempty references list')
    atomic_write(outdir/'manifest.json', dumps(manifest)+'\n')
    unique = {}
    for seed in seeds:
        identity = seed.get('id') or record_id(seed)
        unique.setdefault(identity,seed)
    order = {identity:i for i,identity in enumerate(unique)}
    for seed, entry, error in _catalog_results(index,list(unique.values()),outdir,views,contacts,refresh,jobs):
        identity = seed.get('id') or record_id(seed)
        if error is None:
            entries.append(entry)
            entries.sort(key=lambda e:order[e['id']])
            if progress:
                progress(dict(id=identity, completed=len(entries), total=len(seeds), status=entry['card']['status']))
        else:
            failures.append(dict(id=identity, error=error))
            if progress:
                progress(dict(id=identity, error=error))
        # A stopped run remains browseable; matching cards are reused on resume.
        report = dict(version=1, title=manifest.get('title','LDraw reference library'), count=len(entries), requested=len(seeds),
                      results=[{k:v for k,v in e.items() if k!='card'} | dict(card=e['id']+'/card.json',preview=e['id']+'/renders/'+e['card']['views'][0]+'.png',
                               status=e['card']['status'],description=e['card']['description'],kind=e['card']['kind']) for e in entries], failures=failures)
        atomic_write(outdir/'catalog.json', dumps(report)+'\n')
        if len(entries) < 3 or len(entries) % 10 == 0:
            write_gallery(outdir, entries, failures)
    write_gallery(outdir,entries,failures)
    return dict(**report, gallery=str(outdir/'index.html'), note='Source preparations and renders are cached; open selected views before recording a visual review.')


def _current_card(index, identity, card_dir):
    source = confined(card_dir, identity)
    card = json.loads((source/'card.json').read_text())
    current = index.get(identity)
    if card['id'] != identity or current.get('source_sha256') != card['source']['sha256']:
        raise ValueError('Reference card is stale; prepare it again')
    artifacts = ['source.mpd','preview.mpd','extraction.json','renders/leocad-bom.csv',
                 *['renders/'+view+'.png' for view in card['views']]]
    for name in artifacts:
        path = confined(source, name)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != card.get('artifact_hashes',{}).get(name):
            raise ValueError('Reference artifacts changed; prepare and review the card again')
    return source, card


def record_review(index, identity, card_dir, *, decision, note, viewed_views):
    """Record only the views actually opened, independently of those rendered."""
    source, card = _current_card(index, identity, card_dir)
    if decision not in {'reuse','adapt','technique','reject'} or not note.strip():
        raise ValueError('Visual review needs a decision and a substantive note')
    if not viewed_views or len(set(viewed_views)) != len(viewed_views) or any(v not in card['views'] for v in viewed_views):
        raise ValueError('List distinct rendered views that you actually inspected')
    card['visual_review'] = dict(decision=decision,note=note,views=list(viewed_views))
    atomic_write(source/'card.json',dumps(card)+'\n')
    return dict(id=identity,visual_review=card['visual_review'],card=str(source/'card.json'))


def export_example(index, identity, card_dir, output, *, title, lesson, placement_notes, scale='unknown', force=False):
    """Export an inspected source plus an editable placement wrapper and its guide."""
    source, card = _current_card(index, identity, card_dir)
    if (card['status'] != 'reference' or not card['contacts_checked'] or
            not card.get('geometry') or not _passed(card['geometry']['diagnostics'])):
        raise ValueError('Example needs passing source and geometry checks, a matching BOM and a contact inspection')
    if not isinstance(card.get('visual_review'),dict) or card['visual_review'].get('decision') not in {'reuse','adapt'}:
        raise ValueError('Record a visual review with a reuse/adapt decision before exporting an example')
    target = Path(output).resolve()
    if target.exists() and any(target.iterdir()) and not force:
        raise ValueError('Example destination exists; use --force')
    target.mkdir(parents=True,exist_ok=True)
    for filename in ['source.mpd','preview.mpd','extraction.json','card.json']:
        shutil.copyfile(source/filename,target/filename)
    shutil.copytree(source/'renders',target/'renders',dirs_exist_ok=True)
    plan = dict(version=1,author='ldraw-nova reference example',assets=['source.mpd'],sections=[
        dict(name='example-'+identity+'.ldr',description=title,anchors={'source_origin':dict(at=[0,0,0])},steps=[[
            dict(id='reference',ref=card['source_root'],colour=card['preview_colour'],at=[0,0,0],purpose=lesson)]])])
    atomic_write(target/'scene.plan.json',dumps(plan)+'\n')
    guide = f'# {title}\n\n{lesson}\n\nSource: `{card["model"]}` / `{card["parser_section"]}`. Scale: {scale}.\n\n{placement_notes}\n\nThe `source_origin` anchor is a positioning frame, not a claimed mechanical connector. The source retains its original coordinates and palette. Read the measured bounds, parent placements and connection coverage in [card.json](card.json) before adapting it.\n\n[Editable plan](scene.plan.json) · [Source MPD](source.mpd) · [Preview](renders/home.png) · [Attribution and repairs](extraction.json).\n\nRun `./ldraw-agent build PATH/scene.plan.json --output output/example.mpd`, then inspect the combined assembly and review its renders.\n'
    atomic_write(target/'README.md',guide)
    return dict(key=target.name,title=title,category='reference',scale=scale,lesson=lesson,placement_notes=placement_notes,
                model=str(target/'preview.mpd'),plan=str(target/'scene.plan.json'),guide=str(target/'README.md'),preview=str(target/'renders/home.png'),
                reference_id=identity,source_sha256=card['source']['sha256'])
