"""Authoring intent must survive edits, nesting, and failed prerequisites."""
import json

import pytest

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.identity import BuildError
from ldraw_tools.technic_recipes import structure_plan
from ldraw_tools.workflow import build_checked, review


def named_frame():
    plan, contract = structure_plan('box-chassis')
    ids = [p['id'] for step in plan['sections'][0]['steps'] for p in step]
    for joint in contract['required_joints']:
        joint['between'] = [ids[i] for i in joint['between']]
    for step in contract['assembly']:
        step['connector'] = ids[step['connector']]
        step['before'] = [ids[i] for i in step['before']]
    plan['sections'][0]['structure'] = contract
    return plan


def test_named_contract_reordering_and_missing_joint(official):
    plan = named_frame()
    _, _, first = build_checked(plan, official)
    assert first['checks_passed']
    for step in plan['sections'][0]['steps']:
        step.reverse()
    _, _, reordered = build_checked(plan, official)
    assert reordered['checks_passed']
    entries = [p for step in plan['sections'][0]['steps'] for p in step]
    pin = next(p for p in entries if p['id'].startswith('pin-'))
    pin['at'][0] += 500
    _, _, broken = build_checked(plan, official)
    failure = next(d for d in broken['diagnostics'] if d['code'] == 'technic.missing_required_joint')
    assert pin['id'] in [p['path'] for p in failure['placements']]
    assert broken['failed_stage'] == 'structure'
    assert failure['observed_contacts'] < failure['required_contacts']


def test_identity_nested_repeated_and_include_provenance(tmp_path, parts):
    child = dict(version=1, author='Child', sections=[dict(name='child.ldr', description='Child', steps=[[
        dict(id='brick', ref='3003.dat', colour=4, at=[0, 0, 0], repeat=dict(count=2, step=[60, 0, 0]))]])])
    root = dict(version=1, author='Root', includes=['child.json'], sections=[dict(name='root.ldr',
        description='Root', steps=[[dict(id='module', ref='child.ldr', colour=4, at=[100, 0, 0])]])])
    (tmp_path / 'child.json').write_text(json.dumps(child))
    path = tmp_path / 'root.json'
    path.write_text(json.dumps(root))
    _, _, report = build_checked(load_plan(path), parts)
    assert [r['path'] for r in report['source_map']] == ['module/brick-0', 'module/brick-1']
    assert report['source_map'][1]['position'] == [160, 0, 0]
    origin = report['source_map'][1]['sources'][-1]
    assert origin['file'] == str(tmp_path / 'child.json')
    assert origin['pointer'] == '/sections/0/steps/0/0'


def test_bad_placement_preserves_source_identity(tmp_path, parts):
    plan = dict(version=1, author='Test', sections=[dict(name='bad.ldr', description='Bad', steps=[[
        dict(id='missing', ref='unknown.dat', colour=4, at=[0, 0, 0])]])])
    path = tmp_path / 'bad.json'
    path.write_text(json.dumps(plan))
    with pytest.raises(BuildError) as failed:
        build_plan(load_plan(path), parts)
    assert failed.value.diagnostics[0]['placement'] == 'missing'
    result, status = review(path, parts, parts.path.parent, renders=False)
    assert status == 2 and not result['checks_passed']
    assert result['diagnostics'][0]['file'] == str(path)
    assert json.loads((tmp_path / 'bad-review/validation.json').read_text())['geometry'] is None


def test_scoped_plan_omits_unrelated_errors_and_marks_coverage(tmp_path, official):
    plan = named_frame()
    plan['sections'].insert(0, dict(name='scene.ldr', description='Scene', steps=[[
        dict(id='frame', ref='box-chassis.ldr', colour=4, at=[0, 0, 0]),
        dict(id='bad', ref='missing.dat', colour=4, at=[0, 0, 0])]]))
    path = tmp_path / 'scene.json'
    path.write_text(json.dumps(plan))
    result, status = review(path, official, official.path.parent, section='box-chassis.ldr', renders=False)
    assert status == 0
    assert result['coverage'] == dict(scope='section', section='box-chassis.ldr', final_model_review=False)
    assert 'box-chassis.ldr' in json.loads((tmp_path / 'scene-box-chassis-review/validation.json').read_text())['structure']
    whole, status = review(path, official, official.path.parent, renders=False)
    assert status == 2 and not whole['checks_passed']


