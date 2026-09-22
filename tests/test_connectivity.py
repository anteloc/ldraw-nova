"""Shadow loading, actual mating poses, and occurrence-isolated assembly edits."""
import json
import subprocess
import sys
import zipfile

import numpy as np
import pytest
from ldraw import Parts, Model, Piece, Vector

from conftest import mpd, ref
from ldraw_tools.builder import build_plan, rotation, serialize_mpd
from ldraw_tools.common import ROOT, get_parts, jsonable, shadow_paths
from ldraw_tools.connectivity import (apply_snap, connection_report, inspect_connections,
                                      snap_report)
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.validation import validate_text


@pytest.fixture
def shadow(tmp_path):
    path = tmp_path / 'shadow'
    (path / 'parts').mkdir(parents=True)
    for code, height in [('3001', 24), ('3003', 24), ('3022', 8)]:
        (path / 'parts' / f'{code}.dat').write_text(
            '0 !LDCAD SNAP_CLEAR\n'
            '0 !LDCAD SNAP_CYL [id=top] [gender=M] [secs=R 6 4] [pos=10 0 10]\n'
            f'0 !LDCAD SNAP_CYL [id=bottom] [gender=F] [secs=R 6 4] [pos=10 {height} 10]\n')
    return path


@pytest.fixture
def connected(parts, shadow):
    catalog = Parts(parts.path)
    catalog.add_connection_shadow(shadow)
    return catalog


def model(parts, body):
    parsed, diagnostics = validate_text(mpd(body), parts)
    assert not [d for d in diagnostics if d['severity']=='error']
    return parsed


def pair(parts):
    return model(parts, ref()+'\n'+ref('3022.dat', position='0 -50 0'))


def test_shadow_defaults_and_explicit_disable(parts, shadow, monkeypatch):
    monkeypatch.setenv('LDRAW_SHADOW', str(shadow))
    assert shadow_paths() == [shadow]
    assert shadow_paths([]) == []
    loaded = get_parts(parts.path.parent)
    assert loaded.connection_metadata('3001').coverage == 'complete'
    assert get_parts(parts.path.parent, shadows=[]).connection_metadata('3001').coverage != 'complete'
    monkeypatch.setenv('LDRAW_SHADOW', str(shadow / 'missing'))
    with pytest.raises(ValueError, match='missing'):
        shadow_paths()
    assert shadow_paths([]) == []


@pytest.mark.parametrize('suffix', ['zip', 'csl'])
def test_archive_directory_parity(parts, shadow, tmp_path, suffix):
    archive = tmp_path / f'shadow.{suffix}'
    with zipfile.ZipFile(archive, 'w') as z:
        for path in shadow.rglob('*.dat'):
            z.write(path, path.relative_to(shadow))
    catalogs = [Parts(parts.path), Parts(parts.path)]
    for catalog, source in zip(catalogs, [shadow, archive]):
        catalog.add_connection_shadow(source)
    for catalog in catalogs:
        metadata = catalog.connection_metadata('3001')
        assert metadata.coverage == 'complete'
        assert [f.feature_id for f in metadata.features] == ['top', 'bottom']
        report = snap_report(pair(catalog), catalog, 1, 0, moving_feature='bottom', fixed_feature='top')
        assert report['candidates'][0]['local_placement']['at'] == [0, -8, 0]


def test_shadow_include_grid_clear_and_invalid_metadata(parts, shadow):
    (shadow/'parts'/'3001.dat').write_text(
        '0 !LDCAD SNAP_CLEAR\n0 !LDCAD SNAP_INCL [ref=3022.dat] [pos=20 0 0] [grid=2 1 20 20]\n')
    catalog = Parts(parts.path); catalog.add_connection_shadow(shadow)
    metadata = catalog.connection_metadata('3001')
    assert metadata.coverage == 'complete' and len(metadata.features) == 4
    assert sorted({f.position.x for f in metadata.features}) == [30, 50]
    (shadow/'parts'/'3001.dat').write_text('0 !LDCAD SNAP_CLEAR\n')
    catalog.clear_connection_shadows(); catalog.add_connection_shadow(shadow)
    assert catalog.connection_metadata('3001').coverage == 'complete'
    assert catalog.connections('3001') == ()
    (shadow/'parts'/'3001.dat').write_text('0 !LDCAD SNAP_CYL [secs=broken]\n')
    catalog.clear_connection_shadows(); catalog.add_connection_shadow(shadow)
    metadata = catalog.connection_metadata('3001')
    assert metadata.invalid_record_count and metadata.diagnostics and metadata.coverage == 'partial'


def test_snap_stacks_and_preserves_input(connected):
    original = pair(connected)
    before = original.to_ldraw()
    report = snap_report(original, connected, 1, 0, moving_feature='bottom', fixed_feature='top')
    candidate = report['candidates'][0]
    assert candidate['position'] == [0, -8, 0]
    assert np.allclose(candidate['matrix'], np.eye(3))
    assert candidate['contact_status'] == 'confirmed'
    assert candidate['collision']['status'] == 'no_collision_found'
    applied = apply_snap(original, report)
    assert original.to_ldraw() == before
    assert applied.pieces[1].position.y == -8
    contacts = connection_report(applied, connected, 1)
    assert contacts['metadata']['coverage'] == 'complete'
    assert any(f['contacts'] for f in contacts['connectors'])


