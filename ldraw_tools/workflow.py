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
from pathlib import Path
from tempfile import TemporaryDirectory

import jsonschema
from ldraw import BoundingBox, Vector
from ldraw.errors import PartError

from .builder import build_plan, load_plan
from .common import atomic_write, dumps, jsonable
from .document import physical_context, selected_source
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
    return dict(checks_passed=model is not None and not any(d['severity'] == 'error' for d in diagnostics),
                physical_validity='not_proven', diagnostics=diagnostics, geometry=geometry)


def build_checked(plan, parts, **geometry_options):
    """The same source and geometry checks used by both build and review."""
    text, model, diagnostics = build_plan(plan, parts, instance_limit=geometry_options.get('instance_limit', 100000))
    return text, model, check_model(model, parts, diagnostics, **geometry_options)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_destination(outdir, source, force):
    """Only replace an unchanged, tool-owned bundle; never delete user work."""
    if source.is_relative_to(outdir):
        raise ValueError('Review output must not contain its input; choose another --outdir')
    if not outdir.exists():
        return
    if not outdir.is_dir() or outdir.is_symlink():
        raise ValueError('Review output must be a directory, not a file or symlink')
    if not any(outdir.iterdir()):
        return
    if not force:
        raise ValueError('Review output exists; use --force to replace a generated review')
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


def review(source, parts, library, *, outdir=None, force=False, section=None, colour=None,
           views=('home', 'top', 'front'), renders=True, timeout=90, **geometry_options):
    """Review a JSON plan or MPD/LDR, returning a manifest and CLI exit status.

    Exit 0: selected automatic checks passed (images still need inspection).
    Exit 1: validation or BOM comparison failed. Exit 2: execution/input failure.
    Failed runs also publish their available reports, replacing stale evidence.
    """
    source = Path(source).expanduser().resolve()
    if source.suffix.casefold() not in {'.json', '.mpd', '.ldr'}:
        raise ValueError('Review expects a JSON plan or an MPD/LDR assembly')
    if colour is not None and section is None:
        raise ValueError('--colour requires --section')
    if source.suffix.casefold() == '.json' and section is not None:
        raise ValueError('Build the plan first to review an individual --section of its MPD')
    if not views or len(set(views)) != len(views) or any(v not in
            {'home', 'top', 'front', 'back', 'left', 'right', 'bottom'} for v in views):
        raise ValueError('Choose distinct supported viewpoints')
    if geometry_options.get('offset', 0) < 0:
        raise ValueError('--offset must be nonnegative')
    outdir = Path(outdir or source.with_name(model_name(source) + '-review')).expanduser()
    if outdir.is_symlink():
        raise ValueError('Review output must not be a symlink')
    outdir = outdir.resolve()
    check_destination(outdir, source, force)
    source_hash = sha256(source)
    outdir.parent.mkdir(parents=True, exist_ok=True)
    geometry_options.setdefault('detail', 'summary')
    report = dict(format='ldraw-nova-review', version=1,
                  source=dict(path=str(source), sha256=source_hash, section=section, colour=colour),
                  output=str(outdir), checks_passed=False, physical_validity='not_proven',
                  visual_review='not_rendered', model_sha256=None,
                  stages=dict(validation='not_run', bom='not_run', render='not_run', bom_comparison='not_run'),
                  artifacts={})
    status = 2
    with TemporaryDirectory(prefix='.review-', dir=outdir.parent) as temp:
        work = Path(temp) / 'bundle'
        work.mkdir()
        stage = 'validation'
        try:
            if source.suffix.casefold() == '.json':
                plan = load_plan(source)
                if sha256(source) != source_hash:
                    raise ValueError('Source changed while loading the plan; rerun on the saved revision')
                text, model, validation = build_checked(plan, parts, **geometry_options)
                model_bytes = text.encode('utf-8')
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
            atomic_write(work / 'validation.json', dumps(validation) + '\n')
            report['stages']['validation'] = 'passed' if validation['checks_passed'] else 'failed'
            report['diagnostics'] = validation['diagnostics']
            status = 1
            if validation['checks_passed']:
                model_path = work / 'model.mpd'
                model_path.write_bytes(model_bytes)
                report['model_sha256'] = sha256(model_path)
                stage = 'bom'
                physical, model_parts = physical_context(model, parts)
                bom = jsonable(physical.bill_of_materials(parts=model_parts))
                report['physical_placements'] = sum(row['quantity'] for row in bom)
                atomic_write(work / 'bom.json', dumps(dict(model_sha256=report['model_sha256'], bom=bom,
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
                    atomic_write(work / 'bom-comparison.json', dumps(comparison) + '\n')
                    report['stages']['bom_comparison'] = 'passed' if comparison['matches'] else 'failed'
                    status = 0 if comparison['matches'] else 1
                else:
                    report['stages'].update(render='skipped', bom_comparison='skipped')
                    status = 0
        except (OSError, ValueError, PartError, RecursionError, subprocess.SubprocessError, jsonschema.ValidationError) as exc:
            status = 2
            report['stages'][stage] = 'failed'
            report.update(error=str(exc), error_type=type(exc).__name__)
            if stage == 'render':
                shutil.rmtree(work / 'previews', ignore_errors=True)
        report.update(checks_passed=status == 0, exit_code=status)
        report['artifacts'] = {str(p.relative_to(work)): sha256(p) for p in sorted(work.rglob('*')) if p.is_file()}
        atomic_write(work / 'review.json', dumps(report) + '\n')
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
