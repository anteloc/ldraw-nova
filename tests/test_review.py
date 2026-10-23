"""The short workflow must preserve checks, provenance and failure semantics."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import mpd, ref
from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import atomic_write
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.workflow import review, sha256


@pytest.fixture
def source(tmp_path):
    path = tmp_path / 'brick.mpd'
    atomic_write(path, mpd(ref()))
    return path


@pytest.fixture
def plan(tmp_path):
    path = tmp_path / 'brick.plan.json'
    path.write_text(json.dumps(dict(version=1, author='Tests', sections=[dict(
        name='main.ldr', description='A brick', steps=[[dict(id='brick', ref='3001.dat', colour=4, at=[0, 0, 0])]])])))
    return path


@pytest.fixture
def renderer(monkeypatch):
    calls = []

    def render(path, library, outdir, *, views, **kwargs):
        calls.append(Path(path).read_bytes())
        outdir.mkdir(parents=True, exist_ok=True)
        images = []
        for view in views:
            image = outdir / (view + '.png')
            image.write_bytes(b'fixture image')
            images.append(str(image))
        bom = outdir / 'leocad-bom.csv'
        bom.write_text('Part ID,Color Code,Quantity\n3001.dat,4,1\n')
        return dict(images=images, bom=str(bom))

    monkeypatch.setattr('ldraw_tools.workflow.render', render)
    return calls


def test_plan_review_matches_existing_builder_and_geometry(plan, parts):
    expected, model, diagnostics = build_plan(load_plan(plan), parts)
    geometry = analyze_geometry(model, parts, detail='summary')
    report, status = review(plan, parts, parts.path.parent, renders=False)
    folder = Path(report['output'])
    assert folder.name == 'brick-review'
    assert status == 0 and report['checks_passed']
    assert (folder / 'model.mpd').read_bytes() == expected.encode()
    validation = json.loads((folder / 'validation.json').read_text())
    assert validation['diagnostics'] == diagnostics + geometry['diagnostics']
    assert validation['geometry'] == geometry
    assert report['stages']['render'] == report['stages']['bom_comparison'] == 'skipped'
    assert report['visual_review'] == 'not_rendered'
    assert report['physical_validity'] == 'not_proven'


def test_full_review_binds_all_outputs_to_exact_model(source, parts, renderer):
    original = source.read_bytes()
    report, status = review(source, parts, parts.path.parent)
    folder = Path(report['output'])
    assert status == 0 and all(value == 'passed' for value in report['stages'].values())
    assert source.read_bytes() == original == renderer[0] == (folder / 'model.mpd').read_bytes()
    assert report['source']['sha256'] == report['model_sha256'] == hashlib.sha256(original).hexdigest()
    assert report['physical_placements'] == 1
    assert report['visual_review'].startswith('required:')
    assert all(sha256(folder / name) == digest for name, digest in report['artifacts'].items())
    for name in ['validation.json', 'bom.json', 'bom-comparison.json']:
        assert json.loads((folder / name).read_text())['model_sha256'] == report['model_sha256']
    assert json.loads((folder / 'review.json').read_text()) == report


def test_failed_rebuild_replaces_old_success_without_stale_images(source, parts, renderer):
    first, _ = review(source, parts, parts.path.parent)
    atomic_write(source, mpd(ref() + '\n' + ref(position='10 0 0')))
    report, status = review(source, parts, parts.path.parent, force=True)
    folder = Path(first['output'])
    assert status == 1 and not report['checks_passed']
    assert report['stages']['validation'] == 'failed'
    assert report['stages']['render'] == 'not_run'
    assert not (folder / 'model.mpd').exists() and not (folder / 'previews').exists()
    assert any(d['code'] == 'assembly.body_overlap' for d in report['diagnostics'])
    assert len(renderer) == 1


def test_no_render_rerun_cannot_reuse_old_bom_comparison(source, parts, renderer):
    review(source, parts, parts.path.parent)
    report, status = review(source, parts, parts.path.parent, force=True, renders=False)
    assert status == 0
    assert not (Path(report['output']) / 'bom-comparison.json').exists()
    assert not (Path(report['output']) / 'previews').exists()
    assert report['stages']['bom_comparison'] == 'skipped'


def test_bom_difference_fails_review(source, parts, renderer):
    atomic_write(source, mpd(ref(colour=1)))
    report, status = review(source, parts, parts.path.parent)
    assert status == 1 and not report['checks_passed']
    assert report['stages']['render'] == 'passed'
    assert report['stages']['bom_comparison'] == 'failed'
    comparison = json.loads((Path(report['output']) / 'bom-comparison.json').read_text())
    assert not comparison['matches'] and len(comparison['differences']) == 2


def test_render_failure_keeps_diagnostics_and_removes_partial_previews(source, parts, monkeypatch):
    def fail(path, library, outdir, **kwargs):
        outdir.mkdir()
        (outdir / 'home.png').write_bytes(b'partial')
        raise subprocess.TimeoutExpired('leocad', 1)

    monkeypatch.setattr('ldraw_tools.workflow.render', fail)
    report, status = review(source, parts, parts.path.parent)
    assert status == 2 and not report['checks_passed']
    assert report['stages']['render'] == 'failed'
    assert report['stages']['bom_comparison'] == 'not_run'
    assert report['error_type'] == 'TimeoutExpired'
    folder = Path(report['output'])
    assert (folder / 'validation.json').exists() and (folder / 'bom.json').exists()
    assert not (folder / 'previews').exists()


def test_existing_output_requires_force_and_user_files_are_preserved(source, parts):
    report, _ = review(source, parts, parts.path.parent, renders=False)
    folder = Path(report['output'])
    with pytest.raises(ValueError, match='--force'):
        review(source, parts, parts.path.parent, renders=False)
    note = folder / 'my-notes.md'
    note.write_text('Keep my work')
    with pytest.raises(ValueError, match='user files'):
        review(source, parts, parts.path.parent, force=True, renders=False)
    assert note.read_text() == 'Keep my work'
    note.unlink()
    (folder / 'model.mpd').write_text('Edited by the user')
    with pytest.raises(ValueError, match='artifacts were edited'):
        review(source, parts, parts.path.parent, force=True, renders=False)
    assert (folder / 'model.mpd').read_text() == 'Edited by the user'


def test_review_cannot_replace_source_directory_or_follow_output_symlink(source, parts, tmp_path):
    with pytest.raises(ValueError, match='contain its input'):
        review(source, parts, parts.path.parent, outdir=source.parent, force=True)
    link = tmp_path / 'link'
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        review(source, parts, parts.path.parent, outdir=link, force=True)
    with pytest.raises(ValueError, match='contain its input'):
        review(source, parts, parts.path.parent, outdir=link / '..' / tmp_path.name, force=True)


def test_reviewed_section_resolves_colour_and_preserves_source_lines(source, parts):
    atomic_write(source, mpd(ref('child.ldr', colour=4)) + mpd(ref(colour=16), 'child.ldr'))
    report, status = review(source, parts, parts.path.parent, section='child.ldr', colour=1,
                            renders=False, detail='full')
    assert status == 0 and report['source']['section'] == 'child.ldr'
    folder = Path(report['output'])
    validation = json.loads((folder / 'validation.json').read_text())
    assert validation['geometry']['instances'][0]['line_number'] == 13
    bom = json.loads((folder / 'bom.json').read_text())['bom']
    assert len(bom) == 1 and bom[0]['colour_code'] == 1
    assert source.read_bytes() != (folder / 'model.mpd').read_bytes()


def test_embedded_dat_stays_one_physical_part(source, parts):
    atomic_write(source, mpd(ref('custom.dat')) + mpd(ref(), 'custom.dat').replace(
        '!LDRAW_ORG Model', '!LDRAW_ORG Unofficial_Part'))
    report, status = review(source, parts, parts.path.parent, renders=False)
    assert status == 0 and report['physical_placements'] == 1
    bom = json.loads((Path(report['output']) / 'bom.json').read_text())['bom']
    assert bom[0]['part'] == 'custom'


def test_invalid_plan_produces_failure_manifest_without_model(plan, parts):
    plan.write_text('{"version": 1}')
    report, status = review(plan, parts, parts.path.parent, renders=False)
    assert status == 2 and report['error_type'] == 'ValidationError'
    assert report['stages']['validation'] == 'failed'
    assert report['artifacts'] == {}
    assert (Path(report['output']) / 'review.json').exists()


def test_plan_includes_resolve_relative_to_plan(plan, parts, monkeypatch, tmp_path):
    child = tmp_path / 'child.json'
    child.write_bytes(plan.read_bytes())
    data = json.loads(plan.read_text())
    data['sections'][0].update(name='scene.ldr', steps=[[dict(id='child', ref='main.ldr', colour=4, at=[0, 0, 0])]])
    data['includes'] = ['child.json']
    plan.write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path.parent)
    report, status = review(plan, parts, parts.path.parent, renders=False)
    assert status == 0 and report['physical_placements'] == 1
    assert '0 FILE main.ldr' in (Path(report['output']) / 'model.mpd').read_text()


def test_instance_limit_remains_a_failure(source, parts):
    atomic_write(source, mpd(ref() + '\n' + ref(position='100 0 0')))
    report, status = review(source, parts, parts.path.parent, renders=False, instance_limit=1)
    assert status == 1 and not report['checks_passed']
    assert any(d['code'] == 'coverage.instance_budget' for d in report['diagnostics'])


def test_skipped_contacts_never_imply_connectivity(source, parts):
    report, status = review(source, parts, parts.path.parent, renders=False, contacts='none')
    assert status == 0
    validation = json.loads((Path(report['output']) / 'validation.json').read_text())
    assert not validation['geometry']['contacts_checked']
    assert validation['geometry']['optimistic_component_count'] is None
    assert any(d['code'] == 'coverage.contacts_skipped' for d in report['diagnostics'])


def test_source_edit_during_render_does_not_change_reviewed_snapshot(source, parts, monkeypatch, renderer):
    from ldraw_tools import workflow
    render = workflow.render
    original = source.read_bytes()

    def edit_then_render(*args, **kwargs):
        atomic_write(source, mpd(ref(colour=1)))
        return render(*args, **kwargs)

    monkeypatch.setattr(workflow, 'render', edit_then_render)
    report, status = review(source, parts, parts.path.parent)
    assert status == 0
    assert renderer[0] == original != source.read_bytes()
    assert report['source']['sha256'] == report['model_sha256'] == hashlib.sha256(original).hexdigest()


def test_plan_edit_during_load_cannot_attach_wrong_source_hash(plan, parts, monkeypatch):
    def changing_plan(path):
        loaded = load_plan(path)
        loaded['author'] = 'Changed while loading'
        path.write_text(json.dumps(loaded))
        return loaded

    monkeypatch.setattr('ldraw_tools.workflow.load_plan', changing_plan)
    report, status = review(plan, parts, parts.path.parent, renders=False)
    assert status == 2 and 'Source changed' in report['error']
    assert report['artifacts'] == {}


def test_failed_bundle_publication_restores_previous_review(source, parts, monkeypatch):
    first, _ = review(source, parts, parts.path.parent, renders=False)
    folder = Path(first['output'])
    previous = (folder / 'review.json').read_bytes()
    replace = Path.replace

    def fail_bundle(path, target):
        if path.name == 'bundle' and target == folder:
            raise OSError('Publication failed')
        return replace(path, target)

    monkeypatch.setattr(Path, 'replace', fail_bundle)
    with pytest.raises(OSError, match='Publication failed'):
        review(source, parts, parts.path.parent, force=True, renders=False)
    assert (folder / 'review.json').read_bytes() == previous
    assert all(sha256(folder / name) == digest for name, digest in first['artifacts'].items())


def test_cli_infers_build_path_and_keeps_explicit_output_compatible(plan, parts):
    command = [sys.executable, '-m', 'ldraw_tools.cli', '--library', str(parts.path.parent), '--no-shadow']
    result = subprocess.run(command + ['build', str(plan)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    target = plan.with_name('brick.mpd')
    assert json.loads(result.stdout)['output'] == str(target)
    expected = target.read_bytes()
    explicit = plan.with_name('explicit.mpd')
    result = subprocess.run(command + ['build', str(plan), '--output', str(explicit)], capture_output=True, text=True)
    assert result.returncode == 0 and explicit.read_bytes() == expected
    result = subprocess.run(command + ['build', str(plan)], capture_output=True, text=True)
    assert result.returncode == 2 and target.read_bytes() == expected
    result = subprocess.run(command + ['review', str(plan), '--no-render'], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)['physical_placements'] == 1


@pytest.mark.parametrize('kind,notes_option', [('manual', '--notes'), ('mechanism', '--operation')])
def test_shared_manual_cli_keeps_notes_and_study_kind(kind, notes_option, source, parts, monkeypatch, tmp_path):
    from ldraw_tools import cli
    captured = {}

    def prepare(*args, **kwargs):
        captured.update(kwargs)
        return dict(source_checks_passed=True, bom_matches=None)

    monkeypatch.setattr(cli, 'get_parts', lambda *args, **kwargs: parts)
    monkeypatch.setattr('ldraw_tools.manuals.prepare_manual', prepare)
    notes = tmp_path / 'notes.json'
    notes.write_text('{"lesson": "fixture"}')
    args = cli.parser().parse_args(['--library', str(parts.path.parent), kind, 'prepare', str(source),
                                   '--section', 'main.ldr', '--outdir', str(tmp_path / 'manual'), notes_option, str(notes), '--no-render'])
    _, status = cli.run(args)
    assert status == 0 and captured['notes'] == {'lesson': 'fixture'}
    assert captured['kind'] == ('construction' if kind == 'manual' else 'mechanism')
    assert not captured['renders'] and not captured['overview']


@pytest.mark.parametrize('explicit_output', [False, True])
def test_build_palette_preserves_checked_workflow_and_existing_output(plan, parts, explicit_output):
    from ldraw_tools import cli
    from ldraw_tools.parts_catalog import PartsUnavailable

    palette = plan.with_name('palette.csv')
    palette.write_text('part_id,color_id,max_quantity\n3001,4,1\n')
    target = plan.with_name('explicit.mpd' if explicit_output else 'brick.mpd')
    command = ['--library', str(parts.path.parent), '--no-shadow', 'build', str(plan),
               '--parts-palette', str(palette), '--force']
    if explicit_output:
        command += ['--output', str(target)]
    args = cli.parser().parse_args(command)
    report, status = cli.run(args)
    assert status == 0 and report['written'] and report['checks_passed']
    assert report['geometry'] is not None
    assert report['parts_palette'] == dict(valid=True, allowed_combinations=1, physical_parts=1)
    original = target.read_bytes()

    palette.write_text('part_id,color_id,max_quantity\n3001,0,1\n')
    with pytest.raises(PartsUnavailable):
        cli.run(args)
    assert target.read_bytes() == original

    palette.write_text('part_id,color_id,max_quantity\n3001,4,1\n')
    content = json.loads(plan.read_text())
    content['sections'][0]['steps'][0].append(dict(id='extra', ref='3001.dat', colour=4, at=[100, 0, 0]))
    plan.write_text(json.dumps(content))
    with pytest.raises(PartsUnavailable):
        cli.run(args)
    assert target.read_bytes() == original

    content['sections'][0]['steps'][0][1]['at'] = [10, 0, 0]
    plan.write_text(json.dumps(content))
    report, status = cli.run(args)
    assert status == 1 and not report['written']
    assert any(d['code'] == 'assembly.body_overlap' for d in report['diagnostics'])
    assert target.read_bytes() == original