def test_named_contract_never_accepts_absent_or_module_path(official):
    plan = named_frame()
    plan['sections'][0]['structure']['required_joints'][0]['between'][0] = 'absent'
    with pytest.raises(BuildError, match='absent'):
        build_checked(plan, official)


def test_joints_scope_does_not_claim_rigidity(official):
    plan = named_frame()
    contract = plan['sections'][0]['structure']
    contract.update(scope='joints', require_rigid=False)
    _, _, report = build_checked(plan, official)
    result = report['structure']['box-chassis.ldr']
    assert result['checks_passed'] and result['scope'] == 'technic-joints'
    assert result['restrained_groups'] == []


def route_plan():
    return dict(version=1, author='Tests', sections=[dict(name='route.ldr', description='Named port fixture', steps=[[
        dict(id='pump', ref='2797c01-f1.dat', colour=7, at=[0, 0, 0]),
        dict(id='other', ref='2797c01-f1.dat', colour=7, at=[0, 0, -160], yaw=180),
    ], [dict(id='hose', colour=4, flex=dict(method='TECHNIC_PNEUMATIC_HOSE_BEVELED',
        **{'from': dict(part='pump', port='outlet', lead=22),
           'to': dict(part='other', port='outlet', lead=22)}, checks=dict(min_radius=15, tube_radius=5)))]] )])


def test_inline_flex_named_ports_move_with_nested_parts(official):
    from ldraw_tools.builder import rotation
    plan = route_plan()
    _, _, first = build_checked(plan, official, contacts='none')
    assert first['checks_passed']
    assert len(first['source_map']) == 3
    plan['sections'].insert(0, dict(name='assembly.ldr', description='Transformed route', steps=[[
        dict(id='unit', ref='route.ldr', colour=7, at=[200, 100, 30], matrix=rotation('x', 90).rows)]]))
    _, _, moved = build_checked(plan, official, contacts='none')
    assert moved['checks_passed']
    assert moved['flex'][0]['cache_hit']
    assert moved['source_map'][-1]['inline_route']['path'] == 'unit/hose'
    assert moved['flex_interactions']['coverage']['obstacles_checked'] == ['unit/hose']


def test_inline_wheels_owned_once_and_rigid_links_counted(official):
    plan = dict(version=1, author='Tests', sections=[dict(name='chain.ldr', description='Chain fixture', steps=[[
        dict(id='drive', ref='4019.dat', colour=7, at=[-60, 0, 0]),
        dict(id='idler', ref='4019.dat', colour=7, at=[60, 0, 0]),
    ], [dict(id='chain', colour=14, flex=dict(method='TECHNIC_CHAIN_LINK', wheels=['drive', 'idler']))]])])
    _, _, report = build_checked(plan, official, contacts='none')
    assert report['checks_passed']
    assert len(report['source_map']) == 26
    assert sum(r['part'] == '4019.dat' for r in report['source_map']) == 2
    assert len({r['path'] for r in report['source_map']}) == 26
    plan['sections'][0]['steps'][0][1]['at'][2] = 10
    with pytest.raises(BuildError) as failed:
        build_checked(plan, official, contacts='none')
    assert any('plane' in d['code'] for d in failed.value.diagnostics)


def test_routes_in_repeated_modules_are_compared_in_assembly_frame(official):
    plan = route_plan()
    plan['sections'].insert(0, dict(name='pair.ldr', description='Nearly overlapping hoses', steps=[[
        dict(id='left', ref='route.ldr', colour=7, at=[0, 0, 0]),
        dict(id='right', ref='route.ldr', colour=7, at=[6, 0, 0]),
    ]]))
    _, _, report = build_checked(plan, official, contacts='none')
    assert not report['checks_passed']
    failed = next(d for d in report['diagnostics'] if d['code'] == 'flex.separation')
    assert failed['routes'] == ['left/hose', 'right/hose']
    assert [p['path'] for p in failed['placements']] == failed['routes']
    assert all(p['pointer'] == '/sections/1/steps/1/0' for p in failed['placements'])
    assert failed['distance_ldu'] < failed['required_ldu']
    assert report['failed_stage'] == 'flex.interactions'


