"""Attributed source studies with build pages, parts lists and explicit review.

Construction studies for any atlas; mechanism analysis remains separate.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil

from ldraw import Colour, Piece, inspect_model

from .builder import serialize_mpd
from .common import DATA, atomic_write, dumps, jsonable, normalized
from .discovery import confined
from .document import (dependency_closure, extract_section, is_part, parse_source,
                       physical_context, resolve_section, section_table)
from .external import compare_bom, render, render_steps
from .geometry import analyze_geometry, geometry_complete
from .reference_catalog import preview_wrapper
from .validation import validate_text


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def construction_steps(model, section, parts):
    """Keep source step numbers; a subassembly placement remains a callout."""
    selected = resolve_section(model, section)
    table = section_table(model)
    rows = []
    for number, step in enumerate(selected.steps, 1):
        counts = Counter((p.reference, p.colour.code) for p in step if isinstance(p, Piece))
        if not counts:
            continue
        added = []
        for (ref, colour), quantity in counts.items():
            child = table.get(normalized(ref))
            kind = 'submodel' if child is not None and not is_part(child) else 'part'
            title = child.description if child is not None else parts.by_code.get(normalized(ref).removesuffix('.dat'), ref)
            added.append(dict(ref=ref, colour=colour, quantity=quantity, kind=kind,
                              description=title, source_section=child.name if kind == 'submodel' else None))
        rows.append(dict(number=number, added_placements=sum(counts.values()), parts=added, images={}))
    return rows


def preview_section(model, section, colour):
    closure = dependency_closure(model, section)
    selected = closure[0]
    # Resolve only this section's inherited placements. Descendants retain their
    # inheritance, including explicit colours on subassembly instances.
    return replace(selected, objects=[replace(p, colour=Colour(colour))
        if isinstance(p, Piece) and p.colour.code == 16 else p for p in selected.objects],
        submodels={normalized(s.name):s for s in closure[1:]})


NOTE_FIELDS = {
    "mechanism": ("function", "fixed", "moving", "input", "output", "parent_context", "reuse_notes"),
    "construction": ("lesson", "construction", "interfaces", "parent_context", "reuse_notes"),
}


def study_kind(manual):
    return "mechanism" if manual["scope"] == "mechanism-construction-study" else "construction"


def operation_notes(notes=None, *, kind="mechanism"):
    notes = dict(notes or {})
    if kind not in NOTE_FIELDS:
        raise ValueError('Choose construction or mechanism notes')
    allowed = set(NOTE_FIELDS[kind])
    if set(notes) - allowed or any(not isinstance(v, str) for v in notes.values()):
        raise ValueError('Study notes accept text fields: '+', '.join(sorted(allowed)))
    return dict(version=1, evidence='interpretation_of_source_and_images',
                **({'analytical_verification':'deferred'} if kind == 'mechanism' else {}),
                **{k:notes.get(k, '') for k in sorted(allowed)})


def prepare_manual(path, section, outdir, parts, *, title=None, views=('home', 'back'),
                   colour=7, notes=None, renders=True, normalize_rotations=False,
                   repair_bfc=False, force=False, max_instances=2000, kind="mechanism", overview=False):
    path, outdir = Path(path).resolve(), Path(outdir).resolve()
    if path.is_relative_to(outdir):
        raise ValueError('Use a separate destination; preparation must not overwrite its source')
    if outdir.exists() and any(outdir.iterdir()) and not force:
        raise ValueError('Destination exists; use --force for an intentional refresh')
    if colour in {16,24} or colour not in parts.colours_by_code:
        raise ValueError('Choose an explicit installed preview colour')
    if not views or len(set(views)) != len(views) or any(v not in
            {'home','front','back','left','right','top','bottom'} for v in views):
        raise ValueError('Choose distinct supported viewpoints')
    original = parse_source(path)
    selected = resolve_section(original, section)
    if is_part(selected):
        raise ValueError('Choose an assembly section, not an embedded part definition')
    namespace = 'study-'+hashlib.sha256((path.name+'|'+selected.name).encode()).hexdigest()[:12]
    text, extraction = extract_section(path, selected.name, namespace=namespace,
        normalize_rotations=normalize_rotations, repair_bfc=repair_bfc)
    preview_text = preview_wrapper(text, extraction['root'], colour, namespace)
    model, diagnostics = validate_text(preview_text, parts, assembly=True, instance_limit=max_instances)
    if model is None:
        raise ValueError('Source could not be parsed')
    geometry = analyze_geometry(model, parts, detail='summary', contacts='none', instance_limit=max_instances)
    source_passed = not any(d['severity']=='error' for d in diagnostics+geometry['diagnostics'])
    operation = operation_notes(notes, kind=kind)
    notes_file = "operation.json" if kind == "mechanism" else "study-notes.json"
    verification = {"analytical_verification":"deferred"} if kind == "mechanism" else {}
    outdir.mkdir(parents=True, exist_ok=True)
    # Refresh invalidates the current review even if rendering subsequently fails.
    (outdir/'visual-review.json').unlink(missing_ok=True)
    atomic_write(outdir/'source.mpd', text)
    atomic_write(outdir/'extraction.json', dumps(extraction)+'\n')
    atomic_write(outdir/notes_file, dumps(operation)+'\n')
    checks = dict(source_checks_passed=source_passed, diagnostics=diagnostics, geometry=geometry,
                  **verification, physical_validity='not_proven')
    atomic_write(outdir/'source-checks.json', dumps(checks)+'\n')
    model = parse_source(outdir/'source.mpd')
    table = section_table(model)
    physical, overlay = physical_context(model, parts, colour=colour)
    bom = [jsonable(r) for r in physical.bill_of_materials(parts=overlay)]
    atomic_write(outdir/'bom.json', dumps(bom)+'\n')
    parents = [dict(section=s.name, description=s.description, at=jsonable(p.position),
                    matrix=jsonable(p.matrix), colour=p.colour.code)
               for s in section_table(original).values() for p in s.pieces
               if normalized(p.reference) == normalized(selected.name)]
    plan = dict(version=1, author='ldraw-nova '+kind+' reference wrapper', assets=['source.mpd'], sections=[
        dict(name=namespace+'-placement.ldr', description=title or selected.description,
             anchors={'source_origin':dict(at=[0,0,0])}, steps=[[
                 dict(id='reference', ref=model.name, colour=colour, at=[0,0,0],
                      purpose='Source construction; preserve internal geometry and review external interfaces')]])])
    atomic_write(outdir/'scene.plan.json', dumps(plan)+'\n')
    sections, artifacts = [], ['source.mpd','extraction.json','source-checks.json',notes_file,'bom.json','scene.plan.json']
    library = (parts.path.parent/'parts').resolve().parent
    original_names = {v:k for k,v in extraction['renames'].items()}
    root_bounds = None
    for index, sub in enumerate(s for s in table.values() if not is_part(s)):
        steps = construction_steps(model, sub.name, overlay)
        if not steps:
            continue
        directory = f'manual/{index:02}'
        preview = preview_section(model, sub.name, colour)
        preview_path = outdir/directory/'preview.mpd'
        atomic_write(preview_path, serialize_mpd(preview))
        artifacts.append(f'{directory}/preview.mpd')
        if renders and (not overview or index == 0):
            mesh_model, mesh_parts = physical_context(preview, parts)
            mesh = inspect_model(mesh_model, mesh_parts)
            if not geometry_complete(mesh):
                raise ValueError('Cannot make complete build pages: unresolved geometry')
            if index == 0:
                root_bounds = mesh.bounds
            rendered = [] if overview else render_steps(preview_path, library, outdir/directory,
                                    steps=[s['number'] for s in steps], views=views, bounds=mesh.bounds)
            for item in rendered:
                name = f'{directory}/{item["file"]}'
                next(s for s in steps if s['number']==item['step'])['images'][item['view']] = name
                artifacts.append(name)
        sections.append(dict(name=sub.name, original_name=original_names[sub.name],
                             description=sub.description, directory=directory, steps=steps))
    if not sections:
        raise ValueError('Selected assembly has no construction placements')
    comparison = None
    if renders:
        root_preview = outdir/sections[0]['directory']/'preview.mpd'
        render(root_preview, library, outdir/'renders', views=tuple(dict.fromkeys(['home',*views])) if overview else ('home',), bounds=root_bounds)
        comparison = compare_bom(parse_source(root_preview), parts, outdir/'renders/leocad-bom.csv')
        atomic_write(outdir/'bom-comparison.json', dumps(comparison)+'\n')
        artifacts += ['renders/leocad-bom.csv','bom-comparison.json']
        artifacts += ['renders/'+v+'.png' for v in dict.fromkeys(['home',*views] if overview else ['home'])]
    manual = dict(version=1, title=title or selected.description, scope=kind+'-construction-study', notes_file=notes_file,
        image_mode='overview' if overview else 'steps',
        final_images=['renders/'+v+'.png' for v in dict.fromkeys(['home',*views] if overview else ['home'])] if renders else [],
        source=dict(model=path.name, section=selected.name, sha256=extraction['source_sha256']),
        source_root=model.name, preview_colour=colour, parents=parents, sections=sections,
        physical_placements=sum(r['quantity'] for r in bom), views=list(views), rendered=renders,
        source_checks_passed=source_passed, bom_matches=comparison['matches'] if comparison else None,
        **verification, physical_validity='not_proven',
        artifact_hashes={name:sha(outdir/name) for name in artifacts})
    atomic_write(outdir/'manual.json', dumps(manual)+'\n')
    write_manual_viewer(outdir, manual, operation)
    return manual


def write_manual_viewer(outdir, manual, operation):
    if manual.get('image_mode') == 'overview':
        return write_overview_viewer(outdir, manual, operation)
    payload = json.dumps(dict(manual=manual, operation=operation, notes_kind=study_kind(manual),
                              notes_fields=NOTE_FIELDS[study_kind(manual)]), ensure_ascii=False).replace('</','<\\/')
    page = (DATA/'build-manual.html').read_text().replace('/*MANUAL_DATA*/null', payload)
    atomic_write(Path(outdir)/'index.html', page)


def write_overview_viewer(outdir, manual, notes):
    import html
    safe = html.escape
    images = ''.join(f'<figure><img src="{safe(p)}" alt="Completed assembly: {safe(Path(p).stem)}"><figcaption>{safe(Path(p).stem)}</figcaption></figure>' for p in manual['final_images'])
    explanation = ''.join(f'<dt>{safe(k.replace("_"," "))}</dt><dd>{safe(notes[k])}</dd>' for k in NOTE_FIELDS[study_kind(manual)])
    sections = ''.join(f'<li>{safe(s["original_name"])} — {len(s["steps"])} source steps</li>' for s in manual['sections'])
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{safe(manual['title'])}</title><style>body{{font:16px/1.5 system-ui;max-width:1100px;margin:32px auto;padding:0 20px;background:#f6f8fa;color:#20303a}}img{{width:100%}}figure{{margin:16px 0}}dt{{font-weight:bold}}dd{{margin:0 0 12px}}a{{color:#165e9e}}</style><h1>{safe(manual['title'])}</h1><p>Whole-model study · {manual['physical_placements']} parts. These images show the completed assembly, not construction steps.</p><p><a href="source.mpd">Attributed source</a> · <a href="scene.plan.json">Editable plan</a> · <a href="extraction.json">Provenance</a> · <a href="source-checks.json">Checks</a> · <a href="manual.json">Section and step data</a></p><dl>{explanation}</dl>{images}<h2>Sections to study separately</h2><p>Use manual prepare on a selected source section to create its build pages.</p><ul>{sections}</ul></html>'''
    atomic_write(Path(outdir)/'index.html', page)


def current_manual(folder):
    folder = Path(folder).resolve()
    manual = json.loads((folder/'manual.json').read_text())
    required = {'source.mpd','extraction.json','source-checks.json',manual.get('notes_file','operation.json'),'bom.json','scene.plan.json'}
    images = [image for section in manual['sections'] for step in section['steps'] for image in step['images'].values()]
    if manual['rendered']:
        required.update([*manual.get('final_images',['renders/home.png']),'renders/leocad-bom.csv','bom-comparison.json',*images])
        if manual.get('image_mode','steps') != 'overview' and (not images or any(set(s['images']) != set(manual['views']) for section in manual['sections'] for s in section['steps'])):
            raise ValueError('Build manual has incomplete rendered steps')
    hashes = manual.get('artifact_hashes', {})
    if not required.issubset(hashes):
        raise ValueError('Build manual is missing required evidence hashes')
    for name, digest in hashes.items():
        path = confined(folder, name)
        if not path.is_file() or sha(path) != digest:
            raise ValueError('Study artifacts changed; prepare and review the build manual again')
    return folder, manual


def review_manual(folder, *, images, note):
    folder, manual = current_manual(folder)
    available = {image for section in manual['sections'] for step in section['steps'] for image in step['images'].values()}
    available.update(manual.get('final_images',['renders/home.png']))
    if not manual['rendered'] or not note.strip() or set(images) != available or len(images) != len(available):
        raise ValueError('A complete review needs a note and every rendered step/view plus renders/home.png; list only images actually opened')
    review = dict(status='visually_reviewed', note=note, viewed_images=list(images),
                  manual_sha256=sha(folder/'manual.json'),
                  **({'analytical_verification':'deferred'} if study_kind(manual) == 'mechanism' else {}),
                  physical_validity='not_proven')
    atomic_write(folder/'visual-review.json', dumps(review)+'\n')
    return review


def export_manual(folder, outdir, *, force=False):
    folder, manual = current_manual(folder)
    review_path = folder/'visual-review.json'
    review = json.loads(review_path.read_text()) if review_path.is_file() else {}
    images = {p for section in manual['sections'] for step in section['steps'] for p in step['images'].values()}
    images.update(manual.get('final_images',['renders/home.png']))
    if (review.get('status') != 'visually_reviewed' or review.get('manual_sha256') != sha(folder/'manual.json')
            or set(review.get('viewed_images', [])) != images or not review.get('note', '').strip()):
        raise ValueError('Record a current visual review before exporting this construction reference')
    if not manual['source_checks_passed'] or manual['bom_matches'] is not True:
        raise ValueError('Export requires passing source checks and a matching rendered BOM')
    operation = json.loads(confined(folder, manual.get('notes_file','operation.json')).read_text())
    if any(not operation.get(k, '').strip() for k in NOTE_FIELDS[study_kind(manual)]):
        raise ValueError('Describe the construction and parent context before export; mark unresolved roles explicitly')
    target = Path(outdir).resolve()
    if target == folder or target.is_relative_to(folder) or folder.is_relative_to(target):
        raise ValueError('Choose a separate export directory')
    if target.exists() and any(target.iterdir()) and not force:
        raise ValueError('Export destination exists; use --force')
    target.mkdir(parents=True, exist_ok=True)
    for name in [*manual['artifact_hashes'], 'manual.json', 'visual-review.json', 'index.html']:
        dest = confined(target, name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(confined(folder, name), dest)
    for name in ['GUIDE.md', 'generate.py']:
        if (folder/name).is_file():
            shutil.copyfile(folder/name, target/name)
    return dict(output=str(target), plan=str(target/'scene.plan.json'), source=str(target/'source.mpd'),
                **({'analytical_verification':'deferred'} if study_kind(manual) == 'mechanism' else {}),
                next='Build the plan, inspect its interfaces and review the composed model; use --contacts none for mechanisms.')


def regenerate_placement(directory):
    """Rebuild a copied placement plan without running mechanism analysis."""
    from .builder import build_plan, load_plan
    from .common import get_parts
    directory = Path(directory)
    parts = get_parts()
    text, model, diagnostics = build_plan(load_plan(directory/'scene.plan.json'), parts)
    geometry = analyze_geometry(model, parts, detail='summary', contacts='none')
    if any(d['severity']=='error' for d in diagnostics+geometry['diagnostics']):
        raise ValueError(dumps(dict(diagnostics=diagnostics, geometry=geometry)))
    target = directory/(directory.name+'.mpd')
    atomic_write(target, text)
    return dict(output=str(target), source_checks_passed=True, analytical_verification='deferred')
