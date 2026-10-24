"""One-command authoring must preserve the old geometry and all required checks."""
import json
from pathlib import Path

import jsonschema
import pytest

from ldraw_tools.builder import build_plan, check_schema, load_plan
from ldraw_tools.cli import parser, run
from ldraw_tools.common import ROOT
from ldraw_tools.workflow import build_checked, review


def assembly(ref='route.ldr'):
    return dict(version=1, author='Tests', sections=[dict(name='scene.ldr', description='Assembly',
        steps=[[dict(id='part', ref=ref, colour=4, at=[0, 0, 0])]])])


@pytest.fixture
def flex_env(tmp_path, monkeypatch):
    pytest.importorskip('lsynth_nova')
    from ldraw_tools import flex, flex_workflow
    monkeypatch.setattr(flex, 'CACHE', tmp_path / 'cache')
    monkeypatch.setattr(flex_workflow, 'CACHE', tmp_path / 'cache')
    source = tmp_path / 'route.ldr'
    source.write_bytes((ROOT / 'examples/flex/hose.ldr').read_bytes())
    calls = []
    original = flex.subprocess.run

    def synthesize(*args, **kwargs):
        calls.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(flex.subprocess, 'run', synthesize)
    return source, tmp_path / 'route.mpd', calls


def test_plan_resolves_generated_sources_and_contracts_from_each_include(tmp_path):
    nested = tmp_path / 'nested'
    nested.mkdir()
    child = assembly('3001.dat')
    child['sections'][0].update(name='child.ldr', structure='frame.structure.json')
    child['assets'] = [dict(source='route.ldr', namespace='route', checks={'obstacles': 'frame.mpd'})]
    (nested / 'child.json').write_text(json.dumps(child))
    root = assembly('child.ldr')
    root['includes'] = ['nested/child.json']
    path = tmp_path / 'root.json'
    path.write_text(json.dumps(root))
    result = load_plan(path)
    assert result['assets'][0]['source'] == str(nested / 'route.ldr')
    assert result['assets'][0]['checks']['obstacles'] == str(nested / 'frame.mpd')
    assert result['sections'][1]['structure'] == str(nested / 'frame.structure.json')


@pytest.mark.parametrize('asset', [
    {'source': 'hose.ldr'}, {'source': 'hose.ldr', 'namespace': '../escape'},
    {'source': 'hose.ldr', 'namespace': 'hose', 'checks': {'min_raduis': 15}},
    {'source': 'hose.ldr', 'namespace': 'hose', 'checks': {'tube_radius': 0}},
])
def test_generated_asset_schema_rejects_ambiguous_or_misspelled_options(asset):
    plan = assembly()
    plan['assets'] = [asset]
    with pytest.raises(jsonschema.ValidationError):
        check_schema(plan)


def test_flex_build_checks_before_synthesis_and_keeps_previous_files(flex_env, official):
    from ldraw_tools.flex_workflow import build
    source, output, calls = flex_env
    build(source, output, official)
    old = output.read_bytes(), output.with_suffix('.manifest.json').read_bytes()
    # The old lightweight preflight accepted duplicate markers.
    source.write_text('0 SYNTH BEGIN TECHNIC_PNEUMATIC_HOSE_BEVELED 4\n' +
                      '1 4 0 0 0 1 0 0 0 1 0 0 0 1 LS01.dat\n' * 2 + '0 SYNTH END\n')
    with pytest.raises(ValueError, match='coincident_markers'):
        build(source, output, official, force=True)
    assert len(calls) == 1
    assert (output.read_bytes(), output.with_suffix('.manifest.json').read_bytes()) == old


def test_cache_reuses_only_synthesis_and_rechecks_tighter_limits(flex_env, official):
    from ldraw_tools.flex_workflow import build
    source, output, calls = flex_env
    first = build(source, output, official)
    raw = output.read_bytes()
    second = build(source, output, official, force=True)
    old_manifest = output.with_suffix('.manifest.json').read_bytes()
    assert not first['cache_hit'] and second['cache_hit'] and len(calls) == 1
    assert output.read_bytes() == raw
    with pytest.raises(ValueError, match='flex.length'):
        build(source, output, official, force=True, checks={'length': 1})
    assert len(calls) == 1
    assert output.read_bytes() == raw and output.with_suffix('.manifest.json').read_bytes() == old_manifest
    build(source, output, official, force=True, cache=False)
    assert len(calls) == 2