@pytest.mark.parametrize('moving,fixed,depth', [(-1, 0, None), (99, 0, None), (1, -1, None),
                                             (1, 1, None), (1, 0, -1), (1, 0, 5)])
def test_invalid_occurrence_inputs_are_actionable(connected, moving, fixed, depth):
    with pytest.raises(ValueError):
        snap_report(pair(connected), connected, moving, fixed, moving_depth=depth)


def test_features_and_search_budget(connected):
    m = pair(connected)
    with pytest.raises(ValueError, match='feature ID'):
        snap_report(m, connected, 1, 0, moving_feature='missing')
    report = snap_report(m, connected, 1, 0, max_candidates=1)
    assert report['checked_candidates'] == 1 and report['search_truncated']


def test_occupied_fixed_interface_excluded(connected):
    m = model(connected, ref()+'\n'+ref('3022.dat', position='0 -8 0')+'\n'+ref('3003.dat', position='200 0 0'))
    report = snap_report(m, connected, 2, 0, moving_feature='bottom', fixed_feature='top')
    assert not report['candidates'] and report['rejected']['occupied_feature']
    report = snap_report(m, connected, 2, 0, moving_feature='bottom', fixed_feature='top', allow_occupied=True)
    assert report['candidates'][0]['collision']['status'] == 'blocked'
    with pytest.raises(ValueError, match='collision'):
        apply_snap(m, report)


def test_rotated_body_overlap_and_touch(connected):
    orient = rotation('z', 35)
    for y, collides in [(12, True), (24, False)]:
        m = Model.from_pieces([Piece.place('3001', colour=4, matrix=orient),
                              Piece.place('3003', colour=4, matrix=orient, position=orient*Vector(0, y, 0))], name='main.ldr')
        report = analyze_geometry(m, connected, contacts='none')
        assert any(d['code']=='assembly.body_overlap' for d in report['diagnostics']) is collides


def test_oriented_bounds_separate_aabb_false_positive(connected):
    from ldraw_tools.collision import collision_pairs
    orient = rotation('y', 45)
    m = Model.from_pieces([Piece.place('3001', colour=4, matrix=orient),
                          Piece.place('3001', colour=4, matrix=orient, position=orient*Vector(0, 0, 45))], name='main.ldr')
    pairs = list(collision_pairs(inspect_connections(m, connected), {}))
    assert len(pairs)==1 and pairs[0]['status']=='oriented_bounds_separated'


def nested(parts):
    text = mpd(ref()+'\n'+ref('unit.ldr', position='200 0 0', matrix='0 -1 0 1 0 0 0 0 1')+
               '\n'+ref('unit.ldr', position='400 0 0'))
    text += mpd(ref('3022.dat')+'\n'+ref('3003.dat', position='100 0 0'), 'unit.ldr')
    parsed, _ = validate_text(text, parts)
    return parsed


def test_submodel_rigid_move_checks_all_children(connected):
    m = nested(connected)
    report = snap_report(m, connected, 1, 0, moving_depth=0, moving_feature='bottom', fixed_feature='top')
    assert report['moving_instances'] == [1, 2] and report['placement_path'] == [1]
    applied = apply_snap(m, report)
    before, after = list(m.iter_occurrences()), list(applied.iter_occurrences())
    delta = report['candidates'][0]['delta']
    for index in [1, 2]:
        expected = np.array(delta['matrix'])@jsonable(before[index].position)+delta['position']
        assert np.allclose(jsonable(after[index].position), expected)
    assert jsonable(before[3].position)==jsonable(after[3].position)


def test_nested_leaf_clones_shared_ancestor_and_local_inverse(connected):
    m = nested(connected)
    before = list(m.iter_occurrences())
    report = snap_report(m, connected, 1, 0, moving_feature='bottom', fixed_feature='top')
    candidate = report['candidates'][0]
    applied = apply_snap(m, report)
    after = list(applied.iter_occurrences())
    assert np.allclose(jsonable(after[1].position), candidate['position'])
    assert candidate['position'] != candidate['local_placement']['at']
    for index in [0, 2, 3, 4]:
        assert jsonable(after[index].position)==jsonable(before[index].position)
    _, diagnostics = validate_text(serialize_mpd(applied), connected)
    assert not [d for d in diagnostics if d['severity']=='error']


def test_sibling_collision_blocks_submodel_candidate(connected):
    text = mpd(ref()+'\n'+ref('unit.ldr', position='200 0 0')+'\n'+ref('3001.dat', position='100 -8 0'))
    text += mpd(ref('3022.dat')+'\n'+ref('3003.dat', position='100 0 0'), 'unit.ldr')
    m, _ = validate_text(text, connected)
    report = snap_report(m, connected, 1, 0, moving_depth=0, moving_feature='bottom', fixed_feature='top')
    candidate = report['candidates'][0]
    assert candidate['collision']['status']=='blocked'
    assert any(set(p['instances'])=={2, 3} and p['status']=='rectangular_body_overlap'
               for p in candidate['collision']['pairs'])


