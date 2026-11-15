"""Build and review assemblies through the existing validation/CAD adapters.

A review owns one output directory. Work is staged so a failed rerun cannot
leave old previews attached to a new validation report. The manifest identifies
the exact model bytes and every artifact; visual inspection remains a human task.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import jsonschema
from ldraw import BoundingBox, Vector
from ldraw.errors import PartError

from .builder import build_plan, load_plan
from .common import CACHE, atomic_write, dumps, jsonable, normalized
from .report import schema_diagnostic, text as compact_text
from .identity import BuildError, annotate, named_contract
from .document import dependency_closure, physical_context, selected_source
from .external import compare_bom, render
from .geometry import analyze_geometry
from .validation import validate_file


def model_name(source):
    """Use the same basename for foo.plan.json, foo.json and foo.mpd."""
    path = Path(source)
    return path.name[:-10] if path.name.endswith('.plan.json') else path.stem


def check_model(model, parts, diagnostics, **geometry_options):
    """Add geometry evidence only after source validation succeeds."""
    diagnostics = list(diagnostics)
    geometry = None
    if model is not None and not any(d['severity'] == 'error' for d in diagnostics):
        geometry = analyze_geometry(model, parts, **geometry_options)
        diagnostics.extend(geometry['diagnostics'])
    report = dict(checks_passed=model is not None and not any(d['severity'] == 'error' for d in diagnostics),
                  physical_validity='not_proven', diagnostics=diagnostics, geometry=geometry)
    if not report['checks_passed']:
        report['failed_stage'] = 'source' if geometry is None else 'geometry'
    return report


def build_checked(plan, parts, **geometry_options):
    """The same source and geometry checks used by both build and review."""
    assets, context = [], {}
    text, model, diagnostics = build_plan(plan, parts, instance_limit=geometry_options.get('instance_limit', 100000),
                                         asset_reports=assets, context=context)
    report = check_model(model, parts, diagnostics, **geometry_options)
    identity = context['identity']
    source_map = identity.map(model, parts, instance_limit=geometry_options.get('instance_limit', 100000)) if model else []
    report['source_map'] = source_map
    if context.get('seats'):
        report['seats'] = context['seats']
    report['diagnostics'] = annotate(report['diagnostics'], source_map)
    if context.get('curves') and report['checks_passed']:
        from .flex_plan import review_routes
        interactions = review_routes(model, parts, source_map, context['curves'],
                                     instance_limit=geometry_options.get('instance_limit', 100000))
        report['flex_interactions'] = interactions
        report['diagnostics'].extend(interactions['diagnostics'])
        report['checks_passed'] &= interactions['checks_passed']
        if not interactions['checks_passed']:
            report['failed_stage'] = 'flex.interactions'
    if assets:
        report['flex'] = assets
        report['diagnostics'].extend(d for asset in assets for d in asset['validation']['diagnostics'])
    if report['checks_passed']:
        from .technic_review import review_structure
        for section in plan['sections']:
            if not section.get('structure'):
                continue
            # Hash the source model, including embedded part definitions. Physical
            # expansion happens inside the reviewer, after revision validation.
            scoped = model
            if normalized(section['name']) != normalized(model.name):
                closure = dependency_closure(model, section['name'])
                scoped = replace(closure[0], submodels={normalized(s.name): s for s in closure[1:]})
            scoped_map = identity.map(scoped, parts, instance_limit=geometry_options.get('instance_limit', 100000))
            if isinstance(section['structure'], dict):
                try:
                    contract = named_contract(section['structure'], scoped_map, scoped)
                except ValueError as exc:
                    raise BuildError(str(exc), stage='structure', section=section['name'],
                                     **identity.sources.get(normalized(section['name']), {})) from exc
                raw = (dumps(contract) + '\n').encode()
                path = CACHE / 'contracts' / (hashlib.sha256(raw).hexdigest() + '.json')
                atomic_write(path, raw.decode())
            else:
                path = Path(section['structure'])
                raw = path.read_bytes()
                contract = json.loads(raw)
            checked = review_structure(scoped, parts, contract=contract,
                                       instance_limit=geometry_options.get('instance_limit', 100000))
            checked['diagnostics'] = annotate(checked['diagnostics'], scoped_map)
            checked.update(contract=str(path), contract_sha256=hashlib.sha256(raw).hexdigest())
            report.setdefault('structure', {})[section['name']] = checked
            report['diagnostics'].extend(dict(d, section=section['name']) for d in checked['diagnostics'])
            report['checks_passed'] &= checked['checks_passed']
            if not checked['checks_passed']:
                report['failed_stage'] = 'structure'
    return text, model, report


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_destination(outdir, source, force=False):
    """Only replace an unchanged, tool-owned bundle; never delete user work.

    A verified generated bundle is replaced without --force: it is evidence for
    an older revision and is regenerated from source. Added, missing or edited
    files and symlinks still stop the review.
    """
    if source.is_relative_to(outdir):
        raise ValueError('Review output must not contain its input; choose another --outdir')
    if not outdir.exists():
        return
    if not outdir.is_dir() or outdir.is_symlink():
        raise ValueError('Review output must be a directory, not a file or symlink')
    if not any(outdir.iterdir()):
        return
    try:
        manifest = json.loads((outdir / 'review.json').read_text())
        artifacts = manifest['artifacts']
        if manifest['format'] != 'ldraw-nova-review' or manifest['version'] != 1 or not isinstance(artifacts, dict):
            raise ValueError('Unrecognized review manifest')
        actual = {str(p.relative_to(outdir)) for p in outdir.rglob('*') if p.is_file()}
        if actual != set(artifacts) | {'review.json'} or any(p.is_symlink() for p in outdir.rglob('*')):
            raise ValueError('Review directory contains additional or missing files')
        if any(sha256(outdir / name) != digest for name, digest in artifacts.items()):
            raise ValueError('Review artifacts were edited')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f'Refusing to replace user files in {outdir}; choose another --outdir ({exc})') from exc


def toolkit_fingerprint():
    root = Path(__file__).resolve().parent
    rows = sorted(f'{p.relative_to(root)}:{p.stat().st_size}:{p.stat().st_mtime_ns}'
                  for p in root.rglob('*') if p.is_file() and p.suffix in {'.py', '.json'})
    return hashlib.sha256('\n'.join(rows).encode()).hexdigest()


def review_inputs(source, source_hash, parts, *, section, colour, views, renders, draft, geometry_options):
    """Everything a review result depends on; equal inputs reuse the bundle."""
    dependencies = {}
    if source.suffix.casefold() == '.json':
        plan = load_plan(source)
        dependencies = {s['file']: s['sha256'] for s in plan.sources.values()}
        files = [a if isinstance(a, str) else a['source'] for a in plan.get('assets', [])]
        files += [a['checks']['obstacles'] for a in plan.get('assets', []) if isinstance(a, dict) and a.get('checks', {}).get('obstacles')]
        files += [s['structure'] for s in plan['sections'] if isinstance(s.get('structure'), str)]
        for file in files:
            dependencies[str(file)] = sha256(file)
        if any('flex' in e for s in plan['sections'] for step in s['steps'] for e in step):
            return None  # inline synthesis depends on LSynth and its cache: always rerun
    index = getattr(parts, 'path', None)
    signature = Path(index).with_name('signature') if index else None
    return dict(source=source_hash, dependencies=dependencies, section=section, colour=colour, views=list(views),
                renders=renders, draft=draft, geometry={k: v for k, v in sorted(geometry_options.items())},
                toolkit=toolkit_fingerprint(),
                library=signature.read_text() if signature and signature.exists() else None)


def floating_names(validation, source_map=None):
    """Placement names outside the main connected group, or None without contacts."""
    geometry = validation.get('geometry') or {}
    outside = geometry.get('outside_main_group')
    if outside is None:
        return None, None
    rows = {r['index']: r['path'] for r in source_map or []}
    total = geometry.get('occurrence_count', 0)
    def name(i):
        return rows.get(i, f'#{i}')
    return [name(i) for i in outside], [name(i) for i in range(total)]


def connectivity_change(previous, floating, everyone):
    """Placements that were connected in the previous bundle and are not now."""
    if previous is None or floating is None:
        return []
    before = set(previous.get('placements', [])) - set(previous.get('floating', []))
    return sorted(set(floating) & before)


def review(source, parts, library, *, outdir=None, force=False, section=None, colour=None,
           views=('home', 'top', 'front'), renders=True, timeout=90, draft=False, **geometry_options):
    """Review a JSON plan or MPD/LDR, returning a manifest and CLI exit status.

    Exit 0: selected automatic checks passed (images still need inspection).
    Exit 1: validation or BOM comparison failed. Exit 2: execution/input failure.
    Failed runs also publish their available reports, replacing stale evidence.
    Unchanged inputs reuse the existing bundle unless ``force`` is set.
    With ``draft``, a model that fails its checks is still rendered for inspection.
    """
    source = Path(source).expanduser().resolve()
    if source.suffix.casefold() not in {'.json', '.mpd', '.ldr'}:
        raise ValueError('Review expects a JSON plan or an MPD/LDR assembly')
    if colour is not None and section is None:
        raise ValueError('--colour requires --section')
    if not views or len(set(views)) != len(views) or any(v not in
            {'home', 'top', 'front', 'back', 'left', 'right', 'bottom'} for v in views):
        raise ValueError('Choose distinct supported viewpoints')
    if geometry_options.get('offset', 0) < 0:
        raise ValueError('--offset must be nonnegative')
    suffix = '-' + Path(section).stem if section else ''
    outdir = Path(outdir or source.with_name(model_name(source) + suffix + '-review')).expanduser()
    if outdir.is_symlink():
        raise ValueError('Review output must not be a symlink')
    outdir = outdir.resolve()
    check_destination(outdir, source, force)
    source_hash = sha256(source)
    outdir.parent.mkdir(parents=True, exist_ok=True)
    geometry_options.setdefault('detail', 'summary')
    try:
        inputs = review_inputs(source, source_hash, parts, section=section, colour=colour, views=views,
                               renders=renders, draft=draft, geometry_options=geometry_options)
    except (OSError, ValueError, jsonschema.ValidationError):
        inputs = None  # the review itself reports the failure
    previous_connectivity = None
    if (outdir / 'review.json').exists():
        try:
            previous = json.loads((outdir / 'review.json').read_text())
            if not force and inputs is not None and previous.get('inputs') == inputs:
                return dict(previous, reused=True), previous.get('exit_code', 1)
            if (outdir / 'connectivity.json').exists():
                previous_connectivity = json.loads((outdir / 'connectivity.json').read_text())
        except (OSError, ValueError):
            pass
    report = dict(format='ldraw-nova-review', version=1,
                  source=dict(path=str(source), sha256=source_hash, section=section, colour=colour),
                  output=str(outdir), checks_passed=False, physical_validity='not_proven',
                  visual_review='not_rendered', model_sha256=None,
                  stages=dict(validation='not_run', bom='not_run', render='not_run', bom_comparison='not_run'),
                  artifacts={}, inputs=inputs)
    report['coverage'] = dict(scope='section' if section else 'model', section=section,
                              final_model_review=section is None)
    status = 2
    with TemporaryDirectory(prefix='.review-', dir=outdir.parent) as temp:
        work = Path(temp) / 'bundle'
        work.mkdir()
        stage = 'validation'
        source_map = None
        try:
            if source.suffix.casefold() == '.json':
                plan = load_plan(source)
                if section:
                    from .builder import select_plan
                    plan = select_plan(plan, section, colour=colour)
                if sha256(source) != source_hash:
                    raise ValueError('Source changed while loading the plan; rerun on the saved revision')
                text, model, validation = build_checked(plan, parts, **geometry_options)
                model_bytes = text.encode('utf-8')
                source_map = validation.get('source_map')
                sources = {s['file']: s['sha256'] for key, s in plan.sources.items()
                           if key in {normalized(s['name']) for s in plan['sections']}}
                for i, (path, digest) in enumerate(sorted(sources.items()), 1):
                    frozen = work / 'sources' / f'{i}.json'
                    frozen.parent.mkdir(exist_ok=True)
                    shutil.copyfile(path, frozen)
                    if sha256(frozen) != digest:
                        raise ValueError(f'Plan dependency changed during review: {path}; rerun on the saved revision')
                validation['source_dependencies'] = sources
            else:
                # Freeze input before parsing, scoping or invoking an external renderer.
                snapshot = Path(temp) / source.name
                snapshot.write_bytes(source.read_bytes())
                if sha256(snapshot) != source_hash:
                    raise ValueError('Source changed while starting review; rerun on the saved revision')
                model, diagnostics = validate_file(snapshot, parts, assembly=True, section=section,
                    colour=colour, instance_limit=geometry_options.get('instance_limit', 100000))
                validation = check_model(model, parts, diagnostics, **geometry_options)
                model_bytes = (selected_source(snapshot, section, colour)[0].encode('utf-8')
                               if section and validation['checks_passed'] else snapshot.read_bytes())
            validation.update(file=str(source), section=section, profile='assembly')
            validation['model_sha256'] = hashlib.sha256(model_bytes).hexdigest()
            # Freeze the generated dependencies and their evidence with this review.
            # The editable originals and disposable cache can change afterward.
            for i, asset in enumerate(validation.get('flex', []), 1):
                folder = work / 'flex' / str(i)
                folder.mkdir(parents=True)
                for key, name in [('source', 'constraints.ldr'), ('output', 'asset.mpd'), ('manifest', 'asset.manifest.json')]:
                    shutil.copyfile(asset[key], folder / name)
                if sha256(folder / 'constraints.ldr') != asset['source_sha256'] or sha256(folder / 'asset.mpd') != asset['model_sha256']:
                    raise ValueError('Flexible asset changed during review; rerun on the saved revision')
            for i, checked in enumerate(validation.get('structure', {}).values(), 1):
                target = work / 'structure' / f'{i}.json'
                target.parent.mkdir(exist_ok=True)
                shutil.copyfile(checked['contract'], target)
                if sha256(target) != checked['contract_sha256']:
                    raise ValueError('Structure contract changed during review; rerun on the saved revision')
            floating, everyone = floating_names(validation, source_map)
            if floating is not None:
                atomic_write(work / 'connectivity.json', compact_text(dict(
                    model_sha256=validation['model_sha256'], floating=floating, placements=everyone)) + '\n')
                lost = connectivity_change(previous_connectivity, floating, everyone)
                if lost:
                    validation['diagnostics'].append(dict(
                        code='assembly.became_floating', severity='warning', count=len(lost),
                        message=f'{len(lost)} placement(s) were connected in the previous review and are not now; '
                                'the last edit disconnected them.',
                        placements=[dict(path=name) for name in lost[:20]]))
            atomic_write(work / 'validation.json', compact_text(validation) + '\n')
            report['stages']['validation'] = 'passed' if validation['checks_passed'] else 'failed'
            report['diagnostics'] = validation['diagnostics']
            if not validation['checks_passed']:
                report['failed_stage'] = validation.get('failed_stage', 'validation')
            status = 1
            if draft and not validation['checks_passed'] and model is not None:
                # Show the failing state; nothing here counts as passing evidence.
                stage = 'render'
                draft_path = work / 'draft.mpd'
                draft_path.write_bytes(model_bytes)
                bounds = (validation.get('geometry') or {}).get('bounds')
                bounds = BoundingBox(Vector(*bounds['min']), Vector(*bounds['max'])) if bounds else None
                render(draft_path, library, work / 'previews', views=views, timeout=timeout, bounds=bounds)
                (work / 'previews' / 'leocad-bom.csv').unlink(missing_ok=True)
                report['stages']['render'] = 'draft'
                report['visual_review'] = 'draft: these images show a model that failed its checks'
            if validation['checks_passed']:
                model_path = work / 'model.mpd'
                model_path.write_bytes(model_bytes)
                report['model_sha256'] = sha256(model_path)
                stage = 'bom'
                physical, model_parts = physical_context(model, parts)
                bom = jsonable(physical.bill_of_materials(parts=model_parts))
                report['physical_placements'] = sum(row['quantity'] for row in bom)
                atomic_write(work / 'bom.json', compact_text(dict(model_sha256=report['model_sha256'], bom=bom,
                    physical_placements=report['physical_placements'])) + '\n')
                report['stages']['bom'] = 'passed'
                if renders:
                    stage = 'render'
                    bounds = validation['geometry']['bounds']
                    bounds = BoundingBox(Vector(*bounds['min']), Vector(*bounds['max'])) if bounds else None
                    rendered = render(model_path, library, work / 'previews', views=views, timeout=timeout, bounds=bounds)
                    report['stages']['render'] = 'passed'
                    report['visual_review'] = 'required: open and inspect the images'
                    stage = 'bom_comparison'
                    comparison = compare_bom(model, parts, rendered['bom'])
                    comparison['model_sha256'] = report['model_sha256']
                    atomic_write(work / 'bom-comparison.json', compact_text(comparison) + '\n')
                    report['stages']['bom_comparison'] = 'passed' if comparison['matches'] else 'failed'
                    status = 0 if comparison['matches'] else 1
                else:
                    report['stages'].update(render='skipped', bom_comparison='skipped')
                    status = 0
        except (OSError, ValueError, PartError, RecursionError, subprocess.SubprocessError, jsonschema.ValidationError) as exc:
            status = 2
            report['stages'][stage] = 'failed'
            report.update(error=str(exc), error_type=type(exc).__name__)
            if isinstance(exc, BuildError):
                report.update(failed_stage=exc.stage, diagnostics=exc.diagnostics)
                atomic_write(work / 'validation.json', compact_text(jsonable(dict(checks_passed=False,
                    physical_validity='not_proven', geometry=None, failed_stage=exc.stage,
                    diagnostics=exc.diagnostics))) + '\n')
            elif isinstance(exc, jsonschema.ValidationError):
                diagnostic = schema_diagnostic(exc, getattr(exc, 'nova_file', str(source)))
                report.update(error=diagnostic['message'], failed_stage='schema', diagnostics=[diagnostic])
                atomic_write(work / 'validation.json', compact_text(dict(checks_passed=False,
                    physical_validity='not_proven', geometry=None, failed_stage='schema',
                    diagnostics=report['diagnostics'])) + '\n')
            if stage == 'render':
                shutil.rmtree(work / 'previews', ignore_errors=True)
        report.update(checks_passed=status == 0, exit_code=status)
        report['artifacts'] = {str(p.relative_to(work)): sha256(p) for p in sorted(work.rglob('*')) if p.is_file()}
        report = jsonable(report)
        atomic_write(work / 'review.json', compact_text(report) + '\n')
        # Recheck before replacing, in case the user edited an earlier bundle.
        check_destination(outdir, source, force)
        previous = Path(temp) / 'previous'
        if outdir.exists():
            outdir.replace(previous)
        try:
            work.replace(outdir)
        except OSError:
            if previous.exists():
                previous.replace(outdir)
            raise
    return report, status