def test_cache_invalidation_and_corruption(flex_env, official, monkeypatch):
    from ldraw_tools import flex
    from ldraw_tools.flex_workflow import build
    source, output, calls = flex_env
    first = build(source, output, official)
    cache = flex.CACHE / 'flex-synthesis' / (first['synthesis_key'] + '.json')
    cache.write_text('{broken')
    assert not build(source, output, official, force=True)['cache_hit']
    source.write_text(source.read_text() + '0 Edited constraints\n')
    changed = build(source, output, official, force=True)
    assert changed['synthesis_key'] != first['synthesis_key'] and len(calls) == 3
    # A config edit must invalidate even in an already-running Python process.
    cfg, config, bundled = flex.engine()
    altered = source.parent / 'lsynth.mpd'
    altered.write_bytes(config.read_bytes() + b'\n0 Changed configuration\n')
    monkeypatch.setattr(flex, 'engine', lambda: (cfg, altered, bundled))
    from ldraw_tools import flex_review, flex_constraints
    monkeypatch.setattr(flex_review, 'engine', flex.engine)
    monkeypatch.setattr(flex_constraints, 'engine', flex.engine)
    revised = build(source, output, official, force=True)
    assert revised['synthesis_key'] != changed['synthesis_key'] and len(calls) == 4


def test_cached_synthesis_does_not_bypass_library_validation(flex_env, official, monkeypatch):
    from ldraw_tools import flex
    from ldraw_tools.flex_workflow import build
    source, output, calls = flex_env
    build(source, output, official)
    raw = output.read_bytes()
    monkeypatch.setattr(flex, 'validate_text', lambda *a, **k: (None, [
        dict(severity='error', code='missing.part', message='Library changed')]))
    with pytest.raises(ValueError, match='Library changed'):
        build(source, output, official, force=True)
    assert len(calls) == 1 and output.read_bytes() == raw


@pytest.mark.parametrize('name', ['hose', 'band', 'chain'])
def test_declared_flex_matches_existing_builder(flex_env, official, name):
    from ldraw_tools.flex import build
    source, output, _ = flex_env
    source.write_bytes((ROOT / f'examples/flex/{name}.ldr').read_bytes())
    build(source, output, official, namespace='route')
    legacy = assembly()
    legacy['assets'] = [str(output)]
    expected = build_plan(legacy, official)[0]
    automatic = assembly()
    automatic['assets'] = [dict(source=str(source), namespace='route')]
    text, _, checked = build_checked(automatic, official, contacts='none')
    assert text == expected and checked['checks_passed']
    assert checked['flex'][0]['validation']['measurements']


def test_review_freezes_constraints_and_flex_evidence(flex_env, official):
    source, _, _ = flex_env
    plan = assembly()
    plan['assets'] = [dict(source=source.name, namespace='route')]
    path = source.with_suffix('.plan.json')
    path.write_text(json.dumps(plan))
    result, status = review(path, official, official.path.parent, renders=False, contacts='none')
    folder = Path(result['output'])
    assert status == 0
    assert (folder / 'flex/1/constraints.ldr').read_bytes() == source.read_bytes()
    validation = json.loads((folder / 'validation.json').read_text())
    assert validation['flex'][0]['checks_passed']
    assert 'flex/1/asset.mpd' in result['artifacts']
    source.write_text('broken source')
    failed, status = review(path, official, official.path.parent, force=True, renders=False)
    assert status != 0 and not failed['checks_passed']
    assert not (folder / 'model.mpd').exists()


def test_press_automatic_assets_keep_reviewed_model_byte_for_byte(flex_env, official):
    plan = load_plan(ROOT / 'examples/flex/pneumatic-press/press.plan.json')
    plan['assets'] = [dict(source=str(ROOT / 'examples/flex/pneumatic-press/hoses.ldr'),
                          namespace='press-hoses', checks=dict(min_radius=15, min_separation=10))]
    text, _, report = build_checked(plan, official, contacts='none')
    assert report['checks_passed']
    assert text.encode() == (ROOT / 'examples/flex/pneumatic-press/press.mpd').read_bytes()


def test_technic_export_reviews_contract_automatically(tmp_path, official, monkeypatch):
    monkeypatch.setattr('ldraw_tools.cli.get_parts', lambda *a, **k: official)
    path = tmp_path / 'frame.plan.json'
    result, status = run(parser().parse_args(['technic', 'plan', 'box-chassis', '--output', str(path)]))
    assert status == 0
    plan = load_plan(path)
    assert plan['sections'][0]['structure'] == str(Path(result['contract']).resolve())
    reviewed, status = review(path, official, official.path.parent, renders=False, contacts='none')
    assert status == 0
    validation = json.loads((Path(reviewed['output']) / 'validation.json').read_text())
    assert validation['structure']['box-chassis.ldr']['checks_passed']
    assert 'structure/1.json' in reviewed['artifacts']
    # Required mounts are checked even when generic contacts are disabled.
    contract = json.loads(Path(result['contract']).read_text())
    contract.pop('model_sha256')
    contract['required_joints'].append({'between': [0, 1], 'minimum': 100})
    Path(result['contract']).write_text(json.dumps(contract))
    _, _, failed = build_checked(load_plan(path), official, contacts='none')
    assert not failed['checks_passed']
    assert any(d['code'] == 'technic.missing_required_joint' for d in failed['diagnostics'])