def test_stale_snap_report_is_rejected(connected):
    m = pair(connected)
    report = snap_report(m, connected, 1, 0)
    m.pieces[0].position = Vector(1, 0, 0)
    with pytest.raises(ValueError, match='different model revision'):
        apply_snap(m, report)


def test_missing_geometry_and_expansion_limit_refuse_snap(connected):
    m, _ = validate_text(mpd(ref()+'\n'+ref('missing.dat')), connected, assembly=False)
    with pytest.raises(ValueError, match='incomplete'):
        snap_report(m, connected, 1, 0)
    with pytest.raises(ValueError, match='budget'):
        snap_report(pair(connected), connected, 1, 0, instance_limit=1)


def test_plan_snaps_module_and_builds_dependencies_first(connected):
    plan = dict(version=1, author='Tests', sections=[
        dict(name='main.ldr', description='Snap', steps=[[
            dict(id='base', ref='3001.dat', colour=4, at=[0, 0, 0]),
            dict(id='upper', ref='unit.ldr', colour=1, snap=dict(to='base', moving_feature='bottom', fixed_feature='top'))]]),
        dict(name='unit.ldr', description='Module', steps=[[
            dict(id='plate', ref='3022.dat', colour=16, at=[0, 0, 0])]])])
    text, m, diagnostics = build_plan(plan, connected)
    assert not diagnostics
    assert m.name=='main.ldr' and m.pieces[1].position.y == -8
    assert build_plan(plan, connected)[0] == text
    plan['sections'][0]['steps'][0][1]['snap']['to']='missing'
    with pytest.raises(ValueError, match='earlier'):
        build_plan(plan, connected)


def test_cli_applies_copy_and_reports_invalid_indices(connected, shadow, tmp_path):
    source, output = tmp_path/'source.mpd', tmp_path/'snapped.mpd'
    source.write_bytes(serialize_mpd(pair(connected)).encode())
    original = source.read_bytes()
    command = [sys.executable, '-m', 'ldraw_tools.cli', '--library', str(connected.path.parent),
               '--shadow', str(shadow), 'snap', str(source), '--moving', '1', '--fixed', '0',
               '--moving-feature', 'bottom', '--fixed-feature', 'top']
    result = subprocess.run([*command, '--output', str(output)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout+result.stderr
    assert json.loads(result.stdout)['written'] and source.read_bytes()==original
    assert output.exists()
    result = subprocess.run([*command, '--moving', '-1'], capture_output=True, text=True)
    assert result.returncode==2 and json.loads(result.stdout)['error_type']=='ValueError'


def test_real_shadow_square_socket_and_sideways_snap(official):
    m = Model.from_pieces([Piece.place('3005', colour=4, position=Vector(100, 0, 0), matrix=rotation('z', 90)),
                          Piece.place('3005', colour=1, position=Vector(100, -50, 0))], name='main.ldr')
    report = snap_report(m, official, 1, 0)
    candidate = report['candidates'][0]
    assert candidate['contact_status']=='potential'
    assert candidate['collision']['status'] != 'blocked'
    assert np.linalg.det(candidate['matrix']) == pytest.approx(1)
    applied = apply_snap(m, report)
    assert analyze_geometry(applied, official)['optimistic_component_count']==1


@pytest.mark.parametrize('moving,fixed,kinds', [('3705', '32064', ('axle', 'axle_hole')),
                                              ('30374', '4085c', ('bar', 'clip'))])
def test_real_technic_and_clip_interfaces(official, moving, fixed, kinds):
    m = Model.from_pieces([Piece.place(fixed, colour=4),
                          Piece.place(moving, colour=1, position=Vector(100, 0, 0))], name='main.ldr')
    report = snap_report(m, official, 1, 0)
    candidate = report['candidates'][0]
    assert (candidate['moving_feature']['kind'], candidate['fixed_feature']['kind']) == kinds
    assert candidate['contact_status']=='confirmed'
    # Real mating interfaces still require review of irregular solid geometry.
    assert candidate['collision']['status']=='review_required'


def test_real_primitive_snap_without_shadows(official):
    catalog = get_parts(shadows=[])
    m = Model.from_pieces([Piece.place('3001', colour=4),
                          Piece.place('3022', colour=1, position=Vector(0, -50, 0))], name='main.ldr')
    report = snap_report(m, catalog, 1, 0)
    assert report['candidates'] and report['candidates'][0]['contact_status']=='confirmed'
    assert report['metadata']['coverage']=='partial'


def test_supplied_snap_plan(official):
    from ldraw_tools.builder import load_plan
    _, m, diagnostics = build_plan(load_plan(ROOT/'examples/shadow-snap.plan.json'), official)
    assert not diagnostics
    report = analyze_geometry(m, official)
    assert report['occurrence_count']==3 and report['optimistic_component_count']==1
    assert not report['diagnostics']