def test_flex_failure_retains_route_and_measurements(tmp_path, official):
    plan = route_plan()
    plan['sections'][0]['steps'][1][0]['flex']['checks']['length'] = 1
    path = tmp_path / 'route.json'
    path.write_text(json.dumps(plan))
    result, status = review(path, official, official.path.parent, renders=False)
    assert status == 2 and not result['checks_passed']
    diagnostic = next(d for d in result['diagnostics'] if d['code'] == 'flex.length')
    assert diagnostic['placement'] == 'hose'
    assert diagnostic['pointer'] == '/sections/0/steps/1/0'


def test_rigid_cannot_depend_on_generated_route(official):
    plan = route_plan()
    plan['sections'][0]['steps'].append([dict(id='brick', ref='3003.dat', colour=4, on='hose')])
    with pytest.raises(BuildError, match='cannot depend'):
        build_checked(plan, official)


def test_changed_named_port_geometry_fails(official, monkeypatch):
    from dataclasses import replace
    from ldraw_tools.flex_plan import ports
    original = official.geometry
    monkeypatch.setattr(official, 'geometry', lambda code: replace(original(code), points=original(code).points[1:]))
    with pytest.raises(ValueError, match='different geometry revision'):
        ports(official, '2797c01-f1.dat')


def test_named_press_preserves_rigid_geometry_and_closes_mount_gaps(official):
    from ldraw_tools.common import ROOT
    original = load_plan(ROOT / 'examples/flex/pneumatic-press/press.plan.json')
    named = load_plan(ROOT / 'examples/flex/pneumatic-press/named.plan.json')
    _, _, before = build_checked(original, official)
    _, _, after = build_checked(named, official)
    assert before['checks_passed'] and after['checks_passed']
    def rigid(report):
        return [(r['part'], r['position'], r['matrix']) for r in report['source_map']
                if not r.get('inline_route') and not r['part'].startswith('press-hoses-')]
    assert rigid(before) == rigid(after)
    assert len(after['source_map']) == len(before['source_map']) == 41
    assert after['flex_interactions']['coverage']['measured_pairs'] == 3
    # Displacing the real pump fails a declared mount; matching hose markers
    # alone cannot make an unmounted pump pass.
    pump = named['sections'][-1]['steps'][0][0]
    assert pump['id'] == 'pump'
    pump['at'][1] -= 8
    named['sections'][0]['steps'] = named['sections'][0]['steps'][:4]
    _, _, bad = build_checked(named, official)
    assert any(d['code'] == 'technic.missing_required_joint' for d in bad['diagnostics'])


def test_workshop_recipes_and_retention_failure(official):
    from ldraw_tools.workshop import chain_drive, workshop_plan
    for plan in [chain_drive(), workshop_plan()]:
        _, _, report = build_checked(plan, official, contacts='all')
        assert report['checks_passed'], [d for d in report['diagnostics'] if d['severity'] == 'error']
    chain = chain_drive()
    stop = next(p for step in chain['sections'][0]['steps'] for p in step if p['id'] == 'crank-stop')
    stop['at'][2] += 40
    _, _, report = build_checked(chain, official)
    assert not report['checks_passed']
    assert any(d['code'] == 'technic.missing_required_joint' for d in report['diagnostics'])
    # This bush still engages the axle but no longer touches the bearing.
    chain = chain_drive()
    stop = next(p for step in chain['sections'][0]['steps'] for p in step if p['id'] == 'drive-stop--60')
    stop['at'][2] -= 5
    _, _, report = build_checked(chain, official)
    assert any(d['code'] == 'technic.axial_retention' and d['severity'] == 'error' for d in report['diagnostics'])


def test_inline_schema_rejects_mixed_position_and_endpoint_modes():
    from ldraw_tools.builder import check_schema
    import jsonschema
    plan = route_plan()
    entry = plan['sections'][0]['steps'][1][0]
    entry['at'] = [0, 0, 0]
    with pytest.raises(jsonschema.ValidationError):
        check_schema(plan)
    entry.pop('at')
    entry['flex']['from']['feature'] = 'ambiguous'
    with pytest.raises(jsonschema.ValidationError):
        check_schema(plan)