def test_stale_automatic_contract_is_never_ignored(tmp_path, official):
    from ldraw_tools.technic_recipes import structure_plan
    plan, contract = structure_plan('box-chassis')
    contract['model_sha256'] = '0' * 64
    target = tmp_path / 'contract.json'
    target.write_text(json.dumps(contract))
    plan['sections'][0]['structure'] = str(target)
    with pytest.raises(ValueError, match='different model revision'):
        build_checked(plan, official, contacts='none')


def test_automatic_contract_hash_keeps_embedded_part_definitions(tmp_path, parts):
    import hashlib
    from conftest import mpd, ref
    asset = tmp_path / 'embedded.mpd'
    asset.write_text(mpd(ref(part='local.dat')).replace('0 NOFILE',
        '0 FILE local.dat\n0 Embedded brick\n0 Name: local.dat\n0 !LDRAW_ORG Unofficial_Part\n' + ref() + '\n0 NOFILE'))
    plan = assembly('main.ldr')
    plan['assets'] = [str(asset)]
    _, model, _ = build_plan(plan, parts)
    contract = tmp_path / 'contract.json'
    contract.write_text(json.dumps(dict(version=1, model_sha256=hashlib.sha256(model.to_ldraw().encode()).hexdigest())))
    plan['sections'][0]['structure'] = str(contract)
    _, _, checked = build_checked(plan, parts, contacts='none')
    assert checked['structure']['scene.ldr']['checks_passed']


def test_flex_cli_infers_output_and_supports_checked_limits(flex_env, official, monkeypatch):
    source, output, calls = flex_env
    monkeypatch.setattr('ldraw_tools.cli.get_parts', lambda *a, **k: official)
    result, status = run(parser().parse_args(['flex', 'build', str(source)]))
    assert status == 0 and result['output'] == str(output)
    assert result['checks_passed'] and len(calls) == 1


def test_included_structure_uses_its_own_occurrence_indices(tmp_path, official):
    import hashlib
    from ldraw_tools.technic_recipes import structure_plan
    child, contract = structure_plan('box-chassis')
    _, model, _ = build_plan(child, official)
    contract['model_sha256'] = hashlib.sha256(model.to_ldraw().encode()).hexdigest()
    child['sections'][0]['structure'] = 'joints.json'
    (tmp_path / 'child.json').write_text(json.dumps(child))
    (tmp_path / 'joints.json').write_text(json.dumps(contract))
    root = assembly('box-chassis.ldr')
    root['includes'] = ['child.json']
    root['sections'][0]['steps'][0].insert(0, dict(id='unrelated', ref='3001.dat', colour=4, at=[500, 0, 0]))
    (tmp_path / 'root.json').write_text(json.dumps(root))
    _, _, report = build_checked(load_plan(tmp_path / 'root.json'), official, contacts='none')
    assert report['checks_passed']
    assert report['structure']['box-chassis.ldr']['joint_count'] == 24


def test_source_edit_during_measurement_prevents_publication(flex_env, official, monkeypatch):
    from ldraw_tools import flex_workflow
    source, output, _ = flex_env
    original = flex_workflow.check_asset

    def edited(*args, **kwargs):
        report = original(*args, **kwargs)
        source.write_text(source.read_text() + '0 Edited during measurement\n')
        return report

    monkeypatch.setattr(flex_workflow, 'check_asset', edited)
    with pytest.raises(ValueError, match='changed during review'):
        flex_workflow.build(source, output, official)
    assert not output.exists()


@pytest.mark.parametrize('existing', [False, True])
def test_flex_publication_rolls_back_if_manifest_cannot_be_replaced(flex_env, official, monkeypatch, existing):
    from ldraw_tools.flex_workflow import build
    source, output, _ = flex_env
    manifest = output.with_suffix('.manifest.json')
    if existing:
        build(source, output, official)
        previous = output.read_bytes(), manifest.read_bytes()
    original = Path.replace

    def fail_manifest(path, target):
        if Path(target) == manifest:
            raise OSError('Simulated manifest write failure')
        return original(path, target)

    monkeypatch.setattr(Path, 'replace', fail_manifest)
    with pytest.raises(OSError, match='Simulated'):
        build(source, output, official, force=True)
    if existing:
        assert (output.read_bytes(), manifest.read_bytes()) == previous
    else:
        assert not output.exists() and not manifest.exists()