def test_rigid_errors_prevent_inline_synthesis(official, monkeypatch):
    from ldraw_tools import flex_plan
    plan = route_plan()
    plan['sections'][0]['steps'][0][0]['matrix'] = [[2, 0, 0], [0, 1, 0], [0, 0, 1]]
    monkeypatch.setattr(flex_plan, 'prepare_inline', lambda *a, **k: pytest.fail('Synthesis before rigid validation'))
    with pytest.raises(BuildError) as failed:
        build_checked(plan, official)
    assert failed.value.stage == 'rigid'
    assert any(p['path'] == 'pump' for d in failed.value.diagnostics for p in d.get('placements', []))


def test_included_schema_failure_keeps_actual_source(tmp_path, official):
    child = route_plan()
    child['sections'][0]['steps'][0][0]['at'] = [0, 0]
    (tmp_path / 'child.json').write_text(json.dumps(child))
    root = dict(version=1, author='Tests', includes=['child.json'], sections=[dict(
        name='root.ldr', description='Root', steps=[[dict(id='unit', ref='route.ldr', colour=4, at=[0, 0, 0])]])])
    path = tmp_path / 'root.json'
    path.write_text(json.dumps(root))
    result, status = review(path, official, official.path.parent, renders=False)
    assert status == 2 and result['failed_stage'] == 'schema'
    assert result['diagnostics'][0]['file'] == str(tmp_path / 'child.json')
    assert result['diagnostics'][0]['pointer'].startswith('/sections/0/steps/0/0')
    assert json.loads((tmp_path / 'root-review/validation.json').read_text())['geometry'] is None


def test_scoped_plan_skips_unneeded_flex_dependency(tmp_path, official):
    plan = named_frame()
    plan['assets'] = [dict(source='missing.ldr', namespace='missing')]
    plan['sections'].insert(0, dict(name='scene.ldr', description='Scene', steps=[[
        dict(id='frame', ref='box-chassis.ldr', colour=4, at=[0, 0, 0]),
        dict(id='unavailable', ref='missing.ldr', colour=4, at=[0, 0, 0])]]))
    path = tmp_path / 'scene.json'
    path.write_text(json.dumps(plan))
    result, status = review(path, official, official.path.parent, section='box-chassis.ldr', renders=False)
    assert status == 0 and not result['coverage']['final_model_review']


def test_inline_cache_rechecks_stricter_limits(official):
    plan = route_plan()
    _, _, first = build_checked(plan, official, contacts='none')
    assert first['checks_passed']
    plan['sections'][0]['steps'][1][0]['flex']['checks']['length'] = 1
    with pytest.raises(BuildError) as failed:
        build_checked(plan, official, contacts='none')
    assert failed.value.stage == 'flex.measurement'
    assert any(d['code'] == 'flex.length' for d in failed.value.diagnostics)


def test_inline_synthesis_failure_has_named_unavailable_evidence(official, monkeypatch):
    import subprocess
    from ldraw_tools import flex
    def fail(*args, **kwargs):
        raise subprocess.TimeoutExpired('lsynth', 1)
    monkeypatch.setattr(flex, 'build', fail)
    with pytest.raises(BuildError) as failed:
        build_checked(route_plan(), official, contacts='none')
    assert failed.value.stage == 'flex.synthesis'
    assert failed.value.diagnostics[0]['placement'] == 'hose'
    assert failed.value.diagnostics[0]['measurement'] == 'unavailable'


def test_drive_foundation_and_workshop_attachment_cannot_float(official):
    from ldraw_tools.workshop import chain_drive, workshop_plan
    # Regression from the independent trial: the rails can sit between the
    # plate's stud rows even though every shaft joint still seats correctly.
    drive = chain_drive()
    drive['sections'][0]['steps'][0][0]['at'][2] -= 10
    _, _, bad = build_checked(drive, official, contacts='all')
    failures = [d for d in bad['diagnostics'] if d['code'] == 'technic.missing_required_joint']
    assert any({'base', 'rail--40--24'} <= {p['path'] for p in d['placements']} for d in failures)
    # A correct internal drive still needs to engage the actual workbench.
    machine = workshop_plan()
    conveyor = next(p for step in machine['sections'][0]['steps'] for p in step if p['id'] == 'conveyor')
    conveyor['at'][2] -= 10
    _, _, bad = build_checked(machine, official, contacts='all')
    assert any(d['code'] == 'technic.missing_required_joint'
               and any(p['path'] == 'conveyor/base' for p in d['placements']) for d in bad['diagnostics'])
